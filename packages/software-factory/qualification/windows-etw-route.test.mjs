import assert from 'node:assert/strict';
import test from 'node:test';
import { spawn, spawnSync } from 'node:child_process';
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, readdirSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { prepareUpload, validateObservation } from './windows-etw-route.mjs';
const receipt = [
 'ROUTE\t1\tbaseline-git', 'OWNED\t1', 'API\tstart\t0', 'API\treadyQuery\t0',
 'QUERY\treadyQuery\t1\t1\t1\t1\t1','MODE\treadyQuery\t1\t1\t0\tstop\t0',
 'API\tbeforeStopQuery\t0','QUERY\tbeforeStopQuery\t1\t1\t1\t1\t1',
 'MODE\tbeforeStopQuery\t1\t1\t0\tstop\t0','SESSION\t37748737\t5\t64',
 'ABI\t120\t280\t112\t448','API\tstop\t0','API\topen\t0','API\tprocess\t0','API\tclose\t0',
 'ROOT\t100\t10\t90\t20\t100', 'DIRECT\t101','HELD\troot\t1\t1\t1',
 'P\tS\t100\t50\t11\t10\tnode\t0','P\tS\t101\t100\t12\t30\tgit\t0',
 'I\t100\t15\tnode','I\t101\t35\tgit',
 'I\t101\t36\tgit-dll-1','I\t101\t37\tgit-dll-2','I\t101\t38\tgit-dll-3',
 'I\t101\t39\tgit-dll-4','I\t101\t40\tgit-dll-5',
 'P\tE\t101\t100\t12\t60\tgit\t0','P\tE\t100\t50\t11\t95\tnode\t0',
 'COUNTS\t20\t11','SCHEMA\tverified','STATS\t0\t0\t0',
 'HEADER\t110\t0\t0','FILE\t65536','CLEANUP\t1','COMPLETE',''].join('\n');
const result = { protocol:1,case:'baseline-git',rootPid:100,childPid:101,
 spawnObserved:true,exitObserved:true,closeObserved:true,stdoutClosed:true,stderrClosed:true,
 exitCode:0,closeCode:0,exitSignal:null,closeSignal:null,stdoutBytes:6,stderrBytes:0,
 stdoutCapturedBytes:6,stderrCapturedBytes:0,error:null,stop:null,
 spawnOptions:{detached:false,windowsHide:false,shell:false,stdio:['ignore','pipe','pipe']}};
test('complete independent event observation never grants transient file identity',()=>{
 const value=validateObservation(receipt,result,'baseline-git');
 assert.equal(value.observationComplete,true); assert.equal(value.graphMatched,true);
 assert.equal(value.productAdmission,false); assert.equal(value.helperAdmission,'refused');
 assert.equal(value.helperIdentity,'process-file-identity-unverified');
 assert.ok(value.refusals.includes('transient-process-identity-unverified'));
});


test('driver refuses ambiguous lifecycles, forged direct PID and image/console uncertainty',()=>{
 const mutations=[
  receipt.replace('P\tS\t101\t100\t12\t30\tgit\t0', 'P\tS\t101\t100\t12\t30\tgit\t0\nP\tS\t101\t100\t13\t31\tgit\t0'),
  receipt.replace('P\tE\t101\t100\t12', 'P\tE\t101\t100\t99'),
  receipt.replace('P\tE\t101\t100\t12\t60\tgit\t0\n',''),
  receipt.replace('P\tS\t101\t100','P\tS\t101\t999'),
  receipt.replace('I\t101\t35\tgit','I\t101\t35\tother'),
  receipt.replace('I\t101\t35\tgit','I\t101\t35\tC:\\foreign\\git.exe'),
  receipt.replace('COUNTS\t20\t11','P\tS\t202\t999\t88\t40\tconsole\t0\nP\tE\t202\t999\t88\t70\tconsole\t0\nCOUNTS\t20\t13'),
  receipt.replace('COUNTS\t20\t11','P\tS\t102\t101\t13\t40\tcmd\t0\nP\tE\t102\t101\t13\t50\tcmd\t0\nI\t102\t42\tcmd\nCOUNTS\t20\t14'),
 ];
 for(const changed of mutations) assert.equal(validateObservation(changed,result,'baseline-git').graphMatched,false);
 assert.equal(validateObservation(receipt,{...result,childPid:999},'baseline-git').graphMatched,false);
});
test('public complete status requires session, close, cap, header and cleanup evidence',()=>{
 for(const changed of [receipt.replace('API\tclose\t0','API\tclose\t5'),
 receipt.replace('STATS\t0\t0\t0','STATS\t1\t0\t0'),
 receipt.replace('HEADER\t110\t0\t0','HEADER\t0\t0\t0'),
 receipt.replace('FILE\t65536','FILE\t67108864'),receipt.replace('CLEANUP\t1','CLEANUP\t0'),
 receipt.replace('COUNTS\t20\t11','COUNTS\t100001\t11'), receipt.replace('SCHEMA\tverified\n',''),
 receipt.replace('QUERY\treadyQuery\t1\t1\t1\t1\t1','QUERY\treadyQuery\t1\t0\t1\t1\t1'),
 receipt+'x'.repeat(65537),receipt.replace('COMPLETE','COMPLETE\nCOMPLETE')]) {
  assert.equal(validateObservation(changed,result,'baseline-git').observationComplete,false);
 }
});

test('real launcher gates spawn and holds completion without delaying the helper', { timeout: 7000 }, async()=>{
 const work=mkdtempSync(join(tmpdir(),'etw-route-launch-'));
 const spec=join(work,'spec.json'), output=join(work,'result.json');
 writeFileSync(spec,JSON.stringify({case:'baseline-git',executable:process.execPath,
  args:['-e','process.stdout.write("route-ok")'],cwd:work,env:{...process.env}}));
 const child=spawn(process.execPath,[fileURLToPath(new URL('./windows-etw-route-launch.mjs',import.meta.url)),spec,output],
  {stdio:['pipe','pipe','pipe']});
 let transcript='', errors='';
 child.stdout.on('data',x=>{transcript+=x}); child.stderr.on('data',x=>{errors+=x});
 const until=async text=>{
  const end=Date.now()+3000;
  while(!transcript.includes(text)&&child.exitCode===null&&Date.now()<end) await new Promise(r=>setTimeout(r,10));
  assert.ok(transcript.includes(text),`missing ${text}, transcript ${transcript}, exit ${child.exitCode}`);
 };
 try {
  await until('READY\n'); assert.equal(transcript,'READY\n');
  child.stdin.write('R'); await until('DONE\t');
  const value=JSON.parse(readFileSync(output,'utf8'));
  assert.equal(value.stdoutBase64,Buffer.from('route-ok').toString('base64'));
  assert.equal(value.exitCode,0); assert.equal(value.closeObserved,true);
  assert.equal(child.exitCode,null); child.stdin.end('X');
  const exit=await new Promise(resolve=>child.once('close',(code,signal)=>resolve({code,signal})));
  assert.deepEqual(exit,{code:0,signal:null}); assert.equal(errors,'');
 }finally{if(child.exitCode===null)child.kill();rmSync(work,{recursive:true,force:true});}
});

test('artifact preparation recomputes private evidence and exports only fixed bounded fields',()=>{
 const evidence=mkdtempSync(join(tmpdir(),'etw-route-upload-'));
 const directory=join(evidence,'cases','baseline-git');mkdirSync(directory,{recursive:true});
 const complete={...result,stdoutBase64:Buffer.from('/repo\n').toString('base64'),stderrBase64:''};
 const save=()=>{
  writeFileSync(join(directory,'observation.private.tsv'),receipt);
  writeFileSync(join(directory,'launcher.private.json'),JSON.stringify(complete));
  writeFileSync(join(directory,'spec.private.json'),JSON.stringify({case:'baseline-git',cwd:'/repo',env:{SECRET:'never-upload'}}));
  writeFileSync(join(evidence,'qualification.json'),JSON.stringify({productAdmission:true,status:'FORGED',
   rawEtl:'removed-after-offline-parse',cleanupUncertain:false,cases:[{name:'baseline-git',secret:'C:\\ambient',diagnostics:{graph:[{role:'forged'}]}}]}));
 };
 try{
  save(); prepareUpload(evidence);
  const text=readFileSync(join(evidence,'upload','qualification.json'),'utf8');
  const output=JSON.parse(text);
  assert.equal(output.productAdmission,false);assert.equal(output.cases[0].outputVerified,true);
  assert.deepEqual(readdirSync(join(evidence,'upload')).sort(),['native.tsv','qualification.json']);
  assert.ok(output.cases[0].diagnostics.graph.some(x=>x.role==='root'));
  assert.equal(text.includes('forged'),false);
  for(const secret of ['SECRET','never-upload','C:\\ambient','FORGED','"childPid"','"env"']) assert.equal(text.includes(secret),false);
  writeFileSync(join(directory,'trace.etl'),'raw');assert.throws(()=>prepareUpload(evidence));
  rmSync(join(directory,'trace.etl'));save();
  writeFileSync(join(directory,'observation.private.tsv'),receipt+'C:\\ambient');assert.throws(()=>prepareUpload(evidence));
 }finally{rmSync(evidence,{recursive:true,force:true});}
});

test('a missing pinned Git import blocks comparison independently of main-image evidence',()=>{
 const missing=receipt.replace('I\t101\t40\tgit-dll-5\n','').replace('COUNTS\t20\t11','COUNTS\t20\t10');
 assert.equal(validateObservation(missing,result,'baseline-git').graphMatched,false);
});

test('native driver refuses an unsupported host with fixed output and no native skip',()=>{
 const directory=mkdtempSync(join(tmpdir(),'etw-route-host-'));
 try{
  const command=spawnSync(process.execPath,[fileURLToPath(new URL('./windows-etw-route-run.mjs',import.meta.url))],
   {encoding:'utf8',timeout:3000,env:{...process.env,GITHUB_ACTIONS:'true',WINDOWS_ETW_ROUTE_EVIDENCE:directory}});
  assert.equal(command.status,1);assert.equal(command.stdout,'');assert.equal(command.stderr,'ETW route observation incomplete\n');
  const report=JSON.parse(readFileSync(join(directory,'qualification.json'),'utf8'));
  assert.equal(report.productAdmission,false);assert.ok(['host','pin'].includes(report.failure.stage));
  assert.equal(report.cases.length,0);
 }finally{rmSync(directory,{recursive:true,force:true});}
});
test('output contracts check actual marker, bytes, stdout and fresh compiler output',async()=>{
 const {verifyOutput}=await import('./windows-etw-route.mjs');
 const exact={...result,stdoutBase64:Buffer.from('/repo\n').toString('base64'),stderrBase64:''};
 assert.equal(verifyOutput(exact,'baseline-git','/repo'),true);
 assert.equal(verifyOutput({...exact,stdoutBase64:Buffer.from('/foreign\n').toString('base64')},'baseline-git','/repo'),false);
 assert.equal(verifyOutput({...exact,stdoutBase64:'',stdoutCapturedBytes:0,stdoutBytes:0},'baseline-typescript','',Buffer.from('old')),false);
});

test('receipt grammar rejects noncanonical IDs and compound or misplaced failures',()=>{
 for(const invalid of [receipt.replace('ROOT\t100','ROOT\t0100'),
  receipt.replace('P\tS\t101\t100\t12','P\tS\t101\t100\t18446744073709551616'),
  receipt.replace('P\tE\t101\t100\t12','P\tE\t101\t100\t18446744073709551616'),
  receipt+'FAIL\tschema\n',receipt.replace('COMPLETE','FAIL\tschema\nFAIL\tclose')])
  assert.equal(validateObservation(invalid,result,'baseline-git').observationComplete,false);
});

test('closing the root control pipe before release refuses without creating a helper', {timeout:5000},async()=>{
 const work=mkdtempSync(join(tmpdir(),'etw-route-abort-'));
 const path=join(work,'spec.json'),output=join(work,'result.json');
 writeFileSync(path,JSON.stringify({case:'baseline-git',executable:process.execPath,args:['-e','process.exit(99)'],cwd:work,env:{}}));
 const root=spawn(process.execPath,[fileURLToPath(new URL('./windows-etw-route-launch.mjs',import.meta.url)),path,output],{stdio:['pipe','pipe','pipe']});
 try{
  const ready=await new Promise(resolve=>root.stdout.once('data',resolve));assert.equal(ready.toString(),'READY\n');
  const closed=new Promise(resolve=>root.once('close',resolve));root.stdin.end();assert.equal(await closed,2);
  const value=JSON.parse(readFileSync(output,'utf8'));assert.equal(value.childPid,null);assert.equal(value.spawnObserved,false);
 }finally{if(root.exitCode===null)root.kill();rmSync(work,{recursive:true,force:true});}
});

test('all observed modules must belong to the selected process lifetime and pin set',()=>{
 const late=receipt.replace('I\t101\t40\tgit-dll-5','I\t101\t61\tgit-dll-5');
 assert.equal(validateObservation(late,result,'baseline-git').graphMatched,false);
 const rootForeign=receipt.replace('COUNTS\t20\t11','I\t100\t40\tgit-dll-5\nCOUNTS\t20\t12');
 assert.equal(validateObservation(rootForeign,result,'baseline-git').graphMatched,false);
});

test('nested cmd requires both independent generations and stop requires a definite outcome',()=>{
 const cmdReceipt=receipt.replaceAll('baseline-git','candidate-nested-cmd').replaceAll('\tgit\t','\tcmd\t').replaceAll('\tgit\n','\tcmd\n')
  .replace(/I\t101\t(?:36|37|38|39|40)\tgit-dll-[1-5]\n/g,'')
  .replace('COUNTS\t20\t11','P\tS\t102\t101\t13\t40\tcmd\t0\nP\tE\t102\t101\t13\t50\tcmd\t0\nI\t102\t42\tcmd\nCOUNTS\t20\t9');
 const cmdResult={...result,case:'candidate-nested-cmd',stdoutBytes:0,stdoutCapturedBytes:0,
  spawnOptions:{detached:true,windowsHide:true,shell:false,stdio:['ignore','pipe','pipe']}};
 assert.equal(validateObservation(cmdReceipt,cmdResult,'candidate-nested-cmd').graphMatched,true);
 const stopReceipt=cmdReceipt.replaceAll('candidate-nested-cmd','candidate-deadline-control')
  .replaceAll('\tcmd\t','\tcontrol\t').replaceAll('\tcmd\n','\tcontrol\n').replace('P\tE\t101\t100\t12\t60\tcontrol\t0','P\tE\t101\t100\t12\t60\tcontrol\t1')
  .replace('P\tS\t102\t101\t13\t40\tcontrol\t0\nP\tE\t102\t101\t13\t50\tcontrol\t0\nI\t102\t42\tcontrol\n','')
  .replace('COUNTS\t20\t9','COUNTS\t20\t6');
 const stopped={...cmdResult,case:'candidate-deadline-control',stdoutBytes:15,stdoutCapturedBytes:15,
  exitCode:null,closeCode:null,exitSignal:'SIGTERM',closeSignal:'SIGTERM',stop:{reason:'deadline',killReturned:true,requestedAtMs:500}};
 assert.equal(validateObservation(stopReceipt,stopped,'candidate-deadline-control').graphMatched,true);
 assert.equal(validateObservation(stopReceipt,{...stopped,exitSignal:null,closeSignal:null},'candidate-deadline-control').graphMatched,false);
});


test('bounded diagnostics distinguish console graph roles without attribution',()=>{
 const extra=(parent)=>receipt.replace('COUNTS\t20\t11',`P\tS\t102\t${parent}\t13\t40\tconsole\t0\nP\tE\t102\t${parent}\t13\t50\tconsole\t0\nI\t102\t42\tconsole\nCOUNTS\t20\t14`);
 const root=validateObservation(extra(100),result,'baseline-git');
 const helper=validateObservation(extra(101),result,'baseline-git');
 const ambient=validateObservation(extra(999),result,'baseline-git');
 assert.deepEqual(root.diagnostics.graph.find(x=>x.processClass==='console'),{role:'other-descendant',processClass:'console',parentRole:'root',startPhase:'release-to-observed',endRelation:'before',count:1});
 assert.equal(helper.diagnostics.graph.find(x=>x.processClass==='console').parentRole,'direct');
 assert.equal(ambient.diagnostics.graph.find(x=>x.processClass==='console').role,'unassigned');
 for(const value of [root,helper,ambient]) { assert.equal(value.graphMatched,false); assert.equal(value.productAdmission,false); }
});


test('diagnostics isolate predicate subreasons and ambiguous identities',()=>{
 const check=(text,reason,role='direct')=>{const value=validateObservation(text,result,'baseline-git'); assert.ok(value.diagnostics.predicates.some(x=>x.role===role&&x.reason===reason),reason); assert.equal(value.graphMatched,false);};
 check(receipt.replace('I\t101\t35\tgit','I\t101\t35\tother'),'expected-image-zero');
 check(receipt.replace('I\t101\t35\tgit','I\t101\t35\tother'),'prohibited-image-class');
 check(receipt.replace('I\t101\t40\tgit-dll-5\n','').replace('COUNTS\t20\t11','COUNTS\t20\t10'),'missing-git-import');
 check(receipt.replace('P\tS\t101\t100\t12\t30','P\tS\t101\t100\t12\t19'),'nonroot-outside-bracket');
 check(receipt.replace('P\tE\t101\t100\t12\t60','P\tE\t101\t100\t12\t96'),'child-end-at-or-after-root');
 check(receipt.replace('P\tE\t101\t100\t12\t60\tgit\t0','P\tE\t101\t100\t12\t60\tgit\t2'),'direct-exit-mismatch');
 const duplicate=receipt.replace('P\tS\t101\t100\t12\t30\tgit\t0','P\tS\t101\t100\t12\t30\tgit\t0\nP\tS\t101\t100\t13\t31\tgit\t0').replace('COUNTS\t20\t11','COUNTS\t20\t12');
 const value=validateObservation(duplicate,result,'baseline-git');
 assert.ok(value.diagnostics.graph.some(x=>x.role==='unknown'));assert.ok(value.failures.includes('lifecycle-ambiguous'));
});

test('diagnostic public grammar rejects forged and sensitive fields',async()=>{
 const {safeObservation}=await import('./windows-etw-route.mjs');
 const valid=validateObservation(receipt,result,'baseline-git');
 for(const patch of [d=>d.graph[0].role='C:\\private',d=>d.graph[0].count=4097,d=>d.graph[0].count=1.5,d=>d.graph[0].secret='path',d=>d.graph.push({...d.graph[0]}),d=>d.secret='private']) {
  const forged=structuredClone(valid);patch(forged.diagnostics);assert.throws(()=>safeObservation(forged));
 }
});


test('ambiguous parent identity propagates uncertainty to descendants',()=>{
 const changed=receipt.replace('P\tS\t100\t50\t11\t10\tnode\t0','P\tS\t100\t50\t11\t10\tnode\t0\nP\tS\t100\t50\t77\t11\tnode\t0').replace('COUNTS\t20\t11','COUNTS\t20\t12');
 const value=validateObservation(changed,result,'baseline-git');
 assert.equal(value.diagnostics.graph.some(x=>x.role==='direct'),false);
 assert.ok(value.failures.includes('lifecycle-ambiguous'));
});

test('nested extra exit and image timing retain separate subreasons',()=>{
 const nested=receipt.replaceAll('baseline-git','candidate-nested-cmd').replaceAll('\tgit\t','\tcmd\t').replaceAll('\tgit\n','\tcmd\n')
  .replace(/I\t101\t(?:36|37|38|39|40)\tgit-dll-[1-5]\n/g,'')
  .replace('COUNTS\t20\t11','P\tS\t102\t101\t13\t40\tcmd\t0\nP\tE\t102\t101\t13\t50\tcmd\t2\nI\t102\t51\tcmd\nCOUNTS\t20\t9');
 const candidate={...result,case:'candidate-nested-cmd',stdoutBytes:0,stdoutCapturedBytes:0,spawnOptions:{detached:true,windowsHide:true,shell:false,stdio:['ignore','pipe','pipe']}};
 const value=validateObservation(nested,candidate,'candidate-nested-cmd');
 for(const reason of ['other-nonzero-exit','expected-load-outside-lifetime','image-outside-lifetime']) assert.ok(value.diagnostics.predicates.some(x=>x.role==='intended-nested'&&x.reason===reason),reason);
 assert.equal(value.diagnostics.predicates.some(x=>x.role==='intended-nested'&&x.reason==='invalid-lifecycle'),false);
 assert.ok(value.failures.includes('exit-status'));assert.equal(value.productAdmission,false);
});


test('ordinary extra helper and pre-release child have distinct closed categories',()=>{
 const extra=receipt.replace('COUNTS\t20\t11','P\tS\t102\t100\t13\t19\tcmd\t0\nP\tE\t102\t100\t13\t50\tcmd\t0\nI\t102\t21\tcmd\nCOUNTS\t20\t14');
 const value=validateObservation(extra,result,'baseline-git');
 assert.deepEqual(value.diagnostics.graph.find(x=>x.role==='other-descendant'),{role:'other-descendant',processClass:'expected',parentRole:'root',startPhase:'before-release',endRelation:'before',count:1});
 assert.ok(value.diagnostics.predicates.some(x=>x.role==='other-descendant'&&x.reason==='nonroot-outside-bracket'));
 assert.ok(value.failures.includes('unexpected-descendant'));assert.equal(value.graphMatched,false);
});

test('duplicate keys and image-only console retain unknown identity',()=>{
 const duplicate=receipt.replace('P\tS\t101\t100\t12','P\tS\t101\t100\t11').replace('P\tE\t101\t100\t12','P\tE\t101\t100\t11');
 const value=validateObservation(duplicate,result,'baseline-git');
 assert.ok(value.failures.includes('identity-key'));assert.ok(value.diagnostics.graph.some(x=>x.role==='unknown'));
 const imageOnly=receipt.replace('COUNTS\t20\t11','I\t202\t45\tconsole\nCOUNTS\t20\t12');
 assert.deepEqual(validateObservation(imageOnly,result,'baseline-git').diagnostics.console,[{membership:'unknown',evidence:'image',count:1}]);
});


test('multiple intended nested candidates remain unknown rather than merging roles',()=>{
 const nested=receipt.replaceAll('baseline-git','candidate-nested-cmd').replaceAll('\tgit\t','\tcmd\t').replaceAll('\tgit\n','\tcmd\n')
  .replace(/I\t101\t(?:36|37|38|39|40)\tgit-dll-[1-5]\n/g,'')
  .replace('COUNTS\t20\t11','P\tS\t102\t101\t13\t40\tcmd\t0\nP\tE\t102\t101\t13\t50\tcmd\t0\nI\t102\t42\tcmd\nP\tS\t103\t101\t14\t41\tcmd\t0\nP\tE\t103\t101\t14\t51\tcmd\t0\nI\t103\t43\tcmd\nCOUNTS\t20\t12');
 const candidate={...result,case:'candidate-nested-cmd',stdoutBytes:0,stdoutCapturedBytes:0,spawnOptions:{detached:true,windowsHide:true,shell:false,stdio:['ignore','pipe','pipe']}};
 const value=validateObservation(nested,candidate,'candidate-nested-cmd');
 assert.equal(value.diagnostics.graph.find(x=>x.role==='unknown').count,2);
 assert.ok(value.failures.includes('unexpected-descendant'));
});
