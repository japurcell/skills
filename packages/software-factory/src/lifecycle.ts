import type { AgentConfiguration } from './agents.js';
import { environmentRedactionPolicy, redactText } from './redaction.js';
import { randomUUID } from 'node:crypto';
import { existsSync, lstatSync, mkdirSync, readFileSync, realpathSync } from 'node:fs';
import { currentOwner, duration } from './native/process.js';
import { join } from 'node:path';
import { buildWorkflow } from './build.js';
import { InvocationRecorder } from './capture.js';
import { openRepositoryStore } from './store.js';
import { CommandRunner, NeedsInput, ShutdownInterrupted, workflowContext } from './workflow.js';
import { createWorktree, git, repositoryIdentity, selectedCommit, StartupGitControl, StartupInterrupted, worktreeIdentity } from './workspace.js';

export interface InvokeOptions extends AgentConfiguration {
  repository: string; workflow: string; input: string; newWorktree: boolean; ref?: string;
  worktreeId?: string; runId?: string; question?: string; contexts?: string[]; commandTimeoutMs?:number; agentTimeoutMs?:number; shutdownGraceMs?:number;
}
export async function invoke(options:InvokeOptions) {
  const settings={agentTimeoutMs:duration(options.agentTimeoutMs,3600000),commandTimeoutMs:duration(options.commandTimeoutMs,1800000),shutdownGraceMs:duration(options.shutdownGraceMs,30000,300000)};
  const early=new StartupGitControl(settings.shutdownGraceMs,settings.commandTimeoutMs);let runner:CommandRunner|undefined;
  const onInt=()=>{early.stop('SIGINT');runner?.requestShutdown('signal','user SIGINT','SIGINT');};
  const onTerm=()=>{early.stop('SIGTERM');runner?.requestShutdown('signal','user SIGTERM','SIGTERM');};
  // Awaiting authored code alone does not keep Node alive; this foreground owner remains live until finalization/explicit stop.
  const foreground=setInterval(()=>{},1000);process.on('SIGINT',onInt);process.on('SIGTERM',onTerm);
  try{return await invokeOwned(options,settings,early,value=>{runner=value;});}
  catch(error){const message=redactText(error instanceof Error?error.message:'startup refused');if(error instanceof StartupInterrupted)throw new StartupInterrupted(error.exitCode,message);throw new Error(message);}
  finally{clearInterval(foreground);process.off('SIGINT',onInt);process.off('SIGTERM',onTerm);}
}
async function invokeOwned(options:InvokeOptions,settings:{agentTimeoutMs:number;commandTimeoutMs:number;shutdownGraceMs:number},early:StartupGitControl,attach:(runner:CommandRunner)=>void) {
  if (!options.repository || !options.workflow || !options.input || options.newWorktree === !!options.worktreeId) throw new Error('invoke requires --repository, --workflow, --input and exactly one of --new-worktree or --worktree');
  if (options.ref && !options.newWorktree) throw new Error('--ref requires --new-worktree');
  const inputs: unknown = JSON.parse(readFileSync(options.input, 'utf8'));
  if (!inputs || typeof inputs !== 'object' || Array.isArray(inputs)) throw new Error('input must be a JSON object');
  const executeEarly=(repository:string,args:string[])=>git(repository,args,early.launch);
  const identity = await repositoryIdentity(options.repository,executeEarly);
  const commit = options.newWorktree ? await selectedCommit(identity.root, options.ref ?? 'HEAD',executeEarly) : null;
  const policy=environmentRedactionPolicy();
  const store = openRepositoryStore(identity.common);
  let invocation: Awaited<ReturnType<typeof store.startInvocation>> | undefined;
  let recorder: InvocationRecorder | undefined;
  let worktreePath: string | undefined;
  let entered = false;
  let runner: CommandRunner | undefined;
  try {
    const runId = options.runId ?? (await store.createRun()).id;
    store.readAccounting(runId);
    if (options.question) store.validateReference({ id: options.question, runId, question: true });
    for (const id of options.contexts ?? []) store.validateReference({ id, runId });
    let worktree;
    if (options.newWorktree) {
      const directory = join(identity.common, 'factory', 'worktrees');
      if (!existsSync(directory)) mkdirSync(directory, { mode: 0o700 });
      if (!lstatSync(directory).isDirectory() || lstatSync(directory).isSymbolicLink()) throw new Error('factory worktrees directory must not be a symlink');
      worktree = await store.reserveWorktree(join(directory, randomUUID()));
    } else {
      try { worktree = store.readWorktree(options.worktreeId!); }
      catch {
        const registration = await worktreeIdentity(options.worktreeId!, identity.common,executeEarly);
        worktree = await store.registerWorktree({ path: realpathSync(options.worktreeId!), registration });
      }
      if (await worktreeIdentity(worktree.path, identity.common,executeEarly) !== worktree.registration) throw new Error('worktree Git registration changed; refusing reuse');
    }
    worktreePath = worktree.path;
    invocation = await store.startInvocation({ runId, worktreeId: worktree.id, owner: currentOwner() });
    recorder = new InvocationRecorder({ store, invocationId: invocation.id, secrets: policy.secrets, requestShutdown: reason => { store.blockAdmissions(invocation!.id); runner?.requestShutdown('recording',reason); } });
    runner = new CommandRunner(store,recorder,invocation.id,worktree.path,{...settings,...(options.adapters?{adapters:options.adapters}:{}),...(options.agentOverrides?{agentOverrides:options.agentOverrides}:{})});
    attach(runner);
    if(early.stopSignal)runner.requestShutdown('signal',`user ${early.stopSignal}`,early.stopSignal);
    const context = await recorder.openCapture({ channel: 'context' });
    await context.write(JSON.stringify({ inputs, question: options.question ?? null, contexts: options.contexts ?? [] })); await context.finish();
    await store.saveInvocationMetadata(invocation.id, { settings, workflow: options.workflow, selectedCommit: commit, inputCaptureId: context.id, question: options.question ?? null, contexts: options.contexts ?? [] });
    if (commit) {
      const executeSetup=(repository:string,args:string[])=>git(repository,args,(argv,cwd,env)=>runner!.startupGit(argv,cwd,env));
      await createWorktree(identity.root, worktree.path, commit,executeSetup);
      await store.finalizeWorktree({ id: worktree.id, claimId: invocation.claim.id, token: invocation.claim.token, registration: await worktreeIdentity(worktree.path, identity.common,executeSetup) });
    }
    const run = await runner.waitFor(buildWorkflow({ common: identity.common, worktree: worktree.path, workflow: options.workflow, invocationId: invocation.id, runner }));
    await store.activateInvocation(invocation.id); entered = true;
    const result = await runner.waitFor(run(workflowContext(runner), inputs as Record<string, unknown>));
    await runner.drain();
    if (result !== undefined) { const writer = await recorder.openCapture({ channel: 'report' }); await writer.write(JSON.stringify(result)); await writer.finish(); }
    await recorder.barrier(); await runner.drain(); await store.stopAdmissions(invocation.id);
    runner.close();
    await store.finalizeInvocation({id:invocation.id,outcome:'succeeded',cleanup:'complete',claimId:invocation.claim.id,token:invocation.claim.token});
    return { runId, invocationId: invocation.id, worktreeId: worktree.id, worktree: worktree.path, outcome: 'succeeded', cleanup: 'complete', exitCode: 0 };
  } catch (error) {
    if (!invocation) throw error;
    let failure = error;
    if (!(error instanceof NeedsInput) && !(error instanceof ShutdownInterrupted)) runner?.requestShutdown('failure', error instanceof Error ? error.message : 'workflow failed');
    try { await runner?.drain(); }
    catch (pendingFailure) {
      // An independent managed failure outranks a question, regardless of arrival order.
      const rank = (value:unknown) => value instanceof ShutdownInterrupted ? 1 : value instanceof NeedsInput ? 2 : 3;
      if (rank(pendingFailure) > rank(failure)) failure = pendingFailure;
    }
    const diagnostic = redactText(failure instanceof Error ? failure.message : 'workflow failed',policy);
    let cleanup: 'complete' | 'unknown' = 'unknown';
    runner?.close();
    const outcome = failure instanceof NeedsInput ? 'needs_input' : failure instanceof ShutdownInterrupted ? (runner?.signal ? 'interrupted' : 'cancelled') : 'failed';
    try {
      if (recorder && !recorder.failed) { const writer = await recorder.openCapture({ channel: 'event' }); await writer.write(JSON.stringify({diagnostic,reasons:runner?.reasons ?? []})); await writer.finish(); await recorder.barrier(); }
      await store.stopAdmissions(invocation.id);
      cleanup = !store.hasOccupiedActivity(invocation.id) && !recorder?.failed && !runner?.unresolved ? 'complete' : 'unknown';
      await store.finalizeInvocation({id:invocation.id,outcome,cleanup,claimId:invocation.claim.id,token:invocation.claim.token});
    } catch { cleanup = 'unknown'; }
    return { runId: invocation.runId, invocationId: invocation.id, worktreeId: invocation.worktreeId, worktree: worktreePath, outcome, cleanup, diagnostic, exitCode: cleanup !== 'complete' ? 1 : outcome === 'interrupted' && runner?.signal ? (runner.signal === 'SIGINT' ? 130 : 143) : !entered ? 3 : outcome === 'needs_input' ? 2 : 1 };
  } finally { runner?.close(); store.close(); }
}
