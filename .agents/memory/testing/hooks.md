---
type: Testing Guidance
description: Test guidance for repo-local Copilot plus installed Copilot and Gemini hooks under `.github/hooks/`, `.copilot/hooks/`, and `.gemini/hooks/`.
---

# Hooks - Testing

## Repo checks

- After changing hook source, run `./scripts/install.sh` before any live validation because installed hooks execute from `~/.copilot/hooks` or `~/.gemini/hooks`, not from repo source paths.
- Centralize standard test environment helper utilities (such as `install_into_temp_home()`) in `scripts/test-common.sh` instead of duplicating them across individual test files.
- Read official hook docs before non-trivial changes and keep implementation aligned with them.
- The retained supported hook surface is Python-first; validate the Python entrypoints and installed copies rather than the retired shell format surface.
- Copilot hook checks:
  - `bash scripts/test-hooks-auto-ingest.sh`
  - `bash scripts/test-hooks-startup.sh`
  - `bash scripts/test-hooks-observability.sh`
  - `bash scripts/test-hooks-secrets-scanner.sh`
  - `bash scripts/test-hooks-tool-guard.sh`
  - `bash scripts/test-hooks-rtk.sh`
- Gemini hook checks:
  - `bash scripts/test-gemini-hooks-auto-ingest.sh`
  - `bash scripts/test-gemini-hooks-startup.sh`
  - `bash scripts/test-gemini-hooks-secrets-scanner.sh`
  - `bash scripts/test-gemini-hooks-tool-guard.sh`
  - `bash scripts/test-gemini-hooks-rtk.sh`
- `scripts/test-gemini-hooks-startup.sh` includes a negative missing-skill case that intentionally prints `Hook hard stop: Required skill file not found...`; trust the script exit status and assertions, not stderr alone.
- Gemini repo config should use workspace-relative Python commands in `.gemini/settings.json`, including `python .gemini/hooks/scripts/auto-ingest.py` and `python .gemini/hooks/scripts/inject-auto-ingest-context.py`; installed global settings continue to use quoted `$HOME/.gemini/hooks/scripts/...` paths. Validate both forms through the Gemini hook regressions.
- **Dynamic-Cleanup traps:** When writing bash function-level traps under `set -u` (nounset), register local cleanup variables using single-quotes inside double-quotes (e.g. `trap 'rm -rf "'"$workdir"'"' RETURN`). This interpolates the variable at trap registration time, preventing unbound variable errors when the function exits and pops local scope before execution.

## Live evidence

- Copilot CLI: verify installed behavior from `~/.copilot/hooks/logs/observability.ndjson` or direct installed-script smoke tests.
- VS Code Copilot: inspect `GitHub Copilot Chat Hooks.log` and `GitHub Copilot Chat.log` for returned hook JSON and applied context.
- If VS Code omits `SubagentStart` for `runSubagent` child sessions, verify the direct `SubagentStart` hook is installed and use `SessionStart` as the fallback evidence.
- `scripts/test-hooks-observability.sh` exercises installed Copilot hook copies and validates `send-event.py`, `hook_execution`, `event_capture`, `rollup`, lock-wait fail-open behavior, redaction/capping, log rotation, and the observability kill-switch against `$HOME/.copilot/hooks/logs/observability.ndjson`; it also keeps stdin open after sending compact or multiline JSON and requires the emitter to exit promptly while rejecting already-buffered trailing junk.
- `scripts/test-gemini-hooks-observability.sh` exercises installed Gemini hook copies and validates `send-event.py`, `hook_execution`, `event_capture`, `rollup`, lock-wait fail-open behavior, redaction/capping, log rotation, and the observability kill-switch against `$HOME/.gemini/hooks/logs/observability.ndjson`; it also keeps stdin open after sending compact or multiline JSON and requires the emitter to exit promptly while rejecting already-buffered trailing junk.
- The observability suites also verify owner-only primary/shadow audit logs and that a zero-byte maximum disables active-log rotation without skipping stale-backup pruning.
- The Copilot secret-scanner suite verifies that malformed input, unexpected exceptions, and real block-mode findings emit runtime-specific deny decisions with exit `0`, while warn mode remains a JSON no-op.
- Both secret-scanner suites prepend stalling POSIX `git` and Windows `git.cmd` shims to `PATH`. They verify the public hook stdin/stdout path returns JSON within 8 seconds in warn mode and emits a deny decision in block mode, covering bounded, fail-closed Windows Git-probe behavior.
- `scripts/test-hooks-startup.sh` and `scripts/test-hooks-rtk.sh` must assert both `bash` and exact `powershell` command paths for Copilot hook registrations so Windows path regressions fail fast.
- `scripts/test-hooks-auto-ingest.sh` covers new-source scaffolding, the hard-coded ingest workflow text, repo-local Copilot `userPromptTransformed` prompt rewriting, stale-summary detection, rename orphans, deleted-source cleanup prompts, and committed manifest updates.
- `scripts/test-hooks-auto-ingest.sh` and `scripts/test-gemini-hooks-auto-ingest.sh` also cover the pending-ingest gate, the `/ingest-source` recovery checklist when the skill is missing, and the Copilot/Gemini final-response backstop.
- Both auto-ingest suites verify exact generated OKF draft-summary frontmatter, treat semantically equivalent quoted/commented draft scalars as pending, ignore draft-marker text outside frontmatter, and cover quoted/URI-encoded resources for nested source paths containing spaces, `#`, and `?`.
- `scripts/test-gemini-hooks-auto-ingest.sh` covers Gemini startup scanning plus `BeforeAgent` prompt-time context injection, including new-source scaffolding, stale-summary detection, rename orphans, deleted-source cleanup prompts, committed manifest updates, manifest summary-path sanitization, the startup fallback when the Gemini payload omits `cwd`, and the `AfterAgent` pending-ingest deny path.
- `scripts/test-hooks-startup.sh` now also verifies the repo-local `.github/hooks/hooks.json` startup, prompt-time, and final-response auto-ingest registrations while confirming `.copilot/hooks/hooks.json` no longer owns any auto-ingest wiring.
- After changing the Copilot prompt-time injector or its hook ordering, run a direct smoke test against `.github/hooks/scripts/inject-auto-ingest-context.py`; repo-source tests alone do not prove the repo-local CLI surface.
- `scripts/test-install.sh` verifies `.gemini/global-settings.json` is copied into `~/.gemini/settings.json` during install.
- When benchmarking the Gemini Tool Guardian port, measure the installed shell-command path after `./scripts/install.sh`; direct repo invocation is slower and can miss the `<40ms` target even when the installed surface passes.
- Hook event compatibility contract lives in `.agents/instructions/hooks.md`.

## Python unit tests

- Run Python unit tests with:
  `python scripts/test_helpers.py`
- These tests verify helper functions (`convert_windows_path_to_posix`, `emit_json` Unicode encoding, path-merging, frontmatter stripping, logs sanitization, `.github` audit timeout and rotation behavior, and observability UTF-8 fast-path capping parity) across `.github`, `.gemini`, and `.copilot` script hook structures.
- **Module Caching / Isolation Solution:** Because Python caches modules in `sys.modules` and mutating `sys.path` globally can leak paths and pollute the search space, use the `_get_common_module()` helper pattern. This helper leverages `importlib.util.spec_from_file_location` and `importlib.util.module_from_spec` to dynamically execute and load each module as a cleanly isolated module object from its absolute/relative path without global pollution or caching side effects.
- **Unicode Stdout Mocking:** Testing stdout stream reconfiguration (e.g. `sys.stdout.reconfigure(encoding="utf-8")`) under unit tests requires mocking `sys.stdout` using `io.TextIOWrapper` wrapped around an underlying `io.BytesIO` stream (emulating a default Windows shell like `cp1252`). This guarantees the `reconfigure` method is available and executed, allowing you to flush and verify the decoded UTF-8 bytes without silent `AttributeError` suppressions.
