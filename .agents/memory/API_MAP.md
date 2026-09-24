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
- The generator owns 38 executable outputs under `.copilot/hooks/scripts/`, `.gemini/hooks/scripts/`, `.github/hooks/scripts/`, and `.codex/hooks/`. They carry a `Generated from hooks/families/...` header, remain self-contained at runtime, and are copied unchanged by both installers. Before any destination mutation, each installer runs bytecode-disabled `scripts/generate-hooks.py --check`: stale output exits `1` with the exact `--write` recovery command, and invalid canonical input exits `2` without write advice.
- The generated `tool-guard.py` hooks return provider-native block or warning JSON with one redacted, at-most-160-character `Action:` excerpt. Quoted CLI credentials and JSON credential fields are redacted before truncation. Their owner-only guard records keep threat metadata and the exact displayed excerpt, never raw tool input.
- The generated `scan-secrets.py` hooks read provider JSON from stdin and return JSON with exit `0`. An incomplete Git scan emits a provider-native denial in block mode or a `scan-secrets warning` naming the scan action in warn mode. They never mark incomplete output clean or expose raw Git output in the response.

## Installed hook delivery probe

- `scripts/probe-provider-hook-delivery.py prepare --provider copilot|gemini|codex [--mode normal|timeout]` installs only nonce-tagged temporary handlers and prints exact backup, marker, and transcript paths. `verify --provider NAME --id ID --transcript PATH [--mode timeout]` checks invocation, valid response, native visible feedback, and timeout indication where required; `cleanup --provider NAME --id ID` removes only probe-owned state and restores or merges existing hook settings. Always cleanup after a failed verify.
- For Copilot CLI, the probe emits one progress JSON line containing the nonce before its one final provider-valid JSON object. Its normal verification requires visible nonces for `preToolUse`, `postToolUse`, and `agentStop`. A timeout verify requires an observed timeout message as well as entry markers and no completion markers; a silent fail-open timeout fails verification even if the tool runs.

## Repository-state protection

- Copilot's native `create` joins `edit` and `write` in the guarded editor-tool set. A `.git` target in its `file_path` or `path` input denies before file creation; ordinary workspace file creation still allows.
- Generated `repository-state.py` hooks at `.copilot/hooks/scripts/`, `.gemini/hooks/scripts/`, and `.codex/hooks/` accept provider-native pre-tool JSON and emit `{}` for unaffected calls. A denial uses Copilot `permissionDecision: deny`, Gemini `decision: deny`, or Codex `hookSpecificOutput.permissionDecision: deny`, all with exit `0` and a safe reason. Malformed input denies. No hook approval token is accepted.
- The canonical family checks workspace `.git`, its resolved Git directory, and the common Git directory. It denies direct editor writes, recognizable literal shell/script metadata writes including in-place `sed`, `perl`, `truncate`, and `install`, and Git checkout/restore/reset/clean variants that can discard work. Read-only Git commands and `git clean --dry-run` stay available. The hook cannot inspect operations hidden inside a later child process.

## Explicit RTK prerelease

- `scripts/install-rtk-prerelease.py [--home PATH] [--archive PATH] [--platform PLATFORM]` fetches or reads a tag-pinned archive, verifies its published SHA-256, and installs `rtk` or `rtk.exe` plus an integrity receipt under `HOME/.agents/rtk/dev-0.50.0-rc.451/`. Unsupported platforms and invalid archives exit `1` before installing a binary. It never replaces stable `rtk`.
- Generated `rtk-explicit-*.py` adapters accept provider-native pre-tool JSON and emit `{}` when the verified side-by-side binary is absent or shell syntax is unsafe. Safe rewrites use Copilot `modifiedArgs`, Gemini `hookSpecificOutput.tool_input`, or Codex `hookSpecificOutput.updatedInput` with `permissionDecision: allow`. The generated `rtk-agent-launcher.py` applies child-only warning suppression and passes through stdout, stderr, and exit status.

## Markdown health

- Generated `markdown-health.py` entry points take provider hook JSON on stdin and emit provider-native JSON on stdout. Their `MARKDOWN_HEALTH_EVENT` is `pre`, `post`, or `final`. State is keyed by provider session and resolved workspace root. Missing state, unreadable input, and checker failure report `incomplete` instead of a clean pass.
- `python3 ~/.<provider>/hooks/[scripts/]markdown-health.py --check PATH [PATH ...]` is the explicit, read-only rerun CLI from workspace root; exit `0` means no definite defect, `1` means definite findings, and `2` means incomplete or invalid input. Copilot and Gemini use the `scripts/` segment; Codex does not.

## OKF validation

- `scripts/lint-okf.py [--format human|json]` validates both canonical document bundles. Human diagnostics use `path:line:column: ID message`; JSON uses schema version `1` with exact `id`, `path`, `line`, `column`, and `message` fields. Exit `0` is clean, `1` reports profile findings, and `2` reports an untrustworthy `OKF900` result.
- `.github/hooks/scripts/validate-stop.py` is the registered Copilot `agentStop` and `subagentStop` entry point. It reads one complete JSON mapping without waiting for stdin EOF, passes one compact serialization to the source-ingest validator and then the OKF adapter, preserves both validators as separate processes, and emits one UTF-8 `decision: block` response with recognizable source-ingest and OKF reason prefixes in that order. The complete serialized response stays below 8 KiB even when both child reasons require truncation. It emits `decision: allow` only when both validators allow the stop.
- `.github/hooks/scripts/lint-okf.py` reads one complete Copilot hook payload without waiting for stdin EOF and emits one UTF-8 JSON object with exit `0`. Clean post-tool events emit `{}`, invalid post-tool events emit `additionalContext`, clean stop events emit `decision: allow`, and invalid stop events emit `decision: block` plus `reason`. Every failure reason reports the number of omitted diagnostics, including central-linter execution failures and inconsistent exit statuses. The stop coordinator consumes its stop response; `postToolUse` remains registered directly.
- `.gemini/hooks/scripts/lint-okf.py` reads one Gemini hook payload from stdin and emits one JSON object with exit `0`. Clean events emit `{}`, invalid `AfterTool` and first-pass `AfterAgent` events emit `decision: deny` plus `reason`, and an invalid retry with `stop_hook_active` emits `continue: false` plus `stopReason`.
- Both adapters execute only the central linter from their containing checkout, accept nested payload working directories within that checkout, reject external working directories as `OKF900`, and keep serialized output below 8 KiB with at most 20 displayed diagnostics.
