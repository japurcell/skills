# Provider binding contract: facts for native adapters

Checked 2026-09-30 against current official documentation. These are documented contracts, not deployed-version observations or certification. Existing context: [provider lifecycle capabilities](../provider-lifecycle-capabilities/findings.md) and [stage invocation interfaces](../context-stage-invocation/findings.md). The latter notes Codex app-server is experimental/unsupported for production and does not document attachment to an existing desktop conversation. Codex docs use “Codex” generically; applicability to standalone Codex desktop versus this installed ChatGPT host is unverified.

## Codex hooks

Official [hooks reference](https://learn.chatgpt.com/docs/hooks) says hook sources are `hooks.json` or inline `[hooks]` in `config.toml` beside active config layers, with common user paths `~/.codex/hooks.json` and `~/.codex/config.toml`, and repo paths `<repo>/.codex/hooks.json` and `<repo>/.codex/config.toml`; plugin manifests can contribute lifecycle configuration. Matching sources merge. Hooks are enabled by default unless feature/admin configuration disables them. No desktop-versus-CLI installation parity certification is given here.

- `SessionStart` matcher distinguishes `startup`, `resume`, `clear`, and `compact`; common payload includes `session_id`, `transcript_path` (nullable), `cwd`, event name, model, and permission mode. Session-start response can inject context (`systemMessage`/event-specific context). It is a lifecycle notification and may happen on resume/compact, not just fresh startup.
- `UserPromptSubmit` includes active `turn_id` and prompt; stdout context augments developer context, and `decision: block` with reason can block the prompt.
- `PreToolUse` gets tool name/input; supports denying, adding context, or rewriting supported local tool input. It is not comprehensive for hosted tools/specialized opt-out paths. `PostToolUse` follows tool execution; it cannot undo effects.
- `PreCompact`/`PostCompact` carry compaction trigger. Shared `continue:false`/stop output can continue/block at supported turn events; compact is not a fresh session. Transcript format is explicitly unstable.
- `SubagentStart` carries parent session ID, turn ID, agent ID/type and can add context, but `continue:false` does not prevent startup. `SubagentStop` supports continuation. Payload identifies subagent separately; it does not establish independent child session IDs.
- `Stop` supports block-and-reason continuation. `SessionEnd` is main-thread-only and not a semantic completion guarantee; do not equate with task success.

## GitHub Copilot CLI hooks

Official [hooks reference](https://docs.github.com/en/copilot/reference/hooks-reference) describes CLI local execution and distinct cloud-agent environment (out of scope). CLI sources are policy files, repo `.github/hooks/*.json`, user `~/.copilot/hooks/*.json` (or `$COPILOT_HOME/hooks`), inline repo `.github/copilot/settings[.local].json`, user `~/.copilot/settings.json`, and plugin hooks; sources combine in policy/user/project/plugin order. `settings.json` can disable all non-policy hooks.

- Native camelCase event names use camelCase payload; PascalCase names select VS Code-compatible snake_case schema. This is a schema choice, not evidence that the VS Code harness is supported here.
- `sessionStart` identifies session, cwd and source (`startup|resume|new`), with optional initial prompt; output `additionalContext` is consumed. `userPromptSubmitted` input exists, but command hook output is ignored; `userPromptTransformed` is the model-facing rewrite event.
- `preToolUse` identifies session, cwd, tool name and arguments; output allows/denies/asks or modifies arguments. Command errors fail closed for this event except timeouts, which fail open. `postToolUse` can modify result/add model context after action.
- `preCompact` has trigger and transcript path but is notification-only. No post-compaction event documented in the reference.
- `subagentStart` supplies `agentName`, session ID, cwd and transcript path; adds context but cannot block creation. Built-in `general-purpose` emits neither subagent start nor stop. Other built-ins/custom agents may emit both. `subagentStop` can block continuation or rewrite response. `agentStop` can block continuation with reason; provider caps at eight consecutive blocks and supplies `stop_hook_active`.
- `sessionEnd` is not proof of successful task completion. `sessionId`, `cwd`, transcript path and stop event fields are available, but transcript contents/schema should not be treated as stable unless documented for the selected event.

## Gemini CLI hooks

Official [hooks reference](https://geminicli.com/docs/hooks/reference/) describes `settings.json` `hooks` object; command hooks are currently the only supported execution type. User/project/system/extension merge behavior and trust requirements are described in [hook overview](https://geminicli.com/docs/hooks/). Payload common fields: `session_id`, absolute `transcript_path`, `cwd`, event name and timestamp.

- `SessionStart` fires on startup, resume, and clear, with `source` distinguishing `startup|resume|clear`; can add context. Flow-control output is ignored, so it cannot block startup.
- `BeforeAgent` fires after prompt submission and before planning; has prompt and supports additional context or denial. `AfterAgent` fires after final response; provides prompt, final `prompt_response`, and `stop_hook_active`; denial with reason retries, `continue:false` stops. No explicit retry cap established in the cited reference.
- `BeforeModel` runs immediately before an LLM request and receives `llm_request` (`model`, `messages`, generation `config`); `hookSpecificOutput.llm_request` can override request parts. It can also return a documented synthetic `llm_response` to skip the model call. This gives a request-bound interception point, but docs do not specify its ordering relative to `PreCompress`, nor establish that request messages expose a durable post-compaction summary before a dependent conclusion. `AfterModel` is per response chunk, not final completion.
- `BeforeTool`/`AfterTool` identify tool events; before can block, after can add context or alter result. After-event output cannot undo already-performed tool effects.
- `PreCompress` is documented as pre-compression notification but hook execution is asynchronous/advisory and cannot change or block compression. `SessionEnd` runs on exit/clear with reason but is best effort, not waited for, and ignores flow-control fields.
- The official hook event reference has no subagent lifecycle event; do not infer child inheritance or separate child context from ordinary hooks.

## Failure and continuation limits

- Copilot CLI documents 30-second default hook timeout. All timeouts, including command `preToolUse`, fail open with warning; non-timeout command `preToolUse` errors fail closed. `agentStop` block continuation has a hard runaway guard at eight consecutive blocks. [Copilot reference](https://docs.github.com/en/copilot/reference/hooks-reference).
- Gemini CLI documents configurable hook timeout in milliseconds, default 60,000; exit code 2 is an event-specific block/retry, while other nonzero exit is a non-fatal warning and CLI continues. The reference does not specify timeout disposition per event, so fail-open/fail-closed behavior on timeout is unknown. It states no hard `AfterAgent` retry cap. [Gemini reference](https://geminicli.com/docs/hooks/reference/).
- Codex command hooks default to 600 seconds for most events, while `SessionEnd` and `Interrupt` default to 1 second and are capped at 3 seconds; `Stop` can therefore be configured with a long timeout. The hooks reference documents explicit event decisions, but does not define a general timeout/failure disposition for `PreToolUse` or `Stop`; errors/timeouts cannot be assumed to block or continue in a particular way. It states no hard `Stop` continuation cap. Unsupported output on `PreToolUse` is marked failed and the tool call proceeds; explicit supported denial blocks. [Codex hooks](https://learn.chatgpt.com/docs/hooks).

## Capability and evidence limits

The official references describe event/config schemas, not that a particular installed build has hooks enabled, trusts a particular config, executes a handler, or delivers its response. No provider was launched and no authenticated config was read. No desktop attach/control endpoint is established by these hook pages; a Codex CLI/app-server process is not evidence of attachment to desktop. Task/session identifiers are provider lifecycle identifiers, not proof of durable semantic task identity. Exact deployed Codex standalone desktop and ChatGPT-host Codex compatibility is unknown.

These documented contracts can seed later acceptance tests: config discovery/scope and trust; event order and source on startup/resume/clear/compact; exact payload fields; context delivery; pre-action denial and post-action non-reversibility; continuation behavior/caps; absent/advisory end and compression events; and subagent identity/event absence. No recommendation about whether to support or rely on a capability is made here.
