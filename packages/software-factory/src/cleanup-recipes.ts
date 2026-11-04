import { isDeepStrictEqual as equal } from 'node:util';
import { cleanupCursor, cleanupId, cleanupObject, type CleanupAttemptFact, type CleanupCaptureHeader } from './cleanup-read.js';
import { cleanupEffective, cleanupProfile, type LearningGraph } from './cleanup-learning.js';
import type { CleanupBlocker, CleanupNode } from './cleanup-references.js';

type Obj = Record<string, unknown>;
const shape = (value: unknown, required: string[], optional: string[] = []): value is Obj => cleanupObject(value)
  && required.every(key => Object.hasOwn(value, key)) && Object.keys(value).every(key => required.includes(key) || optional.includes(key));
const text = (value: unknown, empty = false): value is string => typeof value === 'string' && (empty || !!value.trim())
  && !value.includes('\0') && Buffer.byteLength(value) <= 393216 && Buffer.from(value).toString('utf8') === value;
const list = (value: unknown, check: (item: unknown) => boolean): value is unknown[] => Array.isArray(value) && value.length <= 100 && value.every(check);
const strictProfile = (value: unknown): boolean => cleanupObject(value)
  && (value.permissions===undefined || typeof value.permissions==='string') && (value.skillDelivery===undefined || typeof value.skillDelivery==='string')
  && cleanupProfile(value);
function strictEffective(value: unknown): value is Obj {
  if(!cleanupObject(value) || typeof value.permissions!=='string' || typeof value.skillDelivery!=='string'
    || !Array.isArray(value.layers) || value.layers.length>100 || !value.layers.every(layer=>cleanupObject(layer)&&strictProfile(layer.fields))
    || !cleanupEffective(value)) return false;
  const layers=value.layers as Obj[];let index=0;
  if(layers[index]?.source==='repository defaults') index++;
  if(value.profile!==null) {if(layers[index]?.source!==`profile:${value.profile}`)return false;index++;}
  if(layers[index]?.source!=='step')return false;index++;
  if(layers[index]?.source==='invocation override')index++;
  if(index!==layers.length)return false;
  const merged:Obj={},provenance:Obj={};
  for(const layer of layers) for(const [key,field] of Object.entries(layer.fields as Obj)) {merged[key]=field;provenance[key]=layer.source;}
  if(!equal(value.provenance,provenance))return false;
  for(const key of ['harness','model','reasoning','permissions','skillDelivery'])
    if(Object.hasOwn(merged,key)!==Object.hasOwn(value,key) || merged[key]!==value[key])return false;
  if(!equal(value.requiredCapabilities,merged.requiredCapabilities??[]))return false;
  if(!Object.hasOwn(merged,'prompt'))return false;
  if(typeof merged.prompt==='string' && value.prompt!==merged.prompt)return false;
  const declared=merged.skills??[];if(!Array.isArray(declared)||!Array.isArray(value.skills)||declared.length!==value.skills.length)return false;
  for(let i=0;i<declared.length;i++) {
    const spec=declared[i] as Obj,actual=value.skills[i] as Obj;
    if(spec.name!==actual.name || spec.file!==actual.file || !equal(spec.resources??[],(actual.resources as Obj[]).map(item=>item.file)))return false;
  }
  return true;
}
const phase = (value: unknown): boolean => shape(value, [], ['profile','timeoutMs','harness','model','reasoning','permissions','prompt','skills','skillDelivery','requiredCapabilities'])
  && (value.profile === undefined || text(value.profile)) && (value.timeoutMs === undefined || typeof value.timeoutMs === 'number' && Number.isFinite(value.timeoutMs) && value.timeoutMs > 0)
  && strictProfile(Object.fromEntries(Object.entries(value).filter(([key]) => key !== 'profile' && key !== 'timeoutMs')));
const summary = (value: unknown): value is {summary:string} => shape(value, ['summary']) && text(value.summary);
const capture = (invocationId:string,captureId:string):CleanupNode => ({kind:'capture',invocationId,captureId});
const attempt = (value:CleanupAttemptFact):CleanupNode => ({kind:'attempt',invocationId:value.invocationId,attemptId:value.id});
class Refusal extends Error {}

/** Only declared ordinary formats are candidates. The declaration is a format claim, not producer authentication. */
export function ordinaryDeclaration(value: unknown): boolean {
  return cleanupObject(value) && value.version === 1 && (value.kind === 'change-report' || value.kind === 'audit-report');
}

function input(value:unknown,audit:boolean): value is Obj {
  if (!shape(value, [], ['snapshot','prompt','plan','planning','implement','review','checks','browserVerification','agents','priorAttempts', ...(audit?['scopes','synthesis']:[])])) return false;
  if (audit && value.implement !== undefined) return false;
  if (value.snapshot !== undefined && (!shape(value.snapshot, [], ['maxEntries','maxBytes','timeoutMs']) || Object.values(value.snapshot).some(v => typeof v !== 'number' || !Number.isFinite(v) || v <= 0)
    || ['maxEntries','maxBytes'].some(k => value.snapshot && cleanupObject(value.snapshot) && value.snapshot[k] !== undefined && !Number.isSafeInteger(value.snapshot[k])))) return false;
  if (value.prompt !== undefined && !text(value.prompt)) return false;
  if (value.plan !== undefined && !(text(value.plan) || shape(value.plan,['steps']) && list(value.plan.steps, item => shape(item,['title','prompt'],['skip']) && text(item.title) && text(item.prompt) && (item.skip === undefined || typeof item.skip === 'boolean')))) return false;
  if (value.prompt === undefined && value.plan === undefined) return false;
  if (['planning','implement','review','synthesis'].some(k => value[k] !== undefined && typeof value[k] !== 'boolean')) return false;
  if (value.checks !== undefined && (!list(value.checks, item => shape(item,['name','argv'],['cwd','env','timeoutMs']) && text(item.name)
    && Array.isArray(item.argv) && item.argv.length > 0 && item.argv.length <= 100 && item.argv.every(v => text(v,true))
    && (item.cwd === undefined || text(item.cwd,true)) && (item.env === undefined || cleanupObject(item.env) && Object.keys(item.env).length <= 100 && Object.values(item.env).every(v => text(v,true)))
    && (item.timeoutMs === undefined || typeof item.timeoutMs === 'number' && Number.isFinite(item.timeoutMs) && item.timeoutMs > 0))
    || new Set(value.checks.map(item => (item as Obj).name)).size !== value.checks.length)) return false;
  if (value.browserVerification !== undefined && !(shape(value.browserVerification,['enabled'],['agent']) && typeof value.browserVerification.enabled === 'boolean'
    && (value.browserVerification.agent === undefined || phase(value.browserVerification.agent)))) return false;
  const phases = audit ? ['planning','investigation','synthesis','review','repair'] : ['planning','implementation','review','repair'];
  if (value.agents !== undefined && (!shape(value.agents,[],phases) || !Object.values(value.agents).every(phase))) return false;
  if (value.priorAttempts !== undefined && (!cleanupObject(value.priorAttempts) || Object.keys(value.priorAttempts).length > 100
    || !Object.entries(value.priorAttempts).every(([key,id]) => cleanupId(key) && cleanupId(id)))) return false;
  if (audit && (!list(value.scopes, item => shape(item,['name','target'],['questions','skip','agent']) && text(item.name) && text(item.target)
    && (item.questions === undefined || text(item.questions)) && (item.skip === undefined || typeof item.skip === 'boolean') && (item.agent === undefined || phase(item.agent)))
    || !value.scopes.length || new Set(value.scopes.map(item => (item as Obj).name)).size !== value.scopes.length)) return false;
  return true;
}

export function ordinaryReferenceInterpreter(graph: LearningGraph) {
  const fail = (code:CleanupBlocker['code'],node:CleanupNode):never => { graph.block({code,node}); throw new Refusal(); };
  function require(value:unknown,node:CleanupNode,code:CleanupBlocker['code']='opaque'):asserts value { if (!value) fail(code,node); }
  function read(id:string,owner:string,attemptId:string|null,channel:CleanupCaptureHeader['channel'],limit:number|null) {
    const node=capture(owner,id), header=graph.owned(id,owner,attemptId,channel); if (!header) throw new Refusal();
    const result=graph.read(header,limit); if (!result) throw new Refusal(); return {node,...result};
  }
  function parsed(value:{node:CleanupNode;text:string|null}):unknown {
    require(value.text!==null,value.node,'malformed');
    try { const data=graph.parse(value.text); graph.retain(data); return data; }
    catch(error) { if(error instanceof SyntaxError) fail('malformed',value.node); throw error; }
  }
  function actual(id:string,runId:string,key:string,from:CleanupNode) {
    const found=graph.attempts.get(id); require(found,from,'missing'); graph.edge(from,attempt(found),'prior-attempt');
    require(found.runId===runId,attempt(found),'foreign'); require(found.operationKey===key,attempt(found),'ownership'); return found;
  }
  function agent(value:CleanupAttemptFact,validator:string,purpose:string) {
    const node=attempt(value),meta=value.agent;
    require(value.kind==='agent' && value.outcome==='succeeded' && value.launch==='started' && value.quiescent && !value.occupied
      && meta?.validator===validator && meta.validatedResultCaptureId && meta.reusedAttemptId===null,node,'ownership');
    require(new Set([meta.inputsCaptureId,meta.resultCaptureId,meta.validatedResultCaptureId]).size===3
      && meta.outputCaptureId!==meta.inputsCaptureId && meta.outputCaptureId!==meta.validatedResultCaptureId,node,'ownership');
    const wrapper=parsed(read(meta.inputsCaptureId,value.invocationId,value.id,'context',393216));
    require(shape(wrapper,['inputs','purpose','context','sourceCaptureId']) && strictEffective(wrapper.inputs) && wrapper.purpose===purpose
      && typeof wrapper.context==='string' && cleanupId(wrapper.sourceCaptureId),node);
    const source=read(wrapper.sourceCaptureId,value.invocationId,null,'context',393216); graph.edge(node,source.node,'source-input');
    const original=parsed(source); require(shape(original,['step','inputs','purpose','context','validator']) && original.step===value.operationKey
      && original.validator===validator && original.purpose===purpose && equal(original.inputs,wrapper.inputs) && original.context===wrapper.context,node,'ownership');
    read(meta.resultCaptureId,value.invocationId,value.id,'result',null);
    const output=graph.headers.get(meta.outputCaptureId); require(output,node,'missing');
    require(meta.outputCaptureId===meta.resultCaptureId ? output.channel==='result' : ['stdout','stderr'].includes(output.channel),node,'ownership');
    read(meta.outputCaptureId,value.invocationId,value.id,output.channel,null);
    for (const header of graph.headers.values()) if (header.attemptId===value.id) require(graph.read(header,null),node);
    const normalized=parsed(read(meta.validatedResultCaptureId,value.invocationId,value.id,'validated-result',131072));
    require(shape(normalized,['kind','payload']) && normalized.kind==='result' && cleanupObject(normalized.payload)
      && text(normalized.payload.summary),node);
    if (validator==='recipe-review-v1') require(list(normalized.payload.findings,item=>text(item)),node);
    let context:unknown; try { context=graph.parse(wrapper.context); graph.retain(context); } catch(error) { if(error instanceof SyntaxError) fail('malformed',node); throw error; }
    return {context,payload:normalized.payload,inputs:wrapper.inputs};
  }
  function invalidAgent(value:CleanupAttemptFact,validator:string,purpose:string) {
    const node=attempt(value),meta=value.agent;
    require(value.kind==='agent' && value.outcome==='failed' && value.launch==='started' && value.quiescent && !value.occupied
      && meta?.validator===validator && meta.validatedResultCaptureId===null && meta.reusedAttemptId===null,node,'ownership');
    require(meta.inputsCaptureId!==meta.resultCaptureId && meta.outputCaptureId!==meta.inputsCaptureId,node,'ownership');
    const wrapper=parsed(read(meta.inputsCaptureId,value.invocationId,value.id,'context',393216));
    require(shape(wrapper,['inputs','purpose','context','sourceCaptureId']) && strictEffective(wrapper.inputs) && wrapper.purpose===purpose
      && typeof wrapper.context==='string' && cleanupId(wrapper.sourceCaptureId),node);
    const source=read(wrapper.sourceCaptureId,value.invocationId,null,'context',393216);graph.edge(node,source.node,'source-input');
    const original=parsed(source);require(shape(original,['step','inputs','purpose','context','validator']) && original.step===value.operationKey
      && original.validator===validator && original.purpose===purpose && equal(original.inputs,wrapper.inputs) && original.context===wrapper.context,node,'ownership');
    read(meta.resultCaptureId,value.invocationId,value.id,'result',null);
    const output=graph.headers.get(meta.outputCaptureId);require(output,node,'missing');
    require(meta.outputCaptureId===meta.resultCaptureId ? output.channel==='result' : ['stdout','stderr'].includes(output.channel),node,'ownership');
    read(meta.outputCaptureId,value.invocationId,value.id,output.channel,null);
    for(const header of graph.headers.values()) if(header.attemptId===value.id) require(graph.read(header,null),node);
    let context:unknown;try {context=graph.parse(wrapper.context);graph.retain(context);}catch(error){if(error instanceof SyntaxError)fail('malformed',node);throw error;}
    return {context,inputs:wrapper.inputs};
  }
  function report(header:CleanupCaptureHeader) {
    const node=capture(header.invocationId,header.id), raw=read(header.id,header.invocationId,null,'report',131072), value=parsed(raw);
    if(!ordinaryDeclaration(value)) return false;
    require(cleanupObject(value),node);
    const audit=value.kind==='audit-report',owner=graph.invocations.get(header.invocationId);
    require(owner?.stage==='finalized' && owner.outcome==='succeeded' && header.attemptId===null,node,'ownership');
    require([...graph.headers.values()].filter(item=>item.invocationId===owner.id&&item.channel==='report').length===1,node,'ownership');
    require(shape(value,['version','kind','status','candidateFingerprint','candidate','checks','corrections','skipped','priorAttempts',...(audit?['investigations']:[])]),node);
    require(value.status==='complete' && typeof value.candidateFingerprint==='string' && /^[a-f0-9]{64}$/.test(value.candidateFingerprint)
      && summary(value.candidate) && Number.isSafeInteger(value.corrections) && Number(value.corrections)>=0 && Number(value.corrections)<=2
      && list(value.skipped,item=>text(item)) && new Set(value.skipped).size===value.skipped.length
      && cleanupObject(value.priorAttempts) && Object.keys(value.priorAttempts).length<=100
      && Object.entries(value.priorAttempts).every(([key,id])=>cleanupId(key)&&cleanupId(id))
      && list(value.checks,item=>shape(item,['name','attemptId','exitCode','cleanup'])&&text(item.name)&&cleanupId(item.attemptId)
        && item.exitCode===0&&item.cleanup==='complete'),node);
    require(owner.inputCaptureId,node,'missing');
    const root=parsed(read(owner.inputCaptureId,owner.id,null,'context',393216));
    require(shape(root,['inputs','question','contexts']) && input(root.inputs,audit) && root.question===owner.question && equal(root.contexts,owner.contexts),node);
    const options=root.inputs, prior=cleanupObject(options.priorAttempts)?options.priorAttempts:{}, mapped=value.priorAttempts;
    for(const [key,id] of Object.entries(prior)) actual(id as string,owner.runId,key,node);
    for(const [key,id] of Object.entries(mapped)) actual(id as string,owner.runId,key,node);
    const groups=new Map<string,CleanupAttemptFact[]>(), indices=new Map<string,number>();
    for(const fact of graph.attempts.values()) {
      graph.tick(); if(fact.invocationId!==owner.id || !Object.hasOwn(mapped,fact.operationKey)) continue;
      const group=groups.get(fact.operationKey)??[]; require(group.length<6,attempt(fact),'limit');graph.retain([fact.operationKey,fact.id]);group.push(fact);groups.set(fact.operationKey,group);
    }
    for(const [key,id] of Object.entries(mapped)) {
      const final=actual(id as string,owner.runId,key,node), group=groups.get(key)??[];
      group.sort((a,b)=>cleanupCursor(a.cursor)<cleanupCursor(b.cursor)?-1:1);
      if(group.length) {
        require(group.at(-1)?.id===id,node,'ownership'); let previous=prior[key]??null;
        for(const fact of group) {require(fact.priorAttemptId===previous,attempt(fact),'ownership');previous=fact.id;}
      } else {
        require(prior[key]===id,node,'ownership');
        const previousOwner=graph.invocations.get(final.invocationId);
        require(previousOwner && cleanupCursor(previousOwner.cursor)<cleanupCursor(owner.cursor),attempt(final),'ownership');
      }
    }
    for(const key of Object.keys(prior)) require(Object.hasOwn(mapped,key),node,'ownership');
    const used=new Set<string>(), selected=Array.isArray(options.checks)?options.checks:[];
    function next(key:string) {
      const index=indices.get(key)??0, fact=groups.get(key)?.[index]; require(fact,node,'missing');
      indices.set(key,index+1); graph.retain(fact.id);used.add(fact.id); return fact;
    }
    function checks(verified:unknown) {
      require(list(verified,item=>shape(item,['name','attemptId','exitCode','cleanup'])&&text(item.name)&&cleanupId(item.attemptId)
        && Number.isSafeInteger(item.exitCode)&&item.cleanup==='complete') && verified.length===selected.length,node);
      for(let i=0;i<selected.length;i++) {
        const spec=selected[i] as Obj, check=verified[i] as Obj, key=`${audit?'audit':'change'}/check/${spec.name}`;
        const fact=next(key); require(check.name===spec.name && check.attemptId===fact.id,node,'ownership');
        graph.edge(node,attempt(fact),'objective');
        require(fact.kind==='command' && fact.launch==='started' && fact.quiescent && !fact.occupied
          && fact.outcome===(check.exitCode===0?'succeeded':'failed'),attempt(fact),'ownership');
        const contexts=[...graph.headers.values()].filter(item=>item.attemptId===fact.id&&item.channel==='context'); require(contexts.length===1,node,'ownership');
        const command=parsed(read(contexts[0]!.id,header.invocationId,fact.id,'context',393216));
        require(shape(command,['argv','cwd','env','shell','required','timeoutMs','childScope','limitation']) && equal(command.argv,spec.argv)
          && (spec.env===undefined || equal(command.env,spec.env)) && (spec.timeoutMs===undefined || command.timeoutMs===spec.timeoutMs)
          && command.shell===false && command.required===false,node,'ownership');
      }
      return verified as Obj[];
    }
    const phases=cleanupObject(options.agents)?options.agents:{};
    function runAgent(key:string,purpose:string,validator:string,expectedContext:unknown,config:unknown) {
      let fact=next(key);
      const supplied=cleanupObject(config)?config:{}, expected=JSON.stringify(expectedContext);
      const fields=Object.fromEntries(Object.entries(supplied).filter(([k])=>k!=='profile'&&k!=='timeoutMs'));
      fields.permissions=purpose==='implementation'?'workspace-write':'read-only';
      function settings(inputs:Obj,expectedFields:Obj,subject:CleanupAttemptFact) {
        const layers=inputs.layers as Obj[],step=layers.filter(layer=>layer.source==='step');
        require(inputs.profile===(supplied.profile??null) && step.length===1 && equal(step[0]!.fields,expectedFields),attempt(subject),'ownership');
      }
      if(fact.outcome==='failed') {
        const previous=fact, invalid=invalidAgent(previous,validator,purpose), previousMeta=previous.agent;
        require(previousMeta,attempt(previous),'missing');
        require(shape(invalid.context,['operation','context'])&&invalid.context.operation===key&&invalid.context.context===expected,attempt(previous),'digest');
        settings(invalid.inputs,fields,previous);
        fact=next(key);require(fact.priorAttemptId===previous.id,attempt(fact),'ownership');
        const corrected=agent(fact,validator,purpose), context=corrected.context;
        require(shape(context,['instruction','operation','originalContext','resultCaptureId','diagnostic'])
          && context.instruction==='Correct only the saved control output format. Do not edit code or repeat the work.'
          && context.operation===key && context.originalContext===expected && context.resultCaptureId===previousMeta.resultCaptureId
          && text(context.diagnostic),attempt(fact),'ownership');
        graph.edge(attempt(fact),capture(previous.invocationId,previousMeta.resultCaptureId),'source-capture');
        settings(corrected.inputs,{...fields,permissions:'read-only'},fact);
        require(corrected.inputs.permissions==='read-only',attempt(fact),'ownership');
        return corrected.payload;
      }
      const saved=agent(fact,validator,purpose);
      require(shape(saved.context,['operation','context'])&&saved.context.operation===key&&saved.context.context===expected,attempt(fact),'digest');
      settings(saved.inputs,fields,fact);
      return saved.payload;
    }
    let plan=''; if(typeof options.plan==='string') plan=options.plan;
    else if(cleanupObject(options.plan)&&Array.isArray(options.plan.steps)) plan=JSON.stringify({steps:options.plan.steps.filter(step=>!(step as Obj).skip)});
    let request=JSON.stringify({prompt:options.prompt??null,plan:plan||null});
    const skipped:string[]=[]; let planning:Obj|undefined, investigations:Obj[]=[];
    const prefix=audit?'audit':'change';
    if(audit && !(cleanupObject(options.browserVerification)&&options.browserVerification.enabled)) skipped.push('agent-browser-verification');
    if(options.planning) {
      planning=runAgent(`${prefix}/planning`,'report','recipe-summary-v1',JSON.parse(request),phases.planning);
      if(!audit) request=JSON.stringify({request,planning});
    } else skipped.push('planning');
    let candidate:Obj;
    if(!audit) {
      candidate=options.implement===false?{summary:'Implementation explicitly skipped; inspect current worktree.'}:
        runAgent('change/implementation','implementation','recipe-summary-v1',JSON.parse(request),phases.implementation);
      if(options.implement===false) skipped.push('implementation');
    } else {
      for(const scope of options.scopes as Obj[]) {
        if(scope.skip) { skipped.push(`scope:${scope.name}`); continue; }
        const cfg={...(cleanupObject(phases.investigation)?phases.investigation:{}),...(cleanupObject(scope.agent)?scope.agent:{})};
        const result=runAgent(`audit/investigation/${scope.name}`,'report','recipe-summary-v1',
          {request,...(planning?{planning}:{}),scope,instruction:'Investigate the explicit target without editing or switching the worktree.'},cfg);
        investigations.push({name:scope.name,target:scope.target,result});
      }
      require(list(value.investigations,item=>shape(item,['name','target','result'])&&text(item.name)&&text(item.target)&&summary(item.result))
        && equal(value.investigations,investigations.map(item=>({name:item.name,target:item.target,result:{summary:(item.result as Obj).summary}}))),node,'digest');
      if(options.synthesis===false) {candidate={summary:JSON.stringify(investigations)};skipped.push('synthesis');}
      else candidate=runAgent('audit/synthesis','report','recipe-summary-v1',{request,...(planning?{planning}:{}),investigations},phases.synthesis);
    }
    if(!audit && !(cleanupObject(options.browserVerification)&&options.browserVerification.enabled)) skipped.push('agent-browser-verification');
    if(options.review===false) skipped.push('review');
    const writer=audit?'audit/synthesis':'change/implementation', purpose=audit?'report':'implementation';
    for(let round=0;round<=Number(value.corrections);round++) {
      let verified:unknown=value.checks;
      if(round<Number(value.corrections)) {
        const nextWriter=groups.get(writer)?.[indices.get(writer)??0]; require(nextWriter,node,'missing');
        const saved=nextWriter.outcome==='failed'?invalidAgent(nextWriter,'recipe-summary-v1',purpose):agent(nextWriter,'recipe-summary-v1',purpose);
        require(shape(saved.context,['operation','context'])&&saved.context.operation===writer&&typeof saved.context.context==='string',attempt(nextWriter));
        let correction:unknown;
        try {correction=graph.parse(saved.context.context);graph.retain(correction);} catch(error) {if(error instanceof SyntaxError) fail('malformed',attempt(nextWriter));throw error;}
        require(cleanupObject(correction),attempt(nextWriter)); verified=audit?correction.verified:correction.checks;
      }
      const checked=checks(verified);
      const findings=checked.filter(item=>item.exitCode!==0).map(item=>`Check ${item.name} exited ${item.exitCode}; attempt ${item.attemptId}`);
      const reviewContext=audit?{request,investigations,candidate,verified:checked}:{request,candidate,verified:checked};
      if(!findings.length && cleanupObject(options.browserVerification)&&options.browserVerification.enabled) {
        const reviewed=runAgent(`${prefix}/browser-verification`,'review','recipe-review-v1',reviewContext,options.browserVerification.agent);
        findings.push(...reviewed.findings as string[]);
      }
      if(!findings.length && options.review!==false) {
        const reviewed=runAgent(`${prefix}/review`,'review','recipe-review-v1',reviewContext,phases.review);
        findings.push(...reviewed.findings as string[]);
      }
      if(round===Number(value.corrections)) {require(findings.length===0,node,'digest');break;}
      require(findings.length>0 && (audit?options.synthesis!==false:options.implement!==false),node,'ownership');
      const config={...(cleanupObject(audit?phases.synthesis:phases.implementation)?(audit?phases.synthesis:phases.implementation) as Obj:{}),
        ...(cleanupObject(phases.repair)?phases.repair:{})};
      const correctionContext=audit?{request,investigations,candidate,findings,verified:checked,instruction:'Correct only the report; do not edit the repository.'}
        :{request,candidate,findings,checks:checked};
      candidate=runAgent(writer,purpose,'recipe-summary-v1',correctionContext,config);
    }
    require(value.candidate.summary===candidate.summary,node,'digest');
    require(equal(value.skipped,skipped),node,'digest');
    for(const fact of graph.attempts.values()) if(fact.invocationId===owner.id && fact.kind==='agent') require(used.has(fact.id),attempt(fact),'ownership');
    for(const group of groups.values()) for(const fact of group) require(used.has(fact.id),attempt(fact),'ownership');
    const recognized={key:{invocationId:owner.id,captureId:header.id},format:audit?'audit-report-v1' as const:'change-report-v1' as const,sha256:raw.sha256};
    graph.retain(recognized);graph.report(recognized);
    return true;
  }
  return { inspect(header:CleanupCaptureHeader) { try { report(header); } catch(error) { if(!(error instanceof Refusal)) throw error; } } };
}
