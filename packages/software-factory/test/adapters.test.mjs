import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { cpSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';
import { initializeRepositoryStore, openRepositoryStore } from '../dist/store.js';
import { createRepository } from './fixtures/repository.mjs';
const root = fileURLToPath(new URL('../', import.meta.url));
async function fixture(source, config = {}, streamProtocol = false) {
  const repo = createRepository();
  mkdirSync(join(repo.path, '.factory/workflows'), { recursive: true });
  writeFileSync(join(repo.path, '.factory/package.json'), ' {"type":"module"}');
  writeFileSync(
    join(repo.path, '.factory/workflows/agent.ts'),
    `import type { WorkflowContext } from '@local/software-factory';
export async function run(context: WorkflowContext, inputs: Record<string, unknown>) { ${source} }`,
  );
  writeFileSync(
    join(repo.path, '.factory/agents.json'),
    JSON.stringify({
      defaults: {
        harness: 'fake',
        model: 'fixture',
        permissions: 'read-only',
        skillDelivery: 'instructions',
        prompt: 'default',
        skills: [],
      },
      ...config,
    }),
  );
  repo.git(['add', '.factory']);
  repo.git(['commit', '-m', 'Agent workflow', '--only', '.factory']);
  const common = join(repo.path, '.git');
  (await initializeRepositoryStore(common, { release: 'fixture' })).close();
  const tc = join(common, 'factory/toolchain');
  mkdirSync(tc);
  cpSync(join(root, 'node_modules'), join(tc, 'node_modules'), { recursive: true });
  writeFileSync(
    join(tc, 'manifest.json'),
    JSON.stringify({ schema: 1, node: '24.22.1', typescript: '7.0.2', dependencies: { '@types/node': '24.19.2' } }),
  );
  const input = join(common, 'input.json');
  writeFileSync(input, '{}');
  const host = join(common, 'host.mjs');
  writeFileSync(
    host,
    `import {invoke} from ${JSON.stringify(new URL('../dist/lifecycle.js', import.meta.url).href)};
import {openRepositoryStore} from ${JSON.stringify(new URL('../dist/store.js', import.meta.url).href)};
import {appendFileSync} from 'node:fs';
import {createFakeAdapter} from ${JSON.stringify(new URL('../dist/adapters/fake.js', import.meta.url).href)};
const options=JSON.parse(process.argv[2]);
const adapter=createFakeAdapter({executable:process.execPath,script:${JSON.stringify(join(root, 'test/fixtures/agent-harness.mjs'))},reuse:options.fakeReuse!==false});
const requests=[];const start=adapter.start, mapEvent=adapter.mapEvent;
adapter.start=request=>{const store=openRepositoryStore(${JSON.stringify(common)});try{const attempt=store.readAttempt(request.attemptId);if(!attempt.agent||store.readCapture({id:attempt.agent.inputsCaptureId}).state!=='complete')throw new Error('inputs exposed before save');}finally{store.close();}requests.push(request);appendFileSync(request.worktree+'/saved-before-exposure.jsonl','inputs\\n');return start(request);};
adapter.mapEvent=line=>{const store=openRepositoryStore(${JSON.stringify(common)});try{if(!requests.some(request=>{const attempt=store.readAttempt(request.attemptId);return store.readCapture({id:attempt.agent.outputCaptureId}).chunks.map(c=>c.text).join('').includes(line);}))throw new Error('machine event exposed before raw save');}finally{store.close();}appendFileSync(requests[0].worktree+'/saved-before-exposure.jsonl','stream\\n');return mapEvent(line);};
${streamProtocol ? `
adapter.decodeFinal=text=>JSON.parse(text.trim().split('\\n').at(-1));
adapter.mapEvent=()=>undefined;
adapter.start=request=>{
  const script=\`import {appendFileSync} from 'node:fs';
import {spawn} from 'node:child_process';
const context=process.argv[1], nativeId='thread-'+context;
appendFileSync('agent-launches.jsonl',context+'\\\\n');
process.on('exit',code=>appendFileSync('native-exits.jsonl',JSON.stringify({context,code})+'\\\\n'));
if(context.includes('live')){process.on('SIGTERM',()=>appendFileSync('native-signals.jsonl','SIGTERM\\\\n'));setInterval(()=>{},10000);}
process.stdout.write(JSON.stringify({type:'thread.started',nativeId})+'\\\\n');
if(context.includes('bad-event')){
  if(context.includes('closed'))process.stdout.end();
  if(context.includes('escaped')){
    const escaped=spawn(process.execPath,['-e','setInterval(()=>{},10000)'],{detached:true,stdio:['ignore',process.stdout,process.stderr]});
    appendFileSync('escaped-child.pid',String(escaped.pid));escaped.unref();
    setTimeout(()=>process.stderr.write('invalid event bytes\\\\n',()=>process.exit(0)),80);
  }else{setTimeout(()=>process.stderr.write('invalid event bytes\\\\n'),80);setInterval(()=>{},10000);}
}else setTimeout(()=>{
  process.stdout.write(JSON.stringify({type:'turn.completed',tokens:context==='alpha'?7:13})+'\\\\n');
  process.stdout.write(JSON.stringify(context.includes('question')?{kind:'needs_input',question:'Which target?',context:'authoritative saved context'}:{kind:'result',payload:{context}})+'\\\\n');
  if(context.includes('denial')){process.stderr.write('native sandbox violation: denied write\\\\n');if(context.includes('question'))process.stdout.end();process.stderr.end();}
},context==='alpha'?120:80);\`;
  let nativeId;
  const launch={argv:[process.execPath,'--input-type=module','-e',script,request.context],env:{},childScope:'process-group',eventChannels:['stdout','stderr'],mapEvent(line,channel){
    const store=openRepositoryStore(${JSON.stringify(common)});
    try {
      const history=store.readHistory(request.invocationId,{limit:100});
      const capture=history.captures.find(c=>c.attemptId===request.attemptId&&c.channel===(channel==='stdout'?'result':'stderr'));
      if(!capture||!store.readCapture({id:capture.id}).chunks.map(c=>c.text).join('').includes(line))throw new Error('launch event exposed before raw save');
    } finally {store.close();}
    if(channel==='stderr'){if(line.includes('invalid event bytes'))throw new Error('invalid event bytes');if(line.includes('denied write'))throw new Error('native sandbox violation');return;}
    const event=JSON.parse(line);
    if(event.type==='thread.started'){nativeId=event.nativeId;return {nativeId,parentNativeId:null,lifecycle:'running'};}
    if(event.type==='turn.completed')return {nativeId,parentNativeId:null,lifecycle:'succeeded',usage:{tokens:event.tokens,scope:'self'}};
  }};
  if(options.unknownScope)launch.childScope='unknown';
  if(options.streamConfig==='empty')launch.eventChannels=[];
  if(options.streamConfig==='duplicate')launch.eventChannels=['stdout','stdout'];
  if(options.streamConfig==='unknown')launch.eventChannels=['stdin'];
  if(options.streamConfig==='scalar')launch.eventChannels='stdout';
  if(options.streamConfig==='sparse')launch.eventChannels=new Array(1);
  if(options.streamConfig==='mapper')launch.mapEvent=17;
  return launch;
};` : ''}
if(options.stopMode==='hang')adapter.requestStop=()=>new Promise(()=>{});
if(options.stopMode==='reject')adapter.requestStop=()=>Promise.reject(new Error('fixture stop rejected'));
const result=await invoke({...options,adapters:{fake:adapter}});console.log(JSON.stringify(result));process.exit(result.exitCode);`,
  );
  const invoke = (extra = {}) =>
    spawnSync(
      process.execPath,
      [
        host,
        JSON.stringify({
          repository: repo.path,
          workflow: '.factory/workflows/agent.ts',
          input,
          newWorktree: true,
          shutdownGraceMs: 100,
          ...extra,
        }),
      ],
      { encoding: 'utf8', timeout: 30000 },
    );
  const sessions = (id) => {
    const s = openRepositoryStore(common);
    try {
      return s.readSessions({ invocationId: id });
    } finally {
      s.close();
    }
  };
  const history = (id) => {
    const s = openRepositoryStore(common);
    try {
      return s.readHistory(id, { limit: 100 });
    } finally {
      s.close();
    }
  };
  return { ...repo, common, input, invoke, history, sessions };
}
const agents = (h) => h.attempts.filter((a) => a.kind === 'agent');
const text = (h) => JSON.stringify(h.captures);
test('typed workflow runs concurrent real agents with captured effective profiles and independent sessions', async () => {
  const repo = await fixture(
    `const results=await Promise.all([context.agent('build',{profile:'builder',prompt:'step'}),context.agent('review',{profile:'reviewer'})]); return results;`,
    { profiles: { builder: { model: 'builder', prompt: 'profile', skills: [] }, reviewer: { model: 'reviewer' } } },
  );
  try {
    const r = repo.invoke({ agentOverrides: { build: { reasoning: 'high' } } });
    assert.equal(r.status, 0, r.stdout + r.stderr);
    const h = repo.history(JSON.parse(r.stdout).invocationId);
    assert.equal(agents(h).length, 2);
    assert.ok(agents(h).every((a) => a.outcome === 'succeeded' && a.quiescent));
    assert.match(text(h), /builder/);
    assert.match(text(h), /high/);
    assert.match(text(h), /step/);
    assert.match(text(h), /reviewer/);
    const audited = readFileSync(join(JSON.parse(r.stdout).worktree, 'saved-before-exposure.jsonl'), 'utf8')
      .trim()
      .split('\n');
    assert.equal(audited.filter((v) => v === 'inputs').length, 2);
    assert.ok(audited.filter((v) => v === 'stream').length >= 4);
  } finally {
    repo.dispose();
  }
});

for (const mode of ['malformed', 'missing'])
  test(`invalid ${mode} result preserves raw evidence and cannot be ignored`, async () => {
    const repo = await fixture(
      `await context.agent('report',{prompt:'${mode}',output:{name:'summary',validate:(value):value is {summary:string}=>typeof value==='object'&&value!==null&&'summary' in value}});`,
    );
    try {
      const r = repo.invoke();
      assert.equal(r.status, 1, r.stdout + r.stderr);
      const saved = JSON.parse(r.stdout),
        h = repo.history(saved.invocationId);
      assert.equal(agents(h).length, 1);
      assert.equal(agents(h)[0].outcome, 'failed');
      assert.match(saved.diagnostic, /unresolved invalid/);
      assert.ok(h.captures.some((c) => c.channel === 'result'));
      if (mode === 'malformed') assert.match(text(h), /invalid control JSON/);
    } finally {
      repo.dispose();
    }
  });
test('unsupported required capability records selected inputs and launches zero attempts', async () => {
  const repo = await fixture(`await context.agent('blocked',{requiredCapabilities:['universal-child-control']});`);
  try {
    const r = repo.invoke();
    assert.equal(r.status, 1, r.stdout + r.stderr);
    const h = repo.history(JSON.parse(r.stdout).invocationId);
    assert.equal(agents(h).length, 0);
    assert.match(text(h), /universal-child-control/);
  } finally {
    repo.dispose();
  }
});
for (const prompt of ['denied', 'interaction'])
  test(`${prompt} stays terminal without retry, terminal inheritance or invented question`, async () => {
    const repo = await fixture(
      `try {await context.agent('step',{prompt:'${prompt}'});}catch{} await context.agent('late',{});`,
    );
    try {
      const r = repo.invoke();
      assert.equal(r.status, 1, r.stdout + r.stderr);
      const h = repo.history(JSON.parse(r.stdout).invocationId);
      assert.equal(agents(h).length, 1);
      assert.equal(agents(h)[0].outcome, 'failed');
      assert.equal(h.captures.filter((c) => c.channel === 'request').length, 0);
      const logs = readFileSync(join(JSON.parse(r.stdout).worktree, 'agent-launches.jsonl'), 'utf8')
        .trim()
        .split('\n');
      assert.equal(logs.length, 1);
      assert.match(text(h), prompt === 'denied' ? /permission denied/ : /terminal closed:undefined/);
    } finally {
      repo.dispose();
    }
  });
for (const reuse of [true, false])
  test(`explicit correction is one charged attempt with ${reuse ? 'compatible reuse' : 'unsupported reuse fresh'}`, async () => {
    const repo = await fixture(
      `const first=await context.agent('write',{prompt:'malformed'});if(first.status==='invalid')return await context.agent('write',{prompt:'malformed',intent:'format_correction',priorAttemptId:first.attemptId,reuse:true,context:'correct saved invalid output'});`,
    );
    try {
      const r = repo.invoke({ fakeReuse: reuse });
      assert.equal(r.status, 0, r.stdout + r.stderr);
      const h = repo.history(JSON.parse(r.stdout).invocationId),
        a = agents(h);
      assert.equal(a.length, 2);
      assert.deepEqual(
        a.map((x) => x.outcome),
        ['failed', 'succeeded'],
      );
      assert.equal(h.accounting.additionalUsed, 1);
      assert.equal(a[1].agent.sessionMode, reuse ? 'reuse' : 'fresh');
      const lines = readFileSync(join(JSON.parse(r.stdout).worktree, 'agent-launches.jsonl'), 'utf8')
        .trim()
        .split('\n')
        .map(JSON.parse);
      assert.equal(lines.length, 2);
      assert.equal(lines[1].reused, reuse);
      assert.equal(lines[0].nativeId === lines[1].nativeId, reuse);
    } finally {
      repo.dispose();
    }
  });
test('valid question is saved, stops concurrent peer and never launches a format correction', async () => {
  const repo = await fixture(
    `await Promise.all([context.agent('peer',{prompt:'hold'}),context.agent('question',{prompt:'question'})]);`,
  );
  try {
    const start = Date.now(),
      r = repo.invoke();
    assert.equal(
      r.status,
      2,
      r.stdout + r.stderr + JSON.stringify(repo.history(JSON.parse(r.stdout).invocationId).attempts),
    );
    assert.ok(Date.now() - start < 5000);
    const h = repo.history(JSON.parse(r.stdout).invocationId);
    assert.equal(agents(h).length, 2);
    assert.equal(agents(h).find((a) => a.operationKey === 'question').outcome, 'needs_input');
    assert.equal(agents(h).find((a) => a.operationKey === 'peer').outcome, 'interrupted');
    assert.match(text(h), /Which target/);
    assert.equal(h.accounting.additionalUsed, 0);
  } finally {
    repo.dispose();
  }
});
test('agent timeout is enforced and unknown scope retains occupied capacity', async () => {
  const repo = await fixture(`await context.agent('hold',{prompt:'hold',timeoutMs:40});`);
  try {
    const r = repo.invoke();
    assert.equal(r.status, 1, r.stdout + r.stderr);
    const h = repo.history(JSON.parse(r.stdout).invocationId);
    assert.equal(agents(h).length, 1);
    assert.equal(agents(h)[0].outcome, 'failed');
    assert.match(JSON.parse(r.stdout).diagnostic, /timeout/);
  } finally {
    repo.dispose();
  }
});
test('unknown child control does not turn absent optional telemetry into cleanup proof', async () => {
  const repo = await fixture(`await context.agent('unknown',{prompt:'unknown-cleanup'});`);
  try {
    const r = repo.invoke();
    assert.equal(r.status, 1, r.stdout + r.stderr);
    const saved = JSON.parse(r.stdout),
      h = repo.history(saved.invocationId);
    assert.equal(saved.cleanup, 'unknown');
    assert.equal(h.accounting.occupiedAgents, 1);
    const page = repo.sessions(saved.invocationId);
    assert.equal(page.sessions.length, 1);
    assert.deepEqual(page.sessions[0].usage, { state: 'unknown' });
    assert.deepEqual(page.sessions[0].loadedSkills, { state: 'unknown' });
  } finally {
    repo.dispose();
  }
});

test('later selected inputs reread prompt and skill bytes with replacement and targeted overrides', async () => {
  const repo = await fixture(
    `const first=await context.agent('first',{profile:'specialist',skills:[]}); await context.command('edit',{argv:[process.execPath,'-e',"require('node:fs').writeFileSync('.factory/prompt.txt','changed prompt'); require('node:fs').writeFileSync('.factory/skill.txt','changed skill')"],env:{}});const second=await context.agent('second',{profile:'specialist'});return {first,second};`,
    {
      defaults: {
        harness: 'fake',
        model: 'default-model',
        reasoning: 'default-reasoning',
        permissions: 'read-only',
        skillDelivery: 'instructions',
        prompt: 'default',
        skills: [{ name: 'default-skill', file: '.factory/skill.txt' }],
      },
      profiles: {
        specialist: {
          model: 'specialist',
          prompt: { file: '.factory/prompt.txt' },
          skills: [{ name: 'selected', file: '.factory/skill.txt' }],
        },
      },
    },
  );
  try {
    writeFileSync(join(repo.path, '.factory/prompt.txt'), 'original prompt');
    writeFileSync(join(repo.path, '.factory/skill.txt'), 'original skill');
    repo.git(['add', '.factory']);
    repo.git(['commit', '-m', 'Instructions', '--only', '.factory']);
    const r = repo.invoke({ agentOverrides: { first: { model: 'targeted' } } });
    assert.equal(r.status, 0, r.stdout + r.stderr);
    const saved = JSON.parse(r.stdout),
      logs = readFileSync(join(saved.worktree, 'agent-launches.jsonl'), 'utf8').trim().split('\n').map(JSON.parse);
    assert.deepEqual(
      logs.map((x) => [x.inputs.model, x.inputs.prompt, x.inputs.reasoning]),
      [
        ['targeted', 'original prompt', 'default-reasoning'],
        ['specialist', 'changed prompt', 'default-reasoning'],
      ],
    );
    assert.deepEqual(logs[0].inputs.skills, []);
    assert.equal(logs[1].inputs.skills[0].instructions, 'changed skill');
    assert.equal(logs[0].inputs.provenance.model, 'invocation override');
    assert.equal(logs[1].inputs.provenance.model, 'profile:specialist');
  } finally {
    repo.dispose();
  }
});
test('incompatible correction starts fresh exactly once; independent review starts fresh', async () => {
  const repo = await fixture(
    `const first=await context.agent('write',{});await context.agent('write',{intent:'code_correction',priorAttemptId:first.attemptId,reuse:true,context:'explicit saved findings',model:'different'});await context.agent('independent',{purpose:'review'});`,
  );
  try {
    const r = repo.invoke();
    assert.equal(r.status, 0, r.stdout + r.stderr);
    const saved = JSON.parse(r.stdout),
      h = repo.history(saved.invocationId),
      logs = readFileSync(join(saved.worktree, 'agent-launches.jsonl'), 'utf8').trim().split('\n').map(JSON.parse);
    assert.equal(logs.length, 3);
    assert.ok(logs.every((x) => !x.reused));
    assert.equal(new Set(logs.map((x) => x.nativeId)).size, 3);
    assert.equal(h.accounting.additionalUsed, 1);
  } finally {
    repo.dispose();
  }
});
test('failed compatible reuse never launches a fresh retry', async () => {
  const repo = await fixture(
    `const first=await context.agent('write',{prompt:'reuse-fail'});await context.agent('write',{prompt:'reuse-fail',intent:'code_correction',priorAttemptId:first.attemptId,reuse:true,context:'saved findings'});`,
  );
  try {
    const r = repo.invoke();
    assert.equal(r.status, 1, r.stdout + r.stderr);
    const saved = JSON.parse(r.stdout),
      h = repo.history(saved.invocationId),
      logs = readFileSync(join(saved.worktree, 'agent-launches.jsonl'), 'utf8').trim().split('\n').map(JSON.parse);
    assert.equal(logs.length, 2);
    assert.equal(logs[1].reused, true);
    assert.deepEqual(
      agents(h).map((x) => x.outcome),
      ['succeeded', 'failed'],
    );
    assert.equal(h.accounting.additionalUsed, 1);
  } finally {
    repo.dispose();
  }
});
test('later invocation with known session IDs and joined lineage always starts fresh', async () => {
  const repo = await fixture(
    `const prior=inputs.prior;return await context.agent('write',typeof prior==='string'?{intent:'followup',priorAttemptId:prior,context:'explicit saved context'}:{});`,
  );
  try {
    const first = repo.invoke();
    assert.equal(first.status, 0, first.stdout + first.stderr);
    const a = JSON.parse(first.stdout),
      old = agents(repo.history(a.invocationId))[0];
    writeFileSync(repo.input, JSON.stringify({ prior: old.id }));
    const second = repo.invoke({ newWorktree: false, worktreeId: a.worktreeId, runId: a.runId });
    assert.equal(second.status, 0, second.stdout + second.stderr);
    const b = JSON.parse(second.stdout),
      h = repo.history(b.invocationId),
      logs = readFileSync(join(a.worktree, 'agent-launches.jsonl'), 'utf8').trim().split('\n').map(JSON.parse);
    assert.equal(logs.length, 2);
    assert.equal(logs[1].reused, false);
    assert.notEqual(logs[0].nativeId, logs[1].nativeId);
    assert.equal(h.accounting.additionalUsed, 1);
  } finally {
    repo.dispose();
  }
});
test('recorder failure stops a live agent promptly and retains uncertain claim', async () => {
  const repo = await fixture(`await context.agent('hold',{prompt:'hold'});`);
  try {
    const { DatabaseSync } = await import('node:sqlite');
    const db = new DatabaseSync(join(repo.common, 'factory/history.sqlite'));
    db.exec(
      "CREATE TRIGGER fail_agent_output BEFORE INSERT ON capture_chunks WHEN EXISTS (SELECT 1 FROM captures c JOIN attempts a ON c.attempt_id=a.id WHERE c.id=NEW.capture_id AND a.kind='agent' AND c.channel='stderr') BEGIN SELECT RAISE(FAIL,'fixture recording failure'); END;",
    );
    db.close();
    const start = Date.now(),
      r = repo.invoke({ agentTimeoutMs: 2000 });
    assert.equal(r.status, 1, r.stdout + r.stderr);
    assert.ok(Date.now() - start < 1800, 'recording failure must stop before agent timeout');
    const saved = JSON.parse(r.stdout),
      h = repo.history(saved.invocationId);
    assert.equal(saved.cleanup, 'unknown');
    assert.equal(agents(h).length, 1);
    assert.equal(h.accounting.occupiedAgents, 1);
  } finally {
    repo.dispose();
  }
});

test('a successful bounded correction resolves the invalid ancestor chain without rewriting attempts', async () => {
  const repo = await fixture(
    `const a=await context.agent('write',{prompt:'malformed'});const b=await context.agent('write',{prompt:'malformed',intent:'code_correction',priorAttemptId:a.attemptId,context:'saved bad output'});return context.agent('write',{prompt:'malformed',intent:'code_correction',priorAttemptId:b.attemptId,context:'correct saved chain'});`,
  );
  try {
    const r = repo.invoke();
    assert.equal(r.status, 0, r.stdout + r.stderr);
    const h = repo.history(JSON.parse(r.stdout).invocationId);
    assert.deepEqual(
      agents(h).map((a) => a.outcome),
      ['failed', 'failed', 'succeeded'],
    );
    assert.equal(h.accounting.additionalUsed, 2);
  } finally {
    repo.dispose();
  }
});

test('machine-event failure stops a live process immediately instead of waiting for its timeout', async () => {
  const repo = await fixture(`await context.agent('bad',{prompt:'bad-event',timeoutMs:2500});`);
  try {
    const start = Date.now(),
      r = repo.invoke();
    assert.equal(r.status, 1, r.stdout + r.stderr);
    assert.ok(Date.now() - start < 1800);
    const h = repo.history(JSON.parse(r.stdout).invocationId);
    assert.equal(agents(h).length, 1);
    assert.match(text(h), /invalid event bytes/);
  } finally {
    repo.dispose();
  }
});
test('capacity waiters spend no timeout or hidden managed attempts', async () => {
  const repo = await fixture(
    `await Promise.all(['a','b','c'].map(name=>context.agent(name,{context:'wait:200',timeoutMs:300})));`,
  );
  try {
    const r = repo.invoke();
    assert.equal(r.status, 0, r.stdout + r.stderr);
    const h = repo.history(JSON.parse(r.stdout).invocationId);
    assert.equal(agents(h).length, 3);
    assert.equal(h.accounting.additionalUsed, 0);
    assert.equal(h.accounting.occupiedAgents, 0);
  } finally {
    repo.dispose();
  }
});
test('code correction exhaustion never launches a third correction', async () => {
  const repo = await fixture(
    `let result=await context.agent('write',{});for(let i=0;i<3;i++)result=await context.agent('write',{intent:'code_correction',priorAttemptId:result.attemptId,context:'explicit check finding'});`,
  );
  try {
    const r = repo.invoke();
    assert.equal(r.status, 1, r.stdout + r.stderr);
    const saved = JSON.parse(r.stdout),
      h = repo.history(saved.invocationId);
    assert.match(saved.diagnostic, /code correction allowance exhausted/);
    assert.equal(agents(h).length, 3);
    assert.equal(h.accounting.additionalUsed, 2);
    assert.equal(readFileSync(join(saved.worktree, 'agent-launches.jsonl'), 'utf8').trim().split('\n').length, 3);
  } finally {
    repo.dispose();
  }
});
test('profile fallback chains are rejected with zero launch', async () => {
  const repo = await fixture(`await context.agent('selected',{profile:'bad'});`, {
    profiles: { bad: { fallbacks: ['other'] } },
  });
  try {
    const r = repo.invoke();
    assert.equal(r.status, 1, r.stdout + r.stderr);
    const h = repo.history(JSON.parse(r.stdout).invocationId);
    assert.equal(agents(h).length, 0);
    assert.match(JSON.parse(r.stdout).diagnostic, /fallback chains are unsupported/);
  } finally {
    repo.dispose();
  }
});

test('reported child sessions page independently without double-charging parent-inclusive usage', async () => {
  const repo = await fixture(`await context.agent('delegation',{prompt:'children'});`);
  try {
    const r = repo.invoke();
    assert.equal(r.status, 0, r.stdout + r.stderr);
    const saved = JSON.parse(r.stdout),
      h = repo.history(saved.invocationId),
      store = openRepositoryStore(repo.common);
    try {
      const first = store.readSessions({ invocationId: saved.invocationId, limit: 1 });
      assert.equal(first.sessions.length, 1);
      assert.equal(first.hasMore, true);
      const second = store.readSessions({ invocationId: saved.invocationId, after: first.nextCursor, limit: 1 });
      assert.equal(second.sessions.length, 1);
      assert.equal(second.hasMore, false);
      assert.notEqual(first.sessions[0].id, second.sessions[0].id);
      const both = [...first.sessions, ...second.sessions],
        parent = both.find((s) => s.parentNativeId === null),
        child = both.find((s) => s.parentNativeId !== null);
      assert.equal(child.parentNativeId, parent.nativeId);
      assert.deepEqual(parent.usage, { tokens: 9, scope: 'includes-children' });
      assert.deepEqual(child.usage, { tokens: 4, scope: 'self' });
      assert.equal(parent.loadedSkills[0], 'fixture-observed');
      assert.ok(both.every((s) => s.outputCaptureId && s.resultCaptureId && s.inputsCaptureId));
      assert.throws(() => store.readSessions({ invocationId: saved.invocationId, limit: 201 }));
    } finally {
      store.close();
    }
    assert.equal(agents(h).length, 1);
    assert.equal(h.accounting.additionalUsed, 0);
  } finally {
    repo.dispose();
  }
});

test('authoritative question survives uncertain cleanup and is saved before peer shutdown', async () => {
  const repo = await fixture(`await context.agent('question',{prompt:'question-unknown'});`);
  try {
    const r = repo.invoke();
    assert.equal(r.status, 1, r.stdout + r.stderr);
    const saved = JSON.parse(r.stdout),
      h = repo.history(saved.invocationId);
    assert.equal(saved.outcome, 'needs_input');
    assert.equal(saved.cleanup, 'unknown');
    assert.equal(agents(h)[0].outcome, 'needs_input');
    assert.match(text(h), /Which target/);
    assert.equal(h.captures.filter((c) => c.channel === 'request').length, 1);
  } finally {
    repo.dispose();
  }
});

test('a closed authoritative question stops peers while its owner is still running', async () => {
  const repo = await fixture(
    `await Promise.all([context.agent('peer',{prompt:'hold'}),context.agent('early',{prompt:'question-early'})]);`,
  );
  try {
    const start = Date.now(),
      r = repo.invoke();
    assert.equal(r.status, 2, r.stdout + r.stderr);
    assert.ok(Date.now() - start < 2000);
    const saved = JSON.parse(r.stdout),
      h = repo.history(saved.invocationId),
      question = h.captures.find((c) => c.channel === 'request');
    assert.ok(question);
    const store = openRepositoryStore(repo.common);
    try {
      const events = store.readEvents({ after: '0', limit: 200 }).events;
      const savedQuestion = events.find(
        (e) => e.kind === 'capture.appended' && e.data.captureId === question.id && e.data.state === 'complete',
      );
      const peer = agents(h).find((a) => a.operationKey === 'peer');
      const peerStopped = events.find((e) => e.kind === 'attempt.settled' && e.data.attemptId === peer.id);
      assert.ok(BigInt(savedQuestion.cursor) < BigInt(peerStopped.cursor));
    } finally {
      store.close();
    }
    assert.equal(agents(h).length, 2);
  } finally {
    repo.dispose();
  }
});
test('independent native failure outranks its saved valid question without inventing correction', async () => {
  const repo = await fixture(`await context.agent('question',{prompt:'question-fail'});`);
  try {
    const r = repo.invoke();
    assert.equal(r.status, 1, r.stdout + r.stderr);
    const saved = JSON.parse(r.stdout),
      h = repo.history(saved.invocationId);
    assert.equal(saved.outcome, 'failed');
    assert.equal(h.captures.filter((c) => c.channel === 'request').length, 1);
    assert.equal(agents(h).length, 1);
    assert.equal(agents(h)[0].outcome, 'failed');
    assert.equal(h.accounting.occupiedAgents, 0);
  } finally {
    repo.dispose();
  }
});


test('an unresolved invalid result outranks a later saved question', async () => {
  const repo = await fixture(`await context.agent('invalid',{prompt:'malformed'});await context.agent('question',{prompt:'question'});`);
  try {
    const r = repo.invoke();
    assert.equal(r.status, 1, r.stdout + r.stderr);
    const saved = JSON.parse(r.stdout), h = repo.history(saved.invocationId);
    assert.equal(saved.outcome, 'failed');
    assert.match(saved.diagnostic, /unresolved invalid/);
    assert.equal(h.captures.filter(c => c.channel === 'request').length, 1);
    assert.deepEqual(agents(h).map(a => a.outcome), ['failed', 'needs_input']);
  } finally { repo.dispose(); }
});


test('oversized machine lines fail even when their terminating chunk includes a newline', async () => {
  const repo = await fixture(`await context.agent('large',{prompt:'oversized-event'});`);
  try {
    const r = repo.invoke();
    assert.equal(r.status, 1, r.stdout + r.stderr);
    const saved=JSON.parse(r.stdout), h=repo.history(saved.invocationId);
    assert.equal(agents(h).length, 1);
    assert.match(saved.diagnostic, /machine event exceeds size limit/);
    const store=openRepositoryStore(repo.common);
    try {assert.equal(store.readCapture({id:agents(h)[0].agent.outputCaptureId}).state,'partial');}
    finally {store.close();}
  } finally { repo.dispose(); }
});

test('oversized authoritative results remain raw evidence and cannot be ignored', async () => {
  const repo = await fixture(`await context.agent('large',{prompt:'oversized-result'});`);
  try {
    const r=repo.invoke();
    assert.equal(r.status, 1, r.stdout+r.stderr);
    const saved=JSON.parse(r.stdout), h=repo.history(saved.invocationId);
    assert.equal(agents(h).length, 1);
    assert.equal(agents(h)[0].outcome, 'failed');
    assert.match(saved.diagnostic, /unresolved invalid/);
    const store=openRepositoryStore(repo.common);
    try {
      let after=0, bytes=0, page;
      do {
        page=store.readCapture({id:agents(h)[0].agent.resultCaptureId,after,limit:200});
        assert.equal(page.state, 'complete');
        bytes+=page.chunks.reduce((sum,c)=>sum+Buffer.byteLength(c.text),0);
        after=page.nextSequence;
      } while(page.hasMore);
      assert.ok(bytes>1048576);
    } finally { store.close(); }
  } finally { repo.dispose(); }
});


test('session persistence rejects forged ownership, oversized rows and invalid telemetry', async () => {
  const repo=await fixture(`await context.agent('session',{});`);
  try {
    const r=repo.invoke();assert.equal(r.status,0,r.stdout+r.stderr);
    const saved=JSON.parse(r.stdout), attempt=agents(repo.history(saved.invocationId))[0], store=openRepositoryStore(repo.common);
    try {
      const base={nativeId:'external',parentNativeId:null,lifecycle:'running'};
      await assert.rejects(store.saveSession(attempt.id,{...base,id:'forged',attemptId:'other',invocationId:'other'}),/invalid session/);
      await assert.rejects(store.saveSession(attempt.id,{...base,loadedSkills:['x'.repeat(8192)]}),/exceeds limit/);
      await assert.rejects(store.saveSession(attempt.id,{...base,usage:{tokens:-1,scope:'self'}}),/invalid session usage/);
      await assert.rejects(store.saveSession(attempt.id,{...base,usage:0}),/invalid session usage/);
      await assert.rejects(store.saveSession(attempt.id,{...base,loadedSkills:0}),/invalid loaded-skill/);
      await assert.rejects(store.saveSession(attempt.id,{...base,loadedSkills:[17]}),/invalid loaded-skill/);
      assert.equal(store.readSessions({invocationId:saved.invocationId}).sessions.length,1);
    } finally {store.close();}
  } finally {repo.dispose();}
});

test('session pages preserve stable cursors and remain below the serialized byte bound', async () => {
  const repo=await fixture(`await context.agent('session',{});`);
  try {
    const r=repo.invoke();assert.equal(r.status,0,r.stdout+r.stderr);
    const saved=JSON.parse(r.stdout), attempt=agents(repo.history(saved.invocationId))[0], store=openRepositoryStore(repo.common);
    try {
      for(let i=0;i<180;i++) await store.saveSession(attempt.id,{nativeId:'session-'+i,parentNativeId:null,lifecycle:'running',loadedSkills:['x'.repeat(6000)]});
      const first=store.readSessions({invocationId:saved.invocationId,limit:200});
      assert.equal(first.hasMore,true);
      assert.ok(first.sessions.length<181);
      assert.ok(Buffer.byteLength(JSON.stringify(first))<1048576);
      const head=first.sessions[0];
      await store.saveSession(attempt.id,{nativeId:head.nativeId,parentNativeId:null,lifecycle:'stopped'});
      const second=store.readSessions({invocationId:saved.invocationId,after:first.nextCursor,limit:200});
      assert.equal(second.hasMore,false);
      assert.equal(new Set([...first.sessions,...second.sessions].map(s=>s.id)).size,181);
      assert.ok(Buffer.byteLength(JSON.stringify(second))<1048576);
      const updated=store.readSessions({invocationId:saved.invocationId,limit:1});
      assert.equal(updated.nextCursor,1);
      assert.equal(updated.sessions[0].id,head.id);
      assert.equal(updated.sessions[0].lifecycle,'stopped');
      assert.throws(()=>store.readSessions({invocationId:saved.invocationId,after:-1}),/invalid session page/);
    } finally {store.close();}
  } finally {repo.dispose();}
});


test('unsupported selected harness and model fail before launch without substitution', async () => {
  for(const [options,diagnostic] of [[{harness:'absent'},/adapter unavailable: absent/],[{model:'unsupported'},/fake model unsupported/]]) {
    const repo=await fixture(`await context.agent('selected',${JSON.stringify(options)});`);
    try {
      const r=repo.invoke();assert.equal(r.status,1,r.stdout+r.stderr);
      const saved=JSON.parse(r.stdout),h=repo.history(saved.invocationId);
      assert.match(saved.diagnostic,diagnostic);
      assert.equal(agents(h).length,0);
      assert.match(text(h),new RegExp(Object.values(options)[0]));
    } finally {repo.dispose();}
  }
});


for(const [change, expectedAttempts] of [['omit',1],['rename',1],['weaken',2]])
  test(`format correction cannot ${change} the original required payload validator`, async () => {
    const correctionOutput=change==='omit'?'':change==='rename'?",output:{name:'replacement',validate:(value):value is unknown=>true}":",output:{name:'required-number',validate:(value):value is unknown=>true}";
    const repo=await fixture(`const first=await context.agent('write',{output:{name:'required-number',validate:(value):value is number=>typeof value==='number'}});return await context.agent('write',{intent:'format_correction',priorAttemptId:first.attemptId,context:'correct invalid result'${correctionOutput}});`);
    try {
      const r=repo.invoke();assert.equal(r.status,1,r.stdout+r.stderr);
      const saved=JSON.parse(r.stdout),h=repo.history(saved.invocationId);
      assert.equal(saved.outcome,'failed');
      assert.equal(agents(h).length,expectedAttempts);
      assert.ok(agents(h).every(a=>a.outcome==='failed'));
      assert.equal(h.accounting.additionalUsed,expectedAttempts-1);
      assert.match(saved.diagnostic,change==='weaken'?/unresolved invalid/:/preserve output validator/);
    } finally {repo.dispose();}
  });


test('renaming an operation cannot give a failed format correction another format budget', async () => {
  const repo=await fixture(`const first=await context.agent('write',{prompt:'malformed'});const second=await context.agent('write',{prompt:'malformed',intent:'format_correction',priorAttemptId:first.attemptId,context:'still malformed'});return context.agent('renamed',{loopKey:'write',prompt:'malformed',intent:'format_correction',priorAttemptId:second.attemptId,context:'correct now'});`);
  try {
    const r=repo.invoke();assert.equal(r.status,1,r.stdout+r.stderr);
    const saved=JSON.parse(r.stdout),h=repo.history(saved.invocationId);
    assert.match(saved.diagnostic,/format correction cannot correct a format correction/);
    assert.equal(agents(h).length,2);
    assert.deepEqual(agents(h).map(a=>a.outcome),['failed','failed']);
    assert.equal(h.accounting.additionalUsed,1);
  } finally {repo.dispose();}
});

test('reopened store retains the prohibition on recursive format corrections', async () => {
  const repo=await fixture(`const first=await context.agent('write',{prompt:'malformed'});return context.agent('write',{prompt:'malformed',intent:'format_correction',priorAttemptId:first.attemptId,context:'still malformed'});`);
  try {
    const r=repo.invoke();assert.equal(r.status,1,r.stdout+r.stderr);
    const saved=JSON.parse(r.stdout),h=repo.history(saved.invocationId), prior=agents(h)[1];
    const store=openRepositoryStore(repo.common);
    try {
      const next=await store.startInvocation({runId:saved.runId,worktreeId:saved.worktreeId,owner:{host:'fixture',pid:process.pid,start:'fixture'}});
      await store.activateInvocation(next.id);
      await assert.rejects(store.admitAttempt({id:'recursive-format',invocationId:next.id,operationKey:'renamed',loopKey:'write',kind:'agent',intent:'format_correction',priorAttemptId:prior.id}),/format correction cannot correct a format correction/);
      assert.equal(store.readAccounting(saved.runId).additionalUsed,1);
      assert.equal(store.readAccounting(saved.runId).occupiedAgents,0);
      await store.finalizeInvocation({id:next.id,outcome:'failed',cleanup:'complete',claimId:next.claim.id,token:next.claim.token});
    } finally {store.close();}
  } finally {repo.dispose();}
});


for(const prompt of ['bad-event','bad-session','bad-event-unknown'])
  test(`protocol failure ${prompt} settles from actual cleanup evidence`, async () => {
    const repo=await fixture(`await context.agent('bad',{prompt:'${prompt}',timeoutMs:2500});`);
    try {
      const start=Date.now(),r=repo.invoke();assert.equal(r.status,1,r.stdout+r.stderr);
      assert.ok(Date.now()-start<1800);
      const saved=JSON.parse(r.stdout),h=repo.history(saved.invocationId),attempt=agents(h)[0];
      assert.equal(agents(h).length,1);
      assert.equal(attempt.outcome,'failed');
      assert.equal(attempt.quiescent,prompt!=='bad-event-unknown');
      assert.equal(saved.cleanup,prompt==='bad-event-unknown'?'unknown':'complete');
      assert.equal(h.accounting.occupiedAgents,prompt==='bad-event-unknown'?1:0);
      assert.throws(()=>process.kill(-attempt.owner.pid,0),error=>error.code==='ESRCH');
      const store=openRepositoryStore(repo.common);
      try {
        const capture=store.readCapture({id:attempt.agent.outputCaptureId});
        assert.equal(capture.state,'partial');
        assert.match(capture.chunks.map(c=>c.text).join(''),prompt==='bad-session'?/"tokens":-1/:/invalid event bytes/);
        assert.equal(store.inspectOwners().length,prompt==='bad-event-unknown'?1:0);
      } finally {store.close();}
    } finally {repo.dispose();}
  });


test('an explicit correction satisfying the original callable validator resolves its invalid result', async () => {
  const repo=await fixture(`const output={name:'required-number',validate:(value):value is number=>typeof value==='number'};const first=await context.agent('write',{output});return context.agent('write',{output,intent:'format_correction',priorAttemptId:first.attemptId,context:'correct-number'});`);
  try {
    const r=repo.invoke();assert.equal(r.status,0,r.stdout+r.stderr);
    const saved=JSON.parse(r.stdout),h=repo.history(saved.invocationId);
    assert.deepEqual(agents(h).map(a=>a.outcome),['failed','succeeded']);
    assert.ok(agents(h).every(a=>a.agent.validator==='required-number'));
    assert.equal(h.accounting.additionalUsed,1);
  } finally {repo.dispose();}
});

test('an intervening code correction cannot renew an ancestral format budget', async () => {
  const repo=await fixture(`const a=await context.agent('write',{prompt:'malformed'});const b=await context.agent('write',{prompt:'malformed',intent:'format_correction',priorAttemptId:a.attemptId,context:'still malformed'});const c=await context.agent('write',{prompt:'malformed',intent:'code_correction',priorAttemptId:b.attemptId,context:'still malformed'});return context.agent('renamed',{loopKey:'write',prompt:'malformed',intent:'format_correction',priorAttemptId:c.attemptId,context:'correct now'});`);
  try {
    const r=repo.invoke();assert.equal(r.status,1,r.stdout+r.stderr);
    const saved=JSON.parse(r.stdout),h=repo.history(saved.invocationId);
    assert.match(saved.diagnostic,/format correction cannot correct a format correction/);
    assert.equal(agents(h).length,3);
    assert.ok(agents(h).every(a=>a.outcome==='failed'));
    assert.equal(h.accounting.additionalUsed,2);
  } finally {repo.dispose();}
});


test('mutating the caller validator object cannot weaken the saved correction contract', async () => {
  const repo=await fixture(`const output={name:'required-number',validate:(value):value is number=>typeof value==='number'};const first=await context.agent('write',{output});output.validate=(value):value is number=>true;return context.agent('write',{output,intent:'format_correction',priorAttemptId:first.attemptId,context:'correct invalid result'});`);
  try {
    const r=repo.invoke();assert.equal(r.status,1,r.stdout+r.stderr);
    const saved=JSON.parse(r.stdout),h=repo.history(saved.invocationId);
    assert.match(saved.diagnostic,/unresolved invalid/);
    assert.deepEqual(agents(h).map(a=>a.outcome),['failed','failed']);
    assert.equal(h.accounting.additionalUsed,1);
  } finally {repo.dispose();}
});


test('launch-scoped stream context keeps concurrent unkeyed lifecycle and usage on their own native sessions', async () => {
  const repo = await fixture(`await Promise.all(['alpha','beta'].map(contextValue=>context.agent(contextValue,{context:contextValue})));`, {}, true);
  try {
    const r=repo.invoke();
    assert.equal(r.status,0,r.stdout+r.stderr);
    const saved=JSON.parse(r.stdout), h=repo.history(saved.invocationId), sessions=repo.sessions(saved.invocationId).sessions;
    assert.equal(agents(h).length,2);
    assert.equal(sessions.length,2);
    for(const [name,tokens] of [['alpha',7],['beta',13]]) {
      const attempt=agents(h).find(a=>a.operationKey===name), session=sessions.find(s=>s.attemptId===attempt.id);
      assert.equal(session.nativeId,'thread-'+name);
      assert.equal(session.lifecycle,'succeeded');
      assert.deepEqual(session.usage,{tokens,scope:'self'});
    }
    assert.equal(h.accounting.occupiedAgents,0);
  } finally {repo.dispose();}
});


for(const contextValue of ['denial','denial-question'])
  test(`stderr-only denial outranks valid stdout ${contextValue.includes('question')?'question and EOF':'result and exit zero'}`, async () => {
    const repo=await fixture(`await context.agent('denied',{context:'${contextValue}'});`,{},true);
    try {
      const r=repo.invoke();
      assert.equal(r.status,1,r.stdout+r.stderr);
      const saved=JSON.parse(r.stdout), h=repo.history(saved.invocationId), attempt=agents(h)[0];
      assert.equal(saved.outcome,'failed');
      assert.match(saved.diagnostic,/native sandbox violation/);
      assert.equal(saved.cleanup,'complete',JSON.stringify({saved,attempt}));
      assert.equal(agents(h).length,1);
      assert.equal(attempt.outcome,'failed');
      assert.equal(attempt.quiescent,true);
      assert.equal(h.accounting.occupiedAgents,0);
      assert.equal(h.accounting.additionalUsed,0);
      assert.deepEqual(JSON.parse(readFileSync(join(saved.worktree,'native-exits.jsonl'),'utf8').trim()),{context:contextValue,code:0});
      assert.throws(()=>process.kill(-attempt.owner.pid,0),error=>error.code==='ESRCH');
      const store=openRepositoryStore(repo.common);
      try {
        const denial=h.captures.find(c=>c.attemptId===attempt.id&&c.channel==='stderr'), raw=store.readCapture({id:denial.id});
        assert.equal(raw.state,'partial');
        assert.match(raw.chunks.map(c=>c.text).join(''),/native sandbox violation: denied write/);
        assert.equal(store.inspectOwners().length,0);
      } finally {store.close();}
      const requests=h.captures.filter(c=>c.channel==='request');
      assert.equal(requests.length,contextValue.includes('question')?1:0);
      if(requests.length){assert.match(text(h),/Which target/);assert.match(text(h),/authoritative saved context/);}
    } finally {repo.dispose();}
  });


for(const streamConfig of ['empty','duplicate','unknown','scalar','sparse','mapper'])
  test(`invalid launch stream configuration ${streamConfig} settles cleanly before spawn`, async () => {
    const repo=await fixture(`await context.agent('invalid',{context:'alpha'});`,{},true);
    try {
      const r=repo.invoke({streamConfig});
      assert.equal(r.status,1,r.stdout+r.stderr);
      const saved=JSON.parse(r.stdout), h=repo.history(saved.invocationId), attempt=agents(h)[0];
      assert.match(saved.diagnostic,/invalid adapter launch/);
      assert.equal(saved.cleanup,'complete',JSON.stringify({saved,attempt}));
      assert.equal(agents(h).length,1);
      assert.equal(attempt.launch,'not_started');
      assert.equal(attempt.outcome,'failed');
      assert.equal(attempt.quiescent,true);
      assert.equal(h.accounting.occupiedAgents,0);
      assert.equal(h.accounting.additionalUsed,0);
      assert.equal(repo.sessions(saved.invocationId).sessions.length,0);
      assert.throws(()=>readFileSync(join(saved.worktree,'agent-launches.jsonl')),error=>error.code==='ENOENT');
      const store=openRepositoryStore(repo.common);
      try {
        for(const capture of h.captures.filter(c=>c.attemptId===attempt.id))assert.equal(store.readCapture({id:capture.id}).state,'complete');
        assert.equal(store.inspectOwners().length,0);
      } finally {store.close();}
    } finally {repo.dispose();}
  });


for(const shutdownGraceMs of [1,100])
  test(`stream failure stops a still-live resistant owner within its existing ${shutdownGraceMs}ms grace`, async () => {
    const repo=await fixture(`await context.agent('denied',{context:'denial-live',timeoutMs:10000});`,{},true);
    try {
      const started=Date.now(), r=repo.invoke({shutdownGraceMs});
      assert.equal(r.status,1,r.stdout+r.stderr);
      assert.ok(Date.now()-started<2000,'resistant owner must be killed without waiting for its live timer');
      const saved=JSON.parse(r.stdout),h=repo.history(saved.invocationId),attempt=agents(h)[0];
      assert.equal(saved.outcome,'failed');
      assert.equal(saved.cleanup,'complete');
      assert.equal(attempt.outcome,'failed');
      assert.equal(attempt.quiescent,true);
      assert.match(attempt.evidence,/signal=SIGKILL/);
      assert.equal(h.accounting.occupiedAgents,0);
      assert.equal(agents(h).length,1);
      assert.throws(()=>readFileSync(join(saved.worktree,'native-exits.jsonl')),error=>error.code==='ENOENT');
      assert.throws(()=>process.kill(-attempt.owner.pid,0),error=>error.code==='ESRCH');
      const store=openRepositoryStore(repo.common);
      try {assert.equal(store.inspectOwners().length,0);} finally {store.close();}
    } finally {repo.dispose();}
  });


for(const stopMode of ['hang','reject'])for(const channelState of ['open','closed'])
  test(`independent stream failure cleans its live scope when adapter stop ${stopMode}s with stdout ${channelState}`, async () => {
    const repo=await fixture(`await context.agent('bad',{context:'bad-event-${channelState}',timeoutMs:10000});`,{},true);
    let ownerPid;
    try {
      const started=Date.now(),r=repo.invoke({stopMode,shutdownGraceMs:100});
      assert.equal(r.status,1,r.stdout+r.stderr);
      const saved=JSON.parse(r.stdout),h=repo.history(saved.invocationId),attempt=agents(h)[0];
      ownerPid=attempt.owner?.pid;
      assert.equal(saved.outcome,'failed');
      assert.match(saved.diagnostic,/invalid event bytes/);
      assert.equal(saved.cleanup,'complete');
      assert.equal(attempt.outcome,'failed');
      assert.equal(attempt.quiescent,true);
      assert.ok(Date.now()-started<1800,'hung stop callback must not consume invocation drain allowance');
      assert.equal(agents(h).length,1);
      assert.equal(h.accounting.occupiedAgents,0);
      assert.equal(h.accounting.additionalUsed,0);
      assert.throws(()=>process.kill(-ownerPid,0),error=>error.code==='ESRCH');
      const store=openRepositoryStore(repo.common);
      try {
        const capture=h.captures.find(c=>c.attemptId===attempt.id&&c.channel==='stderr'), raw=store.readCapture({id:capture.id});
        assert.equal(raw.state,'partial');
        assert.match(raw.chunks.map(c=>c.text).join(''),/invalid event bytes/);
        assert.equal(store.inspectOwners().length,0);
      } finally {store.close();}
    } finally {
      if(ownerPid)try{process.kill(-ownerPid,'SIGKILL');}catch(error){if(error.code!=='ESRCH')throw error;}
      repo.dispose();
    }
  });


test('an exited owner with escaped inherited pipes keeps stream-failure cleanup unknown', async () => {
  const repo=await fixture(`await context.agent('bad',{context:'bad-event-escaped',timeoutMs:10000});`,{},true);
  let escapedPid;
  try {
    const r=repo.invoke({stopMode:'hang',unknownScope:true,shutdownGraceMs:100});
    assert.equal(r.status,1,r.stdout+r.stderr);
    const saved=JSON.parse(r.stdout),h=repo.history(saved.invocationId),attempt=agents(h)[0];
    escapedPid=Number(readFileSync(join(saved.worktree,'escaped-child.pid'),'utf8'));
    assert.equal(saved.outcome,'failed');
    assert.match(saved.diagnostic,/invalid event bytes/);
    assert.equal(saved.cleanup,'unknown');
    assert.equal(attempt.outcome,'failed');
    assert.equal(attempt.quiescent,false);
    assert.equal(h.accounting.occupiedAgents,1);
    assert.deepEqual(JSON.parse(readFileSync(join(saved.worktree,'native-exits.jsonl'),'utf8').trim()),{context:'bad-event-escaped',code:0});
    assert.throws(()=>process.kill(-attempt.owner.pid,0),error=>error.code==='ESRCH');
    assert.doesNotThrow(()=>process.kill(escapedPid,0));
    const store=openRepositoryStore(repo.common);
    try {assert.equal(store.inspectOwners().length,1);} finally {store.close();}
  } finally {
    if(escapedPid)try{process.kill(-escapedPid,'SIGKILL');}catch(error){if(error.code!=='ESRCH')throw error;}
    repo.dispose();
  }
});
