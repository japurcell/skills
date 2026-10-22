import { spawn } from 'node:child_process';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const cancellationGraceMs = 1000;
const worker = fileURLToPath(new URL('./ordered-test-worker.mjs', import.meta.url));

// Keep Node's ordered test runner inside an owned process tree. Its AbortSignal
// only requests termination; a test that handles SIGTERM can otherwise keep it open.
export async function runOrderedTests(files, { concurrency, cwd, execArgv = [], signal } = {}) {
  if (files.length === 0) throw new Error('no test files selected');
  if (signal?.aborted) return 1;
  const config = { files: files.map((file) => resolve(cwd, file)), concurrency, cwd, execArgv };
  const env = { ...process.env };
  delete env.NODE_TEST_CONTEXT;
  return new Promise((resolveResult) => {
    const child = spawn(process.execPath, [worker, JSON.stringify(config)], {
      cwd, env, stdio: ['inherit', 'inherit', 'inherit', 'ipc'],
      detached: process.platform !== 'win32',
    });
    let graceTimer;
    let forcePromise;
    let spawnError;
    let forceError;
    const forceTree = () => {
      if (forcePromise) return forcePromise;
      if (child.pid === undefined) return Promise.resolve();
      if (process.platform === 'win32') {
        // taskkill /T targets only this runner and children started by it.
        forcePromise = new Promise((resolveForce) => {
          const killer = spawn('taskkill.exe', ['/PID', String(child.pid), '/T', '/F'], { stdio: 'ignore', windowsHide: true });
          killer.on('error', (error) => { forceError = error; });
          killer.on('close', (code) => {
            if (code !== 0 && !forceError) forceError = new Error(`taskkill exited ${code}`);
            resolveForce();
          });
        });
      } else {
        try { process.kill(-child.pid, 'SIGKILL'); }
        catch (error) { if (error.code !== 'ESRCH') forceError = error; }
        forcePromise = Promise.resolve();
      }
      return forcePromise;
    };
    const abort = () => {
      if (graceTimer) return;
      if (child.connected) child.send('abort', (error) => {
        if (error && error.code !== 'ERR_IPC_CHANNEL_CLOSED') process.stderr.write(`factory tests: ${error.message}\n`);
      });
      graceTimer = setTimeout(() => { void forceTree(); }, cancellationGraceMs);
    };
    signal?.addEventListener('abort', abort, { once: true });
    if (signal?.aborted) abort();
    child.on('error', (error) => { spawnError = error; process.stderr.write(`factory tests: ${error.message}\n`); });
    child.on('close', async (code, termination) => {
      clearTimeout(graceTimer);
      signal?.removeEventListener('abort', abort);
      if (signal?.aborted && process.platform !== 'win32') await forceTree();
      if (forcePromise) await forcePromise;
      if (forceError) process.stderr.write(`factory tests: failed to close owned test tree: ${forceError.message}\n`);
      resolveResult((spawnError || forceError || signal?.aborted || termination) ? 1 : (code ?? 1));
    });
  });
}
