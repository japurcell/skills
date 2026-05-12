Phase Execution

- Core phase ready set: T010, T011, T012.
- Each implementation subagent loads the `tdd` skill first and is limited to its assigned task ID and allowed file paths.
- **W1 (parallel wave)**
  - Launch W1-A (T010) and W1-B (T012) in parallel as separate implementation subagents.
  - **W1-A — T010:** implement query parser in `src/search/service.ts`. Allowed files: `src/search/service.ts` plus directly required verification files.
  - **W1-B — T012:** implement telemetry in `src/search/metrics.ts`. Allowed files: `src/search/metrics.ts` plus directly required verification files.
- T010 and T011 cannot run in parallel because both touch `src/search/service.ts`, so keep T011 for W2.
- Wait for W1 results before launching W2.
- If either W1 member fails, let the already-launched independent work finish. The controller does not launch another wave until the failure has been reported to the user and resolved.
- **W2 (sequential slot)**
  - Launch W2-A (T011) as a separate implementation subagent after W1 completes and after T010's `src/search/service.ts` changes are verified.
  - **W2-A — T011:** implement ranking logic in `src/search/service.ts`. Allowed files: `src/search/service.ts` plus directly required verification files.
- Wait for W2 results before closing the Core phase.

Checkpoint Decision
- Status: PASS
- Evidence: W1 captures the only file-disjoint parallel work, W2 serializes the overlapping `src/search/service.ts` task, and explicit wait boundaries prevent unsafe overlap.
- Integrity check: No task is marked `[X]` until its assigned subagent returns verification evidence.
- Next Action: Launch W1, wait for results, then launch W2 if W1 completes without blocking failures.
