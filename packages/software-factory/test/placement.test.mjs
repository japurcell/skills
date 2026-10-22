import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdtempSync, mkdirSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';
import { assertLocalPlacement } from '../src/placement.ts';

test('placement accepts a native local directory including literal shell metacharacters', () => {
  const root = mkdtempSync(join(tmpdir(), 'factory-placement-'));
  try {
    const directory = join(root, "literal ' $ ; [safe]");
    mkdirSync(directory);
    const result = assertLocalPlacement(directory);
    assert.equal(result.platform, process.platform);
    assert.ok(['apfs', 'hfs', 'ext', 'btrfs', 'xfs', 'NTFS', 'ReFS'].includes(result.filesystem));
    assert.ok(result.directory.endsWith("literal ' $ ; [safe]"));
  } finally { rmSync(root, { recursive: true, force: true }); }
});

test('placement refuses missing, non-directory and network paths without fallback storage', () => {
  const root = mkdtempSync(join(tmpdir(), 'factory-placement-'));
  try {
    const file = join(root, 'file');
    writeFileSync(file, '');
    assert.throws(() => assertLocalPlacement(file), /directory/);
    assert.throws(() => assertLocalPlacement(join(root, 'missing')));
    assert.throws(() => assertLocalPlacement(String.raw`\\server\share\factory`));
  } finally { rmSync(root, { recursive: true, force: true }); }
});

test('Darwin placement uses the native filesystem name instead of an unstable numeric identifier', () => {
  const program = String.raw`
    import assert from 'node:assert/strict';
    import childProcess from 'node:child_process';
    import fs from 'node:fs';
    import { syncBuiltinESMExports } from 'node:module';
    Object.defineProperty(process, 'platform', { value: 'darwin' });
    const directory = "/private/literal ' $ ; [placement]";
    fs.realpathSync.native = () => directory;
    fs.statSync = () => ({ isDirectory: () => true });
    fs.statfsSync = () => ({ type: 25 });
    childProcess.spawnSync = (command, args, options) => {
      assert.equal(command, '/bin/df');
      assert.deepEqual(args, ['-n', '-P', '-T', 'apfs', '--', directory]);
      assert.equal(options.shell, undefined);
      assert.deepEqual(options.env, { LC_ALL: 'C' });
      assert.equal(options.timeout, 1000);
      assert.equal(options.stdio, 'ignore');
      return { status: 0, signal: null };
    };
    syncBuiltinESMExports();
    const { assertLocalPlacement } = await import(${JSON.stringify(new URL('../src/placement.ts', import.meta.url).href)});
    assert.deepEqual(assertLocalPlacement(directory), { directory, platform: 'darwin', filesystem: 'apfs' });
  `;
  const child = spawnSync(process.execPath, ['--input-type=module', '-e', program], {
    encoding: 'utf8', timeout: 5000, maxBuffer: 8192,
  });
  assert.ifError(child.error);
  assert.equal(child.status, 0, child.stderr);
});

test('Darwin placement refuses unverified names and native probe failures without leaking output', () => {
  const program = String.raw`
    import assert from 'node:assert/strict';
    import childProcess from 'node:child_process';
    import fs from 'node:fs';
    import { syncBuiltinESMExports } from 'node:module';
    Object.defineProperty(process, 'platform', { value: 'darwin' });
    const directory = '/private/placement-secret-marker';
    fs.realpathSync.native = () => directory;
    fs.statSync = () => ({ isDirectory: () => true });
    fs.statfsSync = () => ({ type: 26 });
    let responses, calls;
    childProcess.spawnSync = (command, args, options) => {
      calls.push(args[3]);
      assert.equal(command, '/bin/df');
      assert.deepEqual(args, ['-n', '-P', '-T', calls.length === 1 ? 'apfs' : 'hfs', '--', directory]);
      assert.deepEqual(options.env, { LC_ALL: 'C' });
      assert.equal(options.stdio, 'ignore');
      assert.equal(options.timeout, 1000);
      return { stdout: directory, stderr: directory, ...responses.shift() };
    };
    syncBuiltinESMExports();
    const { assertLocalPlacement } = await import(${JSON.stringify(new URL('../src/placement.ts', import.meta.url).href)});
    calls = []; responses = [{ status: 1 }, { status: 0 }];
    assert.equal(assertLocalPlacement(directory).filesystem, 'hfs');
    assert.deepEqual(calls, ['apfs', 'hfs']);
    calls = []; responses = [{ status: 1 }, { status: 1 }];
    assert.throws(() => assertLocalPlacement(directory), { message: 'unsupported storage placement: requires APFS or HFS' });
    assert.deepEqual(calls, ['apfs', 'hfs']);
    for (const failure of [
      { status: null, error: { code: 'ETIMEDOUT', message: directory } },
      { status: null, error: { code: 'ENOENT', message: directory } },
      { status: 0, signal: 'SIGKILL' }, { status: 2 }, { status: null },
    ]) {
      calls = []; responses = [failure, { status: 0 }];
      assert.throws(() => assertLocalPlacement(directory), { message: 'native Darwin placement probe failed; storage refused' });
      assert.deepEqual(calls, ['apfs']);
      calls = []; responses = [{ status: 1 }, failure];
      assert.throws(() => assertLocalPlacement(directory), { message: 'native Darwin placement probe failed; storage refused' });
      assert.deepEqual(calls, ['apfs', 'hfs']);
    }
  `;
  const child = spawnSync(process.execPath, ['--input-type=module', '-e', program], {
    encoding: 'utf8', timeout: 5000, maxBuffer: 8192,
  });
  assert.ifError(child.error);
  assert.equal(child.status, 0, child.stderr);
});

// The native process boundary is substituted only inside this disposable Node child.
// These cases prove refusal diagnostics on every host, not Windows API execution.
test('Windows placement failures expose bounded process facts without native output or paths', () => {
  const program = String.raw`
    import assert from 'node:assert/strict';
    import childProcess from 'node:child_process';
    import fs from 'node:fs';
    import { syncBuiltinESMExports } from 'node:module';
    Object.defineProperty(process, 'platform', { value: 'win32' });
    process.env.SystemRoot = 'C:' + String.fromCharCode(92) + 'Windows';
    const privatePath = 'C:' + String.fromCharCode(92) + 'private-placement-marker';
    fs.realpathSync.native = () => privatePath;
    fs.statSync = () => ({ isDirectory: () => true });
    let response;
    childProcess.spawnSync = (command, args, options) => {
      assert.ok(command.endsWith('powershell.exe'));
      assert.equal(options.timeout, 10_000);
      assert.equal(options.maxBuffer, 8192);
      assert.equal(options.env.FACTORY_PLACEMENT_PATH, privatePath);
      assert.ok(!args.join(' ').includes(privatePath));
      return response;
    };
    syncBuiltinESMExports();
    const { assertLocalPlacement } = await import(${JSON.stringify(new URL('../src/placement.ts', import.meta.url).href)});
    const cases = [
      [{ error: { code: 'ETIMEDOUT', message: privatePath }, status: null, signal: 'SIGTERM', stderr: 'FACTORY_PLACEMENT_STAGE:entered\r\nFACTORY_PLACEMENT_STAGE:interop_ready\r\nFACTORY_PLACEMENT_STAGE:volume_path\r\n' + privatePath }, 'error=ETIMEDOUT; status=none; signal=SIGTERM; stage=volume_path'],
      [{ error: { code: 'ENOENT', message: privatePath }, status: null, signal: null }, 'error=ENOENT; status=none; signal=none; stage=none'],
      [{ error: { code: 'ENOBUFS', message: privatePath }, status: null, signal: 'SIGTERM' }, 'error=ENOBUFS; status=none; signal=SIGTERM'],
      [{ status: 1, signal: null, stderr: 'FACTORY_PLACEMENT_STAGE:unknown\n' + privatePath }, 'error=none; status=1; signal=none; stage=none'],
      [{ status: 1, signal: null, stderr: 'FACTORY_PLACEMENT_STAGE:entered\nFACTORY_PLACEMENT_STAGE:forged_unknown\n' + privatePath }, 'error=none; status=1; signal=none; stage=entered'],
      [{ status: 1, signal: null, stderr: privatePath.repeat(500) + '\nFACTORY_PLACEMENT_STAGE:complete' }, 'error=none; status=1; signal=none; stage=none'],
      [{ status: null, signal: 'SIGKILL' }, 'error=none; status=none; signal=SIGKILL'],
      [{ error: { code: privatePath, message: privatePath }, status: null, signal: privatePath }, 'error=other; status=none; signal=other'],
    ];
    for (const [outcome, expected] of cases) {
      response = { stdout: privatePath.repeat(100), stderr: privatePath.repeat(100), ...outcome };
      assert.throws(() => assertLocalPlacement(privatePath), (error) => {
        assert.ok(error.message.startsWith('native Windows placement probe failed; storage refused ('));
        assert.ok(error.message.includes(expected), error.message);
        assert.match(error.message, /elapsedMs=\d+\)$/);
        assert.ok(error.message.length < 256);
        assert.ok(!error.message.includes(privatePath));
        assert.equal(error.cause, undefined);
        return true;
      });
    }
    response = { status: 0, signal: null, stdout: privatePath + ' invalid JSON', stderr: '' };
    assert.throws(() => assertLocalPlacement(privatePath), (error) => {
      assert.equal(error.message, 'native Windows placement probe returned invalid JSON; storage refused');
      assert.ok(!error.message.includes(privatePath));
      assert.equal(error.cause, undefined);
      return true;
    });
    response = { status: 0, signal: null, stdout: JSON.stringify({ driveType: 3, filesystem: 'FAT32' }), stderr: '' };
    assert.throws(() => assertLocalPlacement(privatePath), /unsupported storage placement: requires fixed local NTFS or ReFS/);
    for (const filesystem of ['NTFS', 'ReFS']) {
      response = { status: 0, signal: null, stdout: '\uFEFF' + JSON.stringify({ driveType: 3, filesystem }), stderr: '' };
      assert.deepEqual(assertLocalPlacement(privatePath), { directory: privatePath, platform: 'win32', filesystem });
    }
  `;
  const child = spawnSync(process.execPath, ['--input-type=module', '-e', program], {
    encoding: 'utf8', timeout: 5000, maxBuffer: 8192,
  });
  assert.ifError(child.error);
  assert.equal(child.status, 0, child.stderr);
});
