import assert from 'node:assert/strict';
import { copyFileSync, linkSync, mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { test } from 'node:test';
import { fileURLToPath } from 'node:url';
import { notificationCommand, repositoryNotificationAppId, sendDesktopNotification } from '../dist/native/notifications.js';
import { executeNotificationProcess } from '../dist/native/notification-transport.js';

const fixture = fileURLToPath(new URL('./fixtures/notification-helper.mjs', import.meta.url));
const fake = (mode, ...args) => ({ file: process.execPath, args: [fixture, mode, ...args] });

test('fixed native commands pass filtered title and body as data', () => {
  const input = { title: 'Factory "alert"', body: 'line 1; $(touch /tmp/unsafe) <& secret-value', secrets: ['secret-value'] };
  assert.deepEqual(notificationCommand(input, 'darwin'), {
    file: '/usr/bin/osascript',
    args: ['-e', 'on run argv', '-e', 'display notification (item 2 of argv) with title (item 1 of argv)', '-e', 'end run', '--', 'Factory "alert"', 'line 1; $(touch /tmp/unsafe) <& [REDACTED]'],
  });
  assert.deepEqual(notificationCommand(input, 'linux'), {
    file: '/usr/bin/notify-send',
    args: ['--app-name=Software Factory', '--', 'Factory "alert"', 'line 1; $(touch /tmp/unsafe) &lt;&amp; [REDACTED]'],
  });
  assert.equal(notificationCommand({ title: 'Safe', body: '<a href="https://example.com">click</a>' }, 'linux').args.at(-1),
    '&lt;a href=&quot;https://example.com&quot;&gt;click&lt;/a&gt;');
});

test('Windows message cannot select an executable or identity', () => {
  const appId = repositoryNotificationAppId('C:\\repos\\one');
  assert.match(appId, /^SoftwareFactory\.Repository\.[0-9A-F]{24}$/);
  assert.notEqual(appId, repositoryNotificationAppId('C:\\repos\\two'));
  assert.throws(() => notificationCommand({ title: 'Title', body: 'Body', windowsHelper: 'C:\\unmanaged\\windows-notify.exe', windowsAppId: appId }, 'win32'), /registration|installation/);
});

test('invalid and oversized text is refused before any process starts', () => {
  assert.throws(() => notificationCommand({ title: '', body: 'Body' }, 'linux'), /title/);
  assert.throws(() => notificationCommand({ title: 'Title', body: 'nul\0byte' }, 'linux'), /body/);
  assert.throws(() => notificationCommand({ title: 'Title', body: 'x'.repeat(4097) }, 'linux'), /body/);
  assert.throws(() => notificationCommand({ title: 'Title', body: '&'.repeat(1000) }, 'linux'), /body/);
  assert.throws(() => notificationCommand({ title: 'Title', body: 'Body', secrets: [''] }, 'linux'), /filter/);
  assert.throws(() => notificationCommand({ title: 'Title', body: 'Body', secrets: Array(129).fill('same') }, 'linux'), /filter/);
});

test('timeout over five seconds is rejected without touching the desktop', async () => {
  assert.deepEqual(await sendDesktopNotification({ title: 'Title', body: 'Body', timeoutMs: 5001 }), {
    state: 'failed', reason: 'invalid_request', cleanup: 'complete',
  });
});

test('missing notification request fails with a fixed result', async () => {
  assert.deepEqual(await sendDesktopNotification(null), {
    state: 'failed', reason: 'invalid_request', cleanup: 'complete',
  });
});

test('real child submission waits for clean exit and closed pipes', async () => {
  const dir = mkdtempSync(join(tmpdir(), 'factory-notify-'));
  try {
    const output = join(dir, 'args.json');
    const result = await executeNotificationProcess(fake('record', output, 'literal; <&', '$(echo data)'), 1000);
    assert.deepEqual(result, { state: 'submitted', cleanup: 'complete' });
    assert.deepEqual(JSON.parse(readFileSync(output, 'utf8')), ['literal; <&', '$(echo data)']);
  } finally { rmSync(dir, { recursive: true, force: true }); }
});

test('missing executable, unavailable service, denied setting and nonzero exit have safe reasons', async () => {
  assert.deepEqual(await executeNotificationProcess({ file: join(tmpdir(), 'missing-factory-notify-command'), args: [] }, 1000), {
    state: 'failed', reason: 'missing_executable', cleanup: 'complete',
  });
  assert.deepEqual(await executeNotificationProcess(fake('service-unavailable'), 1000), {
    state: 'failed', reason: 'service_unavailable', cleanup: 'complete',
  });
  assert.deepEqual(await executeNotificationProcess(fake('denied'), 1000), {
    state: 'failed', reason: 'denied', cleanup: 'complete',
  });
  assert.deepEqual(await executeNotificationProcess(fake('exit-code', '9'), 1000), {
    state: 'failed', reason: 'sender_exit_nonzero', cleanup: 'complete',
  });
});

test('missing owned Windows registration has its own fixed reason', async () => {
  const dir = mkdtempSync(join(tmpdir(), 'factory-notify-'));
  try {
    const helper = join(dir, 'windows-notify.exe');
    try { linkSync(process.execPath, helper); }
    catch { copyFileSync(process.execPath, helper); }
    assert.deepEqual(await executeNotificationProcess({ file: helper, args: ['-e', 'process.exit(3)'] }, 1000), {
      state: 'failed', reason: 'registration_missing', cleanup: 'complete',
    });
  } finally { rmSync(dir, { recursive: true, force: true }); }
});

test('Windows helper exit codes take priority over diagnostic wording', async () => {
  const dir = mkdtempSync(join(tmpdir(), 'factory-notify-'));
  try {
    const helper = join(dir, 'windows-notify.exe');
    try { linkSync(process.execPath, helper); }
    catch { copyFileSync(process.execPath, helper); }
    const run = (code, stderr) => executeNotificationProcess({ file: helper, args: [fixture, 'exit-code-stderr', String(code), stderr] }, 1000);
    assert.deepEqual(await run(3, 'Access denied'), { state: 'failed', reason: 'registration_missing', cleanup: 'complete' });
    assert.deepEqual(await run(5, 'notification daemon unavailable'), { state: 'failed', reason: 'sender_exit_nonzero', cleanup: 'complete' });
    assert.deepEqual(await run(4, 'notification daemon unavailable'), { state: 'failed', reason: 'denied', cleanup: 'complete' });
  } finally { rmSync(dir, { recursive: true, force: true }); }
});

test('lowercase environment password is filtered from public notification command', () => {
  const key = 'factory_password';
  const before = process.env[key];
  process.env[key] = 'fixture-lowercase-password';
  try {
    const command = notificationCommand({ title: 'Factory', body: `Value: ${process.env[key]}` }, 'linux');
    assert.equal(command.args.at(-1), 'Value: [REDACTED]');
  } finally {
    if (before === undefined) delete process.env[key];
    else process.env[key] = before;
  }
});

test('deadline kills an owned child and does not report submission', async () => {
  const start = performance.now();
  const result = await executeNotificationProcess(fake('wait'), 250);
  assert.deepEqual(result, { state: 'timed_out', reason: 'deadline_exceeded', cleanup: 'complete' });
  assert.ok(performance.now() - start < 500, 'deadline includes termination and pipe cleanup');
});

test('inherited pipe beyond the deadline is unknown, never submitted', async () => {
  const start = performance.now();
  const result = await executeNotificationProcess(fake('hold-pipe'), 200);
  assert.deepEqual(result, { state: 'unknown', reason: 'cleanup_unconfirmed', cleanup: 'unknown' });
  assert.ok(performance.now() - start < 450);
});
