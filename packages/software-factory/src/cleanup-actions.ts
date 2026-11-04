import { isAbsolute } from 'node:path';
import { isDeepStrictEqual as equal } from 'node:util';
import { cleanupId, cleanupObject, type CleanupCaptureHeader } from './cleanup-read.js';
import type { CleanupBlocker, CleanupEdgeKind, CleanupNode, ReferenceAnalysis } from './cleanup-references.js';
import type { LearningGraph } from './cleanup-learning.js';
import type { AdoptionApproval, AdoptionPreparation, AdoptionOutcome, RevertPreparation, RevertOutcome, LearningReference, TargetObservation } from './learning.js';

type ObjectValue = Record<string, unknown>;
type Applied = Extract<AdoptionOutcome, { status: 'applied' }>;
type ActionReport = AdoptionPreparation|AdoptionOutcome|RevertPreparation|RevertOutcome;
type EvaluationFacts = { raw: { sha256: string }; report: {
  assessment: string; limitations: readonly unknown[]; target: { scope: string; path: string }|null;
  suppliedReferences: { extraction: { invocationId: string; proposalKey: string }; baseline: LearningReference; candidate: LearningReference };
  extractionReport: AdoptionPreparation['evidence']['extractionReport']|null;
  extractionResult: AdoptionPreparation['evidence']['extractionResult']|null;
  resolved?: { baselineSha256: string; candidateSha256: string };
} };
const capture = (invocationId: string,captureId: string): CleanupNode => ({ kind:'capture',invocationId,captureId });
const shape = (value: unknown,required: readonly string[]): value is ObjectValue => cleanupObject(value)
  &&required.every(key=>Object.hasOwn(value,key))&&Object.keys(value).every(key=>required.includes(key));
const text = (value: unknown,max: number): value is string => typeof value==='string'&&!!value.trim()&&!value.includes('\0')
  &&Buffer.byteLength(value)<=max&&Buffer.from(value).toString('utf8')===value;
const sha = (value: unknown): value is string => typeof value==='string'&&/^[0-9a-f]{64}$/.test(value);
const revision = (value: unknown): value is string => typeof value==='string'&&/^[0-9a-f]{40}(?:[0-9a-f]{24})?$/.test(value);
const reference = (value: unknown): value is LearningReference => shape(value,['invocationId','captureId','sha256'])
  &&cleanupId(value.invocationId)&&cleanupId(value.captureId)&&sha(value.sha256);
const observation = (value: unknown): value is TargetObservation => shape(value,['revision','sha256'])&&revision(value.revision)&&sha(value.sha256);
const approval = (value: unknown): value is AdoptionApproval => shape(value,['reference','extraction','evaluation','candidate','target'])
  &&text(value.reference,256)&&shape(value.extraction,['invocationId','proposalKey'])&&cleanupId(value.extraction.invocationId)&&text(value.extraction.proposalKey,80)
  &&shape(value.evaluation,['invocationId','reportCaptureId','sha256'])&&cleanupId(value.evaluation.invocationId)&&cleanupId(value.evaluation.reportCaptureId)&&sha(value.evaluation.sha256)
  &&reference(value.candidate)&&shape(value.target,['repository','scope','path','expectedRevision','expectedSha256'])
  &&text(value.target.repository,131072)&&isAbsolute(value.target.repository)&&value.target.scope==='repository'&&text(value.target.path,512)
  &&value.target.path.split('/').every(part=>/^[A-Za-z0-9._-]+$/.test(part)&&part!=='.'&&part!=='..')
  &&revision(value.target.expectedRevision)&&sha(value.target.expectedSha256);
const evidence = (value: unknown): value is AdoptionPreparation['evidence'] => shape(value,['extractionReport','extractionResult'])
  &&shape(value.extractionReport,['captureId','sha256'])&&cleanupId(value.extractionReport.captureId)&&sha(value.extractionReport.sha256)
  &&shape(value.extractionResult,['attemptId','rawCaptureId','validatedCaptureId'])&&Object.values(value.extractionResult).every(cleanupId);
const action = (value: unknown) => shape(value,['reference','status'])&&text(value.reference,256)&&typeof value.status==='string'&&['succeeded','failed','uncertain'].includes(value.status);
function applied(value: unknown): value is Applied {
  return shape(value,['kind','status','approval','evidence','preparationReference','action','applied'])&&value.kind==='adoption'&&value.status==='applied'
    &&approval(value.approval)&&evidence(value.evidence)&&reference(value.preparationReference)&&action(value.action)&&observation(value.applied);
}
function adoptionPreparation(value: unknown): value is AdoptionPreparation {
  return shape(value,['kind','approval','evidence','expected'])&&value.kind==='adoption-preparation'&&approval(value.approval)&&evidence(value.evidence)&&observation(value.expected);
}
function adoption(value: unknown): value is AdoptionOutcome {
  return applied(value)||shape(value,['kind','status','approval','evidence','preparationReference','action','observed','reason'])&&value.kind==='adoption'
    &&typeof value.status==='string'&&['not_applied','uncertain'].includes(value.status)&&approval(value.approval)&&evidence(value.evidence)&&reference(value.preparationReference)
    &&action(value.action)&&(value.observed===null||observation(value.observed))&&text(value.reason,2048);
}
function revertPreparation(value: unknown): value is RevertPreparation {
  return shape(value,['kind','originalAdoption','originalAdoptionReference','approvalReference','expected'])&&value.kind==='revert-preparation'
    &&applied(value.originalAdoption)&&reference(value.originalAdoptionReference)&&text(value.approvalReference,256)&&observation(value.expected);
}
function revert(value: unknown): value is RevertOutcome {
  if(!cleanupObject(value))return false;
  const positive=value.status==='reverted';
  return shape(value,['kind','status','originalAdoption','preparationReference','approvalReference','action',...(positive?['reverted']:['observed','reason'])])
    &&value.kind==='revert'&&typeof value.status==='string'&&['reverted','not_reverted','uncertain'].includes(value.status)&&applied(value.originalAdoption)
    &&reference(value.preparationReference)&&text(value.approvalReference,256)&&action(value.action)
    &&(positive?observation(value.reverted):(value.observed===null||observation(value.observed))&&text(value.reason,2048));
}
class Refusal extends Error {}
/** Closed historical compatibility only. Paths, revisions and human labels never trigger I/O or become locators. */
export function actionReferenceInterpreter(graph: LearningGraph,evaluationReport: (header: CleanupCaptureHeader)=>EvaluationFacts) {
  const cache=new Map<string,{value:ActionReport;sha256:string}>(),active=new Set<string>();
  const fail = (code: CleanupBlocker['code'],node: CleanupNode,limit?: string): never => {graph.block({code,node,...(limit?{limit}:{})});throw new Refusal();};
  function require(value: unknown,node: CleanupNode,code: CleanupBlocker['code']='opaque'): asserts value {if(!value)fail(code,node);}
  const decoded = (header: CleanupCaptureHeader) => {
    const node=capture(header.invocationId,header.id),owner=graph.invocations.get(header.invocationId);
    require(owner?.stage==='finalized'&&owner.outcome==='succeeded'&&header.attemptId===null,node,'ownership');
    const owned=graph.owned(header.id,header.invocationId,null,'report');require(owned,node,'ownership');
    const raw=graph.read(owned,131072);require(raw?.text!==null&&raw?.text!==undefined,node,'partial');
    let value:unknown;try{value=graph.parse(raw.text);}catch(error){if(error instanceof SyntaxError)fail('malformed',node);throw error;}
    graph.retain(value);return {value,sha256:raw.sha256};
  };
  const linked = (ref: LearningReference,from: CleanupNode,kind: CleanupEdgeKind,expected: ActionReport['kind'],appliedOnly = false) => {
    const node=capture(ref.invocationId,ref.captureId);graph.edge(from,node,kind);
    const header=graph.headers.get(ref.captureId);require(header,node,'missing');require(header.invocationId===ref.invocationId,node,'foreign');
    const raw=decoded(header);require(cleanupObject(raw.value)&&raw.value.kind===expected&&(!appliedOnly||raw.value.status==='applied'),node,'ownership');
    require(raw.sha256===ref.sha256,node,'digest');const result=resolve(header,raw);return result.value;
  };
  function approved(value: AdoptionPreparation|AdoptionOutcome,node: CleanupNode) {
    const {approval:approved,evidence:saved}=value,ref=approved.evaluation;
    const evaluationNode=capture(ref.invocationId,ref.reportCaptureId);graph.edge(node,evaluationNode,'review');
    graph.edge(node,{kind:'invocation',invocationId:approved.extraction.invocationId},'source-invocation');
    graph.edge(node,capture(approved.extraction.invocationId,saved.extractionReport.captureId),'extraction-report');
    graph.edge(node,{kind:'attempt',invocationId:approved.extraction.invocationId,attemptId:saved.extractionResult.attemptId},'extraction-result');
    const candidateNode=capture(approved.candidate.invocationId,approved.candidate.captureId);graph.edge(node,candidateNode,'candidate');
    const header=graph.headers.get(ref.reportCaptureId);require(header,evaluationNode,'missing');require(header.invocationId===ref.invocationId,evaluationNode,'foreign');
    const result=evaluationReport(header),report=result.report;require(result.raw.sha256===ref.sha256,evaluationNode,'digest');
    require(report.assessment==='supported'&&!report.limitations.length&&equal(report.suppliedReferences.extraction,approved.extraction)
      &&equal(report.suppliedReferences.candidate,approved.candidate)&&report.suppliedReferences.baseline.sha256===approved.target.expectedSha256
      &&equal(report.target,{scope:approved.target.scope,path:approved.target.path})
      &&equal(report.resolved,{baselineSha256:approved.target.expectedSha256,candidateSha256:approved.candidate.sha256})
      &&equal(saved,{extractionReport:report.extractionReport,extractionResult:report.extractionResult}),node,'digest');
    for(const reference of [report.suppliedReferences.baseline,approved.candidate]) {
      const header=graph.headers.get(reference.captureId),refNode=capture(reference.invocationId,reference.captureId);
      require(header,refNode,'missing');require(header.invocationId===reference.invocationId,refNode,'foreign');require(header.channel==='event',refNode,'ownership');
      const raw=graph.read(header,null);require(raw,refNode,'partial');require(raw.sha256===reference.sha256,refNode,'digest');
    }
  }
  function outcome(value: AdoptionOutcome|RevertOutcome,expected: TargetObservation,node: CleanupNode) {
    const reverting=value.kind==='revert',positive=value.status==='applied'||value.status==='reverted';
    const target=reverting?value.originalAdoption.approval.target:value.approval.target;
    const expectedHash=reverting?target.expectedSha256:value.approval.candidate.sha256;
    if(positive) {
      const observed=value.status==='applied'?value.applied:value.reverted;
      require(value.action.status==='succeeded'&&observed.sha256===expectedHash&&observed.revision!==expected.revision,node,'digest');return;
    }
    if(value.observed===null) {require(value.status==='uncertain'&&value.reason==='target observation unavailable',node,'digest');return;}
    const unchanged=equal(value.observed,expected),negative=reverting?'not_reverted':'not_applied';
    if(value.action.status!=='succeeded')require(value.status===(unchanged?negative:'uncertain')&&value.reason===`action ${value.action.status}`,node,'digest');
    else if(unchanged)require(value.status===negative&&value.reason==='target revision and content unchanged',node,'digest');
    else require(value.status==='uncertain'&&value.reason===(reverting?'actual revert commit does not restore only the original target':'actual commit does not contain only the approved candidate target'),node,'digest');
  }
  function resolve(header: CleanupCaptureHeader,initial?: ReturnType<typeof decoded>): {value:ActionReport;sha256:string} {
    graph.tick();const node=capture(header.invocationId,header.id),existing=cache.get(header.id);if(existing)return existing;
    require(!active.has(header.id),node,'cycle');active.add(header.id);
    try {
      const raw=initial??decoded(header),value=raw.value;
      let objects=0;const pending=[value];
      while(pending.length) {graph.tick();const item=pending.pop();if(item&&typeof item==='object') {
        if(++objects>64)fail('limit',node,'actionObjects');pending.push(...Object.values(item));
      }}
      require(adoptionPreparation(value)||adoption(value)||revertPreparation(value)||revert(value),node);
      if(value.kind==='adoption-preparation') {
        approved(value,node);require(equal(value.expected,{revision:value.approval.target.expectedRevision,sha256:value.approval.target.expectedSha256}),node,'digest');
      } else if(value.kind==='adoption') {
        const prepared=linked(value.preparationReference,node,'preparation','adoption-preparation');require(prepared.kind==='adoption-preparation',node,'ownership');
        require(equal(value.approval,prepared.approval)&&equal(value.evidence,prepared.evidence),node,'digest');approved(value,node);outcome(value,prepared.expected,node);
      } else if(value.kind==='revert-preparation') {
        const original=linked(value.originalAdoptionReference,node,'original-adoption','adoption',true);require(original.kind==='adoption'&&original.status==='applied',node,'ownership');
        require(equal(value.originalAdoption,original)&&equal(value.expected,original.applied),node,'digest');
      } else {
        const prepared=linked(value.preparationReference,node,'preparation','revert-preparation');require(prepared.kind==='revert-preparation',node,'ownership');
        require(equal(value.originalAdoption,prepared.originalAdoption)&&value.approvalReference===prepared.approvalReference,node,'digest');outcome(value,prepared.expected,node);
      }
      const result={value,sha256:raw.sha256};graph.retain(header.id);cache.set(header.id,result);return result;
    } finally {active.delete(header.id);}
  }
  return (header: CleanupCaptureHeader): {handled:boolean;fact:ReferenceAnalysis['reports'][number]|null} => {
    try {
      // Decode before filename dispatch: compatibility is independent of the workflow which retained the value.
      const raw=decoded(header);if(!cleanupObject(raw.value)||typeof raw.value.kind!=='string'||!['adoption-preparation','adoption','revert-preparation','revert'].includes(raw.value.kind))return {handled:false,fact:null};
      const result=resolve(header,raw),kind=result.value.kind;
      return {handled:true,fact:{key:{invocationId:header.invocationId,captureId:header.id},
        format:kind==='adoption-preparation'?'adoption-preparation-compat1':kind==='adoption'?'adoption-compat1':kind==='revert-preparation'?'revert-preparation-compat1':'revert-compat1',sha256:result.sha256}};
    } catch(error) {if(!(error instanceof Refusal))throw error;return {handled:true,fact:null};}
  };
}
