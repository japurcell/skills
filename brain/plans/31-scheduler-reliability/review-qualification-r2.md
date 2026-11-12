# Qualification review pass 2

Both independent axes approve with zero findings. Source acceptance for T4-Q1-R1 and T4-Q1-C is met. M2, native owner prerequisites and T4/T5 remain incomplete. No native-qualified execution has occurred.

Reviewed target `c76587dee707b4674b9012514d3174ea864ea43b`, base and merge-base `df54c117e8b8bccc46420d87ae6e3671c6c14ae1`, previous review target `294a741602fb08822fb3d604de67dd1a1ec56cc3` and R1 source `0f93342fffb4b66eeaad8a4d50b677df8064c8da`.

Source diff SHA-256 `21eb4f89676772479875a755ffc61807f39dae8aedbf2ff45dd744338fd088be`. Incremental source diff SHA-256 `a30c1a6ef211803201047823d8f795fdbdfcd229ce59156d7e78457aac0d07a8`. Full diff SHA-256 `ec55a74ff5e0d2f922e2c02a1bb40dcc37fb76b73fcf7fe6aef1094a6d2a7d21`.

Spec independently replayed the corrected counterexample with exits `[0, 0, 2, 0]` for both smokes, scenario and grade, resulting in invalid setup, unevaluated behavior and comparison ineligibility while preserving individual behavior assertions. It independently ran two focused tests in 7.367 seconds. The retained 34-test full suite covers the earlier traversal-only guard. Final grammar source verification comprises focused worker and independent Spec checks. The original pass-1 report remains [historical evidence](review-qualification.md).

Both reviewer bodies follow with heading levels adjusted. In the Spec command, `<E>` means the external review directory linked below.

## Retained inputs and originals

- [Review metadata](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-qualification-r2/review-input.json)
- [Scoped source diff](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-qualification-r2/source.diff)
- [Incremental source diff](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-qualification-r2/incremental-source.diff)
- [Full diff](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-qualification-r2/full.diff)
- [Frozen specification](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-qualification-r2/spec.md)
- [Standards original](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-qualification-r2/standards.md)
- [Spec original](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-qualification-r2/spec-review.md)
- [Independent focused checks](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-qualification-r2/spec-focused-checks.json)
- [Corrected reproduction driver](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-qualification-r2/spec-traversal-repro.py)
- [Corrected reproduction output](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-qualification-r2/spec-traversal-repro.json)
- [Corrected command receipt](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-qualification-r2/spec-traversal-command.json)
- [Corrected native-shaped records](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-qualification-r2/spec-traversal-native.jsonl)

## Standards

### Verdict and source boundary

APPROVE for the Standards axis. Zero Critical issues, zero Important issues, zero actionable heuristic advisories.

The fixed range is `df54c117e8b8bccc46420d87ae6e3671c6c14ae1...c76587dee707b4674b9012514d3174ea864ea43b`. The merge-base equals the base. Target and inspected HEAD matched `c76587dee707b4674b9012514d3174ea864ea43b`. All three scoped source hashes and all seven supplied artifact hashes matched `review-input.json`.

Carry forward the unchanged-source Standards assessment from `294a741602fb08822fb3d604de67dd1a1ec56cc3`. Independently reviewed the incremental source diff, exact commit log, frozen current contract and adjacent validation code. The owning README is byte-identical to the prior review.

### Per-file assessment

- `scheduler_pilot.py`, lines 696-701. No documented-standard breach. The new `target_text.startswith("outputs/")` and `".." in target.parts` checks precede existing physical confinement, native fileEdits matching and current-content checks. Errors continue through the established invalid-evidence channel. This follows predictable malformed-input handling in `brain/codebase/scripts-and-installers.md`.
- `test_scheduler_pilot.py`, fixture changes and new lexical-negative regression. No documented-standard breach. All three cases use the public CLI, execute underlying helpers and filesystem operations, require valid prerequisite smokes, and assert individual rubric observations after invalid qualification. This follows `brain/codebase/script-testing.md`, “Fixtures that must remain meaningful,” and `brain/codebase/testing.md`, preserving meaningful failure evidence.
- `evals/README.md`. Unchanged. Prior Standards assessment applies.

The supplied smell baseline produced no actionable finding. The small lexical check stays in the existing native-patch validation boundary. No new abstraction or duplicated production responsibility is introduced.

### Verification and limits

Static review, with tests read before evaluating the implementation. No failures are claimed as independently reproduced. Retained `green-final-grammar.txt` reports two final-source tests passing in 7.049 seconds, covering three lexical negatives and both-variant supported positive scenarios. The 34-test run in 129.631 seconds covered the earlier traversal-only guard, SHA-256 `ee7fd61943d92308b53b433eca26b1468b036514fd89bf4aee369bfdc52ccd3e`. Final-source full-suite execution remains unverified.

Hash and Git identity checks exited 0 with matches. No tests, builds, aggregate checks or native/model calls were rerun. No source edits were made. Sources remain repository AGENTS.md, the three supplied brain standards, owning eval README and previously activated review/brain/create-skill guidance.

## Spec

Verdict APPROVE

Reviewed exact scope `df54c117e8b8bccc46420d87ae6e3671c6c14ae1...c76587dee707b4674b9012514d3174ea864ea43b`, merge-base equal to base. All three source hashes match `review-input.json`. This follow-up carries forward the prior unchanged-source assessment at `294a741602fb08822fb3d604de67dd1a1ec56cc3` and independently reviews the complete incremental source diff against frozen `spec.md`.

### Missing or partial requirements

Zero findings.

### Unasked behavior

Zero findings.

### Implemented wrongly

Zero findings. The previous P2 is resolved at `scheduler_pilot.py:696`. Current T4-Q1-B requires “Reject extra targets, traversal, linked paths, unsupported headers, updates, deletes and moves.” The correction checks the relative `outputs/` prefix and rejects `..` components before physical confinement, completion-path and current-content verification. Existing semantic per-claim guards remain intact.

### Verification

Tests reviewed before correction source. Replayed the prior public-CLI counterexample on the pinned current source using real helper/scheduler children and the supported offline Copilot transport. Exact command is `rtk proxy python3 <E>/spec-traversal-repro.py`. Both smokes exit 0, scenario exits 2, and public grade exits 0 with `setup_status=invalid`, `behavior_status=not_evaluated`, `comparison_eligible=false` and a lexical-target invalid reason. Every original individual behavior assertion remains true.

Also ran `rtk proxy python3 skills/default/delegate-to-subagents/evals/test_scheduler_pilot.py PilotTests.test_public_copilot_patch_lexical_traversal_invalidates_qualification PilotTests.test_public_copilot_both_smokes_replay_bindings_and_raw_regrading`. Exit 0, two tests passed in 7.367 seconds. This covers traversal, absolute and `./outputs` negatives plus supported baseline/candidate positive smokes/scenarios and raw regrading. Exact argv/environment descriptions/exits/output and raw counterexample events are retained in `spec-focused-checks.json`, `spec-traversal-command.json`, `spec-traversal-repro.json` and `spec-traversal-native.jsonl`.

### Limits

Synthetic transport proves adapter behavior only. Native Codex unsupported telemetry remains invalid. No native/model calls, authentication, trust, source changes, build or aggregate test occurred. The retained 34-test full run predates the final lexical grammar extension. Final-source verification consists of the focused checks above and retained worker checks. No other review-axis report was inspected.
