import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import test from 'node:test';
import { validateProbeReceipt } from './windows-etw-probe.mjs';

const good = [
  'ABI\t120\t280\t112\t448', 'TOKEN\tadministrator', 'OS\tWindows NT 10.0.26100',
  'API\tstart\t0', 'API\treadyQuery\t0', 'API\tbeforeStopQuery\t0',
  'API\tstop\t0', 'API\topen\t0', 'API\tprocess\t0', 'API\tclose\t0',
  'OWNERSHIP\t11111111-2222-4333-8444-555555555555\tCodex factory ETW feasibility 11111111222243338444555555555555',
  'SESSION\t33554433\t5\t64', 'ROOT\t100\t134000000000000000\tC:\\node\\node.exe',
  'CHILD\t101', 'EVENT\tprocess-start\t100\t50\troot\tnode.exe\t134000000000000000',
  'EVENT\tprocess-start\t101\t100\tchild\tnode.exe\t134000000000100000',
  'EVENT\timage-load\t100\tC:\\node\\node.exe\t134000000000200000',
  'EVENT\timage-load\t101\tC:\\node\\node.exe\t134000000000300000',
  'EVENT\tprocess-end\t101\t100\tchild\t0\t134000000000500000',
  'EVENT\tprocess-end\t100\t50\troot\t0\t134000000000600000',
  'SCHEMA\tProcessId:u32\tParentId:u32\tUniqueProcessKey:pointer\tImageFileName:string\tExitStatus:u32\tImage.ProcessId:u32\tImage.FileName:string',
  'RUNDOWN\t0\t0', 'COUNTS\t20\t6',
  'STATS\t0\t0\t0', 'HEADER\t134000000001000000\t0\t0',
  'FILE\t65536', 'COMPLETE', ''
].join('\n');

test('public receipt accepts a complete known root and child, pending native proof', () => {
  assert.deepEqual(validateProbeReceipt(good, 'C:\\node\\node.exe'), {
    ok: true, reasons: [], rootPid: 100, childPid: 101,
    processStarts: 2, processEnds: 2, imageLoads: 2
  });
});

test('public receipt fails closed on health, schema and missing positive controls', () => {
  for (const changed of [
    good.replace('HEADER\t134000000001000000\t0\t0', 'HEADER\t0\t0\t0'),
    good.replace('STATS\t0\t0\t0', 'STATS\t1\t0\t0'),
    good.replace('API\tstop\t0', 'API\tstop\t5'),
    good.replace('EVENT\tprocess-start\t101\t100\tchild\tnode.exe\t134000000000100000\n', ''),
    good.replace('EVENT\timage-load\t101\tC:\\node\\node.exe\t134000000000300000\n', ''),
    good.replace('COMPLETE\n', ''),
    good.replace('FILE\t65536', 'FILE\t67108864'),
    good.replace('CHILD\t101', 'CHILD\t100'),
    good.replace('EVENT\tprocess-start\t100\t50\troot\tnode.exe\t134000000000000000',
      'EVENT\tprocess-start\t100\t50\troot\tnode.exe\t134000000900000000'),
    good.replace('EVENT\tprocess-end\t101\t100\tchild\t0\t134000000000500000',
      'EVENT\tprocess-end\t101\t100\tchild\t0\t134000000000050000')
  ]) assert.equal(validateProbeReceipt(changed, 'C:\\node\\node.exe').ok, false);
});

test('public CLI rejects unsupported host before native process launch', () => {
  if (process.platform === 'win32') return;
  const cli = fileURLToPath(new URL('./windows-etw-probe.mjs', import.meta.url));
  const result = spawnSync(process.execPath, [cli], { encoding: 'utf8', timeout: 5000 });
  assert.equal(result.status, 2);
  assert.match(result.stderr, /unsupported host/);
});
