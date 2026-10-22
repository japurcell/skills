'use strict';

const { spawn } = require('node:child_process');

const release = Buffer.from('R');
let child;
function fail() {
  if (child && child.exitCode === null) child.kill();
  process.exit(2);
}

if (process.argv[2] === '--child' && process.argv.length === 3) {
  const timer = setTimeout(fail, 12000);
  process.stdin.once('data', (value) => {
    if (value.length !== 1 || value[0] !== release[0]) fail();
    clearTimeout(timer);
    process.exit(0);
  });
  process.stdin.once('end', fail);
  process.stdin.resume();
} else if (process.argv.length === 2) {
  child = spawn(process.execPath, [__filename, '--child'], {
    shell: false, windowsHide: true, stdio: ['pipe', 'ignore', 'ignore']
  });
  if (!Number.isInteger(child.pid) || child.pid <= 0) fail();
  let released = false;
  const timer = setTimeout(fail, 15000);
  child.once('error', fail);
  child.stdin.once('error', fail);
  child.once('exit', (code, signal) => {
    clearTimeout(timer);
    if (!released || code !== 0 || signal !== null) fail();
    process.exit(0);
  });
  process.stdout.write(`${child.pid}\n`, (error) => { if (error) fail(); });
  process.stdin.once('data', (value) => {
    if (value.length !== 1 || value[0] !== release[0]) fail();
    released = true;
    child.stdin.end(release);
  });
  process.stdin.once('end', () => { if (!released) fail(); });
  process.stdin.resume();
} else fail();
