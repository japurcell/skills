import { spawn } from 'node:child_process';
import { once } from 'node:events';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';

/** Disposable-fixture-only native write denial; no product injection or database replacement. */
export async function lockWindowsWalWrites(walPath) {
  const systemRoot = process.env.SystemRoot;
  if (process.platform !== 'win32' || !systemRoot || !/^[A-Za-z]:\\/.test(systemRoot)) throw new Error('native Windows WAL lock prerequisite missing');
  const script = fileURLToPath(new URL('./windows-wal-write-lock.ps1', import.meta.url));
  const child = spawn(join(systemRoot, 'System32', 'WindowsPowerShell', 'v1.0', 'powershell.exe'),
    ['-NoLogo', '-NoProfile', '-NonInteractive', '-File', script, walPath], { stdio: ['pipe', 'pipe', 'pipe'], windowsHide: true });
  const closed = once(child, 'close');
  let stdout = '', stderr = '';
  child.stderr.on('data', (chunk) => { stderr = (stderr + chunk).slice(-8192); });
  let timeout;
  try {
    await Promise.race([
      new Promise((resolve, reject) => {
        child.stdout.on('data', (chunk) => {
          stdout += chunk;
          if (stdout.length > 8192) reject(new Error('unexpected native lock helper output'));
          const line = stdout.split('\n')[0]?.trim();
          if (line === '{"ready":true}') resolve();
        });
      }),
      closed.then(([code]) => { throw new Error(`native WAL lock helper exited before ready (${code}): ${stderr}`); }),
      new Promise((_, reject) => { timeout = setTimeout(() => reject(new Error('native WAL lock handshake timed out')), 10000); }),
    ]);
  } catch (error) {
    if (child.exitCode === null && child.signalCode === null) child.kill('SIGKILL');
    await closed.catch(() => {});
    throw error;
  } finally { clearTimeout(timeout); }
  return async () => {
    child.stdin.end('release\n');
    const timer = setTimeout(() => child.kill('SIGKILL'), 3000);
    try {
      const [code, signal] = await closed;
      if (code !== 0 || signal) throw new Error(`native WAL lock cleanup failed (${code}, ${signal}): ${stderr}`);
    } finally { clearTimeout(timer); }
  };
}
