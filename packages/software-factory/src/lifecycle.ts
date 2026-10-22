import { randomUUID } from 'node:crypto';
import { existsSync, lstatSync, mkdirSync, readFileSync, realpathSync } from 'node:fs';
import { hostname } from 'node:os';
import { join } from 'node:path';
import { buildWorkflow } from './build.js';
import { InvocationRecorder } from './capture.js';
import { openRepositoryStore } from './store.js';
import { CommandRunner, NeedsInput, workflowContext } from './workflow.js';
import { createWorktree, repositoryIdentity, selectedCommit, worktreeIdentity } from './workspace.js';

export interface InvokeOptions {
  repository: string; workflow: string; input: string; newWorktree: boolean; ref?: string;
  worktreeId?: string; runId?: string; question?: string; contexts?: string[];
}
export async function invoke(options: InvokeOptions) {
  if (!options.repository || !options.workflow || !options.input || options.newWorktree === !!options.worktreeId) throw new Error('invoke requires --repository, --workflow, --input and exactly one of --new-worktree or --worktree');
  if (options.ref && !options.newWorktree) throw new Error('--ref requires --new-worktree');
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
    invocation = await store.startInvocation({ runId, worktreeId: worktree.id, owner: { host: hostname(), pid: process.pid, start: null } });
    recorder = new InvocationRecorder({ store, invocationId: invocation.id, secrets: Object.entries(process.env).filter(([key]) => /SECRET|TOKEN|PASSWORD|API_KEY/.test(key)).map(([, value]) => value!).filter(value => value.length >= 4), requestShutdown: () => { store.blockAdmissions(invocation!.id); } });
    const context = await recorder.openCapture({ channel: 'context' });
    await context.write(JSON.stringify({ inputs, question: options.question ?? null, contexts: options.contexts ?? [] })); await context.finish();
    await store.saveInvocationMetadata(invocation.id, { workflow: options.workflow, selectedCommit: commit, inputCaptureId: context.id, question: options.question ?? null, contexts: options.contexts ?? [] });
    if (commit) {
      createWorktree(identity.root, worktree.path, commit);
      await store.finalizeWorktree({ id: worktree.id, claimId: invocation.claim.id, token: invocation.claim.token, registration: worktreeIdentity(worktree.path, identity.common) });
    }
    runner = new CommandRunner(store, recorder, invocation.id, worktree.path);
    const run = await buildWorkflow({ common: identity.common, worktree: worktree.path, workflow: options.workflow, invocationId: invocation.id, runner });
    await store.activateInvocation(invocation.id); entered = true;
    const result = await run(workflowContext(runner), inputs as Record<string, unknown>);
    await runner.drain();
    if (result !== undefined) { const writer = await recorder.openCapture({ channel: 'report' }); await writer.write(JSON.stringify(result)); await writer.finish(); }
    await recorder.barrier(); await store.stopAdmissions(invocation.id);
    await store.finishInvocation(invocation.id, 'succeeded', 'complete');
    await store.releaseClaim({ claimId: invocation.claim.id, token: invocation.claim.token, basis: 'quiescent' });
    return { runId, invocationId: invocation.id, worktreeId: worktree.id, worktree: worktree.path, outcome: 'succeeded', cleanup: 'complete', exitCode: 0 };
  } catch (error) {
    if (!invocation) throw error;
    try { await runner?.drain(); } catch { /* Preserve the workflow failure and all settled command facts. */ }
    const diagnostic = error instanceof Error ? error.message : 'workflow failed';
    let cleanup: 'complete' | 'unknown' = 'unknown';
    const outcome = error instanceof NeedsInput ? 'needs_input' : 'failed';
    try {
      if (recorder && !recorder.failed) { const writer = await recorder.openCapture({ channel: 'event' }); await writer.write(diagnostic); await writer.finish(); await recorder.barrier(); }
      await store.stopAdmissions(invocation.id);
      const history = store.readHistory(invocation.id);
      cleanup = history.attempts.every(attempt => attempt.quiescent) && !recorder?.failed ? 'complete' : 'unknown';
      await store.finishInvocation(invocation.id, outcome, cleanup);
      if (cleanup === 'complete') await store.releaseClaim({ claimId: invocation.claim.id, token: invocation.claim.token, basis: 'quiescent' });
    } catch { cleanup = 'unknown'; }
    return { runId: invocation.runId, invocationId: invocation.id, worktreeId: invocation.worktreeId, worktree: worktreePath, outcome, cleanup, diagnostic, exitCode: cleanup !== 'complete' ? 1 : !entered ? 3 : outcome === 'needs_input' ? 2 : 1 };
  } finally { store.close(); }
}
