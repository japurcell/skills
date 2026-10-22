import { createHash } from 'node:crypto';
import { constants } from 'node:fs';
import { lstat, open, opendir, readlink } from 'node:fs/promises';
import { join } from 'node:path';
import type { Stats } from 'node:fs';
import type { AgentOptions, AgentResult, PayloadValidator, ProfileFields, WorkflowContext } from '@local/software-factory';

/** Copy and customize this ordinary code. The runtime owns admission, recording and cleanup. */
export type Phase = ProfileFields & { profile?: string; timeoutMs?: number };
export interface Check { name: string; argv: string[]; cwd?: string; env?: Record<string, string>; timeoutMs?: number }
export interface RecipeInputs {
  snapshot?: SnapshotLimits;
  prompt?: string;
  plan?: string | { steps: { title: string; prompt: string; skip?: boolean }[] };
  planning?: boolean;
  implement?: boolean;
  review?: boolean;
  checks?: Check[];
  browserVerification?: { enabled: boolean; agent?: Phase };
  agents?: { planning?: Phase; implementation?: Phase; review?: Phase; repair?: Phase };
  /** Explicit prior attempt IDs from a saved report when invoking current code again in joined history. */
  priorAttempts?: Record<string, string>;
}
export interface SnapshotLimits { maxEntries?: number; maxBytes?: number; timeoutMs?: number }
function snapshotLimits(limits: SnapshotLimits = {}) {
  if (!object(limits) || Object.keys(limits).some(key => !['maxEntries', 'maxBytes', 'timeoutMs'].includes(key))) throw new Error('invalid candidate snapshot limits');
  const selected = { maxEntries: 100000, maxBytes: 1073741824, timeoutMs: 10000, ...limits };
  if (!Number.isSafeInteger(selected.maxEntries) || selected.maxEntries <= 0 || !Number.isSafeInteger(selected.maxBytes) || selected.maxBytes <= 0 || !Number.isFinite(selected.timeoutMs) || selected.timeoutMs <= 0)
    throw new Error('candidate snapshot limits require finite positive entry/byte counts and duration');
  return selected;
}
export interface Summary { summary: string }
export interface Review extends Summary { findings: string[] }
const object = (value: unknown): value is Record<string, unknown> => !!value && typeof value === 'object' && !Array.isArray(value);
export const summaryOutput: PayloadValidator<Summary> = {
  name: 'recipe-summary-v1',
  validate: (value): value is Summary => object(value) && typeof value['summary'] === 'string' && !!value['summary'].trim(),
};
export const reviewOutput: PayloadValidator<Review> = {
  name: 'recipe-review-v1',
  validate: (value): value is Review => summaryOutput.validate(value) && Array.isArray((value as unknown as Record<string, unknown>)['findings']) &&
    ((value as unknown as Record<string, unknown>)['findings'] as unknown[]).every(item => typeof item === 'string' && !!item.trim()),
};
export function checkInputs(inputs: RecipeInputs) {
  snapshotLimits(inputs.snapshot);
  for (const field of ['planning', 'implement', 'review'] as const)
    if (inputs[field] !== undefined && typeof inputs[field] !== 'boolean') throw new Error(`${field} must be a boolean`);
  if (inputs.browserVerification !== undefined && (!object(inputs.browserVerification) || typeof inputs.browserVerification.enabled !== 'boolean'))
    throw new Error('browserVerification requires an explicit enabled boolean');
  if (inputs.priorAttempts !== undefined && (!object(inputs.priorAttempts) || Object.values(inputs.priorAttempts).some(id => typeof id !== 'string' || !id)))
    throw new Error('priorAttempts must contain explicit attempt IDs');
  if (inputs.checks !== undefined && !Array.isArray(inputs.checks)) throw new Error('checks must be an array');
  for (const check of inputs.checks ?? []) {
    if (!object(check)) throw new Error('checks require named argv commands');
    const unsupported = Object.keys(check).find(key => !['name', 'argv', 'cwd', 'env', 'timeoutMs'].includes(key));
    if (unsupported) throw new Error(`unsupported check field: ${unsupported}`);
    if (typeof check.name !== 'string' || !check.name.trim() || !Array.isArray(check.argv) || !check.argv.length || check.argv.some(arg => typeof arg !== 'string'))
      throw new Error('checks require unique names and argv arrays');
    if (check.cwd !== undefined && typeof check.cwd !== 'string') throw new Error('check cwd must be a string');
    if (check.env !== undefined && (!object(check.env) || Object.values(check.env).some(value => typeof value !== 'string')))
      throw new Error('check env must contain string values');
    if (check.timeoutMs !== undefined && (typeof check.timeoutMs !== 'number' || !Number.isFinite(check.timeoutMs) || check.timeoutMs <= 0))
      throw new Error('check timeoutMs must be finite and positive');
  }
  if (new Set((inputs.checks ?? []).map(check => check.name)).size !== (inputs.checks ?? []).length) throw new Error('check names must be unique');
}
export function requestText(inputs: RecipeInputs): string {
  if (inputs.prompt !== undefined && (typeof inputs.prompt !== 'string' || !inputs.prompt.trim())) throw new Error('prompt must be nonempty text');
  let plan = '';
  if (typeof inputs.plan === 'string') {
    if (!inputs.plan.trim()) throw new Error('plan must be nonempty text');
    plan = inputs.plan;
  } else if (inputs.plan !== undefined) {
    if (!object(inputs.plan) || !Array.isArray(inputs.plan.steps) || inputs.plan.steps.some(step => !object(step) || typeof step.title !== 'string' || !step.title.trim() || typeof step.prompt !== 'string' || !step.prompt.trim() || (step.skip !== undefined && typeof step.skip !== 'boolean')))
      throw new Error('structured plan requires titled prompt steps and optional boolean skip');
    plan = JSON.stringify({ steps: inputs.plan.steps.filter(step => !step.skip) });
  }
  if (!inputs.prompt && !plan) throw new Error('provide a prompt, prose plan or structured plan');
  return JSON.stringify({ prompt: inputs.prompt ?? null, plan: plan || null });
}
export function lineage(key: string, attempts: Record<string, string>): Pick<AgentOptions, 'intent' | 'priorAttemptId'> {
  return attempts[key] ? { intent: 'followup', priorAttemptId: attempts[key] } : { intent: 'initial' };
}
/** Best-effort identity of local candidate content/modes, excluding root Git metadata.
 * Symlinks are identified, not followed. This is a review freshness check, not a filesystem sandbox.
 */
export async function candidateFingerprint(worktree: string, limits?: SnapshotLimits): Promise<string> {
  const policy = snapshotLimits(limits), deadline = performance.now() + policy.timeoutMs;
  const hash = createHash('sha256');
  let entries = 0, totalBytes = 0;
  const budget = () => {
    if (performance.now() >= deadline) throw new Error('candidate snapshot time limit exceeded; narrow the candidate or explicitly increase snapshot.timeoutMs');
    if (entries > policy.maxEntries) throw new Error('candidate snapshot entry limit exceeded; narrow the candidate or explicitly increase snapshot.maxEntries');
    if (totalBytes > policy.maxBytes) throw new Error('candidate snapshot byte limit exceeded; narrow the candidate or explicitly increase snapshot.maxBytes');
  };
  const identity = (stat: Stats) => JSON.stringify([stat.dev, stat.ino, stat.mode, stat.size, stat.mtimeMs, stat.ctimeMs]);
  const record = (value: unknown[]) => hash.update(JSON.stringify(value) + '\n');
  const visit = async (directory: string, relative = '') => {
    budget();
    const originalDirectory = await lstat(directory);
    if (!originalDirectory.isDirectory()) throw new Error('candidate directory changed during inspection');
    const names: string[] = [];
    for await (const entry of await opendir(directory)) {
      if (!relative && entry.name === '.git') continue;
      entries++; budget(); names.push(entry.name);
    }
    for (const name of names.sort()) {
      budget();
      const path = join(directory, name), key = relative ? `${relative}/${name}` : name, stat = await lstat(path);
      if (stat.isSymbolicLink()) record([key, 'link', stat.mode, await readlink(path)]);
      else if (stat.isDirectory()) { record([key, 'directory', stat.mode]); await visit(path, key); }
      else if (stat.isFile()) {
        if (stat.size > policy.maxBytes - totalBytes) throw new Error('candidate snapshot byte limit exceeded; narrow the candidate or explicitly increase snapshot.maxBytes');
        const file = await open(path, constants.O_RDONLY | (constants.O_NOFOLLOW ?? 0) | (constants.O_NONBLOCK ?? 0));
        const content = createHash('sha256'), buffer = Buffer.alloc(65536);
        let bytes = 0;
        try {
          const opened = await file.stat();
          if (!opened.isFile() || identity(opened) !== identity(stat)) throw new Error(`candidate file changed before read: ${key}`);
          while (true) {
            budget();
            const { bytesRead } = await file.read(buffer, 0, Math.min(buffer.length, policy.maxBytes - totalBytes + 1), null);
            if (!bytesRead) break;
            bytes += bytesRead; totalBytes += bytesRead; budget(); content.update(buffer.subarray(0, bytesRead));
          }
          if (bytes !== stat.size || identity(await file.stat()) !== identity(stat) || identity(await lstat(path)) !== identity(stat))
            throw new Error(`candidate file changed during inspection: ${key}`);
        } finally { await file.close(); }
        record([key, 'file', stat.mode, bytes, content.digest('hex')]);
      } else throw new Error(`candidate contains unsupported special file: ${key}`);
    }
    if (identity(await lstat(directory)) !== identity(originalDirectory)) throw new Error('candidate directory changed during inspection');
  };
  await visit(worktree); budget();
  return hash.digest('hex');
}
export async function stable<T>(context: WorkflowContext, action: () => Promise<T>, limits?: SnapshotLimits): Promise<T> {
  const before = await candidateFingerprint(context.worktree, limits);
  const value = await action();
  if (await candidateFingerprint(context.worktree, limits) !== before) throw new Error('candidate changed during read-only phase; saved checks/review cannot certify it');
  return value;
}
/** Exactly one format-only correction; valid needs_input and infrastructure failures throw in the runtime. */
export async function structured<T>(context: WorkflowContext, key: string, options: AgentOptions<T>, attempts: Record<string, string>, limits?: SnapshotLimits): Promise<Extract<AgentResult<T>, { status: 'succeeded' }>> {
  let result = await context.agent(key, { ...options, context: JSON.stringify({ operation: key, context: options.context }), reuse: false });
  attempts[key] = result.attemptId;
  if (result.status === 'invalid') {
    const invalid = result;
    result = await stable(context, () => context.agent(key, {
      ...options, permissions: 'read-only', reuse: false, intent: 'format_correction', priorAttemptId: invalid.attemptId,
      context: JSON.stringify({ instruction: 'Correct only the saved control output format. Do not edit code or repeat the work.', operation: key, originalContext: options.context, resultCaptureId: invalid.resultCaptureId, diagnostic: invalid.diagnostic }),
    }), limits);
    attempts[key] = result.attemptId;
  }
  if (result.status === 'invalid') throw new Error(`invalid control output after one format correction: ${key}; ${result.diagnostic}`);
  return result;
}
export async function checks(context: WorkflowContext, prefix: string, selected: Check[], attempts: Record<string, string>) {
  const results: { name: string; attemptId: string; exitCode: number | null; cleanup: string }[] = [];
  for (const check of selected) {
    const key = `${prefix}/check/${check.name}`;
    const result = await context.command(key, {
      argv: check.argv,
      ...(check.cwd !== undefined ? { cwd: check.cwd } : {}),
      ...(check.env !== undefined ? { env: check.env } : {}),
      ...(check.timeoutMs !== undefined ? { timeoutMs: check.timeoutMs } : {}),
      ...lineage(key, attempts), required: false,
    });
    attempts[key] = result.attemptId;
    results.push({ name: check.name, ...result });
  }
  return results;
}

export async function run(context: WorkflowContext, raw: Record<string, unknown>) {
  const inputs = raw as RecipeInputs;
  checkInputs(inputs);
  const safe = <T>(action: () => Promise<T>) => stable(context, action, inputs.snapshot);
  let request = requestText(inputs);
  const attempts = { ...inputs.priorAttempts };
  const phases = inputs.agents ?? {};
  const skipped: string[] = [];
  if (inputs.planning) {
    const key = 'change/planning';
    const result = await structured(context, key, { ...phases.planning, ...lineage(key, attempts), purpose: 'report', permissions: 'read-only', context: request, output: summaryOutput }, attempts, inputs.snapshot);
    request = JSON.stringify({ request, planning: result.value });
  } else skipped.push('planning');
  const implementationKey = 'change/implementation';
  let candidate: Summary = { summary: 'Implementation explicitly skipped; inspect current worktree.' };
  if (inputs.implement !== false) {
    const result = await structured(context, implementationKey, { ...phases.implementation, ...lineage(implementationKey, attempts), purpose: 'implementation', permissions: 'workspace-write', context: request, output: summaryOutput }, attempts, inputs.snapshot);
    candidate = result.value;
  } else skipped.push('implementation');
  if (!inputs.browserVerification?.enabled) skipped.push('agent-browser-verification');
  if (inputs.review === false) skipped.push('review');
  for (let correction = 0; ; correction++) {
    // Every writer has settled before checks; all review operations settle before any repair starts.
    const verified = await checks(context, 'change', inputs.checks ?? [], attempts);
    const findings = verified.filter(result => result.exitCode !== 0).map(result => `Check ${result.name} exited ${result.exitCode}; attempt ${result.attemptId}`);
    if (!findings.length && inputs.browserVerification?.enabled) {
      const key = 'change/browser-verification';
      const result = await safe(() => structured(context, key, { ...inputs.browserVerification?.agent, ...lineage(key, attempts), purpose: 'review', permissions: 'read-only', context: JSON.stringify({ request, candidate, verified }), output: reviewOutput }, attempts, inputs.snapshot));
      findings.push(...result.value.findings);
    }
    if (!findings.length && inputs.review !== false) {
      const key = 'change/review';
      const result = await safe(() => structured(context, key, { ...phases.review, ...lineage(key, attempts), purpose: 'review', permissions: 'read-only', context: JSON.stringify({ request, candidate, verified }), output: reviewOutput }, attempts, inputs.snapshot));
      findings.push(...result.value.findings);
    }
    if (!findings.length) return { status: 'complete', candidateFingerprint: await candidateFingerprint(context.worktree, inputs.snapshot), candidate, checks: verified, corrections: correction, skipped, priorAttempts: attempts };
    if (inputs.implement === false) throw new Error(`selected checks/review failed with implementation disabled: ${JSON.stringify(findings)}`);
    if (correction >= 2) throw new Error(`quality correction allowance exhausted: ${JSON.stringify(findings)}`);
    const result = await structured(context, implementationKey, {
      ...phases.implementation, ...phases.repair, purpose: 'implementation', permissions: 'workspace-write',
      intent: 'code_correction', priorAttemptId: attempts[implementationKey]!,
      context: JSON.stringify({ request, candidate, findings, checks: verified }), output: summaryOutput,
    }, attempts, inputs.snapshot);
    candidate = result.value;
  }
}
