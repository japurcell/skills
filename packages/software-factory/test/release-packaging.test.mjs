import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { existsSync, mkdirSync, mkdtempSync, readFileSync, readdirSync, rmSync, symlinkSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { spawnSync } from 'node:child_process';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

const command = fileURLToPath(new URL('../scripts/package-release.mjs', import.meta.url));
const officialNode = {
  version: 'v24.22.1',
  url: 'https://nodejs.org/download/release/v24.22.1/node-v24.22.1-darwin-arm64.tar.xz',
  sha256: '654ba79de6155647e22321932b45f2a1ccb705976cc337c9b8e278beb085a628',
};
const requiredTemplates = [
  'agents.json', 'prompts/audit.md', 'prompts/implementation.md', 'prompts/planning.md',
  'prompts/recipe.md', 'prompts/review.md', 'workflows/audit.ts', 'workflows/change.ts',
  'workflows/evaluate.ts', 'workflows/learn.ts',
];

function put(root, relative, content) {
  const path = join(root, relative);
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, content);
}

function fixture() {
  const root = mkdtempSync(join(tmpdir(), 'factory-release-test-'));
  const source = join(root, 'source');
  for (const module of ['cli', 'learning', 'release']) {
    put(source, `src/${module}.ts`, `export const ${module} = true;\n`);
    put(source, `dist/${module}.js`, `export const ${module} = true;\n`);
    put(source, `dist/${module}.js.map`, '{}\n');
    put(source, `dist/${module}.d.ts`, `export declare const ${module} = true;\n`);
  }
  for (const file of ['index.html', 'style.css', 'app.js']) {
    put(source, `web/${file}`, `web:${file}\n`);
    put(source, `dist/web/${file}`, `web:${file}\n`);
  }
  for (const file of requiredTemplates) put(source, `templates/${file}`, `template:${file}\n`);
  put(source, 'node_modules/dev-only.js', 'secret development dependency\n');
  const descriptorPath = join(root, 'selection.json');
  const destination = join(root, 'release');
  const selection = { version: '1.2.3', platform: 'darwin-arm64', node: officialNode };
  const run = () => spawnSync(process.execPath, [command, '--descriptor', descriptorPath, '--source-root', source, '--destination', destination], { encoding: 'utf8' });
  const select = value => writeFileSync(descriptorPath, `${JSON.stringify(value)}\n`);
  select(selection);
  return { root, source, destination, selection, run, select, dispose: () => rmSync(root, { recursive: true, force: true }) };
}

test('explicit release command owns a deterministic complete payload and safe repeat', () => {
  const f = fixture();
  try {
    let result = f.run();
    assert.equal(result.status, 0, result.stderr);
    const first = readFileSync(join(f.destination, 'release-manifest.json'), 'utf8');
    const manifest = JSON.parse(first);
    assert.equal(manifest.version, '1.2.3');
    assert.equal(manifest.platform, 'darwin-arm64');
    assert.deepEqual(manifest.node, officialNode);
    assert.ok(manifest.files.some(file => file.path === 'dist/learning.js'));
    assert.ok(manifest.files.some(file => file.path === 'dist/web/index.html'));
    assert.ok(manifest.files.some(file => file.path === 'templates/workflows/learn.ts'));
    assert.ok(manifest.files.some(file => file.path === 'package.json'));
    assert.equal(existsSync(join(f.destination, 'node_modules')), false);
    assert.deepEqual(manifest.files.map(file => file.path), [...manifest.files.map(file => file.path)].sort());
    for (const file of manifest.files) {
      const bytes = readFileSync(join(f.destination, file.path));
      assert.equal(createHash('sha256').update(bytes).digest('hex'), file.sha256);
      assert.equal(bytes.length, file.bytes);
    }
    result = f.run();
    assert.equal(result.status, 0, result.stderr);
    assert.equal(readFileSync(join(f.destination, 'release-manifest.json'), 'utf8'), first);
    assert.deepEqual(readdirSync(f.root).filter(name => name.startsWith('.release-')), []);
  } finally { f.dispose(); }
});

test('existing changed or unowned payload refuses repeat without deleting evidence', () => {
  const f = fixture();
  try {
    assert.equal(f.run().status, 0);
    put(f.destination, 'dist/learning.js', 'tampered\n');
    const result = f.run();
    assert.equal(result.status, 1);
    assert.match(result.stderr, /hash|changed|integrity/i);
    assert.equal(readFileSync(join(f.destination, 'dist/learning.js'), 'utf8'), 'tampered\n');
    put(f.destination, 'dist/learning.js', 'export const learning = true;\n');
    put(f.destination, 'unowned.txt', 'keep me\n');
    const unowned = f.run();
    assert.equal(unowned.status, 1);
    assert.match(unowned.stderr, /unowned/i);
    assert.equal(readFileSync(join(f.destination, 'unowned.txt'), 'utf8'), 'keep me\n');
    rmSync(join(f.destination, 'unowned.txt'));
    mkdirSync(join(f.destination, 'orphan'));
    const emptyDirectory = f.run();
    assert.equal(emptyDirectory.status, 1);
    assert.match(emptyDirectory.stderr, /unowned/i);
    rmSync(join(f.destination, 'orphan'), { recursive: true });
    rmSync(join(f.destination, 'dist/cli.js'));
    const missing = f.run();
    assert.equal(missing.status, 1);
    assert.equal(existsSync(join(f.destination, 'release-manifest.json')), true);
  } finally { f.dispose(); }
});

test('exact Linux asset selection packages the same runtime surface without a native helper', () => {
  const f = fixture();
  try {
    const linuxNode = {
      version: 'v24.22.1',
      url: 'https://nodejs.org/download/release/v24.22.1/node-v24.22.1-linux-x64.tar.xz',
      sha256: '6c172a9ab6718f7b801fb5a7bd486af2ee5e32758086a04b84fcce2aa77095e6',
    };
    f.select({ ...f.selection, platform: 'linux-x64', node: linuxNode });
    const result = f.run();
    assert.equal(result.status, 0, result.stderr);
    const manifest = JSON.parse(readFileSync(join(f.destination, 'release-manifest.json'), 'utf8'));
    assert.deepEqual(manifest.node, linuxNode);
    assert.equal(manifest.platform, 'linux-x64');
    assert.equal(existsSync(join(f.destination, 'native')), false);
  } finally { f.dispose(); }
});

test('public bundle validator requires an external manifest hash and refuses traversal or duplicate claims', async () => {
  const { validateReleaseBundle } = await import('../dist/release.js');
  const f = fixture();
  try {
    assert.equal(f.run().status, 0);
    const manifestPath = join(f.destination, 'release-manifest.json');
    const original = readFileSync(manifestPath);
    const digest = createHash('sha256').update(original).digest('hex');
    assert.equal(validateReleaseBundle(f.destination, digest).version, '1.2.3');
    assert.throws(() => validateReleaseBundle(f.destination), /manifest hash/i);
    assert.throws(() => validateReleaseBundle(f.destination, '0'.repeat(64)), /manifest hash/i);
    const manifest = JSON.parse(original.toString('utf8'));
    manifest.files[0].path = '../outside';
    let bytes = Buffer.from(`${JSON.stringify(manifest)}\n`);
    writeFileSync(manifestPath, bytes);
    assert.throws(() => validateReleaseBundle(f.destination, createHash('sha256').update(bytes).digest('hex')), /unsafe manifest path/i);
    manifest.files[0] = { ...manifest.files[1] };
    bytes = Buffer.from(`${JSON.stringify(manifest)}\n`);
    writeFileSync(manifestPath, bytes);
    assert.throws(() => validateReleaseBundle(f.destination, createHash('sha256').update(bytes).digest('hex')), /duplicate manifest file/i);
  } finally { f.dispose(); }
});

test('source symlink and stale built web refuse packaging', () => {
  const f = fixture();
  try {
    symlinkSync(join(f.source, 'dist/learning.js'), join(f.source, 'dist/extra.js'));
    let result = f.run();
    assert.equal(result.status, 1);
    assert.match(result.stderr, /symlink|unexpected/i);
    assert.equal(existsSync(f.destination), false);
    rmSync(join(f.source, 'dist/extra.js'));
    put(f.source, 'dist/web/app.js', 'stale\n');
    result = f.run();
    assert.equal(result.status, 1);
    assert.match(result.stderr, /stale|web/i);
    assert.equal(existsSync(f.destination), false);
  } finally { f.dispose(); }
});

test('output inside the source tree refuses before creating a recursive payload', () => {
  const f = fixture();
  try {
    const nested = join(f.source, 'release');
    const result = spawnSync(process.execPath, [command, '--descriptor', join(f.root, 'selection.json'), '--source-root', f.source, '--destination', nested], { encoding: 'utf8' });
    assert.equal(result.status, 1);
    assert.match(result.stderr, /destination|source/i);
    assert.equal(existsSync(nested), false);
  } finally { f.dispose(); }
});

test('selection requires exact version, platform and pinned Node asset', () => {
  const f = fixture();
  try {
    for (const selection of [
      { ...f.selection, version: '../escape' },
      { ...f.selection, platform: 'linux-arm64' },
      { ...f.selection, node: { ...officialNode, version: 'v24.21.0' } },
      { ...f.selection, node: { ...officialNode, sha256: '0'.repeat(64) } },
    ]) {
      f.select(selection);
      const result = f.run();
      assert.equal(result.status, 1, result.stderr);
      assert.equal(existsSync(f.destination), false);
    }
  } finally { f.dispose(); }
});

test('Windows refuses missing, unqualified and changed required native helper', () => {
  const f = fixture();
  try {
    const winNode = {
      version: 'v24.22.1',
      url: 'https://nodejs.org/download/release/v24.22.1/node-v24.22.1-win-x64.zip',
      sha256: 'd2046d28c2c3dcd211ac5145c0bf30e2047ef9dfb306693c8c6e2eccd8b95fa5',
    };
    f.select({ ...f.selection, platform: 'win32-x64', node: winNode });
    assert.equal(f.run().status, 1);
    const helperPath = join(f.root, 'windows-notify.exe');
    writeFileSync(helperPath, 'fake binary');
    f.select({ ...f.selection, platform: 'win32-x64', node: winNode, windowsHelper: {
      path: helperPath, sha256: createHash('sha256').update('fake binary').digest('hex'), qualificationRun: '39808257041',
    } });
    const result = f.run();
    assert.equal(result.status, 1);
    assert.match(result.stderr, /qualified|helper/i);
    f.select({ ...f.selection, platform: 'win32-x64', node: winNode, windowsHelper: {
      path: helperPath,
      sha256: 'f46ba4a408f8618d5e186ce29cf47bdac3411b67356136d79da4a0ed0c35ec44',
      qualificationRun: '39808257041',
    } });
    const changed = f.run();
    assert.equal(changed.status, 1);
    assert.match(changed.stderr, /changed Windows helper hash/i);
    assert.equal(existsSync(f.destination), false);
  } finally { f.dispose(); }
});
