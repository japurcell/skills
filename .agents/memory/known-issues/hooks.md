---
type: Known Issue
description: General provider-hook failures; specialized auto-ingest and observability issues live in focused sibling files
---

# Hooks - Known Issues

Load this file for general provider-hook work. For source scanners, manifests, summaries, injectors, or pending gates, read [Hook Auto-Ingest - Known Issues](hooks-auto-ingest.md). For emitters, SQLite traces, transcripts, logs, or maintenance, read [Hook Observability - Known Issues](hooks-observability.md).

## Active guards can block their own maintenance

Tool Guardian scans patch, search, replacement, and cleanup payloads. Raw dangerous command strings can block safe policy edits or tests; multiline serialized text can also create false matches across escaped newlines. Construct required threat strings dynamically, keep unrelated dangerous lines outside replacement hunks, and keep deletion-target matching bounded to one logical line and a short distance.

Secret scanning has the same self-edit risk for realistic fake credentials. Use unmistakably fake values such as `fake-api-key`; never write a real secret.

Large multi-file Markdown patches can hit Tool Guardian's 128-command-segment limit before mutation. Split the work into focused patches instead of retrying the same oversized payload; this limit is distinct from structured byte and string limits.

## Structured input can reach its byte limit before text scanning

Tool Guardian traverses structured input before matching command text. A large `write_file.content` value therefore reports `structured_bytes` first, with its 32768-byte threshold and measured UTF-8 byte count. The generic scan-text limit applies to later text scanning and includes the tool name prefix. Keep those counts and units distinct when adding rule details or tests.

## Same-named hook modules confuse mypy

Copilot and Gemini contain same-relative-path modules such as `observability.py`. Run mypy on each file separately instead of passing both in one invocation.

## Bash `RETURN` traps can outlive local variables

Under `set -u`, interpolate function-local cleanup paths when registering the trap, for example `trap 'rm -rf -- "'"$workdir"'"' RETURN`. At trap execution, the local variable may no longer exist.

## Secret-scanner Git probes can hang on Windows

Run Git with `GIT_TERMINAL_PROMPT=0`, an empty `GIT_ASKPASS`, and a short timeout. Let timeout errors reach the top-level handler so block mode denies; warn mode may emit a sanitized no-op.

The native Windows `gemini/block/descendant` and `gemini/warn/oversized` fixtures intermittently saw a `tmp*` Git-output capture file immediately after the hook returned. A diagnostic replay found synthetic `PING.EXE` alive after the hook exited. Earlier, `handle64` found no handle by the time its scan completed, so neither observation established the file-handle owner. Cleanup must terminate the Git root and observed children before waiting on any one process, remember ancestor PIDs, and rescan within its bounded deadline for children spawned after the first snapshot. The complete native workflow passed twice after this change, including five extra repeats of each fixture per attempt. Keep the immediate `tmp*` assertion and exact provider/mode/scenario/filename failure text; a recurrence needs fresh process and handle evidence.

## Extensionless commands fail on Windows

With `shell=False`, resolve commands such as `rtk` through `shutil.which()` so `.cmd` or `.bat` executables are found.


## Empty RTK output is a valid no-op

When RTK exits `0` with empty or whitespace-only stdout, return `({}, None)` instead of attempting JSON parsing.

## Explicit RTK command notice

RTK 0.49 can print `No hook installed` when an agent explicitly runs `rtk ...`, even when that command filters output. Stable RTK 0.50.0 supports `hooks.suppress_hook_warning = true`; both installers set it in user config. The Copilot and Gemini forwarders still capture subprocess stderr and never display that notice directly. Diagnose explicit CLI behavior separately from automatic forwarding.

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

## Retired installed hooks require manual cleanup

The Bash and PowerShell installers preserve existing Copilot and Gemini registrations that are absent from maintained source when refreshing a user home. This includes retired repository-state and Markdown Health entries. Fresh installs receive only current source registrations. An old installed registration and its script can therefore continue to execute until the user removes them manually; source and fresh-home checks do not certify an existing home.

## Gemini `AfterAgent` needs deployed-version proof

Upstream Gemini CLI issue `google-gemini/gemini-cli#27712` reports that configured `AfterAgent` hooks did not execute in version `0.45.0` and related builds. The issue remained open on 2026-09-16. Treat final-response enforcement through `AfterAgent` as version-sensitive and require a live capability probe on the deployed CLI instead of relying only on configuration or simulated tests.

On Windows with Gemini CLI 0.60.0, a one-second probe displayed a timeout yet recorded no `BeforeTool` entry, even with the probe handler first; the harmless tool still ran. The same handler and matcher at two seconds recorded all three event entries and passed timeout verification. This does not isolate process-start latency as the cause or establish one-second enforcement. Check each event's entry and completion markers, not just the visible timeout text. A separate nonce-visible `SessionEnd` probe and a live incomplete scanner warning prove those other events independently.
