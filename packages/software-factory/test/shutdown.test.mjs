import { randomUUID } from 'node:crypto';
import assert from 'node:assert/strict';
import { spawn, spawnSync } from 'node:child_process';
import { cpSync, mkdirSync, readFileSync, writeFileSync, existsSync, chmodSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { setTimeout as delay } from 'node:timers/promises';
import test from 'node:test';
import { DatabaseSync } from 'node:sqlite';
import { hostname } from 'node:os';
import { initializeRepositoryStore, openRepositoryStore } from '../dist/store.js';
import { createRepository } from './fixtures/repository.mjs';
const cli = fileURLToPath(new URL('../dist/cli.js', import.meta.url));
const packageRoot = fileURLToPath(new URL('../', import.meta.url));
async function fixture(source) {
  const repo = createRepository();
  mkdirSync(join(repo.path, '.factory/workflows'), { recursive: true });
  writeFileSync(join(repo.path, '.factory/package.json'), '{"type":"module"}');
  writeFileSync(join(repo.path, '.factory/workflows/run.ts'), source);
  repo.git(['add', '.factory']); repo.git(['commit', '-m', 'Commit shutdown workflow', '--only', '.factory']);
  const common = join(repo.path, '.git');
  const store = await initializeRepositoryStore(common, { release: 'fixture' }); store.close();
  const toolchain = join(common, 'factory/toolchain'); mkdirSync(toolchain);
  cpSync(join(packageRoot, 'node_modules'), join(toolchain, 'node_modules'), {recursive: true});
  writeFileSync(join(toolchain, 'manifest.json'), JSON.stringify({schema:1,node:'24.22.1',typescript:'7.0.2',dependencies:{'@types/node':'24.19.2'}}));
  const input = join(common, 'input.json'); writeFileSync(input, '{}');
  const args = extra => [cli, 'invoke', '--repository', repo.path, '--workflow', '.factory/workflows/run.ts', '--input', input, '--new-worktree', '--json', ...extra];
  const invoke = (extra=[]) => spawnSync(process.execPath, args(extra), {encoding:'utf8',timeout:10000});
  const call = extra => spawnSync(process.execPath, [cli, ...extra, '--repository',repo.path,'--json'],{encoding:'utf8',timeout:10000});
  return {...repo, common, input, args, invoke, call};
}
test('saved needs-input stops a live peer without waiting for its ordinary result', async () => {
  const repo = await fixture(`export async function run(c) { void c.command('peer', {argv:[process.execPath,'-e','setTimeout(()=>{},3000)'],env:{}}); await new Promise(resolve=>setTimeout(resolve,100)); await c.needsInput('Choose', 'Need a target'); }`);
  try {
    const started = performance.now(); const result = repo.invoke();
    assert.equal(result.status,2,result.stdout+result.stderr); assert.ok(performance.now()-started < 2500, 'needs-input waited for peer instead of interrupting it');
    const saved = JSON.parse(result.stdout); assert.equal(saved.outcome,'needs_input'); assert.equal(saved.cleanup,'complete');
    const history = JSON.parse(repo.call(['history','--invocation',saved.invocationId]).stdout);
    assert.equal(history.attempts.at(-1).outcome,'interrupted');
    assert.equal(history.captures.find(capture=>capture.channel==='request').state,'complete');
  } finally {repo.dispose();}
});

async function waitFor(action, timeout=8000) {
  const end=performance.now()+timeout;
  while (performance.now()<end) { const value=await action(); if(value) return value; await delay(25); }
  throw new Error('fixture state did not arrive before deadline');
}
function start(repo, extra=[]) {
  const child=spawn(process.execPath,repo.args(extra),{stdio:['ignore','pipe','pipe']}); let stdout='',stderr='';
  child.stdout.on('data',chunk=>{stdout+=chunk;}); child.stderr.on('data',chunk=>{stderr+=chunk;});
  const done=new Promise(resolve=>child.once('close',(status,signal)=>resolve({status,signal,get stdout(){return stdout;},get stderr(){return stderr;}})));
  return {child,done};
}
async function active(repo, key) {
  return waitFor(()=>{
    const store=openRepositoryStore(repo.common);
    try { for(const claim of store.inspectOwners()) { if(!claim.invocationId)continue; const attempt=store.inspectActivity(claim.invocationId).attempts.find(a=>a.operationKey===key&&a.launch==='started'); if(attempt)return {claim,attempt}; } }
    finally {store.close();}
  });
}
test('command timeout escalates an owned SIGTERM-ignoring process within bounded grace', async()=>{
  const repo=await fixture(`export async function run(c){await c.command('ignore',{argv:[process.execPath,'-e','process.on("SIGTERM",()=>{});setInterval(()=>{},1000)'],env:{},timeoutMs:150});}`);
  try {
    const before=performance.now();const result=repo.invoke(['--shutdown-grace-ms','100']);
    assert.equal(result.status,1,result.stdout+result.stderr); assert.ok(performance.now()-before<3000);
    const saved=JSON.parse(result.stdout);assert.equal(saved.outcome,'failed');assert.equal(saved.cleanup,'complete');assert.match(saved.diagnostic,/timeout/);
    const history=JSON.parse(repo.call(['history','--invocation',saved.invocationId]).stdout);
    assert.equal(history.attempts.at(-1).outcome,'failed');assert.match(history.attempts.at(-1).evidence,/SIGKILL/);
  }finally{repo.dispose();}
});
for(const [signal,status] of [['SIGINT',130],['SIGTERM',143]]) {
  test(`handled ${signal} interrupts real managed work and preserves candidate files`,async()=>{
    const repo=await fixture(`export async function run(c){await c.command('working',{argv:[process.execPath,'-e','require("node:fs").writeFileSync("candidate.txt","preserved");setInterval(()=>{},1000)'],env:{}});}`);
    let running;
    try {
      running=start(repo,['--shutdown-grace-ms','100']);const owned=await active(repo,'working');
      await waitFor(()=>existsSync(join(openWorktree(repo,owned.claim),'candidate.txt')));
      const inspection=repo.call(['inspect-owner','--claim',owned.claim.id]);assert.equal(inspection.status,0,inspection.stderr);assert.equal(JSON.parse(inspection.stdout)[0].inspection.state,'known_live');
      const refused=repo.call(['clear-owner','--claim',owned.claim.id,'--token',owned.claim.token,'--operator-confirmed','--note','must refuse live owner']);assert.equal(refused.status,3);assert.match(refused.stderr,/known-live/);
      running.child.kill(signal);const result=await running.done;assert.equal(result.status,status,result.stdout+result.stderr);
      const saved=JSON.parse(result.stdout);assert.equal(saved.outcome,'interrupted');assert.equal(saved.cleanup,'complete');
      assert.equal(readFileSync(join(saved.worktree,'candidate.txt'),'utf8'),'preserved');
      const history=JSON.parse(repo.call(['history','--invocation',saved.invocationId]).stdout);assert.equal(history.attempts.at(-1).outcome,'interrupted');
      assert.deepEqual(JSON.parse(repo.call(['inspect-owner']).stdout),[]);
    }finally{running?.child.kill('SIGKILL');repo.dispose();}
  });
}
function openWorktree(repo,claim){const store=openRepositoryStore(repo.common);try{return store.readWorktree(store.readInvocation(claim.invocationId).worktreeId).path;}finally{store.close();}}
test('late unawaited scope work is bounded and cannot write to a closed store',async()=>{
  const repo=await fixture(`export async function run(c){void c.scope('late',async s=>{await new Promise(resolve=>setTimeout(resolve,3000));await s.progress('must not write after finalization');});await c.needsInput('Choose','Need a target');}`);
  try {const before=performance.now();const result=repo.invoke(['--shutdown-grace-ms','50']);assert.equal(result.status,1,result.stdout+result.stderr);assert.ok(performance.now()-before<2500);assert.equal(JSON.parse(result.stdout).cleanup,'unknown');assert.doesNotMatch(result.stderr,/database.*closed|unhandled/i);}
  finally{repo.dispose();}
});

test('inherited pipes are bounded and unsupported escaped children retain blocked ownership',async()=>{
  const repo=await fixture(`export async function run(c){await c.command('escaped',{argv:[process.execPath,'-e','const fs=require("node:fs"),{spawn}=require("node:child_process");const child=spawn(process.execPath,["-e","setInterval(()=>{},1000)"],{detached:true,stdio:["ignore",1,2]});fs.writeFileSync("escaped.pid",String(child.pid));child.unref();process.exit(0)'],env:{},childScope:'unknown'});}`);
  let escaped;
  try {
    const before=performance.now();const result=repo.invoke(['--shutdown-grace-ms','100']);assert.equal(result.status,1,result.stdout+result.stderr);assert.ok(performance.now()-before<3000);
    const saved=JSON.parse(result.stdout);assert.equal(saved.cleanup,'unknown');escaped=Number(readFileSync(join(saved.worktree,'escaped.pid'),'utf8'));
    process.kill(escaped,0);
    const inspection=JSON.parse(repo.call(['inspect-owner']).stdout);assert.equal(inspection.length,1);assert.equal(inspection[0].inspection.state,'unknown');
    const denied=repo.call(['invoke','--workflow','.factory/workflows/run.ts','--input',repo.input,'--worktree',saved.worktreeId]);assert.equal(denied.status,3);assert.match(denied.stderr,/claimed/);
    const history=JSON.parse(repo.call(['history','--invocation',saved.invocationId]).stdout);assert.equal(history.accounting.occupiedCommands,1);assert.ok(history.captures.some(capture=>capture.state==='partial'));
  }finally{if(escaped){try{process.kill(escaped,'SIGKILL');}catch{}}repo.dispose();}
});
test('exact-claim clearance saves unknown identity limitations and cannot clear replacement ownership',async()=>{
  const repo=await fixture(`export async function run(c){await c.progress('current entry');}`);let store;
  try {
    store=openRepositoryStore(repo.common);const run=await store.createRun();const worktree=await store.registerWorktree({path:repo.path,registration:'fixture'});
    const owner={host:hostname(),pid:process.pid,start:null};const invocation=await store.startInvocation({runId:run.id,worktreeId:worktree.id,owner});store.close();store=undefined;
    const inspection=JSON.parse(repo.call(['inspect-owner','--claim',invocation.claim.id]).stdout)[0];assert.equal(inspection.inspection.state,'unknown');
    const noConfirmation=repo.call(['clear-owner','--claim',invocation.claim.id,'--token',invocation.claim.token,'--note','inspected']);assert.equal(noConfirmation.status,3);
    const cleared=repo.call(['clear-owner','--claim',invocation.claim.id,'--token',invocation.claim.token,'--operator-confirmed','--note','Operator inspected unsupported scope']);assert.equal(cleared.status,0,cleared.stderr);
    const record=JSON.parse(cleared.stdout);assert.equal(record.basis,'operator_confirmed');assert.match(JSON.stringify(record.details),/PID alone/);
    store=openRepositoryStore(repo.common);const replacement=await store.startInvocation({runId:run.id,worktreeId:worktree.id,owner});store.close();store=undefined;
    const stale=repo.call(['clear-owner','--claim',replacement.claim.id,'--token',invocation.claim.token,'--operator-confirmed','--note','stale token']);assert.equal(stale.status,3);assert.match(stale.stderr,/token/);
    store=openRepositoryStore(repo.common);assert.equal(store.inspectOwners()[0].id,replacement.claim.id);assert.equal(store.readClearances({claimId:invocation.claim.id}).length,1);
  }finally{store?.close();repo.dispose();}
});
test('boot/start mismatch is PID-reuse evidence and clearance never signals that PID',async()=>{
  const repo=await fixture(`export async function run(c){await c.progress('entry');}`);let store;
  try {
    store=openRepositoryStore(repo.common);const run=await store.createRun();const worktree=await store.registerWorktree({path:repo.path,registration:'fixture'});
    const invocation=await store.startInvocation({runId:run.id,worktreeId:worktree.id,owner:{host:hostname(),pid:process.pid,start:process.platform==='linux'?'linux:00000000-0000-0000-0000-000000000000:1':'darwin:{ sec = 1, usec = 0 } Thu Jan 1 00:00:01 1970:Thu Jan 1 00:00:01 1970'}});store.close();store=undefined;
    const inspected=JSON.parse(repo.call(['inspect-owner','--claim',invocation.claim.id]).stdout)[0];assert.equal(inspected.inspection.state,'not_live');assert.match(inspected.inspection.owner.limitation,/PID reuse/);
    const result=repo.call(['clear-owner','--claim',invocation.claim.id,'--token',invocation.claim.token,'--operator-confirmed','--note','Old identity differs']);assert.equal(result.status,0,result.stderr);process.kill(process.pid,0);
  }finally{store?.close();repo.dispose();}
});
test('failed ownership release rolls back successful finalization and keeps the exact claim blocked',async()=>{
  const repo=await fixture(`export async function run(c){await c.progress('finished work');}`);let db;
  try {
    db=new DatabaseSync(join(repo.common,'factory/history.sqlite'));db.exec("CREATE TRIGGER fixture_refuse_release BEFORE DELETE ON owner_claims BEGIN SELECT RAISE(ABORT,'fixture release denied'); END");db.close();db=undefined;
    const result=repo.invoke();assert.equal(result.status,1,result.stdout+result.stderr);const saved=JSON.parse(result.stdout);assert.equal(saved.cleanup,'unknown');
    const store=openRepositoryStore(repo.common);try{assert.equal(store.inspectOwners().length,1);assert.notEqual(store.readInvocation(saved.invocationId).outcome,'succeeded');}finally{store.close();}
  }finally{db?.close();repo.dispose();}
});

test('needs-input cancels capacity waiters without admitting or failing intentionally stopped work',async()=>{
  const repo=await fixture(`export async function run(c){for(const name of ['one','two','waiting']) void c.command(name,{argv:[process.execPath,'-e','setInterval(()=>{},1000)'],env:{}});await new Promise(resolve=>setTimeout(resolve,100));await c.needsInput('Choose','Stop capacity wait');}`);
  try{const result=repo.invoke(['--shutdown-grace-ms','100']);assert.equal(result.status,2,result.stdout+result.stderr);const saved=JSON.parse(result.stdout);const history=JSON.parse(repo.call(['history','--invocation',saved.invocationId]).stdout);assert.equal(history.attempts.filter(attempt=>attempt.operationKey==='waiting').length,0);assert.equal(history.accounting.occupiedCommands,0);assert.ok(history.attempts.filter(attempt=>['one','two'].includes(attempt.operationKey)).every(attempt=>attempt.outcome==='interrupted'));}
  finally{repo.dispose();}
});
test('recorder failure stops live peers and pending admission while retaining unknown ownership',async()=>{
  const repo=await fixture(`export async function run(c){void c.command('invalid',{argv:[process.execPath,'-e','process.stdout.write("committed prefix");setTimeout(()=>process.stdout.write(Buffer.from([255])),100);setInterval(()=>{},1000)'],env:{}});void c.command('peer',{argv:[process.execPath,'-e','setInterval(()=>{},1000)'],env:{}});void c.command('waiting',{argv:[process.execPath,'-e','console.log("must not launch")'],env:{}});}`);
  try{const result=repo.invoke(['--shutdown-grace-ms','100']);assert.equal(result.status,1,result.stdout+result.stderr);const saved=JSON.parse(result.stdout);assert.equal(saved.cleanup,'unknown');assert.match(result.stderr,/recording failed/);const history=JSON.parse(repo.call(['history','--invocation',saved.invocationId]).stdout);assert.equal(history.attempts.filter(attempt=>attempt.operationKey==='waiting').length,0);assert.ok(history.captures.some(capture=>capture.state==='partial'));assert.match(JSON.stringify(history.captures),/committed prefix/);assert.equal(JSON.parse(repo.call(['inspect-owner']).stdout).length,1);}
  finally{repo.dispose();}
});
test('failed summary save cannot publish success or release ownership',async()=>{
  const repo=await fixture(`export async function run(c){await c.progress('work received');}`);let db;
  try{db=new DatabaseSync(join(repo.common,'factory/history.sqlite'));db.exec("CREATE TRIGGER fixture_refuse_summary BEFORE UPDATE ON invocations WHEN json_extract(NEW.data,'$.stage')='finalized' BEGIN SELECT RAISE(ABORT,'fixture summary denied'); END");db.close();db=undefined;const result=repo.invoke();assert.equal(result.status,1,result.stdout+result.stderr);const saved=JSON.parse(result.stdout);assert.equal(saved.cleanup,'unknown');const store=openRepositoryStore(repo.common);try{const record=store.readInvocation(saved.invocationId);assert.equal(record.outcome,null);assert.equal(record.stage,'shutting_down');assert.equal(store.inspectOwners().length,1);}finally{store.close();}}
  finally{db?.close();repo.dispose();}
});
test('deadline bounds refuse invalid public configuration before creating an invocation',async()=>{
  const repo=await fixture(`export async function run(c){await c.progress('not entered');}`);
  try{for(const flags of [['--shutdown-grace-ms','0'],['--command-timeout-ms','NaN'],['--shutdown-grace-ms','300001'],['--command-timeout-ms','1.5']]){const result=repo.invoke(flags);assert.equal(result.status,3);assert.equal(result.stdout,'');assert.match(result.stderr,/duration/);}assert.deepEqual(JSON.parse(repo.call(['inspect-owner']).stdout),[]);}
  finally{repo.dispose();}
});

test('operator clearance permits fresh current-entry followup without resetting real fixture attempt allowance',async()=>{
  const repo=await fixture(`export async function run(c){await c.command('unsupported',{argv:[process.execPath,'-e','require("node:fs").writeFileSync("candidate.txt","keep candidate")'],env:{},childScope:'unknown'});}`);
  let store;
  try {
    store=openRepositoryStore(repo.common);const run=await store.createRun();const worktree=await store.registerWorktree({path:repo.path,registration:repo.git(['rev-parse','--path-format=absolute','--git-dir']).replace(/\n$/,'')});
    const seed=await store.startInvocation({runId:run.id,worktreeId:worktree.id,owner:{host:hostname(),pid:process.pid,start:null}});await store.activateInvocation(seed.id);
    const harness=fileURLToPath(new URL('./fixtures/fake-harness.mjs',import.meta.url));let prior;
    for(const intent of ['initial','code_correction']){
      const attempt=await store.admitAttempt({id:randomUUID(),invocationId:seed.id,operationKey:'implement',kind:'agent',intent,...(prior?{priorAttemptId:prior}:{})});
      const child=spawn(process.execPath,[harness,'--mode','permission-denied','--result',join(repo.common,'fixture-result.json')],{stdio:'ignore'});
      const closed=new Promise(resolve=>child.once('close',resolve));await store.markStarted({id:attempt.id,owner:{host:hostname(),pid:child.pid,start:null}});
      assert.equal(await closed,1);await store.settleAttempt({id:attempt.id,launch:'started',outcome:'failed',quiescent:true,evidence:'real fake-harness permission-denied exit 1; no children'});prior=attempt.id;
    }
    assert.equal(store.readAccounting(run.id).additionalUsed,1);await store.stopAdmissions(seed.id);await store.finalizeInvocation({id:seed.id,outcome:'failed',cleanup:'complete',claimId:seed.claim.id,token:seed.claim.token});store.close();store=undefined;
    const blocked=repo.invoke(['--run',run.id,'--shutdown-grace-ms','50']);assert.equal(blocked.status,1,blocked.stdout+blocked.stderr);const saved=JSON.parse(blocked.stdout);assert.equal(saved.cleanup,'unknown');
    const claim=JSON.parse(repo.call(['inspect-owner']).stdout)[0].claim;
    const cleared=repo.call(['clear-owner','--claim',claim.id,'--token',claim.token,'--operator-confirmed','--note','Operator verified unsupported scope stopped']);assert.equal(cleared.status,0,cleared.stderr);
    writeFileSync(join(saved.worktree,'.factory/workflows/run.ts'),`export async function run(c,inputs){await c.progress('fresh current entry:' + inputs.answer);}`);writeFileSync(repo.input,'{"answer":"explicit answer"}');
    const next=repo.call(['invoke','--workflow','.factory/workflows/run.ts','--input',repo.input,'--worktree',saved.worktreeId,'--run',run.id]);assert.equal(next.status,0,next.stdout+next.stderr);
    const fresh=JSON.parse(next.stdout);assert.notEqual(fresh.invocationId,saved.invocationId);assert.equal(fresh.runId,run.id);assert.equal(readFileSync(join(fresh.worktree,'candidate.txt'),'utf8'),'keep candidate');
    const history=JSON.parse(repo.call(['history','--invocation',fresh.invocationId]).stdout);assert.match(JSON.stringify(history.captures),/fresh current entry:explicit answer/);assert.equal(history.accounting.additionalUsed,1);
    store=openRepositoryStore(repo.common);assert.equal(store.readInvocation(saved.invocationId).cleanup,'unknown');assert.equal(store.readAccounting(run.id).additionalUsed,1);let cursor='0',starts=0;while(true){const page=store.readEvents({after:cursor});starts+=page.events.filter(event=>event.kind==='invocation.started').length;if(page.events.length<200)break;cursor=page.nextCursor;}assert.equal(starts,3);
  }finally{store?.close();repo.dispose();}
});

test('owner process loss leaves incomplete history and known-live scope blocks clearance until explicit operator cleanup',async()=>{
  const repo=await fixture(`export async function run(c){await c.command('orphan',{argv:[process.execPath,'-e','require("node:fs").writeFileSync("candidate.txt","preserved after owner loss");setInterval(()=>{},1000)'],env:{}});}`);
  let running,owned;
  try {
    running=start(repo,['--shutdown-grace-ms','100']);owned=await active(repo,'orphan');const path=openWorktree(repo,owned.claim);await waitFor(()=>existsSync(join(path,'candidate.txt')));
    running.child.kill('SIGKILL');const lost=await running.done;assert.equal(lost.signal,'SIGKILL');
    const inspection=JSON.parse(repo.call(['inspect-owner','--claim',owned.claim.id]).stdout)[0];assert.equal(inspection.inspection.owner.state,'not_live');assert.equal(inspection.inspection.state,'known_live');
    const refused=repo.call(['clear-owner','--claim',owned.claim.id,'--token',owned.claim.token,'--operator-confirmed','--note','must refuse remaining live scope']);assert.equal(refused.status,3);assert.match(refused.stderr,/known-live/);
    // Explicit fixture operator cleanup after positive identity inspection, never runtime restart cleanup.
    process.kill(-owned.attempt.owner.pid,'SIGTERM');await waitFor(()=>{try{process.kill(owned.attempt.owner.pid,0);return false;}catch(error){return error.code==='ESRCH';}});
    const cleared=repo.call(['clear-owner','--claim',owned.claim.id,'--token',owned.claim.token,'--operator-confirmed','--note','Operator stopped verified fixture scope']);assert.equal(cleared.status,0,cleared.stderr);
    const store=openRepositoryStore(repo.common);try{const prior=store.readInvocation(owned.claim.invocationId);assert.equal(prior.outcome,null);assert.notEqual(prior.stage,'finalized');assert.equal(store.readAttempt(owned.attempt.id).cleanupBasis,'operator_confirmed');assert.equal(store.readAccounting(prior.runId).occupiedCommands,0);}finally{store.close();}
    assert.equal(readFileSync(join(path,'candidate.txt'),'utf8'),'preserved after owner loss');
  }finally{running?.child.kill('SIGKILL');if(owned){try{process.kill(-owned.attempt.owner.pid,'SIGKILL');}catch{}}repo.dispose();}
});
test('manual workflow cancellation uses the same shutdown path and records its cause',async()=>{
  const repo=await fixture(`export async function run(c){void c.command('peer',{argv:[process.execPath,'-e','setInterval(()=>{},1000)'],env:{}});await new Promise(resolve=>setTimeout(resolve,100));await c.cancel('explicit workflow cancellation');}`);
  try{const result=repo.invoke(['--shutdown-grace-ms','100']);assert.equal(result.status,1,result.stdout+result.stderr);const saved=JSON.parse(result.stdout);assert.equal(saved.outcome,'cancelled');assert.equal(saved.cleanup,'complete');const history=JSON.parse(repo.call(['history','--invocation',saved.invocationId]).stdout);assert.equal(history.attempts.at(-1).outcome,'interrupted');assert.match(JSON.stringify(history.captures),/explicit workflow cancellation/);}
  finally{repo.dispose();}
});

test('failed spawn-identity save keeps live control until the actual process is stopped',async()=>{
  const repo=await fixture(`export async function run(c){await c.command('launch-record',{argv:[process.execPath,'-e','setTimeout(()=>require("node:fs").writeFileSync("continued-after-save-failure","unsafe continuation"),200);setInterval(()=>{},1000)'],env:{}});}`);let db;
  try{db=new DatabaseSync(join(repo.common,'factory/history.sqlite'));db.exec("CREATE TRIGGER fixture_refuse_spawn_identity BEFORE UPDATE ON attempts WHEN json_extract(NEW.data,'$.operationKey')='launch-record' AND json_extract(NEW.data,'$.launch')='started' BEGIN SELECT RAISE(ABORT,'fixture spawn identity denied'); END");db.close();db=undefined;const result=repo.invoke(['--shutdown-grace-ms','100']);assert.equal(result.status,1,result.stdout+result.stderr);const saved=JSON.parse(result.stdout);assert.equal(saved.cleanup,'unknown');await delay(300);assert.equal(existsSync(join(saved.worktree,'continued-after-save-failure')),false);const history=JSON.parse(repo.call(['history','--invocation',saved.invocationId]).stdout);assert.equal(history.attempts.at(-1).launch,'admitted');assert.equal(history.accounting.occupiedCommands,1);assert.equal(JSON.parse(repo.call(['inspect-owner']).stdout).length,1);}
  finally{db?.close();repo.dispose();}
});

test('review diagnostic boundary filters harmless configured fixture key',async()=>{
 const repo=await fixture(`export async function run(c){await c.command('missing',{argv:[process.env.REVIEW_API_KEY],env:{}});}`);
 try{const value='fixture-review-diagnostic-only';const result=spawnSync(process.execPath,repo.args([]),{encoding:'utf8',env:{...process.env,REVIEW_API_KEY:value},timeout:10000});assert.equal(result.status,1);assert.ok(!result.stdout.includes(value),'raw configured fixture key escaped returned diagnostic');}finally{repo.dispose();}
});
test('promise-only workflow remains foreground until explicit signal',async()=>{
 const repo=await fixture(`export async function run(c){await c.progress('entered current workflow');await new Promise(()=>{});}`);let child;
 try{child=spawn(process.execPath,repo.args(['--shutdown-grace-ms','100']),{stdio:['ignore','pipe','pipe']});const closed=new Promise(resolve=>child.once('close',resolve));await waitFor(()=>{const store=openRepositoryStore(repo.common);try{return store.inspectOwners().some(claim=>claim.invocationId && JSON.stringify(store.readHistory(claim.invocationId).captures).includes('entered current workflow'));}finally{store.close();}});await delay(100);assert.equal(child.exitCode,null,'promise-only workflow exited without final history');child.kill('SIGTERM');assert.equal(await closed,143);}finally{child?.kill('SIGKILL');repo.dispose();}
});

test('worktree checkout filter remains interruptible within grace',async()=>{
 const repo=await fixture(`export async function run(c){await c.progress('not entered after checkout interruption');}`);let child;
 try{
 const script=join(repo.common,'checkout-filter.mjs'),marker=join(repo.common,'checkout-filter-started');writeFileSync(script,`import{writeFileSync}from'node:fs';writeFileSync(${JSON.stringify(marker)},'started');process.stdin.resume();setTimeout(()=>process.stdout.write('filtered payload'),3000);`);
 writeFileSync(join(repo.path,'.gitattributes'),'payload.txt filter=review\n');writeFileSync(join(repo.path,'payload.txt'),'payload');repo.git(['add','.gitattributes','payload.txt']);repo.git(['commit','-m','Commit smudge fixture','--only','.gitattributes','payload.txt']);repo.git(['config','filter.review.smudge',JSON.stringify(process.execPath)+' '+JSON.stringify(script)]);repo.git(['config','filter.review.required','true']);
 child=spawn(process.execPath,repo.args(['--shutdown-grace-ms','100']),{stdio:['ignore','pipe','pipe']});let stdout='',stderr='';child.stdout.on('data',v=>stdout+=v);child.stderr.on('data',v=>stderr+=v);const done=new Promise(resolve=>child.once('close',status=>resolve({status,stdout,stderr})));
 const until=performance.now()+8000;while(!existsSync(marker)&&performance.now()<until)await delay(25);assert.ok(existsSync(marker));const before=performance.now();child.kill('SIGTERM');const result=await done;assert.equal(result.status,143,result.stdout+result.stderr);assert.ok(performance.now()-before<2000,'checkout smudge filter blocked signal processing');const saved=JSON.parse(result.stdout);const history=JSON.parse(repo.call(['history','--invocation',saved.invocationId]).stdout);assert.ok(history.attempts.every(attempt=>attempt.kind==='command'&&attempt.operationKey.startsWith('startup/git/')));assert.equal(history.attempts.at(-1).outcome,'interrupted');assert.ok(history.captures.every(capture=>capture.channel!=='report'));assert.doesNotMatch(JSON.stringify(history.captures),/\\"cause\\":\\"failure\\"/);
 }finally{child?.kill('SIGKILL');repo.dispose();}
});

test('common-dir manual recovery works without Git and filters operator notes',async()=>{
 const repo=await fixture(`export async function run(c){await c.progress('entry');}`);let store;
 try{store=openRepositoryStore(repo.common);const run=await store.createRun(),worktree=await store.registerWorktree({path:repo.path,registration:'fixture'});const invocation=await store.startInvocation({runId:run.id,worktreeId:worktree.id,owner:{host:hostname(),pid:process.pid,start:null}});store.close();store=undefined;
 const key='fixture-common-dir-note-only';const call=args=>spawnSync(process.execPath,[cli,...args,'--common-dir',repo.common,'--json'],{encoding:'utf8',env:{...process.env,PATH:'/fixture-no-git-available',REVIEW_API_KEY:key},timeout:10000});
 const inspection=call(['inspect-owner','--claim',invocation.claim.id]);assert.equal(inspection.status,0,inspection.stderr);assert.equal(JSON.parse(inspection.stdout)[0].claim.token,invocation.claim.token);
 const cleared=call(['clear-owner','--claim',invocation.claim.id,'--token',invocation.claim.token,'--operator-confirmed','--note','Operator removed '+key]);assert.equal(cleared.status,0,cleared.stderr);assert.ok(!cleared.stdout.includes(key));assert.match(cleared.stdout,/REDACTED/);
 store=openRepositoryStore(repo.common);assert.ok(!JSON.stringify(store.readClearances({claimId:invocation.claim.id})).includes(key));
 }finally{store?.close();repo.dispose();}
});
test('common-dir recovery rejects wrong or incompatible storage without creating history',async()=>{
 const repo=await fixture(`export async function run(c){}`);let db;
 try{const wrong=join(repo.path,'wrong-common');mkdirSync(wrong);const call=path=>spawnSync(process.execPath,[cli,'inspect-owner','--common-dir',path,'--json'],{encoding:'utf8',env:{...process.env,PATH:'/fixture-no-git-available'}});const missing=call(wrong);assert.equal(missing.status,3);assert.equal(existsSync(join(wrong,'factory')),false);
 db=new DatabaseSync(join(repo.common,'factory/history.sqlite'));db.exec('PRAGMA user_version=999');db.close();db=undefined;const incompatible=call(repo.common);assert.equal(incompatible.status,3);assert.match(incompatible.stderr,/incompatible schema/);
 writeFileSync(join(repo.common,'factory/history.sqlite'),'fixture corrupt essential store');const corrupt=call(repo.common);assert.equal(corrupt.status,3);assert.equal(readFileSync(join(repo.common,'factory/history.sqlite'),'utf8'),'fixture corrupt essential store');
 }finally{db?.close();repo.dispose();}
});
for(const mode of ['signal','timeout']) test(`read-only startup Git probe has live bounded ${mode} control before repository admission`,async()=>{
 const repo=await fixture(`export async function run(c){}`);let child;
 try{const bin=join(repo.path,'probe-bin');mkdirSync(bin);const marker=join(repo.common,'probe-started'),script=join(repo.common,'probe.mjs');writeFileSync(script,`import{writeFileSync}from'node:fs';writeFileSync(${JSON.stringify(marker)},'started');setInterval(()=>{},1000);`);writeFileSync(join(bin,'git'),'#!/bin/sh\nexec '+JSON.stringify(process.execPath)+' '+JSON.stringify(script)+'\n');chmodSync(join(bin,'git'),0o755);
 child=spawn(process.execPath,repo.args(['--shutdown-grace-ms','100',...(mode==='timeout'?['--command-timeout-ms','150']:[])]),{env:{...process.env,PATH:bin},stdio:['ignore','pipe','pipe']});let stdout='',stderr='';child.stdout.on('data',v=>stdout+=v);child.stderr.on('data',v=>stderr+=v);const done=new Promise(resolve=>child.once('close',resolve));if(mode==='signal'){await waitFor(()=>existsSync(marker));child.kill('SIGTERM');}const status=await done;assert.equal(status,mode==='signal'?143:3,stdout+stderr);assert.equal(stdout,'');assert.match(stderr,mode==='signal'?/interrupted/:/timed out/);const store=openRepositoryStore(repo.common);try{assert.deepEqual(store.inspectOwners(),[]);}finally{store.close();}
 }finally{child?.kill('SIGKILL');repo.dispose();}
});
