# Validation levels and routes

- Choose the narrowest existing maintained suite via `rtk proxy python3 scripts/test-all.py --list` and `--help`. Run `rtk proxy python3 scripts/test-all.py` for aggregate integration when warranted and prerequisites exist; formatting and live model evaluation remain separate checks.
- Missing prerequisites are errors, never passing skips. Record command, OS, interpreter/provider version, exit status, and decisive result. The aggregate runner supports macOS/Linux; native Windows uses dedicated workflows.
- Source tests, disposable installations, actual provider delivery, and native Windows execution prove different things. Check [installation ownership](repository-workflow.md#retention-and-installed-evidence); platform skips are not platform evidence.
- Label hypotheses as candidates until an artifact supports them. When stronger certainty is requested, obtain a new relevant file view, search, or validation result. Verify a removed branch with one targeted search; repeat tests only for changed source, failures, or unresolved concerns.
- Preserve failing cases and evidence; never weaken surviving tests to claim success.

## Select by changed area

| Changed area | Guidance |
| --- | --- |
| Shared hook runtime/registration | [Hook source checks](hook-testing.md) |
| Emitters, traces, transcripts, audit/log maintenance | [Hook observability](hook-observability.md) and [hook tests](hook-testing.md) |
| Tool Guardian, scanner security, performance acceptance | [Security testing](security-testing.md) |
| Installed provider event delivery/visible messages | [Live-hook evidence](live-hook-testing.md) |
| Skills, graders, evaluation artifacts | [Skill evaluation](skill-evaluation.md) |
| Shell/Python helper scripts | [Script validation and fixtures](script-testing.md) |
| Bash/PowerShell installers and agent conversion | [Installer validation](installer-testing.md) |
| PowerShell/native Windows behavior | [PowerShell parity and native proof](powershell-installers.md) |

Evidence: restored `.agents/instructions/testing.md` scope at `092038394a2e3bb0cc21fffdec2eb60a12cece29`; [maintained runner](../../scripts/test-all.py) and linked suites checked 2026-10-21. Recheck when suite ownership, prerequisites, platform support, or validation routes change. The table selects checks; it does not assert they passed.
