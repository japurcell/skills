---
type: Agent Memory
description: Public validation entry points and provider adapter contracts for the repository
---

# API Map

## Repository test runner

- `scripts/test-all.py [-h|--help] [--list]` runs every explicitly registered maintained suite with no arguments. Help and command listing use stdout without checking suite dependencies. Unknown or abbreviated flags fail with usage on stderr. The script resolves its checkout from its own location and runs suites there regardless of the caller's current directory.
- Suites run sequentially with inherited stdout/stderr and EOF on stdin. The runner never consumes caller input. Progress, individual child failure codes, and the final suite summary use plain stderr. Host-specific skips remain in suite output; a successful suite status does not assert that every individual platform-specific test ran.
- Exit `0` means successful suites, `1` means suite failures, `2` means usage/dependency/runner errors, `130` means SIGINT, `143` means SIGTERM, and `141` means the runner encountered a broken pipe. Ordinary child failures, including broken pipes, do not stop later suites. Required dependencies and suite paths are checked before execution; see [Testing Strategy](TESTING_STRATEGY.md) for prerequisites.
- There is no default suite timeout. Cancellation signals the active child's process group, waits up to five seconds for cleanup, then sends SIGKILL. A repeated interrupt forces termination. PowerShell version preflight has a separate five-second timeout and participates in the same cancellation handling.

## OKF validation

- `scripts/lint-okf.py [--format human|json]` validates both canonical document bundles. Human diagnostics use `path:line:column: ID message`; JSON uses schema version `1` with exact `id`, `path`, `line`, `column`, and `message` fields. Exit `0` is clean, `1` reports profile findings, and `2` reports an untrustworthy `OKF900` result.
- `.github/hooks/scripts/validate-stop.py` is the registered Copilot `agentStop` and `subagentStop` entry point. It reads one complete JSON mapping without waiting for stdin EOF, passes one compact serialization to the source-ingest validator and then the OKF adapter, preserves both validators as separate processes, and emits one UTF-8 `decision: block` response with recognizable source-ingest and OKF reason prefixes in that order. The complete serialized response stays below 8 KiB even when both child reasons require truncation. It emits `decision: allow` only when both validators allow the stop.
- `.github/hooks/scripts/lint-okf.py` reads one complete Copilot hook payload without waiting for stdin EOF and emits one UTF-8 JSON object with exit `0`. Clean post-tool events emit `{}`, invalid post-tool events emit `additionalContext`, clean stop events emit `decision: allow`, and invalid stop events emit `decision: block` plus `reason`. Every failure reason reports the number of omitted diagnostics, including central-linter execution failures and inconsistent exit statuses. The stop coordinator consumes its stop response; `postToolUse` remains registered directly.
- `.gemini/hooks/scripts/lint-okf.py` reads one Gemini hook payload from stdin and emits one JSON object with exit `0`. Clean events emit `{}`, invalid `AfterTool` and first-pass `AfterAgent` events emit `decision: deny` plus `reason`, and an invalid retry with `stop_hook_active` emits `continue: false` plus `stopReason`.
- Both adapters execute only the central linter from their containing checkout, accept nested payload working directories within that checkout, reject external working directories as `OKF900`, and keep serialized output below 8 KiB with at most 20 displayed diagnostics.
