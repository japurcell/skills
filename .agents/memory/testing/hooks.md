---
type: Testing Guidance
description: Test routes for Codex, Copilot, and Gemini hook sources and installed copies
---

# Hooks - Testing

## Repo checks

- After changing hook source, run `./scripts/install.sh` before any live validation because installed hooks execute from `~/.codex/hooks`, `~/.copilot/hooks`, or `~/.gemini/hooks`, not from repo source paths.
- Centralize standard test environment helper utilities (such as `install_into_temp_home()`) in `scripts/test-common.sh` instead of duplicating them across individual test files.
- Read official hook docs before non-trivial changes and keep implementation aligned with them.
- The retained supported hook surface is Python-first; validate the Python entrypoints and installed copies rather than the retired shell format surface.
- Copilot hook checks:
  - `bash scripts/test-hooks-okf-lint.sh`
  - `bash scripts/test-hooks-auto-ingest.sh`
  - `bash scripts/test-hooks-startup.sh`
  - `bash scripts/test-hooks-observability.sh`
  - `bash scripts/test-hooks-secrets-scanner.sh`
  - `bash scripts/test-hooks-tool-guard.sh`
  - `bash scripts/test-hooks-rtk.sh`
- Gemini hook checks:
  - `bash scripts/test-gemini-hooks-okf-lint.sh`
  - `bash scripts/test-gemini-hooks-auto-ingest.sh`
  - `bash scripts/test-gemini-hooks-startup.sh`
  - `bash scripts/test-gemini-hooks-secrets-scanner.sh`
  - `bash scripts/test-gemini-hooks-tool-guard.sh`
  - `bash scripts/test-gemini-hooks-rtk.sh`
- Codex hook checks:
  - `bash scripts/test-codex-hooks-startup.sh`
  - `bash scripts/test-install.sh`
  - `pwsh -NoProfile -File scripts/test-install.ps1` when PowerShell 7 is available
- Codex source remains inactive at `.codex/global-hooks.json`; fixture tests validate the user-global merge without writing to the real home directory. After a real install, review and trust the changed non-managed definition through `/hooks` before live validation.
- The Codex startup suite covers open-stdin completion and malformed-prefix time bounds, raw skill-file and final-context limits, large removable frontmatter, path containment, UTF-8 output, and POSIX audit-link defenses. Exercise PowerShell installer behavior and Windows audit reparse-point handling on a Windows host when available.
- `scripts/test-gemini-hooks-startup.sh` includes a negative missing-skill case that intentionally prints `Hook hard stop: Required skill file not found...`; trust the script exit status and assertions, not stderr alone.
- **Dynamic-Cleanup traps:** When writing bash function-level traps under `set -u` (nounset), register local cleanup variables using single-quotes inside double-quotes (e.g. `trap 'rm -rf "'"$workdir"'"' RETURN`). This interpolates the variable at trap registration time, preventing unbound variable errors when the function exits and pops local scope before execution.

For source auto-ingest behavior, read [Hook Auto-Ingest Testing](hooks-auto-ingest.md). Skip it for unrelated hooks. For observability, trace, transcript, audit-log, or maintenance behavior, read [Hook Observability Testing](hooks-observability.md). Skip it for operational hooks.

## Live evidence

- Copilot CLI: verify installed behavior from `~/.copilot/hooks/logs/observability.ndjson` or direct installed-script smoke tests.
- VS Code Copilot: inspect `GitHub Copilot Chat Hooks.log` and `GitHub Copilot Chat.log` for returned hook JSON and applied context.
- If VS Code omits `SubagentStart` for `runSubagent` child sessions, verify the direct `SubagentStart` hook is installed and use `SessionStart` as the fallback evidence.
- The Copilot secret-scanner suite verifies that malformed input, unexpected exceptions, and real block-mode findings emit runtime-specific deny decisions with exit `0`, while warn mode remains a JSON no-op.
- Both secret-scanner suites prepend stalling POSIX `git` and Windows `git.cmd` shims to `PATH`. They verify the public hook stdin/stdout path returns JSON within 8 seconds in warn mode and emits a deny decision in block mode, covering bounded, fail-closed Windows Git-probe behavior.
- `scripts/test-hooks-startup.sh` and `scripts/test-hooks-rtk.sh` must assert both `bash` and exact `powershell` command paths for Copilot hook registrations so Windows path regressions fail fast.
- `scripts/test-hooks-startup.sh` now also verifies the repo-local `.github/hooks/hooks.json` startup, prompt-time, and final-response auto-ingest registrations while confirming `.copilot/hooks/hooks.json` no longer owns any auto-ingest wiring.
- The two OKF adapter suites copy the adapters and valid two-bundle fixture into one checkout, exercise the public stdin/stdout seam, and cover central-diagnostic parity, real provider envelopes, missing or invalid dependencies, timeout/`OKF900` behavior, Windows rerun text, 20-item and serialized 8 KiB bounds, nested checkout paths, out-of-checkout decoy rejection, and simultaneous pending-ingest plus OKF failures. The Copilot suite invokes the registered stop-hook entry and requires one response containing both blocking reasons in source-ingest-first order.
- Registration assertions keep repository-specific OKF hooks out of `.copilot/hooks/hooks.json` and `.gemini/global-settings.json`. Copilot registers one final-response coordinator for each stop event, while Gemini preserves source-ingest-first command ordering. Both provider registrations retain their timeout units and mutation matchers.
- `scripts/test-install.sh` verifies `.gemini/global-settings.json` is copied into `~/.gemini/settings.json` during install.
- Hook event compatibility contract lives in `.agents/instructions/hooks.md`.
