import { spawn } from 'node:child_process';
import { writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const [mode, ...args] = process.argv.slice(2);
if (mode === 'record') {
  writeFileSync(args[0], JSON.stringify(args.slice(1)));
} else if (mode === 'wait') {
  process.on('SIGTERM', () => {});
  setInterval(() => {}, 1000);
} else if (mode === 'hold-pipe') {
  spawn(process.execPath, [fileURLToPath(import.meta.url), 'wait-short'], {
    detached: true, stdio: 'inherit',
  }).unref();
} else if (mode === 'wait-short') {
  setTimeout(() => {}, 700);
} else if (mode === 'service-unavailable') {
  process.stderr.write('Could not connect to notification daemon: secret data must not be copied\n');
  process.exitCode = 1;
} else if (mode === 'denied') {
  process.stderr.write('Access denied: secret data must not be copied\n');
  process.exitCode = 1;
} else if (mode === 'exit-code') {
  process.exitCode = Number(args[0]);
} else if (mode === 'exit-code-stderr') {
  process.stderr.write(args[1]);
  process.exitCode = Number(args[0]);
} else {
  process.exitCode = 2;
}
