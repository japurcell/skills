# Focused harness review 1

Reviewed uncommitted snapshot rooted at base/target HEAD/merge base `35c31ab9782c293a8777b2145892c31b8aa0c6ae`. This is an implementation checkpoint, with source acceptance pending. Standards has one P2 coverage finding. Spec has one P1 canonical-state finding and one P2 telemetry finding. Counts remain separate, Standards 1 and Spec 2.

[Snapshot metadata](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-focused-1/source.json), [captured diff](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-focused-1/diff.patch) and [commit log](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-focused-1/commits.txt). Diff SHA-256 `73565492abfe6d6a5ca3586d0485b68941d91d94b3fbcba6cf98d46845e53dfd`. All five listed source hashes were verified against captured bytes. Current worker changes can advance independently and are not represented by this immutable review.

## Standards

Reviewed immutable `review-focused-1/snapshot`, identified by `source.json`. Base, target HEAD and merge base are `35c31ab9782c293a8777b2145892c31b8aa0c6ae`, with no intervening commits. Captured command is `git diff 35c31ab9782c293a8777b2145892c31b8aa0c6ae --`. Diff SHA-256 is `73565492abfe6d6a5ca3586d0485b68941d91d94b3fbcba6cf98d46845e53dfd`. Relevant untracked fixture bytes are included in the snapshot and source hashes.

### One documented-standard finding

- **P2 - Restore retained Copilot status cancellation coverage.** `skills/default/delegate-to-subagents/evals/test_scheduler_pilot.py`, deleted `test_public_native_status_interruption_and_repo_layer_rejection` hunk, removes `process.send_signal(signal.SIGINT)`, the exit-130 assertion and the status-child disappearance assertion together with obsolete repo-layer checks. The actual `copilot_status()` subprocess path remains in preflight and run. The only surviving SIGINT test exercises `invoke_scheduler.py`, while the retained status failure test covers timeout. Preserve the existing cancellation half as a standalone test and retire the repo-layer half. This follows `brain/codebase/testing.md` (preserve failing cases and surviving tests), `skills/default/create-skill/references/validation.md` (keep coverage for behavior still promised), and current F1 acceptance (keep CLI boundary/exit/cleanup checks). The test-disposition inventory incorrectly classifies this entire mixed test as obsolete. This is a static coverage finding, with no claimed observed cancellation failure.

No material baseline-smell findings. No native calls or test suites were run in this review. The independently running maintained suite result is outside this report.

[Original Standards report](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-focused-1/standards.md).

## Spec

Reviewed immutable `review-focused-1/snapshot` and captured `git diff 35c31ab9782c293a8777b2145892c31b8aa0c6ae --`. Base, target and merge base are `35c31ab9782c293a8777b2145892c31b8aa0c6ae`, with no intervening commits. The active focused ExecPlan supplied the contract.

- **P1 - Canonical scenario state can be hidden behind a detached copy.** `skills/default/delegate-to-subagents/evals/scheduler_pilot.py:930` reads the agent-selected `final_state.scheduler_state`, and line 944 compares that artifact with the final receipt. It never independently reads the fixed `outputs/scenario-state.json` used by every helper command. A session can retain a matching copied state, point its result at that copy and alter the actual scheduler state after the last helper call. The output/state checks can still pass. The parent ownership check already binds its artifact to the actual target, but scheduler state lacks the equivalent binding. Active F1 requires “Compromised source, state or results remain invalid” and “a consistent independent before/after state chain with output readbacks.” This is a static inference, without a full-session reproduction.

- **P2 - Unknown telemetry still imposes a schema gate.** `skills/default/delegate-to-subagents/evals/scheduler_pilot.py:445` requires every event to have object-valued `data` before determining whether it supplies authoritative evidence. An unknown `{"type":"future.telemetry","data":[]}` produces `malformed-native-line:1` and is excluded from normalized raw observations. `validate_phase` propagates that reason into phase invalidity at line 742. Active F1 says “Unknown non-authoritative telemetry is retained as raw evidence without automatic invalidity.” A direct offline invocation of `native_events` against the immutable snapshot reproduced this result with exit 0 using `rtk proxy python3 -B -c`, importing the captured module and passing that JSON event. No provider process or maintained suite was executed.

No additional unrequested scope found. Native qualification remains an F3 obligation.

[Original Spec report](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-focused-1/spec.md).

## Verification chronology and disposition

The first frozen full suite ran 36 tests in 136.981 seconds with 35 passing and one failing. The helper cleanup success subcase returned 2 with `[Errno 1] Operation not permitted`. The isolated same-byte cleanup check passed one test in 1.123 seconds. The isolated pass does not establish a full-suite pass or the cause of the earlier failure. [Full-suite log](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-focused-harness/pre-review-full-suite.log), [isolated check](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-focused-harness/f1-cleanup-check.log) and [pre-review source hashes](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-focused-harness/pre-review-hashes.json).

The [test-disposition inventory](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-focused-harness/test-disposition.json) is a current mutable worker bookkeeping artifact. It now reports 37 tests and restores the cancellation half of the mixed test. That later inventory does not change this review's captured coverage finding or establish accepted correction. All three findings are assigned to the serialized source worker under [F2 correction tasks](ExecPlan.md#f2-correction-tasks-from-focused-review-1). No source acceptance or native qualification is claimed.
