# Qualification review pass 3 and bounded EOF correction

Original review target `ab51884db265331f7522dd055290fe7afebf35cb`, base and merge-base `df54c117e8b8bccc46420d87ae6e3671c6c14ae1`, previous target `c76587dee707b4674b9012514d3174ea864ea43b`.

Standards approves with zero findings. Spec requests changes with one Important / P2 EOF finding. These original verdicts remain intact. Correction `2470dac6f5ed0fb17577bf5e9155e5a292e44a28` is integrated, and limited independent closure verification of that exact finding is complete and resolved. The correction completes the fix portion of the third review-and-fix iteration. No fourth broad review is planned. Native qualification, owner prerequisites and T4/T5 remain incomplete.

Source diff SHA-256 `813987e6325157d5dba3eda03b0748cd1e8643f95ee63c1555659af0962bf0fe`. Incremental source diff SHA-256 `c4e835af9050c8aced8b26cf1daa2dde405b1ed6af3d882f2a5f95e4f51ec9f2`. Full diff SHA-256 `b667d3a09a0c2c8502446f3eab2db09fa1e67e030f1ba01e01d8f14531d8a92c`.

The original failure discards unterminated pending bytes at stdout EOF after a valid final reply, producing false setup readiness. Integrated R3 rejects nonempty pending bytes through the existing sanitized discovery failure. Retained final-source verification reports 38 tests passing in 142.471 seconds, with parent native metadata checks using identical harness SHA-256 `3f57143af2dfa8faf4507910e249a4d99f021486579945c4f69c43734f6439bd`. These establish no native-qualified execution. Original reviewer bodies follow with heading levels adjusted. `<E>` in the Spec command means the external review directory linked below.

## Retained inputs and originals

- [Frozen metadata](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-qualification-r3/review-input.json)
- [Source diff](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-qualification-r3/source.diff)
- [Incremental source diff](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-qualification-r3/incremental-source.diff)
- [Original Standards report](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-qualification-r3/standards.md)
- [Original Spec report](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-qualification-r3/spec-review.md)
- [Original public CLI reproducer](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-qualification-r3/spec-truncated-repro.py)
- [Original public CLI result](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-qualification-r3/spec-truncated-repro.json)
- [Original command receipt](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-qualification-r3/spec-truncated-command.json)
- [Original focused checks](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-qualification-r3/spec-focused-checks.json)
- [Correction outcome](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-Q1-R3/outcome.md)
- [Correction final source hashes](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-Q1-R3/source-hashes.json)
- [Correction full suite](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-Q1-R3/full-suite.txt)
- [Correction tested source identity](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-Q1-R3/tested-source.json)
- [Correction native source receipt](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-Q1-R3/native-check/source-receipt.json)

## Standards

### Verdict and source boundary

APPROVE for the Standards axis. Zero Critical issues, zero Important issues and zero actionable heuristic advisories meet the confidence threshold.

Reviewed fixed range `df54c117e8b8bccc46420d87ae6e3671c6c14ae1...ab51884db265331f7522dd055290fe7afebf35cb`. Merge-base equals the base. Target and inspected HEAD matched `ab51884db265331f7522dd055290fe7afebf35cb`. All three scoped source hashes and seven supplied artifact hashes matched `review-input.json`.

Carry forward the unchanged-source Standards assessment from `c76587dee707b4674b9012514d3174ea864ea43b`. Independently reviewed the incremental source diff, current contract, exact commit log and relevant surrounding code. Owning README bytes remain identical.

### Per-file assessment

- `scheduler_pilot.py`, DiscoveryError, discovery exchange/trailing-read and preflight hunks. No confirmed documented breach. Notification observations retain allowlisted method/status or warning classification/field presence. Arbitrary warning text stays outside retained evidence. Exact integer reply correlation, cumulative receive bound, original deadline and process-group cleanup remain explicit. This follows `brain/codebase/scripts-and-installers.md` rules for predictable malformed input, EOF, cancellation and machine-readable CLI behavior.
- `test_scheduler_pilot.py`, startup fixture and three public-CLI tests. No documented breach. Covers supported disabled notices, warning sanitization, malformed/unknown/active notices, mismatched/duplicate replies, timeout descendants and interruption. Individual readiness flags and cleanup are asserted before teardown, following `brain/codebase/script-testing.md`, “Fixtures that must remain meaningful.”
- `evals/README.md`. Unchanged. Previous Standards assessment applies.

The supplied heuristic smell baseline produced no actionable advisory. The exception carries sanitized evidence across the existing discovery boundary and has actual callers.

### Verification and limits

Tests reviewed before assessing implementation. Final retained evidence reports 37 tests passing in 144.030 seconds against harness SHA-256 `792f97ed9d1a4b85ba58028fe7675d6f92195a65c126c822ded257f84c6fea4c`. Parent no-inference source receipt identifies identical before/after bytes and zero model calls. Those results were inspected, without rerunning the suite or native checks.

Two additional bounded offline public-preflight probes supplied trailing unterminated JSON through the fake provider. Both returned setup-invalid exit 2. One reported truncated trailing notification, the immediate-exit variation reported OSError. Neither established false readiness. Review claims otherwise remain static.

Git/hash checks exited 0. No source changes, aggregate execution, model calls or authentication/trust changes occurred. Native qualification remains unsupported. Applicable standards remain repository AGENTS.md, the three supplied brain standards, owning README and previously activated review/brain/create-skill guidance.

## Spec

Verdict REQUEST CHANGES

Reviewed `df54c117e8b8bccc46420d87ae6e3671c6c14ae1...ab51884db265331f7522dd055290fe7afebf35cb`, merge-base equal to base. All three scoped source hashes match `review-input.json`. Carry forward the unchanged-source assessment from accepted pass-2 target `c76587dee707b4674b9012514d3174ea864ea43b`. This pass independently inspected the entire incremental source diff against frozen current `spec.md`.

### Implemented wrongly

- Important / P2, confidence 100. `skills/default/delegate-to-subagents/evals/scheduler_pilot.py:333` drops pending trailing bytes when stdout reaches EOF. Current T4-Q1-R2 requires “Reject active/unknown/malformed remote status, unknown notifications, mismatched/duplicate replies and RPC errors.” A valid final config/read reply followed by an active `remoteControl/status/changed` row without its terminating newline is buffered, then silently discarded by the EOF branch. Public preflight returns exit 0, `setup_ready=true`, `smoke_ready=true`, `prerequisites=[]` for this malformed/active input. The no-data branch checks `pending`, but the EOF branch omits the same check. Raise a sanitized truncated-notification failure when EOF arrives with pending bytes. Preserve existing byte/deadline limits and cleanup. Add a public-CLI EOF-with-pending negative.

Current reproduction command is `rtk proxy python3 <E>/spec-truncated-repro.py`. The driver prepares a pinned offline fake-Codex executable, emits the final reply plus unterminated active row, then closes stdout while staying alive briefly for bounded cleanup. Driver exits 0 and reports `{"exit":0,"setup_ready":true,"prerequisites":[]}`. Exact public argv/environment/exit/receipt are in `spec-truncated-repro.json`. Driver command/status/output are in `spec-truncated-command.json`. No native provider was invoked.

### Missing or partial requirements

No additional findings.

### Unasked behavior

No findings.

### Verification and limits

Tests reviewed first. Three maintained notification/correlation/warning/timeout/interruption tests passed in 10.148 seconds, retained in `spec-focused-checks.json`. Sanitized warning retention and unchanged request deadlines are implemented. Retained worker evidence records all 37 tests passing against the final harness hash. Parent native-check evidence uses identical bytes. This review ran focused offline checks only. No full suite, native/model calls, authentication/trust changes, source edits or other-axis report inspection occurred. Native execution qualification remains unsupported. Review cap reached, finding retained for owner decision.

## Limited EOF finding closure

The independent reviewer marked only the reported EOF finding RESOLVED at correction `2470dac6f5ed0fb17577bf5e9155e5a292e44a28`. The original third broad review above remains Standards zero / Spec one P2 REQUEST CHANGES. This closure completes that review-and-fix iteration and is no fourth broad review. The original counterexample now yields public preflight exit 2 with the sanitized truncated-notification error and all three readiness flags false. Two independent focused tests passed in 0.960 seconds, preserving the supported disabled-notification positive and asserting both fake-server PIDs absent before teardown. Source correction is accepted with the retained 38-test final-source result and this bounded closure. Native qualification and model approval remain incomplete.

- [Independent closure report](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-qualification-r3/closure.md)
- [Independent focused checks](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-qualification-r3/closure-focused.json)
- [Corrected counterexample](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-qualification-r3/closure-counterexample.json)
- [Current prepared payload and owner action](pilot-setup-review.md)
