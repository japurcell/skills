// Manual CI qualification only. Never import this from product startup.
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { existsSync, lstatSync, mkdirSync, readFileSync, readdirSync, writeFileSync } from 'node:fs';
import { basename, join, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const artifacts = {
  git: {
    url: 'https://github.com/git-for-windows/git/releases/download/v2.54.0.windows.1/MinGit-2.54.0-64-bit.zip',
    archive: 'MinGit-2.54.0-64-bit.zip',
    sha256: '04f937e1f0918b17b9be6f2294cb2bb66e96e1d9832d1c298e2de088a1d0e668',
    source: '2b8a3ab140826ac423c2845ef81d4c6ac4f7bf3c',
    known: {
      'mingw64/bin/git.exe': 'cab4c4eea1d869cf9f7be73868dc9a90ad2df1b1b673e5f8c8714a576c25ea96',
      'mingw64/bin/libiconv-2.dll': '7a282a854e01be726c6cccfe46f548c716aa45b3014818468253aaa4efbcd067',
      'mingw64/bin/libintl-8.dll': '0537c3dd2378218508ebe3cc416d72a99ee2d24ae1c5525e23458f32544ef861',
      'mingw64/bin/libpcre2-8-0.dll': 'c135a87ed0f11eae8ffc4cb469671ff0b3f5d71fab5fb024e9b1e7241ca25b52',
      'mingw64/bin/libwinpthread-1.dll': '851f61482ad5b6aac7c6abc54bbe31d24f89e0ca683a75fcec2d47f86b2d2242',
      'mingw64/bin/zlib1.dll': '93e9243a44c29200eeacaf9658efe2558581770e4b11ca4b500e18e424a6e3b5',
    },
  },
  typescript: {
    url: 'https://registry.npmjs.org/@typescript/typescript-win32-x64/-/typescript-win32-x64-7.0.2.tgz',
    archive: 'typescript-win32-x64-7.0.2.tgz',
    sha256: '61fc4e141d2bc687db580e71bbfa63b9c209f0310645d82ca1b457eb3a24fd19',
    source: '2bd066d87f5bafd315be9f40889d0a60b9e58e0b',
    known: {
      'package/lib/tsc.exe': 'f9ecfbdc93753d2c972d66a8d0d75f5bd737fd4a5f88b422d9091ea282bcb2c7',
    },
  },
};

function sha256(bytes) { return createHash('sha256').update(bytes).digest('hex'); }

async function download(url, limit) {
  let current = url;
  for (let redirects = 0; redirects < 4; redirects++) {
    const parsed = new URL(current);
    assert.ok(['github.com', 'release-assets.githubusercontent.com', 'objects.githubusercontent.com', 'registry.npmjs.org'].includes(parsed.hostname), 'unexpected archive host');
    const response = await fetch(current, { redirect: 'manual', signal: AbortSignal.timeout(120_000) });
    if ([301, 302, 303, 307, 308].includes(response.status)) {
      current = new URL(response.headers.get('location'), current).toString();
      continue;
    }
    assert.equal(response.status, 200, `archive download failed: ${response.status}`);
    const chunks = []; let length = 0;
    for await (const chunk of response.body) {
      length += chunk.length;
      assert.ok(length <= limit, 'archive exceeds byte bound');
      chunks.push(chunk);
    }
    return Buffer.concat(chunks);
  }
  throw new Error('archive redirect bound exceeded');
}

function walk(root) {
  const files = {};
  const visit = (directory) => {
    for (const entry of readdirSync(directory, { withFileTypes: true })) {
      const path = join(directory, entry.name);
      const stat = lstatSync(path);
      assert.ok(!stat.isSymbolicLink(), `unexpected archive symlink: ${path}`);
      if (stat.isDirectory()) visit(path);
      else {
        assert.ok(stat.isFile(), `unexpected archive member: ${path}`);
        files[relative(root, path).replaceAll('\\', '/')] = sha256(readFileSync(path));
      }
    }
  };
  visit(root);
  return files;
}

export async function prepareArtifacts(evidence, offline = false) {
  assert.ok(offline || process.platform === 'win32' && process.env.GITHUB_ACTIONS === 'true' && process.env.RUNNER_TEMP,
    'network qualification requires a disposable Windows Actions runner');
  mkdirSync(evidence, { recursive: true });
  const report = { scope: 'windows-startup-artifacts', status: 'failed', archives: {} };
  try {
    for (const [name, artifact] of Object.entries(artifacts)) {
      const root = join(evidence, name);
      mkdirSync(root, { recursive: true });
      const offlinePath = name === 'git' ? process.env.WINDOWS_STARTUP_OFFLINE_GIT_ARCHIVE : process.env.WINDOWS_STARTUP_OFFLINE_TS_ARCHIVE;
      assert.ok(!offline || offlinePath && existsSync(offlinePath), `missing offline ${name} archive`);
      const bytes = offline ? readFileSync(offlinePath) : await download(artifact.url, name === 'git' ? 80_000_000 : 30_000_000);
      const actual = sha256(bytes);
      assert.equal(actual, artifact.sha256, `${name} archive SHA256 mismatch`);
      const archivePath = join(root, artifact.archive);
      writeFileSync(archivePath, bytes, { flag: 'wx' });
      const members = spawnSync('tar', ['-tf', archivePath], { encoding: 'utf8', timeout: 120_000, maxBuffer: 1_048_576 });
      assert.equal(members.status, 0, `${name} archive listing failed: ${members.stderr}`);
      for (const member of members.stdout.split(/\r?\n/).filter(Boolean))
        assert.ok(!member.startsWith('/') && !member.startsWith('\\') && !/^[A-Za-z]:/.test(member) &&
          !member.split(/[\\/]/).includes('..'), `${name} archive path escapes root`);
      const extraction = spawnSync('tar', ['-xf', archivePath, '-C', root], { encoding: 'utf8', timeout: 120_000, maxBuffer: 1_048_576 });
      assert.equal(extraction.status, 0, `${name} archive extraction failed: ${extraction.stderr}`);
      const files = walk(root);
      delete files[basename(archivePath)];
      for (const [member, expected] of Object.entries(artifact.known))
        assert.equal(files[member], expected, `${name} member mismatch: ${member}`);
      report.archives[name] = { root: resolve(root), archive: artifact.archive, url: artifact.url,
        sha256: actual, bytes: bytes.length, source: artifact.source, files };
    }
    report.status = 'prepared-not-natively-qualified';
    return report;
  } catch (error) {
    report.error = error instanceof Error ? error.message : String(error);
    throw error;
  } finally {
    writeFileSync(join(evidence, 'artifacts.json'), `${JSON.stringify(report, null, 2)}\n`);
  }
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const evidence = resolve(process.env.WINDOWS_STARTUP_EVIDENCE ?? join(process.cwd(), 'windows-startup-evidence'));
  prepareArtifacts(evidence, process.argv.includes('--offline')).catch((error) => { console.error(error); process.exitCode = 1; });
}
