import type { RepositoryStore } from './store.js';
import { createHash } from 'node:crypto';
import { execFile as execFileCallback } from 'node:child_process';
import { constants } from 'node:fs';
import { lstat, open, realpath } from 'node:fs/promises';
import { isAbsolute, join } from 'node:path';
import { promisify } from 'node:util';

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
  channel: string, limit = 131072): Promise<string> {
  let cursor = 0, found = false, more = false;
  for (let page = 0; page < 8; page++) {
    const result = await history.read(invocationId, 0, cursor);
    if (result.invocation.stage !== 'finalized' || result.invocation.outcome !== 'succeeded')
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
  for (let page = 0; page < 8 && hasMore; page++) {
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

/** A successful action result alone cannot claim application; the target commit and bytes must agree. */
export async function confirmAdoption(prepared: AdoptionPreparation, action: ActionEvidence): Promise<AdoptionOutcome> {
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
  try { scoped = await scopedRevision(prepared.approval.target.repository, prepared.expected.revision,
    observed.revision, prepared.approval.target.path); } catch { /* Observation failures remain uncertain. */ }
  if (observed.sha256 !== prepared.approval.candidate.sha256 || !scoped)
    return { ...common, status: 'uncertain', observed, reason: 'actual commit does not contain only the approved candidate target' };
  return { ...common, status: 'applied', applied: observed };
}

export async function prepareRevert(originalAdoption: AdoptionOutcome, approval: { reference: string }): Promise<RevertPreparation> {
  if (!originalAdoption || originalAdoption.status !== 'applied' || !named(approval?.reference))
    throw new Error('revert requires applied adoption and explicit approval');
  validateApproval(originalAdoption.approval);
  if (!revision(originalAdoption.applied?.revision) || !hex(originalAdoption.applied?.sha256)
    || originalAdoption.applied.sha256 !== originalAdoption.approval.candidate.sha256
    || originalAdoption.action?.status !== 'succeeded' || !named(originalAdoption.action.reference))
    throw new Error('revert requires a valid observed adoption record');
  const observed = await observeTarget(originalAdoption.approval.target.repository, originalAdoption.approval.target.path);
  if (observed.revision !== originalAdoption.applied.revision || observed.sha256 !== originalAdoption.applied.sha256)
    throw new Error('revert target changed; renewed review required');
  return immutable({ kind: 'revert-preparation', originalAdoption: structuredClone(originalAdoption),
    approvalReference: approval.reference, expected: observed });
}

export async function confirmRevert(prepared: RevertPreparation, action: ActionEvidence): Promise<RevertOutcome> {
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
  try { scoped = await scopedRevision(target.repository, prepared.expected.revision, observed.revision, target.path); }
  catch { /* Observation failures remain uncertain. */ }
  if (observed.sha256 !== target.expectedSha256 || !scoped)
    return { ...common, status: 'uncertain', observed, reason: 'actual revert commit does not restore only the original target' };
  return { ...common, status: 'reverted', reverted: observed };
}
