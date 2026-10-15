# T7 integration evidence

Observed on macOS on 2026-10-14. This is the exclusive merger result for T7, an integration portion of I3. No base branch or primary worktree was changed.

## Rebase and conflicts

- Original private branch `codex/hook-resilience-t7`: `2f5271beda40478949d6ea20c59defd85d915c2e`.
- Frozen base `codex/fix-hook-bug-reports-2`: `8af2e8cf9b798aa435eff46974228d1c8208e2c5`.
- Rebased implementation: `3b444894a833a8977d02d927f39fa6cbb0e10b8a`.

`rtk proxy git rebase 8af2e8cf9b798aa435eff46974228d1c8208e2c5` conflicted only in `DIAG_BUILD` and `DIAG_ASSETS` in six generated scanner/standalone diagnostic files across all providers. Both canonical changes applied cleanly: T6's whole-label Guardian sanitizer and T7's trusted installed-registration recognition. Resolved the outputs with `rtk proxy python3 scripts/generate-hooks.py --write`, staged them, and continued the rebase. No generated side was selected and no substantive source repair was needed.

Original SHA references in [T7 evidence](T7-evidence.md) remain historical red/green evidence. Primary owns active-plan reconciliation, final integration, cleanup and the single end-of-session knowledge-maintenance pass.

## Combined-tree checks

Commands ran from the T7 worktree. Elapsed times are functional observations, not performance acceptance.

- `rtk proxy python3 scripts/generate-hooks.py --check`: all 38 files current before and after the suites.
- `rtk proxy python3 scripts/test-security-reporting.py -v`: 11 tests passed in 31.605 seconds, including embedded credential labels and clean logging.
- `rtk proxy python3 scripts/test-hook-diagnostics.py -v`: 8 tests passed in 2.078 seconds, including current build identity and assets.
- `rtk proxy python3 scripts/test-hook-diagnostic-recovery.py -v`: all 12 passed in 31.543 seconds. Actual isolated Bash and macOS PowerShell installations exercised registered scanner/Guardian commands against hostile PYTHONPATH/site startup and post-install PATH replacement. Ordinary scanning, Guardian denial, audit evidence, doctor counts and appended-operand rejection passed.
- `rtk proxy python3 scripts/test-install-codex-hooks.py`: maintained Codex merge assertions passed, including exact trusted pairs and preservation.
- `rtk proxy python3 scripts/test-generate-hooks.py`: all 26 passed in 18.896 seconds, alone after all other worktree test processes finished, with source frozen.
- `rtk proxy git diff --check`: passed. Worktree was clean before adding this evidence and the base ref still matched its frozen SHA.

## Reused evidence and limits

`git diff 2f5271be HEAD --` was empty for canonical diagnostics, both installers, both registration mergers, `scripts/trusted_hook_launch.py`, recovery tests and all three install test files. `git diff 8af2e8cf HEAD --` was empty for canonical Guardian, security-reporting tests and all three generated policy helpers. Broad T7 Bash/PowerShell installer evidence remains applicable to unchanged installer logic. Fresh recovery12 proves actual installed-launch interactions with combined identities.

No full merge33, aggregate or benchmark was run. Native Windows and authenticated provider dispatch remain unverified. Branch remains private and unpushed. Primary may fast-forward after confirming both worktrees clean and owns subsequent composed I3/release acceptance.
