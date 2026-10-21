# Validation levels

- Run the narrowest relevant maintained suites, then the integrated checks required by the active plan.
- Record command, OS, interpreter/provider version, exit status, and decisive result.
- Source tests, temporary installations, native platform runs, and actual provider delivery prove different things.
- Skips and missing dependencies are not passes. The aggregate runner supports macOS/Linux; dedicated Windows workflows cover native behavior.
- Preserve failing cases and evidence. Do not weaken surviving tests to claim success.

Routes: [hook-testing](hook-testing.md), [live-hook-testing](live-hook-testing.md), [security-testing](security-testing.md), [powershell-installers](powershell-installers.md), [skill-evaluation](skill-evaluation.md).

Evidence: [maintained runner](../../scripts/test-all.py), checked 2026-10-20. Recheck suite ownership and platform assumptions when changing tests.
