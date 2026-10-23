import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdirSync, mkdtempSync, realpathSync, rmSync, symlinkSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

const script = fileURLToPath(new URL('../../../skills/software-factory/scripts/install.py', import.meta.url));
const python = process.env.FACTORY_TEST_PYTHON ?? 'python3';

test('public verify, prepare and install reject an unsafe provider selector before selected JavaScript', () => {
  const root = realpathSync(mkdtempSync(join(tmpdir(), 'factory-provider-public-')));
  try {
    const providers = join(root, 'providers.json');
    writeFileSync(providers, '{"codex":{"executable":"relative","modes":["read-only"]}}\n');
    for (const command of ['verify', 'prepare', 'install']) {
      const result = spawnSync(python, [script, command,
        ...(command === 'verify' ? [] : ['--repository', root]),
        '--bundle-root', join(root, 'bundle'), '--manifest-sha256', '0'.repeat(64),
        '--node-archive', join(root, 'node.tar.xz'), '--providers', providers],
      { encoding: 'utf8', timeout: 30_000 });
      assert.equal(result.status, 1, `${command}: ${result.stderr}`);
      assert.match(result.stderr, /provider selection refused/i);
      assert.doesNotMatch(result.stderr, /relative|providers\.json|Traceback/);
    }
  } finally { rmSync(root, { recursive: true, force: true }); }
});

test('public selector refuses duplicate, extra, oversized, deep, linked and unsupported descriptors', () => {
  const root = realpathSync(mkdtempSync(join(tmpdir(), 'factory-provider-refusals-')));
  try {
    const executable = join(root, 'codex');
    const packageRoot = join(root, 'copilot');
    const manifestFile = join(root, 'copilot-manifest.json');
    writeFileSync(executable, 'disposable bytes');
    mkdirSync(packageRoot);
    writeFileSync(manifestFile, '{}');
    symlinkSync(executable, join(root, 'linked-codex'));
    const cases = [
      '{"codex":{},"codex":{}}',
      JSON.stringify({ gemini: { executable, modes: ['read-only'] } }),
      JSON.stringify({ codex: { executable, modes: ['read-only'], account: 'private' } }),
      JSON.stringify({ codex: { executable, modes: ['read-only', 'read-only'] } }),
      JSON.stringify({ copilot: { packageRoot, manifestFile, modes: ['workspace-write'] } }),
      JSON.stringify({ codex: { executable: join(root, 'linked-codex'), modes: ['read-only'] } }),
      JSON.stringify({ codex: { executable, modes: [['read-only']] } }),
      JSON.stringify({ codex: { executable, modes: ['read-only'] }, extra: { nested: { too: { deep: true } } } }),
      ' '.repeat(4097),
    ];
    const providers = join(root, 'providers.json');
    for (const [index, content] of cases.entries()) {
      writeFileSync(providers, content);
      const result = spawnSync(python, [script, 'verify', '--bundle-root', join(root, 'bundle'),
        '--manifest-sha256', '0'.repeat(64), '--node-archive', join(root, 'node.tar.xz'), '--providers', providers],
      { encoding: 'utf8', timeout: 30_000 });
      assert.equal(result.status, 1, `${index}: ${result.stderr}`);
      assert.match(result.stderr, /provider selection refused/i, `${index}: ${result.stderr}`);
      assert.doesNotMatch(result.stderr, /codex|copilot-manifest|Traceback/);
    }
    const linkedDescriptor = join(root, 'linked-providers.json');
    symlinkSync(providers, linkedDescriptor);
    const linked = spawnSync(python, [script, 'verify', '--bundle-root', join(root, 'bundle'),
      '--manifest-sha256', '0'.repeat(64), '--node-archive', join(root, 'node.tar.xz'), '--providers', linkedDescriptor],
    { encoding: 'utf8', timeout: 30_000 });
    assert.equal(linked.status, 1);
    assert.match(linked.stderr, /provider selection refused/i);
  } finally { rmSync(root, { recursive: true, force: true }); }
});

test('public selector accepts the bounded provider shape and continues to release authentication', () => {
  const root = realpathSync(mkdtempSync(join(tmpdir(), 'factory-provider-shape-')));
  try {
    const executable = join(root, 'codex');
    const providers = join(root, 'providers.json');
    writeFileSync(executable, 'disposable nonqualified bytes');
    writeFileSync(providers, JSON.stringify({ codex: { executable, modes: ['read-only', 'workspace-write'] } }));
    const result = spawnSync(python, [script, 'verify', '--bundle-root', join(root, 'absent-bundle'),
      '--manifest-sha256', '0'.repeat(64), '--node-archive', join(root, 'absent-node.tar.xz'), '--providers', providers],
    { encoding: 'utf8', timeout: 30_000 });
    assert.equal(result.status, 1);
    assert.doesNotMatch(result.stderr, /provider selection refused|Traceback/i);
    assert.match(result.stderr, /source|bundle/i);
  } finally { rmSync(root, { recursive: true, force: true }); }
});
