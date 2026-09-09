# Add a user-global required-skills hook for Codex CLI

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds. Maintain this plan in accordance with the repository's `exec-plans` skill.

## Purpose / Big Picture

After this change, running the repository installer will configure Codex CLI to load the body of `~/.agents/skills/caveman/SKILL.md` as developer context whenever a root Codex session starts, resumes, clears, or continues after compaction. A successful hook run will visibly announce `Required skill context loaded from {count} file(s).`, with `{count}` replaced by the number of loaded files. If a required skill is missing, unreadable, invalid, outside the installed skills tree, or too large, Codex will stop before normal work begins and explain the failure.

The feature is user-global. Repository source files remain inactive until installed, so working in this repository after a global install does not inject the same context twice. Installation preserves unrelated entries in an existing `~/.codex/hooks.json`, is idempotent, creates a recoverable backup before a real configuration change, and supports both the Bash and PowerShell installers without adding dependencies.

## Progress

- [x] (2026-09-09 13:35Z) [milestone-0] Confirmed the design tree, official Codex hook contract, public test seams, security constraints, and user-visible success announcement.
- [x] (2026-09-09 13:35Z) [milestone-0] Recorded later implementation ownership and validation commands in this ExecPlan.
- [ ] [milestone-1] Add one failing public hook test for successful `SessionStart` injection and the exact announcement, then add the smallest Codex hook implementation and configuration template that passes it.
- [ ] [milestone-1] Add hook tests one vertical slice at a time for all accepted failure, path, size, input, audit, and event-source behavior.
- [ ] [milestone-2] Add failing installer tests for absent and existing Codex configurations, then implement the shared atomic JSON merge and POSIX installation path.
- [ ] [milestone-2] Add installer tests one vertical slice at a time for idempotence, backup, malformed configuration, permissions, and partial-failure recovery.
- [ ] [milestone-3] Add failing PowerShell installer parity tests, then implement the PowerShell installation path using the same Python merge helper.
- [ ] [milestone-4] Run targeted and aggregate validation, inspect the complete diff, and perform a security-focused review.
- [ ] [milestone-5] Run the mandatory `update-agent-docs` pass, apply `okf-authoring`, run the OKF linter, and synchronize this plan's outcome sections.

## Surprises & Discoveries

- Observation: The repository currently has no Codex-specific hook source, installer destination, or tests.
  Evidence: Existing hook sources are under `.copilot/`, `.gemini/`, and `.github/`; repository searches found no `.codex` source tree.
- Observation: Codex user, project, managed, session, and plugin hooks can all match, and matching command hooks run concurrently.
  Evidence: The official Codex hook documentation says matching hook files merge and multiple matching command hooks for one event launch concurrently. The design therefore cannot rely on registration order and must avoid a simultaneously active project-local copy.
- Observation: Codex ordinary command handlers have no documented `name` identity field.
  Evidence: The documented handler schema includes `type`, `command`, `commandWindows`, `timeout`, `statusMessage`, `additionalContextLimit`, and `async`, but no stable name. Installer ownership must use the stable installed command path.
- Observation: Codex spills model-visible hook output above an approximately 2,500-token default.
  Evidence: The official documentation describes `additionalContextLimit` and recommends an explicit positive limit rather than unbounded output. The accepted design combines an 8,000-token handler threshold with a strict 20,000-byte script cap.
- Observation: `rtk` is unavailable in the current environment even though repository instructions prefer it.
  Evidence: `rtk` commands fail with `command not found`. During execution, report this once and use direct targeted commands rather than pretending the wrapper ran.

## Decision Log

- Decision: Install a user-global hook, not a project-local hook and not both.
  Rationale: This matches the existing Copilot and Gemini distribution model and prevents duplicate context when Codex merges hook layers.
  Date/Author: 2026-09-09, user and Codex.
- Decision: Register only synchronous `SessionStart`, matching `startup|resume|clear|compact`, with a five-second timeout; do not register `SubagentStart`.
  Rationale: This mirrors the currently registered required-skill behavior on Copilot and Gemini while reinjecting instructions after Codex compaction.
  Date/Author: 2026-09-09, user and Codex.
- Decision: Use Codex's native hard-stop output on required-skill failures.
  Rationale: `continue: false` and `stopReason` enforce the required instruction instead of relying on the model to obey a soft warning.
  Date/Author: 2026-09-09, user and Codex.
- Decision: Define `required_skill_files = ["caveman/SKILL.md"]` near the top of the hook and do not add an environment override.
  Rationale: The requested list is easy to edit, supports multiple skills, and avoids an undocumented handler environment field or arbitrary file injection through process state.
  Date/Author: 2026-09-09, user and Codex.
- Decision: Resolve required-skill entries only below `~/.agents/skills`, rejecting absolute paths, parent traversal, and symlink escapes.
  Rationale: Hook output enters the model context, so restricting the file source prevents accidental disclosure of unrelated local files or secrets.
  Date/Author: 2026-09-09, user and Codex.
- Decision: Cap final UTF-8 context at 20,000 bytes and set `additionalContextLimit` to 8,000.
  Rationale: The current Caveman skill is 7,022 bytes. The script cap keeps the hook bounded while the higher Codex threshold prevents the accepted bounded payload from spilling to a preview.
  Date/Author: 2026-09-09, user and Codex.
- Decision: Emit the exact success announcement `Required skill context loaded from {count} file(s).` through Codex's `systemMessage` field.
  Rationale: The user explicitly requested visible parity with Copilot and Gemini; Codex documents `systemMessage` as the user-visible common output field.
  Date/Author: 2026-09-09, user and Codex.
- Decision: Keep lightweight audit logging but do not port `send-event.py`, SQLite observability, NDJSON shadow logs, retention, or lifecycle-wide telemetry.
  Rationale: The requested feature needs local diagnostics, not the broader observability system. Concurrent hook execution would not preserve any assumed send-event ordering.
  Date/Author: 2026-09-09, user and Codex.
- Decision: Treat audit logging as best effort, but required-skill validation and loading as fail closed.
  Rationale: An unavailable audit file should not disable correctly loaded instructions; an unavailable required skill must stop work.
  Date/Author: 2026-09-09, user and Codex.
- Decision: Merge `~/.codex/hooks.json` atomically and idempotently, preserving unrelated user data and writing `hooks.json.bak` only before an actual change.
  Rationale: A global installer must coexist safely with user hooks and remain recoverable without creating unbounded timestamped backups.
  Date/Author: 2026-09-09, user and Codex.
- Decision: Keep the source template at `.codex/global-hooks.json` and the script at `.codex/hooks/load-required-skills.py`.
  Rationale: Codex auto-loads `.codex/hooks.json`, not `.codex/global-hooks.json`, so the maintained source remains inactive until installed.
  Date/Author: 2026-09-09, user and Codex.

## Outcomes & Retrospective

Planning is complete and implementation has not started. The accepted design is represented in this plan, including the later work split, validation evidence, and documentation obligations. Update this section after every completed milestone and replace this planning-only statement with the delivered behavior, remaining gaps, and lessons learned when the plan finishes.

## Context and Orientation

This repository publishes reusable skills from `skills/` and installs them under `~/.agents/skills`. It also maintains separate runtime-specific hook trees for Copilot and Gemini. `.copilot/hooks/scripts/load-required-skills.py` and `.gemini/hooks/scripts/skill-context-injector.py` demonstrate existing behavior: read configured skill files, remove YAML frontmatter, wrap each body in clear begin/end markers, inject it as model-visible context, announce success, and diagnose failures. Runtime-specific code must remain independent; the new Codex hook must not import from `.copilot` or `.gemini`.

Codex command hooks receive one JSON object on standard input. Common fields include `session_id`, `cwd`, and `hook_event_name`; `SessionStart` also receives `source`, whose current values are `startup`, `resume`, `clear`, and `compact`. A successful `SessionStart` hook can return `hookSpecificOutput` containing `hookEventName: "SessionStart"` and `additionalContext`. Common output can also include `systemMessage`. Returning `continue: false` with `stopReason` stops the session flow. Command hooks run synchronously unless `async` is true, and `commandWindows` overrides `command` on Windows. Non-managed hooks must be reviewed and trusted; changed hook definitions are skipped until reviewed again.

The maintained source configuration will be `.codex/global-hooks.json`. It will contain one `SessionStart` group with matcher `startup|resume|clear|compact` and one command handler. The POSIX command will invoke `python3 ~/.codex/hooks/load-required-skills.py`. The Windows override will invoke `py -3 "%USERPROFILE%\.codex\hooks\load-required-skills.py"`. The handler will use a five-second timeout, an 8,000-token `additionalContextLimit`, a concise status message, and synchronous execution.

The hook entry point will be `.codex/hooks/load-required-skills.py`. It will be a Python standard-library program with no imports from another runtime tree. Near the top it will expose the editable values `required_skill_files = ["caveman/SKILL.md"]` and `max_context_bytes = 20_000`. It will parse exactly one complete JSON object without requiring standard-input EOF, reject trailing non-whitespace, validate `hook_event_name == "SessionStart"` and the four accepted sources, and encode JSON to stdout as UTF-8. Stdout must contain exactly one final JSON object; diagnostics go to stderr or the audit file.

For each required entry, the hook will reject absolute paths and resolve the candidate below the resolved `~/.agents/skills` root. It will reject parent traversal and symlink escapes, require an existing readable regular file, read UTF-8 text, remove valid leading YAML frontmatter, and add `BEGIN REQUIRED SKILL` and `END REQUIRED SKILL` markers. The final injected context, including its prefix and markers, must not exceed `max_context_bytes` when UTF-8 encoded. Success returns the context and the exact count-bearing `systemMessage`. Failure returns `continue: false`, a concise `stopReason`, and `systemMessage: "Required skill context was NOT loaded."`, then exits zero so Codex can parse the decision.

The audit path will be `~/.codex/hooks/logs/audit.log`. The hook will create its directory with owner-only permissions and append sanitized event, source, session, loaded-path, and failure information through an owner-only descriptor. It must not log skill contents. Failure to create or append the audit emits a warning to stderr and otherwise leaves hook behavior unchanged.

The shared configuration merger will be `scripts/install-codex-hooks.py`, a Python standard-library CLI invoked by both installers. It will accept explicit source-template and destination paths so tests can use temporary directories. It will parse the maintained template and an existing destination, require JSON objects and the expected hook container shapes, remove only installed handlers whose command ends in the stable `~/.codex/hooks/load-required-skills.py` or Windows equivalent, prune only groups made empty by that removal, and append the maintained `SessionStart` group. It will preserve all unrelated keys, events, groups, and handlers. If the merged structure is semantically unchanged, it will not rewrite or back up the destination.

Before a real destination change, the merger will create or refresh `hooks.json.bak` from the previous valid destination, with owner-only permissions. It will serialize the new configuration to a same-directory temporary file, flush and synchronize it where supported, set owner-only permissions, and replace the destination atomically. It will clean temporary files on failure. Missing destination means start from an empty object and does not require a backup. Invalid JSON, a non-object root, or incompatible owned container shapes must fail with a clear stderr diagnostic without changing the destination or backup.

The POSIX installer is `scripts/install.sh`; its public behavior is tested by `scripts/test-install.sh`. The PowerShell installer is `scripts/install.ps1`; its public behavior is tested by `scripts/test-install.ps1`. Both will copy the Codex hook source to `~/.codex/hooks/load-required-skills.py`, make it executable where Unix modes apply, and invoke the same merger. They must not repurpose the process home in production code, add dependencies, or copy runtime logs from the source tree.

The dedicated hook contract test will be `scripts/test-codex-hooks-startup.sh`. Tests observe only public seams: execute the script as a process with JSON stdin and a temporary home, then inspect exit status, stdout JSON, stderr, and documented audit-file effects. Installer tests execute the installer against fixture repositories and temporary homes, then inspect installed files and JSON outputs. Tests must not import private hook or merger functions.

## Plan of Work

### Milestone 0: Record the executable design
Status: done
Acceptance: met

This plan captures every accepted design branch, the official Codex schema needed to implement it, the public seams approved for testing, the later file ownership split, and commands that demonstrate completion. No implementation file changes belong to this milestone.

### Milestone 1: Build the Codex hook through public process tests
Status: open
Acceptance: not met

Assign one implementation agent exclusive ownership of `.codex/hooks/load-required-skills.py`, `.codex/global-hooks.json`, and `scripts/test-codex-hooks-startup.sh`. The agent must activate the `tdd` skill before coding and work in vertical red-green slices.

Begin with a test that launches the hook for a `SessionStart` startup payload, supplies a temporary `~/.agents/skills/caveman/SKILL.md`, and expects stripped skill content, markers, the correct Codex hook-specific output, and the exact success announcement. Run it and capture the expected missing-script or missing-output failure before implementing the minimum success path. Continue one failing case at a time for resume, clear, compact, unsupported events, malformed and trailing input, missing/unreadable/non-file skills, absolute paths, parent traversal, symlink escape, malformed UTF-8, combined-size overflow, multiple editable list entries, audit permissions, audit write failure, stdout JSON discipline, UTF-8 output, and an input pipe that remains open after one complete JSON value.

Add `.codex/global-hooks.json` only after a failing assertion establishes its public schema. Verify exactly one `SessionStart` group, the accepted matcher, POSIX and Windows commands, timeout, context limit, status message, and absence of `SubagentStart`. Keep implementation self-contained and standard-library only.

### Milestone 2: Install and merge Codex hooks safely on POSIX
Status: open
Acceptance: not met

Assign a second implementation agent exclusive ownership of `scripts/install-codex-hooks.py`, `scripts/install.sh`, and `scripts/test-install.sh`. The agent must activate `tdd` before coding. The Milestone 1 agent owns the `.codex` fixture sources; coordinate only after those source filenames and config schema exist, without editing them.

First extend the installer fixture and add a test showing a temporary home with no Codex config receives the hook and a valid user-global config. Run the test red, then add the minimum copy and merge behavior. Add subsequent red-green slices for preserving unrelated top-level keys and hook events, preserving unrelated handlers in the same `SessionStart` group, replacing a prior owned handler, repeated-install idempotence without backup churn, creating and refreshing a single backup only on change, rejecting malformed and non-object JSON without mutation, owner-only destination and backup modes, executable hook mode, same-directory temporary cleanup, and retry after an interrupted or failed merge.

Do not duplicate JSON merge logic in shell. `scripts/install.sh` should validate required Codex sources, create the destination directory, copy the maintained script, apply executable mode, invoke `scripts/install-codex-hooks.py`, and report the installed Codex paths alongside existing installer output.

### Milestone 3: Add PowerShell parity
Status: open
Acceptance: not met

Assign a third implementation agent exclusive ownership of `scripts/install.ps1` and `scripts/test-install.ps1`. The agent must activate `tdd` before coding. It may rely on the public CLI of `scripts/install-codex-hooks.py` but must not edit that helper. Add a failing fixture-level test before adding Codex installation. Verify the copied script, merged config, preservation and idempotence behavior, exact `commandWindows` value, and Unix executable mode on non-Windows hosts. Keep the script `-NoProfile` compatible and use no external PowerShell modules.

If Python executable discovery differs across Windows and non-Windows PowerShell, use the repository's existing Python dependency and choose an explicit, tested invocation without shell-string evaluation. Do not fork the merge algorithm into PowerShell.

### Milestone 4: Integrate, validate, and review
Status: open
Acceptance: not met

The root agent owns integration and must not make simultaneous edits to files assigned to active implementation agents. After all three agents finish, inspect their diffs and run the focused suites. Resolve failures in the owning area with another red-green slice. Then run syntax checks and aggregate relevant tests.

Perform a security-focused review across the complete diff. Confirm that stdin and JSON sizes are bounded, skill paths cannot escape the installed skills root through traversal or symlinks, no contents enter logs, file creation modes are restrictive at descriptor creation, config writes are atomic, backups are bounded, malformed existing user data is never overwritten, shell commands do not interpolate untrusted input, and no secrets or dependencies were added. Also confirm Codex output uses documented fields and success stdout is one JSON document.

### Milestone 5: Synchronize human and agent documentation
Status: open
Acceptance: not met

The root agent exclusively owns `README.md`, `AGENTS.md`, `.agents/instructions/`, `.agents/memory/`, and this ExecPlan. Update README installation destinations, behavior, trust review through `/hooks`, configuration preservation, and validation commands. Update the opening repository scope in `AGENTS.md` without modifying its protected sections.

Run the mandatory `update-agent-docs` workflow after implementation and validation. At minimum, assess `.agents/instructions/hooks.md`, `.agents/memory/FILE_MAP.md`, `.agents/memory/ARCHITECTURE.md`, `.agents/memory/API_MAP.md`, and `.agents/memory/testing/hooks.md`; add only durable current-state guidance and remove nearby stale statements. No new memory file is expected, so `.agents/memory/INDEX.md` should change only if actual routing changes.

After semantic edits under `.agents/instructions/` or `.agents/memory/`, activate `okf-authoring`, read its shared profile, apply only required representation changes, and run `./scripts/lint-okf.py`. Inspect the scoped documentation diff and confirm it contains only authorized paths. Finally synchronize every milestone status, Progress checkbox, discovery, decision, and the retrospective in this plan.

## Concrete Steps

All commands run from `/Users/adam/.codex/worktrees/84b7/skills`. `rtk` should prefix commands when available; on the current host it is unavailable, so report that fact and run the exact targeted commands directly.

Before implementation, verify the working tree and plan:

    git status --short
    sed -n '1,9999p' docs/codex-load-required-skills/execplan.md

For each TDD slice, run the narrow public suite and observe a meaningful assertion fail before adding implementation:

    bash scripts/test-codex-hooks-startup.sh
    bash scripts/test-install.sh
    pwsh -NoProfile -File scripts/test-install.ps1

After implementation, run syntax checks and the complete affected validation set:

    python3 -m py_compile .codex/hooks/load-required-skills.py scripts/install-codex-hooks.py
    bash -n scripts/install.sh scripts/test-codex-hooks-startup.sh scripts/test-install.sh
    bash scripts/test-codex-hooks-startup.sh
    bash scripts/test-install.sh
    pwsh -NoProfile -File scripts/test-install.ps1
    python scripts/test_helpers.py
    ./scripts/lint-okf.py

If `pwsh` is unavailable, record the exact unavailable-command evidence, keep the PowerShell work unverified, and do not claim cross-platform completion. Do not install into the real home directory during automated validation; repository guidance says installed targets may be outside the writable workspace. Fixture tests must set a child process's home before launch and use only a `mktemp`-created test directory.

For a manual hook smoke test, use a temporary home containing a copied Caveman fixture, send a `SessionStart` JSON object to the source hook, and inspect the single stdout object. Expected fields include:

    systemMessage: Required skill context loaded from 1 file(s).
    hookSpecificOutput.hookEventName: SessionStart
    hookSpecificOutput.additionalContext: Required skill context loaded. ...

For a manual failure smoke test, point the temporary home at an absent skill. Expected fields include:

    continue: false
    systemMessage: Required skill context was NOT loaded.
    stopReason: Required skill file not found: ...

## Validation and Acceptance

Acceptance requires all of the following observable behaviors:

1. A root Codex `SessionStart` payload for each documented source loads the frontmatter-free Caveman body, includes begin/end markers, returns the documented hook-specific context shape, and announces exactly `Required skill context loaded from 1 file(s).`.
2. No `SubagentStart` handler is installed. The `SessionStart` matcher covers `startup`, `resume`, `clear`, and `compact`; the handler is synchronous, times out after five seconds, and sets `additionalContextLimit` to 8,000.
3. Required-skill failures return parseable JSON with `continue: false` and a useful reason while exiting zero. Invalid input, escape paths, symlink escapes, invalid UTF-8, and output above 20,000 UTF-8 bytes are covered.
4. The hook writes no skill content to logs. The audit directory and file are owner-only, and audit failures warn without suppressing otherwise valid injected context.
5. A fresh install creates `~/.codex/hooks/load-required-skills.py` and `~/.codex/hooks.json`. An existing valid config keeps every unrelated value. A second install causes no semantic change and does not churn the backup.
6. A real config change preserves the immediately previous valid file as owner-only `hooks.json.bak`, writes the new file atomically with owner-only permissions, and leaves no temporary file. Malformed or non-object existing JSON remains byte-for-byte unchanged.
7. Bash and PowerShell installer suites pass through their public process seams. No new package or module dependency appears.
8. README and agent documentation describe the installed Codex surface, trust review, testing route, and durable constraints. The OKF linter exits zero after the documentation pass.
9. The final diff contains only the Codex hook, its installer integration and tests, necessary human/agent documentation, and this plan. Unrelated user changes remain untouched.

## Idempotence and Recovery

All test and installer operations must be repeatable. The hook is read-only except for its append-only audit file. Installer configuration merge first validates both JSON inputs in memory, computes an owned-handler replacement, and compares the semantic result before touching disk. A no-change install leaves both destination and backup untouched.

On a changed valid destination, `hooks.json.bak` is the immediate rollback file. Restoring consists of stopping Codex, copying `hooks.json.bak` over `hooks.json`, and reviewing trust again through `/hooks`. A merge failure leaves the original destination unchanged; an already copied but unreferenced hook script is harmless and will be reused on retry. Same-directory temporary files are removed in `finally` cleanup. No cleanup command may target the home directory, repository root, or an unresolved variable.

If a hook run cannot write its audit, it warns and continues with the computed success or failure response. If a required skill fails validation, recovery is to restore a readable `~/.agents/skills/<relative path>` or edit the source-level `required_skill_files` list, reinstall, and review the changed hook definition through `/hooks`.

## Artifacts and Notes

The implementation is governed by the official Codex Hooks documentation at `https://learn.chatgpt.com/docs/hooks`, fetched on 2026-09-09. The plan embeds the relevant contract so implementation does not depend on remembering the page: user-global configuration is `~/.codex/hooks.json`; command handlers use `command` and optional `commandWindows`; `SessionStart` matcher values are `startup`, `resume`, `clear`, and `compact`; success context uses `hookSpecificOutput.additionalContext`; common output supports `systemMessage`; `continue: false` plus `stopReason` stops the flow; matching hooks run concurrently; non-managed hooks require trust review; and `additionalContextLimit` controls output spilling.

No ADR is planned. The source layout, merge identity, limits, and failure policy are localized, directly tested, and inexpensive to revise; they do not meet the repository's threshold for a hard-to-reverse architectural record.

## Interfaces and Dependencies

The implementation must use Python's standard library only. No dependency installation or lockfile change is authorized.

`.codex/hooks/load-required-skills.py` is a process interface. It accepts one Codex hook JSON object on stdin and returns one JSON object on stdout. Its editable source configuration is:

    required_skill_files = ["caveman/SKILL.md"]
    max_context_bytes = 20_000

On success, the public output contract is:

    {
      "systemMessage": "Required skill context loaded from 1 file(s).",
      "hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": "Required skill context loaded.\n\n..."
      }
    }

On failure, the public output contract is:

    {
      "continue": false,
      "stopReason": "<concise reason>",
      "systemMessage": "Required skill context was NOT loaded."
    }

`scripts/install-codex-hooks.py` is a process interface shared by both installers. It must expose explicit command-line arguments for the maintained source template and destination `hooks.json`, return zero on successful creation, merge, or no-op, and return nonzero with a concise stderr diagnostic on invalid input or write failure. Its exact option names must be established by the first public CLI test and then documented in its `--help` output.

The hook configuration handler interface is fixed as follows:

    event: SessionStart
    matcher: startup|resume|clear|compact
    type: command
    command: python3 ~/.codex/hooks/load-required-skills.py
    commandWindows: py -3 "%USERPROFILE%\.codex\hooks\load-required-skills.py"
    timeout: 5
    additionalContextLimit: 8000
    async: omitted, therefore synchronous

Implementation ownership during later execution is non-overlapping:

- Hook agent: `.codex/hooks/load-required-skills.py`, `.codex/global-hooks.json`, `scripts/test-codex-hooks-startup.sh`.
- POSIX/merge agent: `scripts/install-codex-hooks.py`, `scripts/install.sh`, `scripts/test-install.sh`.
- PowerShell agent: `scripts/install.ps1`, `scripts/test-install.ps1`.
- Root agent: `README.md`, `AGENTS.md`, `.agents/instructions/`, `.agents/memory/`, this ExecPlan, integration fixes after agents finish, final review, and validation.

Revision note (2026-09-09): Created the initial implementation-ready ExecPlan after the user accepted every design-tree recommendation and added the exact success-announcement requirement. Implementation intentionally remains unstarted.

Revision note (2026-09-09): Moved the ExecPlan from the transient `.agents/scratchpad/` location to the version-controlled `docs/codex-load-required-skills/` feature directory at the user's request, and updated its self-verification command.
