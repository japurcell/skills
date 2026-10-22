import type { RepositoryStore } from './store.js';
import { createHash } from 'node:crypto';
import { execFile as execFileCallback } from 'node:child_process';
import { constants } from 'node:fs';
import { lstat, open, realpath } from 'node:fs/promises';
import { isAbsolute, join } from 'node:path';
import { isDeepStrictEqual, promisify } from 'node:util';

/** Read-only, deliberately small view of retained history for explicit workflows. */
export interface SourceHistoryGateway {
  read(invocationId: string, afterAttempt?: number, afterCapture?: number): Promise<{
    invocation: { id: string; outcome: string | null; stage: string; workflow: string | null };
    attempts: { id: string; invocationId: string; outcome: string | null; operationKey: string }[];
    captures: { id: string; attemptId: string | null; channel: string | null; state: string }[];
    attemptsNextCursor: number; hasMoreAttempts: boolean;
    capturesNextCursor: number; hasMoreCaptures: boolean;
  }>;
  capture(invocationId: string, captureId: string, after?: number, byteBudget?: number): Promise<{
    id: string; channel: string | null; state: string; chunks: { sequence: number; text: string }[];
    nextSequence: number; hasMore: boolean;
  }>;
  event(cursor: string): Promise<{ cursor: string; kind: string; data: object } | null>;
  attempt(attemptId: string): Promise<{
    id: string; invocationId: string; operationKey: string; kind: string; outcome: string | null;
    agent: { inputsCaptureId: string; resultCaptureId: string; validatedResultCaptureId?: string; validator: string | null } | null;
  }>;
}

const id = (value: string) => {
  if (typeof value !== 'string' || !value || Buffer.byteLength(value) > 256 || value.includes('\0')) throw new Error('invalid source reference');
  return value;
};

/** No store, database, mutation, or unrestricted history enumeration escapes this port. */
export function sourceHistoryGateway(store: RepositoryStore, track: <T>(action: () => Promise<T>) => Promise<T>): SourceHistoryGateway {
  return Object.freeze({
    read: (invocationId: string, afterAttempt = 0, afterCapture = 0) => track(async () => {
      const page = store.readHistory(id(invocationId), { afterAttempt, afterCapture, limit: 20 });
      return {
        invocation: { id: page.invocation.id, outcome: page.invocation.outcome, stage: page.invocation.stage,
          workflow: typeof (page.invocation.metadata as { workflow?: unknown } | undefined)?.workflow === 'string'
            && Buffer.byteLength((page.invocation.metadata as { workflow: string }).workflow) <= 512
            ? (page.invocation.metadata as { workflow: string }).workflow : null },
        attempts: page.attempts.map(({ id, invocationId, outcome, operationKey }) => ({ id, invocationId, outcome, operationKey })),
        captures: page.captures.map(({ id, attemptId, channel, state }) => ({ id, attemptId, channel, state })),
        attemptsNextCursor: page.attemptsNextCursor, hasMoreAttempts: page.hasMoreAttempts,
        capturesNextCursor: page.capturesNextCursor, hasMoreCaptures: page.hasMoreCaptures,
      };
    }),
    capture: (invocationId: string, captureId: string, after = 0, byteBudget = 32768) => track(async () => {
      if (!Number.isSafeInteger(byteBudget) || byteBudget < 1 || byteBudget > 32768) throw new Error('invalid source capture budget');
      const request = { invocationId: id(invocationId), id: id(captureId), after, limit: 20, byteBudget };
      return store.readInvocationCapture(request);
    }),
    event: (cursor: string) => track(async () => {
      if (typeof cursor !== 'string' || !/^[1-9]\d{0,18}$/.test(cursor) || BigInt(cursor) > 9223372036854775807n) throw new Error('invalid source event cursor');
      const page = store.readEvents({ after: String(BigInt(cursor) - 1n), limit: 1 });
      return page.events[0]?.cursor === cursor ? page.events[0] : null;
    }),
    attempt: (attemptId: string) => track(async () => {
      const attempt = store.readAttempt(id(attemptId));
      return { id: attempt.id, invocationId: attempt.invocationId, operationKey: attempt.operationKey,
        kind: attempt.kind, outcome: attempt.outcome,
        agent: attempt.agent ? { inputsCaptureId: attempt.agent.inputsCaptureId,
          resultCaptureId: attempt.agent.resultCaptureId,
          ...(attempt.agent.validatedResultCaptureId ? { validatedResultCaptureId: attempt.agent.validatedResultCaptureId } : {}),
          validator: attempt.agent.validator } : null };
    }),
  });
}

const execFile = promisify(execFileCallback);
const digest = (value: string | Buffer) => createHash('sha256').update(value).digest('hex');
const hex = (value: unknown): value is string => typeof value === 'string' && /^[0-9a-f]{64}$/.test(value);
const revision = (value: unknown): value is string => typeof value === 'string' && /^[0-9a-f]{40}(?:[0-9a-f]{24})?$/.test(value);
const named = (value: unknown): value is string => typeof value === 'string' && !!value.trim()
  && !value.includes('\0') && Buffer.byteLength(value) <= 256;
const object = (value: unknown): value is Record<string, unknown> => !!value && typeof value === 'object' && !Array.isArray(value);
const targetPath = (value: unknown): value is string => typeof value === 'string' && Buffer.byteLength(value) <= 512
  && value.split('/').every(part => /^[A-Za-z0-9._-]+$/.test(part) && part !== '.' && part !== '..');
function immutable<T>(value: T): T {
  if (value && typeof value === 'object') {
    for (const child of Object.values(value)) immutable(child);
    Object.freeze(value);
  }
  return value;
}

export interface LearningReference { invocationId: string; captureId: string; sha256: string }
export interface ProposalReference { invocationId: string; proposalKey: string }
export interface EvaluationReference { invocationId: string; reportCaptureId: string; sha256: string }
export interface AdoptionApproval {
  reference: string;
  extraction: ProposalReference;
  evaluation: EvaluationReference;
  candidate: LearningReference;
  target: { repository: string; scope: 'repository'; path: string; expectedRevision: string; expectedSha256: string };
}
export interface TargetObservation { revision: string; sha256: string }
export interface AdoptionPreparation {
  kind: 'adoption-preparation'; approval: AdoptionApproval;
  evidence: { extractionReport: { captureId: string; sha256: string }; extractionResult: {
    attemptId: string; rawCaptureId: string; validatedCaptureId: string } };
  expected: TargetObservation;
}
export interface ActionEvidence { reference: string; status: 'succeeded' | 'failed' | 'uncertain' }
export type AdoptionOutcome = { kind: 'adoption'; status: 'not_applied' | 'uncertain'; approval: AdoptionApproval;
  evidence: AdoptionPreparation['evidence']; action: ActionEvidence; observed: TargetObservation | null; reason: string }
  | { kind: 'adoption'; status: 'applied'; approval: AdoptionApproval; evidence: AdoptionPreparation['evidence'];
    action: ActionEvidence; applied: TargetObservation };
export interface RevertPreparation { kind: 'revert-preparation'; originalAdoption: Extract<AdoptionOutcome, { status: 'applied' }>;
  approvalReference: string; expected: TargetObservation }
export type RevertOutcome = { kind: 'revert'; status: 'not_reverted' | 'uncertain'; originalAdoption: RevertPreparation['originalAdoption'];
  approvalReference: string; action: ActionEvidence; observed: TargetObservation | null; reason: string }
  | { kind: 'revert'; status: 'reverted'; originalAdoption: RevertPreparation['originalAdoption'];
    approvalReference: string; action: ActionEvidence; reverted: TargetObservation };

function validReference(value: unknown): value is LearningReference {
  return object(value) && named(value.invocationId) && named(value.captureId) && hex(value.sha256);
}

function validateApproval(value: AdoptionApproval): void {
  if (!object(value) || !named(value.reference) || !object(value.extraction)
    || !named(value.extraction.invocationId) || !named(value.extraction.proposalKey)
    || !object(value.evaluation) || !named(value.evaluation.invocationId)
    || !named(value.evaluation.reportCaptureId) || !hex(value.evaluation.sha256)
    || !validReference(value.candidate) || !object(value.target)
    || typeof value.target.repository !== 'string' || !isAbsolute(value.target.repository)
    || value.target.scope !== 'repository' || !targetPath(value.target.path)
    || !revision(value.target.expectedRevision) || !hex(value.target.expectedSha256))
    throw new Error('adoption requires exact human approval, proposal, evaluation, candidate and repository target references');
}

/** A retained capture is evidence only when its complete bytes and invocation ownership are observed. */
async function retainedText(history: SourceHistoryGateway, invocationId: string, captureId: string,
  channel: string, limit = 131072, requireSuccess = true): Promise<string> {
  let cursor = 0, found = false, more = false;
  for (let page = 0; page < 8; page++) {
    const result = await history.read(invocationId, 0, cursor);
    if (result.invocation.stage !== 'finalized' || (requireSuccess && result.invocation.outcome !== 'succeeded'))
      throw new Error('adoption reference invocation is not successfully finalized');
    const header = result.captures.find(item => item.id === captureId);
    if (header) {
      if (header.channel !== channel || header.state !== 'complete') throw new Error('adoption capture is not complete in required channel');
      found = true; break;
    }
    more = result.hasMoreCaptures;
    if (!more || result.capturesNextCursor === cursor) break;
    cursor = result.capturesNextCursor;
  }
  if (!found) throw new Error(more ? 'adoption capture remains unexamined' : 'adoption capture missing or foreign');
  let after = 0, text = '', hasMore = true;
  for (let page = 0; page < Math.ceil(limit / 32768) + 4 && hasMore; page++) {
    const capture = await history.capture(invocationId, captureId, after, 32768);
    if (capture.channel !== channel || capture.state !== 'complete') throw new Error('adoption capture became unavailable');
    for (const chunk of capture.chunks) text += chunk.text;
    if (Buffer.byteLength(text) > limit) throw new Error('adoption capture exceeds bounded evidence limit');
    if (capture.hasMore && capture.nextSequence === after) throw new Error('adoption capture has unexamined text');
    after = capture.nextSequence; hasMore = capture.hasMore;
  }
  if (hasMore) throw new Error('adoption capture has unexamined text');
  return text;
}

type RetainedHeader = Awaited<ReturnType<SourceHistoryGateway['read']>>['captures'][number];
async function producerCaptures(history: SourceHistoryGateway, invocationId: string, workflow: string): Promise<Map<string, RetainedHeader>> {
  const captures = new Map<string, RetainedHeader>();
  let cursor = 0;
  for (let page = 0; page < 8; page++) {
    const result = await history.read(invocationId, 0, cursor);
    if (result.invocation.id !== invocationId || result.invocation.workflow !== workflow
      || result.invocation.stage !== 'finalized' || result.invocation.outcome !== 'succeeded')
      throw new Error('adoption evidence producer is not verified');
    for (const header of result.captures) captures.set(header.id, header);
    if (!result.hasMoreCaptures) return captures;
    if (result.capturesNextCursor === cursor) break;
    cursor = result.capturesNextCursor;
  }
  throw new Error('adoption producer captures remain unexamined');
}
function requireEvidence(condition: unknown): asserts condition {
  if (!condition) throw new Error('adoption retained evidence relationships are not verified');
}
function parseEvidence(text: string): Record<string, unknown> {
  const value: unknown = JSON.parse(text);
  requireEvidence(object(value));
  return value;
}

/** Verify the retained attempt and each of its owned raw, normalized and input captures. */
async function agentEvidence(history: SourceHistoryGateway, invocationId: string, headers: Map<string, RetainedHeader>,
  attemptId: string, operation: string, validator: string) {
  const attempt = await history.attempt(attemptId);
  requireEvidence(attempt.id === attemptId && attempt.invocationId === invocationId && attempt.kind === 'agent'
    && attempt.outcome === 'succeeded' && attempt.operationKey === operation && attempt.agent?.validator === validator);
  const agent = attempt.agent;
  requireEvidence(agent && named(agent.validatedResultCaptureId));
  const text = async (captureId: string, channel: string, limit?: number) => {
    const header = headers.get(captureId);
    requireEvidence(header?.attemptId === attemptId && header.channel === channel && header.state === 'complete');
    return retainedText(history, invocationId, captureId, channel, limit);
  };
  await text(agent.resultCaptureId, 'result');
  const result = parseEvidence(await text(agent.validatedResultCaptureId, 'validated-result'));
  requireEvidence(result.kind === 'result' && object(result.payload));
  const inputs = parseEvidence(await text(agent.inputsCaptureId, 'context', 393216));
  requireEvidence(object(inputs.inputs) && typeof inputs.context === 'string');
  return { agent, payload: result.payload, inputs, context: parseEvidence(inputs.context) };
}

async function verifyProvenance(history: SourceHistoryGateway, approval: AdoptionApproval, report: Record<string, unknown>): Promise<void> {
  const evaluationHeaders = await producerCaptures(history, approval.evaluation.invocationId, '.factory/workflows/evaluate.ts');
  requireEvidence(evaluationHeaders.get(approval.evaluation.reportCaptureId)?.attemptId === null);
  const extractionHeaders = await producerCaptures(history, approval.extraction.invocationId, '.factory/workflows/learn.ts');
  const reportRef = report.extractionReport as AdoptionPreparation['evidence']['extractionReport'];
  const resultRef = report.extractionResult as AdoptionPreparation['evidence']['extractionResult'];
  requireEvidence([...extractionHeaders.values()].filter(item => item.channel === 'report').length === 1
    && extractionHeaders.get(reportRef.captureId)?.attemptId === null);
  const extractionText = await retainedText(history, approval.extraction.invocationId, reportRef.captureId, 'report');
  requireEvidence(digest(extractionText) === reportRef.sha256);
  const extraction = parseEvidence(extractionText);
  const extracted = await agentEvidence(history, approval.extraction.invocationId, extractionHeaders,
    resultRef.attemptId, 'learn/extract', 'learning-extraction-v1');
  requireEvidence(extraction.version === 1 && extraction.proposalResultCaptureId === resultRef.rawCaptureId
    && extraction.proposalValidatedResultCaptureId === resultRef.validatedCaptureId
    && extracted.agent.resultCaptureId === resultRef.rawCaptureId
    && extracted.agent.validatedResultCaptureId === resultRef.validatedCaptureId
    && Array.isArray(extraction.proposals) && isDeepStrictEqual(extraction.proposals, extracted.payload.proposals)
    && Array.isArray(extraction.suppliedSources) && Array.isArray(extraction.examinedSources)
    && Array.isArray(extracted.context.evidence) && extracted.context.evidence.length > 0
    && extracted.context.evidence.length <= 6 && extracted.inputs.purpose === 'report'
    && Array.isArray(extracted.context.captureLimitations) && extracted.context.captureLimitations.length === 0
    && isDeepStrictEqual(extraction.captureLimitations, extracted.context.captureLimitations));
  const examined: { invocationId: string; outcome: unknown; attemptIds: string[]; eventCursors: string[]; captureIds: string[] }[] = [];
  for (const source of extracted.context.evidence) {
    requireEvidence(object(source) && named(source.invocationId) && Array.isArray(source.attempts)
      && Array.isArray(source.events) && Array.isArray(source.captures));
    const page = await history.read(source.invocationId);
    requireEvidence(page.invocation.id === source.invocationId && page.invocation.stage === 'finalized'
      && page.invocation.outcome === source.outcome);
    for (const entry of source.attempts) {
      requireEvidence(object(entry) && named(entry.id));
      const actual = await history.attempt(entry.id);
      requireEvidence(actual.invocationId === source.invocationId && actual.operationKey === entry.operationKey && actual.outcome === entry.outcome);
    }
    for (const entry of source.events) {
      requireEvidence(object(entry) && named(entry.cursor));
      const actual = await history.event(entry.cursor);
      requireEvidence(actual && actual.kind === entry.kind && isDeepStrictEqual(actual.data, entry.data));
    }
    for (const entry of source.captures) {
      requireEvidence(object(entry) && named(entry.id) && typeof entry.channel === 'string' && Array.isArray(entry.chunks));
      // Extraction may retain a prefix; require that prefix still matches complete retained bytes.
      const actual = await retainedText(history, source.invocationId, entry.id, entry.channel, 131072, false);
      requireEvidence(entry.state === 'complete' && entry.chunks.every((chunk: unknown) => object(chunk) && typeof chunk.text === 'string'));
      requireEvidence(actual.startsWith(entry.chunks.map((chunk: { text: string }) => chunk.text).join('')));
    }
    examined.push({ invocationId: source.invocationId, outcome: source.outcome,
      attemptIds: source.attempts.map((entry: { id: string }) => entry.id),
      eventCursors: source.events.map((entry: { cursor: string }) => entry.cursor),
      captureIds: source.captures.filter((entry: { chunks: unknown[] }) => entry.chunks.length > 0).map((entry: { id: string }) => entry.id) });
  }
  requireEvidence(isDeepStrictEqual(extraction.examinedSources, examined)
    && extraction.suppliedSources.length === examined.length
    && extraction.suppliedSources.every((source, index) => object(source) && source.invocationId === examined[index]!.invocationId
      && (source.attemptIds === undefined || isDeepStrictEqual(source.attemptIds, examined[index]!.attemptIds))
      && (source.eventCursors === undefined || isDeepStrictEqual(source.eventCursors, examined[index]!.eventCursors))));
  const proposals = extraction.proposals.filter(item => object(item) && item.key === approval.extraction.proposalKey);
  requireEvidence(proposals.length === 1);
  const selected = proposals[0] as Record<string, unknown>;
  requireEvidence(isDeepStrictEqual(selected.target, report.target) && object(selected.candidateCapture)
    && selected.candidateCapture.invocationId === approval.candidate.invocationId
    && selected.candidateCapture.captureId === approval.candidate.captureId
    && examined.some(source => source.invocationId === approval.candidate.invocationId && source.captureIds.includes(approval.candidate.captureId))
    && Array.isArray(selected.suggestedCases) && selected.suggestedCases.length > 0
    && isDeepStrictEqual(selected.suggestedCases, report.proposalSuggestedCases));
  const evidenceExamined = (value: unknown) => {
    if (!object(value) || !named(value.invocationId)) return false;
    const source = examined.find(item => item.invocationId === value.invocationId);
    const keys = ['attemptId', 'eventCursor', 'captureId'] as const;
    return keys.filter(key => value[key] !== undefined).length === 1 && keys.some(key =>
      named(value[key]) && source?.[`${key}s`].includes(value[key]));
  };
  requireEvidence(Array.isArray(selected.supportingEvidence) && selected.supportingEvidence.length > 0
    && selected.supportingEvidence.length <= 16 && selected.supportingEvidence.every(evidenceExamined)
    && Array.isArray(selected.contraryEvidence) && selected.contraryEvidence.length <= 16
    && selected.contraryEvidence.every(evidenceExamined));
  const refs = report.suppliedReferences as Record<string, unknown>;
  requireEvidence(validReference(refs.baseline));
  requireEvidence(digest(await retainedText(history, refs.baseline.invocationId, refs.baseline.captureId, 'event')) === approval.target.expectedSha256);
  requireEvidence(Array.isArray(report.cases) && report.cases.length > 0 && report.cases.length <= 3);
  let improvement = false;
  for (const item of report.cases) {
    requireEvidence(object(item) && named(item.key) && object(item.settings) && item.settings.repetitions === 2);
    for (const variant of ['baseline', 'candidate'] as const) {
      const side = item[variant];
      requireEvidence(object(side) && Array.isArray(side.objective) && side.objective.length === 2 && object(side.review));
      requireEvidence(new Set(side.objective.map((entry: Record<string, unknown>) => entry.exitCode)).size === 1);
      const success = variant === 'candidate' || side.objective.every(entry => object(entry) && entry.exitCode === 0);
      if (!success) improvement = true;
      for (const [index, entry] of side.objective.entries()) {
        requireEvidence(object(entry) && named(entry.attemptId) && Number.isInteger(entry.exitCode) && entry.cleanup === 'complete'
          && (entry.exitCode === 0) === success);
        const attempt = await history.attempt(entry.attemptId);
        requireEvidence(attempt.invocationId === approval.evaluation.invocationId && attempt.kind === 'command'
          && attempt.operationKey === `evaluate/${item.key}/${variant}/objective/${index + 1}`
          && attempt.outcome === (success ? 'succeeded' : 'failed'));
        const inputs = [...evaluationHeaders.values()].filter(header => header.attemptId === attempt.id && header.channel === 'context');
        requireEvidence(inputs.length === 1);
        const command = parseEvidence(await retainedText(history, approval.evaluation.invocationId, inputs[0]!.id, 'context'));
        requireEvidence(isDeepStrictEqual(command.argv, item.settings.argv) && command.cwd === item.settings.cwd
          && command.timeoutMs === item.settings.timeoutMs && command.required === false && command.shell === false);
      }
      requireEvidence(named(side.review.attemptId));
      const review = await agentEvidence(history, approval.evaluation.invocationId, evaluationHeaders,
        side.review.attemptId, `evaluate/${item.key}/${variant}/review`, 'learning-evaluation-review-v1');
      requireEvidence(review.agent.resultCaptureId === side.review.resultCaptureId && review.agent.inputsCaptureId === side.review.inputsCaptureId
        && review.payload.judgment === (success ? 'pass' : 'fail') && review.payload.judgment === side.review.judgment
        && review.payload.reason === side.review.reason && object(review.inputs.inputs) && review.inputs.inputs.permissions === 'read-only'
        && side.review.effectiveProfile === (review.inputs.inputs.profile ?? null)
        && side.review.effectivePermissions === 'read-only' && review.inputs.purpose === 'review'
        && review.context.variant === variant && review.context.caseKey === item.key && review.context.criteria === item.criteria
        && isDeepStrictEqual(review.context.target, report.target) && isDeepStrictEqual(review.context.objective, side.objective)
        && typeof review.context.text === 'string' && digest(review.context.text) === (variant === 'baseline' ? approval.target.expectedSha256 : approval.candidate.sha256));
    }
  }
  requireEvidence(improvement && selected.suggestedCases.every(suggestion => (report.cases as Record<string, unknown>[]).some(item => item.sourceSuggestion === suggestion)));
}

async function git(root: string, args: string[]): Promise<string> {
  const { stdout } = await execFile('git', ['-C', root, ...args], { encoding: 'utf8', maxBuffer: 1048576 });
  return stdout;
}

/** Read the committed target and the current file; a dirty or linked path is not an exact revision. */
async function observeTarget(repository: string, path: string): Promise<TargetObservation> {
  const root = await realpath(repository);
  if ((await git(root, ['rev-parse', '--show-toplevel'])).trim() !== root)
    throw new Error('adoption repository must be the selected Git worktree root');
  let part = root;
  for (const component of path.split('/')) {
    part = join(part, component);
    const stat = await lstat(part);
    if (stat.isSymbolicLink()) throw new Error('adoption target contains a symbolic link');
  }
  if (await realpath(part) !== part) throw new Error('adoption target path changed during observation');
  const before = await lstat(part);
  const file = await open(part, constants.O_RDONLY | (constants.O_NOFOLLOW ?? 0));
  let bytes: Buffer;
  try {
    const stat = await file.stat();
    if (!stat.isFile() || stat.size > 131072 || stat.dev !== before.dev || stat.ino !== before.ino)
      throw new Error('adoption target is not a stable bounded regular file');
    bytes = await file.readFile();
    if (bytes.length !== stat.size) throw new Error('adoption target changed during observation');
    const after = await lstat(part);
    if (after.dev !== stat.dev || after.ino !== stat.ino || after.size !== stat.size
      || after.mtimeMs !== stat.mtimeMs || after.ctimeMs !== stat.ctimeMs)
      throw new Error('adoption target changed during observation');
  } finally { await file.close(); }
  const head = (await git(root, ['rev-parse', 'HEAD'])).trim();
  if (!revision(head)) throw new Error('adoption target revision is invalid');
  if ((await git(root, ['status', '--porcelain', '--', path])).trim())
    throw new Error('adoption target has uncommitted changes');
  const committed = await git(root, ['show', `HEAD:${path}`]);
  if (digest(committed) !== digest(bytes)) throw new Error('adoption target differs from committed revision');
  return { revision: head, sha256: digest(bytes) };
}

async function scopedRevision(repository: string, before: string, after: string, path: string): Promise<boolean> {
  if (before === after) return false;
  const root = await realpath(repository);
  const lineage = (await git(root, ['rev-list', '--parents', '-n', '1', after])).trim().split(' ');
  if (lineage.length !== 2 || lineage[0] !== after || lineage[1] !== before) return false;
  const changed = (await git(root, ['diff', '--name-only', '-z', '--no-renames', before, after])).split('\0').filter(Boolean);
  return changed.length === 1 && changed[0] === path;
}

/** Approval is supplied separately from the action; this step only prepares exact, observed evidence. */
export async function prepareAdoption(history: SourceHistoryGateway, approval: AdoptionApproval): Promise<AdoptionPreparation> {
  approval = structuredClone(approval);
  validateApproval(approval);
  const evaluationText = await retainedText(history, approval.evaluation.invocationId, approval.evaluation.reportCaptureId, 'report');
  if (digest(evaluationText) !== approval.evaluation.sha256) throw new Error('approved evaluation report bytes changed');
  let report: unknown;
  try { report = JSON.parse(evaluationText); } catch { throw new Error('approved evaluation report is invalid'); }
  if (!object(report) || report.version !== 1 || report.assessment !== 'supported'
    || !Array.isArray(report.limitations) || report.limitations.length !== 0
    || !object(report.suppliedReferences) || !object(report.suppliedReferences.extraction)
    || report.suppliedReferences.extraction.invocationId !== approval.extraction.invocationId
    || report.suppliedReferences.extraction.proposalKey !== approval.extraction.proposalKey
    || !object(report.suppliedReferences.baseline)
    || report.suppliedReferences.baseline.sha256 !== approval.target.expectedSha256
    || !object(report.suppliedReferences.candidate)
    || report.suppliedReferences.candidate.invocationId !== approval.candidate.invocationId
    || report.suppliedReferences.candidate.captureId !== approval.candidate.captureId
    || report.suppliedReferences.candidate.sha256 !== approval.candidate.sha256
    || !object(report.target) || report.target.scope !== approval.target.scope || report.target.path !== approval.target.path
    || !object(report.resolved) || report.resolved.baselineSha256 !== approval.target.expectedSha256
    || report.resolved.candidateSha256 !== approval.candidate.sha256
    || !object(report.extractionReport) || !named(report.extractionReport.captureId) || !hex(report.extractionReport.sha256)
    || !object(report.extractionResult) || !named(report.extractionResult.attemptId)
    || !named(report.extractionResult.rawCaptureId) || !named(report.extractionResult.validatedCaptureId))
    throw new Error('approval differs from a supported exact evaluation and proposal');
  await verifyProvenance(history, approval, report);
  const candidate = await retainedText(history, approval.candidate.invocationId, approval.candidate.captureId, 'event');
  if (digest(candidate) !== approval.candidate.sha256) throw new Error('approved candidate bytes changed');
  const observed = await observeTarget(approval.target.repository, approval.target.path);
  if (observed.revision !== approval.target.expectedRevision || observed.sha256 !== approval.target.expectedSha256)
    throw new Error('approved target revision or content changed; renewed review required');
  return immutable({ kind: 'adoption-preparation', approval: structuredClone(approval), evidence: {
    extractionReport: { captureId: report.extractionReport.captureId as string, sha256: report.extractionReport.sha256 as string },
    extractionResult: { attemptId: report.extractionResult.attemptId as string,
      rawCaptureId: report.extractionResult.rawCaptureId as string, validatedCaptureId: report.extractionResult.validatedCaptureId as string },
  }, expected: observed });
}

function validateEvidence(value: AdoptionPreparation['evidence']): void {
  if (!object(value) || !object(value.extractionReport) || !named(value.extractionReport.captureId)
    || !hex(value.extractionReport.sha256) || !object(value.extractionResult)
    || !named(value.extractionResult.attemptId) || !named(value.extractionResult.rawCaptureId)
    || !named(value.extractionResult.validatedCaptureId)) throw new Error('invalid adoption preparation evidence');
}

function validatePreparation(prepared: AdoptionPreparation): void {
  if (!object(prepared) || prepared.kind !== 'adoption-preparation') throw new Error('invalid adoption preparation');
  validateApproval(prepared.approval);
  validateEvidence(prepared.evidence);
  if (!object(prepared.expected) || prepared.expected.revision !== prepared.approval.target.expectedRevision
    || prepared.expected.sha256 !== prepared.approval.target.expectedSha256)
    throw new Error('adoption preparation differs from approved target');
}

async function historicalTarget(repository: string, commit: string, path: string, sha256: string): Promise<boolean> {
  return digest(await git(repository, ['show', `${commit}:${path}`])) === sha256;
}

async function validateApplied(original: Extract<AdoptionOutcome, { status: 'applied' }>): Promise<void> {
  validateApproval(original.approval);
  validateEvidence(original.evidence);
  const target = original.approval.target;
  if (original.kind !== 'adoption' || original.status !== 'applied'
    || !revision(original.applied?.revision) || original.applied.sha256 !== original.approval.candidate.sha256
    || original.action?.status !== 'succeeded' || !named(original.action.reference)
    || !await scopedRevision(target.repository, target.expectedRevision, original.applied.revision, target.path)
    || !await historicalTarget(target.repository, target.expectedRevision, target.path, target.expectedSha256)
    || !await historicalTarget(target.repository, original.applied.revision, target.path, original.applied.sha256))
    throw new Error('revert requires a valid observed adoption record');
}

/** A successful action result alone cannot claim application; the target commit and bytes must agree. */
export async function confirmAdoption(prepared: AdoptionPreparation, action: ActionEvidence): Promise<AdoptionOutcome> {
  prepared = structuredClone(prepared); action = structuredClone(action);
  validatePreparation(prepared);
  if (!named(action?.reference) || !['succeeded', 'failed', 'uncertain'].includes(action.status)) throw new Error('invalid adoption action evidence');
  const common = { kind: 'adoption' as const, approval: prepared.approval, evidence: prepared.evidence, action };
  let observed: TargetObservation | null = null;
  try { observed = await observeTarget(prepared.approval.target.repository, prepared.approval.target.path); }
  catch { return { ...common, status: 'uncertain', observed, reason: 'target observation unavailable' }; }
  if (action.status !== 'succeeded') return { ...common, status: observed.revision === prepared.expected.revision
    && observed.sha256 === prepared.expected.sha256 ? 'not_applied' : 'uncertain', observed, reason: `action ${action.status}` };
  if (observed.revision === prepared.expected.revision && observed.sha256 === prepared.expected.sha256)
    return { ...common, status: 'not_applied', observed, reason: 'target revision and content unchanged' };
  let scoped = false;
  try { scoped = await scopedRevision(prepared.approval.target.repository, prepared.approval.target.expectedRevision,
    observed.revision, prepared.approval.target.path)
      && await historicalTarget(prepared.approval.target.repository, prepared.approval.target.expectedRevision,
        prepared.approval.target.path, prepared.approval.target.expectedSha256); } catch { /* Observation failures remain uncertain. */ }
  if (observed.sha256 !== prepared.approval.candidate.sha256 || !scoped)
    return { ...common, status: 'uncertain', observed, reason: 'actual commit does not contain only the approved candidate target' };
  return { ...common, status: 'applied', applied: observed };
}

export async function prepareRevert(originalAdoption: AdoptionOutcome, approval: { reference: string }): Promise<RevertPreparation> {
  if (!originalAdoption || originalAdoption.status !== 'applied' || !named(approval?.reference))
    throw new Error('revert requires applied adoption and explicit approval');
  originalAdoption = structuredClone(originalAdoption); approval = structuredClone(approval);
  await validateApplied(originalAdoption);
  const observed = await observeTarget(originalAdoption.approval.target.repository, originalAdoption.approval.target.path);
  if (observed.revision !== originalAdoption.applied.revision || observed.sha256 !== originalAdoption.applied.sha256)
    throw new Error('revert target changed; renewed review required');
  return immutable({ kind: 'revert-preparation', originalAdoption: structuredClone(originalAdoption),
    approvalReference: approval.reference, expected: observed });
}

export async function confirmRevert(prepared: RevertPreparation, action: ActionEvidence): Promise<RevertOutcome> {
  prepared = structuredClone(prepared); action = structuredClone(action);
  if (!object(prepared) || prepared.kind !== 'revert-preparation' || !named(prepared.approvalReference)
    || !object(prepared.originalAdoption) || !object(prepared.expected)
    || !isDeepStrictEqual(prepared.expected, prepared.originalAdoption.applied))
    throw new Error('invalid revert preparation');
  await validateApplied(prepared.originalAdoption);
  if (!named(action?.reference) || !['succeeded', 'failed', 'uncertain'].includes(action.status)) throw new Error('invalid revert action evidence');
  const common = { kind: 'revert' as const, originalAdoption: prepared.originalAdoption,
    approvalReference: prepared.approvalReference, action };
  const target = prepared.originalAdoption.approval.target;
  let observed: TargetObservation | null = null;
  try { observed = await observeTarget(target.repository, target.path); }
  catch { return { ...common, status: 'uncertain', observed, reason: 'target observation unavailable' }; }
  if (action.status !== 'succeeded') return { ...common, status: observed.revision === prepared.expected.revision
    && observed.sha256 === prepared.expected.sha256 ? 'not_reverted' : 'uncertain', observed, reason: `action ${action.status}` };
  if (observed.revision === prepared.expected.revision && observed.sha256 === prepared.expected.sha256)
    return { ...common, status: 'not_reverted', observed, reason: 'target revision and content unchanged' };
  let scoped = false;
  try { scoped = await scopedRevision(target.repository, prepared.originalAdoption.applied.revision, observed.revision, target.path); }
  catch { /* Observation failures remain uncertain. */ }
  if (observed.sha256 !== target.expectedSha256 || !scoped)
    return { ...common, status: 'uncertain', observed, reason: 'actual revert commit does not restore only the original target' };
  return { ...common, status: 'reverted', reverted: observed };
}
