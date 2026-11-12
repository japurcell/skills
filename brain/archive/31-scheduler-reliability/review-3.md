# Independent source review 3

## Review boundary and evidence

- Base: `5db7440017e081b4d391c92f28d325b2fccf95a0`.
- Integrated target: `7c9080080dd6fd7639b0a925a10d9caea5e4e413`.
- Captured diff SHA-256: `3e0cddb22529d4c06bf0538306ea387f832a6c88d175117120472488be3319aa`.
- Commands: `git diff 5db7440017e081b4d391c92f28d325b2fccf95a0...7c9080080dd6fd7639b0a925a10d9caea5e4e413` and `git log 5db7440017e081b4d391c92f28d325b2fccf95a0..7c9080080dd6fd7639b0a925a10d9caea5e4e413 --oneline`.
- Captured pins and exclusions: [source.json](/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-3/source.json), [commit inventory](/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-3/commits.txt), and [pinned diff](/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-3/diff.patch).
- The review excludes unrelated router-plan commit `e96e3b3826f893abefc320338623a9428cc4e496` and `brain/plans/index.md`, `brain/plans/subagent-model-router-phase-1-exec-plan.md`, and `brain/plans/subagent-model-router-phase-2-exec-plan.md`. It also excludes subsequent coordinator-only plan bookkeeping. The worker commit is not the review boundary; review uses the integrated target above.
- This is the third and final allowed independent review pass. No fourth review is implied.

## Standards axis

Source: [Standards report](/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-3/standards.md).

- Documented-standard violations: **0**. No actionable violation was found in the reviewed source scope.
- Baseline heuristics: **1 advisory, 0 required**. `skills/default/delegate-to-subagents/evals/scheduler_pilot.py:574` repeats the shutdown-unconfirmed and confirmation-order predicates in both generators. A small shared predicate may improve readability. This is not a standards violation, demonstrated defect, blocker, or required change.
- Limits: no suites or model calls were rerun for this review. Offline subprocess evidence does not establish native loading, trust, delivery, permission enforcement, or real worker shutdown. Historical EPERM cause remains **UNKNOWN**. Native Codex remains closed; isolated Copilot authentication is unavailable.

## Spec axis

Source: [Spec report](/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-3/spec.md).

- Findings: **1**, severity P2; no additional missing/partial requirements or unasked behavior found.
- **Malformed second-extension request falsely passes the single-extension claim.** The grader accepts any real `extend B --now 151` exit 2 with unchanged state. Replacing the canonical second request's `--eta 250` with no `--eta` makes the immutable v2/v3 scheduler reject at argparse with `the following arguments are required: --eta`; nevertheless all four provider/version cells grade valid setup, behavior pass, `single_extension.passed=true`, and comparison eligible. This demonstrates malformed-input rejection, not enforcement of the one-extension policy.
- Required fix contract: tie the assertion to an otherwise valid second extension request, including its required `--eta` argument, and require the scheduler's policy rejection with unchanged state. Missing `--eta` and other malformed arguments must not count as proof of the single-extension limit. Preserve the actual child argv, exit, output, and before/after state as evidence.
- Reproduction command: `rtk proxy python3 /var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-3/second-extension-probe.py` (exit 0). Retained [transcript](/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-3/second-extension-probe.txt), [driver](/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-3/second-extension-probe.py), and [captured argv, exits, outputs, environment, and grades](/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-3/malformed-second-extension.json).
- Review limits: this was an independent reproduction against pinned source using public prepare/grade, real immutable helper/scheduler subprocesses, real parent readbacks, and both native-shaped adapters. No broad suite, source edit, inference, trust/auth change, or fourth review occurred. Native pilot gates remain separate.

## Result

R2.1 chronology, R2.2 current-parent/receipt binding, and R2.3 exact linked smoke checks are supported by retained focused verification. M2 remains **not met** because of the P2 second-extension finding, even though the three R2 fixes are integrated and the Standards axis has no documented violations. The one advisory is retained as advisory and does not add a blocker. Further source implementation is outside this cycle; the unresolved fix frontier and current T4/T5 gates are recorded in [ExecPlan](ExecPlan.md).
