import type { WorkflowContext } from '@local/software-factory';
import { candidateFingerprint, checkInputs, checks, lineage, requestText, reviewOutput, stable, structured, summaryOutput } from './change.js';
import type { Phase, RecipeInputs, Summary } from './change.js';

export interface AuditInputs extends Omit<RecipeInputs, 'implement' | 'agents'> {
  scopes: { name: string; target: string; questions?: string; skip?: boolean; agent?: Phase }[];
  synthesis?: boolean;
  agents?: { planning?: Phase; investigation?: Phase; synthesis?: Phase; review?: Phase; repair?: Phase };
}
/** Investigation targets are explicit context (refs, paths, questions), never implementation tasks or checkout instructions. */
export async function run(context: WorkflowContext, raw: Record<string, unknown>) {
  const inputs = raw as unknown as AuditInputs;
  checkInputs(inputs);
  const safe = <T>(action: () => Promise<T>) => stable(context, action, inputs.snapshot);
  const request = requestText(inputs);
  if (!Array.isArray(inputs.scopes) || !inputs.scopes.length || inputs.scopes.some(scope => !scope || typeof scope !== 'object' || typeof scope.name !== 'string' || !scope.name.trim() || typeof scope.target !== 'string' || !scope.target.trim() || (scope.questions !== undefined && (typeof scope.questions !== 'string' || !scope.questions.trim())) || (scope.skip !== undefined && typeof scope.skip !== 'boolean')))
    throw new Error('audit requires explicitly named scopes and targets');
  if (new Set(inputs.scopes.map(scope => scope.name)).size !== inputs.scopes.length) throw new Error('audit scope names must be unique');
  if (inputs.synthesis !== undefined && typeof inputs.synthesis !== 'boolean') throw new Error('synthesis must be a boolean');
  const attempts = { ...inputs.priorAttempts }, phases = inputs.agents ?? {}, skipped: string[] = [];
  if (!inputs.browserVerification?.enabled) skipped.push('agent-browser-verification');
  let planning: Summary | undefined;
  if (inputs.planning) {
    const key = 'audit/planning';
    planning = (await safe(() => structured(context, key, { ...phases.planning, ...lineage(key, attempts), purpose: 'report', permissions: 'read-only', context: request, output: summaryOutput }, attempts, inputs.snapshot))).value;
  } else skipped.push('planning');
  const investigations: { name: string; target: string; result: Summary }[] = [];
  for (const scope of inputs.scopes) {
    if (scope.skip) { skipped.push(`scope:${scope.name}`); continue; }
    const key = `audit/investigation/${scope.name}`;
    const result = await safe(() => structured(context, key, { ...phases.investigation, ...scope.agent, ...lineage(key, attempts), purpose: 'report', permissions: 'read-only', context: JSON.stringify({ request, planning, scope, instruction: 'Investigate the explicit target without editing or switching the worktree.' }), output: summaryOutput }, attempts, inputs.snapshot));
    investigations.push({ name: scope.name, target: scope.target, result: result.value });
  }
  let candidate: Summary = { summary: JSON.stringify(investigations) };
  const synthesisKey = 'audit/synthesis';
  const synthesize = inputs.synthesis !== false;
  if (synthesize) candidate = (await safe(() => structured(context, synthesisKey, { ...phases.synthesis, ...lineage(synthesisKey, attempts), purpose: 'report', permissions: 'read-only', context: JSON.stringify({ request, planning, investigations }), output: summaryOutput }, attempts, inputs.snapshot))).value;
  else skipped.push('synthesis');
  if (inputs.review === false) skipped.push('review');
  for (let correction = 0; ; correction++) {
    const verified = await safe(() => checks(context, 'audit', inputs.checks ?? [], attempts));
    const findings = verified.filter(result => result.exitCode !== 0).map(result => `Check ${result.name} exited ${result.exitCode}; attempt ${result.attemptId}`);
    if (!findings.length && inputs.browserVerification?.enabled) {
      const key = 'audit/browser-verification';
      const result = await safe(() => structured(context, key, { ...inputs.browserVerification?.agent, ...lineage(key, attempts), purpose: 'review', permissions: 'read-only', context: JSON.stringify({ request, investigations, candidate, verified }), output: reviewOutput }, attempts, inputs.snapshot));
      findings.push(...result.value.findings);
    }
    if (!findings.length && inputs.review !== false) {
      const key = 'audit/review';
      const result = await safe(() => structured(context, key, { ...phases.review, ...lineage(key, attempts), purpose: 'review', permissions: 'read-only', context: JSON.stringify({ request, investigations, candidate, verified }), output: reviewOutput }, attempts, inputs.snapshot));
      findings.push(...result.value.findings);
    }
    if (!findings.length) return { status: 'complete', candidateFingerprint: await candidateFingerprint(context.worktree, inputs.snapshot), investigations, candidate, checks: verified, corrections: correction, skipped, priorAttempts: attempts };
    if (!synthesize) throw new Error(`audit findings with synthesis disabled: ${JSON.stringify(findings)}`);
    if (correction >= 2) throw new Error(`audit quality correction allowance exhausted: ${JSON.stringify(findings)}`);
    candidate = (await safe(() => structured(context, synthesisKey, {
      ...phases.synthesis, ...phases.repair, purpose: 'report', permissions: 'read-only', intent: 'code_correction', priorAttemptId: attempts[synthesisKey]!,
      context: JSON.stringify({ request, investigations, candidate, findings, verified, instruction: 'Correct only the report; do not edit the repository.' }), output: summaryOutput,
    }, attempts, inputs.snapshot))).value;
  }
}
