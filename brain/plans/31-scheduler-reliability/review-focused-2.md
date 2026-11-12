# Focused harness review 2

Base/merge base `35c31ab9782c293a8777b2145892c31b8aa0c6ae`, target HEAD `5cf7d65cab25c4c3cdda801529fa64bc6f49f5e0` plus the captured uncommitted source snapshot. Standards reports zero remaining findings. Spec reports zero remaining findings. All three review-1 findings are resolved in the reviewed source. Final suite, committed-byte verification and integration are now complete, recorded separately below.

[Review metadata](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-focused-2/source.json), [captured diff](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-focused-2/diff.patch) and [commit log](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-focused-2/commits.txt). Diff SHA-256 `160b516bafdd5e8f12698293469befd0e08b6f731498d1b1a6e9522584593a96`. All five listed source hashes match snapshot bytes.

## Standards

Reviewed immutable `review-focused-2/snapshot`, its captured `diff.patch` and `commits.txt`. Base and merge base are `35c31ab9782c293a8777b2145892c31b8aa0c6ae`. Target HEAD is `5cf7d65cab25c4c3cdda801529fa64bc6f49f5e0`, plus captured uncommitted source. The sole intervening commit records the first review and correction tasks. Full included-file identities are in `source.json`.

Verified SHA-256 identities directly against captured bytes.

- Diff `160b516bafdd5e8f12698293469befd0e08b6f731498d1b1a6e9522584593a96`.
- Harness `1118f95cdbb2743c05b57ff809ac85e93464800467b9796d7bdaa79adf88f3c9`.
- Tests `9fc26f174275c087f0aa591067e6d90a73da5e1e59c121f105ad379a95d2f4f0`.

**Prior P2 resolved in source.** `skills/default/delegate-to-subagents/evals/test_scheduler_pilot.py:594`, `test_public_native_status_interruption_reaps_descendant`, restores the public Copilot preflight subprocess, SIGINT delivery, bounded `communicate(timeout=5)`, exit-130 assertion and status-child disappearance assertion. This preserves the surviving cancellation contract while obsolete repo-layer checks are retired. It satisfies the retained-coverage rules in `brain/codebase/testing.md`, `skills/default/create-skill/references/validation.md` and F1's CLI cleanup acceptance.

Reviewed the correction delta and resulting full captured change. Zero remaining material documented-standard violations and zero material baseline-smell findings. The approved conformance-feature deletions remain within the current contract.

This is independent static source acceptance. No native calls or test suites were run in this review. Final maintained-suite execution and its result remain separately owned evidence.

[Original Standards report](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-focused-2/standards.md).

## Spec

Reviewed immutable `review-focused-2/snapshot`, the captured full change and active focused ExecPlan. Base/merge base are `35c31ab9782c293a8777b2145892c31b8aa0c6ae`. Target is `5cf7d65cab25c4c3cdda801529fa64bc6f49f5e0` plus captured uncommitted source. Harness SHA-256 is `1118f95cdbb2743c05b57ff809ac85e93464800467b9796d7bdaa79adf88f3c9`, tests SHA-256 is `9fc26f174275c087f0aa591067e6d90a73da5e1e59c121f105ad379a95d2f4f0`.

**Both previous findings are resolved.**

- Canonical scheduler-state binding now satisfies F1 requiring “Compromised source, state or results remain invalid.” Shared `validate_phase` at `skills/default/delegate-to-subagents/evals/scheduler_pilot.py:777` independently reads the fixed state target, binds the result reference to it, verifies every scheduler receipt uses it, checks the continuous before/after chain and compares actual final state with the final receipt. The semantic grader independently enforces the same target binding at line 950. Source inspection supports resolution. Retained `review-state-red.log` demonstrates the prior public-CLI acceptance defect and `review-state-green.log` records three passing correction checks. Those logs are supplied evidence, not reruns by this reviewer.

- Unknown non-object telemetry now satisfies F1 requiring “Unknown non-authoritative telemetry is retained as raw evidence without automatic invalidity.” At line 446, object-shape validation applies to required identity/execution events. Unknown events retain their raw structured data. A direct offline parser check against this exact snapshot passed `future.telemetry` with array-valued data for both providers. Both results preserved the event in `normalized` and returned an empty `invalid_reasons` list, command exit 0.

The full focused change preserves the six-session allocation, immutable execution inputs, identity requirements, real helper receipts, seven common assertions and candidate acknowledgment, ordinary native controls, optional usage, and CLI boundaries. No material new missing requirement, incorrect implementation or unrequested scope found.

The maintained suite is being verified separately. This review executed no suite or provider process. F3 native permission acceptance remains pending.

[Original Spec report](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-focused-2/spec.md).

## Subsequent final-byte verification and integration

Source `b0eae21c26605a4edc7d9ee64524658c9f061196` is committed and integrated by fast-forward into `scheduler-reliability`. All five source hashes match the reviewed snapshot, `final-hashes.json`, committed bytes and root files. The unchanged final suite passed 38 tests in 142.819 seconds, exit 0, with scoped process permissions. [Final suite log](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-focused-harness/final-suite.log), [acceptance receipt](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-focused-harness/acceptance.json), [exact hashes](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-focused-harness/final-hashes.json) and [worker outcome](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-focused-harness/outcome.md).

Preserve the separate chronology. The first sandbox suite ran 36 tests with one helper cleanup EPERM failure in 136.981 seconds. An isolated same-byte check passed in 1.123 seconds. A later 37-test diagnostic run failed caller-source drift while canonical-state code was being edited. The final frozen sandbox run had 37/38 passing with the unchanged helper cleanup EPERM. The same-byte isolated elevated cleanup passed in 1.089 seconds, followed by the successful full final scoped-permission run. Helper source and cleanup assertions remained unchanged. No suite was rerun by the integration coordinator. [Initial suite](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-focused-harness/pre-review-full-suite.log), [initial isolated check](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-focused-harness/f1-cleanup-check.log), [editing-time diagnostic](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-focused-harness/review1-diagnostic-suite.log), [final sandbox suite](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-focused-harness/final-sandbox-suite.log) and [isolated elevated check](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-focused-harness/escalated-cleanup.log).

The original independent reports retain their static review and separate-suite limits. The final receipt establishes offline source acceptance. Native permission acceptance and behavioral results remain F3/F4. [Review 1](review-focused-1.md) stays historical, with its three findings resolved through the accepted correction.
