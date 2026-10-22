#!/usr/bin/env node
// Test-only executable. Never imports or launches a provider.
import { existsSync, writeFileSync } from 'node:fs';
import { spawn } from 'node:child_process';
import { once } from 'node:events';
import { setTimeout as delay } from 'node:timers/promises';
import { fileURLToPath } from 'node:url';
import { parseArgs } from 'node:util';

const { values } = parseArgs({ options: {
  mode: { type: 'string' }, result: { type: 'string' }, child: { type: 'boolean' },
  'launch-log': { type: 'string' }, 'pause-until': { type: 'string' },
} });
let stopping = false;
let descendant;
let descendantClosed;
for (const signal of ['SIGINT', 'SIGTERM']) process.on(signal, () => { stopping = true; process.exitCode = signal === 'SIGINT' ? 130 : 143; });
if (values.child) {
  descendant = spawn(process.execPath, [fileURLToPath(import.meta.url), '--mode', 'hold'], { stdio: 'ignore' });
  descendantClosed = once(descendant, 'close');
  await once(descendant, 'spawn');
}
if (values['launch-log']) writeFileSync(values['launch-log'], JSON.stringify({ pid: process.pid, childPid: descendant?.pid }));
while (!stopping && (values.mode === 'hold' || (values['pause-until'] && !existsSync(values['pause-until'])))) await delay(10);
if (descendant) {
  descendant.kill('SIGTERM');
  await descendantClosed;
}
if (stopping) {
  // Keep the signal exit status instead of producing a final result after cancellation.
} else
if (!values.result || !['success', 'needs-input', 'permission-denied', 'malformed', 'crash'].includes(values.mode)) {
  process.stderr.write('fixture: expected a known --mode and --result PATH\n');
  process.exitCode = 64;
} else {
  process.stdout.write('fixture output\n');
  process.stderr.write('fixture diagnostic\n');
  switch (values.mode) {
    case 'success':
      writeFileSync(values.result, JSON.stringify({ kind: 'result', payload: { summary: 'fixture complete' } }));
      break;
    case 'needs-input':
      writeFileSync(values.result, JSON.stringify({
        kind: 'needs_input', question: 'Which fixture target?', context: 'Fixture requires an explicit target.',
      }));
      process.exitCode = 2;
      break;
    case 'permission-denied':
      process.stderr.write('fixture: permission denied\n');
      process.exitCode = 1;
      break;
    case 'malformed':
      writeFileSync(values.result, '{invalid control JSON');
      break;
    case 'crash':
      process.exitCode = 70;
      break;
  }
}
