# Scripts and installers

- `scripts/test-all.py` explicitly owns the maintained suite registry; never discover fixture or archived tests automatically.
- Installers run the generator's read-only `--check` before destination mutation. Stale output gives the `--write` recovery command; generator errors need their actual diagnostic.
- Keep validation fixtures in temporary homes; never run normal installation into the actual home as a test.
- Preserve unrelated configuration, unmanaged agents, and runtime logs. Repeated installs must converge.
- Refuse linked destinations and unsafe parents; preserve owner-only configuration and atomic writes.
- Prefer standard-library scripts with explicit CLI contracts. Results go to stdout; diagnostics and progress go to stderr.
- Do not add human-only orchestration scripts where agent workflow skills own the process.

Evidence: [Bash installer](../../scripts/install.sh), [provider merger](../../scripts/install-provider-hooks.py), [runner](../../scripts/test-all.py), checked 2026-10-20. Recheck installer ownership or validation changes.
