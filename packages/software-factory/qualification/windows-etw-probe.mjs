// Qualification-only public boundary for one pinned Node/known-child ETW feasibility run.
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { existsSync, mkdirSync, readFileSync, statSync, unlinkSync, writeFileSync } from 'node:fs';
import { basename, join, resolve, win32 } from 'node:path';
import { fileURLToPath } from 'node:url';

const sourceRoot = fileURLToPath(new URL('.', import.meta.url));
const maxEtlBytes = 64 * 1024 * 1024;
const requiredApis = ['start', 'readyQuery', 'beforeStopQuery', 'stop', 'open', 'process', 'close'];
const integer = (value) => /^\d+$/.test(value) && Number.isSafeInteger(Number(value));
const tick = (value) => typeof value === 'string' && /^\d{15,20}$/.test(value) && BigInt(value) > 0n;
const pid = (value) => integer(value) && Number(value) > 0 && Number(value) <= 0xffffffff;
const sameImage = (actual, expected) => win32.basename(actual).toLowerCase() === win32.basename(expected).toLowerCase();

export function validateProbeReceipt(receipt, expectedNode) {
  const reasons = [];
  if (typeof receipt !== 'string' || receipt.length > 65536 || typeof expectedNode !== 'string' || !expectedNode)
    return { ok: false, reasons: ['invalid receipt or expected Node path'] };
  const rows = receipt.trimEnd().split('\n').map((line) => line.replace(/\r$/, '').split('\t'));
  const selected = (kind) => rows.filter((row) => row[0] === kind);
  const one = (kind) => {
    const items = selected(kind);
    if (items.length !== 1) reasons.push(`${kind} count ${items.length}`);
    return items[0] ?? [];
  };
  const apis = selected('API');
  for (const name of requiredApis) {
    const hits = apis.filter((row) => row[1] === name);
    if (hits.length !== 1 || hits[0][2] !== '0' || hits[0].length !== 3)
      reasons.push(`${name} API incomplete`);
  }
  if (apis.length !== requiredApis.length) reasons.push('unexpected API receipt');
  const session = one('SESSION');
  if (session.length !== 4 || session[1] !== '33554433' || session[2] !== '5' || session[3] !== '64')
    reasons.push('session mode, flags or cap mismatch');
  const ownership = one('OWNERSHIP');
  if (ownership.length !== 3 || !/^[\da-f]{8}-[\da-f]{4}-4[\da-f]{3}-[89ab][\da-f]{3}-[\da-f]{12}$/.test(ownership[1]) ||
    ownership[2] !== `Codex factory ETW feasibility ${ownership[1]?.replaceAll('-', '')}`)
    reasons.push('owned session identity missing');
  const abi = one('ABI');
  if (abi.length !== 5 || abi.slice(1).join(',') !== '120,280,112,448') reasons.push('ETW ABI mismatch');
  const token = one('TOKEN');
  if (token.length !== 2 || !['system', 'administrator', 'other'].includes(token[1]))
    reasons.push('token evidence missing');
  const os = one('OS');
  if (os.length !== 2 || !/Windows NT [\d.]+/.test(os[1]) || os[1].length > 128)
    reasons.push('OS evidence missing');
  const schema = one('SCHEMA');
  if (schema.join(',') !== 'SCHEMA,ProcessId:u32,ParentId:u32,UniqueProcessKey:pointer,ImageFileName:string,ExitStatus:u32,Image.ProcessId:u32,Image.FileName:string')
    reasons.push('TDH field schema incomplete');
  const rundown = one('RUNDOWN');
  if (rundown.length !== 3 || !integer(rundown[1]) || !integer(rundown[2]))
    reasons.push('rundown classification missing');
  const counts = one('COUNTS');
  if (counts.length !== 3 || !integer(counts[1]) || !integer(counts[2]) ||
    Number(counts[1]) > 100000 || Number(counts[2]) < 6 || Number(counts[2]) > Number(counts[1]))
    reasons.push('callback/event counts invalid');
  const root = one('ROOT');
  const child = one('CHILD');
  const rootPid = Number(root[1]);
  const childPid = Number(child[1]);
  if (root.length !== 4 || !pid(root[1]) || !tick(root[2]) ||
    root[3].toLowerCase() !== expectedNode.toLowerCase()) reasons.push('root identity invalid');
  if (child.length !== 2 || !pid(child[1]) || childPid === rootPid) reasons.push('child identity invalid');
  const stats = one('STATS');
  const header = one('HEADER');
  if (stats.length !== 4 || stats.slice(1).some((part) => part !== '0')) reasons.push('session loss');
  if (header.length !== 4 || !tick(header[1]) ||
    header[2] !== '0' || header[3] !== '0') reasons.push('ETL not finalized or loss reported');
  const file = one('FILE');
  if (file.length !== 2 || !integer(file[1]) || Number(file[1]) === 0 || Number(file[1]) >= maxEtlBytes)
    reasons.push('ETL missing or at cap');
  if (selected('COMPLETE').length !== 1 || selected('COMPLETE')[0].length !== 1)
    reasons.push('native completion missing');
  const events = selected('EVENT');
  const starts = events.filter((event) => event[1] === 'process-start');
  const ends = events.filter((event) => event[1] === 'process-end');
  const images = events.filter((event) => event[1] === 'image-load');
  if (events.length !== starts.length + ends.length + images.length) reasons.push('unknown event kind');
  for (const [label, list, target] of [
    ['root start', starts, rootPid], ['child start', starts, childPid],
    ['root end', ends, rootPid], ['child end', ends, childPid]
  ]) if (list.filter((event) => Number(event[2]) === target).length !== 1) reasons.push(`${label} count invalid`);
  const start = (target) => starts.find((event) => Number(event[2]) === target) ?? [];
  const end = (target) => ends.find((event) => Number(event[2]) === target) ?? [];
  const rootStart = start(rootPid), childStart = start(childPid);
  const rootEnd = end(rootPid), childEnd = end(childPid);
  for (const [label, event] of [['root start', rootStart], ['child start', childStart]]) {
    if (event.length !== 7 || !pid(event[2]) || !integer(event[3]) ||
      event[4] !== (label === 'root start' ? 'root' : 'child') ||
      !sameImage(event[5] ?? '', expectedNode) || !tick(event[6]))
      reasons.push(`${label} schema invalid`);
  }
  for (const [label, event] of [['root end', rootEnd], ['child end', childEnd]]) {
    if (event.length !== 7 || !pid(event[2]) || !integer(event[3]) ||
      event[4] !== (label === 'root end' ? 'root' : 'child') || event[5] !== '0' || !tick(event[6]))
      reasons.push(`${label} schema invalid`);
  }
  if (childStart[3] !== root[1] || childEnd[3] !== root[1] ||
    rootStart[4] !== rootEnd[4] || childStart[4] !== childEnd[4])
    reasons.push('parent or process key mismatch');
  if ([root[2], rootStart[6], childStart[6], childEnd[6], rootEnd[6], header[1]].every(tick)) {
    const [created, rs, cs, ce, re, finished] =
      [root[2], rootStart[6], childStart[6], childEnd[6], rootEnd[6], header[1]].map(BigInt);
    if (rs < created - 50_000_000n || rs > created + 50_000_000n ||
      !(rs < cs && cs < ce && ce < re && re < finished)) reasons.push('known process times invalid');
  }
  for (const target of [rootPid, childPid]) {
    const startTime = target === rootPid ? rootStart[6] : childStart[6];
    const endTime = target === rootPid ? rootEnd[6] : childEnd[6];
    if (!images.some((event) => event.length === 5 && Number(event[2]) === target &&
      sameImage(event[3], expectedNode) && tick(event[4]) && tick(startTime) && tick(endTime) &&
      BigInt(event[4]) >= BigInt(startTime) - 10_000_000n && BigInt(event[4]) <= BigInt(endTime)))
      reasons.push(`image load missing for ${target}`);
  }
  const known = new Set(['API', 'ABI', 'TOKEN', 'OS', 'OWNERSHIP', 'SCHEMA', 'RUNDOWN', 'COUNTS',
    'SESSION', 'ROOT', 'CHILD', 'EVENT', 'STATS', 'HEADER', 'FILE', 'COMPLETE']);
  if (rows.some((row) => !known.has(row[0]))) reasons.push('unknown receipt row');
  return { ok: reasons.length === 0, reasons, rootPid, childPid,
    processStarts: starts.length, processEnds: ends.length, imageLoads: images.length };
}

function sha256(path) { return createHash('sha256').update(readFileSync(path)).digest('hex'); }

function main() {
  if (process.platform !== 'win32' || process.arch !== 'x64') {
    process.stderr.write('unsupported host: Windows x64 required\n');
    process.exitCode = 2;
    return;
  }
  const evidence = resolve(process.env.WINDOWS_ETW_PROBE_EVIDENCE ?? 'windows-etw-probe-evidence');
  mkdirSync(evidence, { recursive: true });
  const report = { scope: 'T17-Windows-ETW-native-feasibility-only', status: 'failed',
    limitation: 'Known Node/child positive control only; no Git/TypeScript comparator or no-child claim.' };
  const save = () => writeFileSync(join(evidence, 'qualification.json'), `${JSON.stringify(report, null, 2)}\n`);
  const etl = join(evidence, 'trace.etl');
  try {
    if (process.version !== 'v24.22.1') throw new Error('unpinned bootstrap Node version');
    const manifest = JSON.parse(readFileSync(join(sourceRoot, 'runtime-manifest.json'), 'utf8'));
    const bootstrap = JSON.parse(readFileSync(join(evidence, 'bootstrap.json'), 'utf8'));
    if (bootstrap.status !== 'passed' || bootstrap.native?.node !== manifest.node ||
      bootstrap.sha256 !== manifest.artifacts['win32-x64'].sha256) throw new Error('bootstrap identity mismatch');
    const archive = join(bootstrap.directory, basename(new URL(bootstrap.url).pathname));
    if (sha256(archive) !== manifest.artifacts['win32-x64'].sha256) throw new Error('Node archive hash mismatch');
    const node = join(bootstrap.directory, 'node-v24.22.1-win-x64', 'node.exe');
    const member = spawnSync('tar', ['-xOf', archive, 'node-v24.22.1-win-x64/node.exe'],
      { encoding: null, timeout: 120000, maxBuffer: 150000000 });
    if (member.error || member.status !== 0 || !member.stdout?.length ||
      createHash('sha256').update(member.stdout).digest('hex') !== sha256(node))
      throw new Error('extracted Node differs from pinned archive member');
    report.node = { version: process.version, archiveSha256: sha256(archive), executableSha256: sha256(node) };
    const powershell = join(process.env.SystemRoot ?? '', 'System32', 'WindowsPowerShell', 'v1.0', 'powershell.exe');
    if (!existsSync(powershell)) throw new Error('Windows PowerShell 5.1 unavailable');
    const invocation = spawnSync(powershell, ['-NoProfile', '-NonInteractive', '-File',
      join(sourceRoot, 'windows-etw-probe.ps1'), '-NodePath', node, '-EvidenceDir', evidence],
    { cwd: evidence, encoding: 'utf8', timeout: 75000, maxBuffer: 65536 });
    report.bridge = { exitCode: invocation.status, error: invocation.error?.code ?? null,
      stderr: (invocation.stderr ?? '').slice(0, 2048) };
    const receiptPath = join(evidence, 'native.tsv');
    if (existsSync(receiptPath)) {
      report.receipt = validateProbeReceipt(readFileSync(receiptPath, 'utf8'), node);
      report.etlBytes = existsSync(etl) ? statSync(etl).size : null;
    }
    if (invocation.status === 0 && report.receipt?.ok && report.etlBytes > 0 && report.etlBytes < maxEtlBytes)
      report.status = 'native-feasibility-passed-review-required';
    save();
    if (report.status !== 'native-feasibility-passed-review-required') process.exitCode = 1;
  } catch (error) {
    report.error = error instanceof Error ? error.message : String(error);
    save(); process.stderr.write(`${report.error}\n`); process.exitCode = 1;
  } finally {
    try {
      if (existsSync(etl)) unlinkSync(etl);
      report.rawEtl = 'removed-after-offline-parse';
    } catch (error) {
      report.rawEtl = 'cleanup-failed';
      report.cleanupError = error instanceof Error ? error.code ?? error.name : String(error);
      report.status = 'failed'; process.exitCode = 1;
    }
    save();
  }
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) main();
