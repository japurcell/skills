import { randomUUID } from 'node:crypto';
import { appendFileSync, existsSync, lstatSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
const request=JSON.parse(process.argv[2]);
const {requestContext,scenario}=JSON.parse(request.context), control=JSON.parse(requestContext);
const operation=control.operation;
const phase=operation==='change/implementation'?'implementation':operation.endsWith('/review')?'review':operation.endsWith('/browser-verification')?'browser-verification':operation.endsWith('/planning')?'planning':'report';
const formatCorrection=!!control.instruction;
const log=join(scenario.evidence,'workflow-launches.jsonl');
const previous=existsSync(log)?readFileSync(log,'utf8').trim().split('\n').map(JSON.parse):[];
const count=previous.filter(r=>r.operation===operation&&!r.formatCorrection).length;
appendFileSync(log,JSON.stringify({...request,context:requestContext,operation,phase,formatCorrection,reused:!!request.reuseNativeId})+'\n');
appendFileSync(join(scenario.evidence,'sequence.txt'),phase+'\n');
if(phase==='implementation'&&!formatCorrection&&!(scenario.noOpRepairs&&count>0)) writeFileSync('candidate.txt','Harmless fixture '+count);
if(phase==='implementation'&&scenario.largeCandidate) writeFileSync('growing-candidate.bin',Buffer.alloc(2*1024*1024));
if(phase==='review'&&scenario.writeReview) writeFileSync('candidate.txt','Mutated during review');
if(scenario.ambiguousFingerprint&&phase==='implementation') {
  writeFileSync('A.txt','foo');writeFileSync('B.txt','');
  writeFileSync('B.txt',JSON.stringify(['B.txt',lstatSync('B.txt').mode,'file'])+'bar');
}
if(scenario.ambiguousFingerprint&&phase==='review') {
  const header=JSON.stringify(['B.txt',lstatSync('B.txt').mode,'file']);
  writeFileSync('A.txt','foo'+header);writeFileSync('B.txt','bar');
}
const nativeId=randomUUID();
process.stderr.write(JSON.stringify({kind:'session',nativeId,parentNativeId:null,lifecycle:'succeeded'})+'\n');
if(scenario.infrastructure===phase) {process.stderr.write('permission denied by fake harness');process.exit(70);}
if(scenario.question===phase) {process.stdout.write(JSON.stringify({kind:'needs_input',question:'Which explicit target?',context:'Target information missing.'}));process.exitCode=2;}
else if(scenario.malformed===phase&&(!formatCorrection||scenario.malformedAlways)) process.stdout.write('{invalid output');
else process.stdout.write(JSON.stringify({kind:'result',payload:phase==='review'||phase==='browser-verification'?{summary:'Reviewed',findings:count<(scenario.failReviews??0)?['Concrete review finding']:[]}:{summary:phase+' completed'}}));
