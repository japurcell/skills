# Shared hook rules

- Edit canonical `hooks/families/` sources and `hooks/manifest.py`, then run `rtk python3 scripts/generate-hooks.py --write` and `--check`.
- Never hand-edit generated outputs. Build-time sharing is allowed; deployed scripts must not import another provider tree.
- Keep stdout valid provider JSON; diagnostics go to stderr. Emit UTF-8 bytes through `sys.stdout.buffer`.
- Read one complete bounded JSON object without waiting for EOF. Reject buffered non-whitespace trailing data; bound idle and total input time.
- Windows pipe readiness before Python 3.12 needs `PeekNamedPipe`; do not assume POSIX nonblocking flags work.
- Python entrypoints use standard-library operations and argument-list subprocesses, never `shell=True`.
- For local startup and turn-end operational hooks, emit one concise hook-name/outcome and safe count where useful. Report every Stop attempt, including repair retries.
- Ordinary pass messages must contain no path, command, document content, or secret. Keep high-rate tool passes, observability-only hooks, SessionEnd success, and the completion bell silent. Put blocks in native denial fields without duplicate display messages.
- Normalize Windows drive-letter payload paths before absolute-path checks. Resolve extensionless commands with `shutil.which()` on Windows; keep provider helper copies synchronized with canonical sources.
- Installers check generated freshness without write mode. Preserve destination runtime logs and unrelated configuration.
- Brain hooks register at repository scope. Copilot uses `.github/hooks`, not user-level `.copilot/hooks`. Global templates intentionally omit brain and tool-guard registrations. Retirement ownership must match the complete launch, including arguments. See [brain hook contracts](brain-hooks.md).
- Hook `.py` and `.sh` files use executable mode 755; Bash installation reapplies it.
- Run same-named provider modules separately when type checking.

Evidence: [generator](../../scripts/generate-hooks.py), [common renderer](../../hooks/families/common.py), checked 2026-10-20. Recheck input, generation, or deployment changes. Provider contracts: [hooks-codex](hooks-codex.md), [hooks-copilot](hooks-copilot.md), [hooks-gemini](hooks-gemini.md).
