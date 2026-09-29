# Windows validation and optional live-check procedure

Source revision, 2026-09-29. Stable RTK, repository-state retirement, global Markdown Health retirement, repository-local OKF, and sparse lifecycle messages are integrated. Native Windows proof remains open. Do not count old repository-state, global Markdown Health, or prerelease RTK results as revised acceptance.

Native Windows automation is required. A live Windows provider run is supplemental, not the completion gate. Separate Copilot CLI and Gemini CLI live milestones may run in another session with those CLIs available. The macOS high-rate performance audit runs hook scripts directly and has no CLI or Windows timing gate.

## Prepare native Windows automation

Use a disposable Windows checkout. Record provider versions when installed, Python version, PowerShell version, RTK version, Git status, unstaged and staged diffs, and untracked files. Keep fake security fixtures, transcripts, and logs out of the repository scanned by scan-secrets. Do not install provider CLIs solely for this checklist.

The Windows workflow at .github/workflows/ready-ideas-windows.yml must install the [official winget package](https://raw.githubusercontent.com/rtk-ai/rtk/v0.50.0/docs/guide/getting-started/installation.md) before installer tests, then verify that it is Rust Token Killer at version 0.50.0 or newer:

    winget install --id rtk-ai.rtk --exact --accept-package-agreements --accept-source-agreements
    rtk --version
    rtk hook --help

The workflow checks an exact stable `rtk X.Y.Z` version at least `0.50.0` and requires both `copilot` and `gemini` in the hook help. Record its actual version output. `rtk gain` is an optional tracking dashboard check; a database initialization failure does not prove the RTK binary or hook processors are missing.

The repository installer must not download RTK. Its own preflight tests must also prove that absent or old RTK stops before destination mutation. After the native job runs, record its actual installed version and results in the ExecPlan. If winget or its PATH refresh fails on the runner, keep the gate open and use an official stable release asset with checksum verification; do not treat a version shim as proof of real stable RTK behavior.

Run these repository-root commands in PowerShell on native Windows. Every suite must exit 0 without a Windows-specific skip.

    python scripts/generate-hooks.py --check
    python scripts/test-security-banners.py
    pwsh -NoProfile -File scripts/test-install.ps1
    pwsh -NoProfile -File scripts/test-codex-hooks-windows.ps1
    pwsh -NoProfile -File scripts/test-scan-secrets-windows.ps1
    pwsh -NoProfile -File scripts/test-rtk-stable-windows.ps1
    pwsh -NoProfile -File scripts/test-repository-okf-windows.ps1
    pwsh -NoProfile -File scripts/test-lifecycle-messages-windows.ps1

The Windows workflow runs this current list. It has no repository-state, prerelease RTK, or Markdown Health test steps. Do not add deletion regression tests. Inspect checked-in registrations and fresh temporary-home installer output to confirm those handlers are absent, while unrelated handlers remain.

The scanner suite must include a committed Git repository whose rev-parse --verify HEAD call fails unexpectedly. All three provider outputs must say incomplete and must not say clean. Separately verify that a genuinely unborn branch still works. A macOS PowerShell run that skips this fixture does not satisfy this gate.

The installer suites must cover stable RTK preflight, preserving unrelated TOML, changing only hooks.suppress_hook_warning to true, backup on semantic change, byte-stable repeat install, Windows APPDATA path, and preservation of unrelated user hooks. Check owner-only permissions and linked-destination refusal where supported. An explicit stable RTK missing-file command must retain its ordinary error and nonzero exit without the false missing-hook advisory. Automatic Copilot and Gemini RTK forwarding remains separately tested.

The repository OKF suite must check only the canonical .agents/instructions/ and .agents/memory/ trees at turn end. It must cover pass, definite failure and one repair retry, incomplete result, provider JSON, bounded audit paths, and no post-tool OKF registration. The lifecycle suite must check short startup and turn-end outcomes, every stop attempt, silent successful per-tool calls, and visible actionable warnings. Security banner tests must cover exact safe Tool Guardian rule causes, thresholds and counts, redaction, and scan-secrets generic wording. Keep fake data and raw matched values out of recorded evidence.

## Optional installed CLI check on Windows

Use only a local CLI already available. Before a real-home install, inspect the destination hook config and backups and run the temporary-home installer suite. Review provider hook trust after installation, including Codex /hooks where available. Do not bypass ordinary trust. Keep a disposable checkout and compare its starting and final Git status.

For each available Copilot CLI, Gemini CLI, or Codex CLI, record version and exact visible text:

1. Run explicit rtk on an existing file and a missing file. The missing-hook advisory is absent, and the missing-file error and exit code remain. Confirm Copilot or Gemini automatic forwarding still rewrites a safe eligible tool call.
2. Observe one operational session-start message and one successful turn-end message. Trigger a safe turn-end finding and a repeat stop attempt. Confirm each attempt appears, while routine successful pre/post-tool calls do not fill the transcript with messages.
3. Trigger a harmless Tool Guardian rule violation and an input-limit denial in a disposable tool call. Confirm the native message names the safe rule and cause, including limit and measured count when known. Confirm the redacted Action excerpt is one line and at most 160 characters, and the owner-only guard log has matching safe detail without raw input. Trigger a scanner warning or block with fake data; its banner must not include any matched value.
4. Edit a canonical .agents Markdown fixture only in a disposable checkout. Observe repository OKF pass or actionable findings at turn end and one bounded audit record for each nonduplicate validation attempt. Confirm the old workspace-wide Markdown checker does not run from fresh user-level registrations.
5. Use the safe scanner stall fixture or a disposable Git shim. A blocked pre-tool scan or warned session-end scan must finish as incomplete, never clean. Keep scanner logs and CLI transcripts outside the fixture repository.

The file-first PowerShell guidance remains accepted historical work: if rechecked, create a multiline .ps1 with the provider's native file tool and run the saved file. Disposable Probe Files requires only its three checked-in instruction sources, with no new live gate. No live repository-state guard check is required because that hook is retired. Keep the AGENTS.md ban on direct .git edits and review before destructive Git commands; do not execute a destructive action in this checklist.

For Codex verify PreToolUse and Stop delivery after trust review. For Copilot verify preToolUse, postToolUse, and agentStop. For Gemini verify BeforeTool, AfterTool, AfterAgent, and actionable SessionEnd warnings. The existing scripts/probe-provider-hook-delivery.py can insert uniquely named nonce handlers; run prepare, verify, and cleanup in that order, and always cleanup on failure. A nonce must not be in the agent prompt. Record timeout tool continuation as a provider limitation, not an enforcement guarantee.

## Record outcome

For every native suite and optional provider run, record host, provider and RTK versions, command or tool, exit code, brief visible result, safe audit summary, and transcript path. Mark an unavailable CLI or unrun native Windows suite unverified, not passed. Preserve a failure repro only at an exact named scratchpad or temp path. Remove only probe-owned files and compare final Git status with its baseline. The revised ExecPlan remains incomplete until all required automated and live milestones pass.
