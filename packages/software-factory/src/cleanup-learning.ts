import { isDeepStrictEqual as equal } from 'node:util';
import { actionReferenceInterpreter } from './cleanup-actions.js';
import { cleanupCursor, cleanupHash, cleanupId, cleanupObject, type CleanupAttemptFact, type CleanupCaptureHeader,
  type CleanupInvocationFact, type CleanupEventRead } from './cleanup-read.js';
import type { CleanupBlocker, CleanupEdgeKind, CleanupNode, ReferenceAnalysis } from './cleanup-references.js';

type ObjectValue = Record<string, unknown>;
type Source = { invocationId: string; attemptIds?: string[]; eventCursors?: string[] };
type Evidence = { invocationId: string; attemptId?: string; eventCursor?: string; captureId?: string };
type Target = { scope: 'repository'|'shared'; path: string };
type Proposal = { key: string; summary: string; target: Target; diff?: string;
  candidateCapture?: { invocationId: string; captureId: string }; supportingEvidence: Evidence[]; contraryEvidence: Evidence[]; suggestedCases: string[] };
type Limitation = { invocationId: string; kind: string; reference?: string };
type Extraction = { version: 1; suppliedSources: Source[];
  examinedSources: { invocationId: string; outcome: string; attemptIds: string[]; eventCursors: string[]; captureIds: string[] }[];
  captureLimitations: Limitation[]; proposals: Proposal[]; proposalResultCaptureId: string;
  proposalValidatedResultCaptureId?: string; noProposalReason?: string };
type Chunk = { sequence: number; text: string };
type Reference = { invocationId: string; captureId: string; sha256: string };
type CaseInput = { key: string; criteria: string; sourceSuggestion?: string; argv: string[]; timeoutMs: number };
type Objective = { attemptId: string; exitCode: number|null; cleanup: string };
type Review = { judgment: 'pass'|'fail'|'uncertain'; reason: string; attemptId: string; resultCaptureId: string;
  inputsCaptureId: string|null; effectivePermissions: string|null; effectiveProfile: string|null };
type CaseResult = { key: string; criteria: string; sourceSuggestion?: string;
  settings: { argv: string[]; cwd: string; timeoutMs: number; repetitions: 2 };
  baseline: { objective: Objective[]; review: Review }; candidate: { objective: Objective[]; review: Review } };
type EvaluationLimitation = { kind: string; reference?: string };
type Evaluation = { version: 1; suppliedReferences: { extraction: { invocationId: string; proposalKey: string }; baseline: Reference; candidate: Reference };
  target: Target|null; extractionReport: { captureId: string; sha256: string }|null;
  extractionResult: { attemptId: string; rawCaptureId: string; validatedCaptureId: string }|null;
  proposalSuggestedCases: string[]; settings: { cases: CaseInput[]; repetitions: 2; commandRequired: false;
    review: { profile: string|null; purpose:'review';requestedPermissions:'read-only';reuse:false } };
  cases: CaseResult[]; limitations: EvaluationLimitation[]; contraryCases: string[]; assessment: 'supported'|'unsupported'|'inconclusive';
  resolved?: { baselineSha256: string; candidateSha256: string } };
export interface LearningGraph {
  invocations: ReadonlyMap<string,CleanupInvocationFact>; attempts: ReadonlyMap<string,CleanupAttemptFact>;
  headers: ReadonlyMap<string,CleanupCaptureHeader>;
  read(header: CleanupCaptureHeader, limit: number|null, prefix?: readonly Chunk[]): { text: string|null; sha256: string }|null;
  owned(id: string, invocationId: string, attemptId: string|null, channel?: CleanupCaptureHeader['channel']): CleanupCaptureHeader|null;
  event(invocationId: string,cursor: string): CleanupEventRead;
  edge(from: CleanupNode,to: CleanupNode,kind: CleanupEdgeKind): void;
  report(value: ReferenceAnalysis['reports'][number]): void;
  block(value: CleanupBlocker): void; parse(text: string): unknown; retain(value: unknown): void; tick(): void;
}
const capture = (invocationId: string,captureId: string): CleanupNode => ({ kind:'capture',invocationId,captureId });
const attempt = (fact: CleanupAttemptFact): CleanupNode => ({ kind:'attempt',invocationId:fact.invocationId,attemptId:fact.id });
const invocation = (invocationId: string): CleanupNode => ({ kind:'invocation',invocationId });
const text = (value: unknown,max: number,empty = false): value is string => typeof value==='string' && (empty||!!value.trim())
  && !value.includes('\0') && Buffer.byteLength(value)<=max && Buffer.from(value).toString('utf8')===value;
const shape = (value: unknown,required: readonly string[],optional: readonly string[] = []): value is ObjectValue => cleanupObject(value)
  && required.every(key=>Object.hasOwn(value,key)) && Object.keys(value).every(key=>required.includes(key)||optional.includes(key));
const list = (value: unknown,max: number,check: (item: unknown)=>boolean,min = 0): value is unknown[] => Array.isArray(value)
  && value.length>=min && value.length<=max && value.every(check);
const ids = (value: unknown,max: number) => list(value,max,cleanupId) && new Set(value).size===value.length;
const cursor = (value: unknown): value is string => { try { return typeof value==='string'&&cleanupCursor(value)>0n; } catch { return false; } };
const cursors = (value: unknown,max: number) => list(value,max,cursor) && new Set(value).size===value.length;
const namedKey = (value: unknown) => text(value,80)&&/^[A-Za-z0-9][A-Za-z0-9_-]*$/.test(value);
const target = (value: unknown): value is Target => shape(value,['scope','path'])&&['repository','shared'].includes(String(value.scope))
  && text(value.path,512)&&!value.path.startsWith('/')&&!/^[A-Za-z]:/.test(value.path)&&!/[\\\x00-\x1f\x7f]/.test(value.path)
  && value.path.split('/').every(part=>!!part&&part!=='.'&&part!=='..');
const source = (value: unknown): value is Source => shape(value,['invocationId'],['attemptIds','eventCursors'])&&cleanupId(value.invocationId)
  && (value.attemptIds===undefined||ids(value.attemptIds,12))&&(value.eventCursors===undefined||cursors(value.eventCursors,12));
const evidence = (value: unknown): value is Evidence => shape(value,['invocationId'],['attemptId','eventCursor','captureId'])&&cleanupId(value.invocationId)
  && ['attemptId','eventCursor','captureId'].filter(key=>Object.hasOwn(value,key)).length===1
  && (value.attemptId===undefined||cleanupId(value.attemptId))&&(value.captureId===undefined||cleanupId(value.captureId))
  && (value.eventCursor===undefined||cursor(value.eventCursor));
const proposal = (value: unknown): value is Proposal => shape(value,['key','summary','target','supportingEvidence','contraryEvidence','suggestedCases'],['diff','candidateCapture'])
  && namedKey(value.key)&&text(value.summary,2048)&&target(value.target)&&(value.diff===undefined)!==(value.candidateCapture===undefined)
  && (value.diff===undefined||text(value.diff,16384))&&(value.candidateCapture===undefined||shape(value.candidateCapture,['invocationId','captureId'])
    &&cleanupId(value.candidateCapture.invocationId)&&cleanupId(value.candidateCapture.captureId))
  && list(value.supportingEvidence,16,evidence,1)&&list(value.contraryEvidence,16,evidence)&&list(value.suggestedCases,12,item=>text(item,1024),1);
const limitationKinds = new Set(['attempt_pages_unexamined','capture_pages_unexamined','selected_attempt_unexamined','event_ownership_unexamined',
  'captures_unexamined','text_budget_exhausted','capture_text_unexamined','capture_open','capture_partial','capture_unknown','capture_pruned']);
function extraction(value: unknown): value is Extraction {
  return shape(value,['version','suppliedSources','examinedSources','captureLimitations','proposals','proposalResultCaptureId'],['proposalValidatedResultCaptureId','noProposalReason'])
    &&value.version===1&&list(value.suppliedSources,6,source,1)&&new Set(value.suppliedSources.map(item=>(item as Source).invocationId)).size===value.suppliedSources.length
    &&list(value.examinedSources,6,item=>shape(item,['invocationId','outcome','attemptIds','eventCursors','captureIds'])&&cleanupId(item.invocationId)
      &&['succeeded','failed','interrupted','needs_input'].includes(String(item.outcome))&&ids(item.attemptIds,60)&&cursors(item.eventCursors,12)&&ids(item.captureIds,40),1)
    &&value.examinedSources.length===value.suppliedSources.length
    &&list(value.captureLimitations,1000,item=>shape(item,['invocationId','kind'],['reference'])&&cleanupId(item.invocationId)&&typeof item.kind==='string'
      &&limitationKinds.has(item.kind)&&(item.reference===undefined||cleanupId(item.reference)))
    &&list(value.proposals,4,proposal)&&new Set(value.proposals.map(item=>(item as Proposal).key)).size===value.proposals.length
    &&cleanupId(value.proposalResultCaptureId)&&(value.proposalValidatedResultCaptureId===undefined||cleanupId(value.proposalValidatedResultCaptureId))
    &&(value.proposals.length?value.noProposalReason===undefined:text(value.noProposalReason,2048));
}
const sha = (value: unknown): value is string => typeof value==='string'&&/^[0-9a-f]{64}$/.test(value);
const reference = (value: unknown): value is Reference => shape(value,['invocationId','captureId','sha256'])&&cleanupId(value.invocationId)&&cleanupId(value.captureId)&&sha(value.sha256);
const argv = (value: unknown) => list(value,16,item=>text(item,2048,true),1);
const timeout = (value: unknown) => Number.isSafeInteger(value)&&Number(value)>=100&&Number(value)<=30000;
const caseInput = (value: unknown): value is CaseInput => shape(value,['key','criteria','argv','timeoutMs'],['sourceSuggestion'])&&namedKey(value.key)
  &&text(value.criteria,1024)&&(value.sourceSuggestion===undefined||text(value.sourceSuggestion,1024))&&argv(value.argv)&&timeout(value.timeoutMs);
const evaluationLimitations = new Set(['source_unended','capture_unexamined','capture_missing_or_foreign','capture_byte_limit','capture_text_unexamined',
  'capture_pages_unexamined','capture_digest_mismatch','review_attempt_unverified','review_inputs_byte_limit','review_inputs_unexamined','review_inputs_invalid',
  'extraction_not_succeeded','extraction_report_missing_or_partial','extraction_report_unexamined','extraction_report_ambiguous','extraction_report_byte_limit',
  'extraction_report_invalid','extraction_workflow_unverified','extraction_result_capture_missing_or_partial','extraction_result_attempt_unverified',
  'extraction_validated_result_missing_or_partial','extraction_validated_result_unverified','extraction_validated_result_byte_limit','extraction_validated_result_unexamined',
  'extraction_validated_result_invalid','extraction_proposals_mismatch','extraction_inputs_missing_or_partial','extraction_inputs_unverified','extraction_inputs_byte_limit',
  'extraction_inputs_unexamined','extraction_inputs_invalid','extraction_sources_mismatch','extraction_candidate_unexamined','extraction_evidence_unexamined',
  'extraction_source_limitations','nondeterministic_objective','uncertain_review','review_objective_disagreement','no_observed_improvement',
  'unsupported_target_scope','diff_only_candidate_requires_exact_materialization','identical_variants','suggested_case_unexamined','review_not_read_only',
  ...['capture','review_inputs','extraction_report'].flatMap(prefix=>['open','partial','unknown','pruned'].map(state=>`${prefix}_${state}`))]);
function evaluation(value: unknown): value is Evaluation {
  const side = (item: unknown) => shape(item,['objective','review'])&&list(item.objective,2,entry=>shape(entry,['attemptId','exitCode','cleanup'])
    &&cleanupId(entry.attemptId)&&(entry.exitCode===null||Number.isSafeInteger(entry.exitCode))&&text(entry.cleanup,256),2)
    &&shape(item.review,['judgment','reason','attemptId','resultCaptureId','inputsCaptureId','effectivePermissions','effectiveProfile'])
    &&['pass','fail','uncertain'].includes(String(item.review.judgment))&&text(item.review.reason,2048)&&cleanupId(item.review.attemptId)&&cleanupId(item.review.resultCaptureId)
    &&(item.review.inputsCaptureId===null||cleanupId(item.review.inputsCaptureId))&&(item.review.effectivePermissions===null||text(item.review.effectivePermissions,256))
    &&(item.review.effectiveProfile===null||text(item.review.effectiveProfile,80));
  return shape(value,['version','suppliedReferences','target','extractionReport','extractionResult','proposalSuggestedCases','settings','cases','limitations','contraryCases','assessment'],['resolved'])
    &&value.version===1&&shape(value.suppliedReferences,['extraction','baseline','candidate'])
    &&shape(value.suppliedReferences.extraction,['invocationId','proposalKey'])&&cleanupId(value.suppliedReferences.extraction.invocationId)&&text(value.suppliedReferences.extraction.proposalKey,80)
    &&reference(value.suppliedReferences.baseline)&&reference(value.suppliedReferences.candidate)&&(value.target===null||target(value.target))
    &&(value.extractionReport===null||shape(value.extractionReport,['captureId','sha256'])&&cleanupId(value.extractionReport.captureId)&&sha(value.extractionReport.sha256))
    &&(value.extractionResult===null||shape(value.extractionResult,['attemptId','rawCaptureId','validatedCaptureId'])&&Object.values(value.extractionResult).every(cleanupId))
    &&list(value.proposalSuggestedCases,12,item=>text(item,1024))
    &&shape(value.settings,['cases','repetitions','commandRequired','review'])&&list(value.settings.cases,3,caseInput,1)
    &&new Set(value.settings.cases.map(item=>(item as CaseInput).key)).size===value.settings.cases.length&&value.settings.repetitions===2&&value.settings.commandRequired===false
    &&shape(value.settings.review,['profile','purpose','requestedPermissions','reuse'])&&(value.settings.review.profile===null||text(value.settings.review.profile,80))
    &&value.settings.review.purpose==='review'&&value.settings.review.requestedPermissions==='read-only'&&value.settings.review.reuse===false
    &&list(value.cases,3,item=>shape(item,['key','criteria','settings','baseline','candidate'],['sourceSuggestion'])&&namedKey(item.key)&&text(item.criteria,1024)
      &&(item.sourceSuggestion===undefined||text(item.sourceSuggestion,1024))&&shape(item.settings,['argv','cwd','timeoutMs','repetitions'])&&argv(item.settings.argv)
      &&text(item.settings.cwd,393216)&&timeout(item.settings.timeoutMs)&&item.settings.repetitions===2&&side(item.baseline)&&side(item.candidate))
    &&list(value.limitations,1000,item=>shape(item,['kind'],['reference'])&&typeof item.kind==='string'&&evaluationLimitations.has(item.kind)
      &&(item.reference===undefined||text(item.reference,2048)))
    &&list(value.contraryCases,3,namedKey)&&new Set(value.contraryCases).size===value.contraryCases.length
    &&['supported','unsupported','inconclusive'].includes(String(value.assessment))
    &&(value.cases.length?shape(value.resolved,['baselineSha256','candidateSha256'])&&sha(value.resolved.baselineSha256)&&sha(value.resolved.candidateSha256)
      &&value.extractionReport!==null&&value.extractionResult!==null:value.resolved===undefined&&value.assessment==='inconclusive');
}
function profile(value: unknown): boolean {
  if(!shape(value,[],['harness','model','reasoning','permissions','prompt','skills','skillDelivery','requiredCapabilities']))return false;
  for(const key of ['harness','model','reasoning'])if(value[key]!==undefined&&!text(value[key],393216))return false;
  return (value.permissions===undefined||['read-only','workspace-write'].includes(String(value.permissions)))
    &&(value.skillDelivery===undefined||['native','instructions'].includes(String(value.skillDelivery)))
    &&(value.prompt===undefined||text(value.prompt,393216,true)||shape(value.prompt,['file'])&&text(value.prompt.file,393216))
    &&(value.skills===undefined||list(value.skills,100,item=>shape(item,['name','file'],['resources'])&&text(item.name,393216)&&text(item.file,393216)
      &&(item.resources===undefined||list(item.resources,100,entry=>text(entry,393216)))))
    &&(value.requiredCapabilities===undefined||list(value.requiredCapabilities,100,item=>text(item,393216)));
}
function effective(value: unknown): value is ObjectValue {
  return shape(value,['layers','profile','harness','permissions','prompt','skills','skillDelivery','requiredCapabilities','provenance'],['model','reasoning'])
    &&list(value.layers,100,item=>shape(item,['source','fields'])&&text(item.source,393216)&&profile(item.fields))
    &&(value.profile===null||text(value.profile,80))&&text(value.harness,393216)
    &&(value.model===undefined||text(value.model,393216))&&(value.reasoning===undefined||text(value.reasoning,393216))
    &&['read-only','workspace-write'].includes(String(value.permissions))&&text(value.prompt,393216,true)
    &&list(value.skills,100,item=>shape(item,['name','file','instructions','resources'])&&text(item.name,393216)&&text(item.file,393216)
      &&text(item.instructions,393216,true)&&list(item.resources,100,entry=>shape(entry,['file','content'])&&text(entry.file,393216)&&text(entry.content,393216,true)))
    &&['native','instructions'].includes(String(value.skillDelivery))&&list(value.requiredCapabilities,100,item=>text(item,393216))
    &&cleanupObject(value.provenance)&&Object.keys(value.provenance).every(key=>['harness','model','reasoning','permissions','prompt','skills','skillDelivery','requiredCapabilities'].includes(key))
    &&Object.values(value.provenance).every(item=>text(item,393216));
}
class Refusal extends Error {}
/** Internal closed learning interpreter. The caller supplies only the already bounded snapshot readers. */
export function analyzeLearningReferences(graph: LearningGraph): ReferenceAnalysis['reports'] {
  const recognizedAgents=new Set<string>();
  const reports: ReferenceAnalysis['reports'][number][]=[];
  const fail = (code: CleanupBlocker['code'],node: CleanupNode): never => { graph.block({code,node});throw new Refusal(); };
  function require(value: unknown,node: CleanupNode,code: CleanupBlocker['code']='opaque'): asserts value {
    if(!value)fail(code,node);
  }
  const read = (id: string,owner: string,attemptId: string|null,channel: CleanupCaptureHeader['channel'],limit: number|null,prefix?: readonly Chunk[]) => {
    const node=capture(owner,id),header=graph.owned(id,owner,attemptId,channel);if(!header)throw new Refusal();
    const result=graph.read(header,limit,prefix);if(!result)throw new Refusal();return {node,header,...result};
  };
  const parsed = (value: {text:string|null;node:CleanupNode}) => {require(value.text!==null,value.node,'malformed');
    try{const result=graph.parse(value.text);graph.retain(result);return result;}catch(error){if(error instanceof SyntaxError)fail('malformed',value.node);throw error;}};
  function ownedAttempt(id: string,owner: string,from: CleanupNode,kind: CleanupEdgeKind) {
    const value=graph.attempts.get(id);require(value,from,'missing');graph.edge(from,attempt(value),kind);
    require(value.invocationId===owner,attempt(value),'foreign');return value;
  }
  function event(owner: string,id: string,from: CleanupNode) {
    const node:CleanupNode={kind:'event',invocationId:owner,cursor:id};graph.edge(from,node,'source-event');
    const value=graph.event(owner,id);require(value.status==='known',node,value.status==='missing'||value.status==='foreign'?value.status:'opaque');
    for(const key of ['attemptId','captureId','inputsCaptureId'] as const){const ref=value.data[key];if(typeof ref!=='string')continue;
      if(key==='attemptId')ownedAttempt(ref,owner,node,'source-attempt');
      else {const header=graph.headers.get(ref);require(header,node,'missing');graph.edge(node,capture(header.invocationId,ref),'source-capture');
        require(header.invocationId===owner,node,'foreign');require(graph.read(header,null),node);}}
    return value;
  }
  function agent(value: CleanupAttemptFact,purpose: 'report'|'review',validator: string) {
    const node=attempt(value),meta=value.agent;require(value.kind==='agent'&&value.outcome==='succeeded'&&meta?.validator===validator,node,'ownership');
    require(meta.validatedResultCaptureId,node,'missing');
    require(new Set([meta.inputsCaptureId,meta.resultCaptureId,meta.validatedResultCaptureId]).size===3
      &&meta.outputCaptureId!==meta.inputsCaptureId&&meta.outputCaptureId!==meta.validatedResultCaptureId,node,'ownership');
    const input=read(meta.inputsCaptureId,value.invocationId,value.id,'context',393216),wrapper=parsed(input);
    require(shape(wrapper,['inputs','purpose','context','sourceCaptureId'])&&effective(wrapper.inputs)&&wrapper.purpose===purpose
      &&typeof wrapper.context==='string'&&cleanupId(wrapper.sourceCaptureId),node);
    const source=read(wrapper.sourceCaptureId,value.invocationId,null,'context',393216);graph.edge(node,source.node,'source-input');
    const original=parsed(source);require(shape(original,['step','inputs','purpose','context','validator'])&&original.step===value.operationKey
      &&original.validator===validator&&original.purpose===purpose&&equal(original.inputs,wrapper.inputs)&&original.context===wrapper.context,node,'ownership');
    read(meta.resultCaptureId,value.invocationId,value.id,'result',null);
    const output=graph.headers.get(meta.outputCaptureId);require(output,node,'missing');require(meta.outputCaptureId===meta.resultCaptureId?output.channel==='result':['stdout','stderr'].includes(output.channel),node,'ownership');
    read(meta.outputCaptureId,value.invocationId,value.id,output.channel,null);
    for(const header of graph.headers.values())if(header.attemptId===value.id)require(graph.read(header,null),node);
    const normalized=parsed(read(meta.validatedResultCaptureId,value.invocationId,value.id,'validated-result',131072));
    require(shape(normalized,['kind','payload'])&&normalized.kind==='result',node);
    let context:unknown;try{context=graph.parse(wrapper.context);graph.retain(context);}catch(error){if(error instanceof SyntaxError)fail('malformed',node);throw error;}
    recognizedAgents.add(value.id);return {context,payload:normalized.payload,inputs:wrapper.inputs};
  }
  function extractionReport(header: CleanupCaptureHeader) {
    const node=capture(header.invocationId,header.id),owner=graph.invocations.get(header.invocationId);
    require(owner?.stage==='finalized'&&owner.outcome==='succeeded'&&owner.workflow==='.factory/workflows/learn.ts'&&header.attemptId===null,node,'ownership');
    require([...graph.headers.values()].filter(item=>item.invocationId===owner.id&&item.channel==='report').length===1,node,'ownership');
    const raw=read(header.id,header.invocationId,null,'report',131072),report=parsed(raw);require(extraction(report),node);
    const inputHeader=owner.inputCaptureId;require(inputHeader,node,'missing');const root=parsed(read(inputHeader,owner.id,null,'context',393216));
    require(shape(root,['inputs','question','contexts'])&&shape(root.inputs,['version','sources'],['focus','agentProfile'])&&root.inputs.version===1
      &&equal(root.inputs.sources,report.suppliedSources)&&(root.inputs.focus===undefined||text(root.inputs.focus,4096))
      &&(root.inputs.agentProfile===undefined||text(root.inputs.agentProfile,80)),node);
    const resultHeader=graph.headers.get(report.proposalResultCaptureId);require(resultHeader?.attemptId,node,'missing');
    const producer=ownedAttempt(resultHeader.attemptId,owner.id,node,'extraction-result');
    require(producer.operationKey==='learn/extract'&&producer.agent?.resultCaptureId===report.proposalResultCaptureId
      &&producer.agent?.validatedResultCaptureId===report.proposalValidatedResultCaptureId,node,'ownership');
    const saved=agent(producer,'report','learning-extraction-v1');
    require(saved.inputs.permissions==='read-only'&&saved.inputs.profile===(root.inputs.agentProfile??null),node,'ownership');
    require(shape(saved.payload,['proposals'],['noProposalReason'])&&equal(saved.payload.proposals,report.proposals)
      &&saved.payload.noProposalReason===report.noProposalReason,node,'digest');
    const context=saved.context;require(shape(context,['version','focus','evidence','captureLimitations','instruction'])&&context.version===1
      &&context.focus===(root.inputs.focus??null)&&text(context.instruction,131072)&&list(context.evidence,6,()=>true,1)
      &&context.evidence.length===report.suppliedSources.length&&equal(context.captureLimitations,report.captureLimitations),node);
    const examined:Extraction['examinedSources']=[];
    for(let index=0;index<context.evidence.length;index++) {
      graph.tick();const entry=context.evidence[index],supplied=report.suppliedSources[index]!;
      require(shape(entry,['invocationId','outcome','attempts','events','captures'])&&entry.invocationId===supplied.invocationId
        &&list(entry.attempts,60,item=>shape(item,['id','operationKey','outcome'])&&cleanupId(item.id)&&cleanupId(item.operationKey)
          &&(item.outcome===null||text(item.outcome,256)))
        &&list(entry.events,12,item=>shape(item,['cursor','kind','data'])&&cursor(item.cursor)&&cleanupId(item.kind)&&cleanupObject(item.data))
        &&list(entry.captures,40,item=>shape(item,['id','channel','state','chunks'])&&cleanupId(item.id)&&text(item.channel,256)&&text(item.state,256)
          &&list(item.chunks,40,chunk=>shape(chunk,['sequence','text'])&&Number.isSafeInteger(chunk.sequence)&&Number(chunk.sequence)>0&&typeof chunk.text==='string')),node);
      const sourceOwner=graph.invocations.get(supplied.invocationId);graph.edge(node,invocation(supplied.invocationId),'source-invocation');
      require(sourceOwner?.stage==='finalized'&&sourceOwner.outcome===entry.outcome&&['succeeded','failed','interrupted','needs_input'].includes(String(entry.outcome)),node,'ownership');
      for(const id of supplied.attemptIds??[])ownedAttempt(id,supplied.invocationId,node,'source-attempt');
      for(const id of supplied.eventCursors??[])event(supplied.invocationId,id,node);
      for(const item of entry.attempts as {id:string;operationKey:string;outcome:string|null}[]){const actual=ownedAttempt(item.id,supplied.invocationId,node,'source-attempt');
        require(actual.operationKey===item.operationKey&&actual.outcome===item.outcome,attempt(actual),'digest');}
      for(const item of entry.events as {cursor:string;kind:string;data:unknown}[]){const actual=event(supplied.invocationId,item.cursor,node);require(actual.kind===item.kind&&equal(actual.data,item.data),node,'digest');}
      for(const item of entry.captures as {id:string;channel:CleanupCaptureHeader['channel'];state:string;chunks:Chunk[]}[]){
        const actual=graph.headers.get(item.id);require(actual,node,'missing');graph.edge(node,capture(actual.invocationId,item.id),'source-capture');
        require(actual.invocationId===supplied.invocationId&&actual.channel===item.channel,node,'ownership');
        require(actual.state===item.state&&item.state==='complete',node,'partial');
        require(graph.read(actual,null,item.chunks),node,'digest');
      }
      const attempts=entry.attempts as {id:string}[],events=entry.events as {cursor:string}[],captures=entry.captures as {id:string;chunks:Chunk[]}[];
      const observed={invocationId:supplied.invocationId,outcome:String(entry.outcome),attemptIds:attempts.map(item=>item.id),eventCursors:events.map(item=>item.cursor),captureIds:captures.filter(item=>item.chunks.length).map(item=>item.id)};
      require(ids(observed.attemptIds,60)&&cursors(observed.eventCursors,12)&&ids(captures.map(item=>item.id),40),node);
      require((!supplied.attemptIds||equal(supplied.attemptIds,observed.attemptIds))&&(!supplied.eventCursors||equal(supplied.eventCursors,observed.eventCursors)),node,'digest');examined.push(observed);
    }
    require(equal(examined,report.examinedSources),node,'digest');
    for(const item of report.captureLimitations){const source=report.suppliedSources.find(source=>source.invocationId===item.invocationId);require(source,node,'foreign');
      const noRef=['attempt_pages_unexamined','capture_pages_unexamined','captures_unexamined'].includes(item.kind);
      require(noRef?item.reference===undefined:cleanupId(item.reference),node);
      if(item.reference){if(item.kind==='selected_attempt_unexamined')ownedAttempt(item.reference,item.invocationId,node,'source-attempt');
        else if(item.kind==='event_ownership_unexamined')event(item.invocationId,item.reference,node);
        else {const known=graph.headers.get(item.reference);require(known,node,'missing');graph.edge(node,capture(known.invocationId,known.id),'source-capture');require(known.invocationId===item.invocationId,node,'foreign');}}
      graph.block({code:'partial',node});
    }
    const reference = (ref: Evidence) => {const source=examined.find(item=>item.invocationId===ref.invocationId);require(source,node,'foreign');
      if(ref.attemptId){require(source.attemptIds.includes(ref.attemptId),node,'ownership');ownedAttempt(ref.attemptId,ref.invocationId,node,'source-attempt');}
      else if(ref.eventCursor){require(source.eventCursors.includes(ref.eventCursor),node,'ownership');event(ref.invocationId,ref.eventCursor,node);}
      else {require(ref.captureId&&source.captureIds.includes(ref.captureId),node,'ownership');const actual=graph.headers.get(ref.captureId);require(actual,node,'missing');
        graph.edge(node,capture(actual.invocationId,actual.id),'source-capture');require(graph.read(actual,null),node);}};
    for(const proposal of report.proposals){for(const ref of [...proposal.supportingEvidence,...proposal.contraryEvidence])reference(ref);
      if(proposal.candidateCapture){reference(proposal.candidateCapture);graph.edge(node,capture(proposal.candidateCapture.invocationId,proposal.candidateCapture.captureId),'candidate');}}
    return {report,raw,producer};
  }
  function evaluationReport(header: CleanupCaptureHeader) {
    const node=capture(header.invocationId,header.id),owner=graph.invocations.get(header.invocationId);
    require(owner?.stage==='finalized'&&owner.outcome==='succeeded'&&owner.workflow==='.factory/workflows/evaluate.ts'&&header.attemptId===null,node,'ownership');
    const raw=read(header.id,owner.id,null,'report',131072),report=parsed(raw);require(evaluation(report),node);
    const refs=report.suppliedReferences;
    // Record every supplied dependency before a missing one can stop validation.
    graph.edge(node,invocation(refs.extraction.invocationId),'source-invocation');
    for(const [kind,ref] of [['baseline',refs.baseline],['candidate',refs.candidate]] as const){
      const known=graph.headers.get(ref.captureId);graph.edge(node,capture(known?.invocationId??ref.invocationId,ref.captureId),kind);
      graph.edge(node,invocation(ref.invocationId),'source-invocation');
    }
    const extractionHeaders=[...graph.headers.values()].filter(item=>item.invocationId===refs.extraction.invocationId&&item.channel==='report');
    for(const item of extractionHeaders)graph.edge(node,capture(item.invocationId,item.id),'extraction-report');
    require(extractionHeaders.length===1,node,extractionHeaders.length?'ownership':'missing');
    const extracted=extractionReport(extractionHeaders[0]!);
    const proposals=extracted.report.proposals.filter(item=>item.key===refs.extraction.proposalKey);require(proposals.length===1,node,'ownership');
    const selected=proposals[0]!;
    require(report.extractionReport?.captureId===extractionHeaders[0]!.id&&report.extractionReport.sha256===extracted.raw.sha256,node,'digest');
    require(equal(report.extractionResult,{attemptId:extracted.producer.id,rawCaptureId:extracted.report.proposalResultCaptureId,
      validatedCaptureId:extracted.report.proposalValidatedResultCaptureId}),node,'ownership');
    graph.edge(node,attempt(extracted.producer),'extraction-result');
    const variants:{baseline:string;candidate:string}={baseline:'',candidate:''};
    for(const variant of ['baseline','candidate'] as const){const ref=refs[variant],source=graph.invocations.get(ref.invocationId);
      require(source?.stage==='finalized',node,'ownership');const known=graph.headers.get(ref.captureId);require(known,node,'missing');
      require(known.invocationId===ref.invocationId,node,'foreign');const value=read(ref.captureId,ref.invocationId,known.attemptId,known.channel,131072);
      require(value.sha256===ref.sha256,node,'digest');require(value.text!==null,node);variants[variant]=value.text;
    }
    require(owner.inputCaptureId,node,'missing');const root=parsed(read(owner.inputCaptureId,owner.id,null,'context',393216));
    require(shape(root,['inputs','question','contexts'])&&shape(root.inputs,['version','extraction','baseline','candidate','cases'],['reviewProfile'])&&root.inputs.version===1
      &&equal(root.inputs.extraction,refs.extraction)&&equal(root.inputs.baseline,refs.baseline)&&equal(root.inputs.candidate,refs.candidate)
      &&equal(root.inputs.cases,report.settings.cases)&&(root.inputs.reviewProfile===undefined||text(root.inputs.reviewProfile,80))
      &&report.settings.review.profile===(root.inputs.reviewProfile??null),node,'ownership');
    require(equal(report.target,selected.target)&&equal(report.proposalSuggestedCases,selected.suggestedCases),node,'digest');
    const covered=new Set(report.settings.cases.map(item=>item.sourceSuggestion).filter(item=>item!==undefined));
    require([...covered].every(item=>selected.suggestedCases.includes(item)),node,'ownership');
    const expected:EvaluationLimitation[]=[];
    if(selected.target.scope!=='repository')expected.push({kind:'unsupported_target_scope',reference:selected.target.scope});
    else if(!selected.candidateCapture)expected.push({kind:'diff_only_candidate_requires_exact_materialization',reference:refs.extraction.proposalKey});
    else require(selected.candidateCapture.invocationId===refs.candidate.invocationId&&selected.candidateCapture.captureId===refs.candidate.captureId,node,'ownership');
    if(refs.baseline.sha256===refs.candidate.sha256)expected.push({kind:'identical_variants'});
    if(!report.cases.length){
      // Target applicability is not reference completeness. Exact early outcomes
      // can be complete without executing a diff, Git or a proposed target action.
      require(expected.length>0&&equal(report.limitations,expected)&&report.contraryCases.length===0,node,'ownership');
      return {raw,report};
    }
    require(!expected.length&&equal(report.resolved,{baselineSha256:cleanupHash(variants.baseline),candidateSha256:cleanupHash(variants.candidate)}),node,'digest');
    require(report.cases.length===report.settings.cases.length,node,'ownership');
    for(const suggestion of selected.suggestedCases)if(!covered.has(suggestion))expected.push({kind:'suggested_case_unexamined',reference:suggestion});
    const usedAttempts=new Set<string>();
    for(let index=0;index<report.cases.length;index++) {
      graph.tick();const item=report.cases[index]!,input=report.settings.cases[index]!;
      require(item.key===input.key&&item.criteria===input.criteria&&item.sourceSuggestion===input.sourceSuggestion
        &&equal(item.settings.argv,input.argv)&&item.settings.timeoutMs===input.timeoutMs,node,'digest');
      for(const variant of ['baseline','candidate'] as const) {
        const side=item[variant];
        for(let repetition=0;repetition<side.objective.length;repetition++) {
          const evidence=side.objective[repetition]!,actual=ownedAttempt(evidence.attemptId,owner.id,node,'objective');
          require(!usedAttempts.has(actual.id),attempt(actual),'ownership');usedAttempts.add(actual.id);
          require(actual.kind==='command'&&actual.operationKey===`evaluate/${item.key}/${variant}/objective/${repetition+1}`
            &&evidence.exitCode!==null&&actual.outcome===(evidence.exitCode===0?'succeeded':'failed')&&actual.quiescent
            &&!actual.occupied&&actual.launch==='started'&&evidence.cleanup==='complete',attempt(actual),'ownership');
          const inputs=[...graph.headers.values()].filter(header=>header.attemptId===actual.id&&header.channel==='context');require(inputs.length===1,attempt(actual),'ownership');
          const settings=parsed(read(inputs[0]!.id,owner.id,actual.id,'context',393216));
          require(shape(settings,['argv','cwd','env','shell','required','timeoutMs','childScope','limitation'])&&equal(settings.argv,item.settings.argv)
            &&settings.cwd===item.settings.cwd&&settings.timeoutMs===item.settings.timeoutMs&&settings.required===false&&settings.shell===false,attempt(actual),'digest');
          for(const header of graph.headers.values())if(header.attemptId===actual.id)require(graph.read(header,null),attempt(actual));
        }
        const review=side.review,actual=ownedAttempt(review.attemptId,owner.id,node,'review');
        require(!usedAttempts.has(actual.id),attempt(actual),'ownership');usedAttempts.add(actual.id);
        require(actual.operationKey===`evaluate/${item.key}/${variant}/review`&&actual.agent?.resultCaptureId===review.resultCaptureId
          &&actual.agent?.inputsCaptureId===review.inputsCaptureId,attempt(actual),'ownership');
        const saved=agent(actual,'review','learning-evaluation-review-v1');
        require(shape(saved.payload,['judgment','reason'])&&saved.payload.judgment===review.judgment&&saved.payload.reason===review.reason,attempt(actual),'digest');
        require(saved.inputs.permissions===review.effectivePermissions&&saved.inputs.profile===review.effectiveProfile
          &&saved.inputs.profile===report.settings.review.profile,attempt(actual),'ownership');
        const context=saved.context;require(shape(context,['version','variant','caseKey','criteria','target','text','objective'])&&context.version===1
          &&context.variant===variant&&context.caseKey===item.key&&context.criteria===item.criteria&&equal(context.target,selected.target)
          &&typeof context.text==='string'&&cleanupHash(context.text)===refs[variant].sha256&&context.text===variants[variant]
          &&equal(context.objective,side.objective),attempt(actual),'digest');
        if(review.effectivePermissions!=='read-only')expected.push({kind:'review_not_read_only',reference:actual.id});
      }
    }
    const contrary=report.cases.filter(item=>item.baseline.objective.every(item=>item.exitCode===0)&&item.candidate.objective.every(item=>item.exitCode!==0)).map(item=>item.key);
    for(const item of report.cases){
      if(new Set(item.baseline.objective.map(item=>item.exitCode)).size>1||new Set(item.candidate.objective.map(item=>item.exitCode)).size>1)
        expected.push({kind:'nondeterministic_objective',reference:item.key});
      if(item.baseline.review.judgment==='uncertain'||item.candidate.review.judgment==='uncertain')expected.push({kind:'uncertain_review',reference:item.key});
      const success=(side:CaseResult['baseline'])=>side.objective.every(item=>item.exitCode===0);
      if((item.baseline.review.judgment==='pass')!==success(item.baseline)||(item.candidate.review.judgment==='pass')!==success(item.candidate))
        expected.push({kind:'review_objective_disagreement',reference:item.key});
    }
    let assessment:Evaluation['assessment']=expected.length?'inconclusive':report.cases.some(item=>item.candidate.objective.some(item=>item.exitCode!==0))?'unsupported':'supported';
    if(!expected.length&&assessment==='supported'&&report.cases.every(item=>item.baseline.objective.every(item=>item.exitCode===0))) {
      expected.push({kind:'no_observed_improvement'});assessment='inconclusive';
    }
    require(equal(report.limitations,expected)&&equal(report.contraryCases,contrary)&&report.assessment===assessment,node,'digest');
    return {raw,report};
  }
  const actionReport=actionReferenceInterpreter(graph,evaluationReport);
  for(const header of [...graph.headers.values()].filter(header=>header.channel==='report').sort((a,b)=>a.invocationId<b.invocationId?-1:a.invocationId>b.invocationId?1:a.id<b.id?-1:1)) {
    graph.tick();const node=capture(header.invocationId,header.id);
    try { const owner=graph.invocations.get(header.invocationId);
      const action=actionReport(header);
      if(action.handled) {if(action.fact){graph.retain(action.fact);reports.push(action.fact);graph.report(action.fact);}}
      else if(owner?.workflow==='.factory/workflows/learn.ts') {const result=extractionReport(header);const fact={key:{invocationId:header.invocationId,captureId:header.id},format:'extraction-v1' as const,sha256:result.raw.sha256};graph.retain(fact);reports.push(fact);graph.report(fact);}
      else if(owner?.workflow==='.factory/workflows/evaluate.ts') {const result=evaluationReport(header);const fact={key:{invocationId:header.invocationId,captureId:header.id},format:'evaluation-v1' as const,sha256:result.raw.sha256};graph.retain(fact);reports.push(fact);graph.report(fact);}
      else graph.block({code:'opaque',node});
    } catch(error) {if(!(error instanceof Refusal))throw error;}
  }
  for(const owner of graph.invocations.values())if(isLearningWorkflow(owner.workflow)&&!reports.some(item=>item.key.invocationId===owner.id))graph.block({code:'opaque',node:invocation(owner.id)});
  for(const value of graph.attempts.values())if(value.kind==='agent'&&isLearningWorkflow(graph.invocations.get(value.invocationId)?.workflow??null)&&!recognizedAgents.has(value.id))graph.block({code:'opaque',node:attempt(value)});
  return reports;
}

export function isLearningWorkflow(workflow: string|null) { return workflow==='.factory/workflows/learn.ts'||workflow==='.factory/workflows/evaluate.ts'; }
