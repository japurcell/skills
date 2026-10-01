# Native Tool Guardian boundary evidence

Milestone 2 candidate implementation, 2026-10-01. The orchestrator owns final ExecPlan synchronization and the formal agent documentation pass at the end of the entire work session. The provisional native resource cap still requires milestone 4 runtime and memory evidence.

## Public reproductions and test boundary

Every fixture invokes a checked-in generated provider hook with JSON on stdin and observes its JSON decision on stdout. Represented operations are never executed. Disposable log paths are used; no hook is installed into the real user home. Threat text in the focused suite is constructed from numeric character codes.

Before the canonical edit, a valid Codex `apply_patch.command` adding a shell file with a prose command example was denied with `force_push_protected_branch`. The focused public test then passed after the native patch boundary, while its `Bash.command` counterpart remained denied.

The installed guardian additionally blocked the initial multi-hunk source-edit attempt with `command_segments`, threshold 128, reported count 129. No mutation occurred. The exact payload size was not retained, so it is not a byte-limit measurement. Smaller source-edit hunks proceeded without disabling the guard. This confirms the existing installed maintenance issue; it does not establish candidate installed behavior.

## Schema evidence and scope

[Official Codex hooks](https://learn.chatgpt.com/docs/hooks) specifies canonical hook tool names and `Bash` / `apply_patch` input under `tool_input.command`. Only exact Codex `apply_patch` with the sole string `command` field is classified as a native patch. `Write`, `Edit`, and `Grep` are matcher aliases rather than established canonical tool-input schemas. They keep strict inspection. Copilot `apply_patch.command` also keeps strict inspection because the current CLI reference establishes the tool name without proving this argument schema.

[Official Gemini file-system tools](https://geminicli.com/docs/tools/file-system/) establishes `write_file` with required string `file_path` and `content`; `replace` with required string `file_path`, `instruction`, `old_string`, and `new_string`, plus optional boolean `allow_multiple`; and `grep_search` with required string `pattern` and optional string `path` / `include`. These exact tool names and typed shapes are the supported Gemini boundaries.

[GitHub-owned Copilot lifecycle example](https://github.com/github-samples/advanced-copilot-cli/blob/main/content/04-lifecycle-hooks.md) establishes `edit` with string `path`, `old_str`, and `new_str`. The root's sanitized key-and-type-only primary Copilot event survey corroborates that shape and establishes observed `create` arguments `path` / `file_text`, both strings. It establishes observed `grep` arguments with exactly one string `pattern` or `query`, optional `path` string or `paths` string/list of strings, and typed search-output options; observed `rg` uses string `pattern`, optional string/list `paths`, and typed output/context flags. These are conservative observed shapes, not a claim of the provider's complete schema. Additional or ambiguous fields keep strict scanning.

Copilot public fixtures use `toolName` / `toolArgs`, while Codex and Gemini use `tool_name` / `tool_input`. Existing name and argument precedence stays unchanged, including conflicting compatibility keys. Provider identity is a constant in each generated adapter. Neither case folding nor a tool-name match alone establishes native data authority.

## Classification and operation decisions

`NativeToolInput` separates the operation kind, metadata, inert content and patch source operations. Unsupported values return the existing strict text representation. Only whole well-typed native argument shapes receive exemptions. All structural depth, node, string and UTF-8 checks run before returning exempt content. Known native keys and destination bytes count toward the native aggregate.

File bodies, replacement old/new strings and native search patterns are data regardless of destination extension. Known literal destinations do not execute shell syntax. Native content no longer consumes shell token or segment budgets, and its serialized JSON object is not rescanned as executable input. Unknown shapes retain decoded value, decoded dictionary-key and serialized-object inspection; nested unknown strings cannot disappear behind a known tool name. Strict serialized rescanning remains intentionally conservative for later measured work.

The patch parser recognizes begin/end markers, add/update/delete headers, move headers, hunk/context/content lines and end-of-file markers. Unsupported syntax, extra fields or trailing represented commands fall back to strict inspection. Header-like lines inside prefixed file bodies remain data.

Deletion and movement expose their source path separately. The existing `.env` / `.git` removal rule IDs, categories and critical severity apply with the same suffix-followed-by-nonword boundary semantics over normalized literal source paths. Thus `config.env`, `.env-test`, `backup.git`, and `.git-old/config` receive the relevant source-removal finding, while `.envrc` and `.github` do not. This corrects the operation model that previously missed native patch syntax; it is not evidence of a historical native destination policy. Add/update/overwrite destinations receive no invented general allowlist or recursive-directory rule. Repeated operation causes are deduplicated by rule ID before banner/log production.

`MAX_NATIVE_DATA_BYTES = 65536` is provisional and independently bounded. `MAX_SCAN_TEXT = 32768`, 128 command segments, 256 command tokens, depth 32, 256 structural nodes and 128 strings remain unchanged for strict inspection. Native aggregate byte accounting includes data, destination/metadata strings and dictionary keys. Public tests admit exactly 65536 aggregate bytes and deny 65537 for ASCII, UTF-8 and native patches. The 46899-byte patch with 330 literal separator-bearing lines passes. Overflows and UTF-8 inspection failures precede allowlisting and still deny in warn mode. Milestone 4 must validate the cap against preserved incidents and whole-hook runtime/memory bounds.

## Validation evidence

`rtk proxy python3 scripts/test-tool-guard-native-data.py`: 13 test methods passed, last run 2.267 seconds. Coverage includes all three provider public envelopes, validated native writes/edits/searches, Codex patches, paired shell threat denials, decoded unknown keys/nested values, unsupported aliases, malformed patch hunks, separate delete/move sources, distinct rule causes, silent native passes, the 46899-byte incident size, maximum/first-overflow boundaries, UTF-8 failure, warn/allowlist fail-closed precedence, and compatibility-field precedence.

`rtk proxy python3 scripts/test-generate-hooks.py`: 25 tests passed. Generator write mode refreshed only the three manifest-owned Tool Guardian outputs; generator check passed. Copilot and Gemini Tool Guardian shell suites exited zero, with existing sandbox-related observability database warnings.

`rtk proxy python3 scripts/test-security-banners.py`: 12 of 13 test methods passed. The sole failure is the old Gemini valid `write_file` 33000-byte rejection assertion. This input is now below the native cap. The Codex shell suite also exits one because it reruns that shared assertion. Milestone 4 must update this fixture to the measured native overflow while retaining the strict 32768-byte tests for unsupported shapes/providers. These failures were retained rather than disabled or weakened.

No latency or installed-provider-delivery acceptance is claimed by this milestone. The frozen original baseline, integrated corpus, benchmark comparison and final numeric assertion synchronization belong to subsequent work owned by the root.
