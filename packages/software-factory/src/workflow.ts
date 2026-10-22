import { spawn } from 'node:child_process';
import { randomUUID } from 'node:crypto';
import { realpathSync } from 'node:fs';
import { hostname } from 'node:os';
import { isAbsolute, relative, resolve, sep } from 'node:path';
import type { Admission } from './accounting.js';
import type { RepositoryStore } from './store.js';
import type { InvocationRecorder } from './capture.js';

export interface CommandOptions {
  argv: string[]; cwd?: string; env?: Record<string, string>; shell?: string;
  intent?: Admission['intent']; priorAttemptId?: string; loopKey?: string;
}
export interface CommandResult { attemptId: string; exitCode: number | null; cleanup: 'complete' | 'unknown' }
export interface WorkflowContext {
  readonly worktree: string;
  scope<T>(name: string, action: (context: WorkflowContext) => Promise<T>): Promise<T>;
  command(name: string, options: CommandOptions): Promise<CommandResult>;
  progress(message: string): Promise<void>;
  needsInput(question: string, context: string): Promise<never>;
  agent(name: string, options: unknown): Promise<never>;
}
export class NeedsInput extends Error {}
export class CommandRunner {
  constructor(readonly store: RepositoryStore, readonly recorder: InvocationRecorder, readonly invocationId: string, readonly worktree: string) {}
  private readonly pending = new Set<Promise<CommandResult>>();
  private failure: unknown;
  execute(key: string, options: CommandOptions, startup = false): Promise<CommandResult> {
    const operation = this.perform(key, options, startup);
    this.pending.add(operation);
    void operation.then(() => { this.pending.delete(operation); }, error => { this.failure ??= error; this.pending.delete(operation); });
    return operation;
  }
  async drain() {
    while (this.pending.size) await Promise.allSettled([...this.pending]);
    if (this.failure) throw this.failure;
  }
  private async perform(key: string, options: CommandOptions, startup: boolean): Promise<CommandResult> {
    if (!Array.isArray(options.argv) || !options.argv.length || options.argv.some(value => typeof value !== 'string' || value.includes('\0')) || !options.argv[0]) throw new Error('command requires nonempty argv without NUL');
    if (options.shell !== undefined && (typeof options.shell !== 'string' || !isAbsolute(options.shell))) throw new Error('explicit shell must be an absolute executable path');
    const cwd = realpathSync(resolve(this.worktree, options.cwd ?? '.'));
    const outside = relative(realpathSync(this.worktree), cwd);
    if (outside === '..' || outside.startsWith(`..${sep}`) || isAbsolute(outside)) throw new Error('command cwd must be inside selected worktree');
    const env = options.env ?? { PATH: process.env.PATH ?? '' };
    if (!env || typeof env !== 'object' || Array.isArray(env) || Object.entries(env).some(([key, value]) => !key || key.includes('=') || key.includes('\0') || typeof value !== 'string' || value.includes('\0'))) throw new Error('invalid command environment');
    const attempt = await this.store.admitAttempt({ id: randomUUID(), invocationId: this.invocationId, operationKey: key, kind: 'command', intent: options.intent ?? 'initial',
      ...(options.priorAttemptId ? { priorAttemptId: options.priorAttemptId } : {}), ...(options.loopKey ? { loopKey: options.loopKey } : {}) }, startup);
    const request = await this.recorder.openCapture({ channel: 'context', attemptId: attempt.id });
    await request.write(JSON.stringify({ argv: options.argv, cwd, env, shell: options.shell ?? false })); await request.finish();
    const stdout = await this.recorder.openCapture({ channel: 'stdout', attemptId: attempt.id });
    const stderr = await this.recorder.openCapture({ channel: 'stderr', attemptId: attempt.id });
    let child;
    try { child = spawn(options.argv[0]!, options.argv.slice(1), { cwd, env, shell: options.shell ?? false, detached: process.platform !== 'win32', stdio: ['ignore', 'pipe', 'pipe'] }); }
    catch (error) {
      await stdout.finish(); await stderr.finish();
      await this.store.settleAttempt({ id: attempt.id, launch: 'not_started', outcome: 'failed', quiescent: true, evidence: 'spawn rejected before process creation' });
      throw error;
    }
    const close = new Promise<{ code: number | null; error?: Error }>(resolve => {
      let error: Error | undefined;
      child.once('error', value => { error = value; });
      child.once('close', code => resolve({ code, ...(error ? { error } : {}) }));
    });
    const output = Promise.all([stdout.consume(child.stdout!), stderr.consume(child.stderr!)]);
    const launched = child.pid !== undefined;
    if (launched) await this.store.markStarted({ id: attempt.id, owner: { host: hostname(), pid: child.pid!, start: null } });
    const result = await close; await output; await this.recorder.barrier();
    let quiescent = !launched;
    if (launched && process.platform !== 'win32') {
      try { process.kill(-child.pid!, 0); } catch (error) { quiescent = (error as NodeJS.ErrnoException).code === 'ESRCH'; }
    }
    await this.store.settleAttempt({ id: attempt.id, launch: launched ? 'started' : 'not_started', outcome: result.code === 0 && !result.error ? 'succeeded' : 'failed', quiescent,
      evidence: launched ? (quiescent ? 'process closed; owned process group absent' : 'process closed; descendant cleanup unknown') : 'spawn error before process creation' });
    if (result.error) throw result.error;
    if (result.code !== 0) throw new Error(`command failed: ${key} (exit ${result.code})`);
    if (!quiescent) throw new Error(`command descendant cleanup unknown: ${key}`);
    return { attemptId: attempt.id, exitCode: result.code, cleanup: 'complete' };
  }
}
export function workflowContext(runner: CommandRunner, prefix = ''): WorkflowContext {
  const key = (name: string) => {
    if (typeof name !== 'string' || !name || name.includes('\0')) throw new Error('operation requires a name');
    return prefix + name;
  };
  return {
    worktree: runner.worktree,
    scope: (name, action) => action(workflowContext(runner, key(name) + '/')),
    command: (name, options) => runner.execute(key(name), options),
    async progress(message) {
      const writer = await runner.recorder.openCapture({ channel: 'event' });
      await writer.write(message); await writer.finish();
    },
    async needsInput(question, context) {
      if (typeof question !== 'string' || !question.trim() || typeof context !== 'string' || !context.trim()) throw new Error('needsInput requires nonempty question and context');
      const writer = await runner.recorder.openCapture({ channel: 'request' });
      await writer.write(JSON.stringify({ question, context })); await writer.finish();
      throw new NeedsInput('workflow needs input');
    },
    async agent() { throw new Error('agent adapters unavailable; no agent attempt launched'); },
  };
}
