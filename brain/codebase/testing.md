# Validation levels and routes

- Choose the narrowest existing maintained suite via `rtk proxy python3 scripts/test-all.py --list` and `--help`. Run `rtk proxy python3 scripts/test-all.py` for aggregate integration when warranted and prerequisites exist; formatting and live model evaluation remain separate checks.
- Missing prerequisites are errors, never passing skips. Record command, OS, interpreter/provider version, exit status, and decisive result. The aggregate runner supports macOS/Linux; native Windows uses dedicated workflows.
- Source tests, disposable installations, actual provider delivery, and native Windows execution prove different things. Check [installation ownership](repository-workflow.md); platform skips are not platform evidence.
- Label hypotheses as candidates until an artifact supports them. When stronger certainty is requested, obtain a new relevant file view, search, or validation result. Verify a removed branch with one targeted search; repeat tests only for changed source, failures, or unresolved concerns.
- Preserve failing cases and evidence; never weaken surviving tests to claim success.
- Give every worktree an independent dependency install before tests that copy or mutate toolchains. A root `node_modules` symlink survives Node `cpSync` without dereferencing; a disposable fixture can then delete or rewrite the shared target. In `packages/software-factory`, use pinned Node and `rtk proxy npm ci --ignore-scripts --offline --cache /tmp/software-factory-npm-cache`; restore/reverify any exposed shared dependency tree before trusting later checks.

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

Dependency isolation evidence: software-factory `test/startup.test.mjs` copies its dependency root and deliberately removes TypeScript in a negative fixture. A worker's shared root symlink exposed the base compiler and fixture package to that mutation on 2026-10-22; separate locked installs restored isolation. Keep this fixture boundary in mind when provisioning any disposable test toolchain.
