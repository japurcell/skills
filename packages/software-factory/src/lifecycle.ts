import { randomUUID } from 'node:crypto';
import { existsSync, lstatSync, mkdirSync, readFileSync, realpathSync } from 'node:fs';
import { currentOwner, duration } from './native/process.js';
import { join } from 'node:path';
import { buildWorkflow } from './build.js';
import { InvocationRecorder } from './capture.js';
import { openRepositoryStore } from './store.js';
import { CommandRunner, NeedsInput, ShutdownInterrupted, workflowContext } from './workflow.js';
import { createWorktree, repositoryIdentity, selectedCommit, worktreeIdentity } from './workspace.js';

export interface InvokeOptions {
  repository: string; workflow: string; input: string; newWorktree: boolean; ref?: string;
  worktreeId?: string; runId?: string; question?: string; contexts?: string[]; commandTimeoutMs?:number; agentTimeoutMs?:number; shutdownGraceMs?:number;
}
export async function invoke(options: InvokeOptions) {
  if (!options.repository || !options.workflow || !options.input || options.newWorktree === !!options.worktreeId) throw new Error('invoke requires --repository, --workflow, --input and exactly one of --new-worktree or --worktree');
  if (options.ref && !options.newWorktree) throw new Error('--ref requires --new-worktree');
  const settings = {agentTimeoutMs:duration(options.agentTimeoutMs,3600000),commandTimeoutMs:duration(options.commandTimeoutMs,1800000),shutdownGraceMs:duration(options.shutdownGraceMs,30000,300000)};
  const inputs: unknown = JSON.parse(readFileSync(options.input, 'utf8'));
  if (!inputs || typeof inputs !== 'object' || Array.isArray(inputs)) throw new Error('input must be a JSON object');
  const identity = repositoryIdentity(options.repository);
  const commit = options.newWorktree ? selectedCommit(identity.root, options.ref ?? 'HEAD') : null;
  const store = openRepositoryStore(identity.common);
  let invocation: Awaited<ReturnType<typeof store.startInvocation>> | undefined;
  let recorder: InvocationRecorder | undefined;
  let worktreePath: string | undefined;
  let entered = false;
  let runner: CommandRunner | undefined;
  const onInt = () => runner?.requestShutdown('signal','user SIGINT','SIGINT');
  const onTerm = () => runner?.requestShutdown('signal','user SIGTERM','SIGTERM');
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
        const registration = worktreeIdentity(options.worktreeId!, identity.common);
        worktree = await store.registerWorktree({ path: realpathSync(options.worktreeId!), registration });
      }
      if (worktreeIdentity(worktree.path, identity.common) !== worktree.registration) throw new Error('worktree Git registration changed; refusing reuse');
    }
    worktreePath = worktree.path;
    invocation = await store.startInvocation({ runId, worktreeId: worktree.id, owner: currentOwner() });
    recorder = new InvocationRecorder({ store, invocationId: invocation.id, secrets: Object.entries(process.env).filter(([key]) => /SECRET|TOKEN|PASSWORD|API_KEY/.test(key)).map(([, value]) => value!).filter(value => value.length >= 4), requestShutdown: reason => { store.blockAdmissions(invocation!.id); runner?.requestShutdown('recording',reason); } });
    runner = new CommandRunner(store,recorder,invocation.id,worktree.path,settings);
    process.on('SIGINT',onInt); process.on('SIGTERM',onTerm);
    const context = await recorder.openCapture({ channel: 'context' });
    await context.write(JSON.stringify({ inputs, question: options.question ?? null, contexts: options.contexts ?? [] })); await context.finish();
    await store.saveInvocationMetadata(invocation.id, { settings, workflow: options.workflow, selectedCommit: commit, inputCaptureId: context.id, question: options.question ?? null, contexts: options.contexts ?? [] });
    if (commit) {
      createWorktree(identity.root, worktree.path, commit);
      await store.finalizeWorktree({ id: worktree.id, claimId: invocation.claim.id, token: invocation.claim.token, registration: worktreeIdentity(worktree.path, identity.common) });
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
    const diagnostic = failure instanceof Error ? failure.message : 'workflow failed';
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
  } finally { runner?.close(); process.off('SIGINT',onInt); process.off('SIGTERM',onTerm); store.close(); }
}
