'use strict';

const { spawn } = require('node:child_process');
const { writeSync } = require('node:fs');

const release = Buffer.from('R');
let child;
const failureKinds = new Set(['control', 'arguments', 'spawn-no-pid', 'spawn-error', 'child-stdin-error', 'child-stdout-error', 'child-ready-shape', 'root-output-error', 'root-release-shape', 'root-input-ended', 'child-release-shape', 'child-input-ended', 'child-ready-write', 'root-timeout', 'child-timeout']);
function fail(reason = 'control') {
  const category = typeof reason === 'string' && (failureKinds.has(reason) || /^child-exit-[0-9]{1,10}$/.test(reason)) ? reason : 'control';
  try { writeSync(2, `FIXTURE_FAILURE ${category}\n`); } catch { }
  if (child && child.exitCode === null) child.kill();
  process.exit(2);
}

if (process.argv[2] === '--child' && process.argv.length === 3) {
  const timer = setTimeout(() => fail('child-timeout'), 12000);
  process.stdin.once('data', (value) => {
    if (value.length !== 1 || value[0] !== release[0]) fail('child-release-shape');
    clearTimeout(timer);
    process.exit(0);
  });
  process.stdin.once('end', () => fail('child-input-ended'));
  process.stdin.resume();
  process.stdout.write('K', (error) => { if (error) fail('child-ready-write'); });
} else if (process.argv.length === 2) {
  child = spawn(process.execPath, [__filename, '--child'], {
    shell: false, windowsHide: true, stdio: ['pipe', 'pipe', 'ignore']
  });
  if (!Number.isInteger(child.pid) || child.pid <= 0) fail('spawn-no-pid');
  let released = false;
  let initialized = false;
  const timer = setTimeout(() => fail('root-timeout'), 15000);
  child.once('error', () => fail('spawn-error'));
  child.stdin.once('error', () => fail('child-stdin-error'));
  child.stdout.once('error', () => fail('child-stdout-error'));
  child.stdout.on('data', (value) => {
    if (initialized || value.length !== 1 || value[0] !== 0x4b) fail('child-ready-shape');
    initialized = true;
    process.stdout.write(`${child.pid}\n`, (error) => { if (error) fail('root-output-error'); });
  });
  child.once('exit', (code, signal) => {
    clearTimeout(timer);
    if (!released || code !== 0 || signal !== null)
      fail(Number.isInteger(code) ? `child-exit-${code >>> 0}` : 'control');
    process.exit(0);
  });
  process.stdin.once('data', (value) => {
    if (!initialized || value.length !== 1 || value[0] !== release[0]) fail('root-release-shape');
    released = true;
    child.stdin.end(release);
  });
  process.stdin.once('end', () => { if (!released) fail('root-input-ended'); });
  process.stdin.resume();
} else fail('arguments');
