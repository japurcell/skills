# Benchmark delegation scheduler behavior on Codex and Copilot

Completed 2026-11-11. This archived plan is `brain/archive/plans/31-scheduler-evaluation/ExecPlan.md`. All 24 authorized provider attempts and independent evidence review are complete. The valid comparison matrix is incomplete; exclusions and confounds are reported rather than retried. No work remains for this experiment.

## Purpose / Big Picture

Determine whether replacing prose-only delegation deadline guidance with the bundled scheduler improves sampled coordination correctness, and measure observed time and token tradeoffs on Codex and Copilot. Separate written decisions, actual CLI execution with synthetic worker facts, and real native worker control. The experiment does not prove native worker shutdown or general reliability.

The scope was three scenarios, two skill variants, two providers, and two repetitions: 24 fresh-session attempts. The user authorized the remaining 14 calls after reviewing the payload. No additional model calls, whole-suite evaluation, CI changes, or commits were performed during final review. Documentation changes received static validation only.

## Progress

- [x] (2026-11-11) [milestone-1] T1: Freeze baseline/current/router snapshots, hashes, provider preflight, and matched scenario design.
- [x] (2026-11-11) [milestone-2] T2: Retain the narrow harness and its 15 passing infrastructure fixtures; preserve known automatic-grading limitations.
- [x] (2026-11-11) [milestone-2] T3: Retain smoke receipts, original access failures, and the explicit scoped-access revision effective from cell 11.
- [x] (2026-11-11) [milestone-3] T4: Execute all 24 manifest attempts without replacing failures or adding retries.
- [x] (2026-11-11) [milestone-3] T5: Independently review all cells, adjudicate delivery/catalog exposure, and produce the report, benchmark JSON, 24 reviewed grading files, and static viewer.
- [x] (2026-11-11) [milestone-3] Verify paired arithmetic, artifact references, unchanged snapshots/current source, the real-clock bounded wait probe, and plan navigation; close both runner and reviewer assignments.

## Context and Evidence

Working directory: `/Users/adam/dev/skills`. Evaluated source: `skills/default/delegate-to-subagents`. Evidence root, abbreviated `EVIDENCE` below: `/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-eval-09vb9n1r`.

- [Authoritative report](report.md)
- [Structured benchmark](benchmark.json)
- [Static review viewer](review.html)
- [Immutable input manifest](/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-eval-09vb9n1r/snapshots-manifest.json)
- [Final integrity receipt](/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-eval-09vb9n1r/final-integrity-check.json)
- [Bounded wait receipt](/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-eval-09vb9n1r/real-wait-probe/receipt.json)

Raw cells remain under `EVIDENCE/harness/prepared-matrix-t3-attempt-1/iteration-1/eval-A|B|C/codex|copilot/old_skill|with_skill/repeat-1|2/`. The redundant `review-copies/` directory was removed at the user's request on 2026-11-11. The benchmark and embedded static viewer retain per-assertion review findings, output-contract status, eligibility and native evidence references; original prompts and authored outputs remain in the external raw cells. The raw provisional grades are not authoritative.

Codex 0.167.1 requested `gpt-6.1-sol` with medium reasoning; native output does not independently confirm resolved model identity. Copilot 1.0.109 reports `gpt-6-luna` with medium reasoning. Settings were matched within provider and access revision. The baseline is the pre-script snapshot, not a reconstruction from current Git HEAD.

## Plan of Work and Acceptance

### Milestone 1: Freeze a reproducible experiment
Status: done
Acceptance: met

T1 had no prerequisites. Immutable source snapshots, per-file SHA256 records, seven successful provider/help captures, and frozen scenarios are retained. Final verification found no snapshot mismatches or current candidate source changes. Aggregate hashes are old `6c131a364fb593428e2c4afab2f50d6accfec10748592caa59cbb87762a81a5d`, current `18cc02a7d3f535de98dbec187e7e2fdeed86daa647da029c13dc3840c5da6e2a`, and router `23cc9ace9810c74d50f14130193539792ee60caab5fdef05710d9d8f2212b729`.

### Milestone 2: Retain execution evidence and establish review boundaries
Status: done
Acceptance: met

T2 depended on T1; T3 depended on the harness checks. The temporary harness captured fresh sessions, exact prompts/settings, provider events, artifacts, monotonic process timing, and usage under a 600-second process limit. Fifteen infrastructure fixtures passed. Smoke proved arithmetic/tool execution but initially missed denied skill reads; the later explicit delivery gate corrected this for remaining cells. The original failures and immutable access revision are preserved.

The proposed broad automatic semantic grader was not completed or accepted. Final acceptance uses independent assertion-by-assertion review against the unchanged frozen rubric, plus arithmetic and artifact consistency checks. No failing test was removed or weakened. The generic C schema and tool-count heuristics remain documented limitations of provisional artifacts.

### Milestone 3: Run, review, and explain the comparison
Status: done
Acceptance: met

T4 depended on provider preparation and authorization; T5 depended on retained runs. All 24 attempts completed. Five lack proven selected-skill delivery; one additional baseline has proven delivery but no matched candidate under the same access revision. Eighteen cells form nine matched pairs. Two Copilot execution pairs are permission-confounded and cannot establish scheduler effectiveness. There is no valid Copilot A pair and only one Copilot B pair.

Scenario A checks a bounded four-field checkpoint request, valid completion/stop/one-extension choices, and an ETA-based extension with monitoring rearmed. Scenario B checks stopping after a missed checkpoint, stopping after the sole extension without reset, and confirmed worker plus write shutdown before replacement. Each has three common assertions.

Scenario C executes real CLI processes with synthetic times and worker facts. Its five common assertions cover A closing, B's one timely extension, stop request and second-extension rejection, ownership retained during unconfirmed shutdown while C proceeds independently, and final closed/transferred state after confirmation. Candidate-only C6 proves the immutable bundled commands executed and is excluded from common-score denominators. A synthetic parent transfer record suffices; the rubric does not require a separate state file or real worker transfer.

## Outcomes & Retrospective

| Provider and scenario | Old common passes | Current common passes | Interpretation |
| --- | --- | --- | --- |
| Codex A | 3/3, 3/3 | 3/3, 3/3 | Written decisions tie. |
| Codex B | 3/3, 3/3 | 3/3, 3/3 | Written decisions tie. |
| Codex C | 5/5, 5/5 | 4/5, 5/5 | Current repeat 1 records transfer authorization without a parent transfer. |
| Copilot B | 2/3 | 3/3 | Current improves the missed-checkpoint decision but writes the result to the wrong directory. |
| Copilot C | 0/5, 0/5 | 5/5, 4/5 | Baseline execution was denied by permissions; no causal comparison. |

All four current C runs prove bundled-script execution. Current Copilot C repeat 2 also lacks a simulated parent transfer. These completion gaps are not evidence of premature ownership transfer or actual worker safety failures. Overall improvement is not established.

Codex A averaged 8.1 additional seconds and 30,657 additional reported input tokens with the current skill; B averaged 6.1 additional seconds and 48,670.5 additional input tokens. C timing is confounded by different tool-call granularity, and Copilot C additionally by denied baseline execution. Full per-cell values, paired deltas, and sample standard deviations are in the benchmark. Provider time excludes setup, smoke, approval, orchestration, and review. Native token counters are not dollar costs; cached and reasoning subsets are not added twice. Two repeats at most support a diagnostic result only.

The requested brain, reflect, and exec-plans guidance updates remain present. Exec-plans uses repository-neutral durable documentation conventions; reflect supports a review without an active plan. Five skill bundles passed static validation, and staged/unstaged whitespace checks passed. Durable lessons already reside in [evaluation practice](../../../codebase/testing.md) and [guidance placement](../../../principles/guard-the-context-window.md); both were verified reachable from `brain/index.md`. This plan stores task evidence and links to those lessons.

## Surprises & Discoveries

Startup skill catalog metadata did not prove candidate-content contamination. Native reads established that three flagged Copilot baselines received only the selected old body. One early baseline received its full skill through Python despite denied direct reads, correcting the provisional exclusion count from six to five.

The provisional grader applied A/B output fields to C and missed wrapped script execution. Independent review used C's actual `actions` and `final_state` contract. Review initially also demanded an unstated separate ownership-state record; per-cell rereading corrected this before final scores. Codex current C repeat 2 and Copilot current C repeat 1 explicitly record synthetic parent transfers and pass.

The bounded real-clock command `rtk proxy python3 skills/default/delegate-to-subagents/scripts/scheduler.py --state EVIDENCE/real-wait-probe/state.json wait --max-wait 0.2` returned exit 0, no events, and 0.239714 seconds process elapsed. It verifies the bounded no-event wait path only.

## Decision Log

- 2026-11-11: Preserve all 24 attempts and report the incomplete valid matrix; do not add retries beyond the approved scope.
- 2026-11-11: Use independent semantic review and native evidence for final grading. Keep provisional automatic outputs unchanged; report their limitations instead of expanding a temporary grader.
- 2026-11-11: Keep output-contract failures separate from semantic correctness, and permission-confounded observations separate from effectiveness claims.
- 2026-11-11: Archive this completed plan after verifying durable-note navigation and retained historical evidence. No scheduler or skill fixes are inferred from the benchmark request.

## Concrete Steps and Recovery

No task action remains. Review the report and viewer for conclusions and inspect the cited raw cells for individual assertions. Runner and reviewer assignments are marked completed in `EVIDENCE/scheduler.json`; all provider runner sessions returned. OS-wide process listing was denied, so independent system-process enumeration was unavailable. No workers were replaced or assigned overlapping writes during closure.

Do not overwrite original runs or use the provisional automatic pass count as the result. A future authorized evaluation should verify actual skill delivery and permitted execution in a matched pilot, then use fresh run/session identities. Do not change user-global configuration or add broad permission bypasses to repair these retained attempts.

## Historical Record

The [pre-final-review plan snapshot](/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-eval-09vb9n1r/plan-before-final-review.md) retains the original command design, assertions, proposed automation, intermediate status, and recovery details. Its contents were verified before replacing the active plan. It is historical evidence and does not authorize further runs. All reusable guidance is linked from the durable topic notes above.
