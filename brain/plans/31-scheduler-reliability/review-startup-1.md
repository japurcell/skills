# Startup correction review 1

Source correction `3d5a2b5888adf77a49a000e80557bc655f19d8de` is integrated through worker tip `0f416340a39abe2398c86a7b50d94b6eed15e1ee`. The independent reviews used base/target/merge base `c5a430b389392afb7728822d3fc31cfa1b4f8a52` plus complete uncommitted snapshot SHA-256 `3441293ee8fb20606d56cb90acc707e250d15981c7072f3a68fa148d7f1cbd23`. The empty committed range describes the review capture, while the frozen three-file diff identifies the correction.

[Review metadata](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-startup-1/source.json), [reviewed diff](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-startup-1/diff.patch), [captured log](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-startup-1/log.txt). Diff SHA-256 `937b00a2ffe766521b65b3666d9ce10137e0afe9ffc5377949f5b05a5f94f59d`. All 21 snapshot file hashes were verified. All three committed source hashes equal the reviewed and final-suite hashes. Both axes report zero findings. This new-scope review leaves the original closed EOF cycle intact.

## Standards

Reviewed base, target, and merge base `c5a430b389392afb7728822d3fc31cfa1b4f8a52` plus the complete uncommitted snapshot `review-startup-1/source`, digest `3441293ee8fb20606d56cb90acc707e250d15981c7072f3a68fa148d7f1cbd23`. `source.json` records every included file and SHA-256. Independently checked all listed file hashes against the frozen bytes with Python 3, exit 0, zero mismatches.

Reviewed `diff.patch`, captured with `git diff --binary c5a430b389392afb7728822d3fc31cfa1b4f8a52`. The recorded `git log c5a430b389392afb7728822d3fc31cfa1b4f8a52..c5a430b389392afb7728822d3fc31cfa1b4f8a52 --oneline` is empty because this change is uncommitted.

Read all seven standards sources listed in `source.json`, including their testing, fixture-authority, safe-native-metadata, isolation, and evidence-limit requirements. Applied the supplied twelve-smell baseline as judgment guidance and reviewed each changed hunk with its surrounding code.

## Findings

Zero documented-standard breaches and zero actionable judgment smells.

- `skills/default/delegate-to-subagents/evals/scheduler_pilot.py` preserves strict discovery validation, compares the remaining stable projection, bounds diagnostic names, retains sanitized notification observations, and selects create-only native Copilot identity through the existing auth predicate.
- `skills/default/delegate-to-subagents/evals/test_scheduler_pilot.py` adds public CLI coverage using real frozen helper subprocesses, checks receipt immutability, rejects unsafe startup observations before inference, and verifies discovered process cleanup. The new fixture parser cases cover conflicts, malformed UUIDs, and reuse.
- `skills/default/delegate-to-subagents/evals/README.md` distinguishes parser compatibility, offline fixture evidence, and the uncertain historical failure cause.

Static review only. No provider calls or test reruns were performed. The focused four-test result was supplied by the parent. The full affected-suite receipt was pending when this report was written, so this report makes no full-suite success claim.

[Original Standards report](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-startup-1/standards.md).

## Spec

Reviewed base and target `c5a430b389392afb7728822d3fc31cfa1b4f8a52` plus the complete uncommitted snapshot `review-startup-1/source`, digest `3441293ee8fb20606d56cb90acc707e250d15981c7072f3a68fa148d7f1cbd23`. Verified all 21 files against `source.json`, exit 0 with zero hash mismatches. The committed range is empty. The three-file uncommitted diff supplies the reviewed changes.

No Spec findings. No missing or incorrectly implemented source requirement, or unrequested behavioral expansion, was identified in this bounded review.

The T4-STARTUP contract at `brain/plans/31-scheduler-reliability/ExecPlan.md` lines 22-28 maps to the changes as follows.

- Native Copilot selects create-only `--new-session-id`, preserving the phase UUID and ephemeral trust. The separate process-token flag remains. The fixture enforces conflicting options, UUID validation and reused-ID rejection, with the existing both-variant smoke/scenario path retained.
- Codex equality excludes validated notifications and preflight-only authentication. Stable bindings remain compared. Notifications enter sanitized phase receipts, and mismatch diagnostics use bounded known field names. Existing discovery validation, native login, receipt, replay and qualification gates remain in place.
- Added public lifecycle coverage varies valid account-event presence in both directions, relative order and immediate trailing delivery. Positive cases complete real-child smoke. Hook/config/inventory/features drift and unknown/malformed/active/warning events retain the before-inference rejection assertions and immutable preflight receipt checks.
- README retains uncertainty about the discarded original Codex delta and the limits of native parser acceptance.

Validation remains incomplete at this review checkpoint. Line 30 requires “one bounded affected suite on exact final combined bytes”. The parent reports the focused four-test pass and an exact-byte full suite still running. This review makes no full-suite pass claim. No suite, provider runtime or live call was run by this reviewer. Native qualification and replacement-payload approval remain subsequent parent-owned work.

[Original Spec report](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-startup-1/spec.md).

## Subsequent final-byte verification

The original reports retain their then-pending suite status. The separate completed [final suite receipt](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-startup-fix/final-suite.json) records 55 tests passing in 200.507 seconds, exit 0, with identical three-file hashes before and after. Its recovered read-only process inventory records zero remaining test/provider/helper processes. [Worker outcome](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-startup-fix/worker-outcome.json) binds the tested bytes to source commit and worker tip. No tests were rerun for integration.

The [final rendered parser binding](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-startup-fix/final-rendered-parser-binding.json) confirms each of the four final Copilot arrays equals its frozen array with only the proven flag substitution, preserving UUID and ephemeral folder trust. The binding reuses retained installed-parser evidence without a parser or runtime rerun. Original argv digest serialization was unestablished and was not compared. Parser acceptance and offline proof leave native startup, smoke qualification and a replacement live payload incomplete. Source correction is accepted. A fresh frozen payload needs review and explicit approval before replacement live calls.
