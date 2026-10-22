import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { cpSync, existsSync, mkdirSync, mkdtempSync, readFileSync, readdirSync, rmSync, symlinkSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { spawnSync } from 'node:child_process';
import test from 'node:test';
import { fileURLToPath } from 'node:url';
import { buildInputSnapshot, recordBuildReceipt } from '../src/release.ts';

const command = fileURLToPath(new URL('../scripts/package-release.mjs', import.meta.url));
const officialNode = {
  version: 'v24.22.1',
  url: 'https://nodejs.org/download/release/v24.22.1/node-v24.22.1-darwin-arm64.tar.xz',
  sha256: '654ba79de6155647e22321932b45f2a1ccb705976cc337c9b8e278beb085a628',
};
const requiredTemplates = [
  'agents.json', 'package.json', 'prompts/audit.md', 'prompts/implementation.md', 'prompts/planning.md',
  'prompts/recipe.md', 'prompts/review.md', 'workflows/audit.ts', 'workflows/change.ts',
  'workflows/evaluate.ts', 'workflows/learn.ts',
];
const packageRoot = resolve(fileURLToPath(new URL('../', import.meta.url)));

function sourceModules(root = join(packageRoot, 'src'), prefix = '') {
  return readdirSync(root, { withFileTypes: true }).flatMap(entry => {
    const relative = prefix ? `${prefix}/${entry.name}` : entry.name;
    return entry.isDirectory() ? sourceModules(join(root, entry.name), relative) : [relative.slice(0, -3)];
  });
}

function put(root, relative, content) {
  const path = join(root, relative);
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, content);
}

function fixture() {
  const root = mkdtempSync(join(tmpdir(), 'factory-release-test-'));
  const source = join(root, 'source');
  for (const module of sourceModules()) {
    put(source, `src/${module}.ts`, 'export const fixture = true;\n');
    put(source, `dist/${module}.js`, 'export const fixture = true;\n');
    put(source, `dist/${module}.js.map`, '{}\n');
    put(source, `dist/${module}.d.ts`, 'export declare const fixture = true;\n');
  }
  for (const file of ['index.html', 'style.css', 'app.js']) {
    put(source, `web/${file}`, `web:${file}\n`);
    put(source, `dist/web/${file}`, `web:${file}\n`);
  }
  for (const file of requiredTemplates) put(source, `templates/${file}`, readFileSync(join(packageRoot, 'templates', file)));
  for (const file of ['package.json', 'package-lock.json']) put(source, `toolchain/${file}`, readFileSync(join(packageRoot, 'toolchain', file)));
  for (const file of [
    'package.json', 'package-lock.json', 'tsconfig.json', 'scripts/build.mjs', 'scripts/package-release.mjs',
    'node_modules/typescript/package.json',
    `node_modules/@typescript/typescript-${process.platform}-${process.arch}/lib/tsc`,
    'node_modules/@types/node/index.d.ts', 'node_modules/undici-types/index.d.ts',
  ]) put(source, file, `build input:${file}\n`);
  put(source, 'node_modules/dev-only.js', 'secret development dependency\n');
  recordBuildReceipt(source, buildInputSnapshot(source));
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
    assert.equal(manifest.schema, 2);
    assert.equal(manifest.platform, 'darwin-arm64');
    assert.deepEqual(manifest.node, officialNode);
    assert.ok(manifest.files.some(file => file.path === 'dist/learning.js'));
    for (const path of ['dist/notifications.js', 'dist/notifications.js.map', 'dist/notifications.d.ts']) {
      assert.ok(manifest.files.some(file => file.path === path), path);
    }
    assert.ok(manifest.files.some(file => file.path === 'dist/web/index.html'));
    assert.ok(manifest.files.some(file => file.path === 'templates/workflows/learn.ts'));
    assert.ok(manifest.files.some(file => file.path === 'templates/package.json'));
    assert.ok(manifest.files.some(file => file.path === 'toolchain/package.json'));
    assert.ok(manifest.files.some(file => file.path === 'toolchain/package-lock.json'));
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

test('externally selected digest binds the complete authoring and toolchain contract', async () => {
  const { validateReleaseBundle } = await import('../dist/release.js');
  for (const path of ['templates/package.json', 'toolchain/package.json', 'toolchain/package-lock.json']) {
    const f = fixture();
    try {
      const packaged = f.run();
      assert.equal(packaged.status, 0, packaged.stderr);
      const manifestPath = join(f.destination, 'release-manifest.json');
      const manifestBytes = readFileSync(manifestPath);
      const selectedDigest = createHash('sha256').update(manifestBytes).digest('hex');
      assert.equal(validateReleaseBundle(f.destination, selectedDigest).schema, 2);
      put(f.destination, path, 'changed\n');
      assert.throws(() => validateReleaseBundle(f.destination, selectedDigest), /changed file hash/i);
      rmSync(join(f.destination, path));
      assert.throws(() => validateReleaseBundle(f.destination, selectedDigest));
      const manifest = JSON.parse(manifestBytes.toString('utf8'));
      manifest.files = manifest.files.filter(file => file.path !== path);
      const rewritten = Buffer.from(`${JSON.stringify(manifest)}\n`);
      writeFileSync(manifestPath, rewritten);
      assert.throws(() => validateReleaseBundle(f.destination, createHash('sha256').update(rewritten).digest('hex')), /incomplete release payload/i);
    } finally { f.dispose(); }
  }
});

test('consumer refuses a self-consistent manifest with altered authoring or dependency semantics', async () => {
  const { validateReleaseBundle } = await import('../dist/release.js');
  for (const [path, change] of [
    ['templates/package.json', value => { value.type = 'commonjs'; }],
    ['toolchain/package.json', value => { value.dependencies.typescript = '7.0.3'; }],
    ['toolchain/package-lock.json', value => { delete value.packages['node_modules/undici-types']; }],
    ['toolchain/package-lock.json', value => { value.packages['node_modules/playwright'] = value.packages['node_modules/typescript']; }],
  ]) {
    const f = fixture();
    try {
      const packaged = f.run();
      assert.equal(packaged.status, 0, packaged.stderr);
      const changed = JSON.parse(readFileSync(join(f.destination, path), 'utf8'));
      change(changed);
      const fileBytes = Buffer.from(`${JSON.stringify(changed)}\n`);
      writeFileSync(join(f.destination, path), fileBytes);
      const manifestPath = join(f.destination, 'release-manifest.json');
      const manifest = JSON.parse(readFileSync(manifestPath, 'utf8'));
      const entry = manifest.files.find(file => file.path === path);
      entry.bytes = fileBytes.length;
      entry.sha256 = createHash('sha256').update(fileBytes).digest('hex');
      const manifestBytes = Buffer.from(`${JSON.stringify(manifest)}\n`);
      writeFileSync(manifestPath, manifestBytes);
      const selectedDigest = createHash('sha256').update(manifestBytes).digest('hex');
      assert.throws(() => validateReleaseBundle(f.destination, selectedDigest), /authoring|toolchain|dependency/i, path);
    } finally { f.dispose(); }
  }
});

test('dedicated release toolchain lock installs only pinned compiler and Node types offline', () => {
  const f = fixture();
  const installation = join(f.root, 'installation');
  try {
    const packaged = f.run();
    assert.equal(packaged.status, 0, packaged.stderr);
    mkdirSync(installation);
    for (const file of ['package.json', 'package-lock.json']) cpSync(join(f.destination, 'toolchain', file), join(installation, file));
    const result = spawnSync('npm', ['ci', '--ignore-scripts', '--offline', '--cache', '/tmp/software-factory-npm-cache', '--audit=false', '--fund=false'], { cwd: installation, encoding: 'utf8' });
    assert.equal(result.status, 0, result.stderr);
    assert.equal(JSON.parse(readFileSync(join(installation, 'node_modules/typescript/package.json'), 'utf8')).version, '7.0.2');
    assert.equal(JSON.parse(readFileSync(join(installation, 'node_modules/@types/node/package.json'), 'utf8')).version, '24.19.2');
    assert.equal(JSON.parse(readFileSync(join(installation, 'node_modules/undici-types/package.json'), 'utf8')).version, '7.24.6');
    assert.equal(existsSync(join(installation, 'node_modules/playwright')), false);
    assert.equal(existsSync(join(installation, 'node_modules/@playwright')), false);
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
    put(f.destination, 'dist/learning.js', 'export const fixture = true;\n');
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

test('consumer rejects a self-consistent manifest with a missing runtime import or declaration', async () => {
  const { validateReleaseBundle } = await import('../dist/release.js');
  for (const missing of ['dist/redaction.js', 'dist/workflow.d.ts']) {
    const f = fixture();
    try {
      assert.equal(f.run().status, 0);
      const manifestPath = join(f.destination, 'release-manifest.json');
      const manifest = JSON.parse(readFileSync(manifestPath, 'utf8'));
      manifest.files = manifest.files.filter(file => file.path !== missing);
      rmSync(join(f.destination, missing));
      const bytes = Buffer.from(`${JSON.stringify(manifest)}\n`);
      writeFileSync(manifestPath, bytes);
      const digest = createHash('sha256').update(bytes).digest('hex');
      assert.throws(() => validateReleaseBundle(f.destination, digest), /incomplete release payload/i);
    } finally { f.dispose(); }
  }
});

test('portable Windows names are refused at consumer and packaging seams', async () => {
  const { validateReleaseBundle } = await import('../dist/release.js');
  const reservedNames = [
    'CON', 'PRN', 'AUX', 'NUL',
    ...Array.from({ length: 9 }, (_, index) => 'COM' + (index + 1)),
    ...Array.from({ length: 9 }, (_, index) => 'LPT' + (index + 1)),
    'COM¹', 'COM²', 'COM³', 'LPT¹', 'LPT²', 'LPT³',
  ];
  const invalidPaths = [
    ...['<', '>', ':', '"', '|', '?', '*'].map(character => 'dist/bad' + character + '.ts'),
    'dist/bad\\name.ts',
    ...Array.from({ length: 32 }, (_, code) => 'dist/bad' + String.fromCharCode(code) + '.ts'),
    ...reservedNames.flatMap(name => ['dist/' + name, 'dist/' + name + '.txt']),
    'dist/trailing.',
    'dist/trailing ',
  ];
  const f = fixture();
  try {
    const result = f.run();
    assert.equal(result.status, 0, result.stderr);
    const manifestPath = join(f.destination, 'release-manifest.json');
    const original = readFileSync(manifestPath);
    const originalPayloadPath = JSON.parse(original.toString('utf8')).files[0].path;
    assert.equal(existsSync(join(f.destination, originalPayloadPath)), true);
    for (const invalidPath of invalidPaths) {
      const manifest = JSON.parse(original.toString('utf8'));
      manifest.files[0].path = invalidPath;
      const bytes = Buffer.from(JSON.stringify(manifest) + '\n');
      writeFileSync(manifestPath, bytes);
      const digest = createHash('sha256').update(bytes).digest('hex');
      assert.throws(
        () => validateReleaseBundle(f.destination, digest),
        /unsafe manifest path/i,
        invalidPath,
      );
    }
  } finally { f.dispose(); }

  // The consumer checks above run on Windows without creating invalid files.
  if (process.platform === 'win32') return;
  for (const unsafe of ['bad?.ts', 'bad*.ts', 'bad<.ts', 'bad>.ts', 'bad".ts', 'bad|.ts', 'COM¹.ts', 'COM².ts', 'COM³.ts', 'LPT¹.ts', 'LPT².ts', 'LPT³.ts']) {
    const sourceFixture = fixture();
    try {
      put(sourceFixture.source, 'src/' + unsafe, 'export const fixture = true;\n');
      for (const ext of ['.js', '.js.map', '.d.ts']) put(sourceFixture.source, 'dist/' + unsafe.slice(0, -3) + ext, 'fixture\n');
      const packaging = sourceFixture.run();
      assert.equal(packaging.status, 1, unsafe + ': ' + packaging.stderr);
      assert.match(packaging.stderr, /unsafe manifest path/i);
      assert.equal(existsSync(sourceFixture.destination), false);
    } finally { sourceFixture.dispose(); }
  }
});

test('changed source with unchanged compiled output cannot be packaged', () => {
  const f = fixture();
  try {
    put(f.source, 'src/learning.ts', 'export const fixture = false;\n');
    const result = f.run();
    assert.equal(result.status, 1, result.stderr);
    assert.match(result.stderr, /stale|build|source|receipt/i);
    assert.equal(existsSync(f.destination), false);
  } finally { f.dispose(); }
});

test('missing receipt, changed toolchain and changed output all refuse packaging', () => {
  for (const change of [
    source => rmSync(join(source, 'node_modules/.factory-build-receipt.json')),
    source => put(source, 'node_modules/typescript/package.json', 'changed compiler metadata\n'),
    source => put(source, 'dist/learning.js', 'stale output\n'),
    source => put(source, 'toolchain/package-lock.json', `${readFileSync(join(source, 'toolchain/package-lock.json'), 'utf8')}\n`),
  ]) {
    const f = fixture();
    try {
      change(f.source);
      const result = f.run();
      assert.equal(result.status, 1, result.stderr);
      assert.equal(existsSync(f.destination), false);
    } finally { f.dispose(); }
  }
});

test('build receipt refuses source mutation between snapshots', () => {
  const f = fixture();
  try {
    const before = buildInputSnapshot(f.source);
    rmSync(join(f.source, 'node_modules/.factory-build-receipt.json'));
    put(f.source, 'src/learning.ts', 'export const fixture = false;\n');
    assert.throws(() => recordBuildReceipt(f.source, before), /changed during build/i);
    assert.equal(existsSync(join(f.source, 'node_modules/.factory-build-receipt.json')), false);
  } finally { f.dispose(); }
});

test('consumer runs the actual built release CLI help from a selected bundle', async () => {
  const { validateReleaseBundle } = await import('../dist/release.js');
  const root = mkdtempSync(join(tmpdir(), 'factory-release-consumer-'));
  try {
    const descriptorPath = join(root, 'selection.json');
    const destination = join(root, 'bundle');
    writeFileSync(descriptorPath, `${JSON.stringify({ version: '1.2.3', platform: 'darwin-arm64', node: officialNode })}\n`);
    const result = spawnSync(process.execPath, [command, '--descriptor', descriptorPath, '--source-root', packageRoot, '--destination', destination], { encoding: 'utf8' });
    assert.equal(result.status, 0, result.stderr);
    const digest = JSON.parse(result.stdout).manifestSha256;
    assert.equal(validateReleaseBundle(destination, digest).version, '1.2.3');
    const help = spawnSync(process.execPath, [join(destination, 'dist/cli.js'), '--help'], { encoding: 'utf8' });
    assert.equal(help.status, 0, help.stderr);
    assert.match(help.stdout, /software-factory/);
  } finally { rmSync(root, { recursive: true, force: true }); }
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
