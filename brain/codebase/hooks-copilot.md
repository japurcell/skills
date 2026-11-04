# Copilot hooks

- `.copilot/hooks` supplies user-level hooks; `.github/hooks` supplies repository hooks. Brain hooks belong only in `.github/hooks`.
- CLI hooks combine user and project configuration; cloud agent reads `.github/hooks/*.json` in its Linux sandbox.
- `sessionStart` receives `cwd` and startup/resume/new source; return top-level `additionalContext`.
- Native camelCase `sessionStart` payloads have no event-name field. PascalCase compatibility payloads include `hook_event_name`. Do not require an event-name field for startup status after admitting native input.
- `postToolUse` carries successful `toolResult.resultType`; failure has a separate event. PascalCase compatibility uses snake_case payloads.
- Use `bash` and `powershell` launch commands; cloud honors POSIX commands. `timeoutSec` is seconds.
- CLI progress output and VS Code compatibility differ. Use final provider JSON and verify user-visible delivery separately.
- Command pre-tool errors deny tools, but timeouts fail open; do not treat all command failures as equivalent.
- Preserve stop-loop guards in validators. Keep diagnostic stdout separate from protocol output.

## Decision and lifecycle changes

- `userPromptTransformed` changes model-facing content via `modifiedTransformedPrompt`; it cannot block a turn.
- Intentional `preToolUse` denial returns `permissionDecision: "deny"` and `permissionDecisionReason` at exit 0. `allow` can execute without approval; `modifiedArgs` rewrites arguments. `ask` requests approval only where prompting is available; cloud/autopilot deny it.
- Main-response validation uses `agentStop`; `agentStop`/`subagentStop` return `decision: "allow"|"block"`, with a nonempty `reason` for block. This is separate from this repository's informational End Turn status.
- Post-tool formatters return `{}` for no change or `additionalContext` for actionable failure guidance. Use exit 0 for expected JSON decisions. Exit 2 is generally a warning, with event-specific exceptions documented in the reference; timeouts always fail open.
- `subagentStart` has an agent-name matcher; `subagentStop` has no documented matcher. The checked reference excludes built-in `general-purpose` from both lifecycle events. Recheck coverage for the deployed version before relying on either event.
- The required-skill loader's direct legacy-envelope tests do not prove registration or delivery. Its Copilot subagent registrations were already absent before the brain migration; commit `711c1797` removed PascalCase registration intentionally.

Fixed on 2026-10-22: native Copilot startup payloads now emit progress after successful brain injection without requiring an event-name field. The canonical change is in `hooks/families/brain.py`; provider and brain-install bundle outputs were regenerated. The regression test runs the registered command with native startup/resume/new payloads; compatibility tests retain `hook_event_name`. Live Copilot CLI 1.0.103 displayed `inject-brain: pass; index loaded` when the first prompt triggered startup hooks, and debug logs contained brain context. CLI evidence does not establish VS Code delivery.

Source: [official hooks reference](https://docs.github.com/en/copilot/reference/hooks-reference), native startup schema and progress protocol checked 2026-10-22; decision/lifecycle fields rechecked 2026-10-21. Recheck after provider changes. See [hooks-vscode](hooks-vscode.md) for harness selection.
