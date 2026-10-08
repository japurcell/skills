---
type: Agent Instruction
description: Copilot CLI, cloud, and VS Code hook events, output schemas, and compatibility.
---

# Copilot and VS Code Hooks

Read [shared hook rules](hooks.md) for implementation changes. For precise provider behavior, inspect the [Copilot source reference](../sources/copilot-hooks-ref.md) or [VS Code source reference](../sources/vscode-agent-hooks.md), then current official documentation or deployed evidence when version-sensitive.

- **Copilot surface split:** Copilot CLI can load policy, repository, user, inline-settings, and plugin hooks, but Copilot cloud agent only reads `.github/hooks/*.json` in the cloned repo and runs them inside a Linux, non-interactive, ephemeral sandbox where only `bash` or fallback `command` entries are honored.
- **Copilot progress output:** Command hooks may emit one-line progress JSON objects on stdout during execution, but they still need exactly one final non-progress JSON document for the actual hook result.
- **Copilot post-tool event split:** `postToolUse` fires only after successful tool completion. Handle failed tools through `postToolUseFailure`, whose output can add recovery context but cannot retroactively block or undo the failed tool.
- **Copilot stop-loop bound:** Keep stop validators bounded and idempotent. For `agentStop`, use `stop_hook_active` to detect a turn already forced by a prior block and self-limit before Copilot's eight-consecutive-block runaway guard overrides the hook.
- **Copilot required-skill announcement:** `.copilot/hooks/scripts/load-required-skills.py` emits a display-only progress message, `Required skill context loaded from N file(s).`, before its final `additionalContext` JSON for Copilot CLI-shaped payloads when required skills load. Supported progress payloads have no event name or a lowerCamelCase event name such as `sessionStart` or `subagentStart`; VS Code-compatible PascalCase events keep stdout to one final JSON object.
- **Copilot fail behavior:** `userPromptTransformed` can rewrite only the transformed prompt text. Command `preToolUse` hooks fail closed on non-timeout errors, but timeouts stay fail-open. For block-mode policy denials, emit structured deny JSON and exit `0` so Copilot surfaces `permissionDecisionReason` instead of only generic failure output.
- **VS Code compatibility:** VS Code accepts Claude and Copilot hook formats, maps Copilot lowerCamelCase event names to PascalCase, ignores Claude matcher filters, and only enables custom-agent frontmatter hooks when `chat.useCustomAgentHooks` is on.

- **GitHub Hooks Scope:**
  - `agentStop` / `subagentStop` outputs must use: `{ "decision": "allow|block", "reason": ... }`
  - `postToolUse` formatting hooks should emit valid JSON only: use `{}` for no-op success, or `{ "additionalContext": ... }` when the agent should see a formatter/setup failure.
  - `preToolUse` / `PreToolUse` command hooks can control tool execution via `"permissionDecision"`. Set to `"ask"` to trigger a manual interactive confirmation dialog in Copilot CLI, or set to `"allow"` to silently execute the tool call or rewritten `updatedInput` without prompts.
  - Expected `agentStop` and `postToolUse` control flow must exit `0` so Copilot parses `stdout` JSON. Exit code `2` is warning-only for most GitHub hook events and does not apply these decision schemas.

- On Windows systems, Copilot hooks config (e.g. `hooks.json` and `rtk-rewrite.json`) must explicitly define both `"bash"` (Unix) and `"powershell"` (Windows) keys for command hooks to execute natively and in VS Code on Windows.
- In `.copilot/hooks/hooks.json`, keep both `subagentStart` (CLI) and `SubagentStart` (VS Code).
- CLI responses return top-level `additionalContext`; VS Code responses return `hookSpecificOutput` plus `additionalContext`.
- Prefer `agentStop` over `subagentStop` for final-response quality validators; `subagentStop` has no matcher support in Copilot hook docs and built-in `general-purpose` agents do not emit `subagentStart` or `subagentStop`.
- Keep `SessionStart` injection path active even when `SubagentStart` exists because some VS Code `runSubagent` child sessions omit `SubagentStart`.

For installed event delivery and terminal visibility, use [live-hook testing](testing/hooks-live.md). A timeout may fail open; handler invocation alone does not prove that a user saw a message.
