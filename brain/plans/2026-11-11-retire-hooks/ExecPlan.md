# Remove scanner, Guardian, and event-emitter hooks

## Purpose / Big Picture

Remove all scan-secrets, scan-status, tool-guard, and send-event hooks, the standalone scanner CLI and Git gates, and dependencies/configuration owned only by these features. The repository should install only retained hooks and preserve unrelated provider configuration. This is a repository change; existing installations are upgraded by the normal installers, not by editing the user's live home in this session.

## Progress

- [x] (2026-11-11) [milestone-1] T1: Resolve CLI/Git gate scope and identify shared runtime dependencies.
- [x] (2026-11-11) [milestone-1] T2: Remove canonical/runtime/provider artifacts and registrations.
- [x] (2026-11-11) [milestone-1] T3: Update installers and existing installer fixtures.
- [x] (2026-11-11) [milestone-1] T4: Remove obsolete tests/tooling and reconcile remaining suites and CI.
- [x] (2026-11-11) [milestone-2] T5: Reconcile documentation and brain guidance.
- [x] (2026-11-11) [milestone-2] T6: Verify generated artifacts and retained hook/installer behavior; review and reflect.
- [x] (2026-11-12) [milestone-3] T7: Complete independent Standards and Spec reviews against the frozen removal snapshot; record three findings as T8 frontier subtasks.
- [ ] [milestone-3] T8a: Restore the original compact formatting of unrelated Gemini arrays (Standards, low).
- [ ] [milestone-3] T8b: Factor only identical retired helper receipts while preserving the expanded provider mapping (Standards, low).
- [ ] [milestone-3] T8c: Add safe one-time retirement documentation for installed scanner bundles and activated per-repository gates, without auto-searching or mutating user repositories or restoring scanner runtime (Spec, P2).
- [ ] [milestone-3] T9: Independently re-review completed T8 fixes and close the cycle; repeat fix/re-review for at most three iterations.

## Surprises & Discoveries

- RTK imports `helpers.observability.begin_hook_capture`, `helpers.audit`, and `helpers.common`; Copilot/Gemini startup scripts also import audit/common. These helpers remain shared even after send-event is deleted.
- Codex retained scripts are self-contained; its generated scanner helper directory can be removed.
- Both installers install the neutral scanner automatically; Git gate activation is separate. This repository has neither active pre-commit/pre-push gates nor core.hooksPath override.

## Decision Log

- 2026-11-11: User explicitly included standalone CLI and Git gates. Delete their complete runtime and dedicated fixtures/tests rather than preserving an unused scanner subsystem.
- 2026-11-11: Keep exact historical registration and asset identities needed for installer retirement. They are migration ownership data, not active configuration. Preserve modified/unowned destination files and runtime logs.
- 2026-11-11: Do not add regression tests for deleted features. Adjust existing suites only where their expected feature inventory changed; preserve assertions for retained behavior.
- 2026-11-11: Treat the earlier single review as historical evidence only; it does not replace the required independent Standards and Spec reviews. Compare removal changes to `5db7440017e081b4d391c92f28d325b2fccf95a0` and exclude the unrelated `skills/default/execplan-implement/SKILL.md` edit.
- 2026-11-11: Use the worktree/coordinator workflow for T8 fixes and T9 re-review, with one isolated implementer and no more than three fix/re-review iterations. The earlier implementation did not follow this workflow; preserve that process fact without changing its recorded evidence.
- 2026-11-12: Accepted T8 resolutions: preserve original Gemini array formatting; factor only byte-identical retired helper receipts while retaining the expanded provider mapping; and document safe one-time removal of old scanner bundles and activated repository gates without automatic repository discovery/mutation or scanner runtime. Normal provider upgrades remove provider hooks but do not discover/uninstall repository gates or bundles.
- 2026-11-12: Integration baseline `b295b31d4d69e1535503e2ac6e4e315f37e46cb1` includes the unrelated user skill edit `skills/default/execplan-implement/SKILL.md`; that path remains excluded from the frozen review scope. Do not rewrite the existing user commit.

## Context and Orientation

`hooks/manifest.py` declares generated provider files, `hooks/families/` renders them, and `hooks/runtime/` contains scanner/Guardian implementation. Provider templates live in `.codex/global-hooks.json`, `.copilot/hooks/hooks.json`, and `.gemini/global-settings.json`. `hooks/registrations.py` owns safe refresh/retirement. `scripts/install.sh` and `scripts/install.ps1` copy assets and invoke provider config mergers. `scripts/test-all.py` and CI workflows explicitly list maintained tests.

## Plan of Work

### Milestone 1: Remove the features and preserve installation
Status: done
Acceptance: met

T2 removes generated targets and corresponding files, canonical feature families, scanner runtime, CLI/Git gate installers, and obsolete diagnostic/benchmark scripts. Preserve shared common/audit/observability implementation and retained hooks. Remove active registration entries and retain exact identities required to retire old registrations on refresh.

T3 updates Bash/PowerShell copy inventories and removes scanner install/preflight calls. It reconciles existing installer fixtures and safe stale-asset cleanup. T4 removes dedicated scanner/Guardian/emitter test cases and fixtures, adjusts retained generator/startup/RTK/lifecycle/runner suites, and updates CI. T2-T4 share the agreed removal inventory and can proceed independently in disjoint files. Verification waits until all edits finish.

### Milestone 2: Deliver a coherent verified repository
Status: done
Acceptance: met

T5 follows T2-T4 and removes obsolete documentation and current brain guidance, preserving clearly historical ADR/plan evidence. T6 follows all edits: regenerate, run generated freshness and generator tests with no concurrent writes, then execute affected retained public hook and installer suites. Review dependency closure and stale references, resolve defects, and run reflection. Parent owns integrated verification.

### Milestone 3: Close independent Standards and Spec review
Status: in progress
Acceptance: not met

T7 followed T6 and reviewed the frozen removal changes from source base `5db7440017e081b4d391c92f28d325b2fccf95a0`. The review excluded the unrelated `skills/default/execplan-implement/SKILL.md` edit. Independent Standards and Spec review reports found two low Standards findings and one P2 Spec finding; all three are recorded as T8a-T8c frontier subtasks in [iteration 1 review evidence](review-1.md). The earlier single review remains historical evidence and was not treated as the required biaxis review. Review was static only; no fresh tests were run.

T8a-T8c depend on T7 and use the accepted resolutions stated in this plan. One isolated implementer owns fixes in a worktree coordinated from the integration baseline. For T8c, verify the documented one-time retirement procedure in a disposable legacy install/repository, and state that normal upgrades remove provider hooks but do not discover or uninstall repository gates or private scanner bundles. Do not automatically search or mutate user repositories, or reintroduce scanner runtime. T9 independently re-reviews the fixes and closes the cycle. Allow at most three fix/re-review iterations; if actionable findings remain after the third, record the unresolved findings and stop for owner direction. The earlier implementation did not follow the worktree/coordinator workflow; preserve that fact as process context without rewriting its implementation or verification evidence above. The integration baseline includes the unrelated `skills/default/execplan-implement/SKILL.md` user edit, which remains outside the review scope.

## Concrete Steps

T7 is complete; its static reports and pinned snapshot details are recorded in [iteration 1 review evidence](review-1.md). Next, dispatch one isolated implementer for T8a-T8c in the worktree/coordinator workflow, using the accepted resolutions in Milestone 3. For T8c, verify the one-time retirement procedure only in a disposable legacy install/repository and document that normal provider upgrades do not discover or uninstall repository gates or private scanner bundles. Do not auto-search or mutate user repositories, or restore scanner runtime. Then independently review the fixes in T9. Repeat fix/re-review at most three iterations; record unresolved findings and stop for owner direction if the third iteration does not close them. The prior implementation and targeted verification are complete as evidenced below. Verification commands ran from `/Users/adam/.codex/worktrees/93e8/skills` and use `rtk`.

## Validation and Acceptance

The implementation validation is complete with evidence below. T7 acceptance is met: separate independent Standards and Spec reviews were completed against the stated source base and scope, with reports and snapshot evidence in [iteration 1 review evidence](review-1.md). The reviews were static and did not run tests. T9 acceptance requires each actionable finding to be fixed and independently re-reviewed, or explicitly recorded as unresolved after at most three iterations for owner direction.

Historical implementation checks completed: `rtk proxy python3 scripts/generate-hooks.py --write`, then `--check` and `rtk proxy python3 scripts/tests/hooks/test-generate-hooks.py`; retained startup, RTK, brain, provider installer, Bash/PowerShell installer, helper, and runner suites; and `rtk proxy python3 scripts/test-all.py`. Platform-specific skips do not prove native Windows behavior. The stale-reference audit found only retirement identities, relevant historical records, and this plan. Existing shared helpers imported and executed without scanner files.

## Idempotence and Recovery

Regeneration and installer refresh are repeatable. Validate only in disposable installer destinations. Do not delete unrelated home files or logs. Recover an accidental source deletion using the original Git version of that specific file without reverting others' edits.

## Outcomes & Retrospective

The requested repository removal is complete: four hook families, standalone scanner CLI and Git gates, their runtime, diagnostics, dedicated fixtures/tests, benchmarks, and configuration are gone. Shared Copilot/Gemini common/audit/observability helpers remain because startup and RTK hooks use them. Codex retains self-contained brain/startup scripts. Existing user-home installations were not modified.

The aggregate exercised all 27 registered suites: 23 initially passed and four exposed stale test assumptions about deleted targets. Those assumptions were corrected while preserving retained safety assertions, and all four focused reruns passed. Native Windows lifecycle execution and Windows-only fixture cases were skipped on macOS; no native Windows claim is made. Generated freshness, YAML parsing, changed Markdown links, and whitespace checks pass.

A prior single review found no source defect and identified an existing ambiguous-launch assertion to restore, which now passes. That review is historical evidence and does not satisfy the pending independent Standards and Spec biaxis review. The implementation phase also did not use the worktree/coordinator workflow; the T8-T9 fix cycle will use it. Iteration 1 review evidence and its three findings are recorded in [review-1.md](review-1.md). Source comparison base is `5db7440017e081b4d391c92f28d325b2fccf95a0`; the unrelated `skills/default/execplan-implement/SKILL.md` edit is outside the removal-change review scope.

Reflection removed obsolete scanner/security brain notes and the now-irrelevant scanner capacity backlog item. Durable retained dependency/retirement guidance lives in [shared hook rules](../../codebase/hooks.md), [hook testing](../../codebase/hook-testing.md), and [shared observability](../../codebase/hook-observability.md). No additional skill changes were warranted.

## Verification evidence

- `rtk proxy python3 scripts/generate-hooks.py --check`: current, 16 files.
- `rtk proxy python3 scripts/tests/hooks/test-generate-hooks.py`: 13 tests passed as part of the aggregate.
- `rtk proxy python3 scripts/tests/installers/test-install-codex-hooks.py`: passed after correcting its stale fixture expectation.
- Aggregate run: `rtk proxy python3 scripts/test-all.py`: 23 passed, four stale-fixture failures in 212.5 seconds, recorded in `/tmp/retire-hooks-suite.log`.
- Focused reruns after corrections: `rtk proxy bash scripts/tests/hooks/test-gemini-hooks-rtk.sh` and the Codex merge command above both exited 0.
- `rtk proxy bash scripts/tests/installers/test-install.sh`: exit 0; `/tmp/retire-hooks-bash.log`.
- `rtk proxy pwsh -NoProfile -File scripts/tests/installers/test-install.ps1`: all tests passed, exit 0; junction fixture skipped on macOS; `/tmp/retire-hooks-powershell.log`.
- Both changed workflows parse as YAML, modified Markdown has no broken relative links, and `rtk proxy git diff --check` passes.
- Disposable old-install migration scenario: removed 16 Codex and 15 each Copilot/Gemini original assets, removed all four retired hook registrations, preserved an unrelated custom file, and left config byte-identical on repeat. No new regression tests were added for feature deletion.
