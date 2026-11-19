# Milestone 3. Compare dispatch wording

Status: done
Acceptance: met

[W1](wording.md) screens the exact old, short and one-clause-shorter instructions with independent controlled worker decisions. [P0](native-fixture.md) packages the calibrated worker policy and trace grader. [P1](paired-dispatch.md) uses both outputs to run three native old/new pairs per caller. Hold the router, catalog, host, assignment and restriction constant within pairs. Publish only wording with the agreed evidence, and retain ties and failures.

## Progress

- [x] [milestone-3] B1 proved the project worker policy rejects a mismatched native task and lets the permitted fallback run.
- [x] [milestone-3] [W1](wording.md) preserves exact W1 text, total words per caller plus shared rules, hashes and observed decisions. Identify the shortest tested survivor.
- [x] [milestone-3] Prove the native grader with a real smoke run and negative controls.
- [x] [milestone-3] Record P1's twelve runs, compare attempts and record completeness, and apply the qualifying wording to the two callers and router. Confirm the router implementation and catalog are unchanged.
- [x] [milestone-3] In P1 the parent used a display name on a generic worker. [P2](paired-dispatch.md#p2-preserve-the-worker-profile-as-well-as-the-model) tests an explicit native profile control.

The published profile-aware caller passes 23/23 controlled checks for each caller and 6/6 native dispatches. Three complete-source checks produced the required worker and result. One had a malformed saved record. See the [per-attempt verdicts](paired-dispatch.md#published-source-check-and-replay-effort).
