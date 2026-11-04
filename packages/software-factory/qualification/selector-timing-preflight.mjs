import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { cpSync, existsSync, lstatSync, mkdtempSync, readFileSync, realpathSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { buildInputSnapshot } from '../src/release.ts';

let scratch;
let scratchIdentity;
let passed = false;
try {
  assert.equal(process.version, 'v24.22.1');
  assert.equal(process.platform, 'darwin'); assert.equal(process.arch, 'arm64');
  const python = process.env.FACTORY_TEST_PYTHON, helper = process.env.FACTORY_ATOMIC_PYTHON;
  const seed = process.env.FACTORY_TEST_NPM_CACHE_SEED, npm = process.env.FACTORY_NPM_CLI;
  assert.ok(python && helper && seed && npm);
  assert.equal(realpathSync(python), realpathSync(helper));
  assert.equal(realpathSync(seed), seed); assert.ok(existsSync(join(seed, '_cacache')));
  const py = spawnSync(python, ['-I', '-c', 'import sys; print(".".join(map(str,sys.version_info[:3])))'], { encoding: 'utf8', timeout: 10000 });
  assert.equal(py.status, 0); assert.equal(py.stdout.trim(), '3.13.14');
  const node = spawnSync('node', ['-p', 'process.execPath'], { encoding: 'utf8', timeout: 10000 });
  assert.equal(node.status, 0); assert.equal(realpathSync(node.stdout.trim()), realpathSync(process.execPath));
  const root = fileURLToPath(new URL('../', import.meta.url));
  const receipt = JSON.parse(readFileSync(join(root, 'node_modules/.factory-build-receipt.json'), 'utf8'));
  const inputs = JSON.parse(buildInputSnapshot(realpathSync(root)));
  for (const key of Object.keys(inputs)) assert.deepEqual(receipt[key], inputs[key]);
  const hash = bytes => createHash('sha256').update(bytes).digest('hex');
  for (const entry of receipt.outputs) { const bytes = readFileSync(join(root, entry.path)); assert.equal(bytes.length, entry.bytes); assert.equal(hash(bytes), entry.sha256); }
  scratch = realpathSync(mkdtempSync(join(tmpdir(), 'selector-cache-preflight-')));
  scratchIdentity = lstatSync(scratch);
  for (const name of ['package.json', 'package-lock.json']) cpSync(join(root, 'toolchain', name), join(scratch, name));
  const cache = join(scratch, 'npm-cache'), userConfig = join(scratch, 'user.npmrc'), globalConfig = join(scratch, 'global.npmrc');
  cpSync(seed, cache, { recursive: true });
  for (const file of [userConfig, globalConfig]) writeFileSync(file, '', { mode: 0o600 });
  const npmEnvironment = Object.fromEntries(Object.entries(process.env).filter(([key]) => !key.toLowerCase().startsWith('npm_config_')));
  const installed = spawnSync(process.execPath, [realpathSync(npm), 'ci', '--ignore-scripts', '--offline', '--cache', cache, '--audit=false', '--fund=false'], {
    cwd: scratch, encoding: 'utf8', timeout: 120000, maxBuffer: 1048576,
    env: { ...npmEnvironment, NPM_CONFIG_USERCONFIG: userConfig, NPM_CONFIG_GLOBALCONFIG: globalConfig },
  });
  assert.equal(installed.status, 0);
  assert.equal(JSON.parse(readFileSync(join(scratch, 'node_modules/undici-types/package.json'), 'utf8')).version, '7.24.6');
  passed = true;
} catch { process.stderr.write('factory selector timing preflight: refused\n'); process.exitCode = 1; }
finally {
  if (scratch) {
    try {
      const current = lstatSync(scratch);
      assert.ok(scratchIdentity && current.isDirectory() && !current.isSymbolicLink() && current.dev === scratchIdentity.dev && current.ino === scratchIdentity.ino && realpathSync(scratch) === scratch);
      rmSync(scratch, { recursive: true, force: true });
    } catch { process.stderr.write('factory selector timing preflight: refused\n'); process.exitCode = 1; }
  }
}
if (passed && !process.exitCode) process.stdout.write('factory selector timing preflight: passed\n');
