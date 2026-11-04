import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdtempSync, mkdirSync, readFileSync, realpathSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';
import { validateBoundProviderSources, validateRetainedProviderSources, selectUpgradeProviders } from '../dist/installation-bindings.js';

const hash = bytes => createHash('sha256').update(bytes).digest('hex');
test('receipt-bound prior provider closure is checked without granting target qualification', () => {
  const root = realpathSync(mkdtempSync(join(tmpdir(), 'factory-retained-provider-'))), packageRoot = join(root, 'package');
  try {
    mkdirSync(packageRoot);
    const code = Buffer.from('throw new Error("provider must never run")\n');
    const metadata = Buffer.from('{"name":"@github/copilot","version":"1.0.100"}');
    writeFileSync(join(packageRoot, 'index.js'), code, { mode: 0o644 });
    writeFileSync(join(packageRoot, 'package.json'), metadata, { mode: 0o644 });
    const manifest = [{ path: 'index.js', bytes: code.length, mode: 0o644, sha256: hash(code) },
      { path: 'package.json', bytes: metadata.length, mode: 0o644, sha256: hash(metadata) }];
    const manifestFile = join(root, 'manifest.json');
    writeFileSync(manifestFile, JSON.stringify(manifest));
    const providers = { copilot: { packageRoot, manifestFile, version: '1.0.100', manifestSha256: hash(JSON.stringify(manifest)),
      model: 'old-model', reasoning: 'low', modes: ['read-only'] } };
    assert.doesNotThrow(() => validateRetainedProviderSources(providers));
    assert.throws(() => validateBoundProviderSources(providers), /bound Copilot source differs/);
    assert.deepEqual(readFileSync(join(packageRoot, 'index.js')), code);
    writeFileSync(join(packageRoot, 'index.js'), 'changed');
    assert.throws(() => validateRetainedProviderSources(providers), /closure mismatch/);
  } finally { rmSync(root, { recursive: true, force: true }); }
});


test('retained executable must still match its recorded bytes without qualifying a new target', () => {
  const root = realpathSync(mkdtempSync(join(tmpdir(), 'factory-retained-executable-')));
  try {
    const executable = join(root, 'codex'), bytes = Buffer.from('never execute this fixture\n');
    writeFileSync(executable, bytes, { mode: 0o700 });
    const providers = { codex: { executable, version: '0.162.0', sha256: hash(bytes), bytes: bytes.length,
      model: 'previous-model', reasoning: 'low', modes: ['read-only'] } };
    assert.doesNotThrow(() => validateRetainedProviderSources(providers));
    assert.throws(() => validateBoundProviderSources(providers), /bound Codex source differs/);
    writeFileSync(executable, 'modified');
    assert.throws(() => validateRetainedProviderSources(providers), /retained Codex source differs/);
  } finally { rmSync(root, { recursive: true, force: true }); }
});


test('upgrade inherits original provider selection unless an explicit selection is supplied', () => {
  const retained = { codex: { executable: '/private/tmp/selected-codex', version: '0.162.0', sha256: 'a'.repeat(64), bytes: 1,
    model: 'previous-model', reasoning: 'low', modes: ['read-only'] } };
  assert.deepEqual(selectUpgradeProviders(retained, undefined), { codex: { executable: '/private/tmp/selected-codex', modes: ['read-only'] } });
  assert.deepEqual(selectUpgradeProviders(retained, {}), {});
  const explicit = { copilot: { packageRoot: '/private/tmp/package', manifestFile: '/private/tmp/manifest', modes: ['read-only'] } };
  assert.deepEqual(selectUpgradeProviders(retained, explicit), explicit);
});
