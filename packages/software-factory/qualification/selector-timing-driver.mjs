import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { closeSync, fstatSync, mkdirSync, openSync, readSync, writeFileSync } from 'node:fs';
import { availableParallelism, release } from 'node:os';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { collectEvidence, createEvidenceRoot, createCollector, hasSelectorCoverage } from './selector-timing.mjs';

// Explicit qualification entry point. No workflow, provider, receipt or environment preflight is replaced.
const cwd = fileURLToPath(new URL('../', import.meta.url));
let fixtureExitCode = 1;
try {
  if (process.argv.length !== 3 || process.version !== 'v24.22.1') throw new Error('preflight');
  const destination = resolve(process.argv[2]);
  mkdirSync(destination, { mode: 0o700 }); // Exclusive: never overwrite or remove caller data.
  const source = spawnSync('git', ['rev-parse', 'HEAD'], { cwd, encoding: 'utf8' });
  const sourceSha = source.stdout?.trim();
  if (source.status !== 0 || !/^[a-f0-9]{40}$/.test(sourceSha)) throw new Error('preflight');
  const binary = openSync(process.execPath, 'r'); let runtimeSha256;
  try {
    if (fstatSync(binary).size > 536870912) throw new Error('preflight');
    const hash = createHash('sha256'), buffer = Buffer.alloc(1048576);
    for (;;) { const bytes = readSync(binary, buffer); if (bytes === 0) break; hash.update(buffer.subarray(0, bytes)); }
    runtimeSha256 = hash.digest('hex');
  } finally { closeSync(binary); }
  const root = createEvidenceRoot(), collector = createCollector(root);
  collector.mark('worker-open');
  const end = collector.begin('selector');
  const result = spawnSync(process.execPath, ['scripts/test.mjs', 'fixtures'], {
    cwd, stdio: 'inherit', env: { ...process.env, FACTORY_SELECTOR_TIMING_ROOT: root.path, FACTORY_SELECTOR_TIMING_TOKEN: root.token },
  });
  fixtureExitCode = result.status ?? (result.signal === 'SIGINT' ? 130 : result.signal === 'SIGTERM' ? 143 : 1);
  end(fixtureExitCode === 0 ? 'ok' : 'failed', { exitCode: fixtureExitCode }); collector.close();
  let evidence;
  try { evidence = collectEvidence(root); }
  catch { evidence = { status: 'incomplete', records: [] }; }
  if (!hasSelectorCoverage(evidence.records)) evidence.status = 'incomplete';
  const image = value => typeof value === 'string' && /^[a-zA-Z0-9._-]{1,64}$/.test(value) ? value : 'unavailable';
  const metadata = { schema: 1, status: evidence.status, sourceSha, runtimeSha256, node: process.version, platform: process.platform, arch: process.arch,
    availableParallelism: availableParallelism(), runtimeOsRelease: image(release()), runnerImage: image(process.env.ImageOS), runnerImageVersion: image(process.env.ImageVersion), fixtureExitCode,
    clock: 'host-monotonic-ms', attemptClock: 'persisted-utc-wall', cpu: 'emitting-process-only', records: evidence.records.length };
  writeFileSync(resolve(destination, 'selector-timing.jsonl'), evidence.records.map(record => JSON.stringify(record) + '\n').join(''), { flag: 'wx', mode: 0o600 });
  writeFileSync(resolve(destination, 'selector-timing.json'), JSON.stringify(metadata) + '\n', { flag: 'wx', mode: 0o600 });
  if (evidence.status !== 'complete') process.stderr.write('factory qualification timing: incomplete\n');
  process.exitCode = fixtureExitCode || (evidence.status === 'complete' ? 0 : 1);
} catch {
  process.stderr.write('factory qualification timing: incomplete\n');
  process.exitCode = fixtureExitCode || 1;
}
