# Semantic second-extension correction review

New user-authorized cycle, pass 1. Reviewed base `28cbfcde64682936271ee2889ea5b378908a62ae` through integrated target `4bcafb705195d9a9e21bbfa57bc5ea117f6c2820`. Captured diff SHA-256: `4b88913e8bec54c2b9e494028667a573b9b91995370fb6951d0ad48956995728`. Scope is the grader and its maintained test; later documentation/preference changes are excluded.

Commands: `git diff 28cbfcde64682936271ee2889ea5b378908a62ae...4bcafb705195d9a9e21bbfa57bc5ea117f6c2820` and `git log 28cbfcde64682936271ee2889ea5b378908a62ae..4bcafb705195d9a9e21bbfa57bc5ea117f6c2820 --oneline`. [Captured source boundary](/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-semantic-fix/source.json), [diff](/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-semantic-fix/diff.patch), [commits](/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-semantic-fix/commits.txt). Both reviewers used Sol with medium reasoning for this plan.

## Standards

Reviewed exact base `28cbfcde64682936271ee2889ea5b378908a62ae` to target `4bcafb705195d9a9e21bbfa57bc5ea117f6c2820`, using captured `source.json`, `diff.patch`, `commits.txt`, and pinned `git show` source. Scope: only `skills/default/delegate-to-subagents/evals/{scheduler_pilot.py,test_scheduler_pilot.py}`. Concurrent plan/preference bookkeeping and the independent Spec review were excluded.

### Documented violations: 0

The correction follows `brain/codebase/script-testing.md` (real underlying operations inside invented provider envelopes, public CLI boundary, individual claim assertions), `brain/codebase/testing.md` (preserved failures and distinct evidence levels), and `skills/default/create-skill/references/validation.md` (positive/negative public CLI cases and inspection of grading fields).

`scheduler_pilot.py:566` adds a focused predicate requiring the intended B/time151/ETA250 invocation, exact extension-policy diagnostic, consumed-extension prestate, and unchanged state. It reuses the existing operation/state helpers. `test_scheduler_pilot.py:156` exercises seven argument cases across both providers and frozen v2/v3 variants through public prepare/grade, preserving valid setup, output-contract and comparison eligibility checks. No new dependency, secret, global configuration mutation, or unrelated runtime change appears.

### Advisory smells: 0 new findings

Fowler heuristics considered, not treated as automatic violations: Mysterious Name, Duplicated Code, Feature Envy, Data Clumps, Primitive Obsession, Repeated Switches, Shotgun Surgery, Divergent Change, Speculative Generality, Message Chains, Middle Man, and Refused Bequest. The small domain predicate and explicit test table are appropriate here. Existing surrounding repeated predicates are outside this diff; the prior nonblocking advisory is not a new blocker.

### Evidence and limits

Read retained `T2-R3-F1` public reproduction, red result, post-fix probe, and final test result/stderr. Red: 24 failing negatives among 28 subcases. Post-fix: all four missing-ETA cells fail `single_extension` with valid setup. Final maintained CLI suite: 25 tests passed in 100.281 seconds, exit 0. No broad suite rerun, live provider calls, source edits, or functional failure claims were made by this review.

This is approval for the scoped standards correction only. Offline envelopes do not establish native Codex enforcement or isolated Copilot authentication; those remain unverified. Historical EPERM remains unexplained. Counts: 0 required findings, 0 new advisory findings.

## Spec

Findings: **0**. No missing/partial requirement, incorrect implementation, or scope expansion found in the pinned correction `28cbfcde64682936271ee2889ea5b378908a62ae...4bcafb705195d9a9e21bbfa57bc5ea117f6c2820` (new cycle, pass 1).

The pinned ExecPlan, T2-R3-F1, requires: "A valid second extension request must contain the intended B identifier, time 151 and valid ETA 250, reach the scheduler's one-extension rejection, and leave state unchanged. Exit 2 alone is insufficient." `scheduler_pilot.py:566-582` now requires the actual immutable invocation to be `extend B` at 151 with exactly the required now/ETA option pairs, ETA numerically 250, exit 2, the scheduler policy diagnostic, empty stdout, unchanged state, and active/extended B with deadline 200 and its extension already used. These conditions distinguish the intended policy rejection from parser errors and unrelated scheduler rejection. `single_extension` consumes this predicate at line 588.

The same contract says: "Reject missing/invalid ETA, other malformed argv and unrelated rejection reasons" and "Cover all four provider/version cells and assert the individual claim plus aggregate behavior." `test_scheduler_pilot.py:156-175` executes seven actual-child cases per Codex/Copilot and v2/v3 combination, covering the valid positive, missing/invalid/nonfinite/expired ETA, unexpected argument and duplicate ETA. It checks individual and aggregate outcomes, valid setup, output contract, and comparison eligibility. Retained `regression-red.*` records 24 expected failures among 28 subcases before correction; `final-pilot-tests.*` records 25 passing tests in 100.281 seconds. Prior chronology, current-parent binding, smoke, confinement and cleanup tests remain intact.

Retained `public-reproduction.py/.txt` and `malformed-second-extension.json` show four original false passes with real missing-ETA argparse exits. `post-fix-missing-eta.json` and `post-fix-probe.txt` show four individual/aggregate failures while setup stays valid and comparison eligible. The post-fix JSON retains a stale pre-fix `target` label; its results are corroboration, while pinned source and maintained regression establish the reviewed implementation.

Only the grader and its test changed. Limits: read-only pinned source/evidence inspection; no independent rerun or new probe, model call, trust/auth change, or source edit. Native Codex enforcement and isolated Copilot authentication remain separate owner prerequisites. Historical EPERM cause remains unknown.

## Result and retained evidence

Standards: zero required findings and zero new advisories. Spec: zero findings. The semantic correction is accepted for offline use; native provider readiness remains unverified. The earlier duplication advisory is outside this correction. The stale target label in one post-fix probe is retained as an explicit provenance limit, not silently rewritten.

[Pre-fix public proof](/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T2-R3-F1/public-reproduction.txt), [regression red output](/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T2-R3-F1/regression-red.txt), [final suite result](/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T2-R3-F1/final-pilot-tests.result.json), [final suite output](/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T2-R3-F1/final-pilot-tests.stderr.txt), [post-fix probe](/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T2-R3-F1/post-fix-missing-eta.json). Current next steps and owner boundaries remain in [ExecPlan](ExecPlan.md).
