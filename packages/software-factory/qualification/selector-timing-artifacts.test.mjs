import assert from 'node:assert/strict';
import { mkdtempSync, readFileSync, readdirSync, realpathSync, rmSync, symlinkSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';
import { randomUUID } from 'node:crypto';
import { createEvidenceRoot, createCollector, collectEvidence, hasSelectorCoverage, validateWorkerClosure } from './selector-timing.mjs';
import { stageSelectorTimingExports } from './selector-timing-artifacts.mjs';

function fixture() {
  const directory = realpathSync(mkdtempSync(join(tmpdir(), 'selector-export-test-')));
  const root = createEvidenceRoot(), collector = createCollector(root);
  collector.mark('worker-open'); collector.close();
  const records = collectEvidence(root).records;
  const context = { sourceSha: 'a'.repeat(40), runtimeSha256: 'b'.repeat(64) };
  const metadata = { schema: 2, status: 'incomplete', ...context, node: 'v24.22.1', platform: 'darwin', arch: 'arm64',
    availableParallelism: 3, runtimeOsRelease: '24.6.0', runnerImage: 'macos15', runnerImageVersion: '20261028.0489.1',
    fixtureExitCode: 1, clock: 'host-monotonic-ms', attemptClock: 'persisted-utc-wall', cpu: 'emitting-process-only', records: records.length };
  writeFileSync(join(directory, 'selector-timing.json'), JSON.stringify(metadata) + '\n', { mode: 0o600 });
  writeFileSync(join(directory, 'selector-timing.jsonl'), records.map(value => JSON.stringify(value) + '\n').join(''), { mode: 0o600 });
  return { directory, root, context, metadata, records, destination: join(directory, 'unused'),
    dispose() { rmSync(directory, { recursive: true, force: true }); rmSync(root.path, { recursive: true, force: true }); } };
}

test('artifact staging preserves valid incomplete red evidence and publishes exactly two validated files', () => {
  const f = fixture();
  try {
    const destination = join(f.root.path, 'upload');
    stageSelectorTimingExports(f.directory, destination, f.context);
    assert.deepEqual(readdirSync(destination).sort(), ['selector-timing.json', 'selector-timing.jsonl']);
    assert.deepEqual(JSON.parse(readFileSync(join(destination, 'selector-timing.json'), 'utf8')), f.metadata);
    assert.throws(() => stageSelectorTimingExports(f.directory, destination, f.context));
  } finally { f.dispose(); }
});

test('artifact staging refuses private fields, false complete coverage and mismatched source before publication', () => {
  for (const corruption of ['metadata', 'record', 'complete', 'source', 'duplicate', 'duplicate-record']) {
    const f = fixture();
    try {
      if (corruption === 'metadata') f.metadata.pid = 123;
      if (corruption === 'complete') f.metadata.status = 'complete';
      if (corruption === 'source') f.metadata.sourceSha = 'c'.repeat(40);
      if (corruption === 'record') f.records[0].path = '/private-value';
      writeFileSync(join(f.directory, 'selector-timing.json'), JSON.stringify(f.metadata) + '\n');
      if (corruption === 'duplicate') writeFileSync(join(f.directory, 'selector-timing.json'), '{"sourceSha":"/private-value",' + JSON.stringify(f.metadata).slice(1) + '\n');
      writeFileSync(join(f.directory, 'selector-timing.jsonl'), f.records.map(value => JSON.stringify(value) + '\n').join(''));
      if (corruption === 'duplicate-record') writeFileSync(join(f.directory, 'selector-timing.jsonl'), '{"workerId":"private-value",' + JSON.stringify(f.records[0]).slice(1) + '\n' + JSON.stringify(f.records[1]) + '\n');
      const destination = join(f.root.path, 'upload');
      assert.throws(() => stageSelectorTimingExports(f.directory, destination, f.context));
      assert.deepEqual(readdirSync(f.root.path).sort(), ['000.jsonl', 'owner.json']);
    } finally { f.dispose(); }
  }
});

function observedTimeline(template) {
  const parent = template.workerId, subject = randomUUID();
  const record = (workerId, sequence, monoMs, stage, extra = {}) => ({ ...template, workerId, sequence, monoMs, stage, ...extra });
  return [
    record(parent, 1, 1, 'worker-open'),
    record(parent, 2, 2, 'worker-bind', { subjectWorkerId: subject }),
    record(subject, 1, 3, 'worker-open'),
    record(subject, 2, 4, 'cancel'),
    record(parent, 3, 5, 'worker-close-observed', { subjectWorkerId: subject, disposition: 'SIGKILL' }),
    record(parent, 4, 6, 'worker-close'),
  ];
}

test('artifact staging distinguishes bound observed closure from a child self receipt', () => {
  const f = fixture();
  try {
    const records = observedTimeline(f.records[0]);
    assert.equal(validateWorkerClosure(records), true);
    assert.equal(records.some(record => record.workerId === records[1].subjectWorkerId && record.stage === 'worker-close'), false);
    f.metadata.records = records.length;
    writeFileSync(join(f.directory, 'selector-timing.json'), JSON.stringify(f.metadata) + '\n');
    writeFileSync(join(f.directory, 'selector-timing.jsonl'), records.map(record => JSON.stringify(record) + '\n').join(''));
    const destination = join(f.root.path, 'upload');
    stageSelectorTimingExports(f.directory, destination, f.context);
    assert.deepEqual(readdirSync(destination).sort(), ['selector-timing.json', 'selector-timing.jsonl']);
  } finally { f.dispose(); }
});

test('complete case coverage still requires bound closure, and valid observed closure can stage complete evidence', () => {
  for (const retainClosure of [false, true]) {
    const f = fixture();
    try {
      let records = observedTimeline(f.records[0]);
      const parent = records[0].workerId, template = records.pop();
      let sequence = 3, monoMs = 6;
      const counts = { 'notification-sender-uncertain':1, 'notification-success-uncertain':1, 'notification-reminder-uncertain':1,
        'notification-records-cli':2, 'notification-records':3, 'notification-records-success':2, 'notification-reminders':13,
        'notification-senders':9, 'notification-preflight':1, 'notification-pipe':3, 'learning':2,
        'learning-extraction-sources':3, 'learning-extraction-evidence':6, 'learning-extraction-paths':2 };
      const add = data => records.push({ ...template, sequence: ++sequence, monoMs: monoMs++, ...data });
      for (const [file, count] of Object.entries(counts)) for (let caseId = 1; caseId <= count; caseId++) {
        const spanId = randomUUID();
        add({ stage:'case', phase:'begin', fileId:file + '.test.mjs', caseId:String(caseId), spanId });
        add({ stage:'case', phase:'end', fileId:file + '.test.mjs', caseId:String(caseId), spanId });
      }
      for (const operationClass of ['startup/git','startup/build','fake-agent','fixture-command']) add({ stage:'attempt', phase:'attempt.settled', at:'2026-11-04T04:20:00.000Z', invocationId:randomUUID(), attemptId:randomUUID(), operationClass });
      add({ stage:'worker-close' });
      assert.equal(hasSelectorCoverage(records), true);
      if (!retainClosure) {
        const observed = records.find(record => record.stage === 'worker-close-observed');
        records = records.filter(record => record !== observed).map(record => record.workerId === parent && record.sequence > observed.sequence ? { ...record, sequence:record.sequence - 1 } : record);
      }
      assert.equal(validateWorkerClosure(records), retainClosure);
      f.metadata.status = 'complete'; f.metadata.fixtureExitCode = 0; f.metadata.records = records.length;
      writeFileSync(join(f.directory, 'selector-timing.json'), JSON.stringify(f.metadata) + '\n');
      writeFileSync(join(f.directory, 'selector-timing.jsonl'), records.map(record => JSON.stringify(record) + '\n').join(''));
      const destination = join(f.root.path, 'upload');
      if (retainClosure) { stageSelectorTimingExports(f.directory, destination, f.context); assert.deepEqual(readdirSync(destination).sort(), ['selector-timing.json', 'selector-timing.jsonl']); }
      else { assert.throws(() => stageSelectorTimingExports(f.directory, destination, f.context)); assert.deepEqual(readdirSync(f.root.path).sort(), ['000.jsonl', 'owner.json']); }
    } finally { f.dispose(); }
  }
});

test('artifact staging rejects unknown, forged, mismatched and duplicate observed relationships even for partial evidence', () => {
  for (const corruption of ['unknown-mapping','unknown-child','mismatched-parent','duplicate','duplicate-bind','cycle','early','outcome']) {
    const f = fixture();
    try {
      let records = observedTimeline(f.records[0]);
      if (corruption === 'unknown-mapping') { records.splice(1, 1); records[3].sequence = 2; records[4].sequence = 3; }
      if (corruption === 'unknown-child') records = records.filter((_, index) => index !== 2 && index !== 3);
      if (corruption === 'mismatched-parent') {
        const other = randomUUID();
        records.splice(4, 0, { ...records[0], workerId: other, monoMs: 4.5 });
        records[5].workerId = other; records[5].sequence = 2; records[6].sequence = 3;
        records.push({ ...records[0], workerId: other, stage: 'worker-close', sequence: 3, monoMs: 7 });
      }
      if (corruption === 'duplicate') { records.splice(5, 0, { ...records[4], sequence: 4, monoMs: 5.5 }); records[6].sequence = 5; }
      if (corruption === 'duplicate-bind') { records.splice(2, 0, { ...records[1], sequence:3, monoMs:2.5 }); records[5].sequence = 4; records[6].sequence = 5; }
      if (corruption === 'cycle') {
        const parent = records[0].workerId, subject = records[2].workerId;
        records = [records[0], records[1], records[2],
          { ...records[1], workerId:subject, subjectWorkerId:parent }, records[4],
          { ...records[4], workerId:subject, subjectWorkerId:parent }].map(record => ({ ...record, monoMs:1 }));
      }
      if (corruption === 'early') records[4].monoMs = 3.5;
      if (corruption === 'outcome') records[4].exitCode = 0;
      f.metadata.records = records.length;
      writeFileSync(join(f.directory, 'selector-timing.json'), JSON.stringify(f.metadata) + '\n');
      writeFileSync(join(f.directory, 'selector-timing.jsonl'), records.map(record => JSON.stringify(record) + '\n').join(''));
      assert.throws(() => stageSelectorTimingExports(f.directory, join(f.root.path, 'upload'), f.context));
      assert.deepEqual(readdirSync(f.root.path).sort(), ['000.jsonl', 'owner.json']);
    } finally { f.dispose(); }
  }
});

test('artifact staging refuses extra files, linked files and oversized exports', () => {
  for (const corruption of ['extra', 'link', 'oversize']) {
    const f = fixture();
    try {
      const file = join(f.directory, 'selector-timing.jsonl');
      if (corruption === 'extra') writeFileSync(join(f.directory, 'private.json'), '{}');
      if (corruption === 'link') { rmSync(file); symlinkSync(join(f.root.path, '000.jsonl'), file); }
      if (corruption === 'oversize') writeFileSync(file, 'x'.repeat(16 * 1024 * 1024 + 1));
      assert.throws(() => stageSelectorTimingExports(f.directory, join(f.root.path, 'upload'), f.context));
    } finally { f.dispose(); }
  }
});
