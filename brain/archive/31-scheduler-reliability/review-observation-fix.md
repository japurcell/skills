# Final observation and permission correction acceptance

Final accepted source `94dc13e86187280425f88051fb082f88e896ee94`, harness SHA-256 `1ab8d15dabe5306050a86465eefb7c0a49b6b0fd6bf6dcbf9cec17dca42e3187`, tests SHA-256 `00ec6657b05a7a10193cd9f90aaa32d2f3d8795a4b5e162c49f1a24ae8b90703`. Both final independent axes report zero remaining material findings. These final parser bytes were verified offline and were never rerun on native P05. Frozen pilot execution remains source c52/harness2983 with original grades unchanged.

## Verification chronology

The earlier F2-E commit `ade005b8735cd72cd5da96c4fe2e067bd1d0e9ef`, harness8761dc45/tests dafc3386, passed 42 tests in151.453 seconds. Its initial Standards review had zero findings and Spec had one P2 incidental-permission gate finding. The narrow F2-E1 correction resolved that gate. Six targeted final-byte tests passed in13.487 seconds. No repeat full suite is attributed to the new hash. [Earlier suite/acceptance](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-observation-fix/acceptance.json), [earlier outcome](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-observation-fix/outcome.md), [initial Spec finding](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-observation-fix/final-review/spec.md), [final targeted log](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-observation-fix/denial-fix/final-targeted.log) and [final source/test metadata](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-observation-fix/denial-fix/review/metadata.json).

## Standards

Reviewed only the frozen denial-fix delta and relevant unchanged qualification context. Base, worker HEAD and merge base are `ea06e0f319aba19a06d31983d850ff6c52e6274f`, with no intervening commits. Captured command is `git diff ea06e0f319aba19a06d31983d850ff6c52e6274f`.

Verified exact SHA-256 identities against frozen bytes.

- Harness `1ab8d15dabe5306050a86465eefb7c0a49b6b0fd6bf6dcbf9cec17dca42e3187`.
- Tests `00ec6657b05a7a10193cd9f90aaa32d2f3d8795a4b5e162c49f1a24ae8b90703`.
- Diff `de8d5b42af246d299a2568947de8f7448263ea16656dc0f4b0cbb2310116fd38`.

Zero material documented-standard violations and zero material baseline-smell findings.

Incidental denial remains recorded through `permission_denial_observed`, while validated current-phase helper execution, state and rubric proof determine behavior and comparison status. Required-helper denial still produces invalid qualification and a permission-failure classification. The existing real-child scenario/replay test retains all prior assertions and adds incidental-denial observations for both variants. The actual-denied case now also checks scored-phase rejection and classification. This preserves the retained-behavior coverage rules supplied from `brain/codebase/testing.md` and evaluation validation guidance.

Inspected the retained final targeted log, six tests passed in13.487 seconds, and its matching source hash inventory. This is worker evidence. No tests or model/provider calls were run in this review. The earlier42-test full-suite result remains bound to the earlier8761dc45/dafc3386 source and does not establish a full-suite run for these final bytes. No source or original evidence was changed.

[Original Standards report](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-observation-fix/denial-fix/review/standards.md).

## Spec

Zero remaining findings in the bounded F2-E1 correction. The previous incidental-denial P2 is resolved.

Reviewed captured `git diff ea06e0f319aba19a06d31983d850ff6c52e6274f`. Base, worker HEAD and merge base are `ea06e0f319aba19a06d31983d850ff6c52e6274f`, with no intervening commits. Verified exact frozen SHA-256 hashes `1ab8d15dabe5306050a86465eefb7c0a49b6b0fd6bf6dcbf9cec17dca42e3187` for harness and `00ec6657b05a7a10193cd9f90aaa32d2f3d8795a4b5e162c49f1a24ae8b90703` for tests. Read F2-E1, the prior Spec finding and retained correction proof. Standards report was not read.

F2-E1 requires “A fully proven phase cannot fail solely because an unrelated help/redirection/Python inspection was denied.” At `skills/default/delegate-to-subagents/evals/scheduler_pilot.py:958`, the required-execution denial classification comes from authoritative current-phase validation. Line959 preserves incidental denial observation. Lines1119-1120 remove the aggregate denial override from behavioral pass and eligibility, while permission_failure uses the required-execution denial classification.

Required proof remains mandatory. The unchanged validator at lines822-839 requires real helper receipts, rejects duplicates and required-helper permission denial, and retains canonical-state validation. The final qualification override still makes missing/contradictory required execution not evaluated and ineligible. No identity, source, actual-exit, argv, state/readback, replay or rubric condition is weakened by this delta.

Updated public cases retain incidental denials alongside successful proven scenarios and separately retain required-helper-denial rejection. Retained final proof records six targeted tests passing in13.487 seconds on these final hashes. The prior42-test suite in151.453 seconds belongs to earlier8761/dafc bytes. This review does not attribute that broader suite to the new predicate.

No material new missing requirement, incorrect implementation or expanded scope found. No tests, model/provider calls, source edits or original native evidence changes were performed by this reviewer.

[Original Spec report](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-observation-fix/denial-fix/review/spec.md).

## Integration and preservation

Exact committed bytes, final targeted hashes and frozen review identities were verified before fast-forward integration. The helper remains unchanged. Original P05 raw/run/normalized/grade files and independently audited semantic assessments remain preserved. No grading API or new programmatic regrade is required. No model/provider call was made during source correction or closeout.
