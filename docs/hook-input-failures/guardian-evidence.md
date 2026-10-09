# Tool Guardian incident evidence

Collected 2026-10-08 local time, with UTC event dates below. Diagnosis is read-only; fixtures call generated public JSON hooks with disposable homes and logs. No raw session prompts, patch contents, unrelated paths, or credential-like values are retained.

## Conclusions

- The reported segment failures are real historical denials. The current Codex native patch schema and parser already accept the reconstructed historical patches.
- Current installed Codex adapter and policy helper match repository source byte for byte. Recent retained audit logs show four different, genuine patch byte-budget denials at the current 65,536-byte native aggregate ceiling.
- Tune the validated Codex patch budget separately. Keep exact schema validation, strict fallback, independent secret scanning, existing executable budgets, and other providers' native-data budgets.
- A reported strict-path count of 129 segments is a lower bound, not a full-input total. The splitter stops after 128 separators.

## Sampling and actual-versus-quoted classification

An initial newest-80 session sample inspected at most 16 MiB per file and 256 MiB total; it read 165,544,739 bytes. Matching results were research or quoted output, so they did not establish actual tool denials. A focused complete scan then covered 175 session files under the four incident date directories, 2026/09/29 through 2026/10/02, reading 373,547,086 bytes below an explicit 384 MiB ceiling. Long-lived sessions contain later October 7 events too.

The incident scan found 34 matching records: 8 non-tool-output mentions and 26 tool-output blocks. Of the latter, 16 were actual input-limit denials and 10 were quoted or non-limit blocks. Actual denials require the engine error prefix `blocked by PreToolUse hook` immediately before the exact safe guardian banner, with a prefix of at most 200 characters, plus call-id correlation to the patch-producing tool call. Merely finding `command_segments` in prose, echoed source, or a test subprocess result does not count.

Actual session records are `custom_tool_call_output` associated with an orchestration `exec` call. The corresponding JavaScript sometimes contains a literal passed to `tools.apply_patch`, and sometimes constructs a patch dynamically. That session call representation is not the hook's JSON envelope. The documented Codex envelope remains `tool_name: apply_patch` with `tool_input: {command: string}`.

The 16 actual session blocks consist of 13 segment denials, one historical 46,899-byte patch rejected against 32,768 bytes, and two later October 7 denials against 65,536 bytes. Twelve segment-denied inputs contain one reconstructable complete literal patch; all twelve parse under today's native parser and contain zero unprefixed empty lines. One contains multiple patch literals and cannot be reconstructed reliably without interpreting session code. Dynamic recent patch fragments likewise do not establish full-patch line or syntax metrics.

## Historical patch metrics

All listed segment causes report `tool input: 129 segments exceeds limit 128 segments`. Bytes count the decoded UTF-8 literal patch. Separators count the legacy raw splitter grammar, not executable commands. These reconstructed literals were examined in memory only.

| UTC event | Patch bytes | Lines | Raw separators | Operations | Current parser |
| --- | ---: | ---: | ---: | ---: | --- |
| 2026-09-29 21:36:36 | 22,025 | 161 | 197 | 1 | accepts |
| 2026-09-29 23:44:28 | 22,259 | 330 | 346 | 15 | accepts |
| 2026-09-30 00:29:19 | 10,903 | 228 | 240 | 5 | accepts |
| 2026-09-30 02:55:24 | 11,288 | 189 | 195 | 2 | accepts |
| 2026-09-30 04:53:40 | 7,271 | 124 | 141 | 1 | accepts |
| 2026-09-30 05:28:37 | 11,022 | 209 | 222 | 1 | accepts |
| 2026-10-01 21:54:11 | 20,937 | 237 | 242 | 10 | accepts |
| 2026-10-01 22:03:41 | 9,436 | 177 | 176 | 1 | accepts |
| 2026-10-01 22:26:23 | 24,727 | 523 | 536 | 1 | accepts |
| 2026-10-01 22:47:47 | 9,198 | 153 | 161 | 1 | accepts |
| 2026-10-01 23:34:29 | 14,199 | 234 | 241 | 1 | accepts |
| 2026-10-02 19:21:56 | 6,194 | 134 | 133 | 1 | accepts |

Representative safe log basenames: `rollout-2026-09-29T12-09-30-01a0ee92-7433-78a1-a4bd-ebed9ecdc8a1.jsonl`, `rollout-2026-10-01T15-17-11-01a0f98a-febc-7ba2-b1f5-8652312f1c3a.jsonl`, and `rollout-2026-10-01T14-43-29-01a0f96c-2261-79f3-911b-3833cbde24c3.jsonl`.

## Independent deployed audit corroboration

The maintained guard audit is a prefixed JSON log; parsing only whole lines as JSON incorrectly misses events. Decode from the first JSON object marker and retain only allowlisted tool/rule/count fields.

| Audit basename | Patch passes | Patch input-limit events |
| --- | ---: | --- |
| `guard.log.2` | 969 | 13 segment denials on September 29-October 2; one 46,899-byte denial against 32,768 bytes on September 29 |
| `guard.log.1` | 1,231 | one 77,089-byte denial against 65,536 bytes on October 6 |
| `guard.log` | 630 | three byte denials against 65,536 bytes on October 7: 99,186; 80,666; 90,127 |

These files also contain eight other historical patch threat events, excluded from input-limit counts. The current and previous retained audit files contain no patch segment-limit events. Snapshot sizes were approximately 0.72 MiB, 1.05 MiB, and 1.05 MiB; logs grow during investigation, so pass counts describe the snapshot, not a stable total.

At the pre-edit snapshot, repository and installed SHA-256 fingerprints were equal:

- `.codex/hooks/tool-guard.py`: `d51f25f5164d24be0f5d6019e56a4d12db0a8807da0889d4a8aaa3838af0afe7`.
- `.codex/hooks/helpers/tool_guard_policy.py`: `3e56614196ecdec16a08a2618fc6b46ccede727fc7378b561d61c47c701dd4ed`.

## Public entrypoint reproductions

`scripts/tool_guard_test_support.py:15` invokes the actual provider scripts in isolated subprocesses and redirects home, guard, audit, and observability state to disposable directories. All reproductions returned exit 0 and valid provider JSON.

- An inert 4,115-byte, 143-line patch with semicolon examples is allowed by Codex when the input is exactly `{command: patch}`. A scalar patch, `{input: patch}`, `{patch: patch}`, or `{command: patch, extra: true}` reproduces the exact segment error. These are strict-fallback negative controls, not evidence for admitting undocumented schemas.
- The same complete native patch passed to Copilot or Gemini as `apply_patch` is strict input and reproduces the segment error. Their documented write/edit/search tools have separate native schemas; do not generalize Codex's patch exemption across providers.
- A synthetic one-file patch with 24,727 UTF-8 bytes, 523 lines, and 536 raw separators is allowed by the current public Codex entrypoint. It reproduces the dimensions of the largest reconstructed segment-denied literal without retaining its contents.
- Synthetic valid Codex patches sized exactly 77,089, 80,666, 90,127, and 99,186 bytes reproduce the four recent byte-denial diagnostics. Each reports the `apply_patch.command` field and the actual body bytes against 65,536 bytes.
- A 65,529-byte complete patch plus the seven-byte `command` schema key reaches 65,536 aggregate bytes and passes. A 65,530-byte body reaches 65,537 aggregate bytes and denies with `tool input: 65537 bytes exceeds limit 65536 bytes`.
- A 262,137-byte complete patch plus its schema key reaches the proposed 262,144-byte boundary and currently denies against 65,536 bytes. Candidate tests must change that result only for validated Codex patches and deny the next aggregate byte in block and warn modes.

The guard entrypoint never executes a patch. Its denial JSON is pre-execution proof; native host behavior is responsible for omitting the actual tool call. A fixture can assert that invoking a denied guard leaves sentinel files untouched, but should not claim that this proves the patch executor's own transaction semantics.

## Exact flow and budgets

In `hooks/families/tool_guard.py:1703`, `_native_tool_shape` admits only exact Codex `apply_patch` plus `{command: str}`. `read_tool_scan_inputs` at line 1752 counts decoded structure and UTF-8 strings before `_parse_native_patch` at line 666 validates patch grammar. Unsupported shape or syntax falls back to strings, dictionary keys, and JSON serialization under strict inspection. `build_input_threats` at line 1456 inspects valid patch delete/move sources as operations instead of treating body content as shell text.

Current ceilings at lines 165-173 are 32,768 executable scan characters/bytes, 65,536 native-data aggregate bytes, 128 command segments, 256 command tokens, 32 structured levels, 256 structured nodes, and 128 structured strings. Valid native aggregate bytes include all UTF-8 string values and dictionary keys, not raw JSON envelope bytes. Delete/move-source normalization retains its separate 32,768-byte aggregate work budget. Bounds can fail earlier than a later nominal limit.

The strict `_command_segments` path at line 248 first applies NFKC normalization and scan-text bounds, then splits on actual LF/CRLF, literal backslash-n/backslash-r, `&&`, `||`, and `;`, with `maxsplit=128`. It checks the raw split-list length before dropping empty segments. After 128 splits, the remainder is one additional segment even when more separators remain; therefore 129 means at least 129. Per-segment tokens use `shlex` after replacing double quotes and commas with spaces, with whitespace fallback on quoting errors. This heuristic applies to unsupported patch schemas or malformed patch grammar, while validated patch bodies bypass it.

## Bounded implementation and validation recommendation

Keep source edits owned by the parent in the canonical renderer and focused tests. Add a patch-specific 262,144-byte aggregate ceiling, leaving the existing 65,536-byte write/edit/search budget and all executable limits intact. This accommodates the largest recent observed patch with bounded headroom; it is not evidence for an unlimited or universally safe raw-envelope size. Reject unsupported shapes, trailing executable text, malformed patch syntax, and protected delete/move operations as before. Preserve independent scanner decisions.

Make the legacy capped split diagnostic truthful by reporting a lower bound such as `at least 129 segments`; do not raise executable command limits merely to fit documentation. Pair synthetic historical single/multi-file fixtures and a full 256 KiB patch boundary with the existing executable, malformed-schema, normalized-operation, helper-failure, warn-mode, and allowlist controls.

Exact maintained commands from the repository root:

```sh
rtk proxy python3 scripts/generate-hooks.py --check
rtk proxy python3 scripts/test-tool-guard-native-data.py
rtk proxy python3 scripts/test-tool-guard-limits.py
rtk proxy python3 scripts/test-tool-guard-shell-data.py
rtk proxy python3 scripts/test-tool-guard-false-positives.py
rtk proxy python3 scripts/test-security-banners.py
rtk proxy python3 scripts/benchmark-tool-guard-resources.py --help
```

Use the resource benchmark's maintained cases and accepted 500 ms finite-case ceiling after reading its actual interface. Source fixture results, installed-file fingerprints, and native provider delivery remain distinct evidence. The parent owns generation, final acceptance tests, installation, and the coordinated end-of-session knowledge pass.
