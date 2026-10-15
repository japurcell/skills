# T2: Exact Guardian shell option profiles

Implemented on 2026-10-14 in the isolated `codex/hook-resilience-t2` branch, based on `3976fccc`. This is source-level generated-entrypoint evidence. No live installation, authenticated provider dispatch, native Windows execution, resource benchmark, or composed T1/T2 acceptance is claimed.

## Public reproduction and red/green proof

With `command = "rg '" + "example;" * 130 + "' docs"`, the generated Codex Guardian allowed `exec_command` arguments containing only `cmd`. Adding `max_output_tokens: 1000` denied with `input_limits/command_segments`, measured at least 129 segments against 128. The literal semicolons are search data.

The new public `NativeDataTests.test_codex_output_metadata_preserves_literal_search_decision` failed six subcases before repair. After repair, both exact names, `exec_command` and `functions.exec_command`, allow the literal search with independently added output/yield metadata and deny the paired forced-push command. The full-profile test then failed on optional execution and annotation fields before its corresponding implementation and passed afterward.

## Accepted profiles and evidence basis

These are exact provider/tool profiles, not fuzzy aliases or a universal tool schema:

| Provider / tool profile | Recognized arguments |
| --- | --- |
| Codex `exec_command`, `functions.exec_command` | Required `cmd: str`; optional `max_output_tokens: int`, `yield_time_ms: int`, `workdir: str`, `shell: str`, `login: bool`, `tty: bool`, `justification: str`, `sandbox_permissions: str`, `prefix_rule: list[str]` |
| Codex legacy `Bash` | Sole `command: str`, preserving the existing compatibility contract |
| Copilot native `bash` | Required `command: str`; optional `description: str`, `initial_wait: int`, `mode: str`, `detach: bool` |
| Gemini `run_shell_command` | Required `command: str`; optional `description: str`, `dir_path: str`, `is_background: bool`, `delay_ms: int`, `additional_permissions: dict` |

The current Codex `exec_command` tool definition exposed to this task provides its argument names and types. Copilot's retained raw [hook input reference](../../.agents/sources/copilot-hooks-ref.md) establishes `toolName`/`toolArgs`, `sessionId`, timestamp and cwd fields; the [maintainer-filed VS Code reproduction](https://github.com/microsoft/vscode/issues/331027) independently demonstrates the Copilot `bash` `mode`, `detach`, and `initial_wait` combination. The locally installed Copilot binary is version 1.0.97, but no authenticated invocation or complete runtime schema extraction was performed. The recognized Copilot profile remains a bounded supported subset rather than a claim that future or unobserved options are inert.

Gemini's official [shell interface](https://github.com/google-gemini/gemini-cli/blob/main/packages/core/src/tools/shell.ts) and [dynamic shell declaration](https://github.com/google-gemini/gemini-cli/blob/main/packages/core/src/tools/definitions/dynamic-declaration-helpers.ts), read on 2026-10-14, define the complete supported argument set above. Its [base declarations](https://github.com/google-gemini/gemini-cli/blob/main/packages/core/src/tools/definitions/base-declarations.ts) supplies the exact `additional_permissions` spelling. That field accepts only optional `network: bool` and `fileSystem: dict`; the latter accepts only optional `read: list[str]` and `write: list[str]`. Unknown nested keys and malformed path elements keep strict inspection. This follows the official optional sandbox declaration, without granting Guardian exemptions for network or filesystem permissions.

The fixture helper `full_shell_envelope` supplies native event and session fields plus all supported tool options for each provider. Native-data and corpus tests exercise these complete envelopes alongside executable and unknown-option controls. Existing provider field precedence and raw patch boundaries remain unchanged. Alternate Copilot VS Code event/tool mappings are not expanded by this change.

## Security and budget behavior

Command text retains the existing shell-aware proof and executable-sink inspection. Human descriptions and justifications are inert only after their exact string types are validated. Working-directory strings, Codex permission prefixes, and Gemini permission paths undergo separate strict policy inspection; none inherits the command's data proof. Permission and background options never override command enforcement. `login` and `tty` require actual booleans. No environment-object exemption is added.

Counters require actual integers, excluding booleans, in the explicit range 0 through 2,147,483,647. Permission and mode strings have exact enum values. Shell selection recognizes only `bash`, `sh`, `zsh`, and their fixed `/bin/` or `/usr/bin/` spellings; arbitrary script paths and option-bearing shell strings stay strict. This validates supported shell syntax, not executable-file identity or shell startup-file safety.

Unknown or malformed fields retain the pre-existing full strict fallback, including all strings, keys and serialized arguments. They are not unconditionally denied: an entirely harmless unsupported shape may still pass strict inspection. The new semicolon-rich unknown/malformed controls deny, as do executable unknown-field controls. This preserves policy rather than silently exempting unproven fields or claiming schema rejection where it does not exist.

The existing normalized whole-tool traversal still runs before returning any native proof. Inert strings and keys remain charged to byte, depth, node and string limits. Large description/justification controls deny with `structured_bytes` even in warn mode. Patch grammar, exact body proof, late protected delete/move sources, executable options and nested sinks remain covered by the existing focused suites. No budgets, scanner policy, transport, registrations, or test registry were changed.

## Actual verification

All commands ran from the isolated repository root using `rtk proxy`. Decisions were checked through generated provider stdin/stdout entrypoints with fixture homes and logs.

| Command after final implementation | Observed result |
| --- | --- |
| `python3 scripts/test-tool-guard-native-data.py` | 26 tests passed |
| `python3 scripts/test-tool-guard-shell-data.py` | 17 tests passed |
| `python3 scripts/test-tool-guard-limits.py` | 18 tests passed |
| `python3 scripts/test-tool-guard-false-positives.py` | 153 public fixtures passed, zero failed |
| `python3 scripts/test-security-banners.py` | 14 tests passed |
| `bash scripts/test-codex-hooks-tool-guard.sh` | 14 tests passed |
| `bash scripts/test-hooks-tool-guard.sh` | Exit 0 |
| `bash scripts/test-gemini-hooks-tool-guard.sh` | Exit 0 |
| `python3 scripts/test-generate-hooks.py` | 26 tests passed with authorized worktree fixture mutation |
| `python3 scripts/generate-hooks.py --check` | All 35 generated files current |

The first generator-suite launch lacked permission to mutate this secondary worktree and produced five `PermissionError` test errors. The authorized rerun passed all 26 tests and the following read-only freshness gate passed. No test was weakened or skipped. The Copilot/Gemini shell suites used explicit disposable `/tmp` observability logs.

The final full-envelope fixture uses Codex `require_escalated` alongside its permission prefix, as documented by the tool contract. After that fixture-only correction, the full-envelope native test and all 153 corpus fixtures were rerun successfully.

## Remaining acceptance

The coordinator owns generated reconciliation with T1, composed transport/profile checks, performance/resource acceptance, independent review, the single end-of-session knowledge-maintenance pass, and the active ExecPlan. Preserve the distinction between these passing source tests and unavailable installed/native-provider proof. There is no new runtime build/profile identifier in T2; identity/reporting is assigned to later tasks.
