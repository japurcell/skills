# Review 2: scheduler pilot contract

## Pinned scope and commands

Both independent axes reviewed base `5db7440017e081b4d391c92f28d325b2fccf95a0` through target `12daf57d7a8705a205c3d87610c7dbcef365c9fe`; merge base equals base. Captured diff SHA-256: `2041590c92e58537fe73978f008755d7d9b32930d1d611188e79200cbf7535d7`. Exact pins and commands are in [source.json](/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-2/source.json).

```text
git diff 5db7440017e081b4d391c92f28d325b2fccf95a0...12daf57d7a8705a205c3d87610c7dbcef365c9fe
git log 5db7440017e081b4d391c92f28d325b2fccf95a0..12daf57d7a8705a205c3d87610c7dbcef365c9fe --oneline
rtk proxy python3 /tmp/scheduler-standards-r2/evals/test_scheduler_pilot.py
rtk proxy python3 /tmp/scheduler-standards-r2/scripts/test_scheduler.py
rtk proxy python3 /var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-2/spec-repro.py
```

Captured source status was clean. Standards review found zero new actionable breaches; extracted-source suites passed 20 pilot tests and 14 scheduler tests. Spec reproductions exited 0 using offline fake-provider envelopes. No provider inference or repo changes occurred. Full axes are retained in [standards.md](/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-2/standards.md) and [spec.md](/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-2/spec.md).

## Standards review

**Findings: 0 new actionable Standards breaches; no baseline smells worth reporting.** R1 corrections were verified statically: explicit frozen provider environment/private settings and recursive grants; process-group cleanup after leader/pipe exit; exact helper/native receipts, state continuity, and malformed-assignment rejection. Frozen v2 fixture bytes match the pinned base and documented SHA. Native policy loading/trust/failure behavior/tool coverage remain blocked; offline tests do not establish them. Historical EPERM remains unexplained by this pass.

Reproduced verification on macOS 27.2.1 arm64, Python 3.14.6: `rtk proxy python3 /tmp/scheduler-standards-r2/evals/test_scheduler_pilot.py` passed 20 tests; `rtk proxy python3 /tmp/scheduler-standards-r2/scripts/test_scheduler.py` passed 14 tests. No aggregate execution, inference, or global trust changes occurred.

## Spec review

Pinned source symbols: H = `skills/default/delegate-to-subagents/evals/scheduler_pilot.py`; S = `brain/plans/31-scheduler-reliability/ExecPlan.md`.

1. **P1 - Independent progress can occur entirely after shutdown** (H:496-529). S:7 requires independent assignments to progress while shutdown remains unconfirmed; R1.6 binds actions to timestamps/results. The grader trusts supplied `--now` values without native ordering or B's shutdown state during C operations. Reproduction registers C only after B `confirm-stopped`, then backdates C tick/checkpoint/completion to 100/102/104; continuous real child receipts still grade `valid/pass` with `independent_progress=true`. Require C operations while B remains unconfirmed and validate chronology. Evidence: [grade](/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-2/late-independent-grade.json), [native events](/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-2/late-independent-native.jsonl).

2. **P1 - A detached parent artifact can hide the acknowledged record's owner** (H:476-477,519,531-536). S:74 requires reading the updated owner and receipt before reporting reassignment complete. The grader reads arbitrary `final_state.parent_record` but checks acknowledgment evidence against hardcoded `outputs/ownership.json` without binding those records. A real passing scenario still grades `valid/pass` when a new-owner snapshot is retained elsewhere, actual output is restored to agent-old, and the detached snapshot is referenced. Resolve the receipt pointer to the actual final parent artifact and require consistent native readback. Evidence: [grade](/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-2/detached-parent-grade.json), [result](/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-2/detached-parent-result.json), [actual parent](/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-2/detached-parent-actual.json), [native events](/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-2/detached-parent-native.jsonl).

3. **P2 - Smoke does not enforce its frozen state path** (H:347-349). S:92 requires the neutral register/complete fixture to use a separate frozen smoke state. `operation()` checks only command/assignment; real children using `outputs/scenario-state.json` instead of `outputs/smoke-state.json` still yield valid setup. Require exact smoke argv/state. Evidence: [grade](/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-2/wrong-smoke-state-grade.json), [native events](/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-2/wrong-smoke-state-native.jsonl).

All three reproduced against extracted pinned source. Full public argv, exit codes and stdout are in [spec-repro-commands.json](/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-2/spec-repro-commands.json); driver: [spec-repro.py](/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-2/spec-repro.py). C1 native enforcement remains unproven. The prior EPERM cause and pending T4/T5 are not additional review findings.

## T4 draft: superseded, not approved

The [payload review](/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-draft/payload-review.md) was prepared against `12daf57d7a8705a205c3d87610c7dbcef365c9fe`; review 2 supersedes that source. The draft is not final or approved. Codex preflight is blocked on private hook trust/load/failure/tool coverage; Copilot preflight is blocked because an isolated-home auth token is unavailable. [The model-call ledger](/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-draft/model-call-ledger.json) records zero total, smoke, and scored attempts. It authorizes no calls and establishes no live readiness. Any later payload must be prepared and reviewed against the post-R2 source with fresh hashes.
