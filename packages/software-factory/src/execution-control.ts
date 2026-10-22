export class NeedsInput extends Error {}
export class ShutdownInterrupted extends Error {}
export type StopCause = 'needs_input' | 'signal' | 'timeout' | 'recording' | 'failure' | 'manual';
