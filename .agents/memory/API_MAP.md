---
type: Agent Memory
description: Public validation entry points and provider adapter contracts for the repository
---

# API Map

## Codex custom-agent installer

- `scripts/install-codex-agents.py --source-dir PATH --destination-dir PATH` converts valid top-level canonical agent Markdown into personal Codex TOML. It owns only TOML paths listed in `.skills-repo-agents.json`, removes stale manifest-owned output, and preserves unmanaged personal agents. It reports a concise install/update/unchanged/removal summary on stdout; status and failures use stderr. Exit `0` is success, `1` is a validation or installation failure, and argparse usage failures use `2`.
- `scripts/install.sh` and `scripts/install.ps1` call this converter before their existing provider copies. They choose `${CODEX_HOME:-$HOME/.codex}/agents` (Bash) or `$env:CODEX_HOME/agents` with `$HOME/.codex/agents` as the PowerShell fallback.

## Repository test runner

- `scripts/test-all.py [-h|--help] [--list]` runs every explicitly registered maintained suite with no arguments. Help and command listing use stdout without checking suite dependencies. Unknown or abbreviated flags fail with usage on stderr. The script resolves its checkout from its own location and runs suites there regardless of the caller's current directory.
- Suites run sequentially with inherited stdout/stderr and EOF on stdin. The runner never consumes caller input. Progress, individual child failure codes, and the final suite summary use plain stderr. Host-specific skips remain in suite output; a successful suite status does not assert that every individual platform-specific test ran.
- Exit `0` means successful suites, `1` means suite failures, `2` means usage/dependency/runner errors, `130` means SIGINT, `143` means SIGTERM, and `141` means the runner encountered a broken pipe. Ordinary child failures, including broken pipes, do not stop later suites. Required dependencies and suite paths are checked before execution; see [Testing Strategy](TESTING_STRATEGY.md) for prerequisites.
- There is no default suite timeout. Cancellation signals the active child's process group, waits up to five seconds for cleanup, then sends SIGKILL. A repeated interrupt forces termination. PowerShell version preflight has a separate five-second timeout and participates in the same cancellation handling.

## Generated provider-hook CLI

- `scripts/generate-hooks.py --write` renders the complete explicit `hooks/manifest.py` target set and transactionally updates only stale generated outputs. `--check` is read-only, reports every stale or missing output, and exits `0` only when source bytes and executable modes are current. Both actions resolve the checkout from the script location; bare invocation and invalid canonical inputs exit `2`.
- The generator owns 25 executable outputs under `.copilot/hooks/scripts/`, `.gemini/hooks/scripts/`, `.codex/hooks/`, and `.github/hooks/scripts/`. They carry a `Generated from hooks/families/...` header, remain self-contained at runtime, and are copied unchanged by both installers. Before any destination mutation, each installer runs bytecode-disabled `scripts/generate-hooks.py --check`: stale output exits `1` with the exact `--write` recovery command, and invalid canonical input exits `2` without write advice.
- The generated `scan-secrets.py` hooks read provider JSON from stdin and return JSON with exit `0`. An incomplete Git scan emits a provider-native denial in block mode or a `scan-secrets warning` naming the scan action in warn mode. They never mark incomplete output clean or expose raw Git output in the response.

## OKF validation

- `scripts/lint-okf.py [--format human|json]` validates both canonical document bundles. Human diagnostics use `path:line:column: ID message`; JSON uses schema version `1` with exact `id`, `path`, `line`, `column`, and `message` fields. Exit `0` is clean, `1` reports profile findings, and `2` reports an untrustworthy `OKF900` result.
- `.github/hooks/scripts/validate-stop.py` is the registered Copilot `agentStop` and `subagentStop` entry point. It reads one complete JSON mapping without waiting for stdin EOF, passes one compact serialization to the source-ingest validator and then the OKF adapter, preserves both validators as separate processes, and emits one UTF-8 `decision: block` response with recognizable source-ingest and OKF reason prefixes in that order. The complete serialized response stays below 8 KiB even when both child reasons require truncation. It emits `decision: allow` only when both validators allow the stop.
- `.github/hooks/scripts/lint-okf.py` reads one complete Copilot hook payload without waiting for stdin EOF and emits one UTF-8 JSON object with exit `0`. Clean post-tool events emit `{}`, invalid post-tool events emit `additionalContext`, clean stop events emit `decision: allow`, and invalid stop events emit `decision: block` plus `reason`. Every failure reason reports the number of omitted diagnostics, including central-linter execution failures and inconsistent exit statuses. The stop coordinator consumes its stop response; `postToolUse` remains registered directly.
- `.gemini/hooks/scripts/lint-okf.py` reads one Gemini hook payload from stdin and emits one JSON object with exit `0`. Clean events emit `{}`, invalid `AfterTool` and first-pass `AfterAgent` events emit `decision: deny` plus `reason`, and an invalid retry with `stop_hook_active` emits `continue: false` plus `stopReason`.
- Both adapters execute only the central linter from their containing checkout, accept nested payload working directories within that checkout, reject external working directories as `OKF900`, and keep serialized output below 8 KiB with at most 20 displayed diagnostics.
