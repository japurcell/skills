---
type: Research Findings
description: Current official event and output contracts for agent-brain M7 adapter candidates
---

# M7 provider event/output contract recheck

Research checked 2026-10-05 against the linked official provider documentation. The prior comparison is [Provider binding contract: facts for native adapters](../provider-binding-contract/findings.md), checked 2026-09-30. These are documented contracts, not deployed-version observations or certification. No provider CLI was launched, no installed configuration was read, and no model evaluation or home-directory installation/activation was performed.

The Codex and GitHub Copilot reference pages do not expose a semantic version or last-updated date. Gemini CLI's [hooks reference](https://geminicli.com/docs/hooks/reference/) reports “Last updated: Apr 10, 2026”; its [writing-hooks guide](https://geminicli.com/docs/hooks/writing-hooks/) reports “Last updated: Mar 20, 2026.” Provider build versions, and whether live behavior matches these docs, remain **UNVERIFIED**.

## Current native contract matrix

| Provider candidate | Registration format | Context response | Denial or continuation response | Timeout and continuation facts |
| --- | --- | --- | --- | --- |
| Codex CLI/desktop | `hooks.json` beside active config, inline `[hooks]` in `config.toml`, or plugin lifecycle config. Event arrays contain matcher groups and command handlers. Repository hooks require that project layer to be trusted. | Event-specific JSON uses `hookSpecificOutput` with `hookEventName` and `additionalContext`; `SessionStart` and `UserPromptSubmit` are context points. | `PreToolUse` uses `hookSpecificOutput.permissionDecision: "deny"` plus `permissionDecisionReason`. Prompt and stop continuation use `decision: "block"` plus `reason`. | Command timeout defaults to 600 seconds for most events. `SessionEnd` and `Interrupt` default to 1 second and have a 3-second maximum. No numeric `Stop` or `SubagentStop` continuation cap is documented. |
| Copilot CLI | JSON file with `version: 1` and `hooks` event arrays, such as `.github/hooks/agent-brain.json`; camelCase event names select CLI payload names. | `sessionStart` returns top-level `additionalContext`; `postToolUse` and `postToolUseFailure` also have context outputs for their respective result/failure paths. | `preToolUse` returns top-level `permissionDecision` and, for denial, `permissionDecisionReason`. `agentStop` and `subagentStop` return `decision: "block"` plus `reason`. | Default timeout is 30 seconds. Command `preToolUse` fails closed for non-timeout errors, but **all hook timeouts fail open**. The CLI overrides stop blocking after 8 consecutive blocks. |
| Gemini CLI | `.gemini/settings.json` has a `hooks` object keyed by event; each event has matcher groups with `hooks` command-handler arrays. | `SessionStart` and `BeforeAgent` use `hookSpecificOutput` with `hookEventName` and `additionalContext`. | `BeforeTool` denial is top-level `decision: "deny"` plus `reason`. `AfterAgent` uses the same denial shape to request a retry. | Handler timeout is configurable in milliseconds and defaults to 60,000. Timeout disposition is not specified in the reference. `AfterAgent` provides `stop_hook_active`, but the reference gives no numeric retry cap. |

Sources: [Codex Hooks](https://learn.chatgpt.com/docs/hooks), [GitHub Copilot hooks reference](https://docs.github.com/en/copilot/reference/hooks-reference), [Gemini CLI hooks reference](https://geminicli.com/docs/hooks/reference/).

## Codex

The current official [Codex Hooks](https://learn.chatgpt.com/docs/hooks) reference permits `hooks.json`, inline `[hooks]` in `config.toml`, and plugin lifecycle config. User and repository locations are `~/.codex/hooks.json` and `<repo>/.codex/hooks.json` (with the corresponding TOML locations). Matching sources merge; a trusted repository layer is required for repository-local hooks. A command hook receives one JSON object on stdin. Common fields include `session_id`, nullable `transcript_path`, `cwd`, `hook_event_name`, and `model`; transcript format is expressly unstable.

| Event | Relevant current payload/behavior |
| --- | --- |
| `SessionStart` | `source` is `startup`, `resume`, `clear`, or `compact`. A matching `compact` hook runs after compaction and can return context before the immediate next model request, including an automatic mid-turn continuation. |
| `UserPromptSubmit` | Includes `turn_id` and `prompt`; supports the same `hookSpecificOutput.additionalContext` context path and can block the prompt with `decision: "block"` and `reason`. |
| `PreCompact` / `PostCompact` | Both include a `trigger` of `manual` or `auto`. `PreCompact` can stop compaction; `PostCompact` runs after it. `SessionStart(source: "compact")` is the documented route that places context before the next root model request. |
| `PreToolUse` / `PostToolUse` | `PreToolUse` exposes `tool_name` and `tool_input`. Deny a supported call with the event-specific response below. Tool hooks cover local functions, shell, MCP, and edits, with documented hosted-tool exclusions and specialized opt-out paths. `PostToolUse` is after execution and cannot undo side effects. |
| `SubagentStart` / `SubagentStop` | `SubagentStart` can add context, but `continue: false` does not prevent startup. The common `session_id` is the parent session ID; subagent events also expose `agent_id` and `agent_type`. `SubagentStop` can continue the flow with `decision: "block"` and `reason`. |
| `Stop` | `decision: "block"` continues the turn by creating a continuation prompt from `reason`; `stop_hook_active` and `last_assistant_message` are available. The page documents no numeric cap for `Stop` or `SubagentStop`. |

Documented JSON examples, reduced to the fields relevant to an adapter:

```json
{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"Load the current repository map before acting."}}
```

```json
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Required context is missing."}}
```

```json
{"decision":"block","reason":"Run the required completion check before ending the turn."}
```

The `PreToolUse` reference marks `continue`, `stopReason`, and `suppressOutput` unsupported for that event; use its `permissionDecision` shape for a tool denial. Codex docs describe Codex generally and do not establish standalone desktop versus CLI parity, nor the exact behavior of any currently installed build.

## GitHub Copilot CLI

The official [GitHub Copilot hooks reference](https://docs.github.com/en/copilot/reference/hooks-reference) defines JSON hook files with `version: 1`, a `hooks` object, event arrays, and command entries. `.github/hooks/*.json` is a supported repository location; user, inline settings, plugin, and policy sources can also contribute. This M7 candidate uses CLI camelCase event names. CLI payloads use fields such as `sessionId`, `cwd`, and numeric epoch-millisecond `timestamp`; PascalCase names select the VS Code-compatible snake_case schema, and VS Code remains deferred.

| Event | Relevant current payload/behavior |
| --- | --- |
| `sessionStart` | Input contains `sessionId`, `timestamp`, `cwd`, `source` (`startup`, `resume`, or `new`), and optional `initialPrompt`; only top-level `additionalContext` is consumed. |
| `userPromptSubmitted` / `userPromptTransformed` | A command hook's `userPromptSubmitted` output is ignored. `userPromptTransformed` runs after runtime transformation and receives both `prompt` and `transformedPrompt`; its output field is `modifiedTransformedPrompt`. It rewrites the model-facing content and cannot block or handle the turn. |
| `preCompact` | Receives `transcriptPath`, `trigger` (`manual` or `auto`), and `customInstructions`, but is notification-only. The reference lists no post-compaction event. |
| `preToolUse` | Receives `toolName` and `toolArgs`. Output may contain `permissionDecision`, `permissionDecisionReason`, or `modifiedArgs`. An explicit denial is shown below. |
| `postToolUse` / `postToolUseFailure` | `postToolUse` follows successful tool execution and can add `additionalContext` or replace a successful result. Failed tools have a separate `postToolUseFailure` event with an `error` field; its output can add recovery context, but cannot undo the failed action. |
| `subagentStart` / `subagentStop` / `agentStop` | `subagentStart` includes `sessionId`, `cwd`, `transcriptPath`, and `agentName`; top-level `additionalContext` is prepended to the child's first user message but cannot block creation. `subagentStop` includes `agentId`, `agentType`, `agentName`, and full `response`; it can block or return an optional `modifiedResponse`. The built-in `general-purpose` agent does not emit either child event. `agentStop` includes `stopReason: "end_turn"` and `stop_hook_active`. |

The documented native CLI envelopes include:

```json
{"additionalContext":"Load the applicable repository policy before editing."}
```

```json
{"permissionDecision":"deny","permissionDecisionReason":"The required pre-action check did not pass."}
```

```json
{"decision":"block","reason":"Complete the assigned validation before ending this turn."}
```

The documented default timeout is 30 seconds. For command hooks, `preToolUse` is fail-closed on exit 2 and other non-timeout errors. Every timeout, including `preToolUse`, is fail-open. The CLI's runaway guard overrides stop continuation after 8 consecutive `block` results; `stop_hook_active` lets an `agentStop` handler see that a prior block already forced a continuation. These are hard native limits on any claimed timeout or unlimited stop guarantee.

## Gemini CLI

The official [Gemini CLI hooks reference](https://geminicli.com/docs/hooks/reference/) defines hooks in `settings.json` as event arrays containing matcher groups and `hooks` command handlers. `matcher`, `sequential`, and handler `timeout` are documented fields. The [writing-hooks guide](https://geminicli.com/docs/hooks/writing-hooks/) gives a `.gemini/settings.json` registration example and a context response with `hookSpecificOutput.hookEventName` plus `additionalContext`.

| Event | Relevant current payload/behavior |
| --- | --- |
| `SessionStart` | Runs on startup, resume, and `/clear`; input includes `source: startup|resume|clear`. `hookSpecificOutput.additionalContext` is injected as the first history turn interactively or prepended to the prompt in non-interactive mode. `decision` and `continue` are ignored, so startup cannot be blocked. |
| `BeforeAgent` | Runs after prompt submission and before planning. It can add turn-only context through `hookSpecificOutput.additionalContext`, or deny with `decision: "deny"` and `reason`. |
| `BeforeTool` / `AfterTool` | `BeforeTool` can deny before execution with `decision: "deny"` and `reason`. `AfterTool` can append context to the result, but denial only hides/replaces the result after the tool has run. |
| `AfterAgent` | Receives `prompt`, `prompt_response`, and `stop_hook_active`. `decision: "deny"` with `reason` forces a retry; `continue: false` stops without retry. Exit code 2 also requests retry. No numeric retry cap is specified. |
| `PreCompress` | Receives the `auto|manual` trigger and can display `systemMessage`. It fires asynchronously and cannot block or modify compression. The reference documents no post-compression hook or ordering guarantee to the next model request. |
| Child lifecycle | The hooks reference lists no subagent start/stop events. It establishes no child-specific event or context inheritance contract. |

The documented context and denial shapes are:

```json
{"hookSpecificOutput":{"hookEventName":"BeforeAgent","additionalContext":"Load the scoped guidance before planning."}}
```

```json
{"decision":"deny","reason":"Required guidance has not been loaded."}
```

All Gemini command events receive common stdin fields `session_id`, `transcript_path`, `cwd`, `hook_event_name`, and ISO timestamp, plus event-specific fields in the table. The handler timeout is milliseconds, default 60,000. The reference describes exit code 2 and nonzero behavior, but does not define native timeout disposition. `BeforeAgent` denial discards the prompt; `continue: false` blocks while preserving it. `stop_hook_active` indicates a retry sequence, but no numeric cap is documented. Therefore the current docs do not prove that Gemini restores context before a dependent continuation after mid-turn compression. The plan's candidate `BeforeModel` request boundary and `BeforeTool` boundary still require build-specific event-order and content-delivery evidence; the advisory `PreCompress` event alone cannot provide that guarantee.

## Comparison with the 2026-09-30 findings

No source-version change since 2026-09-30 is confirmed here. The earlier findings file is a summary, not a dated snapshot of the provider pages. Gemini's reference exposes a last-updated date earlier than 2026-09-30; the Codex and Copilot pages do not expose a version/date, so their page-level change history is **UNVERIFIED**.

The current recheck adds precise facts that the previous summary did not spell out:

- Codex documents `SessionStart(source: "compact")` before the immediate post-compaction model request, including mid-turn automatic compaction; its source values also include `clear`.
- Copilot's exact prompt rewrite output is `modifiedTransformedPrompt`. Its current reference also documents a distinct `postToolUseFailure` recovery-context event.
- Gemini's current reference specifies the `SessionStart` context placement for interactive and non-interactive execution, the `AfterAgent.stop_hook_active` field, and `PreCompress` as asynchronous and unable to block or modify compression.

These are differences in recorded detail, not evidence that the providers changed behavior after the prior review date. The previously recorded Copilot timeout-open behavior and eight-block stop guard, Codex generic desktop/CLI uncertainty, Gemini advisory compression and absent child hook, and all three platforms' documented event families remain consistent with the current pages.

## Remaining gaps and candidate status

- **Codex surface/build:** The official docs do not pin the event contract to a desktop or CLI release. Current installed versions, actual hook discovery/trust, timeout behavior, and desktop-versus-CLI parity are **UNVERIFIED**. Although event timeout defaults are documented, the outcome of a `PreToolUse` or `Stop` timeout is not. The numeric stop-continuation cap is **UNVERIFIED**. The child event has a provider `agent_id`, but its shared `session_id` is the parent; no independent child session identifier is documented. Generic child ownership remains inconclusive.
- **Copilot timeout and child scope:** Native command-hook timeout is explicitly fail-open, so a tool denial cannot rely on the provider timeout path. The general-purpose built-in child lacks lifecycle hooks. Other selected child paths and actual delivery remain build-specific. This does not certify the candidate for hard timeout denial or for every child type.
- **Gemini compact and retry scope:** The only listed compact event is asynchronous/advisory `PreCompress`; no documented post-compression order ensures refreshed context before the next model request. `AfterAgent` has a retry marker but no numeric cap, and timeout disposition is **UNVERIFIED**. No child lifecycle path is documented. The compact and generic child paths remain inconclusive from docs alone.
- **All providers:** M7 offline envelope tests prove translation only. Native response consumption, startup/resume delivery, context timing before governed work, timeout behavior, and selected child paths require M10's separately authorized exact-build live certification. No provider path is certified by this research.

The accepted core remains the foreground agent, deterministic CLI, and thin provider hooks. This recheck makes no architecture or policy decision and introduces no daemon, model supervisor, or alternate runner.
