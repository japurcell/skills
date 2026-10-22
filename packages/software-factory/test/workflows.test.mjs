import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { cpSync, existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';
import { initializeRepositoryStore, openRepositoryStore } from '../dist/store.js';
import { createRepository } from './fixtures/repository.mjs';
const root=fileURLToPath(new URL('../',import.meta.url));
async function fixture(recipe='change',scenario={}) {
  const repo=createRepository();
  mkdirSync(join(repo.path,'.factory/workflows'),{recursive:true});
  writeFileSync(join(repo.path,'.factory/package.json'),'{"type":"module"}');
  for(const name of ['change','audit']) {
    const source=join(root,'templates/workflows',name+'.ts');
    if(existsSync(source)) cpSync(source,join(repo.path,'.factory/workflows',name+'.ts'));
  }
  writeFileSync(join(repo.path,'.factory/agents.json'),JSON.stringify({defaults:{harness:'fake',permissions:'read-only',skillDelivery:'instructions',prompt:'default',skills:[]}}));
  repo.git(['add','.factory']);repo.git(['commit','-m','Install disposable recipes','--only','.factory']);
  const common=join(repo.path,'.git');
  (await initializeRepositoryStore(common,{release:'fixture'})).close();
  const tc=join(common,'factory/toolchain');mkdirSync(tc);
  cpSync(join(root,'node_modules'),join(tc,'node_modules'),{recursive:true});
  writeFileSync(join(tc,'manifest.json'),JSON.stringify({schema:1,node:'24.22.1',typescript:'7.0.2',dependencies:{'@types/node':'24.19.2'}}));
  const input=join(common,'input.json'),host=join(common,'host.mjs');
  writeFileSync(host,`import {invoke} from ${JSON.stringify(new URL('../dist/lifecycle.js',import.meta.url).href)};
import {createFakeAdapter} from ${JSON.stringify(new URL('../dist/adapters/fake.js',import.meta.url).href)};
const options=JSON.parse(process.argv[2]);
const adapter=createFakeAdapter({executable:process.execPath,script:${JSON.stringify(join(root,'test/fixtures/workflow-harness.mjs'))}});
const start=adapter.start;
adapter.start=request=>start({...request,context:JSON.stringify({requestContext:request.context,scenario:${JSON.stringify({...scenario,evidence:common})}})});
const result=await invoke({...options,adapters:{fake:adapter}});console.log(JSON.stringify(result));process.exit(result.exitCode);`);
  const invoke=(inputs,extra={})=>{
    writeFileSync(input,JSON.stringify(inputs));
    const r=spawnSync(process.execPath,[host,JSON.stringify({repository:repo.path,workflow:'.factory/workflows/'+recipe+'.ts',input,newWorktree:true,shutdownGraceMs:100,...extra})],{encoding:'utf8',timeout:60000});
    assert.equal(r.error,undefined);return {...r,saved:r.stdout.trim()?JSON.parse(r.stdout):undefined};
  };
  const history=id=>{const store=openRepositoryStore(common);try{return store.readHistory(id,{limit:100});}finally{store.close();}};
  const report=id=>{const h=history(id),store=openRepositoryStore(common);try{const c=h.captures.find(c=>c.channel==='report');return JSON.parse(store.readCapture({id:c.id}).chunks.map(c=>c.text).join(''));}finally{store.close();}};
  const launches=worktree=>readFileSync(join(common,'workflow-launches.jsonl'),'utf8').trim().split('\n').map(JSON.parse);
  return {...repo,common,invoke,history,report,launches};
}
const agents=h=>h.attempts.filter(a=>a.kind==='agent');
test('change recipe implements, runs selected checks and independently reviews a stable candidate',async()=>{
  const repo=await fixture();
  try {
    const r=repo.invoke({prompt:'Write a harmless fixture change',checks:[{name:'selected-e2e',argv:[process.execPath,'-e',`require('node:fs').appendFileSync(${JSON.stringify(join(repo.common,'sequence.txt'))},'check\\n')`]}]});
    assert.equal(r.status,0,r.stdout+r.stderr+JSON.stringify(repo.history(r.saved.invocationId).captures.filter(c=>c.channel==='stdout'&&c.chunks.some(p=>p.text.includes('error TS')))));
    const requests=repo.launches(r.saved.worktree);
    assert.deepEqual(requests.map(r=>r.phase),['implementation','review']);
    assert.equal(requests[1].inputs.permissions,'read-only');
    assert.equal(requests[1].reused,false);
    assert.match(readFileSync(join(repo.common,'sequence.txt'),'utf8'),/^implementation\ncheck\nreview\n$/);
    assert.equal(repo.report(r.saved.invocationId).status,'complete');
  } finally {repo.dispose();}
});

test('reviewer mutation cannot certify the candidate that passed checks',async()=>{
  const repo=await fixture('change',{writeReview:true});
  try {const r=repo.invoke({prompt:'Harmless change'},{agentOverrides:{'change/review':{permissions:'workspace-write',model:'explicit-review-override'}}});assert.equal(repo.launches(r.saved.worktree)[1].inputs.model,'explicit-review-override');assert.equal(r.status,1,r.stdout+r.stderr);assert.match(r.saved.diagnostic,/candidate changed/);assert.equal(agents(repo.history(r.saved.invocationId)).length,2);}
  finally {repo.dispose();}
});

test('audit investigates varied explicit branches and scopes without an implementation phase',async()=>{
  const repo=await fixture('audit');
  try {
    const r=repo.invoke({prompt:'Audit repository behavior',scopes:[{name:'branch',target:'main~0',questions:'Check history'},{name:'files',target:'tracked.txt',questions:'Inspect content'},{name:'optional',target:'other',skip:true}]});
    assert.equal(r.status,0,r.stdout+r.stderr);
    const launches=repo.launches(r.saved.worktree);
    assert.ok(launches.every(r=>r.inputs.permissions==='read-only'));
    assert.ok(launches.every(r=>r.phase!=='implementation'));
    assert.match(launches[0].context,/main~0/);
    assert.match(launches[1].context,/tracked.txt/);
    assert.equal(repo.report(r.saved.invocationId).investigations.length,2);
    assert.equal(existsSync(join(r.saved.worktree,'candidate.txt')),false);
  } finally {repo.dispose();}
});

for(const [failReviews,expectedStatus] of [[2,0],[3,1]]) test(`quality loop allows two corrections then ${expectedStatus===0?'passes':'fails without a third repair'}`,async()=>{
  const repo=await fixture('change',{failReviews});
  try {
    const r=repo.invoke({plan:'A prose plan',checks:[{name:'unit',argv:[process.execPath,'-e','process.exit(0)']}]});
    assert.equal(r.status,expectedStatus,r.stdout+r.stderr);
    const h=repo.history(r.saved.invocationId), calls=repo.launches(r.saved.worktree);
    assert.deepEqual(calls.map(r=>r.phase),['implementation','review','implementation','review','implementation','review']);
    assert.equal(agents(h).filter(a=>a.intent==='code_correction').length,2);
    assert.equal(h.attempts.filter(a=>a.operationKey==='change/check/unit').length,3);
    assert.equal(h.accounting.additionalUsed,4);
    assert.ok(calls.filter(r=>r.phase==='review').every(r=>!r.reused));
    assert.equal(new Set(calls.filter(r=>r.phase==='review').map(r=>r.attemptId)).size,3);
    if(expectedStatus) assert.match(r.saved.diagnostic,/quality correction allowance exhausted/);
  } finally {repo.dispose();}
});

test('failed selected check gates review and rechecks after concrete repair',async()=>{
  const repo=await fixture();
  try {
    const r=repo.invoke({prompt:'Fix fixture',checks:[{name:'assertion',argv:[process.execPath,'-e',"process.exit(require('node:fs').readFileSync('candidate.txt','utf8').endsWith('1')?0:1)"]}]});
    assert.equal(r.status,0,r.stdout+r.stderr);
    assert.deepEqual(repo.launches(r.saved.worktree).map(r=>r.phase),['implementation','implementation','review']);
    assert.equal(repo.report(r.saved.invocationId).corrections,1);
  } finally {repo.dispose();}
});

for(const recipe of ['change','audit']) test(`${recipe} rejects shell selection in check input before launching work`,async()=>{
  const repo=await fixture(recipe);
  try {
    const input={prompt:'Inspect existing candidate',implement:false,review:false,checks:[{name:'literal-argument',argv:['echo','hello; touch injected.txt'],shell:'/bin/sh'}]};
    if(recipe==='audit') input.scopes=[{name:'files',target:'tracked.txt',skip:true}];
    const r=repo.invoke(input);
    assert.equal(r.status,1,r.stdout+r.stderr);
    assert.match(r.saved.diagnostic,/unsupported check field: shell/);
    assert.equal(repo.history(r.saved.invocationId).attempts.filter(attempt=>attempt.operationKey.startsWith(recipe+'/')).length,0);
    assert.equal(existsSync(join(r.saved.worktree,'injected.txt')),false);
  } finally {repo.dispose();}
});

for(const recipe of ['change','audit']) test(`${recipe} rejects every undocumented check option before workflow phases`,async()=>{
  const repo=await fixture(recipe);
  try {
    for(const [field,value] of [['required',true],['intent','initial'],['priorAttemptId','injected'],['loopKey','injected'],['childScope','process-group'],['arbitrary','injected'],['__proto__','injected']]) {
      const check={name:'selected',argv:['echo','safe'],...Object.fromEntries([[field,value]])};
      const input={prompt:'Inspect existing candidate',implement:false,review:false,checks:[check]};
      if(recipe==='audit') input.scopes=[{name:'files',target:'tracked.txt',skip:true}];
      const r=repo.invoke(input);
      assert.equal(r.status,1,field+' '+r.stdout+r.stderr);
      assert.match(r.saved.diagnostic,new RegExp(`unsupported check field: ${field}`));
      assert.equal(repo.history(r.saved.invocationId).attempts.filter(attempt=>attempt.operationKey.startsWith(recipe+'/')).length,0);
    }
  } finally {repo.dispose();}
});

test('malformed supported check options fail validation before agent or command work',async()=>{
  const repo=await fixture();
  try {
    for(const [extra,diagnostic] of [[{cwd:42},/check cwd must be a string/],[{env:{VALUE:42}},/check env must contain string values/],[{timeoutMs:0},/check timeoutMs must be finite and positive/]]) {
      const r=repo.invoke({prompt:'Inspect existing candidate',checks:[{name:'selected',argv:['echo','safe'],...extra}]});
      assert.equal(r.status,1,r.stdout+r.stderr);
      assert.match(r.saved.diagnostic,diagnostic);
      assert.equal(repo.history(r.saved.invocationId).attempts.filter(attempt=>attempt.operationKey.startsWith('change/')).length,0);
    }
  } finally {repo.dispose();}
});

test('selected check passes shell metacharacters as literal argv data with supported options',async()=>{
  const repo=await fixture();
  try {
    const r=repo.invoke({prompt:'Inspect existing candidate',implement:false,review:false,checks:[{
      name:'literal-argument',argv:[process.execPath,'-e',"require('node:fs').writeFileSync('literal.txt',process.argv[1]+'|'+process.env.FACTORY_CHECK_VALUE)",'hello; touch injected.txt'],
      cwd:'.',env:{FACTORY_CHECK_VALUE:'supported'},timeoutMs:10000,
    }]});
    assert.equal(r.status,0,r.stdout+r.stderr);
    assert.equal(readFileSync(join(r.saved.worktree,'literal.txt'),'utf8'),'hello; touch injected.txt|supported');
    assert.equal(existsSync(join(r.saved.worktree,'injected.txt')),false);
  } finally {repo.dispose();}
});

for(const malformedAlways of [false,true]) test(`invalid output gets exactly one read-only format correction (${malformedAlways?'invalid again':'corrected'})`,async()=>{
  const repo=await fixture('change',{malformed:'implementation',malformedAlways});
  try {
    const r=repo.invoke({prompt:'Return a structured summary'});
    assert.equal(r.status,malformedAlways?1:0,r.stdout+r.stderr);
    const calls=repo.launches(r.saved.worktree),h=repo.history(r.saved.invocationId);
    assert.equal(calls.filter(r=>r.formatCorrection).length,1);
    assert.equal(calls[1].inputs.permissions,'read-only');
    assert.match(calls[1].context,/resultCaptureId/);
    assert.match(calls[1].context,/diagnostic/);
    assert.equal(h.accounting.additionalUsed,1);
    assert.equal(agents(h).length,malformedAlways?2:3);
  } finally {repo.dispose();}
});

test('valid needs_input ends without format correction or review',async()=>{
  const repo=await fixture('change',{question:'implementation'});
  try {const r=repo.invoke({prompt:'Missing target'});assert.equal(r.status,2,r.stdout+r.stderr);assert.equal(r.saved.outcome,'needs_input');assert.equal(agents(repo.history(r.saved.invocationId)).length,1);}
  finally {repo.dispose();}
});

for(const cause of ['permission','cleanup','spawn']) test(`${cause} infrastructure failure is terminal without quality retry`,async()=>{
  const repo=await fixture('change',cause==='permission'?{infrastructure:'implementation'}:{});
  try {
    const inputs={prompt:'Harmless change',...(cause==='cleanup'?{agents:{implementation:{prompt:'unknown-cleanup'}}}:{}),...(cause==='spawn'?{checks:[{name:'missing',argv:['/factory-intentionally-missing-command']}]}:{})};
    const r=repo.invoke(inputs);assert.equal(r.status,1,r.stdout+r.stderr);
    const h=repo.history(r.saved.invocationId);assert.equal(agents(h).length,1);assert.equal(h.accounting.additionalUsed,0);
    assert.equal(repo.launches(r.saved.worktree).length,1);
    if(cause==='cleanup') assert.equal(r.saved.cleanup,'unknown');
  } finally {repo.dispose();}
});

test('no-op repair is charged and followed by a fresh independent review',async()=>{
  const repo=await fixture('change',{failReviews:1,noOpRepairs:true});
  try {const r=repo.invoke({prompt:'No-op repair'});assert.equal(r.status,0,r.stdout+r.stderr);assert.equal(readFileSync(join(r.saved.worktree,'candidate.txt'),'utf8'),'Harmless fixture 0');assert.equal(repo.history(r.saved.invocationId).accounting.additionalUsed,2);assert.equal(repo.launches(r.saved.worktree).length,4);}
  finally {repo.dispose();}
});

test('structured plans skip optional work and selected phase inputs remain independent',async()=>{
  const repo=await fixture();
  try {
    const r=repo.invoke({plan:{steps:[{title:'Do it',prompt:'Selected task'},{title:'Skip it',prompt:'Do not send this',skip:true}]},planning:true,agents:{planning:{model:'planner'},implementation:{model:'writer'},review:{model:'reviewer'}}});
    assert.equal(r.status,0,r.stdout+r.stderr);
    const calls=repo.launches(r.saved.worktree);
    assert.deepEqual(calls.map(r=>r.inputs.model),['planner','writer','reviewer']);
    assert.ok(calls.every(r=>!r.context.includes('Do not send this')));
    assert.ok(repo.report(r.saved.invocationId).skipped.includes('agent-browser-verification'));
    const second=repo.invoke({prompt:'Inspect existing candidate',implement:false,review:false});
    assert.equal(second.status,0,second.stdout+second.stderr);
    assert.deepEqual(repo.report(second.saved.invocationId).skipped,['planning','implementation','agent-browser-verification','review']);
  } finally {repo.dispose();}
});

test('agent browser verification runs only with explicit enablement',async()=>{
  const repo=await fixture();
  try {const r=repo.invoke({prompt:'Explicit browser inspection',browserVerification:{enabled:true}});assert.equal(r.status,0,r.stdout+r.stderr);assert.deepEqual(repo.launches(r.saved.worktree).map(r=>r.phase),['implementation','browser-verification','review']);}
  finally {repo.dispose();}
});

test('joined history retains twenty additional attempts with changed current inputs',async()=>{
  const repo=await fixture();
  try {
    let priorAttempts={},previous;
    for(let i=0;i<=21;i++) {
      const extra=previous?{newWorktree:false,worktreeId:previous.worktreeId,runId:previous.runId}:{};
      const r=repo.invoke({prompt:'Current input '+i,review:false,agents:{implementation:{model:'model-'+i}},priorAttempts},extra);
      if(i===21) {assert.equal(r.status,1,r.stdout+r.stderr);assert.match(r.saved.diagnostic,/additional agent allowance exhausted/);assert.equal(agents(repo.history(r.saved.invocationId)).length,0);break;}
      assert.equal(r.status,0,r.stdout+r.stderr);previous=r.saved;priorAttempts=repo.report(r.saved.invocationId).priorAttempts;
      assert.equal(repo.history(r.saved.invocationId).accounting.additionalUsed,i);
    }
    const calls=repo.launches(previous.worktree);assert.equal(calls.length,21);assert.equal(calls.at(-1).inputs.model,'model-20');assert.match(calls.at(-1).context,/Current input 20/);
  } finally {repo.dispose();}
});

test('audit browser verification is explicit and report corrections preserve repository content',async()=>{
  const repo=await fixture('audit',{failReviews:1});
  try {
    const r=repo.invoke({plan:'Audit plan',scopes:[{name:'history',target:'main'}],browserVerification:{enabled:true}});
    assert.equal(r.status,0,r.stdout+r.stderr);
    const calls=repo.launches(r.saved.worktree);
    assert.deepEqual(calls.map(r=>r.phase),['report','report','browser-verification','report','browser-verification','review','report','browser-verification','review']);
    assert.ok(calls.every(r=>r.inputs.permissions==='read-only'));
    assert.equal(repo.report(r.saved.invocationId).corrections,2);
    assert.equal(readFileSync(join(r.saved.worktree,'tracked.txt'),'utf8'),'committed\n');
  } finally {repo.dispose();}
});

test('review detects changed files even when content contains the next file header',async()=>{
  const repo=await fixture('change',{ambiguousFingerprint:true});
  try {const r=repo.invoke({prompt:'Protect unambiguous candidate identity'});assert.equal(r.status,1,r.stdout+r.stderr);assert.match(r.saved.diagnostic,/candidate changed/);}
  finally {repo.dispose();}
});

test('joined history cannot reset an exhausted quality correction loop',async()=>{
  const repo=await fixture('change',{failReviews:100});
  try {
    const first=repo.invoke({prompt:'Exhaust correction loop'});assert.equal(first.status,1,first.stdout+first.stderr);
    const firstHistory=repo.history(first.saved.invocationId);
    const priorAttempts=Object.fromEntries(agents(firstHistory).map(a=>[a.operationKey,a.id]));
    const second=repo.invoke({prompt:'Explicit follow-up with same loop',priorAttempts},{newWorktree:false,worktreeId:first.saved.worktreeId,runId:first.saved.runId});
    assert.equal(second.status,1,second.stdout+second.stderr);assert.match(second.saved.diagnostic,/code correction allowance exhausted/);
    const h=repo.history(second.saved.invocationId);assert.equal(agents(h).length,2);assert.equal(agents(h).filter(a=>a.intent==='code_correction').length,0);
    assert.equal(h.accounting.additionalUsed,6);
  } finally {repo.dispose();}
});

test('audit checks cannot mutate source or let review certify it',async()=>{
  const repo=await fixture('audit');
  try {
    const r=repo.invoke({prompt:'Read-only audit',scopes:[{name:'files',target:'tracked.txt'}],checks:[{name:'mutating',argv:[process.execPath,'-e',"require('node:fs').writeFileSync('tracked.txt','mutation')"]}]});
    assert.equal(r.status,1,r.stdout+r.stderr);assert.match(r.saved.diagnostic,/candidate changed/);assert.ok(repo.launches(r.saved.worktree).every(r=>r.phase!=='review'));
  } finally {repo.dispose();}
});

for(const [snapshot,diagnostic] of [[{maxBytes:1},/snapshot byte limit/],[{maxEntries:1},/snapshot entry limit/]]) test(`candidate snapshot fails actionably at ${JSON.stringify(snapshot)} without quality repair`,async()=>{
  const repo=await fixture();
  try {const r=repo.invoke({prompt:'Bound candidate snapshot work',snapshot});assert.equal(r.status,1,r.stdout+r.stderr);assert.match(r.saved.diagnostic,diagnostic);const h=repo.history(r.saved.invocationId);assert.equal(agents(h).length,1);assert.equal(h.accounting.additionalUsed,0);}
  finally {repo.dispose();}
});

test('candidate growth beyond explicit byte policy fails before independent review',async()=>{
  const repo=await fixture('change',{largeCandidate:true});
  try {const r=repo.invoke({prompt:'Bound a growing candidate',snapshot:{maxBytes:1048576}});assert.equal(r.status,1,r.stdout+r.stderr);assert.match(r.saved.diagnostic,/snapshot byte limit/);assert.equal(repo.launches(r.saved.worktree).length,1);assert.equal(repo.history(r.saved.invocationId).accounting.additionalUsed,0);}
  finally {repo.dispose();}
});

test('snapshot deadline is terminal and invalid resource policy launches no agent',async()=>{
  const repo=await fixture();
  try {
    const expired=repo.invoke({prompt:'Bound snapshot time',snapshot:{timeoutMs:Number.MIN_VALUE}});assert.equal(expired.status,1,expired.stdout+expired.stderr);assert.match(expired.saved.diagnostic,/snapshot time limit/);assert.equal(repo.launches(expired.saved.worktree).length,1);
    const invalid=repo.invoke({prompt:'Invalid policy',snapshot:{maxEntries:0}});assert.equal(invalid.status,1,invalid.stdout+invalid.stderr);assert.match(invalid.saved.diagnostic,/finite positive/);assert.equal(agents(repo.history(invalid.saved.invocationId)).length,0);
  } finally {repo.dispose();}
});
