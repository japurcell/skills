import { appendFileSync } from 'node:fs';
import { randomUUID } from 'node:crypto';
import { join } from 'node:path';

const args = process.argv.slice(2);
const worktree = args[args.indexOf('-C') + 1];
let packet = '';
for await (const chunk of process.stdin) packet += chunk;
const mode = packet.startsWith('Active task:\n') ? packet.slice('Active task:\n'.length).split('\n')[0] : '';
appendFileSync(join(worktree, 'copilot-launches.jsonl'), JSON.stringify({ args, stdin: packet }) + '\n');
const emit = value => process.stdout.write(JSON.stringify(value) + '\n');
const sessionId = randomUUID();
emit({ type: 'assistant.turn_start', data: { turnId: '0' } });
if (mode === 'hold') {
  setInterval(() => {}, 1000);
} else {
  if (mode === 'denied') emit({ type: 'tool.execution_complete', data: { success: false, error: { code: 'denied', message: 'private native detail' } } });
  if (mode === 'native-error') emit({ type: 'error', data: { message: 'private native detail' } });
  // A tool request is not a final assistant answer.
  emit({ type: 'assistant.message', data: { messageId: 'tool-message', content: '{"kind":"result","payload":"decoy"}' } });
  const content = mode === 'malformed' && !packet.includes('Saved context:\n') ? 'PRIVATE_INVALID_ASSISTANT' :
    mode === 'question' ? '{"kind":"needs_input","question":"Which target?","context":"Missing target","suggestions":["one"]}' :
      '{"kind":"result","payload":{"summary":"qualified"}}';
  emit({ type: 'assistant.message_start', data: { messageId: 'final-message', phase: 'final_answer' } });
  emit({ type: 'assistant.message_delta', data: { messageId: 'final-message', deltaContent: content } });
  if (mode !== 'no-terminal') {
    emit({ type: 'assistant.turn_end', data: { turnId: '0' } });
    emit({ type: 'result', sessionId, exitCode: 0, usage: { premiumRequests: 1 } });
  }
}
