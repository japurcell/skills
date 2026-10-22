import { AgentCalls } from './agents.js';
import type { AgentConfiguration, AgentOptions } from './agents.js';
import type { AgentResult } from './adapters/types.js';
export type { AgentOptions } from './agents.js';
export type { AgentResult, PayloadValidator } from './adapters/types.js';
export type { ProfileFields, EffectiveInputs, SkillInput } from './profiles.js';
import { spawn } from 'node:child_process';
import { randomUUID } from 'node:crypto';
import { realpathSync } from 'node:fs';
import { setTimeout as delay } from 'node:timers/promises';
import { currentOwner, duration, LiveProcessScope } from './native/process.js';
import { isAbsolute, relative, resolve, sep } from 'node:path';
import type { Admission } from './accounting.js';
import type { RepositoryStore } from './store.js';
import type { InvocationRecorder } from './capture.js';

export interface CommandOptions {
  argv: string[]; cwd?: string; env?: Record<string, string>; shell?: string;
  /** False returns ordinary nonzero exits for explicit workflow handling. Infrastructure failures still throw. */
  required?: boolean; timeoutMs?: number; childScope?: 'process-group' | 'unknown';
  intent?: Admission['intent']; priorAttemptId?: string; loopKey?: string;
}
export interface CommandResult { attemptId: string; exitCode: number | null; cleanup: 'complete' | 'unknown' }
export interface WorkflowContext {
  readonly worktree: string;
  scope<T>(name: string, action: (context: WorkflowContext) => Promise<T>): Promise<T>;
  command(name: string, options: CommandOptions): Promise<CommandResult>;
  progress(message: string): Promise<void>;
  needsInput(question: string, context: string): Promise<never>;
  agent<T=unknown>(name: string, options: AgentOptions<T>): Promise<AgentResult<T>>;
  cancel(reason: string): Promise<never>;
}
export { NeedsInput, ShutdownInterrupted } from './execution-control.js';
import { NeedsInput, ShutdownInterrupted } from './execution-control.js';
import type { StopCause } from './execution-control.js';
export type { StopCause } from './execution-control.js';
export class CommandRunner {
  constructor(readonly store: RepositoryStore, readonly recorder: InvocationRecorder, readonly invocationId: string, readonly worktree: string,
    readonly settings: {commandTimeoutMs?:number; agentTimeoutMs?:number; shutdownGraceMs?:number} & AgentConfiguration = {}) {
    this.agents = new AgentCalls(this,settings);
    this.agentTimeoutMs = duration(settings.agentTimeoutMs,3600000);
    this.commandTimeoutMs = duration(settings.commandTimeoutMs, 1800000);
    this.grace = duration(settings.shutdownGraceMs, 30000, 300000);
    this.stopped = new Promise(resolve => { this.stopResolve = resolve; });
  }
  private readonly agents:AgentCalls;
  private readonly agentStops=new Map<string,()=>Promise<void>>();
  get dispatchStopped(){return this.admissionStopped;}
  registerAgent(id:string,scope:LiveProcessScope,stop:()=>Promise<void>){this.active.set(id,scope);this.agentStops.set(id,stop);if(this.stopping)void stop().catch(()=>{this.unresolved=true;});}
  unregisterAgent(id:string){this.active.delete(id);this.agentStops.delete(id);}
  agent<T>(key:string,options:AgentOptions<T>){return this.track(()=>this.agents.execute(key,options));}
  readonly commandTimeoutMs: number;
  readonly agentTimeoutMs: number;
  readonly grace: number;
  private readonly pending = new Set<Promise<unknown>>();
  private readonly active = new Map<string, LiveProcessScope>();
  private failure: unknown;
  private failed = false;
  private question: NeedsInput | undefined;
  private closed = false;
  private admissionStopped = false;
  private stopAt: number | undefined;
  private stopResolve!: () => void;
  readonly stopped: Promise<void>;
  readonly reasons: {cause:StopCause;message:string}[] = [];
  signal: 'SIGINT' | 'SIGTERM' | undefined;
  unresolved = false;
  private stopRecord: Promise<unknown> | undefined;
  get stopping() { return this.stopAt !== undefined; }
  block() {
    this.admissionStopped = true; this.store.blockAdmissions(this.invocationId);
    return this.stopRecord ??= this.store.stopAdmissions(this.invocationId).catch(error => { this.unresolved = true; this.failed = true; this.failure ??= error; throw error; });
  }
  requestShutdown(cause: StopCause, message: string, signal?: 'SIGINT' | 'SIGTERM') {
    if (this.closed) return;
    if (signal) this.signal ??= signal;
    this.reasons.push({cause,message});
    void this.block().catch(()=>{});
    if (!this.stopping) {
      this.stopAt = performance.now();
      this.stopResolve();
    }
    for (const [id,scope] of this.active) { const stop=this.agentStops.get(id); if(stop)void stop().catch(()=>{this.unresolved=true;}); else void scope.stop(this.grace); }
  }
  track<T>(action: () => Promise<T>): Promise<T> {
    const operation = Promise.resolve().then(() => {
      if (this.closed) throw new ShutdownInterrupted('invocation already closed');
      return action();
    });
    this.pending.add(operation);
    void operation.then(() => { this.pending.delete(operation); }, error => {
      if (!this.closed) {
        if (error instanceof NeedsInput) this.question ??= error;
        else if (!(error instanceof ShutdownInterrupted)) {
          this.failed = true; this.failure ??= error;
          this.requestShutdown('failure', error instanceof Error ? error.message : 'workflow action failed');
        }
      }
      this.pending.delete(operation);
    });
    return operation;
  }
  async waitFor<T>(operation: Promise<T>): Promise<T> {
    return Promise.race([operation, this.stopped.then(() => { throw new ShutdownInterrupted('shutdown requested'); })]);
  }
  execute(key: string, options: CommandOptions, startup = false): Promise<CommandResult> { return this.track(() => this.perform(key, options, startup)); }
  async startupGit(argv:string[],cwd:string,env:Record<string,string>):Promise<string> {
    const parts:Buffer[]=[];let bytes=0;
    await this.track(()=>this.perform(`startup/git/${randomUUID()}/${this.invocationId}`,{argv,env},true,{cwd,stdout:chunk=>{bytes+=chunk.length;if(bytes>1048576)throw new Error('startup Git output exceeds bounded limit');parts.push(Buffer.from(chunk));}}));
    return Buffer.concat(parts).toString('utf8');
  }
  async drain() {
    while (this.pending.size) {
      if (!this.stopping) await Promise.race([Promise.allSettled([...this.pending]), this.stopped]);
      else {
        const remaining = Math.max(0, this.stopAt! + this.grace + 1000 - performance.now());
        const settled = await Promise.race([Promise.allSettled([...this.pending]).then(()=>true), delay(remaining,undefined,{ref:false}).then(()=>false)]);
        if (!settled) { this.unresolved = true; break; }
      }
    }
    if (this.stopping) await this.stopRecord;
    if (this.failed) throw this.failure;
    this.agents.assertValid();
    if (this.question) throw this.question;
    if (this.stopping) throw new ShutdownInterrupted(this.reasons[0]?.message ?? 'shutdown requested');
  }
  close() { this.closed = true; if (this.pending.size || this.active.size) this.unresolved = true; }
  private async perform(key: string, options: CommandOptions, startup: boolean, setup?:{cwd:string;stdout:(chunk:Buffer)=>void}): Promise<CommandResult> {
    if (this.admissionStopped) throw new ShutdownInterrupted('shutdown stopped dispatch');
    if (!Array.isArray(options.argv) || !options.argv.length || options.argv.some(value => typeof value !== 'string' || value.includes('\0')) || !options.argv[0]) throw new Error('command requires nonempty argv without NUL');
    if (options.required !== undefined && typeof options.required !== 'boolean') throw new Error('command required must be a boolean');
    if (options.childScope !== undefined && !['process-group','unknown'].includes(options.childScope)) throw new Error('invalid command child scope');
    const timeout = duration(options.timeoutMs, this.commandTimeoutMs);
    if (options.shell !== undefined && (typeof options.shell !== 'string' || !isAbsolute(options.shell))) throw new Error('explicit shell must be an absolute executable path');
    const cwd = realpathSync(setup?.cwd ?? resolve(this.worktree, options.cwd ?? '.'));
    const outside = setup ? '' : relative(realpathSync(this.worktree), cwd);
    if (outside === '..' || outside.startsWith(`..${sep}`) || isAbsolute(outside)) throw new Error('command cwd must be inside selected worktree');
    const env = options.env ?? { PATH: process.env.PATH ?? '' };
    if (!env || typeof env !== 'object' || Array.isArray(env) || Object.entries(env).some(([key, value]) => !key || key.includes('=') || key.includes('\0') || typeof value !== 'string' || value.includes('\0'))) throw new Error('invalid command environment');
    const admission = {id:randomUUID(),invocationId:this.invocationId,operationKey:key,kind:'command' as const,intent:options.intent ?? 'initial' as const,
      ...(options.priorAttemptId ? {priorAttemptId:options.priorAttemptId} : {}),...(options.loopKey ? {loopKey:options.loopKey} : {})};
    let attempt;
    while (!attempt) {
      if (this.admissionStopped) throw new ShutdownInterrupted('shutdown cancelled capacity wait');
      try { attempt = await this.store.admitAttempt(admission,startup); }
      catch (error) {
        if (error instanceof Error && /command capacity exhausted/.test(error.message)) { await Promise.race([delay(100),this.stopped]); continue; }
        if (this.admissionStopped) throw new ShutdownInterrupted('shutdown stopped admission');
        throw error;
      }
    }
    const request = await this.recorder.openCapture({channel:'context',attemptId:attempt.id});
    await request.write(JSON.stringify({argv:options.argv,cwd,env,shell:options.shell ?? false,required:options.required ?? true,timeoutMs:timeout,
      childScope:options.childScope ?? (process.platform === 'win32' ? 'unknown' : 'process-group'),limitation:'process group members only; escaped/remote activity is not controlled'})); await request.finish();
    const stdout = await this.recorder.openCapture({channel:'stdout',attemptId:attempt.id});
    const stderr = await this.recorder.openCapture({channel:'stderr',attemptId:attempt.id});
    if (this.admissionStopped) {
      await stdout.finish(); await stderr.finish();
      await this.store.settleAttempt({id:attempt.id,launch:'not_started',outcome:'interrupted',quiescent:true,evidence:'shutdown after admission before spawn'});
      throw new ShutdownInterrupted('shutdown stopped launch');
    }
    let child;
    try { child = spawn(options.argv[0]!,options.argv.slice(1),{cwd,env,shell:options.shell ?? false,detached:process.platform !== 'win32',stdio:['ignore','pipe','pipe']}); }
    catch (error) {
      await stdout.finish(); await stderr.finish();
      await this.store.settleAttempt({id:attempt.id,launch:'not_started',outcome:'failed',quiescent:true,evidence:'spawn rejected before process creation'}); throw error;
    }
    const scope = new LiveProcessScope(child, options.childScope === 'unknown'); this.active.set(attempt.id,scope);
    const source = setup ? (async function*(){for await(const chunk of child.stdout!){setup.stdout(chunk as Buffer);yield chunk;}})() : child.stdout!;
    const output = Promise.allSettled([stdout.consume(source).catch(error=>{this.requestShutdown(this.recorder.failed?'recording':'failure','command output unavailable');throw error;}),stderr.consume(child.stderr!)]);
    const launched = child.pid !== undefined;
    let timedOut = false;
    const timer = setTimeout(() => { timedOut = true; this.requestShutdown('timeout',`command timeout: ${key}`); },timeout);
    try {
      if (launched) await this.store.markStarted({id:attempt.id,owner:currentOwner(child.pid!)});
      const result = await scope.result(this.grace); const streams = await output; await this.recorder.barrier();
      const rejected=streams.find(item=>item.status==='rejected');if(rejected?.status==='rejected')throw rejected.reason;
      const interrupted = scope.interrupted && (result.signal !== null || result.code !== 0);
      const outcome = timedOut ? 'failed' : interrupted ? 'interrupted' : result.code === 0 && !result.error ? 'succeeded' : 'failed';
      await this.store.settleAttempt({id:attempt.id,launch:launched ? 'started' : 'not_started',outcome,quiescent:result.quiescent || !launched,
        evidence:!launched ? 'spawn error before process creation' : `exit=${result.code}; signal=${result.signal}; ${timedOut ? 'timeout' : interrupted ? 'shutdown requested' : 'ordinary exit'}; ${result.quiescent ? 'qualified owned group absent' : 'child scope cleanup unknown'}`});
      if (result.error) throw result.error;
      if (timedOut) throw new Error(`command timeout: ${key}`);
      if (interrupted) throw new ShutdownInterrupted(`command interrupted by shutdown: ${key}`);
      if (!result.quiescent) throw new Error(`command descendant cleanup unknown: ${key}`);
      if (result.code === null || (result.code !== 0 && options.required !== false)) throw new Error(`command failed: ${key} (exit ${result.code})`);
      return {attemptId:attempt.id,exitCode:result.code,cleanup:'complete'};
    } catch (error) {
      // Keep the live reference registered until a failed launch/settlement save has stopped it.
      if(!(error instanceof ShutdownInterrupted))this.requestShutdown(this.recorder.failed ? 'recording' : 'failure',error instanceof Error ? error.message : 'command recording failed');
      await scope.stop(this.grace); await output;
      throw error;
    } finally { clearTimeout(timer); this.active.delete(attempt.id); }
  }
}
export function workflowContext(runner: CommandRunner, prefix = ''): WorkflowContext {
  const key = (name: string) => {
    if (typeof name !== 'string' || !name || name.includes('\0')) throw new Error('operation requires a name');
    return prefix + name;
  };
  return {
    worktree: runner.worktree,
    scope: (name, action) => runner.track(() => action(workflowContext(runner, key(name) + '/'))),
    command: (name, options) => runner.execute(key(name), options),
    progress: message => runner.track(async () => {
      const writer = await runner.recorder.openCapture({ channel: 'event' });
      await writer.write(message); await writer.finish();
    }),
    needsInput: (question, context) => runner.track(async () => {
      if (typeof question !== 'string' || !question.trim() || typeof context !== 'string' || !context.trim()) throw new Error('needsInput requires nonempty question and context');
      await runner.block();
      const writer = await runner.recorder.openCapture({ channel: 'request' });
      await writer.write(JSON.stringify({ question, context })); await writer.finish();
      runner.requestShutdown('needs_input','workflow needs input');
      throw new NeedsInput('workflow needs input');
    }),
    cancel: reason => runner.track(async () => { if (typeof reason !== 'string' || !reason.trim()) throw new Error('cancel requires a nonempty reason'); runner.requestShutdown('manual',reason); throw new ShutdownInterrupted(reason); }),
    agent: (name,options) => runner.agent(key(name),options),
  };
}
