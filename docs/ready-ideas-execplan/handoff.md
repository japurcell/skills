# Ready ideas implementation handoff

## Goal and status

The user approved the revised [ExecPlan](ExecPlan.md) and [Windows checklist](windows-live-check.md). Milestones 17-20 and Repair 19A are integrated on `codex/ready-ideas-execplan` at `07d1f133`. Milestone 22 is committed in its isolated branch. Milestones 21 and 23-27 remain open.

## Current evidence

- Milestone 19 removed maintained global Markdown Health source, generated targets, provider registrations, installer copy rules, and dedicated suites. It preserved `scripts/lint-okf.py`, shared audit history, and user-owned old scripts and state. Repair 19A preserves exact old Copilot and Gemini registrations during refresh; fresh homes receive none. The Codex merger leaves old unowned registrations alone.
- The milestone 19 rebase resolved 13 conflicts and retained stable RTK, repository-state retirement, and retired-registration preservation. Source commit: `46eef579`. Generator write/check and 25 tests passed with 26 current outputs. Both temporary-home installer suites passed; PowerShell skipped unsupported junction creation on this Mac.
- Milestone 20 adds project-local OKF turn-end validation for Copilot, Gemini, and Codex with a bounded audit, one repair attempt, checkout containment, and provider-valid incomplete results. The isolated branch passed `bash scripts/test-hooks-okf-lint.sh`, `bash scripts/test-gemini-hooks-okf-lint.sh`, `bash scripts/test-codex-repository-okf.sh`, `bash scripts/test-okf-lint.sh`, `python3 scripts/test_test_all.py`, `python3 scripts/test-install-codex-hooks.py`, `bash scripts/test-install.sh`, `pwsh -NoProfile -File scripts/test-install.ps1`, `python3 scripts/generate-hooks.py --check`, and `python3 scripts/lint-okf.py` on macOS. Native Windows OKF checks skipped here.
- The milestone 20 rebase onto `73db7d4d` resolved four content conflicts in the file map, Windows workflow, ExecPlan, and this handoff. It kept the retired Markdown Health Windows test removed and added the repository OKF Windows test. Post-rebase focused Copilot, Gemini, Codex, central linter, aggregate-runner registry (15 tests), Codex merge, generator freshness (26 outputs), OKF lint, and Bash and PowerShell temporary-home installer checks all passed. The native Windows OKF script skipped on macOS, and PowerShell skipped unsupported junction creation. An earlier automatic review rejected broad Gemini incomplete-result handling; the source commit limits that change to `AfterAgent`.
- The full aggregate runner exits 2 at prerequisite preflight because this Mac lacks external `flock`; it runs no suites. Native Windows scanner HEAD-failure, junction behavior, OKF envelopes, and live provider display remain later gates. No real user home was changed.

## Decisions and limits

Older installations may still execute repository-state or Markdown Health scripts. Review exact user hook registrations and scripts for manual cleanup as described in [README.md](../../README.md); preserve `audit.log` and Markdown Health state by default. Keep milestone branches private and unpushed. Do not weaken tests or add deletion regression tests.

## Next step

Implement milestone 21 sparse lifecycle messages from the integrated milestone 20 hook graph. Then rebase and integrate milestone 22 Tool Guardian detail, and continue the remaining plan frontier.
