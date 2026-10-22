import { join } from 'node:path';
import { createRepository } from './repository.mjs';
import { initializeRepositoryStore } from '../../dist/store.js';
import { InvocationRecorder } from '../../dist/capture.js';
import { lockWindowsWalWrites } from './windows-wal-write-lock.mjs';
if (process.platform !== 'win32') process.on('SIGXFSZ', () => {});
const repository = createRepository();
let store, releaseWriteLock;
try {
  store = await initializeRepositoryStore(join(repository.path, '.git'), { release: 'fixture' });
  const run = await store.createRun();
  const worktree = await store.registerWorktree({ path: repository.path, registration: 'fixture' });
  const invocation = await store.startInvocation({ runId: run.id, worktreeId: worktree.id, owner: { host: 'fixture', pid: process.pid, start: 'failure' } });
  await store.activateInvocation(invocation.id);
  const notices = [], shutdown = [];
  const recorder = new InvocationRecorder({ store, invocationId: invocation.id, requestShutdown: message => shutdown.push(message), fallback: message => notices.push(message) });
  const output = await recorder.openCapture({ channel: 'stdout' });
  await output.write('committed-before-failure'); await recorder.barrier();
  if (process.platform === 'win32') {
    releaseWriteLock = await lockWindowsWalWrites(join(repository.path, '.git', 'factory', 'history.sqlite-wal'));
  }
  let failed = false;
  try { for (let i = 0; i < 100; i++) await output.write('x'.repeat(65536)); await output.finish(); }
  catch { failed = true; }
  let admissionBlocked = false;
  try { await store.admitAttempt({ id: 'never-launched', invocationId: invocation.id, operationKey: 'after-failure', kind: 'command', intent: 'initial' }); }
  catch { admissionBlocked = true; }
  const saved = store.readCapture({ id: output.id });
  console.log(JSON.stringify({ failed, admissionBlocked, shutdown: shutdown.length, notices: notices.length, savedPrefix: saved.chunks[0]?.text, eventsReadable: store.readEvents({ after: '0' }).events.length > 0 }));
} finally {
  try { if (releaseWriteLock) await releaseWriteLock(); }
  finally { store?.close(); repository.dispose(); }
}
