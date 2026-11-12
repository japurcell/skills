# Remove scanner, Guardian, and event-emitter hooks

## Purpose / Big Picture

Remove all scan-secrets, scan-status, tool-guard, and send-event hooks, the standalone scanner CLI and Git gates, and dependencies/configuration owned only by these features. The repository should install only retained hooks and preserve unrelated provider configuration. Normal provider upgrades retire owned provider hook registrations and unchanged owned hook assets. They do not discover or uninstall existing standalone scanner bundles or repository-local Git gates; those require the explicit one-time procedure in [the scanner retirement guide](../../../../docs/retiring-scan-secrets.md). This is a repository change; no user home or repository is modified in this session.

## Progress

- [x] (2026-11-11) [milestone-1] T1: Resolve CLI/Git gate scope and identify shared runtime dependencies.
- [x] (2026-11-11) [milestone-1] T2: Remove canonical/runtime/provider artifacts and registrations.
- [x] (2026-11-11) [milestone-1] T3: Update installers and existing installer fixtures.
- [x] (2026-11-11) [milestone-1] T4: Remove obsolete tests/tooling and reconcile remaining suites and CI.
- [x] (2026-11-11) [milestone-2] T5: Reconcile documentation and brain guidance.
- [x] (2026-11-11) [milestone-2] T6: Verify generated artifacts and retained hook/installer behavior; review and reflect.
- [x] (2026-11-12) [milestone-3] T7: Complete independent Standards and Spec reviews against the frozen removal snapshot; record three findings as T8 frontier subtasks.
- [x] (2026-11-12) [milestone-3] T8a: Restore the original compact formatting of unrelated Gemini arrays (Standards, low).
- [x] (2026-11-12) [milestone-3] T8b: Factor only identical retired helper receipts while preserving the expanded provider mapping (Standards, low).
- [x] (2026-11-12) [milestone-3] T8c: Add safe one-time retirement documentation for installed scanner bundles and activated per-repository gates, without auto-searching or mutating user repositories or restoring scanner runtime (Spec, P2).
- [x] (2026-11-12) [milestone-3] T9a: Complete iteration-2 independent Standards and Spec re-review of the integrated T8a-T8c fixes; record outcomes and evidence.
- [x] (2026-11-12) [milestone-3] T8d: Reconcile the active plan to mark T8a-T8c complete and make re-review the next action.
- [x] (2026-11-12) [milestone-3] T8e: Clarify standalone bundle cleanup: validate every manifest path is relative and confined to the bundle, remove verified payloads, remove root `installation.json` last, then remove empty directories. Preserve ambiguous bundles.
- [x] (2026-11-12) [milestone-3] T9b: Complete the third and final independent review; Standards and Spec found no remaining findings.

## Surprises & Discoveries

- RTK imports `helpers.observability.begin_hook_capture`, `helpers.audit`, and `helpers.common`; Copilot/Gemini startup scripts also import audit/common. These helpers remain shared even after send-event is deleted.
- Codex retained scripts are self-contained; its generated scanner helper directory can be removed.
- Before removal, both installers installed the neutral scanner automatically; Git gate activation was separate. This repository had neither active pre-commit/pre-push gates nor a core.hooksPath override.

## Decision Log

- 2026-11-11: User explicitly included standalone CLI and Git gates. Delete their complete runtime and dedicated fixtures/tests rather than preserving an unused scanner subsystem.
- 2026-11-11: Keep exact historical registration and asset identities needed for installer retirement. They are migration ownership data, not active configuration. Preserve modified/unowned destination files and runtime logs.
- 2026-11-11: Do not add regression tests for deleted features. Adjust existing suites only where their expected feature inventory changed; preserve assertions for retained behavior.
- 2026-11-11: Treat the earlier single review as historical evidence only; it does not replace the required independent Standards and Spec reviews. Compare removal changes to `5db7440017e081b4d391c92f28d325b2fccf95a0` and exclude the unrelated `skills/default/execplan-implement/SKILL.md` edit.
- 2026-11-11: Use the worktree/coordinator workflow for T8 fixes and T9 re-review, with one isolated implementer and no more than three fix/re-review iterations. The earlier implementation did not follow this workflow; preserve that process fact without changing its recorded evidence.
- 2026-11-12: Accepted T8 resolutions: preserve original Gemini array formatting; factor only byte-identical retired helper receipts while retaining the expanded provider mapping; and document safe one-time removal of old scanner bundles and activated repository gates without automatic repository discovery/mutation or scanner runtime. Normal provider upgrades remove provider hooks but do not discover/uninstall repository gates or bundles.
- 2026-11-12: Integration baseline `b295b31d4d69e1535503e2ac6e4e315f37e46cb1` includes the unrelated user skill edit `skills/default/execplan-implement/SKILL.md`; that path remains excluded from the frozen review scope. Do not rewrite the existing user commit.

## Context and Orientation

`hooks/manifest.py` declares generated provider files and `hooks/families/` renders them. The retired scanner/Guardian implementations formerly in `hooks/runtime/` were removed; no scanner runtime remains in the current tree. Provider templates live in `.codex/global-hooks.json`, `.copilot/hooks/hooks.json`, and `.gemini/global-settings.json`. `hooks/registrations.py` owns safe refresh/retirement. `scripts/install.sh` and `scripts/install.ps1` copy assets and invoke provider config mergers. `scripts/test-all.py` and CI workflows explicitly list maintained tests.

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
Status: done
Acceptance: met

T7 followed T6 and reviewed the frozen removal changes from source base `5db7440017e081b4d391c92f28d325b2fccf95a0`. The review excluded the unrelated `skills/default/execplan-implement/SKILL.md` edit. Independent Standards and Spec review reports found two low Standards findings and one P2 Spec finding; all three are recorded as T8a-T8c frontier subtasks in [iteration 1 review evidence](review-1.md). The earlier single review remains historical evidence and was not treated as the required biaxis review. Review was static only; no fresh tests were run.

T8a-T8c are complete in fixer commit `a22ea7685f855f1e3033927efed42c6213b8ae5a`, fast-forwarded onto integration commit `84c0707c5cff5a1feb533783c24ae8df8c6725c0`. T8a restores Gemini formatting; T8b factors shared retired receipts while preserving all 55 expanded mapping entries; T8c adds the [scanner retirement guide](../../../../docs/retiring-scan-secrets.md). The fixer reports its provider installer suite passed, the expanded receipt mapping is identical before and after, Gemini JSON values are unchanged, and a disposable legacy bundle/gate scenario retired ownership, restored the previous `core.hooksPath`, and preserved the original executable pre-commit hook. No deletion regression tests were added. Iteration 2 re-review completed against integrated source commit `a22ea7685f855f1e3033927efed42c6213b8ae5a` and base `5db7440017e081b4d391c92f28d325b2fccf95a0`. Snapshot path: `/tmp/retire-hooks-step7/iteration-2/source`; SHA-256: `4c8b56f2510e2c5972fb003701cd4e5752f58702d4c51c15dfb589792ec5d1f3`; full metadata and findings are in [iteration 2 review evidence](review-2.md). Standards found the frozen plan still directed T8 dispatch; that is resolved in the current plan update. Spec found the guide leaves root `installation.json` behind. T8e completed the required guide fix; T9b is the third and final independent review. If actionable findings remain after it, record them and stop for owner direction. The implementation phase did not follow the worktree/coordinator workflow; the T8-T9 review/fix cycle uses it. The integration baseline includes the unrelated `skills/default/execplan-implement/SKILL.md` user edit, which remains outside the review scope.

## Concrete Steps

All tasks T1-T9b are complete. Iteration 1, 2, and 3 reports and pinned source snapshots are recorded in [review-1.md](review-1.md), [review-2.md](review-2.md), and [review-3.md](review-3.md). The third review found no actionable findings. The reviewed source target was `e4656ef4c1c969d13ec7d8198cb0e0a68b93f1d8`; the later archive, navigation, and review-closure changes are documentation-only and were not part of that source review. Verification commands ran from `/Users/adam/.codex/worktrees/93e8/skills` and use `rtk`.

## Validation and Acceptance

The implementation validation is complete with evidence below. T7 acceptance is met: separate independent Standards and Spec reviews were completed against the stated source base and scope, with reports and snapshot evidence in [iteration 1 review evidence](review-1.md). The reviews were static and did not run tests. T8a-T8e are complete. Iteration 2 static review is recorded in [review-2.md](review-2.md), and T8e disposal evidence is recorded at `/private/tmp/retire-hooks-step7/iteration-2/bundle-cleanup-evidence.txt`. T9b, the third and final independent review, is complete with zero Standards and zero Spec findings. The reviewed source target was `e4656ef4c1c969d13ec7d8198cb0e0a68b93f1d8`; the later archive/navigation commit is documentation-only and is not part of that source review. Full reports and snapshot provenance are in [review-3.md](review-3.md). Milestone 3 acceptance is met; no findings remain unresolved.

Integrated fix checks reported by the fixer: `rtk proxy python3 -c 'import subprocess; p=subprocess.run(["bash", "scripts/tests/installers/test-install.sh"], text=True, capture_output=True); print("exit_code:", p.returncode); lines=(p.stdout+p.stderr).splitlines(); print("\n".join(lines[-12:]))'` exited 0 (covering provider configuration merge behavior); all 55 expanded `RETIRED_ASSETS` entries were identical before and after factoring; Gemini JSON values were unchanged; the disposable legacy uninstall scenario exited 0, restored the prior `core.hooksPath`, preserved the original executable pre-commit hook, and marked retirement complete. `rtk git diff --check` passed. These reports are from the fixer; no broader suite was rerun during integration. After fast-forward integration, `rtk proxy python3 scripts/generate-hooks.py --check` reported current (16 files), and `rtk proxy python3 scripts/tests/installers/test-install-codex-hooks.py` passed. `rtk git diff --check` and the changed brain Markdown link audit passed. Historical implementation checks completed: `rtk proxy python3 scripts/generate-hooks.py --write`, then `--check` and `rtk proxy python3 scripts/tests/hooks/test-generate-hooks.py`; retained startup, RTK, brain, provider installer, Bash/PowerShell installer, helper, and runner suites; and `rtk proxy python3 scripts/test-all.py`. Platform-specific skips do not prove native Windows behavior. The stale-reference audit found only retirement identities, relevant historical records, and this plan. Existing shared helpers imported and executed without scanner files.

## Idempotence and Recovery

Regeneration and installer refresh are repeatable. Validate only in disposable installer destinations. Do not delete unrelated home files or logs. Recover an accidental source deletion using the original Git version of that specific file without reverting others' edits.

## Outcomes & Retrospective

The requested repository removal is complete: four hook families, standalone scanner CLI and Git gates, their runtime, diagnostics, dedicated fixtures/tests, benchmarks, and configuration are gone. Shared Copilot/Gemini common/audit/observability helpers remain because startup and RTK hooks use them. Codex retains self-contained brain/startup scripts. Existing user-home installations were not modified.

The aggregate exercised all 27 registered suites: 23 initially passed and four exposed stale test assumptions about deleted targets. Those assumptions were corrected while preserving retained safety assertions, and all four focused reruns passed. Native Windows lifecycle execution and Windows-only fixture cases were skipped on macOS; no native Windows claim is made. Generated freshness, YAML parsing, changed Markdown links, and whitespace checks pass.

A prior single review found no source defect and identified an existing ambiguous-launch assertion to restore, which now passes. That review is historical evidence and does not substitute for the independent Standards and Spec review and re-review cycle. The implementation phase also did not use the worktree/coordinator workflow; the T8-T9 fix cycle will use it. Iteration 1 review evidence and its three findings are recorded in [review-1.md](review-1.md). Source comparison base is `5db7440017e081b4d391c92f28d325b2fccf95a0`; the unrelated `skills/default/execplan-implement/SKILL.md` edit is outside the removal-change review scope.

T8e completed the documented one-time bundle cleanup gap; its disposable verification is recorded at `/private/tmp/retire-hooks-step7/iteration-2/bundle-cleanup-evidence.txt`. The third/final independent review found no remaining Standards or Spec findings; its report and snapshot provenance are in [review-3.md](review-3.md).

Reflection removed obsolete scanner/security brain notes and the now-irrelevant scanner capacity backlog item. The durable one-time retirement steps are centralized in the scanner retirement guide, with a short link from brain/codebase/hooks.md; no further durable findings or skill changes were warranted. Durable retained dependency guidance lives in [shared hook rules](../../../codebase/hooks.md) and [hook testing](../../../codebase/hook-testing.md). Hook capture was retired later; its original decision is preserved in the [historical observability ADR](../../../../docs/adr/0003-sqlite-backed-hook-observability.md). One-time retirement steps for old standalone scanner bundles and activated repository gates live in the [scanner retirement guide](../../../../docs/retiring-scan-secrets.md); brain guidance links there instead of duplicating its procedure. No additional skill changes were warranted.

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
