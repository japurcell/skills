import type { EffectiveInputs } from '../profiles.js';
export interface SessionEvent {
  nativeId: string;
  parentNativeId: string | null;
  lifecycle: 'running' | 'succeeded' | 'failed' | 'stopped';
  usage?: { tokens: number; scope: 'self' | 'includes-children' };
  loadedSkills?: string[];
}
export interface AdapterRequest {
  attemptId: string;
  invocationId: string;
  worktree: string;
  inputs: EffectiveInputs;
  context: string;
  reuseNativeId?: string;
}
export interface AdapterLaunch {
  argv: string[];
  env: Record<string, string>;
  childScope: 'process-group' | 'unknown';
  /** Optional UTF-8 text sent exactly to a managed child stdin pipe, then closed. Maximum 1 MiB. */
  stdin?: string;
  /** Per-launch decoder state; called only after this stream's raw bytes are saved. */
  mapEvent?(line: string, channel: 'stdout' | 'stderr'): SessionEvent | undefined;
  /** Nonempty unique stream selection; defaults to the adapter's eventChannel. */
  eventChannels?: readonly ('stdout' | 'stderr')[];
}
/** Trusted adapters implement an exact qualified mode. Never launch inside validation or start. */
export interface AgentAdapter {
  readonly id: string;
  readonly capabilities: readonly string[];
  validateProfile(inputs: EffectiveInputs): void;
  canReuse(previous: EffectiveInputs, next: EffectiveInputs): boolean;
  start(request: AdapterRequest): AdapterLaunch;
  readonly finalChannel: 'stdout' | 'stderr';
  readonly eventChannel: 'stdout' | 'stderr';
  readonly questionExitCodes: readonly number[];
  /** Decode only the selected bounded authoritative capture, never arbitrary log text. */
  decodeFinal(text: string): unknown;
  mapEvent(line: string): SessionEvent | undefined;
  requestStop(stopOwnedScope: () => Promise<void>): Promise<void>;
}
export interface PayloadValidator<T = unknown> {
  name: string;
  validate(value: unknown): value is T;
}
export type AgentResult<T = unknown> =
  | {
      attemptId: string;
      status: 'succeeded';
      value: T;
      artifacts: string[] | { state: 'unknown' };
      resultCaptureId: string;
      validatedResultCaptureId?: string;
    }
  | { attemptId: string; status: 'invalid'; diagnostic: string; resultCaptureId: string };
