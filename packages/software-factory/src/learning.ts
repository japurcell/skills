import type { RepositoryStore } from './store.js';

/** Read-only, deliberately small view of retained history for explicit workflows. */
export interface SourceHistoryGateway {
  read(invocationId: string, afterAttempt?: number, afterCapture?: number): Promise<{
    invocation: { id: string; outcome: string | null; stage: string };
    attempts: { id: string; invocationId: string; outcome: string | null; operationKey: string }[];
    captures: { id: string; attemptId: string | null; channel: string | null; state: string }[];
    attemptsNextCursor: number; hasMoreAttempts: boolean;
    capturesNextCursor: number; hasMoreCaptures: boolean;
  }>;
  capture(invocationId: string, captureId: string, after?: number, byteBudget?: number): Promise<{
    id: string; channel: string | null; state: string; chunks: { sequence: number; text: string }[];
    nextSequence: number; hasMore: boolean;
  }>;
  event(cursor: string): Promise<{ cursor: string; kind: string; data: object } | null>;
}

const id = (value: string) => {
  if (typeof value !== 'string' || !value || Buffer.byteLength(value) > 256 || value.includes('\0')) throw new Error('invalid source reference');
  return value;
};

/** No store, database, mutation, or unrestricted history enumeration escapes this port. */
export function sourceHistoryGateway(store: RepositoryStore, track: <T>(action: () => Promise<T>) => Promise<T>): SourceHistoryGateway {
  return Object.freeze({
    read: (invocationId: string, afterAttempt = 0, afterCapture = 0) => track(async () => {
      const page = store.readHistory(id(invocationId), { afterAttempt, afterCapture, limit: 20 });
      return {
        invocation: { id: page.invocation.id, outcome: page.invocation.outcome, stage: page.invocation.stage },
        attempts: page.attempts.map(({ id, invocationId, outcome, operationKey }) => ({ id, invocationId, outcome, operationKey })),
        captures: page.captures.map(({ id, attemptId, channel, state }) => ({ id, attemptId, channel, state })),
        attemptsNextCursor: page.attemptsNextCursor, hasMoreAttempts: page.hasMoreAttempts,
        capturesNextCursor: page.capturesNextCursor, hasMoreCaptures: page.hasMoreCaptures,
      };
    }),
    capture: (invocationId: string, captureId: string, after = 0, byteBudget = 32768) => track(async () => {
      if (!Number.isSafeInteger(byteBudget) || byteBudget < 1 || byteBudget > 32768) throw new Error('invalid source capture budget');
      const request = { invocationId: id(invocationId), id: id(captureId), after, limit: 20, byteBudget };
      return store.readInvocationCapture(request);
    }),
    event: (cursor: string) => track(async () => {
      if (typeof cursor !== 'string' || !/^[1-9]\d{0,18}$/.test(cursor) || BigInt(cursor) > 9223372036854775807n) throw new Error('invalid source event cursor');
      const page = store.readEvents({ after: String(BigInt(cursor) - 1n), limit: 1 });
      return page.events[0]?.cursor === cursor ? page.events[0] : null;
    }),
  });
}
