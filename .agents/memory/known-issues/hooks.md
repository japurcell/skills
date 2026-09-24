---
type: Known Issue
description: General provider-hook failures; specialized auto-ingest and observability issues live in focused sibling files
---

# Hooks - Known Issues

Load this file for general provider-hook work. For source scanners, manifests, summaries, injectors, or pending gates, read [Hook Auto-Ingest - Known Issues](hooks-auto-ingest.md). For emitters, SQLite traces, transcripts, logs, or maintenance, read [Hook Observability - Known Issues](hooks-observability.md).

## Active guards can block their own maintenance

Tool Guardian scans patch, search, replacement, and cleanup payloads. Raw dangerous command strings can block safe policy edits or tests; multiline serialized text can also create false matches across escaped newlines. Construct required threat strings dynamically, keep unrelated dangerous lines outside replacement hunks, and keep deletion-target matching bounded to one logical line and a short distance.

Secret scanning has the same self-edit risk for realistic fake credentials. Use unmistakably fake values such as `fake-api-key`; never write a real secret.

## Same-named hook modules confuse mypy

Copilot and Gemini contain same-relative-path modules such as `observability.py`. Run mypy on each file separately instead of passing both in one invocation.

## Bash `RETURN` traps can outlive local variables

Under `set -u`, interpolate function-local cleanup paths when registering the trap, for example `trap 'rm -rf -- "'"$workdir"'"' RETURN`. At trap execution, the local variable may no longer exist.

## Secret-scanner Git probes can hang on Windows

Run Git with `GIT_TERMINAL_PROMPT=0`, an empty `GIT_ASKPASS`, and a short timeout. Let timeout errors reach the top-level handler so block mode denies; warn mode may emit a sanitized no-op.

The native Windows `gemini/block/descendant` fixture intermittently saw a `tmp*` Git-output capture file immediately after the hook returned. A surviving `cmd.exe` child was still running; the file disappeared after that child exited. `handle64` found no handle by the time its scan completed, so it did not establish a specific handle owner. Windows cleanup now terminates and waits for captured child processes directly through Win32 handles instead of launching `taskkill` with a 250 ms subprocess timeout. The native matrix and six bounded replays of that exact case passed after the change. Keep the test's immediate `tmp*` assertion and exact provider/mode/scenario/filename failure text: a later recurrence needs fresh process and handle evidence rather than an assumed cause.

## Extensionless commands fail on Windows

With `shell=False`, resolve commands such as `rtk` through `shutil.which()` so `.cmd` or `.bat` executables are found.

## Git metadata paths can use platform aliases

On macOS, a temporary worktree pointer can name `/var/...` while resolved Git/common paths use `/private/var/...`. Compare resolved literal path candidates with resolved Git directories; a string comparison of complete shell text misses this alias. Reject linked `.git`, Git-directory, and `commondir` entries before reading pointers.

## Codex apply_patch path is inside `tool_input.command`

Codex `PreToolUse` reports file edits as `tool_name: "apply_patch"` with patch text under `tool_input.command`; it does not provide a `file_path` field. Parse the patch's Add, Update, Delete, and Move headers before deciding whether a Git metadata path is affected. Missing or malformed patch paths deny the edit.

## Codex handler environment does not select Markdown event

Codex CLI 0.155.1 ignores per-handler `env` in `~/.codex/hooks.json`. The Markdown hook reads `hook_event_name` from the input JSON to distinguish `PreToolUse`, `PostToolUse`, and `Stop`. A `PostToolUse` envelope at `Stop` produces `hook returned invalid stop hook JSON output`; Codex `Stop` accepts the common message fields and `decision: "block"` with `reason`, but not `hookSpecificOutput` or `decision: "allow"`.

## Quoted shell prose is not an executable Git command

Do not search raw shell text for `git checkout` or redirection markers. `echo 'git checkout branch'` and `echo '.git/config > file'` are data. Tokenize with quote boundaries intact, inspect executable command positions and redirection targets, and recurse only into recognized shell `-c`/PowerShell `-Command` arguments. Malformed actual commands still deny; a quote-blind split on `;` or `>` creates false denials.

## In-place writers bypass output-redirection checks

A shell command can modify `.git` without `>` or a direct editor tool. Recognize in-place `sed`, `perl`, `truncate`, and `install` forms at executable positions in `_writes_metadata`, including `.exe` names, while preserving read-only commands and quoted prose. Test provider-native public hook envelopes before accepting a writer-rule change.

## Git guard cannot inspect later child-process writes

The repository-state guard sees provider tool arguments before execution. It can block direct editor targets and recognizable literal shell or script text, but cannot prove what `python script.py`, PowerShell child processes, Git hooks, or other later processes will write. Copilot pre-tool hook timeouts also fail open. Treat OS sandbox policy as a separate layer only after inspecting its effective settings on the installed provider and platform; no global sandbox setting is changed by this repository.

## Empty RTK output is a valid no-op

When RTK exits `0` with empty or whitespace-only stdout, return `({}, None)` instead of attempting JSON parsing.

## Explicit RTK commands can show a misleading hook notice

RTK 0.49 can print `No hook installed` when an agent explicitly runs `rtk ...`, even when that command filters output. The provider RTK forwarders in `hooks/families/rtk.py` capture and discard subprocess stderr, so they do not directly display this notice. Diagnose the explicit CLI invocation before changing hook forwarding or suppressing hook errors.

## PowerShell command paths need runtime-specific forms

In installed Gemini settings, prefix Python files with `python` and wrap `$HOME/...` paths in escaped double quotes. In repo-local `.gemini/settings.json`, use workspace-relative `python .gemini/hooks/scripts/...py` commands; `$GEMINI_PROJECT_DIR` plus forward slashes can be split as a PowerShell expression.

## POSIX runtimes need Windows path conversion

Normalize drive-letter payload paths with `convert_windows_path_to_posix` before absolute-path checks. Keep the helper synchronized across `.copilot`, `.github`, and `.gemini`.

## Windows text stdout can reject Unicode JSON

CP1252 streams can raise a charmap error for non-ASCII payloads. `emit_json()` must write UTF-8 bytes through `sys.stdout.buffer`, with `sys.stdout.reconfigure(encoding="utf-8")` only as fallback.

## Open stdin can stall complete JSON payloads

Do not use `sys.stdin.read()` or one `readline()`. Incrementally decode until `JSONDecoder.raw_decode` finds one value, drain buffered bytes, reject non-whitespace trailing data, and bound incomplete input. Use `PeekNamedPipe` on Windows before Python 3.12. Keep provider helpers and open-stdin regressions synchronized.

## Copilot overrides repeated stop blocks

Copilot ends a turn after eight consecutive `agentStop` or `subagentStop` block continuations. `stop_hook_active` identifies an `agentStop` turn already forced by a prior block. Stop validators cannot guarantee an unlimited hard gate: keep them bounded and idempotent, self-limit before the platform cap, and test repeated-block behavior when changing final-response enforcement.

## Copilot CLI may hide unsupported hook response messages

In CLI 1.0.88, a successful `systemMessage` in ordinary `preToolUse`, `postToolUse`, or `agentStop` command-hook JSON produced invocation markers but no visible CLI message. For a visible delivery probe, emit a separate `{"type":"progress","message":"..."}` line before one final provider-valid JSON result; `additionalContext` reaches the model, not necessarily the terminal timeline. A one-second hook timeout can be fail-open and invisible in the CLI transcript: distinguish entry markers, absent completion markers, and the tool's actual result from any claim that the user saw a timeout.

## Copilot-only install should preserve custom user guidance

`scripts/install.ps1` also copies agent skills, Gemini settings, and Copilot global instructions. When a Copilot-only deployed check finds different user-global instructions, do not replace them with the repository copy: inspect and back up the exact maintained hook destinations and install only those hooks. Keep logs and unrelated user files untouched. Use a disposable workspace for the live test.

## Copilot native `create` needs an editor-tool guard

Copilot CLI 1.0.88 uses `create` for new files. A live disposable request to create a harmless file under `.git` succeeded while the guard covered `edit` but not `create`; a work-discarding Git command was separately denied. Treat `create` as an editor tool in the shared repository-state family, test the public Copilot envelope, regenerate provider outputs, and verify a fresh installed Copilot session denies the real native create without relying on shell-command detection.

## Gemini `AfterAgent` needs deployed-version proof

Upstream Gemini CLI issue `google-gemini/gemini-cli#27712` reports that configured `AfterAgent` hooks did not execute in version `0.45.0` and related builds. The issue remained open on 2026-09-16. Treat final-response enforcement through `AfterAgent` as version-sensitive and require a live capability probe on the deployed CLI instead of relying only on configuration or simulated tests.
