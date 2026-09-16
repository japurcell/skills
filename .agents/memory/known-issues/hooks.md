---
type: Known Issue
description: General provider-hook failures; specialized auto-ingest and observability issues live in focused sibling files
---

# Hooks - Known Issues

Load this file for general provider-hook work. For source scanners, manifests, summaries, injectors, or pending gates, read [Hook Auto-Ingest - Known Issues](hooks-auto-ingest.md). For emitters, SQLite traces, transcripts, logs, or maintenance, read [Hook Observability - Known Issues](hooks-observability.md).

## Active guards can block their own maintenance

Tool Guardian scans patch, search, replacement, and cleanup payloads. Raw dangerous command strings can block safe policy edits or tests; multiline serialized text can also create false matches across escaped newlines. Construct required threat strings dynamically, keep unrelated dangerous lines outside replacement hunks, and keep deletion-target matching bounded to one logical line and a short distance.

Secret scanning has the same self-edit risk for realistic fake credentials. Use unmistakably fake values such as `fake-api-key`; never write a real secret.

## Same-named hook modules confuse mypy

Copilot and Gemini contain same-relative-path modules such as `observability.py`. Run mypy on each file separately instead of passing both in one invocation.

## Bash `RETURN` traps can outlive local variables

Under `set -u`, interpolate function-local cleanup paths when registering the trap, for example `trap 'rm -rf -- "'"$workdir"'"' RETURN`. At trap execution, the local variable may no longer exist.

## Secret-scanner Git probes can hang on Windows

Run Git with `GIT_TERMINAL_PROMPT=0`, an empty `GIT_ASKPASS`, and a short timeout. Let timeout errors reach the top-level handler so block mode denies; warn mode may emit a sanitized no-op.

## Extensionless commands fail on Windows

With `shell=False`, resolve commands such as `rtk` through `shutil.which()` so `.cmd` or `.bat` executables are found.

## Empty RTK output is a valid no-op

When RTK exits `0` with empty or whitespace-only stdout, return `({}, None)` instead of attempting JSON parsing.

## PowerShell command paths need runtime-specific forms

In installed Gemini settings, prefix Python files with `python` and wrap `$HOME/...` paths in escaped double quotes. In repo-local `.gemini/settings.json`, use workspace-relative `python .gemini/hooks/scripts/...py` commands; `$GEMINI_PROJECT_DIR` plus forward slashes can be split as a PowerShell expression.

## POSIX runtimes need Windows path conversion

Normalize drive-letter payload paths with `convert_windows_path_to_posix` before absolute-path checks. Keep the helper synchronized across `.copilot`, `.github`, and `.gemini`.

## Windows text stdout can reject Unicode JSON

CP1252 streams can raise a charmap error for non-ASCII payloads. `emit_json()` must write UTF-8 bytes through `sys.stdout.buffer`, with `sys.stdout.reconfigure(encoding="utf-8")` only as fallback.

## Open stdin can stall complete JSON payloads

Do not use `sys.stdin.read()` or one `readline()`. Incrementally decode until `JSONDecoder.raw_decode` finds one value, drain buffered bytes, reject non-whitespace trailing data, and bound incomplete input. Use `PeekNamedPipe` on Windows before Python 3.12. Keep provider helpers and open-stdin regressions synchronized.
