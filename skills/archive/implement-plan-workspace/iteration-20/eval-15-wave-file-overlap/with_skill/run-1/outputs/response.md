## Phase Execution

- Core phase ready set: T010, T011, T012.
- W1 is the only eligible parallel wave.
  - W1-A: T010 — implement query parser in `src/search/service.ts`
  - W1-B: T012 — implement telemetry in `src/search/metrics.ts`
- Launch W1-A (T010) and W1-B (T012) in parallel as separate implementation subagents.
- T010 and T011 cannot run in parallel because both touch `src/search/service.ts`, so keep T011 for W2.
- Wait for W1 results before launching W2.
- W2 is a sequential slot.
  - W2-A: T011 — implement ranking logic in `src/search/service.ts`
- Launch W2-A (T011) only after W1 completes and `src/search/service.ts` is no longer owned by an in-flight wave member.
- Wait for W2 results before closing the Core phase.

Checkpoint Decision
- Status: PASS
- Evidence: Wave plan preserves file ownership boundaries, uses parallelism only for disjoint paths, and serializes the overlapping `src/search/service.ts` work.
- Integrity check: No scheduled wave contains overlapping file targets.
- Next Action: Execute W1, then execute W2 after the W1 wait boundary.
