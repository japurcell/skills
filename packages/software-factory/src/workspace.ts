import { createHash } from 'node:crypto';
import { spawn } from 'node:child_process';
import { closeSync, existsSync, mkdirSync, mkdtempSync, openSync, realpathSync, rmSync, lstatSync, fstatSync, readSync, constants } from 'node:fs';
import { join, resolve } from 'node:path';
import { tmpdir } from 'node:os';
import { LiveProcessScope } from './native/process.js';

export class StartupInterrupted extends Error {
  constructor(readonly exitCode:number, message:string) {super(message);}
}
type Launch = (argv:string[],cwd:string,env:Record<string,string>)=>Promise<string>;
export type GitExecutor = (repository:string,args:string[])=>Promise<string>;
/** Before repository identity/store admission, only bounded read-only probes use this live owner. */
export class StartupGitControl {
  private readonly active = new Set<LiveProcessScope>();
  private signal: 'SIGINT'|'SIGTERM'|undefined;
  constructor(readonly grace=30000,readonly timeout=30000) {}
  get stopSignal(){return this.signal;}
  stop(signal:'SIGINT'|'SIGTERM') { this.signal ??= signal; for(const scope of this.active) void scope.stop(this.grace); }
  readonly launch: Launch = async(argv,cwd,env)=>{
    if(this.signal) throw new StartupInterrupted(this.signal==='SIGINT'?130:143,'startup interrupted before Git probe');
    const child=spawn(argv[0]!,argv.slice(1),{cwd,env,detached:process.platform!=='win32',stdio:['ignore','pipe','pipe']});
    const scope=new LiveProcessScope(child,false);this.active.add(scope);
    let timedOut=false,bytes=0;const stdout:Buffer[]=[],stderr:Buffer[]=[];
    const collect=async(source:AsyncIterable<Buffer>,parts:Buffer[])=>{for await(const chunk of source){bytes+=chunk.length;if(bytes>1048576)throw new Error('startup Git probe output exceeds bounded limit');parts.push(chunk);}};
    const capture=async(source:AsyncIterable<Buffer>,parts:Buffer[])=>{try{await collect(source,parts);}catch(error){void scope.stop(this.grace);throw error;}};
    const streams=Promise.allSettled([capture(child.stdout!,stdout),capture(child.stderr!,stderr)]);
    const timer=setTimeout(()=>{timedOut=true;void scope.stop(this.grace);},this.timeout);
    try {
      const result=await scope.result(this.grace);const output=await streams;
      if(this.signal) throw new StartupInterrupted(result.quiescent?(this.signal==='SIGINT'?130:143):1,result.quiescent?'startup Git probe interrupted':'startup Git probe cleanup unknown; manual inspection required');
      if(timedOut)throw new Error('startup Git probe timed out; no automatic retry');
      const rejected=output.find(item=>item.status==='rejected');if(rejected?.status==='rejected')throw rejected.reason;
      if(result.error)throw result.error;
      if(!result.quiescent)throw new Error('startup Git probe cleanup unknown; manual inspection required');
      if(result.code!==0)throw new Error(`Git probe failed (exit ${result.code}): ${Buffer.concat(stderr).toString('utf8')}`);
      return Buffer.concat(stdout).toString('utf8');
    }finally{clearTimeout(timer);await scope.stop(this.grace);this.active.delete(scope);}
  };
}
/** Temporary regular config/hook paths remain owned until the live Git scope settles. */
export async function git(repository:string,args:string[],launch?:Launch) {
  const temporary=mkdtempSync(join(tmpdir(),'factory-git-config-'));
  const control=launch?undefined:new StartupGitControl();
  const onInt=()=>control?.stop('SIGINT'),onTerm=()=>control?.stop('SIGTERM');
  if(control){process.on('SIGINT',onInt);process.on('SIGTERM',onTerm);}
  try {
    const configuration=join(temporary,'config');closeSync(openSync(configuration,'wx',0o600));
    const hooks=join(temporary,'hooks');mkdirSync(hooks);
    const env={PATH:process.env.PATH??'',...(process.env['SystemRoot']?{SystemRoot:process.env['SystemRoot']}:{}),GIT_CONFIG_NOSYSTEM:'1',GIT_CONFIG_GLOBAL:configuration};
    return (await (launch??control!.launch)(['git','-c',`core.hooksPath=${hooks}`,...args],repository,env)).replace(/\n$/,'');
  }finally{if(control){process.off('SIGINT',onInt);process.off('SIGTERM',onTerm);}rmSync(temporary,{recursive:true,force:true});}
}
export async function repositoryIdentity(repository:string,execute:GitExecutor=git) {
  const root=realpathSync(await execute(repository,['rev-parse','--show-toplevel']));
  const common=realpathSync(await execute(root,['rev-parse','--path-format=absolute','--git-common-dir']));return {root,common};
}
export async function selectedCommit(repository:string,ref:string,execute:GitExecutor=git) {return execute(repository,['rev-parse','--verify','--end-of-options',`${ref}^{commit}`]);}
export async function worktreeIdentity(path:string,common:string,execute:GitExecutor=git) {
  const identity=await repositoryIdentity(path,execute);
  if(identity.root!==realpathSync(path)||identity.common!==common)throw new Error('worktree belongs to another repository');
  const registered=(await execute(path,['worktree','list','--porcelain','-z'])).split('\0').some(field=>field===`worktree ${identity.root}`);
  if(!registered)throw new Error('worktree is not registered with Git');
  return realpathSync(await execute(path,['rev-parse','--path-format=absolute','--git-dir']));
}
export async function createWorktree(repository:string,destination:string,commit:string,execute:GitExecutor=git) {
  if(existsSync(destination))throw new Error('worktree destination collision');await execute(repository,['worktree','add','--detach','--',resolve(destination),commit]);
}


export interface PreparationIdentity {
  directory: { device: string; inode: string };
  marker: { device: string; inode: string; sha256: string };
}
/** Opaque file evidence only. Git remains the authority for registration semantics. */
export function preparationIdentity(path: string): PreparationIdentity {
  const directory=lstatSync(path,{bigint:true});
  if(!directory.isDirectory()||directory.isSymbolicLink()||realpathSync(path)!==path||directory.ino===0n)throw new Error('prepared worktree path identity unavailable or changed');
  const markerPath=join(path,'.git'),marker=lstatSync(markerPath,{bigint:true});
  if(!marker.isFile()||marker.isSymbolicLink()||marker.ino===0n||marker.size>16384n)throw new Error('prepared worktree marker must be a bounded regular file');
  const descriptor=openSync(markerPath,constants.O_RDONLY|(constants.O_NOFOLLOW??0)|(constants.O_NONBLOCK??0));
  try {
    const opened=fstatSync(descriptor,{bigint:true});
    if(!opened.isFile()||opened.dev!==marker.dev||opened.ino!==marker.ino||opened.size>16384n)throw new Error('prepared worktree marker changed');
    const bytes=Buffer.alloc(16385);let count=0;
    while(count<bytes.length){const n=readSync(descriptor,bytes,count,bytes.length-count,count);if(!n)break;count+=n;}
    const ended=fstatSync(descriptor,{bigint:true}),current=lstatSync(markerPath,{bigint:true}),root=lstatSync(path,{bigint:true});
    if(count>16384||BigInt(count)!==opened.size||ended.size!==opened.size||ended.mtimeNs!==opened.mtimeNs||current.isSymbolicLink()||current.dev!==opened.dev||current.ino!==opened.ino||root.isSymbolicLink()||root.dev!==directory.dev||root.ino!==directory.ino||realpathSync(path)!==path)throw new Error('prepared worktree identity changed while reading');
    return {directory:{device:String(directory.dev),inode:String(directory.ino)},marker:{device:String(opened.dev),inode:String(opened.ino),sha256:createHash('sha256').update(bytes.subarray(0,count)).digest('hex')}};
  } finally {closeSync(descriptor);}
}
export function assertPreparationIdentity(path:string,expected:PreparationIdentity) {
  if(JSON.stringify(preparationIdentity(path))!==JSON.stringify(expected))throw new Error('prepared worktree filesystem identity changed; refusing recovery');
}
