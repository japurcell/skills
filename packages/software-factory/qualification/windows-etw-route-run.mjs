// Explicit disposable native experiment. No product imports, downloads, global tracker or PID cleanup.
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { existsSync, lstatSync, mkdirSync, readFileSync, readdirSync, writeFileSync, unlinkSync } from 'node:fs';
import { basename, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { readBounded, routeCases, validateObservation, verifyOutput } from './windows-etw-route.mjs';

const sourceRoot = fileURLToPath(new URL('.', import.meta.url));
const sha256 = path => {
 const stat=lstatSync(path);assert.ok(stat.isFile()&&!stat.isSymbolicLink()&&stat.size<=150000000);
 return createHash('sha256').update(readFileSync(path)).digest('hex');
};
const known = {
 git: { archive: 'MinGit-2.54.0-64-bit.zip', sha256: '04f937e1f0918b17b9be6f2294cb2bb66e96e1d9832d1c298e2de088a1d0e668',
  executable: 'cab4c4eea1d869cf9f7be73868dc9a90ad2df1b1b673e5f8c8714a576c25ea96',
  dlls: {
   'libiconv-2.dll':'7a282a854e01be726c6cccfe46f548c716aa45b3014818468253aaa4efbcd067',
   'libintl-8.dll':'0537c3dd2378218508ebe3cc416d72a99ee2d24ae1c5525e23458f32544ef861',
   'libpcre2-8-0.dll':'c135a87ed0f11eae8ffc4cb469671ff0b3f5d71fab5fb024e9b1e7241ca25b52',
   'libwinpthread-1.dll':'851f61482ad5b6aac7c6abc54bbe31d24f89e0ca683a75fcec2d47f86b2d2242',
   'zlib1.dll':'93e9243a44c29200eeacaf9658efe2558581770e4b11ca4b500e18e424a6e3b5' } },
 typescript: { archive: 'typescript-win32-x64-7.0.2.tgz', sha256: '61fc4e141d2bc687db580e71bbfa63b9c209f0310645d82ca1b457eb3a24fd19',
  executable: 'f9ecfbdc93753d2c972d66a8d0d75f5bd737fd4a5f88b422d9091ea282bcb2c7' }
};
function packageCheck(archive, contract) {
 assert.equal(archive.archive,contract.archive); assert.equal(archive.sha256,contract.sha256);
 assert.equal(sha256(join(archive.root,contract.archive)),contract.sha256);
 assert.ok(archive.files && Object.keys(archive.files).length <= 1024);
 for(const [member,hash] of Object.entries(archive.files)) {
  assert.ok(!member.startsWith('/') && !member.includes('\\') && !member.split('/').includes('..') && !member.includes(':'));
  const path=join(archive.root,...member.split('/')); const stat=lstatSync(path);
  assert.ok(stat.isFile()&&!stat.isSymbolicLink()&&stat.size<=150000000);
  assert.equal(sha256(path),hash);
 }
}
function environment(home, windows) {
 const temporary=join(home,'temp');
 for(const path of [temporary,join(home,'AppData','Roaming'),join(home,'AppData','Local')]) mkdirSync(path,{recursive:true});
 const config=join(home,'global.gitconfig');writeFileSync(config,'',{flag:'wx'});
 return { SystemRoot:windows,WINDIR:windows,ComSpec:join(windows,'System32','cmd.exe'),
  PATH:`${join(windows,'System32')};${windows}`,PATHEXT:'.COM;.EXE;.BAT;.CMD',
  TEMP:temporary,TMP:temporary,HOME:home,USERPROFILE:home,HOMEDRIVE:home.slice(0,2),HOMEPATH:home.slice(2),
  APPDATA:join(home,'AppData','Roaming'),LOCALAPPDATA:join(home,'AppData','Local'),GIT_CONFIG_GLOBAL:config,
  GIT_TRACE2:'0',GIT_TRACE2_EVENT:'0',GIT_TRACE2_PERF:'0',GIT_TERMINAL_PROMPT:'0',GITHUB_ACTIONS:'true' };
}
export async function runNative() {
 const evidence=resolve(process.env.WINDOWS_ETW_ROUTE_EVIDENCE??'windows-etw-route-evidence');
 const report={scope:'T17-Windows-ETW-representative-observation',status:'inconclusive',productAdmission:false,
  cleanupUncertain:false,rawEtl:'pending',cases:[],failure:null};
 let stage='host';
 mkdirSync(evidence,{recursive:true});
 const save=()=>writeFileSync(join(evidence,'qualification.json'),JSON.stringify(report,null,2)+'\n');
 try {
  assert.equal(process.platform,'win32');assert.equal(process.arch,'x64');
  assert.equal(process.version,'v24.22.1');assert.equal(process.env.GITHUB_ACTIONS,'true');
  stage='pin';
  const manifest=JSON.parse(readBounded(join(sourceRoot,'runtime-manifest.json')));
  const bootstrap=JSON.parse(readBounded(join(evidence,'bootstrap.json')));
  assert.equal(bootstrap.status,'passed');assert.equal(bootstrap.native?.node,manifest.node);
  assert.equal(bootstrap.sha256,manifest.artifacts['win32-x64'].sha256);
  const archive=join(bootstrap.directory,basename(new URL(bootstrap.url).pathname));
  assert.equal(sha256(archive),manifest.artifacts['win32-x64'].sha256);
  const member=spawnSync('tar',['-xOf',archive,'node-v24.22.1-win-x64/node.exe'],
   {encoding:null,timeout:120000,maxBuffer:150000000});
  assert.ifError(member.error);assert.equal(member.status,0);assert.ok(member.stdout.length);
  const digest=createHash('sha256').update(member.stdout).digest('hex');
  const node=join(bootstrap.directory,'node-v24.22.1-win-x64','node.exe');assert.equal(sha256(node),digest);
  assert.equal(sha256(process.execPath),digest);
  const artifacts=JSON.parse(readBounded(join(evidence,'artifacts.json'),1048576));
  assert.equal(artifacts.status,'prepared-not-natively-qualified');
  for(const name of ['git','typescript']) packageCheck(artifacts.archives[name],known[name]);
  const git=join(artifacts.archives.git.root,'mingw64','bin','git.exe');assert.equal(sha256(git),known.git.executable);
  const compiler=join(artifacts.archives.typescript.root,'package','lib','tsc.exe');assert.equal(sha256(compiler),known.typescript.executable);
  const windows=process.env.SystemRoot??process.env.WINDIR;assert.match(windows,/^[A-Za-z]:\\/);
  const cmd=join(windows,'System32','cmd.exe'),console=join(windows,'System32','conhost.exe');
  const powershell=join(windows,'System32','WindowsPowerShell','v1.0','powershell.exe');
  assert.ok(existsSync(cmd)&&existsSync(console)&&existsSync(powershell));
  stage='fixture';
  const controlDir=join(evidence,'control');mkdirSync(controlDir);
  const control=join(controlDir,'windows-startup-control.exe');
  const built=spawnSync(powershell,['-NoProfile','-NonInteractive','-File',join(sourceRoot,'windows-startup-control-build.ps1'),
   '-SourcePath',join(sourceRoot,'windows-startup-control.cs'),'-OutputPath',control],
   {cwd:controlDir,encoding:'utf8',timeout:75000,maxBuffer:65536});
  assert.ifError(built.error);assert.equal(built.status,0);assert.equal(built.stdout,'control-built');
  const systemPins=[{label:'node',path:node,sha256:digest},{label:'cmd',path:cmd,sha256:sha256(cmd)},
   {label:'console',path:console,sha256:sha256(console)}];
  for(const name of routeCases) {
   stage='fixture';const directory=join(evidence,'cases',name);mkdirSync(directory,{recursive:true});
   assert.equal(readdirSync(directory).length,0);
   const work=join(directory,'work');mkdirSync(work); const env=environment(join(work,'home'),windows);
   let executable,args;
   const pins=[...systemPins];
   if(name.endsWith('git')) {
    executable=git;args=['--no-pager','--no-lazy-fetch','rev-parse','--show-toplevel'];
    const initialized=spawnSync(git,['init','--initial-branch=main'],{cwd:work,env,encoding:'utf8',timeout:15000,maxBuffer:262144});
    assert.ifError(initialized.error);assert.equal(initialized.status,0);
    pins.push({label:'git',path:git,sha256:known.git.executable});
    let index=0;for(const [dll,hash]of Object.entries(known.git.dlls))
     pins.push({label:`git-dll-${++index}`,path:join(artifacts.archives.git.root,'mingw64','bin',dll),sha256:hash});
   }else if(name.endsWith('typescript')) {
    executable=compiler;const input=join(work,'input.ts');writeFileSync(input,'const result: number = 42;\nexport { result };\n',{flag:'wx'});
    const config=join(work,'tsconfig.generated.json');writeFileSync(config,JSON.stringify({files:[input],compilerOptions:{
     target:'ES2020',module:'ESNext',strict:true,types:[],lib:['ES2020'],outDir:join(work,'out'),noEmitOnError:true}}),{flag:'wx'});
    assert.equal(existsSync(join(work,'out','input.js')),false);args=['-p',config];
    pins.push({label:'typescript',path:compiler,sha256:known.typescript.executable});
   }else if(name.endsWith('cmd')) {executable=cmd;args=['/d','/c',cmd,'/d','/c','exit','0'];}
   else {executable=control;args=[name.includes('deadline')?'deadline':'output-limit'];pins.push({label:'control',path:control,sha256:sha256(control)});}
   const spec={case:name,node,launcher:join(sourceRoot,'windows-etw-route-launch.mjs'),executable,args,cwd:work,env,pins};
   const specPath=join(directory,'spec.private.json');writeFileSync(specPath,JSON.stringify(spec)+'\n',{flag:'wx'});
   const item={name,observationComplete:false};report.cases.push(item);save();
   const etl=join(directory,'trace.etl');
   try {
    stage='bridge';
    const invocation=spawnSync(powershell,['-NoProfile','-NonInteractive','-File',join(sourceRoot,'windows-etw-route.ps1'),
     '-SpecPath',specPath,'-EvidenceDir',directory],{cwd:directory,encoding:'utf8',timeout:75000,maxBuffer:65536});
    if(invocation.error) {report.cleanupUncertain=true;throw new Error('bridge');}
    const text=readBounded(join(directory,'observation.private.tsv'));
    if(!text.includes('CLEANUP\t1\n')||invocation.stdout||invocation.stderr||text.includes('FAIL\ttimeout\n')||
      text.includes('OWNED\t1\n')&&!text.includes('API\tstop\t0\n'))
     {report.cleanupUncertain=true;throw new Error('cleanup');}
    stage='receipt';
    const resultPath=join(directory,'launcher.private.json');
    const result=existsSync(resultPath)?JSON.parse(readBounded(resultPath,800000)):null;
    const checked=validateObservation(text,result,name);
    if(result) {
     const emittedPath=join(work,'out','input.js');
     const emitted=name.endsWith('typescript')&&existsSync(emittedPath)?Buffer.from(readBounded(emittedPath,262144)):undefined;
     checked.outputVerified=verifyOutput(result,name,work,emitted);
     if(name.endsWith('typescript')&&(!existsSync(join(work,'out'))||readdirSync(join(work,'out')).length!==1)) checked.outputVerified=false;
     if(!checked.outputVerified) checked.graphMatched=false;
     if(result.stop?.reason==='guard'||result.error==='output-timeout') report.cleanupUncertain=true;
    }
    Object.assign(item,checked);
    if(invocation.status!==0&&!text.includes('FAIL\t')) throw new Error('bridge');
    if(!checked.observationComplete) report.failure??={stage:'receipt',code:'inconclusive'};
   }finally{
    try{if(existsSync(etl))unlinkSync(etl);}catch{report.cleanupUncertain=true;}
    save();
   }
   assert.equal(sha256(node),digest);
   for(const which of ['git','typescript']) packageCheck(artifacts.archives[which],known[which]);
   if(report.cleanupUncertain) break;
  }
  if(report.cases.length===7&&report.cases.every(item=>item.observationComplete))report.status='observation-complete';
  else if(report.cases.some(item=>item.observationComplete))report.status='route-refused';
 }catch{report.failure??={stage,code:'operation-failed'};}
 finally {
  for(const name of routeCases) {
   const etl=join(evidence,'cases',name,'trace.etl');
   try{if(existsSync(etl))unlinkSync(etl);}catch{report.cleanupUncertain=true;}
  }
  report.rawEtl=report.cleanupUncertain?'cleanup-uncertain':'removed-after-offline-parse';save();
 }
 if(report.status!=='observation-complete'||report.cleanupUncertain){process.stderr.write('ETW route observation incomplete\n');process.exitCode=1;}
 return report;
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)) {
 runNative().catch(()=>{process.stderr.write('ETW route driver failed\n');process.exitCode=1;});
}
