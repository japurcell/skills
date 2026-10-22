import { spawnSync } from 'node:child_process';
import { randomUUID } from 'node:crypto';
import { appendFileSync } from 'node:fs';
import { setTimeout as delay } from 'node:timers/promises';
const request = JSON.parse(process.argv[2]);
const prompt = request.inputs.prompt;
const nativeId = request.reuseNativeId ?? randomUUID();
process.stderr.write(JSON.stringify({ kind: 'session', nativeId, parentNativeId: null, lifecycle: 'running' }) + '\n');
appendFileSync(
  'agent-launches.jsonl',
  JSON.stringify({
    attemptId: request.attemptId,
    nativeId,
    reused: !!request.reuseNativeId,
    inputs: request.inputs,
    context: request.context,
  }) + '\n',
);
if (prompt === 'children') {
  const childId = randomUUID();
  process.stderr.write(
    JSON.stringify({ kind: 'session', nativeId: childId, parentNativeId: nativeId, lifecycle: 'running' }) + '\n',
  );
  const child = spawnSync(process.execPath, ['-e', 'process.stdout.write("child output")'], { encoding: 'utf8' });
  if (child.status !== 0) process.exit(1);
  process.stderr.write(
    JSON.stringify({
      kind: 'session',
      nativeId: childId,
      parentNativeId: nativeId,
      lifecycle: 'succeeded',
      usage: { tokens: 4, scope: 'self' },
    }) + '\n',
  );
}
if (prompt === 'oversized-event') process.stderr.write(JSON.stringify({kind:'log',message:'x'.repeat(1048576)})+'\n');
if (prompt === 'oversized-result') process.stdout.write(JSON.stringify({kind:'result',payload:'x'.repeat(1048576)}));
if (prompt === 'denied') {
  process.stderr.write(JSON.stringify({ kind: 'denied', message: 'permission denied' }) + '\n');
  process.exit(1);
}
if (prompt === 'interaction') {
  process.stderr.write(
    JSON.stringify({ kind: 'interaction', message: 'terminal closed:' + process.stdin.isTTY }) + '\n',
  );
  process.exit(1);
}
if (prompt === 'hold') await delay(30000);
if (prompt === 'bad-session') {
  process.stderr.write(JSON.stringify({kind:'session',nativeId,parentNativeId:null,lifecycle:'running',usage:{tokens:-1,scope:'self'}})+'\n');
  await delay(30000);
}
if (['bad-event','bad-event-unknown'].includes(prompt)) {
  process.stderr.write('invalid event bytes\n');
  await delay(30000);
}
if (request.context.startsWith('wait:')) await delay(Number(request.context.slice(5)));
if (prompt === 'reuse-fail' && request.reuseNativeId) process.exit(70);
if (prompt === 'oversized-result') {}
else if (prompt === 'malformed' && !request.context.startsWith('correct')) process.stdout.write('{invalid control JSON');
else if (prompt === 'missing') {
} else if (['question', 'question-unknown', 'question-early', 'question-fail'].includes(prompt)) {
  process.stdout.write(
    JSON.stringify({ kind: 'needs_input', question: 'Which target?', context: 'An explicit target is required.' }),
  );
  process.exitCode = prompt === 'question-fail' ? 70 : 2;
  if (prompt === 'question-early') {
    process.stdout.end();
    await delay(30000);
  }
} else
  process.stdout.write(
    JSON.stringify({ kind: 'result', payload: request.context==='correct-number'?7:{ summary: 'complete', nativeId, prompt, model: request.inputs.model } }),
  );
process.stderr.write(
  JSON.stringify({
    kind: 'session',
    nativeId,
    parentNativeId: null,
    lifecycle: 'succeeded',
    ...(prompt === 'children'
      ? { usage: { tokens: 9, scope: 'includes-children' }, loadedSkills: ['fixture-observed'] }
      : {}),
  }) + '\n',
);
