// Explicit native controls only. This suffix stays outside default Node test discovery.
import assert from 'node:assert/strict';
import { spawn, spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { mkdtempSync, readFileSync, writeFileSync, existsSync, unlinkSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { readBounded, validateObservation } from './windows-etw-route.mjs';
let foreign, work, passed = false;
try {
 assert.equal(process.platform,'win32');assert.equal(process.arch,'x64');
 assert.equal(process.version,'v24.22.1');assert.equal(process.env.GITHUB_ACTIONS,'true');
 const evidence=resolve(process.env.WINDOWS_ETW_ROUTE_EVIDENCE??'windows-etw-route-evidence');
 const original=join(evidence,'cases','baseline-git');
 const spec=JSON.parse(readBounded(join(original,'spec.private.json')));
 const text=readBounded(join(original,'observation.private.tsv'));
 const result=JSON.parse(readBounded(join(original,'launcher.private.json'),800000));
 assert.equal(validateObservation(text,result,'baseline-git').observationComplete,true);
 const digest=createHash('sha256').update(readFileSync(process.execPath)).digest('hex');
 assert.equal(spec.pins.find(pin=>pin.label==='node').sha256,digest);
 foreign=spawn(process.execPath,['-e','setTimeout(()=>{},120000)'],{windowsHide:true,stdio:'ignore'});
 await new Promise((resolve,reject)=>{foreign.once('spawn',resolve);foreign.once('error',reject);});
 const checked=validateObservation(text,{...result,childPid:foreign.pid},'baseline-git');
 assert.equal(checked.graphMatched,false);assert.ok(checked.failures.includes('direct-pid'));
 assert.doesNotThrow(()=>process.kill(foreign.pid,0));assert.equal(foreign.exitCode,null);
 work=mkdtempSync(join(tmpdir(),'factory-etw-route-native-'));
 const wrong=structuredClone(spec);wrong.pins.find(pin=>pin.label==='node').sha256='0'.repeat(64);
 const path=join(work,'spec.private.json');writeFileSync(path,JSON.stringify(wrong)+'\n',{flag:'wx'});
 const bridge=fileURLToPath(new URL('./windows-etw-route.ps1',import.meta.url));
 const powershell=join(process.env.SystemRoot,'System32','WindowsPowerShell','v1.0','powershell.exe');
 const invocation=spawnSync(powershell,['-NoProfile','-NonInteractive','-File',bridge,'-SpecPath',path,'-EvidenceDir',work],
  {encoding:'utf8',timeout:75000,maxBuffer:65536});
 assert.ifError(invocation.error);assert.equal(invocation.status,4);assert.equal(invocation.stdout,'');assert.equal(invocation.stderr,'');
 const failed=readBounded(join(work,'observation.private.tsv'));
 assert.ok(failed.includes('FAIL\tpin\n'));assert.ok(failed.includes('CLEANUP\t1\n'));
 assert.equal(failed.includes('COMPLETE'),false);assert.equal(failed.includes('HELD\tchild'),false);
 assert.doesNotThrow(()=>process.kill(foreign.pid,0));
 passed = true;
}catch{process.stderr.write('ETW route native controls failed\n');process.exitCode=1;}
finally{
 if(foreign&&foreign.exitCode===null&&foreign.signalCode===null){
  const closed=new Promise(resolve=>foreign.once('close',resolve));foreign.kill();
  await Promise.race([closed,new Promise(resolve=>{const timer=setTimeout(resolve,3000);timer.unref();})]);
  if(foreign.exitCode===null&&foreign.signalCode===null)process.exitCode=1;
 }
 if(work){
  try{const etl=join(work,'trace.etl');if(existsSync(etl))unlinkSync(etl);rmSync(work,{recursive:true,force:true});}
  catch{process.stderr.write('ETW route native cleanup failed\n');process.exitCode=1;}
 }
}

if(passed&&!process.exitCode)process.stdout.write('ETW_ROUTE_NATIVE_CONTROLS_OK\n');
