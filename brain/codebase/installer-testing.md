# Installer validation contracts

- Bash changes: `rtk proxy bash -n scripts/install.sh` then `rtk proxy bash scripts/test-install.sh`. PowerShell changes also use [PowerShell fixture checks](powershell-installers.md#fixture-isolation-and-verification). Apply [script fixture isolation](script-testing.md).
- Stale generated output must stop before destination mutation and show the exact `python3 scripts/generate-hooks.py --write` recovery command. Controlled generator failure must preserve its real diagnostic without misleading stale-output recovery advice.
- Provider refresh fixtures use disposable homes with retired Copilot/Gemini registrations, unrelated settings and unowned handlers, nested Gemini settings, a second install, and a fresh install.
- Malformed or duplicate-key JSON and linked configuration parents must leave the whole home fingerprint unchanged; include external `CODEX_HOME` where applicable. Hard-link checks must preserve the external inode and mode while the installed config becomes an independent owner-only file.
- Codex agents/global instructions: `rtk proxy python3 scripts/test-codex-agents.py` plus the relevant installer suite. Parse TOML; preserve exact instructions, managed cleanup, `CODEX_HOME` selection, malformed-source early failure before copy, and replacement of `$HOME/.codex/AGENTS.md` from repository `.codex/AGENTS.md`.
- Test case-folded agent-output collision at the supported converter decision seam on every host and also through two physical source names when the filesystem permits both.
- Run [RTK preflight/configuration checks](script-testing.md#narrow-checks) for RTK/installer changes; validate only in disposable homes. Installer tests never justify writing into the actual home.
- Keep native Windows junction/ACL proof separate from POSIX mode assertions; a skipped platform case is not passing evidence.

Evidence: restored installer acceptance policy from `.agents/instructions/testing/scripts.md` and `testing/powershell.md` at `092038394a2e3bb0cc21fffdec2eb60a12cece29`; checked [Bash fixtures](../../scripts/test-install.sh), [PowerShell fixtures](../../scripts/test-install.ps1), and [agent converter fixtures](../../scripts/test-codex-agents.py) on 2026-10-21. Recheck when preflight order, merge ownership, link safety, or converter outputs change. Inspection establishes intended coverage, not an executed-suite result.
