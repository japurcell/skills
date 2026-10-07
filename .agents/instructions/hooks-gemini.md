---
type: Agent Instruction
description: Gemini hook events, configuration, validation schemas, and deployed-version checks.
---

# Gemini Hooks

Read [shared hook rules](hooks.md) for implementation changes. For precise provider behavior, inspect the [saved overview](../sources/gemini-hooks.md) and [exit-code reference](../sources/gemini-hooks-best-practices.md), then verify current documentation or the deployed version when needed.

- **Gemini precedence and trust:** Gemini merges hook config in project, user, system, then extension order; project hook trust is fingerprinted from `name` plus `command`, and changed project hooks are warned as new.
- **Gemini selection and redaction:** Multiple Gemini `BeforeToolSelection` hooks union their allowed tool sets, and environment-variable redaction is off by default unless explicitly enabled and allowlisted.

- **Gemini Hooks Scope:**
  - Setup errors must use: `{ "continue": false, "stopReason": ... }`
  - Validation failures must use: `{ "decision": "deny", "reason": ... }`
  - Expected hook control flow must use exit code `0`, with JSON on `stdout` driving the decision. Reserve exit code `2` for true system-block cases that should use `stderr` as the reason.

- For final-response quality validators, prefer `AfterAgent` over `AfterModel`.
- Use `prompt_response` as the text under review.
- Honor `stop_hook_active` to avoid retry loops.

- In installed settings, prefix Python paths with `python` and quote `$HOME/...` paths. In project `.gemini/settings.json`, use workspace-relative `python .gemini/hooks/scripts/...py` commands; preserve native PowerShell coverage.
- Require a live capability probe before claiming `AfterAgent` enforcement on a deployed CLI. Inspect per-event entry, completion, and visible output independently; use [live-hook testing](testing/hooks-live.md).
