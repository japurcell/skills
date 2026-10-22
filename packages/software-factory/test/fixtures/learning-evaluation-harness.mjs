import { randomUUID } from 'node:crypto';
import { appendFileSync, readFileSync, readdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const request = JSON.parse(process.argv[2]);
const { context, launchLog, scenario } = JSON.parse(request.context);
if (scenario && typeof scenario === 'object' && scenario.kind === 'extract') {
  const supplied = JSON.parse(context);
  const source = supplied.evidence[0];
  const candidate = source.captures.at(-1);
  const support = scenario.proposalKind === 'capture' ? candidate : source.captures.find(capture => capture.state === 'complete');
  const proposal = { key: 'improve', summary: 'Improve check', target: scenario.target,
    supportingEvidence: [{ invocationId: source.invocationId, captureId: support.id }], contraryEvidence: [],
    suggestedCases: ['candidate check'],
    ...(scenario.proposalKind === 'capture' ? { candidateCapture: { invocationId: source.invocationId, captureId: candidate.id } }
      : { diff: `--- a/${scenario.target.path}\n+++ b/${scenario.target.path}\n@@ -1 +1 @@\n-baseline\n+candidate` }) };
  process.stderr.write(JSON.stringify({ kind: 'session', nativeId: randomUUID(), parentNativeId: null, lifecycle: 'succeeded' }) + '\n');
  process.stdout.write(JSON.stringify({ kind: 'result', payload: { proposals: [proposal] } }));
  process.exit(0);
}
const evaluation = JSON.parse(context);
const scratch = readdirSync(process.cwd()).filter(name => name.startsWith('.factory-evaluation-'));
const visibleVariants = scratch.flatMap(name => readdirSync(join(process.cwd(), name)));
const stagedPath = join(process.cwd(), scratch[0], 'case', evaluation.target.path);
appendFileSync(launchLog, JSON.stringify({ variant: evaluation.variant, permissions: request.inputs.permissions, caseKey: evaluation.caseKey,
  visibleVariants, stagedText: readFileSync(stagedPath, 'utf8'), stagedCwd: join(process.cwd(), scratch[0], 'case') }) + '\n');
process.stderr.write(JSON.stringify({ kind: 'session', nativeId: randomUUID(), parentNativeId: null, lifecycle: 'succeeded' }) + '\n');
if (scenario === 'needs_input') {
  process.stdout.write(JSON.stringify({ kind: 'needs_input', question: 'Which criterion?', context: 'A criterion is required.' }));
  process.exitCode = 2;
} else if (scenario === 'failure') {
  process.stderr.write('fake review failure');
  process.exitCode = 70;
} else {
  if (scenario === 'mutate') writeFileSync(join(process.cwd(), '.factory/agents.json'), '{"changed":"by evaluation reviewer"}');
  process.stdout.write(JSON.stringify({ kind: 'result', payload: {
    judgment: scenario === 'uncertain' ? 'uncertain' : scenario === 'all_pass' ? 'pass'
      : (evaluation.variant === 'candidate') !== (scenario === 'reverse') ? 'pass' : 'fail',
    reason: `Examined ${evaluation.variant} for ${evaluation.caseKey}`,
  } }));
}
