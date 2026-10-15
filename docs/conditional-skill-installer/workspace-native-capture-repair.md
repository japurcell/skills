# Native Windows Copilot capture-fixture repair

This record covers W7 in [ExecPlan.md](ExecPlan.md). It isolates the Copilot no-HEAD mismatch reported by Windows run [38766556979](https://github.com/japurcell/skills/actions/runs/38766556979), which passed the installer and Codex envelope checks at `b03d627a9e95fd3fa22222fcf8e07c9672bfbab4` before failing at `copilot warn no-HEAD response failed`.

## Red reproduction

The generated public entrypoint `.copilot/hooks/scripts/scan-secrets.py` was run on a genuine disposable Git repository created with `git init` and no commit. The process used Python `-I -S -B`, `SCAN_MODE=warn`, a disposable `SECRETS_LOG_DIR`, and the Windows fixture's JSON payload:

The local harness was invoked from the repository root as an inline `rtk proxy python3 -` command. It launched `python -I -S -B .copilot/hooks/scripts/scan-secrets.py` with the fixture repository as the process working directory and the JSON below on stdin. The logged record was parsed to retain only its status.

```json
{"hook_event_name":"Stop","session_id":"capture-windows","cwd":"<disposable-repo>","reason":"complete"}
```

The public hook exited 0, returned `{"systemMessage":"scan-secrets: pass; 0 modified files"}`, and wrote an audit record with `status=clean`. This is the red condition: the Windows fixture requires an empty response for a clean Copilot scan, but this payload selects the scanner's generic `Stop` pass message.

The same public-process harness then supplied the provider-registered CLI inputs for block `preToolUse` and warn `sessionEnd`. Each returned `{}` and wrote `status=clean` on that no-HEAD repository.

## Decision and repair

The maintained `.copilot/hooks/hooks.json` registrations invoke the scanner on CLI events `preToolUse` in block mode and `sessionEnd` in warn mode. The raw provider contract in `.agents/sources/copilot-hooks-ref.md` says these lowerCamelCase CLI events use camelCase fields and omit `hook_event_name`. `sessionEnd` includes a numeric `timestamp`, `cwd`, and `reason`; `preToolUse` includes a numeric `timestamp`, `cwd`, `toolName`, and `toolArgs`.

The Windows fixture now supplies those Copilot CLI envelopes. `preToolUse` uses `toolName: bash` with a harmless `git status --short` argument; the hook fixture invokes the scanner directly and does not execute that tool call. `sessionEnd` uses `reason: complete`. The existing public hook returned `{}` and wrote a `status=clean` audit record for both updated inputs on the same no-HEAD setup. The exact clean-response and clean-audit assertions remain. Codex `PreToolUse`/`Stop` and Gemini `BeforeTool`/`SessionEnd` payloads are unchanged.

No scanner policy or generated hook changed. All eight provider/mode scenarios, both modes, the five repeated Gemini descendant and oversized runs, the immediate `tmp*` assertion, and the outer watchdogs remain in `scripts/test-scan-secrets-windows.ps1`.

For no-HEAD response or audit assertion failures, the fixture now reports only response type and count, whether a `systemMessage` field exists, stdout/stderr byte counts, and a fixed audit-state label. It does not print response JSON, log contents, stderr contents, or secret values.

## Local verification

On macOS 26.7.1 (build 25G241), Python 3.14.6, PowerShell 7.6.7, and RTK 0.51.0, these checks ran from the repository root:

```text
rtk proxy pwsh -NoProfile -Command '$tokens = $null; $errors = $null; [System.Management.Automation.Language.Parser]::ParseFile((Resolve-Path "scripts/test-scan-secrets-windows.ps1"), [ref]$tokens, [ref]$errors) > $null; if ($errors.Count -gt 0) { $errors | ForEach-Object { $_.Message }; exit 1 }'
```

Exit 0; the PowerShell parser found no syntax errors. A focused check also confirmed that `ConvertFrom-Json -AsHashtable` response objects support the bounded type/count/field diagnostics.

```text
rtk proxy python3 scripts/generate-hooks.py --check
```

Exit 0: `Generated hooks are current (38 files).`

```text
rtk proxy python3 scripts/test-scan-secrets-capture.py copilot
rtk proxy python3 scripts/test-scan-secrets-capture.py gemini
rtk proxy python3 scripts/test-scan-secrets-capture.py codex
```

All exited 0 with their provider-specific `PASS: ... scanner capture failures and no-HEAD success` result. Each provider suite exercises block and warn modes, clean no-HEAD behavior, committed-HEAD failure, and a synthetic fake-secret finding through its generated public JSON entrypoint. The assertions require the correct incomplete/finding outcomes and check that the fake credential is absent from response and audit output.

```text
rtk proxy pwsh -NoProfile -File scripts/test-scan-secrets-windows.ps1
```

This exited 0 with `SKIP: native Windows scanner capture tests require Windows`. It is only non-Windows skip evidence. Native Windows behavior remains unverified here and must be checked by the fresh exact-SHA Windows workflow.

```text
rtk git diff --check
```

Exit 0.

## Hashes and limits

SHA-256 fingerprints at the local green result:

- Baseline `scripts/test-scan-secrets-windows.ps1` at base `8e0efb44`: `e898155ed6cf0e681354360d4c5695f978779be089e553c60c91c21fbe7f887c`.
- Repaired `scripts/test-scan-secrets-windows.ps1`: `7fc5e7298d1a549d7ae55c94b4583b667758c4ebe405a1ebb154edc0237e4bec`.
- Unchanged `scripts/test-scan-secrets-capture.py`: `e60e654b1606f50ea7707eeda7926f0e67a715fd592164407d321770a6000a08`.
- Unchanged canonical `hooks/families/scan_secrets.py`: `223e6bb341fdd9c4111801c5d0eb8e1bd613ef4fccb116a8cdb620cf31c8f0c9`.
- Unchanged generated Copilot scanner: `659940c8892d342b23f178296f5eb2a746720d9d21466d80d945b36ad08098b9`.
- Unchanged generated Gemini scanner: `e64c6c68a41bac72bb5aa65737768448ecd3d0d46d0504c1c907afb769106954`.
- Unchanged generated Codex scanner: `8f74d85673eb4e9597c398832f04052408ff3b347f311cf72a9e196b77ebe315`.

The local tests prove public JSON behavior and audit outcomes on macOS; they do not replace the native Windows process, `git.cmd` child-cleanup, junction, or Windows filesystem proof. No live installation, workflow dispatch, push, or production scanner change occurred in W7.
