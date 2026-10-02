---
type: Agent Memory
description: Public validation entry points and provider adapter contracts for the repository
---

# API Map

## Codex custom-agent installer

- `scripts/install-codex-agents.py --source-dir PATH --destination-dir PATH` converts valid top-level canonical agent Markdown into personal Codex TOML. It owns only TOML paths listed in `.skills-repo-agents.json`, removes stale manifest-owned output, and preserves unmanaged personal agents. It reports a concise install/update/unchanged/removal summary on stdout; status and failures use stderr. Exit `0` is success, `1` is a validation or installation failure, and argparse usage failures use `2`.
- `scripts/install.sh` and `scripts/install.ps1` call this converter before their existing provider copies. They choose `${CODEX_HOME:-$HOME/.codex}/agents` (Bash) or `$env:CODEX_HOME/agents` with `$HOME/.codex/agents` as the PowerShell fallback.

## Copilot and Gemini configuration installer

- `scripts/install-provider-hooks.py --provider copilot|gemini --template PATH --destination PATH --home PATH [--check]` merges current source settings and managed hook handlers with existing user configuration. Unrelated settings and hook handlers remain, including exact old repository-state registrations absent from the source. A fresh destination receives only template entries. `--check` validates both inputs and the proposed merge without writing; invalid, duplicate-key, or structurally ambiguous JSON and linked parent directories exit `1` before either installer mutates the home.
- Both installers run the Copilot and Gemini checks before Codex-agent conversion or asset copying, then write owner-only merged JSON. Changed existing files receive a `.bak` copy of their immediately previous bytes. An unchanged owner-only, singly linked file is untouched; a hard-linked or loose-mode file is atomically replaced with identical owner-only bytes without changing its other links or churning the backup.

## Repository test runner

- `scripts/test-all.py [-h|--help] [--list]` runs every explicitly registered maintained suite with no arguments. Help and command listing use stdout without checking suite dependencies. Unknown or abbreviated flags fail with usage on stderr. The script resolves its checkout from its own location and runs suites there regardless of the caller's current directory.
- Suites run sequentially with inherited stdout/stderr and EOF on stdin. The runner never consumes caller input. Progress, individual child failure codes, and the final suite summary use plain stderr. Host-specific skips remain in suite output; a successful suite status does not assert that every individual platform-specific test ran.
- Exit `0` means successful suites, `1` means suite failures, `2` means usage/dependency/runner errors, `130` means SIGINT, `143` means SIGTERM, and `141` means the runner encountered a broken pipe. Ordinary child failures, including broken pipes, do not stop later suites. Required dependencies and suite paths are checked before execution; see [Testing Strategy](TESTING_STRATEGY.md) for prerequisites.
- There is no default suite timeout. Cancellation signals the active child's process group, waits up to five seconds for cleanup, then sends SIGKILL. A repeated interrupt forces termination. PowerShell version preflight has a separate five-second timeout and participates in the same cancellation handling.

## Generated provider-hook CLI

- `scripts/generate-hooks.py --write` renders the complete explicit `hooks/manifest.py` target set and transactionally updates only stale generated outputs. `--check` is read-only, reports every stale or missing output, and exits `0` only when source bytes and executable modes are current. Both actions resolve the checkout from the script location; bare invocation and invalid canonical inputs exit `2`.
- The generator owns 29 executable outputs under `.copilot/hooks/scripts/`, `.gemini/hooks/scripts/`, `.github/hooks/scripts/`, and `.codex/hooks/`. They carry a `Generated from hooks/families/...` header and are copied unchanged by both installers. Tool Guardian imports its identical policy helper from its own provider tree; no runtime import crosses provider trees. Before any destination mutation, each installer runs bytecode-disabled `scripts/generate-hooks.py --check`: stale output exits `1` with the exact `--write` recovery command, and invalid canonical input exits `2` without write advice.
- The generated `tool-guard.py` hooks return provider-native block or warning JSON with up to three distinct static rule causes, an omitted count, and one redacted, at-most-160-character `Action:` excerpt. Input-limit causes carry rule ID, threshold, measured count, true unit, and a known provider field only when safely identified. Quoted CLI credentials and JSON credential fields are redacted before truncation. Their owner-only guard records keep the same safe rule metadata and exact displayed excerpt, never raw tool input. Input limits and known inspection failures deny even in warn mode and never advise the allowlist.
- The generated `scan-secrets.py` hooks read provider JSON from stdin and return JSON with exit `0`. An incomplete Git scan emits a provider-native denial in block mode or a `scan-secrets warning` naming the scan action in warn mode. They never mark incomplete output clean or expose raw Git output in the response.
- Codex `Stop` scanner success uses `systemMessage` with the count of modified files inspected; a skipped scan says `skipped`. Its `PreToolUse` pass stays `{}`. Copilot and Gemini scanner success at tool or SessionEnd events stays `{}`; their existing warning and denial fields carry actionable results.

## High-rate hook benchmark

- `scripts/benchmark-high-rate-hooks.py [--samples N] [--warmups N] [--concurrency N] [--output PATH] [--guard-only] [--script-root PATH] [--expected-behavior baseline|candidate]` runs direct macOS JSON subprocess workloads against retained Copilot, Gemini, and Codex high-rate handlers. Defaults are 25 warm samples, three discarded warmups, four concurrent calls, the current checkout, and candidate decisions. Ordinary multi-hook mode requires RTK on `PATH`; `--guard-only` permits missing RTK. It creates disposable Git repositories and homes, verifies expected decisions, and emits JSON with environment, input sizes, raw samples, first-call timing, warm median/p95/MAD/min/max, and one concurrent batch per selected handler. `--guard-only` selects the shared guardian corpus; `--script-root` can select an immutable baseline whose known observations are checked by `--expected-behavior baseline`. Source fingerprints come from the retained external measurement drivers/manifests. It does not install hooks or measure provider dispatch.

## Tool Guardian input policy

These are observed accepted shapes, not complete provider schemas. Native classification requires exact tool spelling, required fields, allowed optional fields, and exact value types. Unless specified below, every field is a string and no additional field is accepted. Unrecognized aliases, malformed shapes, extra fields, and invalid patches retain strict inspection of values, keys, and serialized input.

| Provider | Tool | Required fields | Optional fields |
| --- | --- | --- | --- |
| Codex | `Bash` | `command` | None |
| Codex | `exec_command`, `functions.exec_command` | `cmd` | None |
| Codex | `apply_patch` | `command` containing a recognized patch | None |
| Copilot | `bash` | `command` | None |
| Copilot | `create` | `path`, `file_text` | None |
| Copilot | `edit` | `path`, `old_str`, `new_str` | None |
| Copilot | `grep` | Exactly one of `pattern`, `query` | `path`; `paths` string or list of strings; `output_mode`; `head_limit`, `C` integers; `n` boolean or integer; `case_sensitive` boolean |
| Copilot | `rg` | `pattern` | `paths` string or list of strings; `output_mode`, `glob`; `head_limit`, `-A`, `-C`, `n` integers; `-n`, `-i` booleans |
| Gemini | `run_shell_command` | `command` | None |
| Gemini | `write_file` | `file_path`, `content` | None |
| Gemini | `replace` | `file_path`, `instruction`, `old_string`, `new_string` | `allow_multiple` boolean |
| Gemini | `grep_search` | `pattern` | `path`, `include` |

Copilot `grep` cannot combine `path` with `paths`. Native file bodies, edit text, search strings, and valid patch hunks are data. Patch delete and move-source headers retain existing environment-file and Git-metadata removal checks; the exemption grants no general destination protection or later saved-script inspection.

Known shell inputs use bounded quote, substitution, redirection, heredoc, and command parsing. Only proven literal search and narrow Python writer/survey forms receive data treatment. Shell/Python execution sinks remain inspected, including through wrappers, interpreter flags, quoted command names, and nested operands. Unknown syntax stays strict; unresolved or malformed inspection denies even in warn mode and with an allowlist. Python parsing is lazy, and shared command helpers import `subprocess` only when called. The reused shell representation preserves raw provenance; linear suffix scans and the ASCII tool-name sanitizer gate preserve rule and redaction semantics. The normalized identifier gate excludes credential-token prefixes and keeps the existing name clipping.

| Inspection budget | Maximum |
| --- | --- |
| Validated native data, metadata, and dictionary keys combined | 65,536 UTF-8 bytes |
| Unsupported structured strings, strict text, normalized text, and aggregate executable source | 32,768 bytes; strict/normalized text also capped at 32,768 characters |
| Structured depth / nodes / strings | 32 levels / 256 nodes / 128 strings |
| Nested executable depth / aggregate commands / aggregate tokens | 16 levels / 128 commands / 256 tokens |
| Python preflight nesting / tokens | 32 levels / 1,024 tokens |
| Python AST depth / nodes | 32 levels / 2,048 nodes |
| Python string/bytes constants combined and each resolved concatenation | 32,768 bytes, UTF-8 for strings |
| Normalized patch-operation paths combined | 32,768 UTF-8 bytes |

Native shell inputs use the tighter executable bound. Strict fallback adds the tool-name prefix before text scanning; limits and their reported units can therefore differ from a native body limit. Earlier budgets can dominate later ones. These are inspection bounds after JSON decoding, not universal raw-envelope memory limits. Missing or corrupt provider-local policy helpers fail closed in both block and warn modes.

## Tool Guardian benchmark tools

- `scripts/benchmark-tool-guard-resources.py --output PATH --ceiling-ms N [--script-root PATH] [--samples N] [--warmups N]` measures bounded native, strict, normalized, shell, and Python cases on native macOS. The root defaults to the checkout; samples/warmups default to 25/3, with at least five samples. It checks provider decisions and unchanged source fingerprints, reports first and sampled direct-process timing, and collects RSS in a separate `/usr/bin/time -l` launch. RSS is in bytes on macOS; the timing excludes that wrapper. Exit `1` means at least one case exceeded the supplied ceiling.
- `scripts/benchmark-tool-guard-optimizations.py PHASE [--root PATH] [--variant-parent PATH] [--evidence PATH] [--group common|suffix]` exposes `prepare`, `validate`, `measure`, `compare`, `prepare-git`, `validate-git`, and `measure-git`. It freezes isolated ablation variants, validates their public decisions, and measures alternating before/after whole-hook conditions. `prepare` replaces inline matcher functions and cannot use today's extracted entrypoints: replay with a disposable worktree at `84eae394`, invoking the helper from the topic checkout with `--root` pointing there and fresh variant/evidence directories, as documented in [optimization validation notes](../../docs/tool-guardian-tuning/optimization-validation-notes.md). `compare` reports per-case benefits, regressions, or inconclusive results against measured variation. Those optional diagnostics do not certify every optimization as beneficial or replace the acceptance matrix.

## Lifecycle message envelopes

- Copilot required-skill and repository startup hooks emit a single progress object before their final JSON. The repository `validate-stop.py` coordinator emits progress for an allowed pass or notice and prefixes its native block reason on denial; no extra stop coordinator is installed.
- Gemini startup and `AfterAgent` operational hooks, and Codex startup and `Stop` operational hooks, use `systemMessage` for allowed pass, retry, or incomplete outcomes. A denial uses `reason` or `stopReason` without a duplicate `systemMessage`. Safe counts identify skill files, pending sources, diagnostics, checks, or modified files. Observability-only events and successful high-rate tool checks remain silent.

## Installed hook delivery probe

- `scripts/probe-provider-hook-delivery.py prepare --provider copilot|gemini|codex [--mode normal|timeout]` installs only nonce-tagged temporary handlers and prints exact backup, marker, and transcript paths. `verify --provider NAME --id ID --transcript PATH [--mode timeout]` checks invocation, valid response, native visible feedback, and timeout indication where required. Normal verification pairs timestamped entry/completion records by event and invocation ID and prints entry-to-completion milliseconds; these do not measure provider startup-to-entry. `cleanup --provider NAME --id ID` removes only probe-owned state and restores or merges existing hook settings. Always cleanup after a failed verify.
- For Copilot CLI, the probe emits one progress JSON line containing the nonce before its one final provider-valid JSON object. Its normal verification requires visible nonces for `preToolUse`, `postToolUse`, and `agentStop`. A timeout verify requires an observed timeout message as well as entry markers and no completion markers; a silent fail-open timeout fails verification even if the tool runs.

## Stable RTK configuration

- `scripts/configure-rtk.py [--home PATH] [--platform darwin|linux|win32] [--check]` requires RTK 0.50.0 or newer on `PATH`. `--check` validates without writes; default mode creates or updates only `[hooks] suppress_hook_warning = true` in platform RTK TOML. An existing changed file gets an owner-only `.toml.bak`; an unchanged file stays byte-identical. Invalid, ambiguous, or linked destinations exit `1` with stderr guidance. Default mode also removes only exact-hash installed prerelease adapters and launchers, plus a receipt-verified prerelease bundle; modified files are reported for manual review.
- Both installers call `--check` before any installed-file mutation and apply the configuration after generator freshness succeeds. They do not download RTK. Copilot and Gemini automatic forwarders remain; Codex uses explicit RTK commands.

## OKF validation

- `scripts/lint-okf.py [--format human|json]` validates both canonical document bundles. Human diagnostics use `path:line:column: ID message`; JSON uses schema version `1` with exact `id`, `path`, `line`, `column`, and `message` fields. Exit `0` is clean, `1` reports profile findings, and `2` reports an untrustworthy `OKF900` result.
- `.github/hooks/scripts/validate-stop.py` is the registered Copilot `agentStop` and `subagentStop` entry point. It reads one complete JSON mapping without waiting for stdin EOF, runs source ingest first and OKF second, and combines bounded blocking reasons. It preserves a visible OKF warning on an allowed retry or incomplete check. OKF has no registered `postToolUse` invocation.
- `.github/hooks/scripts/lint-okf.py` reads one complete Copilot payload without waiting for stdin EOF and emits one UTF-8 JSON object with exit `0`. Clean stop returns `decision: allow`; definite findings block once, then allow with a reason when `stop_hook_active`; infrastructure failure allows with an `OKF900` reason. The independent source-ingest validator retains its own blocking behavior.
- `.gemini/hooks/scripts/lint-okf.py` is registered only for project `AfterAgent`. Clean validation emits `systemMessage: lint-okf: pass; 0 diagnostics`; definite findings emit `decision: deny` with a reason once, then `continue: true` with a visible `systemMessage`; an incomplete `AfterAgent` check emits a visible `OKF900` warning and permits completion. Source ingest runs first in the sequential group.
- `.codex/hooks.json` registers only project-local `Stop` with `.codex/hooks/repository-okf.py`; the user-global `.codex/global-hooks.json` does not own it. Clean validation emits `systemMessage: repository-okf: pass; 0 diagnostics`, definite findings block once, a retry emits `systemMessage`, and incomplete checks emit an `OKF900` `systemMessage`.
- All three adapters execute only the central linter from their containing checkout, accept nested payload working directories within that checkout, reject external working directories as `OKF900`, and keep serialized output below 8 KiB with at most 20 displayed diagnostics. Their provider-local audit helpers write content-free, deduplicated `audit.log` entries capped at 4 KiB; a retry is a distinct attempt.
