import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdirSync, mkdtempSync, readFileSync, readdirSync, realpathSync, rmSync, symlinkSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';
import { validateInstallSelection } from '../dist/installation-bindings.js';
import { buildInputSnapshot, packageRelease, recordBuildReceipt } from '../src/release.ts';

const packageRoot = realpathSync(fileURLToPath(new URL('../', import.meta.url)));
const officialNode = {
  version: 'v24.22.1',
  url: 'https://nodejs.org/download/release/v24.22.1/node-v24.22.1-darwin-arm64.tar.xz',
  sha256: '654ba79de6155647e22321932b45f2a1ccb705976cc337c9b8e278beb085a628',
};
const linuxNode = {
  version: 'v24.22.1',
  url: 'https://nodejs.org/download/release/v24.22.1/node-v24.22.1-linux-x64.tar.xz',
  sha256: '6c172a9ab6718f7b801fb5a7bd486af2ee5e32758086a04b84fcce2aa77095e6',
};
const templates = [
  'agents.json', 'package.json', 'prompts/audit.md', 'prompts/implementation.md', 'prompts/planning.md',
  'prompts/recipe.md', 'prompts/review.md', 'workflows/audit.ts', 'workflows/change.ts',
  'workflows/evaluate.ts', 'workflows/learn.ts',
];
function modules(root = join(packageRoot, 'src'), prefix = '') {
  return readdirSync(root, { withFileTypes: true }).flatMap(entry => {
    const relative = prefix ? `${prefix}/${entry.name}` : entry.name;
    return entry.isDirectory() ? modules(join(root, entry.name), relative) : [relative.slice(0, -3)];
  });
}
function put(root, relative, bytes) {
  const path = join(root, relative);
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, bytes);
}
function fixture(platform = 'darwin-arm64') {
  const root = realpathSync(mkdtempSync(join(tmpdir(), 'factory-install-selection-')));
  const source = join(root, 'source');
  for (const module of modules()) {
    put(source, `src/${module}.ts`, 'export const fixture = true;\n');
    for (const extension of ['js', 'js.map', 'd.ts']) put(source, `dist/${module}.${extension}`, 'fixture\n');
  }
  for (const file of ['index.html', 'style.css', 'app.js']) {
    put(source, `web/${file}`, `web:${file}\n`);
    put(source, `dist/web/${file}`, `web:${file}\n`);
  }
  for (const file of templates) put(source, `templates/${file}`, readFileSync(join(packageRoot, 'templates', file)));
  for (const file of ['package.json', 'package-lock.json']) put(source, `toolchain/${file}`, readFileSync(join(packageRoot, 'toolchain', file)));
  for (const file of [
    'package.json', 'package-lock.json', 'tsconfig.json', 'scripts/build.mjs', 'scripts/package-release.mjs',
    'node_modules/typescript/package.json', `node_modules/@typescript/typescript-${process.platform}-${process.arch}/lib/tsc`,
    'node_modules/@types/node/index.d.ts', 'node_modules/undici-types/index.d.ts',
  ]) put(source, file, `build input:${file}\n`);
  recordBuildReceipt(source, buildInputSnapshot(source));
  const bundleRoot = join(root, 'bundle');
  const { manifestSha256 } = packageRelease({ version: '1.2.3', platform, node: platform === 'linux-x64' ? linuxNode : officialNode }, source, bundleRoot);
  const nodeArchivePath = join(root, 'node.tar.xz');
  put(root, 'node.tar.xz', 'changed official archive\n');
  return { root, bundleRoot, manifestSha256, nodeArchivePath,
    selection: { bundleRoot, manifestSha256, nodeArchivePath },
    dispose: () => rmSync(root, { recursive: true, force: true }) };
}

test('install selection refuses caller-owned support facts', () => {
  assert.throws(() => validateInstallSelection({
    bundleRoot: '/missing', manifestSha256: '0'.repeat(64), nodeArchivePath: '/missing',
    platform: 'darwin-arm64',
  }), /unknown|selection/i);
});

test('verified bundle cannot turn changed Node bytes or self-consistent Node metadata into a selection', () => {
  const f = fixture();
  try {
    assert.throws(() => validateInstallSelection(f.selection), /Node archive hash/i);
    const manifestPath = join(f.bundleRoot, 'release-manifest.json');
    const manifest = JSON.parse(readFileSync(manifestPath, 'utf8'));
    manifest.node.sha256 = createHash('sha256').update(readFileSync(f.nodeArchivePath)).digest('hex');
    const bytes = Buffer.from(`${JSON.stringify(manifest)}\n`);
    writeFileSync(manifestPath, bytes);
    assert.throws(() => validateInstallSelection({ ...f.selection, manifestSha256: createHash('sha256').update(bytes).digest('hex') }),
      /unqualified Node asset/i);
  } finally { f.dispose(); }
});

test('source path components and release payload must be canonical regular files', () => {
  const f = fixture();
  try {
    const alias = join(f.root, 'archive-alias');
    symlinkSync(f.nodeArchivePath, alias);
    assert.throws(() => validateInstallSelection({ ...f.selection, nodeArchivePath: alias }), /linked path/i);
    const linkedParent = join(f.root, 'linked-parent');
    symlinkSync(f.root, linkedParent);
    assert.throws(() => validateInstallSelection({ ...f.selection, nodeArchivePath: join(linkedParent, 'node.tar.xz') }), /linked path/i);
    put(f.bundleRoot, 'dist/learning.js', 'changed\n');
    assert.throws(() => validateInstallSelection(f.selection), /changed file hash/i);
  } finally { f.dispose(); }
});

test('provider bindings refuse unqualified modes, caller digests and changed executable bytes', () => {
  const f = fixture();
  try {
    const executable = join(f.root, 'codex');
    put(f.root, 'codex', 'impostor\n');
    assert.throws(() => validateInstallSelection({ ...f.selection, providers: { codex: { executable, modes: ['dangerous'] } } }),
      /unqualified provider modes/i);
    assert.throws(() => validateInstallSelection({ ...f.selection, providers: { codex: { executable, modes: Array(1) } } }),
      /unqualified provider modes/i);
    assert.throws(() => validateInstallSelection({ ...f.selection, providers: { codex: { executable, modes: ['read-only'], sha256: '0'.repeat(64) } } }),
      /unknown or missing selection field/i);
    assert.throws(() => validateInstallSelection({ ...f.selection, providers: { codex: { executable, modes: ['read-only'] } } }),
      /unqualified Codex executable hash/i);
    assert.throws(() => validateInstallSelection({ ...f.selection, providers: { copilot: { packageRoot: f.root, manifestFile: executable, modes: ['workspace-write'] } } }),
      /unqualified provider modes/i);
    assert.throws(() => validateInstallSelection({ ...f.selection, providers: { gemini: { packageRoot: f.root } } }),
      /unknown or missing selection field/i);
  } finally { f.dispose(); }
});

test('a valid Linux release cannot inherit Darwin native provider qualification', () => {
  const f = fixture('linux-x64');
  try {
    assert.throws(() => validateInstallSelection({ ...f.selection, providers: { codex: { executable: f.nodeArchivePath, modes: ['read-only'] } } }),
      /native provider platform unqualified/i);
  } finally { f.dispose(); }
});
