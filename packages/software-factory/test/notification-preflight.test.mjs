import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { test } from 'node:test';

test('an unresolved Windows preflight reaches the deadline and cannot later launch', async (t) => {
  let releaseRealpath;
  let launches = 0;
  let realpathCalls = 0;
  t.mock.module('node:fs/promises', {
    exports: {
      realpath: path => ++realpathCalls === 1
        ? new Promise(resolve => { releaseRealpath = resolve; })
        : Promise.resolve(path),
      stat: async () => ({ isFile: () => true, size: 3 }),
      readFile: async () => Buffer.from('abc'),
    },
  });
  t.mock.module('node:child_process', {
    exports: { spawn: () => { launches += 1; throw new Error('unexpected launch'); } },
  });
  const previousPlatform = process.platform;
  Object.defineProperty(process, 'platform', { configurable: true, value: 'win32' });
  try {
    const { createInstalledDesktopNotificationSender } = await import('../dist/native/notifications.js');
    const sender = createInstalledDesktopNotificationSender({
      installRoot: 'C:\\factory',
      helperRelativePath: 'windows-notify.exe',
      helperSha256: createHash('sha256').update('abc').digest('hex'),
      repositoryCommonDirectory: 'C:\\repo',
      shortcutOwnerToken: '0123456789ABCDEF0123456789ABCDEF',
    });
    const started = performance.now();
    assert.deepEqual(await sender({ title: 'Title', body: 'Body', timeoutMs: 40 }), {
      state: 'timed_out', reason: 'deadline_exceeded', cleanup: 'complete',
    });
    assert.ok(performance.now() - started < 300, 'preflight must honor the absolute deadline');
    releaseRealpath('C:\\factory');
    await new Promise(resolve => setTimeout(resolve, 30));
    assert.equal(launches, 0, 'abandoned preflight must not launch after the result');
  } finally {
    Object.defineProperty(process, 'platform', { configurable: true, value: previousPlatform });
  }
});
