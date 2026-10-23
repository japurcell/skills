// Qualification-only public boundary for one pinned Node/known-child ETW feasibility run.
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { existsSync, mkdirSync, readFileSync, statSync, unlinkSync, writeFileSync } from 'node:fs';
import { basename, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const sourceRoot = fileURLToPath(new URL('.', import.meta.url));
const maxEtlBytes = 64 * 1024 * 1024;
const maxReceiptBytes = 65536;
const requiredApis = ['start', 'readyQuery', 'beforeStopQuery', 'stop', 'open', 'process', 'close'];
const diagnosticRow = /^DIAG\t(?:callback\t(?:callback-cap|schema-size|property-size|property-width|text-shape|empty-key|duplicate-event|image-mismatch|other)\t(?:root|child|none)|callback\tprocess-image-mismatch\t(?:root\t(?:name-only|dos-absolute|device-absolute|other)\t(?:same|different)\t(?:before-creation-window|before-creation-within-window|at-or-after-creation-within-window|after-creation-window|unknown)|child\t(?:name-only|dos-absolute|device-absolute|other)\t(?:same|different)\tunknown)|identity\theld-time\t(?:root|child)\t(?:process-start|process-end|image-load)\t(?:before-creation|after-exit|unavailable)|keys\t(?:missing-start-key|missing-end-key|changed-key)\t(?:root|child)|identity\t(?:missing-event|missing-image|duplicate-image|identity-key|parent-mismatch|exit-status|creation-time|process-order|image-lifetime)\t(?:root|child|none))$/;
const integer = (value) => /^\d+$/.test(value) && Number.isSafeInteger(Number(value));
const tick = (value) => typeof value === 'string' && /^\d{15,20}$/.test(value) && BigInt(value) > 0n;
const pid = (value) => integer(value) && Number(value) > 0 && Number(value) <= 0xffffffff;

export function validateProbeReceipt(receipt, expectedNode) {
  const reasons = [];
  if (typeof receipt !== 'string' || Buffer.byteLength(receipt, 'utf8') > maxReceiptBytes ||
    typeof expectedNode !== 'string' || !expectedNode)
    return { ok: false, reasons: ['invalid receipt or expected Node path'] };
  const rows = receipt.trimEnd().split('\n').map((line) => line.replace(/\r$/, '').split('\t'));
  if (rows.some((row) => row[0] === 'DIAG')) reasons.push('diagnostic receipt cannot qualify');
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
  const queries = selected('QUERY');
  if (queries.length !== 2 || ['readyQuery', 'beforeStopQuery'].some((name) => {
    const rows = queries.filter((row) => row[1] === name);
    return rows.length !== 1 || rows[0].length !== 7 || rows[0].slice(2).some((bit) => bit !== '1');
  })) reasons.push('query evidence invalid');
  const modes = selected('MODE');
  if (modes.length !== 2 || ['readyQuery', 'beforeStopQuery'].some((name) => {
    const rows = modes.filter((row) => row[1] === name);
    return rows.length !== 1 || rows[0].length !== 7 ||
      rows[0].slice(2).join(',') !== '1,1,0,stop,0';
  })) reasons.push('mode evidence invalid');
  const session = one('SESSION');
  if (session.length !== 4 || session[1] !== '37748737' || session[2] !== '5' || session[3] !== '64')
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
  if (os.length !== 2 || !/^(?:Microsoft )?Windows NT [\d.]{1,64}$/.test(os[1]))
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
    root[3] !== 'pinned-node') reasons.push('root identity invalid');
  if (child.length !== 2 || !pid(child[1]) || childPid === rootPid) reasons.push('child identity invalid');
  const held = selected('HELD');
  const childAt = rows.findIndex((row) => row[0] === 'CHILD');
  if (held.length !== 2 || held[0]?.join(',') !== 'HELD,root,1,1,1' ||
    held[1]?.join(',') !== 'HELD,child,1,1,1' ||
    rows[childAt + 1] !== held[0] || rows[childAt + 2] !== held[1])
    reasons.push('held fixture proof incomplete');
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
  if (events.length !== 6 || starts.length !== 2 || ends.length !== 2 || images.length !== 2 ||
    counts[2] !== String(events.length)) reasons.push('selected event count invalid');
  if (events.some((event) => {
    if (event[1] === 'image-load') return event.length !== 5 || !pid(event[2]) ||
      ![rootPid, childPid].includes(Number(event[2])) || event[3] !== 'pinned-node' || !tick(event[4]);
    if (event[1] === 'process-start' || event[1] === 'process-end')
      return event.length !== 7 || !pid(event[2]) || !integer(event[3]) ||
        ![rootPid, childPid].includes(Number(event[2])) ||
        event[4] !== (Number(event[2]) === rootPid ? 'root' : 'child') ||
        event[5] !== (event[1] === 'process-start' ? 'pinned-node' : '0') || !tick(event[6]);
    return true;
  })) reasons.push('unverified event row');
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
      event[5] !== 'pinned-node' || !tick(event[6]))
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
      event[3] === 'pinned-node' && tick(event[4]) && tick(startTime) && tick(endTime) &&
      BigInt(event[4]) >= BigInt(startTime) - 10_000_000n && BigInt(event[4]) <= BigInt(endTime)))
      reasons.push(`image load missing for ${target}`);
  }
  const known = new Set(['API', 'QUERY', 'MODE', 'ABI', 'TOKEN', 'OS', 'OWNERSHIP', 'SCHEMA', 'RUNDOWN', 'COUNTS',
    'SESSION', 'ROOT', 'CHILD', 'HELD', 'EVENT', 'STATS', 'HEADER', 'FILE', 'COMPLETE', 'DIAG']);
  if (rows.some((row) => !known.has(row[0]))) reasons.push('unknown receipt row');
  return { ok: reasons.length === 0, reasons, rootPid, childPid,
    processStarts: starts.length, processEnds: ends.length, imageLoads: images.length };
}

function sha256(path) { return createHash('sha256').update(readFileSync(path)).digest('hex'); }

class ProbeFailure extends Error {
  constructor(stage, code) {
    super(code);
    this.stage = stage;
    this.code = code;
  }
}

function stop(stage, code) { throw new ProbeFailure(stage, code); }

function safeNativeLine(line) {
  const decimal = '\\d{1,20}';
  const tickValue = '\\d{15,20}';
  const patterns = {
    ABI: /^ABI\t120\t280\t112\t448$/,
    TOKEN: /^TOKEN\t(system|administrator|other)$/,
    OS: /^OS\t(?:Microsoft )?Windows NT [\d.]{1,64}$/,
    API: new RegExp(`^API\\t(start|readyQuery|beforeStopQuery|stop|open|process|close)\\t${decimal}$`),
    QUERY: /^QUERY\t(readyQuery|beforeStopQuery)(\t[01]){5}$/,
    MODE: /^MODE\t(readyQuery|beforeStopQuery)\t[01]\t[01]\t[01]\t(none|stop|persist|both)\t[01]$/,
    SESSION: /^SESSION\t37748737\t5\t64$/,
    ROOT: new RegExp(`^ROOT\\t${decimal}\\t${tickValue}\\tpinned-node$`),
    CHILD: new RegExp(`^CHILD\\t${decimal}$`),
    HELD: /^HELD\t(root|child)\t1\t1\t1$/,
    EVENT: new RegExp(`^EVENT\\t(process-start|process-end)\\t${decimal}\\t${decimal}\\t(root|child)\\t(pinned-node|${decimal})\\t${tickValue}$|^EVENT\\timage-load\\t${decimal}\\tpinned-node\\t${tickValue}$`),
    SCHEMA: /^SCHEMA\tProcessId:u32\tParentId:u32\tUniqueProcessKey:pointer\tImageFileName:string\tExitStatus:u32\tImage.ProcessId:u32\tImage.FileName:string$/,
    RUNDOWN: new RegExp(`^RUNDOWN\\t${decimal}\\t${decimal}$`),
    COUNTS: new RegExp(`^COUNTS\\t${decimal}\\t${decimal}$`),
    STATS: new RegExp(`^STATS\\t${decimal}\\t${decimal}\\t${decimal}$`),
    HEADER: new RegExp(`^HEADER\\t${tickValue}\\t${decimal}\\t${decimal}$`),
    FILE: new RegExp(`^FILE\\t${decimal}$`),
    COMPLETE: /^COMPLETE$/,
    DIAG: diagnosticRow,
    FAIL: new RegExp(`^FAIL\\t(run|root-stop|child-stop|stop|decode|receipt)\\t(native-api|timeout|invalid-data|invalid-state|operation-failed|unobserved|overflow|missing-etl|etl-cap-or-empty|loss)\\t${decimal}$`)
  };
  if (line.startsWith('OWNERSHIP\t')) {
    const row = line.split('\t');
    return row.length === 3 && /^[\da-f]{8}-[\da-f]{4}-4[\da-f]{3}-[89ab][\da-f]{3}-[\da-f]{12}$/.test(row[1]) &&
      row[2] === `Codex factory ETW feasibility ${row[1].replaceAll('-', '')}`;
  }
  return Boolean(patterns[line.split('\t', 1)[0]]?.test(line));
}

function safeNativeReceipt(text) {
  const lines = text.split(/\r?\n/);
  if (lines.at(-1) === '') lines.pop();
  if (!lines.every(safeNativeLine)) return false;
  const held = lines.filter((line) => line.startsWith('HELD\t'));
  if (held.length !== 0) {
    const childAt = lines.findIndex((line) => line.startsWith('CHILD\t'));
    if (held.length !== 2 || childAt < 0 || lines[childAt + 1] !== 'HELD\troot\t1\t1\t1' ||
      lines[childAt + 2] !== 'HELD\tchild\t1\t1\t1') return false;
  }
  const diagnosticAt = lines.findIndex((line) => line.startsWith('DIAG\t'));
  if (diagnosticAt < 0) return true;
  return lines.filter((line) => line.startsWith('DIAG\t')).length === 1 &&
    lines[diagnosticAt + 1]?.startsWith('FAIL\tdecode\t') &&
    lines.filter((line) => line.startsWith('FAIL\tdecode\t')).length === 1 &&
    !lines.some((line) => /^(?:SCHEMA|RUNDOWN|COUNTS|HEADER|EVENT|COMPLETE)(?:\t|$)/.test(line));
}

function qualificationSummary(bytes, nativeReady) {
  const source = JSON.parse(bytes.toString('utf8'));
  const claimedPass = source.status === 'native-feasibility-passed-review-required';
  const status = claimedPass && nativeReady && source.receipt?.ok === true &&
    source.rawEtl === 'removed-after-offline-parse' && !source.failure ? source.status : 'failed';
  const summary = { scope: 'T17-Windows-ETW-native-feasibility-only', status,
    limitation: 'Known Node/child positive control only; no Git/TypeScript comparator or no-child claim.' };
  const stages = new Set(['bootstrap', 'host', 'pin', 'bridge', 'receipt', 'native', 'cleanup']);
  const codes = new Set(['operation-failed', 'unsupported-platform', 'node-version', 'bootstrap-identity',
    'archive-hash', 'executable-hash', 'powershell-unavailable', 'oversize', 'bridge-launch',
    'bridge-exit', 'bridge-output', 'receipt-invalid', 'etl-removal-failed']);
  if (source.failure) summary.failure = {
    stage: stages.has(source.failure.stage) ? source.failure.stage : 'receipt',
    code: codes.has(source.failure.code) ? source.failure.code : 'receipt-invalid'
  };
  else if (claimedPass && status === 'failed')
    summary.failure = { stage: 'receipt', code: 'receipt-invalid' };
  if (['removed-after-offline-parse', 'cleanup-failed'].includes(source.rawEtl))
    summary.rawEtl = source.rawEtl;
  if (source.node && source.node.version === 'v24.22.1' &&
    /^[a-f0-9]{64}$/.test(source.node.archiveSha256) &&
    /^[a-f0-9]{64}$/.test(source.node.executableSha256)) summary.node = {
      version: 'v24.22.1', archiveSha256: source.node.archiveSha256,
      executableSha256: source.node.executableSha256
    };
  if (source.bridge) summary.bridge = {
    exitCode: Number.isInteger(source.bridge.exitCode) && source.bridge.exitCode >= 0 &&
      source.bridge.exitCode <= 255 ? source.bridge.exitCode : null,
    launchFailed: source.bridge.launchFailed === true,
    timedOut: source.bridge.timedOut === true,
    stderrCode: ['operation-failed', 'unexpected-output'].includes(source.bridge.stderrCode) ?
      source.bridge.stderrCode : null,
    stdoutPresent: source.bridge.stdoutPresent === true
  };
  if (source.receipt) summary.receipt = {
    ok: source.receipt.ok === true && nativeReady,
    rootPid: pid(String(source.receipt.rootPid)) ? source.receipt.rootPid : null,
    childPid: pid(String(source.receipt.childPid)) ? source.receipt.childPid : null,
    processStarts: Number.isInteger(source.receipt.processStarts) && source.receipt.processStarts >= 0 ?
      source.receipt.processStarts : null,
    processEnds: Number.isInteger(source.receipt.processEnds) && source.receipt.processEnds >= 0 ?
      source.receipt.processEnds : null,
    imageLoads: Number.isInteger(source.receipt.imageLoads) && source.receipt.imageLoads >= 0 ?
      source.receipt.imageLoads : null
  };
  if (source.nativeFailure && ['run', 'root-stop', 'child-stop', 'stop', 'decode', 'receipt'].includes(source.nativeFailure.stage) &&
    /^(native-api|timeout|invalid-data|invalid-state|operation-failed|unobserved|overflow|missing-etl|etl-cap-or-empty|loss)$/.test(source.nativeFailure.code) &&
    Number.isInteger(source.nativeFailure.win32Code) && source.nativeFailure.win32Code >= 0 &&
    source.nativeFailure.win32Code <= 0xffffffff) summary.nativeFailure = {
      stage: source.nativeFailure.stage, code: source.nativeFailure.code,
      win32Code: source.nativeFailure.win32Code
    };
  if (Number.isInteger(source.etlBytes) && source.etlBytes >= 0 && source.etlBytes <= maxEtlBytes)
    summary.etlBytes = source.etlBytes;
  return Buffer.from(`${JSON.stringify(summary, null, 2)}\n`);
}

function prepareArtifactsForUpload() {
  const evidence = resolve(process.env.WINDOWS_ETW_PROBE_EVIDENCE ?? 'windows-etw-probe-evidence');
  try {
    const upload = join(evidence, 'upload');
    mkdirSync(upload, { recursive: true });
    let removed = false;
    let nativeReady = false;
    for (const name of ['native.tsv', 'qualification.json']) {
      const uploadPath = join(upload, name);
      if (existsSync(uploadPath)) unlinkSync(uploadPath);
      const path = join(evidence, name);
      if (!existsSync(path)) continue;
      let oversized = statSync(path).size > maxReceiptBytes;
      const bytes = oversized ? null : readFileSync(path);
      oversized ||= bytes.length > maxReceiptBytes;
      const unsafe = name === 'native.tsv' && !oversized && !safeNativeReceipt(bytes.toString('utf8'));
      if (oversized || unsafe) { unlinkSync(path); removed = true; }
      else {
        const output = name === 'qualification.json' ? qualificationSummary(bytes, nativeReady) : bytes;
        if (output.length > maxReceiptBytes) throw new Error('qualification summary over cap');
        writeFileSync(uploadPath, output, { flag: 'wx' });
        if (name === 'native.tsv') nativeReady = validateProbeReceipt(bytes.toString('utf8'), 'pinned-node').ok;
      }
    }
    if (removed) process.stderr.write('ETW artifact receipt removed: invalid\n');
  } catch {
    process.stderr.write('ETW artifact preparation failed: receipt-check\n');
    process.exitCode = 1;
  }
}

function main() {
  const evidence = resolve(process.env.WINDOWS_ETW_PROBE_EVIDENCE ?? 'windows-etw-probe-evidence');
  try { mkdirSync(evidence, { recursive: true }); }
  catch {
    process.stderr.write('ETW probe failed: evidence/unavailable\n');
    process.exitCode = 1;
    return;
  }
  const report = { scope: 'T17-Windows-ETW-native-feasibility-only', status: 'failed',
    limitation: 'Known Node/child positive control only; no Git/TypeScript comparator or no-child claim.' };
  const save = () => {
    try { writeFileSync(join(evidence, 'qualification.json'), `${JSON.stringify(report, null, 2)}\n`); }
    catch { process.stderr.write('ETW probe failed: evidence/write-failed\n'); process.exitCode = 1; }
  };
  const etl = join(evidence, 'trace.etl');
  let stage = 'host';
  try {
    if (process.platform !== 'win32' || process.arch !== 'x64')
      stop('host', 'unsupported-platform');
    stage = 'pin';
    if (process.version !== 'v24.22.1') stop('pin', 'node-version');
    const manifest = JSON.parse(readFileSync(join(sourceRoot, 'runtime-manifest.json'), 'utf8'));
    const bootstrap = JSON.parse(readFileSync(join(evidence, 'bootstrap.json'), 'utf8'));
    if (bootstrap.status !== 'passed' || bootstrap.native?.node !== manifest.node ||
      bootstrap.sha256 !== manifest.artifacts['win32-x64'].sha256) stop('pin', 'bootstrap-identity');
    const archive = join(bootstrap.directory, basename(new URL(bootstrap.url).pathname));
    if (sha256(archive) !== manifest.artifacts['win32-x64'].sha256) stop('pin', 'archive-hash');
    const node = join(bootstrap.directory, 'node-v24.22.1-win-x64', 'node.exe');
    const member = spawnSync('tar', ['-xOf', archive, 'node-v24.22.1-win-x64/node.exe'],
      { encoding: null, timeout: 120000, maxBuffer: 150000000 });
    const memberDigest = member.stdout?.length ? createHash('sha256').update(member.stdout).digest('hex') : null;
    if (member.error || member.status !== 0 || !memberDigest || memberDigest !== sha256(node))
      stop('pin', 'executable-hash');
    report.node = { version: process.version, archiveSha256: sha256(archive), executableSha256: sha256(node) };
    const powershell = join(process.env.SystemRoot ?? '', 'System32', 'WindowsPowerShell', 'v1.0', 'powershell.exe');
    if (!existsSync(powershell)) stop('bridge', 'powershell-unavailable');
    stage = 'bridge';
    const invocation = spawnSync(powershell, ['-NoProfile', '-NonInteractive', '-File',
      join(sourceRoot, 'windows-etw-probe.ps1'), '-NodePath', node, '-EvidenceDir', evidence,
      '-ExpectedExecutableSha256', memberDigest],
    { cwd: evidence, encoding: 'utf8', timeout: 75000, maxBuffer: 65536 });
    report.bridge = { exitCode: invocation.status, launchFailed: Boolean(invocation.error),
      timedOut: invocation.error?.code === 'ETIMEDOUT',
      stderrCode: !invocation.stderr ? null :
        invocation.stderr.trim() === 'ETW bridge failed: bridge/operation-failed' ? 'operation-failed' : 'unexpected-output',
      stdoutPresent: Boolean(invocation.stdout) };
    const receiptPath = join(evidence, 'native.tsv');
    if (existsSync(receiptPath)) {
      stage = 'receipt';
      if (statSync(receiptPath).size > maxReceiptBytes) {
        unlinkSync(receiptPath);
        stop('receipt', 'oversize');
      }
      const nativeText = readFileSync(receiptPath, 'utf8');
      report.receipt = validateProbeReceipt(nativeText, node);
      const nativeFailure = nativeText.split(/\r?\n/).find((line) => line.startsWith('FAIL\t'));
      if (nativeFailure && safeNativeLine(nativeFailure)) {
        const [, nativeStage, nativeCode, win32Code] = nativeFailure.split('\t');
        report.nativeFailure = { stage: nativeStage, code: nativeCode, win32Code: Number(win32Code) };
      }
      report.etlBytes = existsSync(etl) ? statSync(etl).size : null;
    }
    if (invocation.status === 0 && !report.bridge.stderrCode && !report.bridge.stdoutPresent &&
      report.receipt?.ok && report.etlBytes > 0 && report.etlBytes < maxEtlBytes)
      report.status = 'native-feasibility-passed-review-required';
    else report.failure = { stage: 'native', code: invocation.error ? 'bridge-launch' :
      invocation.status !== 0 ? 'bridge-exit' : report.bridge.stderrCode || report.bridge.stdoutPresent ?
        'bridge-output' : 'receipt-invalid' };
    if (report.status !== 'native-feasibility-passed-review-required') process.exitCode = 1;
  } catch (error) {
    report.failure = error instanceof ProbeFailure ? { stage: error.stage, code: error.code } :
      { stage, code: 'operation-failed' };
    report.status = 'failed';
    process.stderr.write(`ETW probe failed: ${report.failure.stage}/${report.failure.code}\n`);
    process.exitCode = report.failure.code === 'unsupported-platform' ? 2 : 1;
  } finally {
    try {
      if (existsSync(etl)) unlinkSync(etl);
      report.rawEtl = 'removed-after-offline-parse';
    } catch {
      report.rawEtl = 'cleanup-failed';
      report.failure = { stage: 'cleanup', code: 'etl-removal-failed' };
      report.status = 'failed'; process.exitCode = 1;
    }
    save();
  }
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  if (process.argv[2] === '--prepare-artifacts') prepareArtifactsForUpload();
  else main();
}
