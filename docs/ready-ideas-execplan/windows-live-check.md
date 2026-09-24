# Windows live-check procedure

This procedure supplements the native Windows automation in
`.github/workflows/ready-ideas-windows.yml`. A live Windows run is not the
completion gate; every workflow step must exit `0` on a Windows runner. A
macOS `pwsh` run that skips Windows cases does not satisfy that gate. Record
provider version, exact tool call, visible result, audit result, and any
limitation for each live check. Do not include secrets in transcripts.

## Prepare a disposable checkout

Use a disposable Windows checkout with no personal work. Before installation,
record `git status --short`, `git diff`, `git diff --cached`, and
`git ls-files --others --exclude-standard`. Inspect existing user hook
settings and their backups. Confirm `python`, `git`, and `pwsh` are available.
Do not install dependencies or provider CLIs as part of this procedure.

Run these repository-root commands in PowerShell. Each must exit `0` without
a host-specific skip:

    python scripts/generate-hooks.py --check
    python scripts/test-security-banners.py
    pwsh -NoProfile -File scripts/test-install.ps1
    pwsh -NoProfile -File scripts/test-codex-hooks-windows.ps1
    pwsh -NoProfile -File scripts/test-scan-secrets-windows.ps1
    pwsh -NoProfile -File scripts/test-repository-state-windows.ps1
    pwsh -NoProfile -File scripts/test-rtk-explicit-windows.ps1
    pwsh -NoProfile -File scripts/test-markdown-health-windows.ps1

Review the temporary-home installer results and the destination diff before
running `scripts/install.ps1` against a real user home. Preserve unrelated
hook groups and files. Review changed non-managed Codex definitions through
`/hooks`; do not bypass trust. Record any provider hook trust state.

## Exercise available local providers

Use local Copilot CLI, Gemini CLI, and Codex only where already
available. Deployed VS Code Copilot hooks are not required for acceptance;
retain source-level compatibility tests. Record each available CLI version
before testing. Keep probe transcripts in OS
temp and clean up only exact files created for this check. The deployed
Copilot and Gemini checks belong to ExecPlan milestones 11 and 12; source
fixtures alone do not close them.

For each available CLI provider:

1. Use its native file-edit tool to write a multiline `.ps1` in OS temp or
   `.agents/scratchpad/`, with quotes and a here-string. Run the saved file.
   Remove that exact file afterward. This checks the file-first guidance;
   the Disposable Probe Files milestone itself has no live acceptance gate.
2. Trigger a safe Tool Guardian warning and block in a disposable context.
   Confirm the displayed action is one redacted line of at most 160 characters,
   that block and warning wording differ, and that the guard log stores the
   same excerpt without raw credentials. Trigger a scanner warning or block
   using fake data only; confirm it names the action and reveals no match.
3. Ask the native editor to create a harmless file under `.git/` in the
   disposable checkout. Confirm denial and that no file appeared. In a
   disposable tracked file, stage and modify separate content, inspect status,
   both diffs, and untracked files, then request a work-discarding Git command.
   Confirm the hook denies it before execution. Never discard real work.
4. Edit a temporary `.md` file to contain a broken relative link. Confirm a
   diagnostic names the file and link, and exactly one bounded audit entry
   lists checked files for that validation batch. Confirm untouched Markdown
   and HTTP(S) URLs do not produce broken-link findings.
5. Use the controlled scanner stall fixture or a disposable Git shim to hold
   output open. Confirm the hook returns promptly with `incomplete` as a
   warning or denial according to mode; it must never report `clean`.
6. Run an explicit `rtk read` on an existing file and a missing file through
   the agent shell. Confirm the false missing-hook notice is absent, while
   the missing-file diagnostic and nonzero exit remain. Normal terminal `rtk`
   must still resolve to the stable installation.

For Codex, verify `PreToolUse` and `Stop` delivery with
`scripts/probe-provider-hook-delivery.py` after trust review, including a
one-second timeout probe. For Copilot CLI, verify `preToolUse`, `postToolUse`,
and `agentStop`. For
Gemini, verify `BeforeTool`, `AfterTool`, `AfterAgent`, and scanner `SessionEnd`.
Use the probe's `prepare`, `verify`, and `cleanup` commands from `ExecPlan.md`,
and always run cleanup after a timeout or failure. Record whether each timed
out tool proceeded, stopped, or showed a message. Copilot pre-tool timeouts
are fail-open; no hook-only claim of complete protection is valid.

## Record outcome

For each provider and each automated suite, record version, command or tool,
exit code, transcript path, and observed result. Mark unavailable CLIs and
unrun Windows workflow steps as **unverified**, not passed. Compare final Git
status with the starting baseline and list any probe files intentionally kept
to reproduce a failure.
