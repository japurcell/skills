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
      [{ error: { code: 'ETIMEDOUT', message: privatePath }, status: null, signal: 'SIGTERM' }, 'error=ETIMEDOUT; status=none; signal=SIGTERM'],
      [{ error: { code: 'ENOENT', message: privatePath }, status: null, signal: null }, 'error=ENOENT; status=none; signal=none'],
      [{ error: { code: 'ENOBUFS', message: privatePath }, status: null, signal: 'SIGTERM' }, 'error=ENOBUFS; status=none; signal=SIGTERM'],
      [{ status: 1, signal: null }, 'error=none; status=1; signal=none'],
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
  `;
  const child = spawnSync(process.execPath, ['--input-type=module', '-e', program], {
    encoding: 'utf8', timeout: 5000, maxBuffer: 8192,
  });
  assert.ifError(child.error);
  assert.equal(child.status, 0, child.stderr);
});
