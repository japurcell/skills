import assert from 'node:assert/strict';
import { spawn, spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { existsSync, mkdtempSync, readFileSync, readdirSync, realpathSync, rmSync, statSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

// Run explicitly with the exact local official archive. Missing native inputs
// fail before test registration; this suite has no platform skips.
const archive = process.env.FACTORY_TEST_NODE_ARCHIVE;
assert.ok(archive, 'FACTORY_TEST_NODE_ARCHIVE is required for native bootstrap qualification');
assert.equal(process.platform, 'darwin', 'native bootstrap qualification currently requires macOS arm64');
assert.equal(process.arch, 'arm64', 'native bootstrap qualification currently requires macOS arm64');
assert.equal(archive, realpathSync(archive), 'native archive path must be canonical');
const nodeAsset = { version: 'v24.22.1', url: 'https://nodejs.org/download/release/v24.22.1/node-v24.22.1-darwin-arm64.tar.xz', sha256: '654ba79de6155647e22321932b45f2a1ccb705976cc337c9b8e278beb085a628' };
const sha = bytes => createHash('sha256').update(bytes).digest('hex');
assert.equal(sha(readFileSync(archive)), nodeAsset.sha256, 'native archive must match exact release pin');
const python = process.env.FACTORY_TEST_PYTHON ?? 'python3';
const prerequisite = spawnSync(python, ['-c', 'import sys; assert sys.version_info >= (3, 11), "Python 3.11+ required"'], { encoding: 'utf8' });
assert.equal(prerequisite.status, 0, `Python 3.11+ prerequisite failed: ${prerequisite.error?.message ?? prerequisite.stderr}`);
const script = resolve(fileURLToPath(new URL('../../../skills/software-factory/scripts/install.py', import.meta.url)));
const packageRoot = resolve(fileURLToPath(new URL('../', import.meta.url)));
const packageCommand = join(packageRoot, 'scripts/package-release.mjs');

function fixture() {
  const root = realpathSync(mkdtempSync(join(tmpdir(), 'factory-bootstrap-native-')));
  const bundle = join(root, 'bundle');
  const selection = join(root, 'selection.json');
  writeFileSync(selection, JSON.stringify({ version: '1.2.3', platform: 'darwin-arm64', node: nodeAsset }));
  const packaged = spawnSync(process.execPath, [packageCommand, '--descriptor', selection, '--source-root', packageRoot, '--destination', bundle], { encoding: 'utf8' });
  assert.equal(packaged.status, 0, packaged.stderr);
  const manifestSha256 = JSON.parse(packaged.stdout).manifestSha256;
  const verify = () => spawnSync(python, [script, 'verify', '--bundle-root', bundle, '--manifest-sha256', manifestSha256, '--node-archive', archive], { encoding: 'utf8' });
  return { root, bundle, manifestSha256, verify, dispose: () => rmSync(root, { recursive: true, force: true }) };
}

test('native public verifier executes authenticated snapshot with exact pinned Node', () => {
  const f = fixture();
  try {
    const result = f.verify();
    assert.equal(result.status, 0, result.stderr);
    const receipt = JSON.parse(result.stdout);
    assert.deepEqual({ schema: receipt.schema, platform: receipt.platform, manifestSha256: receipt.manifestSha256, nodeSha256: receipt.nodeSha256, archiveMembers: receipt.archiveMembers, omittedLinks: receipt.omittedLinks },
      { schema: 1, platform: 'darwin-arm64', manifestSha256: f.manifestSha256, nodeSha256: nodeAsset.sha256, archiveMembers: 5888, omittedLinks: ['bin/corepack', 'bin/npm', 'bin/npx'] });
  } finally { f.dispose(); }
});

test('native preparation runs direct regular Node and npm with no extracted links', () => {
  const f = fixture();
  try {
    const driver = `import importlib.util,json,pathlib,subprocess,sys\n` +
      `s=importlib.util.spec_from_file_location('factory_install',sys.argv[1]); m=importlib.util.module_from_spec(s); sys.modules[s.name]=m; s.loader.exec_module(m)\n` +
      `with m.prepare_install_selection(sys.argv[2],sys.argv[3],sys.argv[4]) as prepared:\n` +
      ` node=prepared.extracted_node_root/'bin/node'; npm=prepared.extracted_node_root/'lib/node_modules/npm/bin/npm-cli.js'\n` +
      ` assert not any(path.is_symlink() for path in prepared.extracted_node_root.rglob('*'))\n` +
      ` version=subprocess.run([str(node),'--version'],check=True,capture_output=True,text=True,timeout=10).stdout.strip()\n` +
      ` npm_version=subprocess.run([str(node),str(npm),'--version'],check=True,capture_output=True,text=True,timeout=10).stdout.strip()\n` +
      ` print(json.dumps({'node':version,'npm':npm_version,'members':prepared.receipt['archiveMembers']}))\n`;
    const path = join(f.root, 'driver.py');
    writeFileSync(path, driver);
    const result = spawnSync(python, [path, script, f.bundle, f.manifestSha256, archive], { encoding: 'utf8' });
    assert.equal(result.status, 0, result.stderr);
    assert.deepEqual(JSON.parse(result.stdout), { node: 'v24.22.1', npm: '11.19.1', members: 5888 });
  } finally { f.dispose(); }
});

test('native first import uses private copy after original module changes', async () => {
  const f = fixture();
  const marker = join(f.root, 'unverified-module-ran');
  const archiveSize = statSync(archive).size;
  const knownStages = new Set(readdirSync(tmpdir()).filter(name => name.startsWith('factory-install-verify-')));
  const child = spawn(python, [script, 'verify', '--bundle-root', f.bundle, '--manifest-sha256', f.manifestSha256, '--node-archive', archive], { stdio: ['ignore', 'pipe', 'pipe'] });
  const completed = new Promise(resolve => child.on('close', resolve));
  let output = '', errors = '';
  child.stdout.setEncoding('utf8').on('data', data => { output += data; });
  child.stderr.setEncoding('utf8').on('data', data => { errors += data; });
  try {
    let copied = false;
    const deadline = Date.now() + 5000;
    while (!copied && Date.now() < deadline) {
      for (const name of readdirSync(tmpdir()).filter(item => item.startsWith('factory-install-verify-') && !knownStages.has(item))) {
        const path = join(tmpdir(), name, 'selected-node-archive');
        if (existsSync(path) && statSync(path).size === archiveSize) copied = true;
      }
      if (!copied) await new Promise(resolve => setTimeout(resolve, 5));
    }
    assert.equal(copied, true, 'completed private bundle copy was never observed');
    writeFileSync(join(f.bundle, 'dist/release.js'), `import {writeFileSync} from 'node:fs'; writeFileSync(${JSON.stringify(marker)}, 'executed');\n`);
    const code = await completed;
    assert.equal(code, 0, errors);
    assert.equal(JSON.parse(output).manifestSha256, f.manifestSha256);
    assert.equal(existsSync(marker), false);
  } finally { child.kill(); await completed; f.dispose(); }
});

test('native preparation preserves selected source identity for later candidate binding', () => {
  const f = fixture();
  try {
    const driver = `import importlib.util,pathlib,sys\n` +
      `s=importlib.util.spec_from_file_location('factory_install',sys.argv[1]); m=importlib.util.module_from_spec(s); sys.modules[s.name]=m; s.loader.exec_module(m)\n` +
      `with m.prepare_install_selection(sys.argv[2],sys.argv[3],sys.argv[4]) as prepared:\n` +
      ` assert prepared.source_bundle_root != prepared.snapshot_bundle_root\n` +
      ` assert prepared.source_node_archive != prepared.snapshot_node_archive\n` +
      ` source=pathlib.Path(sys.argv[2])/'dist/release.js'; source.write_bytes(b'changed after preparation')\n` +
      ` try: prepared.revalidate_sources()\n` +
      ` except ValueError: print('changed source refused')\n` +
      ` else: raise AssertionError('changed source was rebound')\n`;
    const path = join(f.root, 'driver.py');
    writeFileSync(path, driver);
    const result = spawnSync(python, [path, script, f.bundle, f.manifestSha256, archive], { encoding: 'utf8' });
    assert.equal(result.status, 0, result.stderr);
    assert.equal(result.stdout.trim(), 'changed source refused');
  } finally { f.dispose(); }
});
