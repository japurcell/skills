// Only GitHub's disposable runners opt into downloading this reviewed development runtime.
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { appendFileSync, mkdirSync, mkdtempSync, readFileSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { basename, dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const packageRoot = fileURLToPath(new URL('../', import.meta.url));
const evidence = resolve(process.env.FACTORY_EVIDENCE_DIR ?? join(packageRoot, 'qualification-results'));
mkdirSync(evidence, { recursive: true });
const report = { scope: 'runtime-bootstrap', status: 'failed', bootstrapNode: process.version, platform: process.platform, arch: process.arch };
try {
  assert.equal(process.env.GITHUB_ACTIONS, 'true', 'runtime downloads require an ephemeral GitHub Actions runner');
  assert.ok(process.env.GITHUB_PATH && process.env.GITHUB_ENV, 'GitHub runner command files missing');
  const target = `${process.platform}-${process.arch}`;
  assert.equal(process.env.FACTORY_TARGET, target, 'runner architecture does not match reviewed matrix target');
  const manifest = JSON.parse(readFileSync(join(packageRoot, 'qualification/runtime-manifest.json'), 'utf8'));
  const artifact = manifest.artifacts[target];
  assert.ok(artifact, 'no reviewed native artifact');
  assert.match(manifest.node, /^v24\.\d+\.\d+$/);
  assert.match(artifact.sha256, /^[a-f0-9]{64}$/);
  const url = new URL(artifact.url);
  assert.equal(url.origin, 'https://nodejs.org');
  assert.equal(url.pathname, `/download/release/${manifest.node}/${basename(url.pathname)}`);
  const version = manifest.node.slice(1);
  const expectedName = process.platform === 'win32' ? `node-v${version}-win-x64.zip` : `node-v${version}-${target}.tar.xz`;
  assert.equal(basename(url.pathname), expectedName);
  const directory = mkdtempSync(join(process.env.RUNNER_TEMP ?? tmpdir(), 'factory-node-'));
  Object.assign(report, { directory, url: artifact.url, expectedSha256: artifact.sha256 });
  const response = await fetch(url, { signal: AbortSignal.timeout(120_000), redirect: 'error' });
  assert.equal(response.status, 200, 'official runtime download failed');
  assert.ok(response.body, 'empty runtime download');
  const chunks = []; let bytes = 0;
  for await (const chunk of response.body) {
    bytes += chunk.length;
    assert.ok(bytes <= 150_000_000, 'runtime archive exceeds bounded download size');
    chunks.push(chunk);
  }
  const archive = Buffer.concat(chunks);
  const sha256 = createHash('sha256').update(archive).digest('hex');
  Object.assign(report, { sha256, bytes });
  assert.equal(sha256, artifact.sha256, 'official runtime archive integrity mismatch');
  const archivePath = join(directory, expectedName);
  writeFileSync(archivePath, archive, { flag: 'wx' });
  const extraction = spawnSync('tar', ['-xf', archivePath, '-C', directory], { encoding: 'utf8', timeout: 120_000, maxBuffer: 1_048_576 });
  assert.equal(extraction.status, 0, `native tar extraction unavailable or failed: ${extraction.error ?? extraction.stderr}`);
  const runtimeRoot = join(directory, expectedName.replace(/\.tar\.xz$|\.zip$/, ''));
  const binary = join(runtimeRoot, process.platform === 'win32' ? 'node.exe' : 'bin/node');
  const versions = spawnSync(binary, ['-p', 'JSON.stringify({node:process.version,sqlite:process.versions.sqlite,platform:process.platform,arch:process.arch})'], { encoding: 'utf8', timeout: 10_000 });
  assert.equal(versions.status, 0, versions.stderr);
  const native = JSON.parse(versions.stdout);
  assert.deepEqual(native, { node: manifest.node, sqlite: manifest.sqlite, platform: process.platform, arch: process.arch });
  const bin = dirname(binary);
  const npm = join(runtimeRoot, process.platform === 'win32' ? 'node_modules/npm/bin/npm-cli.js' : 'lib/node_modules/npm/bin/npm-cli.js');
  const npmVersion = spawnSync(binary, [npm, '--version'], { encoding: 'utf8', timeout: 10_000 });
  assert.equal(npmVersion.status, 0, npmVersion.stderr);
  appendFileSync(process.env.GITHUB_PATH, `${bin}\n`);
  appendFileSync(process.env.GITHUB_ENV, `FACTORY_NPM_CLI=${npm}\n`);
  Object.assign(report, { status: 'passed', native, npm: npmVersion.stdout.trim() });
} catch (error) {
  report.error = error instanceof Error ? error.message : String(error);
  process.stderr.write(`${report.error}\n`);
  process.exitCode = 1;
} finally {
  writeFileSync(join(evidence, 'bootstrap.json'), `${JSON.stringify(report, null, 2)}\n`);
}
