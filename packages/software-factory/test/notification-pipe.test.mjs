import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { mkdtempSync, readFileSync, rmSync } from 'node:fs';
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
