---
coverage: Rules and conventions for git and Gemini hooks under `{.copilot,.gemini}/hooks`.
---

# Git & Gemini Hooks Conventions

Guidelines for modifying and maintaining repository hook scripts under `{.copilot,.gemini}/hooks`.

## Official References

- **GitHub Copilot hooks reference:** `https://docs.github.com/en/copilot/reference/hooks-reference`
- **VS Code GitHub Copilot hooks reference:** `https://code.visualstudio.com/docs/copilot/customization/hooks`
- **Gemini CLI hooks reference:** `https://github.com/google-gemini/gemini-cli/blob/main/docs/hooks/reference.md`
- **Gemini CLI exit-code best practices:** `https://geminicli.com/docs/hooks/best-practices/#check-exit-codes`

Read official docs before non-trivial hook changes and keep implementation choices aligned with them.

## Shared Runtime Rules

- **stdout discipline:** Hook scripts must keep `stdout` JSON-only. Send logs, audit lines, and debug text to `stderr` or the audit log.
- **installed-copy rule:** Run `./scripts/install.sh` before live validation because Copilot and Gemini execute installed hooks from home-directory targets.

## Output Schemas & Exit Behavior

- **Gemini Hooks Scope:**
  - Setup errors must use: `{ "continue": false, "stopReason": ... }`
  - Validation failures must use: `{ "decision": "deny", "reason": ... }`
  - Expected hook control flow must use exit code `0`, with JSON on `stdout` driving the decision. Reserve exit code `2` for true system-block cases that should use `stderr` as the reason.
- **GitHub Hooks Scope:**
  - `agentStop` / `subagentStop` outputs must use: `{ "decision": "allow|block", "reason": ... }`
  - `postToolUse` formatting hooks should emit valid JSON only: use `{}` for no-op success, or `{ "additionalContext": ... }` when the agent should see a formatter/setup failure.
  - Expected `agentStop` and `postToolUse` control flow must exit `0` so Copilot parses `stdout` JSON. Exit code `2` is warning-only for most GitHub hook events and does not apply these decision schemas.

## Copilot and VS Code compatibility

- In `.copilot/hooks/hooks.json`, keep both `subagentStart` (CLI) and `SubagentStart` (VS Code).
- CLI responses return top-level `additionalContext`; VS Code responses return `hookSpecificOutput` plus `additionalContext`.
- Prefer `agentStop` over `subagentStop` for final-response quality validators; `subagentStop` has no matcher support in Copilot hook docs and built-in `general-purpose` agents do not emit `subagentStart` or `subagentStop`.
- Keep `SessionStart` injection path active even when `SubagentStart` exists because some VS Code `runSubagent` child sessions omit `SubagentStart`.

## Repo-specific hook gotchas

- The supported hook surface is the Python operational entrypoints and Python observability emitters.
- Keep `send-event.py` registered in every supported Copilot hook event block so observability stays complete across surfaces.
- Keep `send-event.py` registered in every supported Gemini hook event block, including the lifecycle hooks that do not currently have other operational behavior (`BeforeAgent`, `BeforeModel`, `AfterModel`, `BeforeToolSelection`, `AfterTool`, `PreCompress`) so the installed config stays fully observable.
- For passive shadow logging, create shadow-log parent directory before first write and keep primary plus shadow writes inside same lock section so event ordering survives.
- When editing security-hook threat patterns or Tool Guard tests, avoid pasting raw dangerous strings directly into tool payloads; construct exact strings dynamically so active guards do not block self-edits.

## Validation route

- Run targeted checks from `.agents/memory/testing/hooks.md`.
- Distinguish repo-source proof from installed/live proof.

## Gemini-specific validator guidance

- For final-response quality validators, prefer `AfterAgent` over `AfterModel`.
- Use `prompt_response` as the text under review.
- Honor `stop_hook_active` to avoid retry loops.
