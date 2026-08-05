---
coverage: Test guidance for repo-local Copilot plus installed Copilot and Gemini hooks under `.github/hooks/`, `.copilot/hooks/`, and `.gemini/hooks/`.
---

# Hooks - Testing

## Repo checks

- After changing hook source, run `./scripts/install.sh` before any live validation because installed hooks execute from `~/.copilot/hooks` or `~/.gemini/hooks`, not from repo source paths.
- Read official hook docs before non-trivial changes and keep implementation aligned with them.
- The retained supported hook surface is Python-first; validate the Python entrypoints and installed copies rather than the retired shell format surface.
- Copilot hook checks:
  - `bash scripts/test-hooks-auto-ingest.sh`
  - `bash scripts/test-hooks-startup.sh`
  - `bash scripts/test-hooks-observability.sh`
  - `bash scripts/test-hooks-secrets-scanner.sh`
  - `bash scripts/test-hooks-tool-guard.sh`
- Gemini hook checks:
  - `bash scripts/test-gemini-hooks-auto-ingest.sh`
  - `bash scripts/test-gemini-hooks-startup.sh`
  - `bash scripts/test-gemini-hooks-secrets-scanner.sh`
  - `bash scripts/test-gemini-hooks-tool-guard.sh`
  - `bash scripts/test-gemini-hooks-rtk.sh`
- `scripts/test-gemini-hooks-startup.sh` includes a negative missing-skill case that intentionally prints `Hook hard stop: Required skill file not found...`; trust the script exit status and assertions, not stderr alone.
- Gemini config should point at the Python operational entrypoints in `.gemini/settings.json`; repo-local startup auto-ingest should use `$GEMINI_PROJECT_DIR/.gemini/hooks/scripts/auto-ingest.py`, while installed global settings continue to use `$HOME/.gemini/hooks/scripts/...` paths. Validate those paths through the Gemini hook regressions.

## Live evidence

- Copilot CLI: verify installed behavior from `~/.copilot/hooks/logs/observability.ndjson` or direct installed-script smoke tests.
- VS Code Copilot: inspect `GitHub Copilot Chat Hooks.log` and `GitHub Copilot Chat.log` for returned hook JSON and applied context.
- If VS Code omits `SubagentStart` for `runSubagent` child sessions, verify the direct `SubagentStart` hook is installed and use `SessionStart` as the fallback evidence.
- `scripts/test-hooks-observability.sh` exercises installed Copilot hook copies and validates `send-event.py`, `hook_execution`, `event_capture`, `rollup`, lock-wait fail-open behavior, redaction/capping, and the observability kill-switch against `$HOME/.copilot/hooks/logs/observability.ndjson`; use it after changing hook registrations because it runs against installed config, not repo source.
- `scripts/test-gemini-hooks-observability.sh` exercises installed Gemini hook copies and validates `send-event.py`, `hook_execution`, `event_capture`, `rollup`, lock-wait fail-open behavior, redaction/capping, and the observability kill-switch against `$HOME/.gemini/hooks/logs/observability.ndjson`; use it after changing hook registrations because it runs against installed config, not repo source.
- `scripts/test-hooks-auto-ingest.sh` and `scripts/test-gemini-hooks-auto-ingest.sh` cover new-source scaffolding, the hard-coded ingest prompt injection, stale-summary detection, rename orphans, deleted-source cleanup prompts, committed manifest updates, manifest summary-path sanitization, and the startup fallback when the Gemini payload omits `cwd`.
- `scripts/test-hooks-startup.sh` now also verifies the repo-local `.github/hooks/hooks.json` startup auto-ingest registration, the removal of auto-ingest from the global Copilot hooks file, and deletion of the legacy `.copilot/hooks/scripts/auto-ingest-source.py` plus its dead helper.
- `scripts/test-install.sh` verifies `.gemini/global-settings.json` is copied into `~/.gemini/settings.json` during install.
- When benchmarking the Gemini Tool Guardian port, measure the installed shell-command path after `./scripts/install.sh`; direct repo invocation is slower and can miss the `<40ms` target even when the installed surface passes.
- Hook event compatibility contract lives in `.agents/instructions/hooks.md`.
