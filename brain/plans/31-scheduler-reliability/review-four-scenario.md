# Independent four-scenario correction review

Both independent axes report zero material findings for the captured F2-D delta. Base/target HEAD/merge base `42f731fb87d86d1e93e5553a65e6561832355fc7` plus immutable uncommitted snapshot. [Metadata](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-four-scenario/source.json), [diff](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-four-scenario/diff.patch) and [captured log](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-four-scenario/commits.txt). Diff SHA-256 `fa2fe244bb4fd3186351d2e9cecf58017cd13fb8bde9f9322ce805ec6f4b3e78`. All four listed source hashes match captured bytes.

## Standards

Reviewed immutable `review-four-scenario/snapshot`, `source.json`, `diff.patch` and empty `commits.txt` against current ExecPlan F2-D. Base, target HEAD and merge base are `42f731fb87d86d1e93e5553a65e6561832355fc7`. The captured uncommitted delta changes the eval README, harness and tests.

Verified captured SHA-256 identities directly.

- Diff `fa2fe244bb4fd3186351d2e9cecf58017cd13fb8bde9f9322ce805ec6f4b3e78`.
- Harness `7cc5afe5ffa42a862a5cf81fdddaeb31c4ea80f04cb46a5372ac197bad2cc6f1`.
- Tests `dc5afd44262cee933f346a2175358ade4e45884cdcfe66c30fd40a5c8d6e361d`.
- README `8da3c4b3a6b11f3737e47cff33bbc2dbd9257bc63c1874aeadfaa1cd4bcb0dda`, recorded in `source.json`.

Zero material documented-standard violations and zero material baseline-smell findings in this delta.

The test disposition preserves the mixed prompt-immutability, authoritative-evidence, raw-evidence mutation and replay checks while retiring the approved cross-phase gates. Both provider scenario tests now exercise independent scored execution without prerequisite smoke. Timeout, helper cancellation, Copilot status cancellation, canonical-state, chronology and rubric checks remain present. The added prefix test uses real helper children and rejects mismatched interpreter and argv claims.

Inspected retained public prefix reproduction and red/green logs. These are historical worker evidence, with no test failures reproduced by this reviewer. Offline passing fixtures establish the bounded parser/helper behavior. Native Copilot direct-helper permission acceptance remains unproven and the README correctly requires current scored execution evidence.

No provider calls or test suites were run during this static review. Final maintained-suite results remain separately owned evidence.

[Original Standards report](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-four-scenario/standards.md).

## Spec

Zero material findings in the bounded F2-D delta review.

Reviewed `review-four-scenario/snapshot`, `source.json`, the captured three-file diff and current snapshot ExecPlan F2-D. Base, target and merge base are `42f731fb87d86d1e93e5553a65e6561832355fc7`, with captured uncommitted changes. Harness SHA-256 is `7cc5afe5ffa42a862a5cf81fdddaeb31c4ea80f04cb46a5372ac197bad2cc6f1`. Tests SHA-256 is `dc5afd44262cee933f346a2175358ade4e45884cdcfe66c30fd40a5c8d6e361d`.

- F2-D requires “Remove redundant separate neutral-smoke and prior-phase-success prerequisites from scored launches and grading.” `run` removes both cross-phase gates and `grade` qualifies solely from current scenario validation. Exclusive attempt directories and current-phase validation remain. Four native-shaped scored positives now run without standalone smokes, while optional smoke CLI support remains diagnostic.
- F2-D requires extensionless `invoke-scheduler`, a “pinned absolute shebang, executable mode, narrow literal helper-path grant and shared prompt prefix.” Preparation uses that generated filename, freezes mode 0500 and bytes, and explicitly instructs direct invocation without prepending Python. Copilot grants retain the exact helper path. Maintained helper source is unchanged.
- F2-D requires recognizing the known Codex Python prefix only through “the frozen shell PATH to the known pinned interpreter” while preserving raw commands, exact argv and child receipts. `helper_arguments` restricts interpreter tokens to `python3` or the pinned absolute path, verifies frozen-PATH resolution and interpreter hash, and requires the exact helper path. `helper_records` still checks the complete child argv. `phase_events` retains `raw_command`. Positive pinned-prefix and negative wrong-interpreter/argv public tests cover the correction.

Static inspection found retained current-phase identity, source/prompt binding, canonical state-chain/readbacks, replay protection, common rubric and separate candidate acknowledgment checks intact. Supplied focused logs report passing correction checks and matching source hashes. Final maintained-suite verification is running separately, so this review makes no completed-suite claim. No suite or native provider process was executed by this reviewer. Actual remaining scored-session acceptance remains F3 evidence.

[Original Spec report](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-four-scenario/spec.md).

## Subsequent verification and integration

The separate final unchanged-byte suite passed 39 tests in 137.926 seconds, exit 0. [Final suite](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-four-scenario-fix/final-suite.log), [acceptance](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-four-scenario-fix/acceptance.json) and [exact hashes](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-four-scenario-fix/final-hashes.json). Committed source verification and integration are complete at `47d985b7b698077e0dcb4a9e28b3169db1a7bc13`. All four listed source hashes match reviewed snapshot, final tested hashes, clean worker commit and integrated root files. The maintained helper source is unchanged. Source correction is accepted. Native scored execution remains separate evidence.

## Next execution boundary

Only the four scenario slots are authorized and active in the next fresh payload. Optional diagnostic smoke CLI or manifest entries do not grant smoke launches. Parent uses the exact prepared PATH. Current-phase native helper/session/selector and full state/rubric evidence determine each scored result independently. P04 remains historical and unchanged.

## Prompt clarification addendum

The one-sentence prompt clarification is accepted and integrated at `c52ab3d7cfee5c783dd62c89a26b51c57de5d0c3`, final harness SHA-256 `2983c40a5bf864917f07c440b2cc991f051b376e436de4da7546ccf8fbfad739`. It explicitly requests one helper invocation per native shell call and preserves the existing evidence contract. Both mechanical delta acknowledgments report zero findings. Public preparation found the sentence exactly once in all six prepared prompts, and three existing targeted public checks passed in 5.623 seconds. The 39-test full-suite pass remains bound to `47d985b7`/harness `7cc5afe5...`; no full-suite pass is claimed for the final prompt-only hash.

- Standards acknowledges zero material findings in the exact one-source-line prompt delta. [Acknowledgment](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-prompt-clarity/standards.md).
- Spec acknowledges zero material findings, with the four-scored-slot contract unchanged. [Acknowledgment](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-prompt-clarity/spec.md).

[Exact delta metadata](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-prompt-clarity/source.json), [public preparation proof](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-four-scenario-fix/prompt-clarity-proof.json) and [targeted test log](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-four-scenario-fix/prompt-clarity-targeted.log). Optional diagnostic smoke prompts in the proof are unlaunched and outside the four active scored slots. The earlier source47 P05 draft is retained as [historical unrun preparation](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-focused-pilot-05-source47-draft/source-binding.json). Parent prepares final P05 from the accepted final source.
