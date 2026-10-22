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
} else if (mode === 'hold-pipe-ready') {
  await new Promise(resolve => setTimeout(resolve, Number(args[1] ?? 0)));
  const holder = spawn(process.execPath, [fileURLToPath(import.meta.url), 'hold-pipe-child', args[0]], {
    detached: true, windowsHide: true, stdio: ['pipe', 'inherit', 'inherit'],
  });
  holder.once('spawn', () => process.send?.({ ready: true, pid: holder.pid }));
  let released = false;
  const release = () => {
    if (released) return;
    released = true;
    holder.stdin.end('start', () => process.exit(0));
  };
  process.once('message', message => { if (message === 'release') release(); });
  process.once('disconnect', release);
  holder.unref();
} else if (mode === 'hold-pipe-child') {
  let started = false;
  const begin = () => {
    if (started) return;
    started = true;
    setTimeout(() => { writeFileSync(args[0], 'exited'); }, 700);
  };
  process.stdin.once('data', begin);
  process.stdin.once('end', begin);
  process.stdin.resume();
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
