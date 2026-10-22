import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { copyFileSync, linkSync, mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { setTimeout as delay } from 'node:timers/promises';
import { test } from 'node:test';
import { fileURLToPath } from 'node:url';
import { currentOwner, inspectOwner } from '../dist/native/process.js';

const fixture = fileURLToPath(new URL('./fixtures/notification-helper.mjs', import.meta.url));

test('inherited pipe beyond the deadline is unknown, never submitted', async (t) => {
  const directory = mkdtempSync(join(tmpdir(), 'factory-notification-pipe-'));
  const args = [fixture, 'hold-pipe-ready', join(directory, 'holder-exited'), '200'];
  // Establish the real escaped pipe before measuring transport cleanup. Process startup
  // belongs to the separate real-spawn deadline case, not this pipe-lifetime fixture.
  const prepared = spawn(process.execPath, args, {
    detached: process.platform !== 'win32', windowsHide: true,
    stdio: ['ignore', 'pipe', 'pipe', 'ipc'],
  });
  let holder;
  try {
    const pid = await new Promise((resolve, reject) => {
      const timer = setTimeout(() => reject(new Error('inherited-pipe fixture did not become ready')), 3000);
      prepared.once('message', message => {
        if (message?.ready === true && Number.isSafeInteger(message.pid)) { clearTimeout(timer); resolve(message.pid); }
      });
      prepared.once('error', error => { clearTimeout(timer); reject(error); });
      prepared.once('exit', () => { clearTimeout(timer); reject(new Error('inherited-pipe fixture exited before readiness')); });
    });
    holder = currentOwner(pid);
    t.mock.module('node:child_process', { exports: {
      spawn: (file, requestedArgs) => {
        assert.equal(file, process.execPath);
        assert.deepEqual(requestedArgs, args);
        queueMicrotask(() => prepared.send('release'));
        return prepared;
      },
    } });
    const { executeNotificationProcess } = await import('../dist/native/notification-transport.js');
    const start = performance.now();
    const result = await executeNotificationProcess({ file: process.execPath, args }, 200);
    assert.deepEqual(result, { state: 'unknown', reason: 'cleanup_unconfirmed', cleanup: 'unknown' });
    assert.ok(performance.now() - start < 450);
  } finally {
    prepared.kill('SIGKILL');
    if (holder) {
      const deadline = performance.now() + 3000;
      while (inspectOwner(holder).state !== 'not_live' && performance.now() < deadline) await delay(20);
      const remaining = inspectOwner(holder);
      if (remaining.state === 'known_live') process.kill(holder.pid, 'SIGKILL');
      assert.equal(inspectOwner(holder).state, 'not_live', 'fixture holder must finish after its bounded timer');
      assert.equal(readFileSync(join(directory, 'holder-exited'), 'utf8'), 'exited');
    }
    rmSync(directory, { recursive: true, force: true });
  }
});

test('Windows helper exit codes take priority over diagnostic wording after real child readiness', async (t) => {
  const directory = mkdtempSync(join(tmpdir(), 'factory-notification-exit-'));
  const helper = join(directory, 'windows-notify.exe');
  const script = [
    'process.send({ ready: true });',
    'process.once("message", () => {',
    '  process.stderr.write(process.argv[2], () => process.exit(Number(process.argv[1])));',
    '});',
  ].join('\n');
  const cases = [
    { code: 3, stderr: 'Access denied', reason: 'registration_missing' },
    { code: 5, stderr: 'notification daemon unavailable', reason: 'sender_exit_nonzero' },
    { code: 4, stderr: 'notification daemon unavailable', reason: 'denied' },
  ];
  const prepared = [];
  try {
    try { linkSync(process.execPath, helper); }
    catch { copyFileSync(process.execPath, helper); }
    for (const item of cases) {
      const args = ['-e', script, String(item.code), item.stderr];
      const child = spawn(helper, args, { windowsHide: true, stdio: ['ignore', 'pipe', 'pipe', 'ipc'] });
      const closed = new Promise(resolve => child.once('close', resolve));
      const ready = new Promise((resolve, reject) => {
        const timer = setTimeout(() => reject(new Error('Windows exit fixture did not become ready')), 3000);
        child.once('message', message => {
          if (message?.ready === true) { clearTimeout(timer); resolve(); }
        });
        child.once('error', error => { clearTimeout(timer); reject(error); });
        child.once('exit', () => { clearTimeout(timer); reject(new Error('Windows exit fixture exited before readiness')); });
      });
      prepared.push({ ...item, args, child, ready, closed });
    }
    await Promise.all(prepared.map(item => item.ready));
    let next = 0;
    t.mock.module('node:child_process', { exports: {
      spawn: (file, args) => {
        const item = prepared[next++];
        assert.equal(file, helper);
        assert.deepEqual(args, item.args);
        queueMicrotask(() => item.child.send('release'));
        return item.child;
      },
    } });
    const { executeNotificationProcess } = await import('../dist/native/notification-transport.js?windows-exit-priority');
    for (const item of prepared) {
      assert.deepEqual(await executeNotificationProcess({ file: helper, args: item.args }, 1000), {
        state: 'failed', reason: item.reason, cleanup: 'complete',
      });
    }
    assert.equal(next, prepared.length);
  } finally {
    for (const { child } of prepared) child.kill('SIGKILL');
    await Promise.all(prepared.map(item => item.closed));
    rmSync(directory, { recursive: true, force: true });
  }
});

test('missing owned Windows registration has its own fixed reason', async (t) => {
  const directory = mkdtempSync(join(tmpdir(), 'factory-notification-registration-'));
  const helper = join(directory, 'windows-notify.exe');
  const args = ['-e', 'process.send({ ready: true }); process.once("message", () => process.exit(3));'];
  let child;
  let closed;
  try {
    try { linkSync(process.execPath, helper); }
    catch { copyFileSync(process.execPath, helper); }
    child = spawn(helper, args, { windowsHide: true, stdio: ['ignore', 'pipe', 'pipe', 'ipc'] });
    closed = new Promise(resolve => child.once('close', resolve));
    await new Promise((resolve, reject) => {
      const timer = setTimeout(() => reject(new Error('Windows registration fixture did not become ready')), 3000);
      child.once('message', message => {
        if (message?.ready === true) { clearTimeout(timer); resolve(); }
      });
      child.once('error', error => { clearTimeout(timer); reject(error); });
      child.once('exit', () => { clearTimeout(timer); reject(new Error('Windows registration fixture exited before readiness')); });
    });
    t.mock.module('node:child_process', { exports: {
      spawn: (file, requestedArgs) => {
        assert.equal(file, helper);
        assert.deepEqual(requestedArgs, args);
        queueMicrotask(() => child.send('release'));
        return child;
      },
    } });
    const { executeNotificationProcess } = await import('../dist/native/notification-transport.js?windows-registration');
    assert.deepEqual(await executeNotificationProcess({ file: helper, args }, 1000), {
      state: 'failed', reason: 'registration_missing', cleanup: 'complete',
    });
  } finally {
    child?.kill('SIGKILL');
    if (closed) await closed;
    rmSync(directory, { recursive: true, force: true });
  }
});
