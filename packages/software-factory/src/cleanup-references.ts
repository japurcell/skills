import { createHash } from 'node:crypto';
import { performance } from 'node:perf_hooks';
import { isDeepStrictEqual } from 'node:util';
import { openCleanupReadStore, type CleanupReadStore } from './store.js';
import { cleanupCursor, cleanupHash, cleanupId, cleanupObject, type CleanupAttemptFact, type CleanupCaptureHeader,
  type CleanupCaptureKey, type CleanupInvocationFact, type CleanupOpaque, type CleanupPage, type CleanupSnapshot } from './cleanup-read.js';
import { readCleanupSnapshotAuthority, type CleanupBackupResolution } from './cleanup-backups.js';
import { repositoryIdentity } from './workspace.js';
import { analyzeLearningReferences, isLearningWorkflow } from './cleanup-learning.js';
import { ordinaryDeclaration, ordinaryReferenceInterpreter } from './cleanup-recipes.js';

export type CleanupNode = { kind: 'invocation'; invocationId: string }
  | { kind: 'attempt'; invocationId: string; attemptId: string }
  | { kind: 'operation'; runId: string; operationId: string }
  | { kind: 'capture'; invocationId: string; captureId: string }
  | { kind: 'event'; invocationId: string; cursor: string };
export type CleanupEdgeKind = 'input'|'question'|'selected-context'|'prior-attempt'|'reused-attempt'|'operation'|'owned-capture'
  |'source-input'|'source-invocation'|'source-attempt'|'source-event'|'source-capture'|'candidate'|'extraction-report'
  |'extraction-result'|'baseline'|'objective'|'review'|'preparation'|'original-adoption';
export interface CleanupEdge { from: CleanupNode; to: CleanupNode; kind: CleanupEdgeKind }
export interface CleanupBlocker {
  code: 'opaque'|'missing'|'foreign'|'partial'|'pruned'|'malformed'|'ownership'|'digest'|'invalid-lineage'|'cycle'|'limit'|'unstable'|'unassessed-recovery';
  node: CleanupNode | null; id?: string|null; cursor?: string; limit?: string; source?: 'invocation'|'attempt'|'capture'|'operation';
}
export interface CleanupAnalysisBounds {
  rowsPerPage: number; metadataPageBytes: number; sourceRows: number; reports: number; nodes: number; edges: number;
  pages: number; stateBytes: number; payloadBytes: number; elapsedMs: number;
}
export type SupportedCleanupFormat = 'extraction-v1'|'evaluation-v1'|'adoption-preparation-compat1'|'adoption-compat1'
  |'revert-preparation-compat1'|'revert-compat1'|'change-report-v1'|'audit-report-v1';
export interface ReferenceAnalysis {
  status: 'complete'|'blocked'; snapshot: CleanupSnapshot; snapshotSha256: string|null; graphSha256: string|null;
  protected: readonly CleanupNode[]; edges: readonly CleanupEdge[];
  reports: readonly { key: CleanupCaptureKey; format: SupportedCleanupFormat; sha256: string }[];
  blockers: readonly CleanupBlocker[];
  usage: { sourceRows: number; reports: number; nodes: number; edges: number; pages: number; decodedBytes: string; stateBytes: string };
}
export type CleanupSelection = { kind: 'captures'; captures: readonly CleanupCaptureKey[];
  exceptional: readonly CleanupCaptureKey[]; reviewNonOutput: readonly CleanupCaptureKey[] }
  | { kind: 'backups'; backups: readonly { operationId: string; backupId: string }[] };
export interface CleanupImpactCapture {
  key: CleanupCaptureKey; disposition: 'eligible'|'protected'|'refused'|'exceptional-impact'|'already-pruned';
  logicalBytes: string|null; payloadSha256: string|null; affectedReports: readonly CleanupCaptureKey[];
  affectedAttempts: readonly { invocationId: string; attemptId: string }[];
  verificationWillFail: boolean; requiresExplicitConfirmation: boolean;
}
export interface CleanupImpact {
  advisory: true; status: 'inspectable'|'blocked'; impactSha256: string|null; snapshotSha256: string|null;
  blockers: readonly CleanupBlocker[]; captures: readonly CleanupImpactCapture[]; backups: readonly CleanupBackupResolution[];
  pages: readonly { index: number; sha256: string; records: readonly (CleanupImpactCapture|CleanupBackupResolution|CleanupBlocker)[] }[];
  selectedLogicalBytes: string|null;
}

const MAX: Readonly<CleanupAnalysisBounds> = Object.freeze({ rowsPerPage: 100, metadataPageBytes: 262144, sourceRows: 100000,
  reports: 1000, nodes: 16384, edges: 65536, pages: 4096, stateBytes: 33554432, payloadBytes: 67108864, elapsedMs: 30000 });
const compare = (a: string,b: string) => a < b ? -1 : a > b ? 1 : 0;
const nodeKey = (node: CleanupNode) => node.kind === 'capture' ? JSON.stringify(['capture',node.invocationId,node.captureId])
  : node.kind === 'attempt' ? JSON.stringify(['attempt',node.invocationId,node.attemptId])
  : node.kind === 'operation' ? JSON.stringify(['operation',node.runId,node.operationId])
  : node.kind === 'event' ? JSON.stringify(['event',node.invocationId,node.cursor]) : JSON.stringify(['invocation',node.invocationId]);
const captureNode = (key: CleanupCaptureKey): CleanupNode => ({ kind: 'capture', ...key });
const attemptNode = (fact: CleanupAttemptFact): CleanupNode => ({ kind: 'attempt', invocationId: fact.invocationId, attemptId: fact.id });
const invocationNode = (fact: CleanupInvocationFact): CleanupNode => ({ kind: 'invocation', invocationId: fact.id });
const operationNode = (fact: CleanupAttemptFact): CleanupNode => ({ kind: 'operation', runId: fact.runId, operationId: fact.operationId });
function exact(value: unknown, keys: readonly string[]): value is Record<string, unknown> {
  return cleanupObject(value) && Object.keys(value).length === keys.length && keys.every(key => Object.hasOwn(value,key));
}
function bounds(input: Partial<CleanupAnalysisBounds> = {}): CleanupAnalysisBounds {
  if (!cleanupObject(input) || Object.keys(input).some(key => !Object.hasOwn(MAX,key))) throw new Error('invalid cleanup analysis bounds');
  const result = { ...MAX,...input };
  for (const field of Object.keys(MAX) as (keyof CleanupAnalysisBounds)[])
    if (!Number.isSafeInteger(result[field]) || result[field] < 1 || result[field] > MAX[field]) throw new Error('invalid cleanup analysis bounds');
  return result;
}
class AnalysisLimit extends Error { constructor(readonly field: string) { super('cleanup analysis limit'); } }
class Budget {
  readonly started = performance.now();
  sourceRows = 0; reports = 0; nodes = 0; edges = 0; pages = 0; stateBytes = 0; payloadBytes = 0;
  constructor(readonly limits: CleanupAnalysisBounds) {}
  tick() { if (performance.now()-this.started >= this.limits.elapsedMs) throw new AnalysisLimit('elapsedMs'); }
  add(field: 'sourceRows'|'reports'|'nodes'|'edges'|'pages'|'stateBytes'|'payloadBytes', amount = 1) {
    this.tick(); if (amount > this.limits[field]-this[field]) throw new AnalysisLimit(field); this[field] += amount;
  }
  retain(value: unknown) { this.add('stateBytes',Buffer.byteLength(JSON.stringify(value))*4+256); }
  usage(): ReferenceAnalysis['usage'] { return { sourceRows: this.sourceRows, reports: this.reports, nodes: this.nodes, edges: this.edges,
    pages: this.pages, decodedBytes: String(this.payloadBytes), stateBytes: String(this.stateBytes) }; }
}
function json(text: string): unknown {
  let depth = 0, quoted = false, escaped = false;
  for (const character of text) {
    if (quoted) { if (escaped) escaped = false; else if (character === '\\') escaped = true; else if (character === '"') quoted = false; }
    else if (character === '"') quoted = true;
    else if (character === '{' || character === '[') { if (++depth > 12) throw new AnalysisLimit('jsonDepth'); }
    else if (character === '}' || character === ']') depth--;
  }
  return JSON.parse(text) as unknown;
}
interface Payload { sha256: string; sequenceSha256: string; bytes: string; text: string|null }
interface GraphState {
  analysis: ReferenceAnalysis; budget: Budget; invocations: Map<string,CleanupInvocationFact>;
  attempts: Map<string,CleanupAttemptFact>; headers: Map<string,CleanupCaptureHeader>; payloads: Map<string,Payload>; content: string[];
}
function payload(store: CleanupReadStore, header: CleanupCaptureHeader, budget: Budget, decodeLimit: number|null,
  block: (value: CleanupBlocker) => void, prefix?: readonly {sequence:number;text:string}[]): Payload|null {
  const node = captureNode({ invocationId: header.invocationId, captureId: header.id });
  if (header.state !== 'complete') { block({ code: header.state === 'pruned' ? 'pruned' : 'partial',node }); return null; }
  if (decodeLimit !== null && BigInt(header.logicalPayloadBytes) > BigInt(decodeLimit)) {
    block({ code: 'limit',node,limit: header.channel === 'report' ? 'reportBytes' : 'inputBytes' }); return null;
  }
  const raw = createHash('sha256'), sequence = createHash('sha256');
  let after = '0', total = 0n, prefixIndex = 0; const texts: string[] = [];
  while (true) {
    budget.add('pages');
    const page = store.readCleanupCapture({ invocationId: header.invocationId,captureId: header.id,after,limit: 20,byteBudget: 262144 });
    budget.tick();
    if (page.status !== 'present' || !isDeepStrictEqual(page.header,header)) {
      block({ code: page.status === 'missing' || page.status === 'foreign' || page.status === 'pruned' ? page.status : 'unstable',node }); return null;
    }
    if (page.blocked) { block({ code: page.blocked === 'byte-budget' ? 'limit' : 'partial',node,...(page.blocked === 'byte-budget' ? {limit:'payloadPageBytes'} : {}) }); return null; }
    for (const chunk of page.chunks) {
      budget.add('sourceRows'); budget.tick();
      if (cleanupCursor(chunk.sequence) !== cleanupCursor(after)+1n || Buffer.from(chunk.text).toString('utf8') !== chunk.text) {
        block({ code: 'partial',node }); return null;
      }
      if(prefix && prefixIndex<prefix.length){const expected=prefix[prefixIndex++]!;if(String(expected.sequence)!==chunk.sequence||expected.text!==chunk.text){block({code:'digest',node});return null;}}
      const bytes = Buffer.byteLength(chunk.text); budget.add('payloadBytes',bytes); total += BigInt(bytes);
      raw.update(chunk.text); sequence.update(JSON.stringify([chunk.sequence,String(bytes),cleanupHash(chunk.text)]));
      if (decodeLimit !== null) { if (total > BigInt(decodeLimit)) { block({code:'limit',node,limit:'inputBytes'}); return null; } budget.add('stateBytes',bytes*4);texts.push(chunk.text); }
      after = chunk.sequence;
    }
    if (page.nextSequence !== after || page.hasMore && !page.chunks.length) { block({code:'partial',node}); return null; }
    if (!page.hasMore) break;
  }
  if (prefix && prefixIndex!==prefix.length) {block({code:'digest',node});return null;}
  if (after !== header.lastSequence || total !== BigInt(header.logicalPayloadBytes)) { block({code:'digest',node}); return null; }
  const result = { sha256: raw.digest('hex'),sequenceSha256: sequence.digest('hex'),bytes:String(total),text:decodeLimit === null?null:texts.join('') };
  budget.retain({ ...result,text:null });
  return result;
}

function analyze(store: CleanupReadStore, budget: Budget): GraphState {
  const snapshot = store.readCleanupSnapshot(), invocations = new Map<string,CleanupInvocationFact>(), attempts = new Map<string,CleanupAttemptFact>();
  const headers = new Map<string,CleanupCaptureHeader>(), nodes = new Map<string,CleanupNode>(), edges = new Map<string,CleanupEdge>();
  const recognizedReports:ReferenceAnalysis['reports'][number][]=[];
  const roots = new Set<string>(), blockers = new Map<string,CleanupBlocker>(), payloads = new Map<string,Payload>(), content: string[] = [];
  const block = (value: CleanupBlocker) => { const key = JSON.stringify(value); if (!blockers.has(key)) { budget.retain(value); blockers.set(key,value); } };
  const addNode = (node: CleanupNode) => { const key=nodeKey(node); if (!nodes.has(key)) { budget.add('nodes');budget.retain(node);nodes.set(key,node); } return key; };
  const root = (node: CleanupNode) => { roots.add(addNode(node)); };
  const edge = (from: CleanupNode,to: CleanupNode,kind: CleanupEdgeKind) => {
    addNode(from);addNode(to);const value={from,to,kind},key=JSON.stringify([nodeKey(from),nodeKey(to),kind]);
    if (!edges.has(key)) { budget.add('edges');budget.retain(value);edges.set(key,value); }
  };
  const factHash = (kind: string,value: unknown) => { const record=JSON.stringify([kind,value]);budget.retain(record);content.push(record); };
  const opaque = (value: CleanupOpaque,source: NonNullable<CleanupBlocker['source']>) => {
    factHash(source,value);block({code:'opaque',node:null,id:value.id,cursor:value.cursor,source});
  };
  const pages = <T extends {cursor:string}>(kind: 'invocations'|'attempts'|'captures',read:(input:{after:string;through:string;limit:number;byteBudget:number})=>CleanupPage<T>,record:(value:T)=>void) => {
    let after='0';const through=snapshot.highWater[kind];cleanupCursor(through);
    while (true) {
      budget.add('pages');const page=read({after,through,limit:budget.limits.rowsPerPage,byteBudget:budget.limits.metadataPageBytes});budget.tick();
      if (page.through!==through || page.records.length>budget.limits.rowsPerPage) {block({code:'unstable',node:null});return;}
      for (const value of page.records) {
        budget.add('sourceRows');
        if (cleanupCursor(value.cursor)<=cleanupCursor(after) || cleanupCursor(value.cursor)>cleanupCursor(through)) {block({code:'unstable',node:null,cursor:value.cursor});return;}
        record(value);after=value.cursor;budget.tick();
      }
      if (page.blocked) {block({code:'limit',node:null,limit:'metadataPageBytes'});return;}
      if (page.nextCursor!==after || page.hasMore && !page.records.length) {block({code:'unstable',node:null,cursor:after});return;}
      if (!page.hasMore) { if(after!==through)block({code:'unstable',node:null,cursor:after});return; }
    }
  };
  const readPayload = (header: CleanupCaptureHeader,decodeLimit: number|null,prefix?: readonly {sequence:number;text:string}[]) => {
    const previous=payloads.get(header.id);
    if (!prefix && previous && (decodeLimit===null || previous.text!==null)) return previous;
    const value=payload(store,header,budget,decodeLimit,block,prefix);
    if (value) { payloads.set(header.id,{...value,text:null});factHash('payload',[nodeKey(captureNode({invocationId:header.invocationId,captureId:header.id})),value.sha256,value.sequenceSha256,value.bytes]); }
    return value;
  };
  const ownedCapture = (captureId: string,invocationId: string,attemptId: string|null,channel?: CleanupCaptureHeader['channel']) => {
    const header=headers.get(captureId),node=captureNode({invocationId,captureId});
    if (!header) { block({code:'missing',node});return null; }
    if (header.invocationId!==invocationId) {block({code:'foreign',node});return null;}
    if (header.attemptId!==attemptId || channel && header.channel!==channel) {block({code:'ownership',node});return null;}
    return header;
  };
  try {
    budget.retain(snapshot);factHash('snapshot',snapshot);
    pages('invocations',input=>store.pageCleanupInvocationFacts(input),value=>{
      if(value.status==='opaque'){opaque(value,'invocation');return;}budget.retain(value);invocations.set(value.id,value);root(invocationNode(value));
      if(value.inputCaptureId!==null)root(captureNode({invocationId:value.id,captureId:value.inputCaptureId}));factHash('invocation',value);
    });
    pages('attempts',input=>store.pageCleanupAttemptFacts(input),value=>{
      if(value.status==='opaque'){opaque(value,'attempt');return;}budget.retain(value);attempts.set(value.id,value);addNode(attemptNode(value));factHash('attempt',value);
    });
    pages('captures',input=>store.pageCleanupCaptureHeaders(input),value=>{
      if(value.status==='opaque'){opaque(value,'capture');return;}budget.retain(value);headers.set(value.id,value);const node=captureNode({invocationId:value.invocationId,captureId:value.id});
      addNode(node);if(value.channel==='report'||value.channel==='request')root(node);factHash('header',value);
    });
    // Retain every known metadata root before interpreting any payload that may
    // exhaust a byte/depth/deadline budget. Owner validation follows below.
    for(const invocation of invocations.values()){
      if(invocation.question!==null){const saved=headers.get(invocation.question);if(saved)root(captureNode({invocationId:saved.invocationId,captureId:invocation.question}));}
      for(const captureId of invocation.contexts){const saved=headers.get(captureId);if(saved)root(captureNode({invocationId:saved.invocationId,captureId}));}
    }
    const byAttempt=new Map<string,CleanupCaptureHeader[]>();
    for(const header of headers.values()) {
      budget.tick();
      if(!invocations.has(header.invocationId))block({code:'missing',node:{kind:'invocation',invocationId:header.invocationId}});
      if(header.attemptId!==null){const owner=attempts.get(header.attemptId);if(!owner || owner.invocationId!==header.invocationId)block({code:owner?'foreign':'missing',node:{kind:'attempt',invocationId:header.invocationId,attemptId:header.attemptId}});
        const list=byAttempt.get(header.attemptId)??[];budget.retain(header.id);list.push(header);byAttempt.set(header.attemptId,list);}
      if(header.channel==='report'||header.channel==='request') {
        root(captureNode({invocationId:header.invocationId,captureId:header.id}));
        const node=captureNode({invocationId:header.invocationId,captureId:header.id});
        if(header.channel==='report')budget.add('reports');
        const value=readPayload(header,header.channel==='report'?131072:393216);
        if(value?.text!==null&&value?.text!==undefined){try{const parsed=json(value.text);if(header.channel==='request'&&(!exact(parsed,['question','context'])||typeof parsed.question!=='string'||typeof parsed.context!=='string'))block({code:'opaque',node});}
          catch(error){if(error instanceof AnalysisLimit)throw error;block({code:'malformed',node});}}

      }
    }
    const ordinaryReports=new Set<string>(), ordinaryOwners=new Set<string>();
    for(const header of headers.values()) if(header.channel==='report') {
      const value=readPayload(header,131072); if(value?.text===null||value?.text===undefined) continue;
      try { if(ordinaryDeclaration(json(value.text))) {budget.retain([header.id,header.invocationId]);ordinaryReports.add(header.id);ordinaryOwners.add(header.invocationId);} }
      catch(error) {if(error instanceof AnalysisLimit)throw error;}
    }
    for(const invocation of [...invocations.values()].sort((a,b)=>compare(a.id,b.id))) {
      budget.tick();const from=invocationNode(invocation);
      if(invocation.inputCaptureId!==null) {
        root(captureNode({invocationId:invocation.id,captureId:invocation.inputCaptureId}));
        edge(from,captureNode({invocationId:invocation.id,captureId:invocation.inputCaptureId}),'input');
        const header=ownedCapture(invocation.inputCaptureId,invocation.id,null,'context'),value=header&&readPayload(header,393216);
        if(value?.text!==null&&value?.text!==undefined) {
          let parsed:unknown;try{parsed=json(value.text);}catch(error){if(error instanceof AnalysisLimit)throw error;block({code:'malformed',node:captureNode({invocationId:invocation.id,captureId:invocation.inputCaptureId})});}
          if(!exact(parsed,['inputs','question','contexts'])||(!exact(parsed.inputs,[])&&!isLearningWorkflow(invocation.workflow)&&!ordinaryOwners.has(invocation.id))||parsed.question!==invocation.question||!isDeepStrictEqual(parsed.contexts,invocation.contexts))
            block({code:'opaque',node:captureNode({invocationId:invocation.id,captureId:invocation.inputCaptureId})});
        }
      }
      if(invocation.question!==null){const saved=headers.get(invocation.question);
        if(!saved)block({code:'missing',node:null,id:invocation.question,source:'capture'});
        else {const node=captureNode({invocationId:saved.invocationId,captureId:invocation.question});root(node);edge(from,node,'question');
          if(invocations.get(saved.invocationId)?.runId!==invocation.runId)block({code:'foreign',node});
          else {const header=ownedCapture(invocation.question,saved.invocationId,null,'request');if(header)readPayload(header,393216);}}}
      for(const captureId of invocation.contexts){const header=headers.get(captureId);
        if(!header){block({code:'missing',node:null,id:captureId,source:'capture'});continue;}
        const node=captureNode({invocationId:header.invocationId,captureId});root(node);edge(from,node,'selected-context');
        if(invocations.get(header.invocationId)?.runId!==invocation.runId)block({code:'foreign',node});else readPayload(header,null);}
    }
    const operations=new Map<string,Extract<ReturnType<CleanupReadStore['readCleanupOperation']>,{status:'known'}>>();
    for(const attempt of [...attempts.values()].sort((a,b)=>compare(nodeKey(attemptNode(a)),nodeKey(attemptNode(b))))) {
      budget.tick();const from=attemptNode(attempt),owner=invocations.get(attempt.invocationId),opNode=operationNode(attempt);
      if(!owner||owner.runId!==attempt.runId)block({code:owner?'foreign':'missing',node:from});edge(from,opNode,'operation');
      const opKey=nodeKey(opNode);let operation=operations.get(opKey);
      if(!operation){budget.add('pages');budget.add('sourceRows');const read=store.readCleanupOperation({runId:attempt.runId,operationId:attempt.operationId});budget.tick();
        if(read.status==='known'){operation=read;budget.retain(read);operations.set(opKey,read);factHash('operation',read);}
        else {block({code:read.status==='missing'||read.status==='foreign'?read.status:'opaque',node:opNode});if(read.status==='opaque')opaque(read,'operation');}}
      if(operation&&(operation.operationKey!==attempt.operationKey||operation.kind!==attempt.kind||attempt.loopKey!==null&&operation.loopKey!==attempt.loopKey))block({code:'ownership',node:opNode});
      for(const [priorId,kind] of [[attempt.priorAttemptId,'prior-attempt'],[attempt.agent?.reusedAttemptId??null,'reused-attempt']] as const){
        if(priorId===null)continue;const prior=attempts.get(priorId);
        if(!prior){block({code:'missing',node:null,id:priorId,source:'attempt'});continue;}
        const node:CleanupNode={kind:'attempt',invocationId:prior.invocationId,attemptId:priorId};edge(from,node,kind);
        if(prior.runId!==attempt.runId)block({code:'foreign',node});
        else if(cleanupCursor(prior.cursor)>=cleanupCursor(attempt.cursor)||prior.kind!==attempt.kind)block({code:'invalid-lineage',node});
      }
      const owned=byAttempt.get(attempt.id)??[];
      for(const header of owned)edge(from,captureNode({invocationId:header.invocationId,captureId:header.id}),'owned-capture');
      if(attempt.kind==='command') {
        const contexts=owned.filter(header=>header.channel==='context');
        if(!contexts.length&&(attempt.launch==='started'||owned.length))block({code:'missing',node:from});
        if(contexts.length>1)block({code:'ownership',node:from});
        for(const header of contexts){root(captureNode({invocationId:header.invocationId,captureId:header.id}));const value=readPayload(header,393216);if(!value||value.text===null)continue;
          let parsed:unknown;try{parsed=json(value.text);}catch(error){if(error instanceof AnalysisLimit)throw error;block({code:'malformed',node:from});continue;}
          if(!exact(parsed,['argv','cwd','env','shell','required','timeoutMs','childScope','limitation'])||!Array.isArray(parsed.argv)||!parsed.argv.length||!parsed.argv.every(item=>typeof item==='string'&&!item.includes('\0'))
            ||typeof parsed.cwd!=='string'||!cleanupObject(parsed.env)||Object.values(parsed.env).some(item=>typeof item!=='string')
            ||!(parsed.shell===false||typeof parsed.shell==='string')||typeof parsed.required!=='boolean'||!Number.isSafeInteger(parsed.timeoutMs)||Number(parsed.timeoutMs)<1
            ||!['process-group','unknown'].includes(String(parsed.childScope))||typeof parsed.limitation!=='string')block({code:'opaque',node:from});
        }
      } else if(attempt.agent) {
        root(from);const agent=attempt.agent;
        for(const [captureId,channel]of [[agent.inputsCaptureId,'context'],[agent.resultCaptureId,'result'],[agent.outputCaptureId,null],[agent.validatedResultCaptureId,'validated-result']] as const){
          if(captureId===null)continue;const header=ownedCapture(captureId,attempt.invocationId,attempt.id,channel??undefined);if(header&&channel===null&&!(captureId===agent.resultCaptureId?header.channel==='result':['stdout','stderr'].includes(header.channel)))block({code:'ownership',node:from});edge(from,captureNode({invocationId:attempt.invocationId,captureId}),'owned-capture');
          if(header&&channel==='context'){const value=readPayload(header,393216);if(value?.text){let parsed:unknown;try{parsed=json(value.text);}catch(error){if(error instanceof AnalysisLimit)throw error;block({code:'malformed',node:from});continue;}
            if(exact(parsed,['inputs','purpose','context','sourceCaptureId'])&&cleanupId(parsed.sourceCaptureId)){edge(from,captureNode({invocationId:attempt.invocationId,captureId:parsed.sourceCaptureId}),'source-input');const source=ownedCapture(parsed.sourceCaptureId,attempt.invocationId,null,'context');if(source)readPayload(source,393216);}}}
        }
        // Only the closed learning contracts below may interpret an agent context.
        if(!isLearningWorkflow(owner?.workflow??null)&&!ordinaryOwners.has(attempt.invocationId))block({code:'opaque',node:from});
      } else if(owned.length) {root(from);block({code:'opaque',node:from});}
    }
    const graph={invocations,attempts,headers,report:(value:ReferenceAnalysis['reports'][number])=>recognizedReports.push(value),read:readPayload,owned:ownedCapture,edge,block,parse:json,retain:(value:unknown)=>budget.retain(value),tick:()=>budget.tick(),
      event(invocationId:string,cursor:string){budget.add('pages');budget.add('sourceRows');const event=store.readCleanupEvent({invocationId,cursor});budget.tick();factHash('event',event);return event;}};
    const ordinary=ordinaryReferenceInterpreter(graph);
    for(const id of ordinaryReports) ordinary.inspect(headers.get(id)!);
    analyzeLearningReferences(graph,ordinaryReports);
    for(const attempt of attempts.values())if(attempt.priorAttemptId!==null){const prior=attempts.get(attempt.priorAttemptId);
      if(prior&&operations.get(nodeKey(operationNode(prior)))?.loopKey!==operations.get(nodeKey(operationNode(attempt)))?.loopKey)
        block({code:'invalid-lineage',node:attemptNode(attempt)});}
  } catch(error) {
    const value:CleanupBlocker={code:error instanceof AnalysisLimit?'limit':'unstable',node:null,...(error instanceof AnalysisLimit?{limit:error.field}:{})};
    blockers.set(JSON.stringify(value),value);
  }
  const adjacency=new Map<string,string[]>();
  for(const value of edges.values()){const from=nodeKey(value.from),list=adjacency.get(from)??[];list.push(nodeKey(value.to));adjacency.set(from,list);}
  for(const list of adjacency.values())list.sort(compare);
  const colors=new Map<string,number>(),depths=new Map<string,number>(),protectedKeys=new Set<string>(roots);
  try{
    for(const key of [...nodes.keys()].sort(compare)){
      if(colors.has(key))continue;const stack:{key:string;index:number}[]=[{key,index:0}];colors.set(key,1);
      while(stack.length){budget.tick();const frame=stack.at(-1)!,neighbors=adjacency.get(frame.key)??[];
        if(frame.index===neighbors.length){let dependencyDepth=0;for(const neighbor of neighbors)dependencyDepth=Math.max(dependencyDepth,depths.get(neighbor)??0);
          if(dependencyDepth+1>128)throw new AnalysisLimit('dependencyDepth');depths.set(frame.key,dependencyDepth+1);colors.set(frame.key,2);stack.pop();continue;}const next=neighbors[frame.index++]!;
        if(colors.get(next)===1)block({code:'cycle',node:nodes.get(next)??null});
        else if(!colors.has(next)){if(stack.length>=128)throw new AnalysisLimit('dependencyDepth');colors.set(next,1);stack.push({key:next,index:0});}
      }
    }
    const expanded=new Set<string>(),pending=[...roots].sort(compare);while(pending.length){budget.tick();const key=pending.pop()!;if(expanded.has(key))continue;expanded.add(key);protectedKeys.add(key);for(const next of adjacency.get(key)??[])pending.push(next);}
  }catch(error){const value:CleanupBlocker={code:'limit',node:null,limit:error instanceof AnalysisLimit?error.field:'stateBytes'};blockers.set(JSON.stringify(value),value);}
  // An attempt dependency includes every actual owned capture and its entire
  // prior/reuse chain, even where the producer sampled no bytes from that stream.
  // Complete content identity therefore follows reachability, not just decoding.
  try {
    for(const key of [...protectedKeys].sort(compare)) {
      budget.tick();const node=nodes.get(key);if(node?.kind!=='capture')continue;
      const header=headers.get(node.captureId);
      if(!header){block({code:'missing',node});continue;}
      if(header.invocationId!==node.invocationId){block({code:'foreign',node});continue;}
      const cap=header.channel==='report'?131072:['context','request'].includes(header.channel)?393216:null;
      if(cap!==null&&BigInt(header.logicalPayloadBytes)>BigInt(cap)) {
        block({code:'limit',node,limit:header.channel==='report'?'reportBytes':'inputBytes'});continue;
      }
      readPayload(header,null);
    }
  }catch(error){const value:CleanupBlocker={code:error instanceof AnalysisLimit?'limit':'unstable',node:null,
    ...(error instanceof AnalysisLimit?{limit:error.field}:{})};blockers.set(JSON.stringify(value),value);}
  const sortedEdges=[...edges.entries()].sort(([a],[b])=>compare(a,b)).map(([,value])=>value);
  const protectedNodes=[...protectedKeys].sort(compare).map(key=>nodes.get(key)!).filter(Boolean);
  let sortedBlockers=[...blockers.entries()].sort(([a],[b])=>compare(a,b)).map(([,value])=>value);
  const graphSha256=cleanupHash(JSON.stringify({version:1,nodes:[...nodes.keys()].sort(compare),roots:[...roots].sort(compare),edges:sortedEdges}));
  const snapshotSha256=sortedBlockers.length?null:cleanupHash(JSON.stringify({domain:'factory-cleanup-content-v1',content:content.sort(compare),graphSha256}));
  try{budget.tick();}catch{const value:CleanupBlocker={code:'limit',node:null,limit:'elapsedMs'};blockers.set(JSON.stringify(value),value);
    sortedBlockers=[...blockers.entries()].sort(([a],[b])=>compare(a,b)).map(([,value])=>value);}
  const complete=!sortedBlockers.length;
  const analysis:ReferenceAnalysis={status:complete?'complete':'blocked',snapshot,snapshotSha256:complete?snapshotSha256:null,
    graphSha256,protected:protectedNodes,edges:sortedEdges,reports:recognizedReports,blockers:sortedBlockers,usage:budget.usage()};
  return {analysis,budget,invocations,attempts,headers,payloads,content};
}

/** Bounded advisory graph. Exact learning v1 and closed library action compatibility reports are understood; other reports block payload eligibility. */
export function analyzeCleanupReferences(store: CleanupReadStore,input:Partial<CleanupAnalysisBounds>={}):ReferenceAnalysis {
  return analyze(store,new Budget(bounds(input))).analysis;
}

function selectionKeys(selection:CleanupSelection):CleanupCaptureKey[] {
  if(!cleanupObject(selection))throw new Error('invalid cleanup selection');
  if(selection.kind==='backups'){
    if(!exact(selection,['kind','backups'])||!Array.isArray(selection.backups)||selection.backups.length<1)throw new Error('invalid cleanup selection');
    if(selection.backups.length>20)throw new AnalysisLimit('selectionBackups');
    let previous='';for(const key of selection.backups){if(!exact(key,['operationId','backupId'])||!cleanupId(key.operationId)||!cleanupId(key.backupId))throw new Error('invalid cleanup selection');
      const current=JSON.stringify([key.operationId,key.backupId]);if(previous&&compare(previous,current)>=0)throw new Error('invalid cleanup selection');previous=current;}return [];
  }
  if(!exact(selection,['kind','captures','exceptional','reviewNonOutput'])||selection.kind!=='captures'||!Array.isArray(selection.captures)||selection.captures.length<1)throw new Error('invalid cleanup selection');
  if(selection.captures.length>100)throw new AnalysisLimit('selectionCaptures');
  const selected=new Set<string>();let previous='';
  for(const key of selection.captures){if(!exact(key,['invocationId','captureId'])||!cleanupId(key.invocationId)||!cleanupId(key.captureId))throw new Error('invalid cleanup selection');const current=nodeKey(captureNode({invocationId:key.invocationId,captureId:key.captureId}));if(previous&&compare(previous,current)>=0)throw new Error('invalid cleanup selection');selected.add(current);previous=current;}
  const exceptional=new Set<string>();for(const [list,seen]of [[selection.exceptional,exceptional],[selection.reviewNonOutput,new Set<string>()]]as const){
    if(!Array.isArray(list)||list.length>100)throw new Error('invalid cleanup selection');let prior='';for(const key of list){if(!exact(key,['invocationId','captureId'])||!cleanupId(key.invocationId)||!cleanupId(key.captureId))throw new Error('invalid cleanup selection');const current=nodeKey(captureNode({invocationId:key.invocationId,captureId:key.captureId}));
      if(!selected.has(current)||prior&&compare(prior,current)>=0||seen!==exceptional&&exceptional.has(current))throw new Error('invalid cleanup selection');seen.add(current);prior=current;}}
  return [...selection.captures];
}

/** Repository resolution precedes analysis. No caller can supply clearance, ownership, a view or a digest. */
export async function inspectCleanupSelection(repository:string,selection:CleanupSelection,input:Partial<CleanupAnalysisBounds>={}):Promise<CleanupImpact>{
  const result:CleanupImpact={advisory:true,status:'blocked',impactSha256:null,snapshotSha256:null,blockers:[],captures:[],backups:[],pages:[],selectedLogicalBytes:null};
  let keys:CleanupCaptureKey[],budget:Budget;
  try{keys=selectionKeys(selection);budget=new Budget(bounds(input));}catch(error){return {...result,blockers:[{code:error instanceof AnalysisLimit?'limit':'malformed',node:null,...(error instanceof AnalysisLimit?{limit:error.field}:{})}]};}
  let identity:Awaited<ReturnType<typeof repositoryIdentity>>;
  try{identity=await repositoryIdentity(repository);}catch{return {...result,blockers:[{code:'unstable',node:null}]};}
  // Repository discovery may execute Git; no Git or authored code runs after this point.
  let store:CleanupReadStore|undefined;
  const blockers:CleanupBlocker[]=[],captures:CleanupImpactCapture[]=[];
  try{
    store=openCleanupReadStore(identity.common);budget.tick();
    const tuples=selection.kind==='backups'?selection.backups:[];
    const authority=readCleanupSnapshotAuthority(identity.root,identity.common,store,tuples,()=>budget.tick());
    result.backups=authority.backups;
    budget.tick();budget.retain(authority);
    if(authority.recovery.status!=='clear'||authority.sha256===null)blockers.push({code:'unassessed-recovery',node:null});
    // Exact backup ownership has no payload-closure dependency. Its authority,
    // DTOs, snapshot, deadline and output still consume the global budget.
    const state=selection.kind==='captures'?analyze(store,budget):null,analysis=state?.analysis;
    const snapshot=analysis?.snapshot??store.readCleanupSnapshot();
    if(!analysis)budget.retain(snapshot);
    if(analysis)blockers.push(...analysis.blockers);
    const protectedKeys=new Set(analysis?.protected.map(nodeKey)??[]);let total=0n,measured=true;
    const selectedDigests:unknown[]=[];
    for(const key of keys){budget.tick();const node=captureNode(key),header=state?.headers.get(key.captureId);
      const row:CleanupImpactCapture={key,disposition:'refused',logicalBytes:null,payloadSha256:null,affectedReports:[],affectedAttempts:[],verificationWillFail:false,requiresExplicitConfirmation:false};
      captures.push(row);budget.retain(row);
      if(!header){blockers.push({code:'missing',node});measured=false;continue;}
      if(header.invocationId!==key.invocationId){blockers.push({code:'foreign',node});measured=false;continue;}
      row.logicalBytes=header.logicalPayloadBytes;total+=BigInt(header.logicalPayloadBytes);
      const value=state?.payloads.get(header.id)??payload(store,header,budget,null,value=>blockers.push(value));
      if(value){row.payloadSha256=value.sha256;selectedDigests.push([nodeKey(node),value.sha256,value.sequenceSha256,value.bytes]);}else measured=false;
      const owner=state?.invocations.get(key.invocationId);
      if(!owner||owner.stage!=='finalized'||owner.outcome===null)blockers.push({code:'unassessed-recovery',node});
      if(protectedKeys.has(nodeKey(node))||['report','request'].includes(header.channel))row.disposition='protected';
      else if(header.state==='pruned'){row.disposition='already-pruned';blockers.push({code:'pruned',node});}
      else if(header.channel==='stdout'||header.channel==='stderr'){
        const attempt=header.attemptId===null?undefined:state?.attempts.get(header.attemptId);
        if(!attempt||attempt.kind!=='command'||attempt.invocationId!==key.invocationId||attempt.runId!==owner?.runId)
          blockers.push({code:'ownership',node});
        else row.disposition='eligible';
      }
      else row.disposition='protected';
    }
    if(selection.kind==='captures'&&selection.exceptional.length)for(const key of selection.exceptional)blockers.push({code:'opaque',node:captureNode(key)});
    const after=readCleanupSnapshotAuthority(identity.root,identity.common,store,tuples,()=>budget.tick());budget.tick();
    if(authority.sha256===null||after.sha256!==authority.sha256||!isDeepStrictEqual(after.backups,authority.backups))blockers.push({code:'unstable',node:null});
    if(selection.kind==='backups')for(const backup of authority.backups)if(backup.status!=='owned')blockers.push({code:'ownership',node:null});
    const unique=[...new Map(blockers.map(value=>[JSON.stringify(value),value])).entries()].sort(([a],[b])=>compare(a,b)).map(([,value])=>value);
    if(unique.length)for(const row of captures)if(row.disposition==='eligible')row.disposition='refused';
    result.captures=captures;result.blockers=unique;result.selectedLogicalBytes=keys.length&&measured?String(total):null;
    const records=[...captures,...authority.backups,...unique];const pages:CleanupImpact['pages'][number][]=[];
    let page:typeof records=[];let bytes=256;
    for(const record of records){budget.tick();const size=Buffer.byteLength(JSON.stringify(record))+1;if(size+256>262144)throw new AnalysisLimit('outputPageBytes');
      if(page.length===100||bytes+size>262144){budget.add('pages');pages.push({index:pages.length,sha256:cleanupHash(JSON.stringify(page)),records:page});page=[];bytes=256;}
      page.push(record);bytes+=size;
    }
    if(page.length){budget.add('pages');pages.push({index:pages.length,sha256:cleanupHash(JSON.stringify(page)),records:page});}result.pages=pages;
    if(!unique.length&&(selection.kind==='backups'||analysis?.snapshotSha256!=null)){
      result.status='inspectable';result.snapshotSha256=cleanupHash(JSON.stringify({domain:'factory-cleanup-selected-content-v1',snapshot,
        referenceSnapshot:analysis?.snapshotSha256??null,authority:authority.sha256,selectedDigests}));
      result.impactSha256=cleanupHash(JSON.stringify({domain:'factory-cleanup-impact-v1',selection,snapshotSha256:result.snapshotSha256,captures,backups:authority.backups,pages}));
    }
    budget.tick();
    return result;
  }catch(error){for(const row of captures)if(row.disposition==='eligible')row.disposition='refused';return {...result,captures,pages:[],status:'blocked',impactSha256:null,snapshotSha256:null,
    blockers:[...blockers,{code:error instanceof AnalysisLimit?'limit':'unstable',node:null,...(error instanceof AnalysisLimit?{limit:error.field}:{})}]};}
  finally{store?.close();}
}
