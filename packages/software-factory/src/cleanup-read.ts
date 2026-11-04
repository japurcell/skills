import { createHash } from 'node:crypto';

/** C1 retained facts are advisory evidence, never cleanup or recovery authority. */
export interface CleanupPageInput { after?: string; through?: string; limit?: number; byteBudget?: number }
export interface CleanupPage<T> {
  records: T[]; nextCursor: string; through: string; hasMore: boolean; blocked: 'byte-budget' | null;
}
export interface CleanupIdentity { id: string | null; cursor: string; bytes: string; sha256: string | null }
export interface CleanupOpaque extends CleanupIdentity {
  status: 'opaque'; reason: 'oversized' | 'page-budget' | 'malformed' | 'unknown-format' | 'invalid-identity';
}
export interface CleanupInvocationFact extends CleanupIdentity {
  status: 'known'; id: string; runId: string; worktreeId: string;
  stage: 'starting' | 'running' | 'shutting_down' | 'finalized'; outcome: string | null;
  inputCaptureId: string | null; question: string | null; contexts: string[];
  workflow: string | null; selectedCommit: string | null;
}
export interface CleanupAttemptFact extends CleanupIdentity {
  status: 'known'; id: string; invocationId: string; runId: string; operationId: string; operationKey: string;
  kind: 'agent' | 'command'; priorAttemptId: string | null; occupied: boolean;
  launch: 'admitted' | 'started' | 'not_started' | 'unknown'; outcome: string | null; quiescent: boolean;
  agent: { inputsCaptureId: string; resultCaptureId: string; outputCaptureId: string;
    validatedResultCaptureId: string | null; reusedAttemptId: string | null; validator: string | null } | null;
}
export interface CleanupCaptureHeader {
  status: 'known'; cursor: string; id: string; invocationId: string; attemptId: string | null;
  channel: 'stdout' | 'stderr' | 'result' | 'validated-result' | 'request' | 'report' | 'event' | 'context';
  state: 'open' | 'complete' | 'partial' | 'unknown' | 'pruned'; lastSequence: string; logicalPayloadBytes: string;
}
export interface CleanupSnapshot {
  repositoryId: string; release: string; schema: 7; databaseIdentity: string;
  highWater: { invocations: string; attempts: string; captures: string; events: string };
  recovery: { authority: 'unassessed'; repositoryState: string; claimCount: string; sha256: string | null;
    claimFacts: (CleanupOpaque | (CleanupIdentity & { status: 'known'; kind: string }))[]; opaque: boolean };
}
export interface CleanupCaptureKey { invocationId: string; captureId: string }
export interface CleanupCapturePage {
  status: 'present' | 'pruned' | 'opaque' | 'missing' | 'foreign';
  header: CleanupCaptureHeader | CleanupOpaque | null; chunks: { sequence: string; text: string }[];
  nextSequence: string; hasMore: boolean; blocked: 'byte-budget' | 'sequence-gap' | 'unknown-header' | null;
}
export interface CleanupCaptureMeasurement extends CleanupCaptureKey {
  status: 'present' | 'empty' | 'pruned' | 'missing' | 'foreign' | 'opaque'; logicalPayloadBytes: string | null;
  header: CleanupCaptureHeader | CleanupOpaque | null;
}
export type CleanupAttemptRead = { status: 'missing' | 'foreign'; fact: null }
  | { status: 'known' | 'opaque'; fact: CleanupAttemptFact | CleanupOpaque };
export type CleanupEventRead = { status: 'missing' | 'foreign'; cursor: string }
  | CleanupOpaque | (CleanupIdentity & { status: 'known'; kind: string; data: Record<string, string | number | boolean | null> });

/** Only these small persisted event contracts are understood in C1; extensions remain opaque. */
export function decodeCleanupEvent(kind: string, value: unknown): Record<string, string | number | boolean | null> | null {
  if (!cleanupObject(value)) return null;
  const shared = ['invocationId','attemptId','captureId','at'];
  const fields: Record<string, string[]> = {
    'invocation.started': ['runId'], 'invocation.inputs': [], 'invocation.running': [], 'invocation.shutting_down': [],
    'invocation.finalized': ['outcome','cleanup'], 'attempt.admitted': [], 'attempt.started': [],
    'attempt.settled': ['outcome','quiescent'], 'attempt.inputs': ['inputsCaptureId'],
    'capture.created': ['channel'], 'capture.appended': ['sequence','state','bytes'],
  };
  if (!Object.hasOwn(fields,kind) || !keys(value,[...shared,...fields[kind]!])) return null;
  for (const [key,field] of Object.entries(value)) {
    if (key.endsWith('Id') && !(field === null && key === 'attemptId') && !cleanupId(field)) return null;
    if (key === 'at' && (typeof field !== 'string' || Buffer.byteLength(field) > 256)) return null;
    if (['sequence','bytes'].includes(key) && (!Number.isSafeInteger(field) || Number(field) < 0)) return null;
    if (key === 'quiescent' && typeof field !== 'boolean') return null;
    if (key === 'outcome' && !(field === null || member(field,['succeeded','failed','needs_input','interrupted','cancelled']))) return null;
    if (key === 'cleanup' && !member(field,['complete','unknown'])) return null;
    if (key === 'state' && !member(field,['open','complete','partial','unknown','pruned'])) return null;
    if (key === 'channel' && !member(field,['stdout','stderr','result','validated-result','request','report','event','context'])) return null;
  }
  const own = kind.startsWith('invocation.') ? 'invocationId' : kind.startsWith('attempt.') ? 'attemptId' : 'captureId';
  if (!cleanupId(value[own])) return null;
  for (const key of fields[kind]!) if (!Object.hasOwn(value,key)) return null;
  return value as Record<string, string | number | boolean | null>;
}

export function cleanupCursor(value: string): bigint {
  if (typeof value !== 'string' || !/^(0|[1-9][0-9]{0,18})$/.test(value) || BigInt(value) > 9223372036854775807n)
    throw new Error('invalid cleanup cursor');
  return BigInt(value);
}
export function cleanupId(value: unknown): value is string {
  return typeof value === 'string' && Buffer.byteLength(value) >= 1 && Buffer.byteLength(value) <= 256
    && !value.includes('\0') && Buffer.from(value).toString('utf8') === value;
}
export function assertCleanupId(value: unknown): asserts value is string {
  if (!cleanupId(value)) throw new Error('invalid cleanup identity');
}
export function cleanupBounds(input: CleanupPageInput, highWater: string) {
  const after = input.after ?? '0', through = input.through ?? highWater;
  const a = cleanupCursor(after), t = cleanupCursor(through), limit = input.limit ?? 100, byteBudget = input.byteBudget ?? 262144;
  if (a > t || !Number.isSafeInteger(limit) || limit < 1 || limit > 100
    || !Number.isSafeInteger(byteBudget) || byteBudget < 1 || byteBudget > 262144) throw new Error('invalid cleanup page');
  return { after, through, a, t, limit, byteBudget };
}
export function cleanupHash(text: string) { return createHash('sha256').update(text).digest('hex'); }
export function cleanupObject(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}
function keys(value: Record<string, unknown>, allowed: string[]) { return Object.keys(value).every(key => allowed.includes(key)); }
function member<T extends string>(value: unknown, values: readonly T[]): value is T { return typeof value === 'string' && values.includes(value as T); }
function nullableId(value: unknown) { return value === null || cleanupId(value); }
function boundedText(value: unknown): value is string { return typeof value === 'string' && Buffer.from(value).toString('utf8') === value; }
export function cleanupIdentity(row: Record<string, unknown>): CleanupIdentity {
  const data = row['data'];
  return { id: cleanupId(row['id']) ? row['id'] : null, cursor: String(row['cursor']), bytes: String(row['bytes']),
    sha256: typeof data === 'string' && BigInt(Buffer.byteLength(data)) === BigInt(String(row['bytes'])) ? cleanupHash(data) : null };
}
export function cleanupOpaque(row: Record<string, unknown>, reason: CleanupOpaque['reason']): CleanupOpaque {
  return { ...cleanupIdentity(row), status: 'opaque', reason };
}
function metadata(row: Record<string, unknown>): { value: Record<string, unknown> } | { opaque: CleanupOpaque } {
  if (!cleanupId(row['id'])) return { opaque: cleanupOpaque(row, 'invalid-identity') };
  if (typeof row['data'] !== 'string') return { opaque: cleanupOpaque(row, BigInt(String(row['bytes'])) > 65536n ? 'oversized' : 'page-budget') };
  if (BigInt(Buffer.byteLength(row['data'])) !== BigInt(String(row['bytes']))) return { opaque: cleanupOpaque(row,'malformed') };
  try {
    const value: unknown = JSON.parse(row['data']);
    return cleanupObject(value) ? { value } : { opaque: cleanupOpaque(row, 'malformed') };
  } catch { return { opaque: cleanupOpaque(row, 'malformed') }; }
}
export function decodeCleanupInvocation(row: Record<string, unknown>): CleanupInvocationFact | CleanupOpaque {
  const parsed = metadata(row);
  if ('opaque' in parsed) return parsed.opaque;
  const value = parsed.value;
  const bad = () => cleanupOpaque(row, 'unknown-format');
  if (!keys(value, ['id','runId','worktreeId','stage','outcome','cleanup','metadata','successNoticePlanned'])
    || value.id !== row['id'] || value.runId !== row['run_id'] || value.worktreeId !== row['worktree_id']
    || !cleanupId(value.runId) || !cleanupId(value.worktreeId)
    || !member(value.stage, ['starting','running','shutting_down','finalized'])
    || !(value.outcome === null || member(value.outcome, ['succeeded','failed','needs_input','interrupted','cancelled']))
    || value.cleanup !== undefined && !member(value.cleanup, ['complete','unknown'])
    || value.successNoticePlanned !== undefined && typeof value.successNoticePlanned !== 'boolean') return bad();
  let inputCaptureId: string | null = null, question: string | null = null, contexts: string[] = [], workflow: string | null = null, selectedCommit: string | null = null;
  if (value.metadata !== undefined) {
    const m = value.metadata;
    if (!cleanupObject(m) || !keys(m, ['settings','workflow','selectedCommit','inputCaptureId','question','contexts'])
      || !cleanupObject(m.settings) || !keys(m.settings,['agentTimeoutMs','commandTimeoutMs','shutdownGraceMs'])
      || Object.values(m.settings).some(setting => !Number.isSafeInteger(setting) || Number(setting) <= 0)
      || !cleanupId(m.workflow) || !cleanupId(m.inputCaptureId)
      || !(m.selectedCommit === null || cleanupId(m.selectedCommit)) || !nullableId(m.question)
      || !Array.isArray(m.contexts) || m.contexts.length > 100 || !m.contexts.every(cleanupId)) return bad();
    inputCaptureId = m.inputCaptureId; question = m.question as string | null; contexts = m.contexts;
    workflow = m.workflow; selectedCommit = m.selectedCommit;
  }
  return { ...cleanupIdentity(row), status: 'known', id: String(row['id']), runId: value.runId, worktreeId: value.worktreeId,
    stage: value.stage, outcome: value.outcome as string | null, inputCaptureId, question, contexts, workflow, selectedCommit };
}
export function decodeCleanupAttempt(row: Record<string, unknown>): CleanupAttemptFact | CleanupOpaque {
  const parsed = metadata(row);
  if ('opaque' in parsed) return parsed.opaque;
  const value = parsed.value;
  const bad = () => cleanupOpaque(row, 'unknown-format');
  if (!keys(value, ['id','invocationId','operationKey','kind','intent','priorAttemptId','loopKey','runId','operationId','fingerprint','launch','outcome','quiescent','owner','evidence','cleanupBasis','agent'])
    || value.id !== row['id'] || value.invocationId !== row['invocation_id'] || value.operationId !== row['operation_id'] || value.kind !== row['kind']
    || ![value.invocationId,value.operationId,value.runId,value.operationKey].every(cleanupId)
    || !member(value.kind, ['agent','command']) || !member(value.intent, ['initial','code_correction','format_correction','repeat','followup'])
    || value.priorAttemptId !== undefined && !cleanupId(value.priorAttemptId) || value.loopKey !== undefined && !cleanupId(value.loopKey)
    || !member(value.launch, ['admitted','started','not_started','unknown'])
    || !(value.outcome === null || member(value.outcome, ['succeeded','failed','needs_input','interrupted']))
    || typeof value.quiescent !== 'boolean' || ![0n,1n].includes(row['occupied'] as bigint) || !boundedText(value.fingerprint)
    || !(value.evidence === null || boundedText(value.evidence))
    || value.cleanupBasis !== undefined && value.cleanupBasis !== 'operator_confirmed'
    || !(value.owner === null || cleanupObject(value.owner) && keys(value.owner,['host','pid','start']) && cleanupId(value.owner.host)
      && Number.isSafeInteger(value.owner.pid) && Number(value.owner.pid) > 0 && nullableId(value.owner.start))) return bad();
  let agent: CleanupAttemptFact['agent'] = null;
  if (value.agent !== undefined) {
    const a = value.agent;
    if (value.kind !== 'agent' || !cleanupObject(a)
      || !keys(a, ['inputsCaptureId','resultCaptureId','outputCaptureId','adapter','sessionMode','context','reusedAttemptId','validator','validatedResultCaptureId'])
      || ![a.inputsCaptureId,a.resultCaptureId,a.outputCaptureId,a.adapter].every(cleanupId)
      || !member(a.sessionMode, ['fresh','reuse']) || !boundedText(a.context)
      || !(a.validator === null || cleanupId(a.validator))
      || a.validatedResultCaptureId !== undefined && !cleanupId(a.validatedResultCaptureId)
      || a.reusedAttemptId !== undefined && !cleanupId(a.reusedAttemptId)) return bad();
    agent = { inputsCaptureId: String(a.inputsCaptureId), resultCaptureId: String(a.resultCaptureId), outputCaptureId: String(a.outputCaptureId),
      validatedResultCaptureId: a.validatedResultCaptureId as string ?? null, reusedAttemptId: a.reusedAttemptId as string ?? null, validator: a.validator as string | null };
  }
  return { ...cleanupIdentity(row), status: 'known', id: String(row['id']), invocationId: String(value.invocationId),
    runId: String(value.runId), operationId: String(value.operationId), operationKey: String(value.operationKey), kind: value.kind,
    priorAttemptId: value.priorAttemptId as string ?? null, occupied: row['occupied'] === 1n, launch: value.launch,
    outcome: value.outcome as string | null, quiescent: value.quiescent, agent };
}
export function decodeCleanupHeader(row: Record<string, unknown>): CleanupCaptureHeader | CleanupOpaque {
  if (row['identity_valid'] === 0n || row['owner_valid'] === 0n || ![row['id'],row['invocation_id']].every(cleanupId) || !nullableId(row['attempt_id'])) return cleanupOpaque(row, 'invalid-identity');
  if (!member(row['channel'], ['stdout','stderr','result','validated-result','request','report','event','context'])
    || !member(row['state'], ['open','complete','partial','unknown','pruned']) || typeof row['sequence'] !== 'bigint' || row['sequence'] < 0n)
    return cleanupOpaque(row, 'unknown-format');
  return { status: 'known', cursor: String(row['cursor']), id: String(row['id']), invocationId: String(row['invocation_id']),
    attemptId: row['attempt_id'] as string | null, channel: row['channel'], state: row['state'],
    lastSequence: String(row['sequence']), logicalPayloadBytes: String(row['bytes']) };
}
