---
type: Agent Instruction
description: Shared hook implementation rules; route to the affected provider and subsystem only.
---

# Shared Hook Rules

Apply these rules to hook changes, then read only matching branches:

| Change | Additional instructions |
| --- | --- |
| Copilot CLI, cloud, or VS Code compatibility | [Copilot](hooks-copilot.md) |
| Gemini events, configuration, or JSON envelopes | [Gemini](hooks-gemini.md) |
| Codex hooks, trust, or installation | [Codex](hooks-codex.md) |
| Tool Guardian, secret scanning, or security output | [Security](hooks-security.md) |
| Repository OKF validation or stop adapters | [OKF adapters](hooks-okf.md) |
| Source scanners, injectors, manifests, or pending gates | [Source ingestion](hooks-auto-ingest.md) |
| Emitters, SQLite traces, transcripts, audit logs, or maintenance | [Observability](hooks-observability.md) |

- **sparse lifecycle messages:** Local CLI startup and turn-end operational hooks report a short hook-name, outcome, and safe count where useful. Copilot uses one progress JSON line before its final JSON for an allowed visible result; Gemini and Codex use `systemMessage`. Put a blocked result in the existing native denial reason without a second display. Every stop attempt, including a repair retry, reports an outcome. Ordinary pass messages contain no path, command, document content, or secret. Keep high-rate tool passes, observability-only hooks, SessionEnd success, and the completion bell free of text messages. Actionable tool blocks, warnings, and incomplete scans remain immediate. Do not add per-call RTK audit records to prove a pass.
- **generated-provider ownership:** Provider-local Python files with a `Generated from hooks/families/...` header are build outputs. Edit their canonical `hooks/families/` renderer or its typed provider metadata, run `python3 scripts/generate-hooks.py --write`, then require `python3 scripts/generate-hooks.py --check` before committing. Both installers run the same read-only check before destination mutation; stale output must stop installation with the `--write` recovery command, while generator failure must stop without write advice. Never add cross-provider runtime imports; installers never invoke generator write mode.
- **raw-source authority:** For exact hook behavior questions or changes (visible CLI output, stdout parsing, progress messages, event timing, matcher behavior, or output schemas), read the matching raw source under `.agents/sources/` after the summary. Summary files route the investigation but are not final authority for precise hook behavior.
- **stdout discipline:** Hook scripts must keep `stdout` JSON-only. Send logs, audit lines, and debug text to `stderr` or the audit log.
- **selected repository runtimes:** Required-skill loaders are generated from `hooks/families/required_skills.py`; repository launchers and configuration helpers are generated from `hooks/families/repository_runtime.py`. Selected packages stay provider-local and include optional observability helpers where common runtime code can enable capture. Prefer validated `AGENT_ASSETS_RUNTIME_CONFIG` for skill/reference roots and required files, then retain personal fallback behavior. Runtime input must never select skill roots.
- **repository runtime state:** Launchers route audit, guard, scanner, and optional trace state to `AGENT_ASSETS_STATE_DIR` or the OS user-state home, partitioned by provider and normalized-target-path hash. Reject state inside the installed repository and disable bytecode writes. Preserve the legacy guard-path distinction: Codex/Copilot expect a file, Gemini expects a directory. Keep personal hook settings unchanged and report additive registrations plus unverified native trust.
- **personal command quoting:** Quote the complete `$HOME/...` Bash command path in Copilot main and RTK registrations. Verify registered commands in a disposable home containing spaces, not only parsed config strings; preserve matching PowerShell commands.
- **installed-copy rule:** For personal live validation, refresh the installed home-directory copies first. Selected repository-hook validation uses a disposable target and its native project registrations; never install into the real home for tests.
- **runtime-log isolation:** Installers must not copy ignored runtime state from source hook trees, especially `.gemini/hooks/logs/`. Preserve existing destination logs while copying maintained hook scripts and config.
- **stdin completion:** Hook JSON readers must return after one complete JSON value is available instead of waiting for stdin EOF. Read pipe bytes incrementally, drain bytes already buffered after the value, and reject any non-whitespace trailing data. Open pipes need a bounded completion window before the first byte and after every incomplete chunk because malformed and valid prefixes cannot always be distinguished syntactically. Keep the Windows path compatible with Python versions before 3.12 by using `PeekNamedPipe` instead of relying on nonblocking pipe support in `os.set_blocking`.
- **RTK failure diagnostics:** When an RTK forwarder receives a nonzero subprocess exit, audit the exit code without copying subprocess stderr. RTK stderr can contain payload or environment details and has no wrapper-defined size bound.
- **Explicit RTK commands:** Use stable RTK 0.50.0 or newer directly. The installers persist `[hooks] suppress_hook_warning = true` in the user's RTK TOML without changing unrelated settings; this account-wide setting silences only the false missing-hook advisory. Keep the Copilot and Gemini automatic RTK forwarders and their provider registrations. Codex uses explicit `rtk` commands and has no automatic RTK forwarder.
- **executable permissions:** All shell (`.sh`) and Python (`.py`) hook scripts must have standard executable permissions (`755`) set in the source tree and verified by the test-install suite. The installer (`scripts/install.sh`) must explicitly apply `chmod 755` to all copied hooks to ensure they remain executable across runtime IDE sessions regardless of the source umask.
- **Separate but Unified:** Keep the `.copilot` and `.gemini` hook scripts completely separated (no cross-directory imports), but structurally unified and synchronized. Use identical helper logic where possible, parameterizing only runtime-specific variables (like default paths or environment lookups) and emitting only the specific JSON decision output expected by each hook platform.

- Keep operational entrypoints Python-first. Use argument-list subprocess calls without `shell=True`; preserve deterministic line-oriented parsing for required-skill delimiters and diff-only secret suppression.
- Normalize Windows drive-letter payload paths before absolute-path checks; keep provider helpers synchronized. Resolve extensionless commands through `shutil.which()` on Windows.
- Emit JSON as UTF-8 bytes through `sys.stdout.buffer`, using stream reconfiguration only as fallback. Preserve the corresponding Windows and open-stdin cases.
- An RTK exit `0` with empty or whitespace-only stdout is a valid no-op. Diagnose explicit CLI notices separately from automatic forwarding.
- Run mypy separately on same-named provider modules to avoid module-name collisions.

Use [hook testing](testing/hooks.md) for validation selection and [live-hook testing](testing/hooks-live.md) only for deployed behavior. Task-specific installation ownership in [repository workflow](repo.md) still applies.
