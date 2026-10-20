# Codex hooks

- Runtime discovery uses `.codex/hooks.json` in a project and user-global `hooks.json`. This repository's `.codex/global-hooks.json` is an inactive installer template.
- `SessionStart` supports startup, resume, clear, compact, and fork. Context JSON uses `hookSpecificOutput.hookEventName: SessionStart` plus `additionalContext`.
- `PostToolUse` also fires after failed Bash commands. Its tool-specific response has no documented universal success field; never infer success by parsing arbitrary output text.
- Use POSIX `command`, Windows `commandWindows`, and timeouts in seconds. Set context limits deliberately; larger context can spill to a file.
- When a worktree hook calls a deleted script, inspect the configuration source named in `hook_run_id` as well as the worktree config. A primary-checkout registration can resolve its command against the worktree cwd.
- Non-managed hooks need trust review through `/hooks` after changes. Do not bypass trust.
- Registered global scripts must appear in both installer copy lists and maintained ownership sets. Preserve unrelated handlers and refuse linked configuration destinations.
- Required-skill injection distinguishes raw file limits from final context limits. Audit destinations reject symlinks and reparse points.
- The maintained required-skill loader emits one JSON document with loaded text in `hookSpecificOutput.additionalContext`, a loaded-file count in `systemMessage`, and `continue: false` when required context cannot be loaded. Keep its runtime self-contained.

Source: [official hooks reference](https://learn.chatgpt.com/docs/hooks), checked 2026-10-20. Local CLI 0.163.0 is installed; this is not live context-delivery proof. Recheck after provider/schema changes.

Local evidence (2026-10-20): the Stop error named the primary checkout hook file while Python tried the removed worktree OKF adapter. The primary checkout still held its old registration; the migrated worktree did not. This records the observed source/cwd split, not a general guarantee about reload behavior.
