# Ready ideas implementation handoff

## Goal and status

The user approved the revised [ExecPlan](ExecPlan.md) and [Windows checklist](windows-live-check.md). Milestones 17-19 and Repair 19A are integrated on `codex/ready-ideas-execplan` at `d54d5619`. Milestone 20 is active in `/Users/adam/.codex/worktrees/ready-retire-git-guard/skills` on `codex/ready-repository-okf`; milestone 22 is committed in its isolated branch. Milestones 21 and 23-27 remain open.

## Current evidence

- Milestone 19 removes maintained global Markdown Health family, generated targets, provider registrations, installer copy rules, and dedicated suites. It preserves `scripts/lint-okf.py`, shared audit history, and user-owned old scripts and state. Repair 19A preserves exact old Copilot and Gemini registrations during refresh; fresh homes receive none. The Codex merger leaves old unowned registrations alone.
- The milestone 19 rebase onto `cc0ca9c7` resolved 13 content conflicts across docs, Windows workflow, Codex ownership, installers, and tests. The result keeps stable RTK, the repository-state retirement, and retired-registration preservation. Source commit: `46eef579`.
- Repair 19A's fresh-install absence assertions stayed intact after automatic review rejected their removal. Its linked-config fix uses private atomic replacement and rejects linked parent directories before writes; native Windows junction proof remains open.
- Generator write/check and its 25 tests pass with 26 current outputs. Both full temporary-home installer suites pass; the PowerShell junction case skips on this Mac. Codex merger and Windows envelope tests, 15 aggregate-runner unit tests, OKF lint and its CLI suite, and Copilot/Gemini RTK and Tool Guardian suites pass. `git diff --check` passes. Retained-hook probes emitted observability database write warnings in the sandbox but exited 0.
- Full `scripts/test-all.py` exits 2 at preflight because this Mac lacks external `flock`; it runs no suites. The targeted suites above provide local proof. Native Windows scanner HEAD-failure, junction behavior, and local provider display are later gates. No real user home was changed.

## Decisions and limits

Older installations on another machine may still execute repository-state or Markdown Health scripts. Review exact user hook registrations and scripts for manual cleanup as described in [README.md](../../README.md); preserve `audit.log` and Markdown Health state by default. The source and fresh-home evidence does not certify an older home. Do not weaken tests or add deletion regression tests. Keep milestone branches private and unpushed.

## Next step

Complete milestone 20's repository-local OKF hook and tests in its isolated worktree. Rebase its branch onto the latest base before fast-forward integration. Then implement milestone 21 lifecycle messages, integrate milestone 22 Tool Guardian detail, and continue the remaining plan frontier.
