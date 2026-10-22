import { randomUUID } from 'node:crypto';
import { closeSync, existsSync, lstatSync, mkdirSync, openSync, realpathSync, unlinkSync } from 'node:fs';
import { basename, dirname, join } from 'node:path';
import { DatabaseSync } from 'node:sqlite';
import { setTimeout as delay } from 'node:timers/promises';
import { initializeSchema, schemaVersion } from './schema.js';
import { validateAdmission } from './accounting.js';
import { assertLocalPlacement } from './placement.js';
import type { Admission } from './accounting.js';

export interface Owner { host: string; pid: number; start: string | null }
export interface Claim {
  id: string; token: string; kind: 'worktree' | 'dashboard' | 'maintenance'; resourceKey: string;
  invocationId: string | null; owner: Owner;
}
interface Run { id: string; additionalLimit: number; codeLimit: number; formatLimit: number }
interface Worktree { id: string; path: string; registration: string }
export interface Invocation { id: string; runId: string; worktreeId: string; stage: 'starting' | 'running' | 'shutting_down' | 'finalized'; outcome: string | null; cleanup?: 'complete' | 'unknown'; metadata?: object }
interface Attempt extends Admission {
  runId: string; operationId: string; fingerprint: string;
  launch: 'admitted' | 'started' | 'not_started' | 'unknown'; outcome: 'succeeded' | 'failed' | 'needs_input' | 'interrupted' | null;
  quiescent: boolean; owner: Owner | null; evidence: string | null;
  cleanupBasis?: 'operator_confirmed';
}
export type CaptureState = 'open' | 'complete' | 'partial' | 'unknown' | 'pruned';
export interface CaptureChunk { sequence: number; text: string }
interface Clearance { id: string; claimId: string; note: string; basis: 'operator_confirmed'; inspection: 'not_live' | 'unknown' }

function text(value: string, label: string) {
  if (typeof value !== 'string' || Buffer.byteLength(value) < 1 || Buffer.byteLength(value) > 256 || value.includes('\0')) {
    throw new Error(`invalid ${label}: expected 1-256 UTF-8 bytes without NUL`);
  }
  return value;
}

function validateOwner(owner: Owner) {
  text(owner.host, 'owner host');
  if (!Number.isSafeInteger(owner.pid) || owner.pid < 1) throw new Error('invalid owner PID');
  if (owner.start !== null) text(owner.start, 'owner start identity');
}

function increase(current: number, requested: number | undefined) {
  if (requested === undefined) return current;
  if (!Number.isSafeInteger(requested) || requested <= current) throw new Error('explicit limit must increase the current allowance');
  return requested;
}

function paths(commonDir: string, create: boolean) {
  const common = realpathSync(commonDir);
  const directory = join(common, 'factory');
  if (create && !existsSync(directory)) mkdirSync(directory, { mode: 0o700 });
  if (lstatSync(directory).isSymbolicLink() || !lstatSync(directory).isDirectory()) throw new Error('factory storage must be an owned directory, not a symlink');
  // Native qualification records support; placement checks reject unsupported storage before opening it.
  assertLocalPlacement(directory);
  return { directory, database: join(directory, 'history.sqlite'), marker: join(directory, 'bootstrap-incomplete') };
}

function configure(database: DatabaseSync) {
  database.exec('PRAGMA journal_mode=WAL; PRAGMA synchronous=FULL; PRAGMA foreign_keys=ON');
  if (database.prepare('PRAGMA journal_mode').get()?.['journal_mode'] !== 'wal'
    || database.prepare('PRAGMA synchronous').get()?.['synchronous'] !== 2
    || database.prepare('PRAGMA foreign_keys').get()?.['foreign_keys'] !== 1) throw new Error('required SQLite durability settings unavailable');
}

/** Explicit bootstrap only. Normal open never treats missing/unreadable storage as a new repository. */
export async function initializeRepositoryStore(commonDir: string, options: { release: string }) {
  text(options.release, 'release');
  const location = paths(commonDir, true);
  if (existsSync(location.database)) throw new Error('store already exists; explicit repair required');
  closeSync(openSync(location.marker, 'wx', 0o600));
  closeSync(openSync(location.database, 'wx', 0o600));
  const database = new DatabaseSync(location.database, { timeout: 100 });
  try {
    configure(database);
    initializeSchema(database);
    database.prepare('INSERT INTO repository(id,release,state) VALUES (?,?,?)').run(randomUUID(), options.release, 'ready');
    unlinkSync(location.marker);
    return new RepositoryStore(database);
  } catch (error) {
    database.close();
    throw error; // Preserve incomplete bootstrap and data for explicit recovery.
  }
}

export function openRepositoryStore(commonDir: string) {
  const location = paths(commonDir, false);
  if (existsSync(location.marker)) throw new Error('incomplete bootstrap; explicit repair required');
  const file = lstatSync(location.database);
  if (!file.isFile() || file.isSymbolicLink()) throw new Error('invalid store file');
  const database = new DatabaseSync(location.database, { timeout: 100 });
  try {
    if (database.prepare('PRAGMA user_version').get()?.['user_version'] !== schemaVersion) throw new Error('incompatible schema; explicit forward maintenance required');
    if (database.prepare('PRAGMA quick_check').get()?.['quick_check'] !== 'ok') throw new Error('corrupt store; preserving data');
    if (!database.prepare('SELECT id FROM repository').get()) throw new Error('missing repository identity');
    configure(database);
    return new RepositoryStore(database);
  } catch (error) { database.close(); throw error; }
}

export class RepositoryStore {
  constructor(private readonly database: DatabaseSync) {}

  private readonly blockedInvocations = new Set<string>();
  blockAdmissions(invocationId: string) { this.blockedInvocations.add(invocationId); }
  close() { this.database.close(); }

  private async transaction<T>(action: () => T): Promise<T> {
    const deadline = performance.now() + 5000;
    while (true) {
      try { this.database.exec('BEGIN IMMEDIATE'); break; }
      catch (error) {
        const code = (error as { errcode?: number }).errcode;
        if (code === undefined || (code & 255) !== 5 || performance.now() >= deadline) throw error;
        await delay(100 + Math.floor(Math.random() * 20));
      }
    }
    try {
      const result = action();
      this.database.exec('COMMIT');
      return result;
    } catch (error) {
      if (this.database.isTransaction) this.database.exec('ROLLBACK');
      throw error;
    }
  }

  private event(kind: string, data: object) {
    if (Buffer.byteLength(JSON.stringify(data)) > 8192) throw new Error('event metadata exceeds limit');
    this.database.prepare('INSERT INTO observation_events(kind,data) VALUES (?,?)').run(kind, JSON.stringify({ ...data, at: new Date().toISOString() }));
  }

  private ready() {
    if (this.database.prepare('SELECT state FROM repository').get()?.['state'] !== 'ready') throw new Error('installation not ready; explicit maintenance required');
    if (this.database.prepare("SELECT id FROM owner_claims WHERE kind='maintenance'").get()) throw new Error('maintenance claimed; startup refused');
  }

  async createRun(): Promise<Run> {
    return this.transaction(() => {
      this.ready();
      const run = { id: randomUUID(), additionalLimit: 20, codeLimit: 2, formatLimit: 1 };
      this.database.prepare('INSERT INTO runs(id,data) VALUES (?,?)').run(run.id, JSON.stringify(run));
      this.event('run.created', { runId: run.id });
      return run;
    });
  }

  async registerWorktree(input: { path: string; registration: string }): Promise<Worktree> {
    const path = realpathSync(input.path);
    text(input.registration, 'Git registration');
    return this.transaction(() => {
      this.ready();
      const existing = this.database.prepare('SELECT data FROM worktrees WHERE path=?').get(path);
      if (existing) {
        const worktree = JSON.parse(String(existing['data'])) as Worktree;
        if (worktree.registration !== input.registration) throw new Error('worktree registration changed; explicit correction required');
        return worktree;
      }
      const worktree = { id: randomUUID(), path, registration: input.registration };
      this.database.prepare('INSERT INTO worktrees(id,path,data) VALUES (?,?,?)').run(worktree.id, path, JSON.stringify(worktree));
      this.event('worktree.registered', { worktreeId: worktree.id });
      return worktree;
    });
  }

  /** Reserve an absent destination without creating it. Ownership must precede Git mutation. */
  async reserveWorktree(destination: string): Promise<Worktree> {
    const path = join(realpathSync(dirname(destination)), basename(destination));
    if (existsSync(path)) throw new Error('worktree destination already exists');
    return this.transaction(() => {
      this.ready();
      const worktree = { id: randomUUID(), path, registration: 'reserved' };
      this.database.prepare('INSERT INTO worktrees(id,path,data) VALUES (?,?,?)').run(worktree.id, path, JSON.stringify(worktree));
      this.event('worktree.reserved', { worktreeId: worktree.id });
      return worktree;
    });
  }

  readWorktree(id: string): Worktree {
    const row = this.database.prepare('SELECT data FROM worktrees WHERE id=?').get(id);
    if (!row) throw new Error('worktree not found');
    return JSON.parse(String(row['data'])) as Worktree;
  }

  async finalizeWorktree(input: { id: string; claimId: string; token: string; registration: string }) {
    text(input.registration, 'Git registration');
    return this.transaction(() => {
      const claim = this.database.prepare('SELECT resource_key FROM owner_claims WHERE id=? AND token=? AND kind=?').get(input.claimId, input.token, 'worktree');
      if (!claim || claim['resource_key'] !== input.id) throw new Error('claim/token no longer matches worktree');
      const worktree = this.readWorktree(input.id);
      if (worktree.registration !== 'reserved') throw new Error('worktree is not reserved');
      if (realpathSync(worktree.path) !== worktree.path) throw new Error('worktree destination changed');
      worktree.registration = input.registration;
      this.database.prepare('UPDATE worktrees SET data=? WHERE id=?').run(JSON.stringify(worktree), input.id);
      this.event('worktree.registered', { worktreeId: input.id });
    });
  }

  readHistory(id: string) {
    const invocation = this.readInvocation(id);
    const attempts = this.database.prepare('SELECT data FROM attempts WHERE invocation_id=? ORDER BY rowid').all(id).map(row => JSON.parse(String(row['data'])) as Attempt);
    const captures = this.database.prepare('SELECT id FROM captures WHERE invocation_id=? ORDER BY rowid').all(id).map(row => {
      const captureId = String(row['id']); let after = 0; const chunks: CaptureChunk[] = [];
      let page;
      do { page = this.readCapture({ id: captureId, after }); chunks.push(...page.chunks); after = page.nextSequence; } while (page.hasMore);
      return { id: captureId, state: page.state, channel: page.channel, chunks };
    });
    return { invocation, worktree: this.readWorktree(invocation.worktreeId), attempts, captures, accounting: this.readAccounting(invocation.runId) };
  }

  validateReference(input: { id: string; runId: string; question?: boolean }) {
    const row = this.database.prepare('SELECT c.channel,c.state,i.run_id FROM captures c JOIN invocations i ON c.invocation_id=i.id WHERE c.id=?').get(input.id);
    if (!row || row['run_id'] !== input.runId || row['state'] !== 'complete' || (input.question && row['channel'] !== 'request')) throw new Error('missing, incomplete or foreign-run context reference');
  }

  async saveInvocationMetadata(id: string, metadata: object) {
    return this.transaction(() => {
      const invocation = this.readInvocation(id);
      invocation.metadata = metadata;
      this.database.prepare('UPDATE invocations SET data=? WHERE id=?').run(JSON.stringify(invocation), id);
      this.event('invocation.inputs', { invocationId: id });
    });
  }

  async finishInvocation(id: string, outcome: string, cleanup: 'complete' | 'unknown') {
    return this.transaction(() => {
      const invocation = this.readInvocation(id);
      if (invocation.stage === 'finalized') throw new Error('invocation already finalized');
      if (cleanup === 'complete' && this.database.prepare('SELECT id FROM attempts WHERE invocation_id=? AND occupied=1').get(id)) throw new Error('activity is not quiescent');
      invocation.stage = 'finalized'; invocation.outcome = outcome; invocation.cleanup = cleanup;
      this.database.prepare('UPDATE invocations SET data=? WHERE id=?').run(JSON.stringify(invocation), id);
      this.event('invocation.finalized', { invocationId: id, outcome, cleanup });
    });
  }

  async startInvocation(input: { runId: string; worktreeId: string; owner: Owner }): Promise<Invocation & { claim: Claim }> {
    validateOwner(input.owner);
    return this.transaction(() => {
      this.ready();
      if (this.database.prepare("SELECT id FROM owner_claims WHERE kind='worktree' AND resource_key=?").get(input.worktreeId)) throw new Error('worktree already claimed');
      const invocation: Invocation = { id: randomUUID(), runId: input.runId, worktreeId: input.worktreeId, stage: 'starting', outcome: null };
      const claim: Claim = { id: randomUUID(), token: randomUUID(), kind: 'worktree', resourceKey: input.worktreeId, invocationId: invocation.id, owner: input.owner };
      this.database.prepare('INSERT INTO invocations(id,run_id,worktree_id,data) VALUES (?,?,?,?)').run(invocation.id, invocation.runId, invocation.worktreeId, JSON.stringify(invocation));
      this.database.prepare('INSERT INTO owner_claims(id,token,kind,resource_key,invocation_id,data) VALUES (?,?,?,?,?,?)')
        .run(claim.id, claim.token, claim.kind, claim.resourceKey, claim.invocationId, JSON.stringify(claim));
      this.event('invocation.started', { invocationId: invocation.id, runId: invocation.runId });
      this.event('owner.claimed', { claimId: claim.id, invocationId: invocation.id });
      return { ...invocation, claim };
    });
  }

  readInvocation(id: string): Invocation {
    const row = this.database.prepare('SELECT data FROM invocations WHERE id=?').get(id);
    if (!row) throw new Error('invocation not found');
    return JSON.parse(String(row['data'])) as Invocation;
  }

  async activateInvocation(id: string) {
    return this.transaction(() => {
      this.ready();
      const invocation = this.readInvocation(id);
      if (invocation.stage !== 'starting' || !this.database.prepare('SELECT id FROM owner_claims WHERE invocation_id=?').get(id)) throw new Error('invocation is not eligible for activation');
      invocation.stage = 'running';
      this.database.prepare('UPDATE invocations SET data=? WHERE id=?').run(JSON.stringify(invocation), id);
      this.event('invocation.running', { invocationId: id });
    });
  }

  async stopAdmissions(id: string) {
    return this.transaction(() => {
      const invocation = this.readInvocation(id);
      if (invocation.stage === 'shutting_down' || invocation.stage === 'finalized') return;
      invocation.stage = 'shutting_down';
      this.database.prepare('UPDATE invocations SET data=? WHERE id=?').run(JSON.stringify(invocation), id);
      this.event('invocation.shutting_down', { invocationId: id });
    });
  }

  async increaseAllowances(input: { runId: string; additionalLimit?: number; codeLimit?: number; formatLimit?: number; reason: string }) {
    text(input.reason, 'increase reason');
    if (input.additionalLimit === undefined && input.codeLimit === undefined && input.formatLimit === undefined) throw new Error('specify an explicit increase');
    return this.transaction(() => {
      this.ready();
      const row = this.database.prepare('SELECT data FROM runs WHERE id=?').get(input.runId);
      if (!row) throw new Error('run not found');
      const run = JSON.parse(String(row['data'])) as Run;
      run.additionalLimit = increase(run.additionalLimit, input.additionalLimit);
      run.codeLimit = increase(run.codeLimit, input.codeLimit);
      run.formatLimit = increase(run.formatLimit, input.formatLimit);
      this.database.prepare('UPDATE runs SET data=? WHERE id=?').run(JSON.stringify(run), run.id);
      this.event('allowances.increased', { ...run, reason: input.reason });
      return run;
    });
  }

  async increaseCapacity(input: { agentLimit?: number; commandLimit?: number; reason: string }) {
    text(input.reason, 'capacity increase reason');
    if (input.agentLimit === undefined && input.commandLimit === undefined) throw new Error('specify an explicit increase');
    return this.transaction(() => {
      this.ready();
      const row = this.database.prepare('SELECT agent_limit,command_limit FROM repository').get()!;
      const agents = increase(Number(row['agent_limit']), input.agentLimit);
      const commands = increase(Number(row['command_limit']), input.commandLimit);
      this.database.prepare('UPDATE repository SET agent_limit=?,command_limit=?').run(agents, commands);
      this.event('capacity.increased', { agents, commands, reason: input.reason });
    });
  }

  readAttempt(id: string): Attempt {
    const row = this.database.prepare('SELECT data FROM attempts WHERE id=?').get(id);
    if (!row) throw new Error('attempt not found');
    return JSON.parse(String(row['data'])) as Attempt;
  }

  readAccounting(runId: string) {
    if (!this.database.prepare('SELECT id FROM runs WHERE id=?').get(runId)) throw new Error('run not found');
    return {
      additionalUsed: Number(this.database.prepare("SELECT coalesce(sum(delta),0) AS n FROM allowance_ledger WHERE run_id=? AND category='additional'").get(runId)?.['n']),
      occupiedAgents: Number(this.database.prepare("SELECT count(*) AS n FROM attempts WHERE kind='agent' AND occupied=1").get()?.['n']),
      occupiedCommands: Number(this.database.prepare("SELECT count(*) AS n FROM attempts WHERE kind='command' AND occupied=1").get()?.['n']),
    };
  }

  private used(runId: string, category: string, scope: string): number {
    return Number(this.database.prepare('SELECT coalesce(sum(delta),0) AS n FROM allowance_ledger WHERE run_id=? AND category=? AND scope=?').get(runId, category, scope)?.['n']);
  }

  async admitAttempt(input: Admission, startup = false): Promise<Attempt> {
    validateAdmission(input);
    const fingerprint = JSON.stringify([input.id, input.invocationId, input.operationKey, input.kind, input.intent, input.priorAttemptId ?? null, input.loopKey ?? null]);
    return this.transaction(() => {
      if (this.blockedInvocations.has(input.invocationId)) throw new Error('capture failure blocks admission');
      const existing = this.database.prepare('SELECT data FROM attempts WHERE id=?').get(input.id);
      if (existing) {
        const attempt = JSON.parse(String(existing['data'])) as Attempt;
        if (attempt.fingerprint !== fingerprint) throw new Error('attempt identity reused with different inputs');
        return attempt; // Uncertain commit acknowledgement resolves by identity without another debit.
      }
      this.ready();
      const invocation = this.readInvocation(input.invocationId);
      if ((invocation.stage !== 'running' && !(startup && invocation.stage === 'starting' && input.kind === 'command' && input.operationKey === `startup/build/${invocation.id}`)) || !this.database.prepare('SELECT id FROM owner_claims WHERE invocation_id=?').get(invocation.id)) throw new Error('invocation not eligible for admission');
      const limits = this.database.prepare('SELECT agent_limit,command_limit FROM repository').get()!;
      const capacity = Number(limits[input.kind === 'agent' ? 'agent_limit' : 'command_limit']);
      if (Number(this.database.prepare('SELECT count(*) AS n FROM attempts WHERE kind=? AND occupied=1').get(input.kind)?.['n']) >= capacity) throw new Error(`${input.kind} capacity exhausted`);
      const operation = this.database.prepare('SELECT id,data FROM operations WHERE run_id=? AND operation_key=?').get(invocation.runId, input.operationKey);
      const original = operation ? JSON.parse(String(operation['data'])) as { loopKey: string; kind: string } : null;
      const loopKey = input.loopKey ?? original?.loopKey ?? input.operationKey;
      if (original && (loopKey !== original.loopKey || original.kind !== input.kind)) throw new Error('operation identity cannot change kind or loop lineage');
      if (input.intent === 'initial' && (operation || input.priorAttemptId)) throw new Error('operation repeat requires additional allowance and lineage');
      if (input.intent !== 'initial') {
        if (!input.priorAttemptId) throw new Error('additional work requires prior attempt lineage');
        const prior = this.readAttempt(input.priorAttemptId);
        if (prior.runId !== invocation.runId) throw new Error('prior attempt belongs to another run');
        const clearedFollowup = input.intent === 'followup' && prior.invocationId !== invocation.id && prior.cleanupBasis === 'operator_confirmed';
        if (!prior.quiescent || (prior.outcome === null && !clearedFollowup)) throw new Error('prior activity is not quiescent');
        const previousOperation = this.database.prepare('SELECT data FROM operations WHERE id=?').get(prior.operationId);
        const priorLoop = (JSON.parse(String(previousOperation?.['data'])) as { loopKey: string }).loopKey;
        if (priorLoop !== loopKey) throw new Error('loop lineage cannot change across additional work');
      }
      const run = JSON.parse(String(this.database.prepare('SELECT data FROM runs WHERE id=?').get(invocation.runId)?.['data'])) as Run;
      const charges: { category: string; scope: string; limit: number; diagnostic: string }[] = [];
      if (input.kind === 'agent' && input.intent !== 'initial') charges.push({ category: 'additional', scope: run.id, limit: run.additionalLimit, diagnostic: 'additional agent allowance' });
      if (input.intent === 'code_correction') charges.push({ category: 'code', scope: loopKey, limit: run.codeLimit, diagnostic: 'code correction allowance' });
      if (input.intent === 'format_correction') charges.push({ category: 'format', scope: input.priorAttemptId!, limit: run.formatLimit, diagnostic: 'format correction allowance' });
      for (const charge of charges) if (this.used(run.id, charge.category, charge.scope) >= charge.limit) throw new Error(`${charge.diagnostic} exhausted`);
      const operationId = operation ? String(operation['id']) : randomUUID();
      if (!operation) this.database.prepare('INSERT INTO operations(id,run_id,operation_key,data) VALUES (?,?,?,?)')
        .run(operationId, invocation.runId, input.operationKey, JSON.stringify({ loopKey, kind: input.kind }));
      const attempt: Attempt = { ...input, runId: invocation.runId, operationId, fingerprint, launch: 'admitted', outcome: null, quiescent: false, owner: null, evidence: null };
      this.database.prepare('INSERT INTO attempts(id,invocation_id,operation_id,kind,occupied,data) VALUES (?,?,?,?,1,?)')
        .run(attempt.id, attempt.invocationId, operationId, input.kind, JSON.stringify(attempt));
      for (const charge of charges) this.database.prepare('INSERT INTO allowance_ledger(id,attempt_id,run_id,scope,category,delta) VALUES (?,?,?,?,?,1)')
        .run(randomUUID(), attempt.id, run.id, charge.scope, charge.category);
      this.event('attempt.admitted', { attemptId: attempt.id, invocationId: invocation.id });
      return attempt;
    });
  }

  async markStarted(input: { id: string; owner: Owner }) {
    validateOwner(input.owner);
    return this.transaction(() => {
      const attempt = this.readAttempt(input.id);
      if (attempt.cleanupBasis === 'operator_confirmed') throw new Error('cleared attempt cannot be started again');
      if (attempt.launch !== 'admitted' || attempt.outcome !== null) throw new Error('attempt cannot be marked started');
      attempt.launch = 'started'; attempt.owner = input.owner;
      this.database.prepare('UPDATE attempts SET data=? WHERE id=?').run(JSON.stringify(attempt), attempt.id);
      this.event('attempt.started', { attemptId: attempt.id });
    });
  }

  async settleAttempt(input: { id: string; launch: 'started' | 'not_started' | 'unknown'; outcome: Exclude<Attempt['outcome'], null>; quiescent: boolean; evidence: string }) {
    text(input.evidence, 'settlement evidence');
    if (!['started', 'not_started', 'unknown'].includes(input.launch)
      || !['succeeded', 'failed', 'needs_input', 'interrupted'].includes(input.outcome)
      || typeof input.quiescent !== 'boolean') throw new Error('invalid settlement facts');
    return this.transaction(() => {
      const attempt = this.readAttempt(input.id);
      if (attempt.cleanupBasis === 'operator_confirmed' && !input.quiescent) throw new Error('settlement cannot undo explicit clearance');
      if (attempt.outcome !== null) {
        if (attempt.launch === input.launch && attempt.outcome === input.outcome && attempt.quiescent === input.quiescent && attempt.evidence === input.evidence) return attempt;
        throw new Error('attempt already settled; preserve terminal outcome');
      }
      if (attempt.launch === 'started' && input.launch !== 'started') throw new Error('confirmed launch cannot be erased or refunded');
      if (input.launch === 'started' && attempt.launch !== 'started') throw new Error('record confirmed spawn identity before settlement');
      if (input.launch === 'not_started' && (!input.quiescent || input.outcome === 'succeeded')) throw new Error('non-launch requires quiescence and cannot succeed');
      attempt.launch = input.launch; attempt.outcome = input.outcome; attempt.quiescent = input.quiescent; attempt.evidence = input.evidence;
      this.database.prepare('UPDATE attempts SET data=?,occupied=? WHERE id=?').run(JSON.stringify(attempt), input.quiescent ? 0 : 1, attempt.id);
      if (input.launch === 'not_started') {
        for (const charge of this.database.prepare('SELECT category,scope FROM allowance_ledger WHERE attempt_id=? AND delta=1').all(attempt.id)) {
          this.database.prepare('INSERT INTO allowance_ledger(id,attempt_id,run_id,scope,category,delta) VALUES (?,?,?,?,?,-1)')
            .run(randomUUID(), attempt.id, attempt.runId, String(charge['scope']), String(charge['category']));
        }
      }
      this.event('attempt.settled', { attemptId: attempt.id, outcome: attempt.outcome, quiescent: attempt.quiescent });
    });
  }

  inspectOwners(): Claim[] {
    return this.database.prepare('SELECT data FROM owner_claims ORDER BY id LIMIT 200').all().map((row) => JSON.parse(String(row['data'])) as Claim);
  }

  async claimResource(input: { kind: 'dashboard' | 'maintenance'; owner: Owner }): Promise<Claim> {
    validateOwner(input.owner);
    if (!['dashboard', 'maintenance'].includes(input.kind)) throw new Error('invalid resource kind');
    return this.transaction(() => {
      this.ready();
      if (input.kind === 'maintenance' && this.database.prepare('SELECT id FROM owner_claims LIMIT 1').get()) throw new Error('active or uncertain owner blocks maintenance');
      if (this.database.prepare('SELECT id FROM owner_claims WHERE kind=?').get(input.kind)) throw new Error(`${input.kind} already claimed`);
      const resourceKey = String(this.database.prepare('SELECT id FROM repository').get()?.['id']);
      const claim: Claim = { id: randomUUID(), token: randomUUID(), kind: input.kind, resourceKey, invocationId: null, owner: input.owner };
      this.database.prepare('INSERT INTO owner_claims(id,token,kind,resource_key,invocation_id,data) VALUES (?,?,?,?,NULL,?)')
        .run(claim.id, claim.token, claim.kind, resourceKey, JSON.stringify(claim));
      this.event('owner.claimed', { claimId: claim.id, kind: claim.kind });
      return claim;
    });
  }

  readClearances(input: { claimId: string }): Clearance[] {
    return this.database.prepare('SELECT data FROM clearances WHERE claim_id=? ORDER BY id LIMIT 200').all(input.claimId)
      .map((row) => JSON.parse(String(row['data'])) as Clearance);
  }

  async clearOwner(input: { claimId: string; token: string; operatorConfirmed: boolean; note: string; inspection: 'known_live' | 'not_live' | 'unknown' }) {
    if (input.inspection === 'known_live') throw new Error('known-live owner cannot be cleared');
    if (!['not_live', 'unknown'].includes(input.inspection)) throw new Error('invalid owner inspection');
    if (input.operatorConfirmed !== true) throw new Error('explicit operator confirmation required');
    text(input.note, 'clearance note');
    return this.transaction(() => {
      const row = this.database.prepare('SELECT data FROM owner_claims WHERE id=? AND token=?').get(input.claimId, input.token);
      if (!row) throw new Error('claim/token no longer matches');
      const claim = JSON.parse(String(row['data'])) as Claim;
      const clearance: Clearance = { id: randomUUID(), claimId: claim.id, note: input.note, basis: 'operator_confirmed', inspection: input.inspection as 'not_live' | 'unknown' };
      this.database.prepare('INSERT INTO clearances(id,claim_id,data) VALUES (?,?,?)').run(clearance.id, claim.id, JSON.stringify(clearance));
      for (const row of this.database.prepare('SELECT data FROM attempts WHERE invocation_id=? AND occupied=1').all(claim.invocationId)) {
        const attempt = JSON.parse(String(row['data'])) as Attempt;
        attempt.quiescent = true; attempt.cleanupBasis = 'operator_confirmed';
        this.database.prepare('UPDATE attempts SET occupied=0,data=? WHERE id=?').run(JSON.stringify(attempt), attempt.id);
      }
      this.database.prepare('DELETE FROM owner_claims WHERE id=? AND token=?').run(claim.id, claim.token);
      this.event('owner.cleared', { claimId: claim.id, clearanceId: clearance.id, basis: clearance.basis });
      return clearance;
    });
  }

  async releaseClaim(input: { claimId: string; token: string; basis: 'quiescent' }) {
    if (input.basis !== 'quiescent') throw new Error('automatic release requires quiescence evidence');
    return this.transaction(() => {
      const row = this.database.prepare('SELECT token FROM owner_claims WHERE id=?').get(input.claimId);
      if (!row || row['token'] !== input.token) throw new Error('claim/token no longer matches');
      if (this.database.prepare('SELECT a.id FROM attempts a JOIN owner_claims c ON c.invocation_id=a.invocation_id WHERE c.id=? AND a.occupied=1').get(input.claimId)) throw new Error('owned activity is not quiescent');
      this.database.prepare('DELETE FROM owner_claims WHERE id=? AND token=?').run(input.claimId, input.token);
      this.event('owner.released', { claimId: input.claimId, basis: input.basis });
    });
  }

  async createCapture(input: { invocationId: string; attemptId?: string; channel: string }) {
    if (!['stdout', 'stderr', 'result', 'request', 'report', 'event', 'context'].includes(input.channel)) throw new Error('unsupported capture channel');
    return this.transaction(() => {
      const invocation = this.readInvocation(input.invocationId);
      if (invocation.stage === 'finalized') throw new Error('invocation finalized');
      if (input.attemptId && this.readAttempt(input.attemptId).invocationId !== input.invocationId) throw new Error('capture attempt belongs to another invocation');
      const capture = { id: randomUUID(), ...input, state: 'open' as CaptureState };
      this.database.prepare('INSERT INTO captures(id,invocation_id,attempt_id,channel,state) VALUES (?,?,?,?,?)')
        .run(capture.id, input.invocationId, input.attemptId ?? null, input.channel, 'open');
      this.event('capture.created', { captureId: capture.id, invocationId: input.invocationId, channel: input.channel });
      return capture;
    });
  }

  async appendCapture(input: { id: string; chunks: CaptureChunk[]; state?: CaptureState }) {
    if (!Array.isArray(input.chunks) || input.chunks.length > 200) throw new Error('invalid capture batch');
    if (input.state !== undefined && !['open','complete','partial','unknown','pruned'].includes(input.state)) throw new Error('invalid capture state');
    let bytes = 0;
    for (const chunk of input.chunks) {
      if (typeof chunk.text !== 'string' || Buffer.from(chunk.text).toString('utf8') !== chunk.text || !Number.isSafeInteger(chunk.sequence) || chunk.sequence < 1) throw new Error('invalid capture chunk');
      const size = Buffer.byteLength(chunk.text);
      if (size > 65536) throw new Error('capture chunk exceeds 64 KiB');
      bytes += size;
    }
    if (bytes > 262144) throw new Error('capture batch exceeds 256 KiB');
    return this.transaction(() => {
      const row = this.database.prepare('SELECT state,sequence,invocation_id FROM captures WHERE id=?').get(input.id);
      if (!row) throw new Error('capture not found');
      let sequence = Number(row['sequence']);
      if ((input.chunks.length && input.chunks[0]!.sequence <= sequence) || (!input.chunks.length && input.state === row['state'] && row['state'] !== 'open')) {
        let prior = input.chunks[0]?.sequence ?? 1;
        for (const chunk of input.chunks) {
          if (chunk.sequence !== prior++ || this.database.prepare('SELECT text FROM capture_chunks WHERE capture_id=? AND sequence=?').get(input.id, chunk.sequence)?.['text'] !== chunk.text) throw new Error('capture sequence conflicts with committed data');
        }
        if (input.state !== undefined && input.state !== row['state']) throw new Error('capture retry state conflicts with committed data');
        return { sequence, state: row['state'] as CaptureState };
      }
      if (row['state'] !== 'open') throw new Error('capture is complete or closed');
      for (const chunk of input.chunks) {
        if (chunk.sequence !== sequence + 1) throw new Error('capture sequence must be contiguous and unique');
        this.database.prepare('INSERT INTO capture_chunks(capture_id,sequence,text) VALUES (?,?,?)').run(input.id, chunk.sequence, chunk.text);
        sequence++;
      }
      const state = input.state ?? 'open';
      this.database.prepare('UPDATE captures SET sequence=?,state=? WHERE id=?').run(sequence, state, input.id);
      this.event('capture.appended', { captureId: input.id, invocationId: row['invocation_id'], sequence, state, bytes });
      return { sequence, state };
    });
  }

  readCapture(input: { id: string; after?: number; limit?: number }) {
    const after = input.after ?? 0, limit = input.limit ?? 200;
    if (!Number.isSafeInteger(after) || after < 0 || !Number.isSafeInteger(limit) || limit < 1 || limit > 200) throw new Error('invalid capture page');
    const row = this.database.prepare('SELECT state,sequence,channel FROM captures WHERE id=?').get(input.id);
    const state = row ? String(row['state']) as CaptureState : 'missing';
    const chunks: CaptureChunk[] = [];
    let size = 0;
    if (row && state !== 'pruned') {
      for (const chunk of this.database.prepare('SELECT sequence,text FROM capture_chunks WHERE capture_id=? AND sequence>? ORDER BY sequence LIMIT ?').iterate(input.id, after, limit)) {
        const item = { sequence: Number(chunk['sequence']), text: String(chunk['text']) };
        const bytes = Buffer.byteLength(JSON.stringify(item)) + 1;
        if (size + bytes > 1047552) break;
        size += bytes; chunks.push(item);
      }
    }
    const nextSequence = chunks.at(-1)?.sequence ?? after;
    return { state, channel: row ? String(row['channel']) : null, chunks, nextSequence, hasMore: !!row && state !== 'pruned' && nextSequence < Number(row['sequence']) };
  }

  readEvents(input: { after: string; limit?: number }) {
    if (!/^\d+$/.test(input.after) || input.after.length > 19 || BigInt(input.after) > 9223372036854775807n) throw new Error('invalid event cursor');
    const limit = input.limit ?? 200;
    if (!Number.isSafeInteger(limit) || limit < 1 || limit > 200) throw new Error('event limit must be 1-200');
    const statement = this.database.prepare('SELECT cursor,kind,data FROM observation_events WHERE cursor>? ORDER BY cursor LIMIT ?');
    statement.setReadBigInts(true);
    const events: { cursor: string; kind: string; data: object }[] = [];
    let size = 0;
    for (const row of statement.iterate(BigInt(input.after), limit)) {
      const event = { cursor: String(row['cursor']), kind: String(row['kind']), data: JSON.parse(String(row['data'])) as object };
      const bytes = Buffer.byteLength(JSON.stringify(event)) + 1;
      if (size + bytes > 1047552) break;
      size += bytes; events.push(event);
    }
    const gap = BigInt(input.after) > 0n && !this.database.prepare('SELECT cursor FROM observation_events WHERE cursor=?').get(BigInt(input.after));
    return { events, nextCursor: events.at(-1)?.cursor ?? input.after, gap };
  }
}
