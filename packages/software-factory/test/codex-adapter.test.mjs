import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { cpSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';
import { createRepository } from './fixtures/repository.mjs';
import { initializeRepositoryStore, openRepositoryStore } from '../dist/store.js';
const root=fileURLToPath(new URL('../',import.meta.url));
async function fixture(source, mode='success') {
 const repo=createRepository(), common=join(repo.path,'.git');
 mkdirSync(join(repo.path,'.factory/workflows'),{recursive:true});
 writeFileSync(join(repo.path,'.factory/package.json'),' {"type":"module"}');
 writeFileSync(join(repo.path,'.factory/workflows/main.ts'),`import type {WorkflowContext} from '@local/software-factory';export async function run(context:WorkflowContext){${source}}`);
 writeFileSync(join(repo.path,'.factory/agents.json'),JSON.stringify({defaults:{harness:'codex',model:'gpt-6-luna',reasoning:'low',permissions:'read-only',skillDelivery:'instructions',prompt:mode}}));
 repo.git(['add','.factory']);repo.git(['commit','-m','Codex fixture','--only','.factory']);
 (await initializeRepositoryStore(common,{release:'fixture'})).close();
 const tc=join(common,'factory/toolchain');mkdirSync(tc);cpSync(join(root,'node_modules'),join(tc,'node_modules'),{recursive:true});
 writeFileSync(join(tc,'manifest.json'),JSON.stringify({schema:1,node:'24.22.1',typescript:'7.0.2',dependencies:{'@types/node':'24.19.2'}}));
 const executable=join(common,'codex-fixture');
 writeFileSync(executable,`#!${process.execPath}\n`+readFileSync(join(root,'test/fixtures/codex-harness.mjs'),'utf8'),{mode:0o700});
 const sha256=createHash('sha256').update(readFileSync(executable)).digest('hex');
 const host=join(common,'host.mjs'),input=join(common,'input.json');writeFileSync(input,'{}');
 writeFileSync(host,`import {invoke} from ${JSON.stringify(new URL('../dist/lifecycle.js',import.meta.url).href)};import {createCodexAdapter} from ${JSON.stringify(new URL('../dist/adapters/codex.js',import.meta.url).href)};const options=JSON.parse(process.argv[2]);const adapter=createCodexAdapter({executable:${JSON.stringify(executable)},sha256:${JSON.stringify(sha256)},environment:{PATH:process.env.PATH,HOME:process.env.HOME}});const result=await invoke({...options,adapters:{codex:adapter}});console.log(JSON.stringify(result));process.exit(result.exitCode);`);
 const invoke=(extra={})=>spawnSync(process.execPath,[host,JSON.stringify({repository:repo.path,workflow:'.factory/workflows/main.ts',input,newWorktree:true,shutdownGraceMs:100,...extra})],{encoding:'utf8',timeout:20000});
 const history=id=>{const s=openRepositoryStore(common);try{return {history:s.readHistory(id,{limit:100}),sessions:s.readSessions({invocationId:id})};}finally{s.close();}};
 return {...repo,common,invoke,history};
}
const agents=h=>h.attempts.filter(a=>a.kind==='agent');
test('Codex JSONL selects completed assistant payload after native turn completion',async()=>{
 const repo=await fixture(`return context.agent('report',{});`);
 try{const r=repo.invoke();assert.equal(r.status,0,r.stdout+r.stderr);const saved=JSON.parse(r.stdout),{history:h,sessions}=repo.history(saved.invocationId);assert.equal(agents(h).length,1);assert.equal(agents(h)[0].outcome,'succeeded');assert.equal(sessions.sessions.length,1);assert.match(sessions.sessions[0].nativeId,/^thread-/);assert.deepEqual(sessions.sessions[0].usage,{state:'unknown'});assert.deepEqual(sessions.sessions[0].loadedSkills,{state:'unknown'});assert.match(JSON.stringify(h.captures),/tool decoy/);const launch=JSON.parse(readFileSync(join(saved.worktree,'codex-launches.jsonl'),'utf8'));assert.equal(launch.args.at(-1),'-');assert.ok(launch.stdin.startsWith('Active task:\nsuccess\n'));assert.ok(!launch.args.some(arg=>arg.includes('Active task:')));}finally{repo.dispose();}
});

import {createCodexAdapter} from '../dist/adapters/codex.js';
const nativeExecutable=process.execPath;
const nativeSha=createHash('sha256').update(readFileSync(nativeExecutable)).digest('hex');
const adapter=()=>createCodexAdapter({executable:nativeExecutable,sha256:nativeSha,environment:{PATH:'/usr/bin:/bin',HOME:'/tmp/native-auth-not-read'}});
const inputs={harness:'codex',model:'gpt-6-luna',reasoning:'low',permissions:'read-only',skillDelivery:'instructions',requiredCapabilities:[],prompt:'test',skills:[]};
function stream(events){return events.map(v=>JSON.stringify(v)).join('\n')+'\n';}
const thread={type:'thread.started',thread_id:'native-a'},start={type:'turn.started'},end={type:'turn.completed'};
const message=text=>({type:'item.completed',item:{type:'agent_message',text}});
test('Codex final parser rejects missing terminal, malformed JSON and native errors without extracting tool JSON',()=>{
 const a=adapter();
 for(const events of [[thread,start,message('{"kind":"result","payload":1}')],[thread,start,{type:'item.completed',item:{type:'command_execution',aggregated_output:'{"kind":"result","payload":1}'}},end],[thread,start,message('malformed'),end],[thread,start,message('{"kind":"result","payload":1}'),{type:'turn.failed',error:{message:'permission denied'}}],[thread,start,message('{"kind":"result","payload":1}'),end,message('{"kind":"result","payload":2}')]]) assert.throws(()=>a.decodeFinal(stream(events)));
 assert.throws(()=>a.decodeFinal('not json'),/JSON/);
 assert.throws(()=>a.decodeFinal(stream([thread,start,{type:'error',message:'private-token-value'}])),error=>error.message.includes('Codex native failure')&&!error.message.includes('private-token-value'));
 assert.equal(a.decodeFinal(stream([thread,start,message('old'),message('{"kind":"result","payload":7}'),end])).payload,7);
});
test('Codex launch is fresh, pinned, explicit, noninteractive and preserves supplied instruction bytes',()=>{
 const a=adapter(), request={attemptId:'a',invocationId:'i',worktree:'/tmp/fixture',inputs:{...inputs,prompt:'literal `$(false)`',skills:[{name:'fixture',file:'SKILL.md',instructions:'bytes\nunchanged',resources:[{file:'guide.md',content:'resource bytes'}]}]},context:'saved findings'};
 const launch=a.start(request);
 assert.deepEqual(launch.argv.slice(0,6),[nativeExecutable,'--no-daemon','exec','--json','--color','never']);
 assert.equal(launch.argv[launch.argv.indexOf('--sandbox')+1],'read-only');assert.ok(launch.argv.includes('approval_policy="never"'));
 assert.ok(!launch.argv.some(v=>['resume','fork','--last','--full-auto','--ignore-user-config','--ignore-rules','--dangerously-bypass-hook-trust','--dangerously-bypass-approvals-and-sandbox'].includes(v)));
 assert.equal(launch.argv.at(-1),'-');
 assert.ok(!launch.argv.some(arg=>arg.includes(request.inputs.prompt)||arg.includes('resource bytes')||arg.includes('saved findings')));
 assert.ok(launch.stdin.startsWith(`Active task:\n${request.inputs.prompt}\n`));
 assert.match(launch.stdin,/Saved context:[\s\S]*saved findings/);
 assert.match(launch.stdin,/Supplied skill: fixture[\s\S]*bytes\nunchanged/);
 assert.match(launch.stdin,/Resource data: guide\.md[\s\S]*resource bytes/);
 assert.equal(a.canReuse(inputs,inputs),false);assert.throws(()=>a.start({...request,reuseNativeId:'native-a'}),/reuse/);
 assert.throws(()=>a.validateProfile({...inputs,skillDelivery:'native'}),/native skill/);
 assert.throws(()=>a.validateProfile({...inputs,model:'other'}),/unqualified/);
 const writable={...inputs,permissions:'workspace-write',requiredCapabilities:['workspace-write']};
 a.validateProfile(writable);
 const writableLaunch=a.start({...request,inputs:writable});
 assert.equal(writableLaunch.argv[writableLaunch.argv.indexOf('--sandbox')+1],'workspace-write');
 assert.throws(()=>a.validateProfile({...inputs,requiredCapabilities:['universal-child-control']}),/unsupported/);
 const bad=createCodexAdapter({executable:nativeExecutable,sha256:'0'.repeat(64),environment:{}});assert.throws(()=>bad.validateProfile(inputs),/SHA256 mismatch/);
});
test('Codex correction delivers the new task first and the supplied resource as data',()=>{
 const a=adapter();
 const previous=a.start({attemptId:'a',invocationId:'i',worktree:'/tmp/fixture',inputs:{...inputs,prompt:'Return draft DRAFT_A'},context:''});
 const correction='Return JSON with payload.marker equal to the exact content of guide.md';
 const launch=a.start({attemptId:'b',invocationId:'i',worktree:'/tmp/fixture',inputs:{...inputs,prompt:correction,skills:[{name:'literal',file:'SKILL.md',instructions:'Use supplied resource',resources:[{file:'guide.md',content:'RESOURCE_C7B2'}]}]},context:'Prior draft DRAFT_A failed validation'});
 assert.ok(previous.stdin.startsWith('Active task:\nReturn draft DRAFT_A\n'));
 assert.ok(launch.stdin.startsWith(`Active task:\n${correction}\n`));
 assert.match(launch.stdin,/Saved context:[\s\S]*Prior draft DRAFT_A failed validation/);
 assert.match(launch.stdin,/Resource data: guide\.md[\s\S]*RESOURCE_C7B2/);
 assert.ok(!launch.argv.some(arg=>arg.includes(correction)||arg.includes('RESOURCE_C7B2')));
});
test('Codex launch parsers isolate concurrent thread state and keep unproven telemetry unknown',()=>{
 const a=adapter(),request={attemptId:'a',invocationId:'i',worktree:'/tmp/fixture',inputs,context:''};
 const left=a.start(request),right=a.start({...request,attemptId:'b'});
 assert.equal(left.mapEvent(JSON.stringify(thread),'stdout').nativeId,'native-a');
 assert.equal(right.mapEvent(JSON.stringify({...thread,thread_id:'native-b'}),'stdout').nativeId,'native-b');
 left.mapEvent(JSON.stringify(start),'stdout');right.mapEvent(JSON.stringify(start),'stdout');
 assert.deepEqual(left.mapEvent(JSON.stringify({...end,usage:{input_tokens:11,output_tokens:4}}),'stdout'),{nativeId:'native-a',parentNativeId:null,lifecycle:'succeeded'});
 assert.equal(right.mapEvent(JSON.stringify(end),'stdout').nativeId,'native-b');
 assert.throws(()=>left.mapEvent(JSON.stringify(end),'stdout'),/after terminal/);
});

test('Codex per-launch parser rejects exact native sandbox denial on stderr',()=>{
 const launch=adapter().start({attemptId:'a',invocationId:'i',worktree:'/tmp/fixture',inputs,context:''});
 assert.deepEqual(launch.eventChannels,['stdout','stderr']);
 assert.equal(launch.mapEvent('native informational warning','stderr'),undefined);
 assert.throws(()=>launch.mapEvent('2026-10-22T06:20:31Z WARN codex_sandboxing::violation: recorded sandbox violation: resource=filesystem backend=seatbelt reason=operation_not_permitted path=unknown','stderr'),/native permission denial/);
 assert.throws(()=>launch.mapEvent('WARN codex_sandboxing::violation: recorded sandbox violation: private-token-value','stderr'),error=>error.message.includes('native permission denial')&&!error.message.includes('private-token-value'));
});

for(const mode of ['malformed','native-error','denied']) test(`Codex ${mode} preserves raw failure without a question or retry`,async()=>{
 const repo=await fixture(`return context.agent('report',{});`,mode);
 try{const r=repo.invoke();assert.equal(r.status,1,r.stdout+r.stderr);const saved=JSON.parse(r.stdout),{history:h}=repo.history(saved.invocationId);assert.doesNotMatch(saved.diagnostic??'',/requires per-launch/);assert.equal(agents(h).length,1);assert.equal(agents(h)[0].outcome,'failed');assert.equal(h.captures.filter(c=>c.channel==='request').length,0);const evidence=JSON.stringify(h.captures);assert.match(evidence,mode==='denied'?/recorded sandbox violation/:mode==='native-error'?/native provider failure/:/malformed assistant/);assert.equal(readFileSync(join(saved.worktree,'codex-launches.jsonl'),'utf8').trim().split('\n').length,1);}finally{repo.dispose();}
});
test('Codex later calls and unsupported reuse correction each launch one fresh process',async()=>{
 const repo=await fixture(`const first=await context.agent('write',{prompt:'malformed'});const second=await context.agent('write',{prompt:'malformed',intent:'format_correction',priorAttemptId:first.attemptId,reuse:true,context:'correct invalid output'});await context.agent('review',{purpose:'review',prompt:'success'});return second;`);
 try{const r=repo.invoke();assert.equal(r.status,0,r.stdout+r.stderr);const saved=JSON.parse(r.stdout),{history:h,sessions}=repo.history(saved.invocationId);assert.equal(agents(h).length,3);assert.deepEqual(agents(h).map(a=>a.agent.sessionMode),['fresh','fresh','fresh']);assert.equal(h.accounting.additionalUsed,1);assert.equal(new Set(sessions.sessions.map(s=>s.nativeId)).size,3);assert.deepEqual(agents(h).map(a=>a.outcome),['failed','succeeded','succeeded']);}finally{repo.dispose();}
});
test('Codex concurrent workflow calls preserve separate terminal session identities',async()=>{
 const repo=await fixture(`return Promise.all([context.agent('a',{}),context.agent('b',{})]);`);
 try{const r=repo.invoke();assert.equal(r.status,0,r.stdout+r.stderr);const saved=JSON.parse(r.stdout),{sessions}=repo.history(saved.invocationId);assert.equal(sessions.sessions.length,2);assert.equal(new Set(sessions.sessions.map(s=>s.nativeId)).size,2);assert.ok(sessions.sessions.every(s=>s.lifecycle==='succeeded'));}finally{repo.dispose();}
});
test('Codex stop delegates to owned group and runner proves process absence',async()=>{
 const repo=await fixture(`return context.agent('hold',{prompt:'hold',timeoutMs:300});`);
 try{const r=repo.invoke();assert.equal(r.status,1,r.stdout+r.stderr);const saved=JSON.parse(r.stdout),{history:h}=repo.history(saved.invocationId),a=agents(h)[0];assert.match(saved.diagnostic,/timeout/);assert.equal(a.outcome,'failed');assert.equal(a.quiescent,true);assert.equal(h.accounting.occupiedAgents,0);assert.throws(()=>process.kill(-a.owner.pid,0),e=>e.code==='ESRCH');}finally{repo.dispose();}
});

test('Codex native failed turn maps to its own failed session without invented usage',()=>{
 const launch=adapter().start({attemptId:'a',invocationId:'i',worktree:'/tmp/fixture',inputs,context:''});
 launch.mapEvent(JSON.stringify(thread),'stdout');launch.mapEvent(JSON.stringify(start),'stdout');
 assert.deepEqual(launch.mapEvent(JSON.stringify({type:'turn.failed',error:{message:'native provider failure'}}),'stdout'),{nativeId:'native-a',parentNativeId:null,lifecycle:'failed'});
});

test('Codex native error cannot later turn a failed session into success',()=>{
 const launch=adapter().start({attemptId:'a',invocationId:'i',worktree:'/tmp/fixture',inputs,context:''});
 launch.mapEvent(JSON.stringify(thread),'stdout');launch.mapEvent(JSON.stringify(start),'stdout');
 assert.equal(launch.mapEvent(JSON.stringify({type:'error',message:'native provider failure'}),'stdout').lifecycle,'failed');
 assert.throws(()=>launch.mapEvent(JSON.stringify(end),'stdout'),/native error/);
});

test('Codex genuine assistant question is saved without treating native denial as interaction',async()=>{
 const repo=await fixture(`return context.agent('question',{prompt:'question'});`);
 try{const r=repo.invoke();assert.equal(r.status,2,r.stdout+r.stderr);const saved=JSON.parse(r.stdout),{history:h}=repo.history(saved.invocationId);assert.equal(agents(h)[0].outcome,'needs_input');assert.equal(h.captures.filter(c=>c.channel==='request').length,1);assert.equal(h.accounting.additionalUsed,0);}finally{repo.dispose();}
});


test('Codex malformed native JSON stays in raw capture without entering workflow diagnostics',async()=>{
 const repo=await fixture(`const result=await context.agent('report',{});if(result.status==='invalid')await context.progress(result.diagnostic);return result;`,'malformed');
 try{
  const result=repo.invoke();assert.equal(result.status,1,result.stdout+result.stderr);
  const saved=JSON.parse(result.stdout),{history}=repo.history(saved.invocationId);
  const report=history.captures.find(capture=>capture.channel==='event');
  assert.ok(report,'workflow-visible diagnostic capture is required');
  assert.doesNotMatch(report.chunks.map(chunk=>chunk.text).join(''),/malformed assistant/);
  assert.match(JSON.stringify(history.captures.filter(capture=>capture.attemptId===agents(history)[0].id)),/malformed assistant/);
  assert.equal(agents(history).length,1);
 }finally{repo.dispose();}
});

test('Codex parser errors do not echo malformed assistant or JSONL bytes',()=>{
 const native=adapter();
 for(const [run,expected] of [
  [()=>native.decodeFinal('PRIVATE_NATIVE_JSONL_BYTES'),'invalid Codex JSONL record'],
  [()=>native.decodeFinal(stream([thread,start,message('PRIVATE_FINAL_BYTES'),end])),'invalid Codex final assistant JSON'],
  [()=>native.start({attemptId:'a',invocationId:'i',worktree:'/tmp/fixture',inputs,context:''}).mapEvent('PRIVATE_NATIVE_JSONL_BYTES','stdout'),'invalid Codex JSONL record'],
 ]) assert.throws(run,error=>error instanceof Error&&error.message===expected);
});
