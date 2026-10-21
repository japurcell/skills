# Gemini hooks

- Project configuration is `.gemini/settings.json`; installed user configuration is `~/.gemini/settings.json`.
- `SessionStart` supports startup/resume/clear; context uses `hookSpecificOutput.additionalContext`.
- `AfterTool` supplies `tool_response` with optional `error`. `PreCompress` is an asynchronous notification, not a documented context injection point.
- `command` uses the host shell; timeout units are milliseconds. Installed commands must quote interpreter and script paths for the target shell.
- Keep stdout JSON-only. Native denial fields drive expected control flow at exit 0; exit 2 is a system-level block.
- For response validation, use `AfterAgent`, `prompt_response`, and `stop_hook_active`; `AfterModel` can run during streaming.
- Changed project hook name/command combinations require trust review. Avoid recording environment values or assuming redaction is enabled.
- Confirm the deployed CLI's event entry, completion, and visible outcome before claiming enforcement.

## Configuration and failure changes

- Hook configurations merge across layers; documented priority is project, user, system, then extension. Priority does not mean the higher layer replaces every lower-layer hook.
- `BeforeToolSelection` unions `allowedFunctionNames` across hooks; `toolConfig.mode: "NONE"` disables all tools and wins. It does not support `decision`, `continue`, or `systemMessage`.
- For required-context setup failure on events that honor flow control, emit `continue: false` with `stopReason`. For validation denial, use the event's `decision: "deny"` and `reason` fields; `AfterAgent` denial requests a retry, while `continue: false` stops without retry.
- Current reference says `SessionStart` ignores `continue` and `decision`. A loader fixture returning a setup-abort envelope does not prove native startup blocking. Preserve this limitation when evaluating missing-context behavior.

Sources: [reference](https://geminicli.com/docs/hooks/reference/), [overview](https://geminicli.com/docs/hooks/), configuration and flow-control fields rechecked 2026-10-21. Gemini is absent on this host; live behavior remains unverified. Recheck after CLI/schema changes.
