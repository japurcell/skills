export interface Admission {
  id: string; invocationId: string; operationKey: string; kind: 'agent' | 'command';
  intent: 'initial' | 'code_correction' | 'format_correction' | 'repeat' | 'followup';
  priorAttemptId?: string; loopKey?: string;
}

export function operationKey(value: string) {
  if (typeof value !== 'string' || Buffer.byteLength(value) < 1 || Buffer.byteLength(value) > 256 || value.includes('\0')) {
    throw new Error('operation key must contain 1-256 UTF-8 bytes without NUL');
  }
  return value;
}

export function validateAdmission(input: Admission) {
  operationKey(input.id);
  operationKey(input.invocationId);
  operationKey(input.operationKey);
  if (input.loopKey !== undefined) operationKey(input.loopKey);
  if (input.priorAttemptId !== undefined) operationKey(input.priorAttemptId);
  if (!['agent', 'command'].includes(input.kind)) throw new Error('invalid attempt kind');
  if (!['initial', 'code_correction', 'format_correction', 'repeat', 'followup'].includes(input.intent)) throw new Error('invalid attempt intent');
  if ((input.intent === 'code_correction' || input.intent === 'format_correction') && input.kind !== 'agent') throw new Error('corrections require an agent attempt');
}
