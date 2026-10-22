import { randomUUID } from 'node:crypto';
import { appendFileSync } from 'node:fs';

const request = JSON.parse(process.argv[2]);
const { scenario, context, launchLog } = JSON.parse(request.context);
appendFileSync(launchLog, JSON.stringify({ context, permissions: request.inputs.permissions }) + '\n');
process.stderr.write(JSON.stringify({ kind: 'session', nativeId: randomUUID(), parentNativeId: null, lifecycle: 'succeeded' }) + '\n');
if (scenario.kind === 'needs_input') {
  process.stdout.write(JSON.stringify({ kind: 'needs_input', question: 'Which target?', context: 'A target is required.' }));
  process.exitCode = 2;
} else if (scenario.kind === 'failure') {
  process.stderr.write('fake extraction infrastructure failure');
  process.exitCode = 70;
} else {
  process.stdout.write(JSON.stringify({ kind: 'result', payload: scenario.payload }));
}
