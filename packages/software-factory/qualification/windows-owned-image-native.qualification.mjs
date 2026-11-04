// Explicit native entry point. Missing Windows/MSVC/runtime prerequisites fail.
import { spawn, spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { mkdirSync, writeFileSync, existsSync, lstatSync, copyFileSync } from 'node:fs';
import { join, resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { cases, limit, readBounded, validateNative } from './windows-owned-image.mjs';
import { parseBuildDiagnostic, formatFailure } from './windows-owned-image-diagnostics.mjs';

const here = dirname(fileURLToPath(import.meta.url));
const evidence = resolve(process.env.WINDOWS_OWNED_IMAGE_EVIDENCE ?? 'windows-owned-image-evidence');
const sourceNames = ['windows-owned-image-probe.cpp', 'windows-owned-image-shared.h', 'windows-owned-image-fixture.cpp', 'windows-owned-image-fixture-dll.cpp'];
const binaryNames = ['probe.exe', 'fixture\\canary.exe', 'fixture\\canary.dll', 'alternate\\canary.exe', 'alternate\\canary.dll', 'copy\\canary.exe', 'copy\\canary.dll'];
let interrupted = false;
let active = null;
let diagnostic = { phase: 'host', category: 'host' };
const signal = () => { interrupted = true; if (active) active.kill(); };
process.on('SIGINT', signal); process.on('SIGTERM', signal);

function run(application, args, maximum, timeout) {
  return new Promise(resolveRun => {
    let child;
    const result = { exitCode: null, signal: null, capped: false, timedOut: false, stdout: '', stderr: '' };
    let bytes = 0;
    try { child = spawn(application, args, { windowsHide: true, shell: false, stdio: ['ignore', 'pipe', 'pipe'] }); }
    catch { resolveRun({ ...result, capped: true }); return; }
    active = child;
    const timer = setTimeout(() => { result.timedOut = true; child.kill(); }, timeout);
    const collect = stream => chunk => {
      bytes += chunk.length;
      if (bytes > maximum) { result.capped = true; child.kill(); return; }
      result[stream] += chunk.toString('utf8');
    };
    child.stdout.on('data', collect('stdout')); child.stderr.on('data', collect('stderr'));
    child.on('error', () => { result.capped = true; });
    child.on('close', (code, sig) => {
      clearTimeout(timer); active = null; result.exitCode = code; result.signal = sig; resolveRun(result);
    });
  });
}

try {
  if (process.platform !== 'win32' || process.arch !== 'x64' || process.version !== 'v24.22.1' || interrupted || existsSync(evidence)) throw new Error('host');
  mkdirSync(evidence, { recursive: false });
  const powershell = join(process.env.SystemRoot ?? '', 'System32', 'WindowsPowerShell', 'v1.0', 'powershell.exe');
  if (!lstatSync(powershell).isFile()) throw new Error('host');
  // Build output is private. Never print compiler paths, versions or logs.
  diagnostic = { phase: 'build', category: 'launch' };
  const build = spawnSync(powershell, ['-NoLogo', '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass',
    '-File', join(here, 'windows-owned-image-native-build.ps1'), '-Evidence', evidence],
  { windowsHide: true, shell: false, encoding: 'utf8', timeout: 180000, maxBuffer: 1048576 });
  diagnostic = { phase: 'build', ...parseBuildDiagnostic(build.stderr) };
  if (build.error || build.signal !== null) diagnostic = { phase: 'build', category: build.error?.code === 'ETIMEDOUT'
    ? 'timeout' : build.error?.code === 'ENOBUFS' ? 'cap' : 'launch' };
  if (interrupted) diagnostic = { phase: 'build', category: 'interrupted' };
  writeFileSync(join(evidence, 'build-launch.private.json'), JSON.stringify({ status: build.status, signal: build.signal,
    stdout: build.stdout ?? '', stderr: build.stderr ?? '', error: build.error ? 'launch' : null }), { flag: 'wx' });
  if (build.status !== 0 || build.signal !== null || build.error || interrupted) throw new Error('build');
  diagnostic = { phase: 'build', category: 'report' };
  const report = JSON.parse(readBounded(join(evidence, 'build.private.json')));
  if (report.protocol !== 1 || report.complete !== true || report.architecture !== 'x64' ||
      !/^5\.1\./.test(report.powershell) || !/^14\.[0-9]{2}\.[0-9]{5}$/.test(report.toolset) ||
      !/^19\./.test(report.compilerVersion) || !/^[a-f0-9]{64}$/.test(report.compilerSha256) ||
      !/^[a-f0-9]{64}$/.test(report.linkerSha256) || report.sources?.length !== sourceNames.length ||
      report.binaries?.length !== binaryNames.length) throw new Error('build');
  // Binary hashing must preserve arbitrary bytes; use bounded held-file reads below.
  diagnostic = { phase: 'pin', category: 'pin' };
  const { openSync, fstatSync, readSync, closeSync } = await import('node:fs');
  const binaryDigest = path => {
    const stat = lstatSync(path);
    if (!stat.isFile() || stat.isSymbolicLink() || stat.size <= 0 || stat.size > 16777216) throw new Error('pin');
    const fd = openSync(path, 'r');
    try {
      const actual = fstatSync(fd);
      if (actual.dev !== stat.dev || actual.ino !== stat.ino || actual.size !== stat.size) throw new Error('pin');
      const hash = createHash('sha256'); const buffer = Buffer.alloc(16384); let total = 0, count;
      while ((count = readSync(fd, buffer, 0, buffer.length, null))) { total += count; if (total > 16777216) throw new Error('pin'); hash.update(buffer.subarray(0, count)); }
      if (total !== stat.size) throw new Error('pin');
      return hash.digest('hex');
    } finally { closeSync(fd); }
  };
  for (const [names, pins, root] of [[sourceNames, report.sources, here], [binaryNames, report.binaries, join(evidence, 'native')]]) {
    for (const [i, name] of names.entries()) {
      if (pins[i].name !== name || pins[i].sha256 !== binaryDigest(join(root, name))) throw new Error('pin');
    }
  }
  const driver = { protocol: 1, node: process.version, complete: false, cleanup: false, cases: [] };
  for (const name of cases) {
    diagnostic = { phase: 'pin', name, category: interrupted ? 'interrupted' : 'pin' };
    if (interrupted) throw new Error('stop');
    // Revalidate every produced asset before each run; this is qualification
    // staging evidence and does not authenticate the controller's own launch.
    for (const pin of report.binaries) if (binaryDigest(join(evidence, 'native', pin.name)) !== pin.sha256) throw new Error('pin');
    diagnostic = { phase: 'case', name, category: 'receipt' };
    if (['path-replacement', 'ancestor-replacement', 'alias-replacement'].includes(name)) {
      const stage = join(evidence, 'native', name);
      mkdirSync(stage); mkdirSync(join(stage, 'fixture'));
      copyFileSync(join(evidence, 'native', 'fixture', 'canary.exe'), join(stage, 'fixture', name === 'alias-replacement' ? 'pin.exe' : 'canary.exe'));
      copyFileSync(join(evidence, 'native', 'fixture', 'canary.dll'), join(stage, 'fixture', 'canary.dll'));
    }
    const result = await run(join(evidence, 'native', 'probe.exe'), [join(evidence, 'native'), name,
      join(evidence, `${name}.details.private.tsv`)], limit, 12000);
    diagnostic = { phase: 'case', name, category: interrupted ? 'interrupted' : result.timedOut ? 'timeout'
      : result.capped ? 'cap' : result.signal !== null ? 'signal' : result.exitCode !== 0 || result.stderr ? 'native' : 'receipt' };
    writeFileSync(join(evidence, `${name}.private.tsv`), result.stdout, { flag: 'wx' });
    writeFileSync(join(evidence, `${name}.stderr.private.txt`), result.stderr, { flag: 'wx' });
    const checked = validateNative(result.stdout, name);
    if (!checked.cleanup && diagnostic.category === 'receipt') diagnostic.category = 'cleanup';
    const detail = readBounded(join(evidence, `${name}.details.private.tsv`));
    if (!detail.length || result.stderr || result.exitCode !== 0 || result.signal !== null || result.capped || result.timedOut ||
        !checked.qualified || !checked.cleanup || interrupted) throw new Error('native');
    driver.cases.push({ name, exitCode: result.exitCode, signal: result.signal, capped: result.capped, timedOut: result.timedOut });
  }
  driver.complete = true; driver.cleanup = true;
  writeFileSync(join(evidence, 'driver.private.json'), JSON.stringify(driver, null, 2) + '\n', { flag: 'wx' });
  process.stdout.write('Owned image native canary completed\n');
} catch {
  process.stderr.write(formatFailure(diagnostic)); process.exitCode = interrupted ? 130 : 1;
} finally {
  process.removeListener('SIGINT', signal); process.removeListener('SIGTERM', signal);
}
