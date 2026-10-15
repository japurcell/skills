# Scanner input failure evidence

## Scope and certainty

Investigation date: 2026-10-08. This records source behavior and disposable subprocess fixtures for the report in `docs/scan-secrets-hook-bug.txt`. It does not identify the incident's exact Linux-host cause: no failing checkout, installed Linux scanner, runtime configuration, or original diagnostic log was supplied.

The owner of the reported wording is the canonical renderer `hooks/families/scan_secrets.py:1256`. Generated entrypoints are `.copilot/hooks/scripts/scan-secrets.py`, `.gemini/hooks/scripts/scan-secrets.py`, and `.codex/hooks/scan-secrets.py`. Copilot registers this scanner under `preToolUse` at `.copilot/hooks/hooks.json:80`, and at agent stop separately. The local macOS installed Copilot scanner was read-only compared with source and was byte-identical, SHA-256 `5ebf897a7ae52a5b3b0a969126fc98380ce855490a399359886b8da0446e0939`. This is not evidence about the reported Linux installation.

The generic denial is reproducible for benign requests. Clean bounded fixtures pass, so the scanner is not universally broken for read tools or argument-free documentation tools. Deliberate incomplete-scan boundaries must remain denials in block mode.

## What is scanned

1. `main()` checks Git availability and audit-directory initialization before parsing input (`hooks/families/scan_secrets.py:1317`).
2. `read_payload()` accepts an object using the shared complete-JSON reader (`:170`; `.copilot/hooks/scripts/helpers/common.py:87`). The shared reader also starts observability capture; it catches observability exceptions. Tool names and arguments are not used to choose scanner files.
3. Event/reason fields choose the fixed action label, such as `tool scan`; session/timestamp fields are logged (`:1340`). Copilot ignores payload `cwd` and uses process cwd (`:1280`). Gemini and Codex use provider cwd fields (`:1292`, `:1304`).
4. Git finds the containing repository and independently distinguishes genuine unborn HEAD from unexpected HEAD failures (`:436`, `:462`, `:476`).
5. Default `SCAN_SCOPE=diff` combines staged, worktree, untracked, and unresolved-merge snapshots (`:536`). Staged-only scope excludes unrelated untracked files. Default scanning is not limited to a tool's referenced file, its requested line range, or external resource. The documentation request's empty arguments still lead to the same repository scan.
6. Index snapshots are read with bounded Git captures; worktree files are safely opened without following links (`:197`, `:633`, `:738`). Text files with HEAD use added diff lines; untracked, unborn, unresolved merge, and staged-only candidates use full content (`:1475`). Binary-like files still receive bounded ASCII scanning. A file extension does not exempt a candidate from byte limits.
7. Results are persisted to the secure scan log before the native decision is emitted (`:1124`, `:1513`). Failure to persist even a clean result becomes an incomplete denial.

The eight-second total budget starts before input parsing, and each Git command also has a five-second maximum. Current limits are 256 candidate snapshots, 1,048,576 bytes per candidate, 8,388,608 total bytes, and 8,388,608 Git capture bytes (`:80`). Multiple sources for the same path are separate snapshots in the candidate-count limit.

## Disposable public-entrypoint reproduction

Commands were launched from the repository root with `rtk proxy python3 - <<'PY'`; a Python driver created fixtures using `tempfile.TemporaryDirectory(prefix='scanner-benign-')`, then invoked the actual generated entrypoints as `[sys.executable, '-I', '-S', '-B', hook_path]`. The driver never invoked an installer or executed an installed home hook.

Fixture recipe:

- Each fixture root contains a child `repo` and sibling audit, scanner-log, and observability locations. Initialize Git; write `readme.txt` containing `safe fixture\n`; commit using local `-c user.name`, `-c user.email=scanner@example.invalid`, and `-c commit.gpgsign=false` arguments. No global Git configuration is changed.
- Remove inherited `AUDIT_*`, `OBSERVABILITY_*`, `COPILOT_OBSERVABILITY_*`, and `GEMINI_OBSERVABILITY_*` variables from the child environment. Set `AUDIT_LOG`, `SECRETS_LOG_DIR`, `OBSERVABILITY_LOG_PATH`, and `TMPDIR` to sibling disposable paths. Set `GIT_CONFIG_NOSYSTEM=1`, `GIT_CONFIG_GLOBAL=os.devnull`, `SCAN_MODE=block`, `SCAN_SCOPE=diff`.
- Invoke with process cwd at the fixture repo, JSON on stdin, captured stdout/stderr, and a 12-second outer timeout. Parse stdout as one JSON object. Inspect only the final scan-log `status`, never fixture secret values.
- Copilot payload: `{"sessionId":"benign-repro","hook_event_name":"preToolUse","cwd":"<fixture repo>","toolName":"functions.fetch_copilot_cli_documentation","toolArgs":{}}`. Gemini changes event to `BeforeTool` and adds `session_id`; Codex uses `PreToolUse` and `session_id`.
- The first Copilot comparison also used `toolName=functions.view`, with `toolArgs={"path":"readme.txt","view_range":[1,1]}`. Both tool shapes produced identical decisions per fixture.

| Fixture change | Copilot | Gemini | Codex | Explained source cause |
| --- | --- | --- | --- | --- |
| Committed clean repository | `{}`; exit 0; clean log | `{}`; exit 0; clean log | `{}`; exit 0; clean log | No modified candidates |
| Untracked `report.json` with 1,048,577 ASCII spaces | Incomplete denial; exit 0 | Incomplete denial; exit 0 | Incomplete denial; exit 0 | Per-file byte limit (`:618`) |
| 257 untracked `report-N.txt` files, each `safe\n` | Incomplete denial; exit 0 | Incomplete denial; exit 0 | Incomplete denial; exit 0 | Candidate-count limit (`:596`) |
| Dirty nested checkout tracked as mode 160000 | Incomplete denial; exit 0 | Incomplete denial; exit 0 | Incomplete denial; exit 0 | A gitlink directory enters worktree candidates and is rejected as nonregular (`:616`) |
| `SECRETS_LOG_DIR` is beneath a sibling regular file | Incomplete denial; exit 0 | Incomplete denial; exit 0 | Incomplete denial; exit 0 | Cannot create secure log directory (`:995`) |

The gitlink fixture uses only local Git: initialize `repo/vendor`, commit its safe `readme.txt`, get its HEAD object ID, register `git update-index --add --cacheinfo 160000,<oid>,vendor` in the parent, commit the parent, then change only `vendor/readme.txt` to `safe benign edit\n`. A simple omission of gitlink candidates would hide unexamined contents; supporting nested checkouts would require an explicit complete bounded scan policy and separate controls. It is a reproducible unsupported repository shape, not evidence that this incident involved a submodule.

Every failure row emitted only this diagnostic:

```text
scan-secrets blocked: tool scan; scan incomplete; potential secrets could not be checked.
```

With fully isolated observability paths, stderr was empty for clean cases and held only that diagnostic for incomplete cases. An earlier run isolated audit and secret logging but inherited observability routing; the readonly sandbox rejected the observability database write. That observation did not change the scanner decision and is not an incident diagnosis. The full-isolation rerun above is the retained evidence.

Additional all-provider controls used an unborn repository and an untracked `candidate.txt`:

| Control | Result in every provider |
| --- | --- |
| Small safe text | `{}`; exit 0; clean log |
| Synthetic recognizer fixture constructed dynamically from a prefix and 36 repeated characters | Findings denial; exit 0; `potential secrets detected`, rather than incomplete |
| Empty disposable `PATH`, Python launched by absolute path | Incomplete denial; exit 0; generic action `scan` |
| `AUDIT_LOG` beneath a disposable regular file | Incomplete denial; exit 0; generic action `scan` |

## Narrowing the reported incident

On this source version, the literal `tool scan` label is assigned only after Git availability, successful audit initialization, and valid input parsing. Consequently missing Git, audit initialization failure, and malformed input cannot produce that exact action label on this version. A deployed version mismatch could invalidate this narrowing.

The likely failure domain is post-input repository discovery, Git capture/HEAD/index/diff handling, candidate safety/bounds, or log persistence. A report saved outside the repository, as in the supplied incident, is not selected merely because a tool argument references it. Its absence or emptiness does not establish why the scanner failed. The real repository's safe candidate sizes and Git state were unavailable.

A runtime scanner log located inside an unignored repository can itself become an untracked candidate on a later invocation. The canonical default puts it under the provider home, outside the ordinary checkout. No supplied evidence places this incident's scanner logs inside its checkout. This remains a configuration-dependent candidate, not a verified cause.

## Bounded repair recommendation

Improve incomplete diagnostics at the canonical source without granting an exemption to read or documentation tools, weakening bounds, or reporting a partial scan as clean. Keep the native provider denial envelopes and exit 0 behavior.

Use typed failures with fixed-vocabulary cause and operation codes rather than rendering exception messages, Git arguments, stderr, filenames, payloads, session IDs, or traceback details. Persist the same allowlisted metadata in the incomplete scan record when secure logging remains available. On log failure, retain the original cause in the response even if the attempted incomplete-log write also fails.

Suggested mapping:

| Source boundary | Fixed cause / operation metadata | Safe recovery wording |
| --- | --- | --- |
| Missing Git (`:193`, `:1323`) | `git_unavailable` / `initialization` | Ensure Git is available to the hook. |
| Audit init false (`:1330`) | `audit_unavailable` / `initialization` | Check hook audit storage. |
| Invalid/malformed JSON (`:170`) | `input_invalid` / `input` | Check the provider hook envelope. |
| Git nonzero (`:281`) | `git_failed` / fixed command-family operation; integer exit status | Check repository accessibility and Git health. |
| Git capture open/read failure (`:291`) | `git_capture_failed` / fixed operation | Check temporary storage and Git execution. |
| Running descendant (`:266`, `:270`) | `git_descendant_running` / fixed operation | Check Git process completion. |
| Malformed capture/index/diff (`:503`, `:776`, `:945`) | `git_output_invalid` / fixed operation | Check Git compatibility and repository integrity. |
| Deadline (`:118`, `:251`, `:1251`) | `scan_timeout` or `git_timeout`; fixed seconds | Retry after checking repository size and Git responsiveness. |
| Count/byte caps (`:596`, `:618`, `:1253`) | `file_count_limit`, `file_bytes_limit`, `total_bytes_limit`, `git_output_limit`; threshold, actual count where bounded | Reduce the pending scan workload or correct unintended generated artifacts. |
| Link/nonregular/unsafe candidate (`:609`, `:616`, `:646`, `:664`) | `candidate_unsafe` or `candidate_read_failed` / `candidate_read` | Check pending file types and accessibility. |
| Secure log/lock/configuration (`:987` onward) | `log_unavailable`, `log_unsafe`, `log_lock_timeout`, `log_configuration_invalid` / `scan_log` | Check secure hook log storage and rotation settings. |
| Unknown exception | `internal_error` / fixed current scan phase | Check the hook installation and retry. |

Codes and recovery sentences are constants. Numeric metadata must be supplied by known scanner counters/statuses, type-checked, and bounded. Distinguish snapshot count from unique file count. Do not infer the cause from arbitrary exception text or expose raw exception `str()`. A private-path or token-shaped adversarial error string must never be echoed through stdout, stderr, or scan-log note fields.

## Verification selection

Source command recommendations, with disposable observability routing and outer watchdogs preserved:

```sh
rtk proxy python3 scripts/generate-hooks.py --check
rtk proxy bash scripts/test-hooks-secrets-scanner.sh
rtk proxy bash scripts/test-gemini-hooks-secrets-scanner.sh
rtk proxy bash scripts/test-codex-hooks-secrets-scanner.sh
rtk proxy python3 scripts/test-scan-secrets-capture.py copilot
rtk proxy python3 scripts/test-scan-secrets-capture.py gemini
rtk proxy python3 scripts/test-scan-secrets-capture.py codex
rtk proxy python3 scripts/test-scan-secrets-merge.py
rtk proxy python3 scripts/test-security-banners.py
```

The capture suite already preserves failed/stalled/malformed/oversized captures, descendant-held output, committed-HEAD failures, genuine unborn success, block/warn behavior, and temporary-file cleanup (`scripts/test-scan-secrets-capture.py:108`). Provider shell suites retain unsafe and oversized candidates and log-lock failure controls (`scripts/test-hooks-secrets-scanner.sh:298`). The merge suite owns multi-stage index and batched-read controls. Require a findings-specific outcome for secret controls and incomplete-specific outcomes for operational failures. Generic deny alone proves neither correct detection nor cause classification.

Run generator fixture tests only during a coordinated pause of all repository edits. Native Windows behavior requires `rtk proxy pwsh -NoProfile -File scripts/test-scan-secrets-windows.ps1`; macOS fixture success does not establish that platform or installed event delivery.
