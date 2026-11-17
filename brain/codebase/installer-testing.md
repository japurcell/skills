# Installer validation contracts

- Activate the `verify-skills` skill for installation journeys and baseline checks. For installer changes, also apply the regression contracts below, [PowerShell fixture checks](powershell-installers.md#fixture-isolation-and-verification), and [script fixture isolation](script-testing.md).
- Stale generated output must stop before destination mutation and show the exact `python3 scripts/generate-hooks.py --write` recovery command. Controlled generator failure must preserve its real diagnostic without misleading stale-output recovery advice.
- Provider refresh fixtures use disposable homes with retired Copilot/Gemini registrations, unrelated settings and unowned handlers, nested Gemini settings, a second install, and a fresh install.
- Malformed or duplicate-key JSON and linked configuration parents must leave the whole home fingerprint unchanged; include external `CODEX_HOME` where applicable. Hard-link checks must preserve the external inode and mode while the installed config becomes an independent owner-only file.
- Codex upgrade fixtures must preserve unmanaged agents, remove stale manifest-owned outputs, and reject malformed sources before copying.
- Test case-folded agent-output collision at the supported converter decision seam on every host and also through two physical source names when the filesystem permits both.
- Run [RTK preflight/configuration checks](script-testing.md#narrow-checks) for RTK/installer changes.

Evidence: restored installer acceptance policy from `.agents/instructions/testing/scripts.md` and `testing/powershell.md` at `092038394a2e3bb0cc21fffdec2eb60a12cece29`; checked [Bash fixtures](../../scripts/tests/installers/test-install.sh), [PowerShell fixtures](../../scripts/tests/installers/test-install.ps1), and [agent converter fixtures](../../scripts/tests/installers/test-codex-agents.py) on 2026-10-21. Recheck when preflight order, merge ownership, link safety, or converter outputs change. Inspection establishes intended coverage, not an executed-suite result.
