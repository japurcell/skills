---
type: Agent Memory
description: Public validation entry points and provider adapter contracts for the repository
---

# API Map

## OKF validation

- `scripts/lint-okf.py [--format human|json]` validates both canonical document bundles. Human diagnostics use `path:line:column: ID message`; JSON uses schema version `1` with exact `id`, `path`, `line`, `column`, and `message` fields. Exit `0` is clean, `1` reports profile findings, and `2` reports an untrustworthy `OKF900` result.
- `.github/hooks/scripts/lint-okf.py` reads one Copilot hook payload from stdin and emits one JSON object with exit `0`. Clean post-tool events emit `{}`, invalid post-tool events emit `additionalContext`, clean stop events emit `decision: allow`, and invalid `agentStop` or `subagentStop` events emit `decision: block` plus `reason`.
- `.gemini/hooks/scripts/lint-okf.py` reads one Gemini hook payload from stdin and emits one JSON object with exit `0`. Clean events emit `{}`, invalid `AfterTool` and first-pass `AfterAgent` events emit `decision: deny` plus `reason`, and an invalid retry with `stop_hook_active` emits `continue: false` plus `stopReason`.
- Both adapters execute only the central linter from their containing checkout, accept nested payload working directories within that checkout, reject external working directories as `OKF900`, and keep serialized output below 8 KiB with at most 20 displayed diagnostics.
