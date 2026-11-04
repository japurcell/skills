import assert from 'node:assert/strict';
import { cpSync, lstatSync, readdirSync, readFileSync, readlinkSync, realpathSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';
import { DatabaseSync } from 'node:sqlite';
import { fixture } from './fixtures/learning-extraction-fixture.mjs';
import { openCleanupReadStore } from '../dist/store.js';
import { analyzeCleanupReferences } from '../dist/cleanup-references.js';
import { invoke } from '../dist/lifecycle.js';
import { createFakeAdapter } from '../dist/adapters/fake.js';

const packageRoot = fileURLToPath(new URL('../', import.meta.url));
function authoringFiles(root) {
  const files = {};
  const visit = (path, relative) => {
    const info = lstatSync(path);
    if (info.isSymbolicLink()) files[relative] = ['link', readlinkSync(path)];
    else if (info.isDirectory()) for (const name of readdirSync(path).sort()) visit(join(path, name), `${relative}/${name}`);
    else files[relative] = ['file', info.mode, readFileSync(path)];
  };
  visit(join(root, '.factory'), '.factory');
  for (const name of ['.gitignore', 'tracked.txt', 'untracked.txt', 'ignored.txt']) visit(join(root, name), name);
  return files;
}
function databaseRows(database) {
  const result={};
  for(const {name} of database.prepare("SELECT name FROM sqlite_schema WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name").all()) {
    const statement=database.prepare(`SELECT * FROM "${name.replaceAll('"','""')}" ORDER BY rowid`);
    statement.setReadBigInts(true);result[name]=statement.all();
  }
  return result;
}

test('ordinary workflow reports retain phase evidence and leave setup output unreferenced', async () => {
  const repo = await fixture();
  try {
    cpSync(join(packageRoot, 'templates/workflows/audit.ts'), join(repo.path, '.factory/workflows/audit.ts'));
    for (const workflow of ['change', 'audit']) {
      const path = join(repo.path, `.factory/workflows/${workflow}.ts`);
      const source = readFileSync(path, 'utf8');
      const startup = `await context.command('startup/ordinary-fixture-output/' + raw.prompt, { argv: [${JSON.stringify(process.execPath)}, '-e', ${JSON.stringify("process.stdout.write('ordinary setup output\\n')")} ] });`;
      writeFileSync(path, source.replace('export async function run(context: WorkflowContext, raw: Record<string, unknown>) {',
        `export async function run(context: WorkflowContext, raw: Record<string, unknown>) { ${startup}`));
    }
    repo.git(['add', '.factory']); repo.git(['commit', '-m', 'Install ordinary workflow fixture']);
    const scenario = { kind: 'result', payload: { summary: 'Retained phase result', findings: [], extra: 'raw only' } };
    const check = { name: 'verify', argv: [process.execPath, '-e', 'process.stdout.write("check output")'] };
    const first = repo.invoke('change', { prompt: 'Implement request', checks: [check] }, scenario);
    console.error('change invocation:', first.stdout, first.stderr);
    assert.equal(first.status, 0, first.stdout + first.stderr);
    const firstReport = repo.report(first.saved.invocationId);
    assert.equal(firstReport.version, 1); assert.equal(firstReport.kind, 'change-report');
    assert.deepEqual(firstReport.candidate, { summary: 'Retained phase result' });
    const second = repo.invoke('change', { prompt: 'Replay request', implement: false, review: false, checks: [check], priorAttempts: firstReport.priorAttempts }, scenario,
      { newWorktree: false, worktreeId: first.saved.worktreeId, runId: first.saved.runId });
    console.error('change replay:', second.stdout, second.stderr);
    assert.equal(second.status, 0, second.stdout + second.stderr);
    const secondReport = repo.report(second.saved.invocationId);
    const audit = repo.invoke('audit', { prompt: 'Investigate request', scopes: [{ name: 'scope', target: 'tracked.txt' }], checks: [check] }, scenario);
    console.error('audit invocation:', audit.stdout, audit.stderr);
    assert.equal(audit.status, 0, audit.stdout + audit.stderr);
    const auditReport = repo.report(audit.saved.invocationId);
    assert.equal(auditReport.version, 1); assert.equal(auditReport.kind, 'audit-report');
    assert.deepEqual(auditReport.investigations[0].result, { summary: 'Retained phase result' });
    const read = openCleanupReadStore(repo.common);
    try {
      const graph = analyzeCleanupReferences(read);
      const headers = read.pageCleanupCaptureHeaders().records;
      const attempts = read.pageCleanupAttemptFacts().records;
      const implementation = attempts.find(row => row.id === firstReport.priorAttempts['change/implementation']);
      for (const id of [implementation.agent.resultCaptureId, implementation.agent.validatedResultCaptureId]) {
        const evidence = read.readCleanupCapture({ invocationId: implementation.invocationId, captureId: id });
        assert.equal(JSON.parse(evidence.chunks.map(chunk => chunk.text).join('')).payload.extra, 'raw only');
      }
      const setup = attempts.find(row => row.invocationId === first.saved.invocationId && row.operationKey === 'startup/ordinary-fixture-output/Implement request');
      const output = headers.find(row => row.attemptId === setup?.id && row.channel === 'stdout');
      assert.ok(output);
      const contents = read.readCleanupCapture({ invocationId: output.invocationId, captureId: output.id });
      assert.equal(contents.status, 'present');
      assert.equal(contents.chunks.map(chunk => chunk.text).join(''), 'ordinary setup output\n');
      assert.equal(graph.status, 'complete', JSON.stringify(graph.blockers));
      assert.equal(graph.protected.some(row => row.kind === 'capture' && row.captureId === output.id), false);
      const phaseIds = new Set([firstReport, secondReport, auditReport].flatMap(report => Object.values(report.priorAttempts)));
      const rootFacts = read.pageCleanupInvocationFacts().records;
      for (const owner of rootFacts) {
        assert.ok(graph.protected.some(row => row.kind === 'capture' && row.captureId === owner.inputCaptureId), `unprotected root input ${owner.inputCaptureId}`);
        const saved = read.readCleanupCapture({ invocationId: owner.id, captureId: owner.inputCaptureId });
        const root = JSON.parse(saved.chunks.map(chunk => chunk.text).join(''));
        for (const id of Object.values(root.inputs.priorAttempts ?? {})) phaseIds.add(id);
      }
      const pending = [...phaseIds];
      while (pending.length) {
        const id = pending.pop(), fact = attempts.find(row => row.id === id);
        assert.ok(fact, `missing referenced attempt ${id}`);
        for (const predecessor of [fact.priorAttemptId, fact.agent?.reusedAttemptId]) if (predecessor && !phaseIds.has(predecessor)) {
          phaseIds.add(predecessor); pending.push(predecessor);
        }
      }
      for (const fact of attempts.filter(row => row.operationKey.startsWith('startup/git/') || row.operationKey.startsWith('startup/build/')))
        assert.equal(phaseIds.has(fact.id), false, `startup unexpectedly in declared prior closure ${fact.id}`);
      for (const header of headers.filter(row => row.channel === 'report' || phaseIds.has(row.attemptId) || row.channel === 'context' && attempts.some(fact => fact.id === row.attemptId && fact.kind === 'command')))
        assert.ok(graph.protected.some(row => row.kind === 'capture' && row.captureId === header.id), `unprotected ${header.channel} ${header.id} attempt ${header.attemptId}`);
      for (const fact of attempts.filter(row => phaseIds.has(row.id) && row.agent)) {
        const input = read.readCleanupCapture({ invocationId: fact.invocationId, captureId: fact.agent.inputsCaptureId });
        const source = JSON.parse(input.chunks.map(chunk => chunk.text).join('')).sourceCaptureId;
        assert.ok(graph.protected.some(row => row.kind === 'capture' && row.captureId === source), `unprotected source input ${source}`);
      }
    } finally { read.close(); }
  } finally { repo.dispose(); }
});

test('change report retains the first failing check and correction attempt', async () => {
  const repo = await fixture();
  try {
    const marker = join(repo.common, 'correction-fixture-marker');
    const script = `const fs = require('node:fs'); const marker = ${JSON.stringify(marker)}; if (!fs.existsSync(marker)) { fs.writeFileSync(marker, 'seen'); process.exit(1); }`;
    const result = repo.invoke('change', { prompt: 'Correct the failed check', checks: [{ name: 'once', argv: [process.execPath, '-e', script] }] },
      { kind: 'result', payload: { summary: 'Correction result', findings: [] } });
    console.error('correction invocation:', result.stdout, result.stderr);
    assert.equal(result.status, 0, result.stdout + result.stderr);
    const report = repo.report(result.saved.invocationId);
    assert.equal(report.corrections, 1);
    const reader = openCleanupReadStore(repo.common);
    try {
      const graph = analyzeCleanupReferences(reader), attempts = reader.pageCleanupAttemptFacts().records;
      const headers = reader.pageCleanupCaptureHeaders().records;
      const named = new Set(Object.values(report.priorAttempts));
      const pending = [...named];
      while (pending.length) {
        const id = pending.pop(), fact = attempts.find(row => row.id === id); assert.ok(fact, `missing referenced attempt ${id}`);
        for (const id of [fact.priorAttemptId, fact.agent?.reusedAttemptId]) if (id && !named.has(id)) { named.add(id); pending.push(id); }
      }
      const checkAttempts = attempts.filter(row => row.operationKey === 'change/check/once');
      const implementationAttempts = attempts.filter(row => row.operationKey === 'change/implementation');
      assert.equal(checkAttempts.length, 2); assert.equal(implementationAttempts.length, 2);
      for (const fact of [...checkAttempts, ...implementationAttempts]) assert.ok(named.has(fact.id));
      assert.equal(graph.status, 'complete', JSON.stringify(graph.blockers));
      for (const header of headers.filter(row => named.has(row.attemptId) || row.channel === 'report'))
        assert.ok(graph.protected.some(row => row.kind === 'capture' && row.captureId === header.id), `unprotected ${header.id}`);
    } finally { reader.close(); }
  } finally { repo.dispose(); }
});

test('two check corrections retain all rounds before browser and review', async () => {
  const repo=await fixture();
  try {
    const marker=join(repo.common,'two-corrections-marker');
    const script=`const fs=require('node:fs'),path=${JSON.stringify(marker)};const count=fs.existsSync(path)?Number(fs.readFileSync(path,'utf8')):0;fs.writeFileSync(path,String(count+1));if(count<2)process.exit(1);`;
    const result=repo.invoke('change',{prompt:'Correct twice',checks:[{name:'twice',argv:[process.execPath,'-e',script]}],browserVerification:{enabled:true}},
      {kind:'result',payload:{summary:'Complete',findings:[]}});
    console.error('two corrections invocation:',result.stdout,result.stderr);assert.equal(result.status,0,result.stdout+result.stderr);
    const report=repo.report(result.saved.invocationId);assert.equal(report.corrections,2);
    const reader=openCleanupReadStore(repo.common);try {
      const attempts=reader.pageCleanupAttemptFacts().records,headers=reader.pageCleanupCaptureHeaders().records,graph=analyzeCleanupReferences(reader);
      const expected=attempts.filter(row=>['change/implementation','change/check/twice','change/browser-verification','change/review'].includes(row.operationKey));
      assert.equal(expected.filter(row=>row.operationKey==='change/implementation').length,3);
      assert.equal(expected.filter(row=>row.operationKey==='change/check/twice').length,3);
      assert.equal(expected.filter(row=>row.operationKey==='change/browser-verification').length,1);
      assert.equal(expected.filter(row=>row.operationKey==='change/review').length,1);
      const named=new Set(Object.values(report.priorAttempts)),pending=[...named];
      while(pending.length){const id=pending.pop(),fact=attempts.find(row=>row.id===id);assert.ok(fact);
        for(const prior of [fact.priorAttemptId,fact.agent?.reusedAttemptId])if(prior&&!named.has(prior)){named.add(prior);pending.push(prior);}}
      for(const fact of expected)assert.ok(named.has(fact.id),`phase attempt absent from report lineage ${fact.id}`);
      assert.equal(graph.status,'complete',JSON.stringify(graph.blockers));
      for(const header of headers.filter(row=>expected.some(fact=>fact.id===row.attemptId)))
        assert.ok(graph.protected.some(row=>row.kind==='capture'&&row.captureId===header.id),`unprotected correction round ${header.id}`);
      for(const fact of expected.filter(row=>row.agent)) {
        const saved=reader.readCleanupCapture({invocationId:fact.invocationId,captureId:fact.agent.inputsCaptureId});
        const source=JSON.parse(saved.chunks.map(chunk=>chunk.text).join('')).sourceCaptureId;
        assert.ok(graph.protected.some(row=>row.kind==='capture'&&row.captureId===source),`unprotected source ${source}`);
      }
    } finally {reader.close();}
  } finally {repo.dispose();}
});

test('relative check working directory remains retained evidence', async () => {
  const repo=await fixture();
  try {
    const check={name:'relative-cwd',cwd:'.factory',argv:[process.execPath,'-e',"process.stdout.write(process.cwd())"]};
    const result=repo.invoke('change',{prompt:'Check in a named directory',checks:[check],review:false},
      {kind:'result',payload:{summary:'Candidate'}});
    console.error('relative cwd invocation:',result.stdout,result.stderr);
    assert.equal(result.status,0,result.stdout+result.stderr);
    const report=repo.report(result.saved.invocationId),reader=openCleanupReadStore(repo.common);
    try {
      const attempts=reader.pageCleanupAttemptFacts().records,headers=reader.pageCleanupCaptureHeaders().records;
      const fact=attempts.find(row=>row.id===report.priorAttempts['change/check/relative-cwd']);assert.ok(fact);
      const context=headers.find(row=>row.attemptId===fact.id&&row.channel==='context'),output=headers.find(row=>row.attemptId===fact.id&&row.channel==='stdout');
      assert.ok(context);assert.ok(output);
      const text=header=>reader.readCleanupCapture({invocationId:header.invocationId,captureId:header.id}).chunks.map(chunk=>chunk.text).join('');
      assert.equal(JSON.parse(text(context)).cwd,realpathSync(join(result.saved.worktree,'.factory')));
      assert.equal(text(output),realpathSync(join(result.saved.worktree,'.factory')));
      const graph=analyzeCleanupReferences(reader);assert.equal(graph.status,'complete',JSON.stringify(graph.blockers));
      for(const header of headers.filter(row=>row.attemptId===fact.id))assert.ok(graph.protected.some(row=>row.kind==='capture'&&row.captureId===header.id));
    } finally {reader.close();}
  } finally {repo.dispose();}
});

test('planning with a named profile and invocation override retains composed inputs', async () => {
  const repo=await fixture();
  try {
    writeFileSync(join(repo.path,'.factory/agents.json'),JSON.stringify({
      defaults:{harness:'fake',permissions:'read-only',skillDelivery:'instructions',prompt:'default',skills:[]},
      profiles:{writer:{model:'named-model',reasoning:'deliberate'}}
    }));
    repo.git(['add','.factory/agents.json']);repo.git(['commit','-m','Configure explicit fixture profile']);
    const result=repo.invoke('change',{planning:true,plan:{steps:[{title:'Use',prompt:'Follow this step'},{title:'Skip',prompt:'Do not follow',skip:true}]},
      agents:{planning:{profile:'writer'},implementation:{profile:'writer'}}},
      {kind:'result',payload:{summary:'Profiled result',findings:[]}},
      {agentOverrides:{'change/review':{model:'override-model'}}});
    console.error('profiled invocation:',result.stdout,result.stderr);assert.equal(result.status,0,result.stdout+result.stderr);
    const report=repo.report(result.saved.invocationId),reader=openCleanupReadStore(repo.common);
    try {
      const attempts=reader.pageCleanupAttemptFacts().records,graph=analyzeCleanupReferences(reader);
      for(const [key,model,profile] of [['change/planning','named-model','writer'],['change/implementation','named-model','writer'],['change/review','override-model',null]]) {
        const fact=attempts.find(row=>row.id===report.priorAttempts[key]);assert.ok(fact?.agent);
        const saved=reader.readCleanupCapture({invocationId:fact.invocationId,captureId:fact.agent.inputsCaptureId});
        const wrapper=JSON.parse(saved.chunks.map(chunk=>chunk.text).join(''));
        assert.equal(wrapper.inputs.model,model);assert.equal(wrapper.inputs.profile,profile);
      }
      assert.equal(graph.status,'complete',JSON.stringify(graph.blockers));
    } finally {reader.close();}
  } finally {repo.dispose();}
});

test('audit skipped scope and disabled synthesis retain actual investigation fallback', async () => {
  const repo=await fixture();
  try {
    cpSync(join(packageRoot,'templates/workflows/audit.ts'),join(repo.path,'.factory/workflows/audit.ts'));
    repo.git(['add','.factory/workflows/audit.ts']);repo.git(['commit','-m','Install audit fixture']);
    const result=repo.invoke('audit',{prompt:'Inspect targets',planning:true,synthesis:false,review:false,
      scopes:[{name:'skipped',target:'ignored.txt',skip:true},{name:'kept',target:'tracked.txt'}]},
      {kind:'result',payload:{summary:'Investigation',extra:'retained only in evidence'}});
    console.error('audit fallback invocation:',result.stdout,result.stderr);assert.equal(result.status,0,result.stdout+result.stderr);
    const report=repo.report(result.saved.invocationId);
    assert.deepEqual(report.skipped,['agent-browser-verification','scope:skipped','synthesis','review']);
    assert.deepEqual(report.investigations,[{name:'kept',target:'tracked.txt',result:{summary:'Investigation'}}]);
    assert.deepEqual(JSON.parse(report.candidate.summary),[{name:'kept',target:'tracked.txt',result:{summary:'Investigation',extra:'retained only in evidence'}}]);
    assert.equal(Object.hasOwn(report.priorAttempts,'audit/synthesis'),false);
    const reader=openCleanupReadStore(repo.common);try {const graph=analyzeCleanupReferences(reader);assert.equal(graph.status,'complete',JSON.stringify(graph.blockers));}
    finally {reader.close();}
  } finally {repo.dispose();}
});

test('review findings lead to retained writer corrections in change and audit', async t => {
  for(const workflow of ['change','audit']) await t.test(workflow,async()=>{
    const repo=await fixture();
    try {
      if(workflow==='audit') {
        cpSync(join(packageRoot,'templates/workflows/audit.ts'),join(repo.path,'.factory/workflows/audit.ts'));
        repo.git(['add','.factory/workflows/audit.ts']);repo.git(['commit','-m','Install audit fixture']);
      }
      const input=join(repo.common,'review-input.json'),harness=join(repo.common,'review-harness.mjs'),marker=join(repo.common,'review-marker');
      writeFileSync(input,JSON.stringify(workflow==='audit'?{prompt:'Review audit',scopes:[{name:'scope',target:'tracked.txt'}]}:{prompt:'Review change'}));
      writeFileSync(harness,`import { existsSync, writeFileSync } from 'node:fs';
import { randomUUID } from 'node:crypto';
const request=JSON.parse(process.argv[2]), context=JSON.parse(request.context), marker=${JSON.stringify(marker)};
const first=context.operation.endsWith('/review')&&!existsSync(marker);if(first)writeFileSync(marker,'seen');
process.stderr.write(JSON.stringify({kind:'session',nativeId:randomUUID(),parentNativeId:null,lifecycle:'succeeded'})+'\\n');
process.stdout.write(JSON.stringify({kind:'result',payload:{summary:'Reviewed',findings:first?['Correct this finding']:[]}}));
`);
      const result=await invoke({repository:repo.path,workflow:`.factory/workflows/${workflow}.ts`,input,newWorktree:true,shutdownGraceMs:100,
        adapters:{fake:createFakeAdapter({executable:process.execPath,script:harness})}});
      console.error(`${workflow} review correction invocation:`,JSON.stringify(result));assert.equal(result.outcome,'succeeded',JSON.stringify(result));
      const report=repo.report(result.invocationId);assert.equal(report.corrections,1);
      const reader=openCleanupReadStore(repo.common);try {
        const attempts=reader.pageCleanupAttemptFacts().records,headers=reader.pageCleanupCaptureHeaders().records,graph=analyzeCleanupReferences(reader);
        const writer=workflow==='audit'?'audit/synthesis':'change/implementation';
        const phaseAttempts=attempts.filter(row=>row.operationKey===writer||row.operationKey===`${workflow}/review`);
        assert.equal(phaseAttempts.filter(row=>row.operationKey===writer).length,2);
        assert.equal(phaseAttempts.filter(row=>row.operationKey===`${workflow}/review`).length,2);
        assert.equal(graph.status,'complete',JSON.stringify(graph.blockers));
        for(const header of headers.filter(row=>phaseAttempts.some(fact=>fact.id===row.attemptId)))
          assert.ok(graph.protected.some(row=>row.kind==='capture'&&row.captureId===header.id),`unprotected review repair evidence ${header.id}`);
        for(const fact of phaseAttempts) {
          const saved=reader.readCleanupCapture({invocationId:fact.invocationId,captureId:fact.agent.inputsCaptureId});
          const source=JSON.parse(saved.chunks.map(chunk=>chunk.text).join('')).sourceCaptureId;
          assert.ok(graph.protected.some(row=>row.kind==='capture'&&row.captureId===source),`unprotected review repair source ${source}`);
        }
      } finally {reader.close();}
    } finally {repo.dispose();}
  });
});

test('format correction retains invalid raw output and the corrected result', async t => {
  const repo = await fixture();
  try {
    const input = join(repo.common, 'format-input.json'), harness = join(repo.common, 'format-harness.mjs'), marker = join(repo.common, 'format-marker');
    writeFileSync(input, JSON.stringify({ prompt: 'Correct output format' }));
    writeFileSync(harness, `import { existsSync, writeFileSync } from 'node:fs';
import { randomUUID } from 'node:crypto';
const marker = ${JSON.stringify(marker)};
const first = !existsSync(marker); if (first) writeFileSync(marker, 'seen');
process.stderr.write(JSON.stringify({kind:'session',nativeId:randomUUID(),parentNativeId:null,lifecycle:'succeeded'})+'\\n');
process.stdout.write(JSON.stringify({kind:'result',payload:first ? {unexpected:true} : {summary:'Corrected',findings:[]}}));
`);
    const adapter = createFakeAdapter({ executable: process.execPath, script: harness });
    const result = await invoke({ repository: repo.path, workflow: '.factory/workflows/change.ts', input, newWorktree: true,
      shutdownGraceMs: 100, adapters: { fake: adapter } });
    console.error('format correction invocation:', JSON.stringify(result));
    assert.equal(result.outcome, 'succeeded', JSON.stringify(result));
    const report = repo.report(result.invocationId), reader = openCleanupReadStore(repo.common);let corrected,invalid;
    try {
      const graph = analyzeCleanupReferences(reader), attempts = reader.pageCleanupAttemptFacts().records;
      const headers = reader.pageCleanupCaptureHeaders().records;
      corrected = attempts.find(row => row.id === report.priorAttempts['change/implementation']);
      invalid = attempts.find(row => row.id === corrected?.priorAttemptId);
      assert.equal(invalid?.outcome, 'failed'); assert.equal(invalid?.agent?.validatedResultCaptureId, null);
      assert.ok(invalid?.agent?.resultCaptureId); assert.equal(corrected?.outcome, 'succeeded');
      assert.equal(graph.status, 'complete', JSON.stringify(graph.blockers));
      for (const header of headers.filter(row => row.attemptId === invalid.id || row.attemptId === corrected.id))
        assert.ok(graph.protected.some(row => row.kind === 'capture' && row.captureId === header.id), `unprotected format evidence ${header.id}`);
      for (const fact of [invalid, corrected]) {
        const input = reader.readCleanupCapture({ invocationId: fact.invocationId, captureId: fact.agent.inputsCaptureId });
        const source = JSON.parse(input.chunks.map(chunk => chunk.text).join('')).sourceCaptureId;
        assert.ok(graph.protected.some(row => row.kind === 'capture' && row.captureId === source), `unprotected format source input ${source}`);
      }
    } finally { reader.close(); }
    await t.test('wrong format correction resultCaptureId blocks even when both wrappers agree',()=>{
      const database=new DatabaseSync(join(repo.common,'factory/history.sqlite'));
      try {
        const before=databaseRows(database),files=authoringFiles(repo.path),index=readFileSync(join(repo.common,'index'));
        const rowsFor=id=>database.prepare('SELECT rowid,sequence,text FROM capture_chunks WHERE capture_id=? ORDER BY sequence').all(id);
        const suppliedId=corrected.agent.inputsCaptureId,suppliedRows=rowsFor(suppliedId),supplied=JSON.parse(suppliedRows.map(row=>row.text).join(''));
        const sourceId=supplied.sourceCaptureId,sourceRows=rowsFor(sourceId),source=JSON.parse(sourceRows.map(row=>row.text).join(''));
        const entries=[[suppliedId,suppliedRows,supplied],[sourceId,sourceRows,source]],sequences=entries.map(([id])=>database.prepare('SELECT sequence FROM captures WHERE id=?').get(id).sequence);
        try {
          for(const [id,,value] of entries) {
            const context=JSON.parse(value.context);context.resultCaptureId=invalid.agent.inputsCaptureId;value.context=JSON.stringify(context);
            const text=JSON.stringify(value);assert.ok(Buffer.byteLength(text)<=4096);
            database.prepare('DELETE FROM capture_chunks WHERE capture_id=?').run(id);
            database.prepare('INSERT INTO capture_chunks(capture_id,sequence,text) VALUES (?,1,?)').run(id,text);
            database.prepare('UPDATE captures SET sequence=1 WHERE id=?').run(id);
          }
          const modified=databaseRows(database),read=openCleanupReadStore(repo.common);let graph;
          try {graph=analyzeCleanupReferences(read);} finally {read.close();}
          assert.equal(graph.status,'blocked');assert.ok(graph.blockers.some(row=>row.code==='ownership'));
          for(const id of [suppliedId,sourceId,invalid.agent.resultCaptureId])assert.ok(graph.protected.some(row=>row.kind==='capture'&&row.captureId===id));
          assert.deepEqual(databaseRows(database),modified);assert.deepEqual(authoringFiles(repo.path),files);assert.deepEqual(readFileSync(join(repo.common,'index')),index);
        } finally {
          entries.forEach(([id,saved],index)=>{
            database.prepare('DELETE FROM capture_chunks WHERE capture_id=?').run(id);
            for(const row of saved)database.prepare('INSERT INTO capture_chunks(rowid,capture_id,sequence,text) VALUES (?,?,?,?)').run(row.rowid,id,row.sequence,row.text);
            database.prepare('UPDATE captures SET sequence=? WHERE id=?').run(sequences[index],id);
          });
          assert.deepEqual(databaseRows(database),before);
        }
      } finally {database.close();}
    });
  } finally { repo.dispose(); }
});

test('unrecognized report declarations block while retained records remain untouched', async t => {
  const repo = await fixture();
  try {
    const result = repo.invoke('change', { prompt: 'Produce a report', review: false },
      { kind: 'result', payload: { summary: 'Candidate', ignored: 'retained raw' } });
    console.error('tamper fixture invocation:', result.stdout, result.stderr);
    assert.equal(result.status, 0, result.stdout + result.stderr);
    const other = repo.invoke('change', { prompt: 'Produce another run', review: false },
      { kind: 'result', payload: { summary: 'Foreign candidate' } });
    console.error('foreign fixture invocation:', other.stdout, other.stderr);
    assert.equal(other.status, 0, other.stdout + other.stderr);
    const foreignAttempt = repo.report(other.saved.invocationId).priorAttempts['change/implementation'];
    const reader = openCleanupReadStore(repo.common);
    let header;
    try { header = reader.pageCleanupCaptureHeaders().records.find(row => row.invocationId === result.saved.invocationId && row.channel === 'report'); }
    finally { reader.close(); }
    assert.ok(header);
    const database = new DatabaseSync(join(repo.common, 'factory/history.sqlite'));
    try {
      const original = database.prepare('SELECT rowid,sequence,text FROM capture_chunks WHERE capture_id=? ORDER BY sequence').all(header.id);
      const sequence = database.prepare('SELECT sequence FROM captures WHERE id=?').get(header.id).sequence;
      const report = JSON.parse(original.map(row => row.text).join(''));
      const rows = () => {
        const result = {};
        for (const { name } of database.prepare("SELECT name FROM sqlite_schema WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name").all()) {
          const statement = database.prepare(`SELECT * FROM "${name.replaceAll('"', '""')}" ORDER BY rowid`);
          statement.setReadBigInts(true); result[name] = statement.all();
        }
        return result;
      };
      const originalRows = rows(), index = readFileSync(join(repo.common, 'index')), files = authoringFiles(repo.path);
      for (const [name, mutate, code] of [
        ['historical unversioned report', value => { delete value.version; delete value.kind; }, 'opaque'],
        ['array version', value => { value.version = [1]; }, 'opaque'],
        ['array status', value => { value.status = ['complete']; }, 'opaque'],
        ['unknown kind', value => { value.kind = 'custom-report'; }, 'opaque'],
        ['unknown report field', value => { value.extra = 'unrecognized'; }, 'opaque'],
        ['summary differs from normalized result', value => { value.candidate.summary = 'Different'; }, 'digest'],
        ['missing mapped attempt', value => { value.priorAttempts['change/implementation'] = 'absent-attempt'; }, 'missing'],
        ['foreign mapped attempt', value => { value.priorAttempts['change/implementation'] = foreignAttempt; }, 'foreign'],
      ]) await t.test(name, () => {
        const changed = structuredClone(report); mutate(changed);
        const text = JSON.stringify(changed), chunks = []; let part = '', bytes = 0;
        for (const point of text) { const size = Buffer.byteLength(point); if (bytes + size > 4096) { chunks.push(part); part = ''; bytes = 0; } part += point; bytes += size; }
        if (part) chunks.push(part);
        database.prepare('DELETE FROM capture_chunks WHERE capture_id=?').run(header.id);
        chunks.forEach((part, index) => database.prepare('INSERT INTO capture_chunks(capture_id,sequence,text) VALUES (?,?,?)').run(header.id, index + 1, part));
        database.prepare('UPDATE captures SET sequence=? WHERE id=?').run(chunks.length, header.id);
        try {
          const before = rows(), snapshot = openCleanupReadStore(repo.common);
          let graph; try { graph = analyzeCleanupReferences(snapshot); } finally { snapshot.close(); }
          assert.equal(graph.status, 'blocked'); assert.ok(graph.blockers.some(row => row.code === code), JSON.stringify(graph.blockers));
          assert.ok(graph.protected.some(row => row.kind === 'capture' && row.captureId === header.id));
          assert.deepEqual(rows(), before); assert.deepEqual(readFileSync(join(repo.common, 'index')), index); assert.deepEqual(authoringFiles(repo.path), files);
        } finally {
          database.prepare('DELETE FROM capture_chunks WHERE capture_id=?').run(header.id);
          for (const row of original) database.prepare('INSERT INTO capture_chunks(rowid,capture_id,sequence,text) VALUES (?,?,?,?)').run(row.rowid, header.id, row.sequence, row.text);
          database.prepare('UPDATE captures SET sequence=? WHERE id=?').run(sequence, header.id);
          assert.deepEqual(rows(), originalRows);
        }
      });
      for (const state of ['open','partial','unknown','pruned']) await t.test(`retained report ${state}`, () => {
        database.prepare('UPDATE captures SET state=? WHERE id=?').run(state,header.id);
        try {
          const before=rows(), snapshot=openCleanupReadStore(repo.common); let graph;
          try {graph=analyzeCleanupReferences(snapshot);} finally {snapshot.close();}
          assert.equal(graph.status,'blocked');assert.ok(graph.blockers.some(row=>row.code===(state==='pruned'?'pruned':'partial')));
          assert.ok(graph.protected.some(row=>row.kind==='capture'&&row.captureId===header.id));
          assert.deepEqual(rows(),before);assert.deepEqual(authoringFiles(repo.path),files);assert.deepEqual(readFileSync(join(repo.common,'index')),index);
        } finally {database.prepare("UPDATE captures SET state='complete' WHERE id=?").run(header.id);assert.deepEqual(rows(),originalRows);}
      });
      await t.test('stalled report paging blocks and keeps the known report root', () => {
        const before=rows(), snapshot=openCleanupReadStore(repo.common);let graph;
        try {graph=analyzeCleanupReferences({...snapshot,readCleanupCapture(input){const page=snapshot.readCleanupCapture(input);
          return input.captureId===header.id?{...page,chunks:[],nextSequence:input.after??'0',hasMore:true}:page;}});}
        finally {snapshot.close();}
        assert.equal(graph.status,'blocked');assert.ok(graph.blockers.some(row=>row.code==='partial'));
        assert.ok(graph.protected.some(row=>row.kind==='capture'&&row.captureId===header.id));
        assert.deepEqual(rows(),before);assert.deepEqual(authoringFiles(repo.path),files);assert.deepEqual(readFileSync(join(repo.common,'index')),index);
      });
      await t.test('payload budget exhaustion retains the known report root',()=>{
        const before=rows(),snapshot=openCleanupReadStore(repo.common);let graph;
        try {graph=analyzeCleanupReferences(snapshot,{payloadBytes:1});} finally {snapshot.close();}
        assert.equal(graph.status,'blocked');assert.ok(graph.blockers.some(row=>row.code==='limit'&&row.limit==='payloadBytes'));
        assert.ok(graph.protected.some(row=>row.kind==='capture'&&row.captureId===header.id));
        assert.deepEqual(rows(),before);assert.deepEqual(authoringFiles(repo.path),files);assert.deepEqual(readFileSync(join(repo.common,'index')),index);
      });
      await t.test('cyclic prior lineage blocks and retains the known report root',()=>{
        const before=rows(),snapshot=openCleanupReadStore(repo.common);let graph;
        const id=report.priorAttempts['change/implementation'];
        try {graph=analyzeCleanupReferences({...snapshot,pageCleanupAttemptFacts(input){const page=snapshot.pageCleanupAttemptFacts(input);
          return {...page,records:page.records.map(row=>row.status==='known'&&row.id===id?{...row,priorAttemptId:id}:row)};}});}
        finally {snapshot.close();}
        assert.equal(graph.status,'blocked');assert.ok(graph.blockers.some(row=>row.code==='cycle'));
        assert.ok(graph.protected.some(row=>row.kind==='capture'&&row.captureId===header.id));
        assert.deepEqual(rows(),before);assert.deepEqual(authoringFiles(repo.path),files);assert.deepEqual(readFileSync(join(repo.common,'index')),index);
      });
      await t.test('successful agent with missing normalized result stays blocked',()=>{
        const before=rows(),snapshot=openCleanupReadStore(repo.common);let graph;
        const id=report.priorAttempts['change/implementation'];
        try {graph=analyzeCleanupReferences({...snapshot,pageCleanupAttemptFacts(input){const page=snapshot.pageCleanupAttemptFacts(input);
          return {...page,records:page.records.map(row=>row.status==='known'&&row.id===id?{...row,agent:{...row.agent,validatedResultCaptureId:null}}:row)};}});}
        finally {snapshot.close();}
        assert.equal(graph.status,'blocked');assert.ok(graph.blockers.some(row=>row.code==='ownership'));
        assert.ok(graph.protected.some(row=>row.kind==='capture'&&row.captureId===header.id));
        assert.deepEqual(rows(),before);assert.deepEqual(authoringFiles(repo.path),files);assert.deepEqual(readFileSync(join(repo.common,'index')),index);
      });
      await t.test('invalid UTF-8 report bytes block and restore exact rows',()=>{
        database.prepare("UPDATE capture_chunks SET text=CAST(X'80' AS TEXT) WHERE capture_id=? AND sequence=1").run(header.id);
        try {
          const before=rows(),snapshot=openCleanupReadStore(repo.common);let graph;
          try {graph=analyzeCleanupReferences(snapshot);} finally {snapshot.close();}
          assert.equal(graph.status,'blocked');assert.ok(graph.blockers.some(row=>row.code==='partial'),JSON.stringify(graph.blockers));
          assert.ok(graph.protected.some(row=>row.kind==='capture'&&row.captureId===header.id));
          assert.deepEqual(rows(),before);assert.deepEqual(authoringFiles(repo.path),files);assert.deepEqual(readFileSync(join(repo.common,'index')),index);
        } finally {
          const first=original.find(row=>row.sequence===1);database.prepare('UPDATE capture_chunks SET text=? WHERE capture_id=? AND sequence=1').run(first.text,header.id);
          assert.deepEqual(rows(),originalRows);
        }
      });
      const rootReader=openCleanupReadStore(repo.common);let rootId;
      try {rootId=rootReader.pageCleanupInvocationFacts().records.find(row=>row.id===result.saved.invocationId).inputCaptureId;} finally {rootReader.close();}
      const rootChunks=database.prepare('SELECT rowid,sequence,text FROM capture_chunks WHERE capture_id=? ORDER BY sequence').all(rootId);
      const rootSequence=database.prepare('SELECT sequence FROM captures WHERE id=?').get(rootId).sequence;
      const root=JSON.parse(rootChunks.map(row=>row.text).join(''));
      for(const [name,mutate] of [
        ['unknown root input reference',value=>{value.inputs.extra={captureId:header.id};}],
        ['array phase permission',value=>{value.inputs.agents={implementation:{permissions:['workspace-write']}};}],
      ]) await t.test(name,()=>{
        const changed=structuredClone(root);mutate(changed);const text=JSON.stringify(changed);assert.ok(Buffer.byteLength(text)<=4096);
        database.prepare('DELETE FROM capture_chunks WHERE capture_id=?').run(rootId);
        database.prepare('INSERT INTO capture_chunks(capture_id,sequence,text) VALUES (?,1,?)').run(rootId,text);
        database.prepare('UPDATE captures SET sequence=1 WHERE id=?').run(rootId);
        try {
          const before=rows(),snapshot=openCleanupReadStore(repo.common);let graph;
          try {graph=analyzeCleanupReferences(snapshot);} finally {snapshot.close();}
          assert.equal(graph.status,'blocked');assert.ok(graph.blockers.some(row=>row.code==='opaque'));
          assert.ok(graph.protected.some(row=>row.kind==='capture'&&row.captureId===rootId));
          assert.deepEqual(rows(),before);assert.deepEqual(authoringFiles(repo.path),files);assert.deepEqual(readFileSync(join(repo.common,'index')),index);
        } finally {
          database.prepare('DELETE FROM capture_chunks WHERE capture_id=?').run(rootId);
          for(const row of rootChunks)database.prepare('INSERT INTO capture_chunks(rowid,capture_id,sequence,text) VALUES (?,?,?,?)').run(row.rowid,rootId,row.sequence,row.text);
          database.prepare('UPDATE captures SET sequence=? WHERE id=?').run(rootSequence,rootId);assert.deepEqual(rows(),originalRows);
        }
      });
      await t.test('effective model cannot disagree with every saved profile layer',()=>{
        const read=openCleanupReadStore(repo.common);let fact;
        try {fact=read.pageCleanupAttemptFacts().records.find(row=>row.id===report.priorAttempts['change/implementation']);}
        finally {read.close();}
        assert.ok(fact?.agent);const suppliedId=fact.agent.inputsCaptureId;
        const suppliedRows=database.prepare('SELECT rowid,sequence,text FROM capture_chunks WHERE capture_id=? ORDER BY sequence').all(suppliedId);
        const supplied=JSON.parse(suppliedRows.map(row=>row.text).join('')),sourceId=supplied.sourceCaptureId;
        const sourceRows=database.prepare('SELECT rowid,sequence,text FROM capture_chunks WHERE capture_id=? ORDER BY sequence').all(sourceId);
        const source=JSON.parse(sourceRows.map(row=>row.text).join(''));
        const captures=[[suppliedId,suppliedRows,supplied],[sourceId,sourceRows,source]];
        const sequences=captures.map(([id])=>database.prepare('SELECT sequence FROM captures WHERE id=?').get(id).sequence);
        try {
          for(const [id,,value] of captures) {
            value.inputs.model='forged-model';value.inputs.provenance.model='step';const text=JSON.stringify(value);assert.ok(Buffer.byteLength(text)<=4096);
            database.prepare('DELETE FROM capture_chunks WHERE capture_id=?').run(id);
            database.prepare('INSERT INTO capture_chunks(capture_id,sequence,text) VALUES (?,1,?)').run(id,text);
            database.prepare('UPDATE captures SET sequence=1 WHERE id=?').run(id);
          }
          const before=rows(),snapshot=openCleanupReadStore(repo.common);let graph;
          try {graph=analyzeCleanupReferences(snapshot);} finally {snapshot.close();}
          assert.equal(graph.status,'blocked',JSON.stringify(graph.blockers));
          for(const [id] of captures)assert.ok(graph.protected.some(row=>row.kind==='capture'&&row.captureId===id));
          assert.deepEqual(rows(),before);assert.deepEqual(authoringFiles(repo.path),files);assert.deepEqual(readFileSync(join(repo.common,'index')),index);
        } finally {
          captures.forEach(([id,saved],index)=>{
            database.prepare('DELETE FROM capture_chunks WHERE capture_id=?').run(id);
            for(const row of saved)database.prepare('INSERT INTO capture_chunks(rowid,capture_id,sequence,text) VALUES (?,?,?,?)').run(row.rowid,id,row.sequence,row.text);
            database.prepare('UPDATE captures SET sequence=? WHERE id=?').run(sequences[index],id);
          });
          assert.deepEqual(rows(),originalRows);
        }
      });
    } finally { database.close(); }
  } finally { repo.dispose(); }
});
