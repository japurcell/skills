import type { AgentAdapter, SessionEvent } from './types.js';
/** Test-only protocol adapter. No provider implementation or support claim. */
export function createFakeAdapter(options: { executable: string; script: string; reuse?: boolean }): AgentAdapter {
  return {
    id: 'fake',
    finalChannel: 'stdout',
    eventChannel: 'stderr',
    questionExitCodes: [2],
    decodeFinal: (text) => JSON.parse(text),
    capabilities: [
      'live-output',
      'lifecycle',
      'final-output',
      'stop',
      'instructions',
      'native-skills',
      'model',
      'reasoning',
      'read-only',
      'workspace-write',
    ],
    validateProfile(inputs) {
      if (inputs.model === 'unsupported') throw new Error('fake model unsupported');
    },
    canReuse: () => options.reuse !== false,
    start: (request) => ({
      argv: [options.executable, options.script, JSON.stringify(request)],
      env: {},
      childScope: ['unknown-cleanup', 'question-unknown'].includes(request.inputs.prompt) ? 'unknown' : 'process-group',
    }),
    mapEvent(line) {
      const raw: unknown = JSON.parse(line);
      if (!raw || typeof raw !== 'object') throw new Error('invalid fake event');
      const v = raw as Record<string, unknown>;
      if (v['kind'] !== 'session') return undefined;
      if (
        typeof v['nativeId'] !== 'string' ||
        !v['nativeId'] ||
        !(v['parentNativeId'] === null || typeof v['parentNativeId'] === 'string') ||
        !['running', 'succeeded', 'failed', 'stopped'].includes(String(v['lifecycle']))
      )
        throw new Error('invalid fake session');
      return {
        nativeId: v['nativeId'],
        parentNativeId: v['parentNativeId'] as string | null,
        lifecycle: v['lifecycle'] as SessionEvent['lifecycle'],
        ...(v['usage'] !== undefined ? { usage: v['usage'] as NonNullable<SessionEvent['usage']> } : {}),
        ...(v['loadedSkills'] !== undefined ? { loadedSkills: v['loadedSkills'] as string[] } : {}),
      };
    },
    requestStop: (stop) => stop(),
  };
}
