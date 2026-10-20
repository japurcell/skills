# Validation levels

- Run the narrowest relevant maintained suites, then the integrated checks required by the active plan.
- Record command, OS, interpreter/provider version, exit status, and decisive result.
- Source tests, temporary installations, native platform runs, and actual provider delivery prove different things.
- Skips and missing dependencies are not passes. The aggregate runner supports macOS/Linux; dedicated Windows workflows cover native behavior.
- Preserve failing cases and evidence. Do not weaken surviving tests to claim success.

Routes: [[hook-testing]], [[live-hook-testing]], [[security-testing]], [[powershell-installers]], [[skill-evaluation]].

Evidence: [maintained runner](../../scripts/test-all.py), checked 2026-10-20. Recheck suite ownership and platform assumptions when changing tests.
