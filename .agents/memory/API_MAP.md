---
type: Agent Memory
description: Public validation entry points and provider adapter contracts for the repository
---

# API Map

## OKF validation

- `scripts/lint-okf.py [--format human|json]` validates both canonical document bundles. Human diagnostics use `path:line:column: ID message`; JSON uses schema version `1` with exact `id`, `path`, `line`, `column`, and `message` fields. Exit `0` is clean, `1` reports profile findings, and `2` reports an untrustworthy `OKF900` result.
- `.github/hooks/scripts/validate-stop.py` is the registered Copilot `agentStop` and `subagentStop` entry point. It reads one complete JSON mapping without waiting for stdin EOF, passes one compact serialization to the source-ingest validator and then the OKF adapter, preserves both validators as separate processes, and emits one UTF-8 `decision: block` response with recognizable source-ingest and OKF reason prefixes in that order. The complete serialized response stays below 8 KiB even when both child reasons require truncation. It emits `decision: allow` only when both validators allow the stop.
- `.github/hooks/scripts/lint-okf.py` reads one complete Copilot hook payload without waiting for stdin EOF and emits one UTF-8 JSON object with exit `0`. Clean post-tool events emit `{}`, invalid post-tool events emit `additionalContext`, clean stop events emit `decision: allow`, and invalid stop events emit `decision: block` plus `reason`. Every failure reason reports the number of omitted diagnostics, including central-linter execution failures and inconsistent exit statuses. The stop coordinator consumes its stop response; `postToolUse` remains registered directly.
- `.gemini/hooks/scripts/lint-okf.py` reads one Gemini hook payload from stdin and emits one JSON object with exit `0`. Clean events emit `{}`, invalid `AfterTool` and first-pass `AfterAgent` events emit `decision: deny` plus `reason`, and an invalid retry with `stop_hook_active` emits `continue: false` plus `stopReason`.
- Both adapters execute only the central linter from their containing checkout, accept nested payload working directories within that checkout, reject external working directories as `OKF900`, and keep serialized output below 8 KiB with at most 20 displayed diagnostics.
