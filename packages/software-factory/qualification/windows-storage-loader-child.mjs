// Fixed qualification child. All pre-load authority belongs to the trusted outer
// controller. No code/image authentication, storage, workers or descendants here.
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';

const scope = 'windows-storage-loader-child';
const emit = fields => process.stdout.write(`${JSON.stringify({ scope, ...fields })}\n`);
let finished = false;
let reported = false;
let phase = 'ready';
let exitCode = 1;
const cases = new Set(['positive-user', 'positive-admin', 'throw-before', 'require-failure',
  'throw-after', 'nonzero', 'stdout-overflow', 'stderr-overflow', 'timeout', 'retained-writer', 'api-mismatch',
  'forged-success', 'unknown-result', 'extra-result']);
function report(state, reason) {
  if (reported) return;
  reported = true;
  emit({ event: 'result', state, reason });
}
function refuse() {
  if (finished) return;
  finished = true;
  report('failed', 'protocol');
  process.exitCode = 1;
  process.stdin.destroy();
}
function load() {
  phase = 'loading';
  const mode = process.argv[2];
  if (mode === 'forged-success' || mode === 'unknown-result' || mode === 'extra-result') {
    // Fixed negative protocol controls. These deliberately do not require the
    // addon: the external controller must independently reject the claim.
    reported = true;
    emit({ event: 'result', state: 'called', reason: mode === 'unknown-result' ? 'unqualified' : 'none',
      ...(mode === 'extra-result' ? { path: 'loader-private-output-canary' } : {}) });
    exitCode = 0;
    phase = 'release';
    return;
  }
  if (mode === 'timeout') return;
  if (mode === 'stdout-overflow' || mode === 'stderr-overflow') {
    phase = 'overflow';
    (mode === 'stdout-overflow' ? process.stdout : process.stderr).write('x'.repeat(8193), () => {
      report('failed', 'bounds');
      phase = 'release';
    });
    return;
  }
  let reason = 'loader';
  try {
    if (mode === 'throw-before') { reason = 'before'; throw new Error('fixed'); }
    // Exactly this full filename once. The trusted controller has custody before
    // it sends load. Node owns its module; no cache deletion or unload claim.
    const canary = createRequire(import.meta.url)(fileURLToPath(new URL('./windows-storage-loader-canary.node', import.meta.url)));
    reason = 'call';
    if (canary === null || typeof canary !== 'object' ||
        Object.keys(canary).length !== 1 || typeof canary.probe !== 'function' ||
        canary.probe() !== 'windows-storage-loader-canary-v1') throw new Error('fixed');
    if (mode === 'throw-after') { reason = 'after'; throw new Error('fixed'); }
    report('called', 'none');
    exitCode = mode === 'nonzero' ? 23 : 0;
  } catch {
    report('failed', reason);
  }
  phase = 'release';
}
if (process.argv.length !== 3 || !cases.has(process.argv[2]) ||
    process.version !== 'v24.22.1' || process.execArgv.length !== 0) {
  refuse();
} else {
  emit({ event: 'ready' });
  let bytes = 0;
  let pending = Buffer.alloc(0);
  process.stdin.on('data', chunk => {
    bytes += chunk.length;
    if (finished) return;
    if (bytes > 1024) { refuse(); return; }
    pending = Buffer.concat([pending, chunk]);
    const newline = pending.indexOf(10);
    if (newline < 0) return;
    if (newline !== pending.length - 1) { refuse(); return; }
    const expected = phase === 'ready' ? '{"command":"load"}\n' : '{"command":"release"}\n';
    if ((phase !== 'ready' && phase !== 'release') || !pending.equals(Buffer.from(expected))) {
      refuse(); return;
    }
    pending = Buffer.alloc(0);
    if (phase === 'ready') load();
    else {
      finished = true;
      phase = 'done';
      process.exitCode = exitCode;
      process.stdin.destroy();
    }
  });
  process.stdin.on('end', refuse);
  process.stdin.on('error', refuse);
}
