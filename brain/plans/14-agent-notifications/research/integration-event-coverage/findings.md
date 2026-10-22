# Integration event coverage

Checked 2026-10-21 against repository notes and current official references. This is a capability map, not proof of live event delivery. No hooks were installed or exercised.

## Finding

All three providers support command hooks in at least one local surface. Their events do not normalize to a reliable success/failure/cancel signal. Copilot CLI has the richest hook events for attention: it distinguishes runtime errors and exposes permission and elicitation notifications. Codex has a direct interruption hook and a richer app-server API for clients that own the agent session. Gemini has a final-response hook and an observational tool-permission hook, but no dedicated failure or cancellation event.

The app must not infer a stall from silence or elapsed time. None of these event catalogs reports a stall. A stall may enter the pending-alert stack only when an external agent host or watchdog reports it, with that source preserved.

## Coverage matrix

| Signal needed | Codex CLI and local Codex Desktop thread | Copilot CLI | VS Code using Copilot target | Gemini CLI |
|---|---|---|---|---|
| Turn complete / success | `Stop` exposes the final assistant text, not an outcome. CLI `notify` runs only for `agent-turn-complete`, whose payload has no outcome. Treat both as `turn_end / unknown`. Local Desktop supports command hooks; its built-in notifications separately cover turn completion. | `agentStop` is an `end_turn` event, not an outcome. `notification` has `agent_idle` for a background agent entering idle; `agent_completed` is for a background subagent and can mean completed or failed. `sessionEnd.reason` includes `complete`, but it fires at session termination, not every turn. | Uses the shared Copilot harness and hook format, with the VS Code hook UI in Preview. `agentStop` is still generic. The reference marks `notification` CLI-only, so do not rely on `agent_idle` or `agent_completed` from VS Code. | `AfterAgent` fires after a final response but gives no success status. The separate native terminal notification can announce successful session completion, but it is experimental, disabled by default, and does not invoke a custom command. |
| Failure | `PostToolUse` also runs after a failed Bash command, but has no universal success field. No dedicated failed-turn hook. `SessionEnd.reason` is always `other`. | `errorOccurred` reports model-call, tool-execution, system, or user-input errors and whether the error is recoverable. `postToolUseFailure` is tool-scoped. `sessionEnd.reason` includes `error` and `timeout`, but only at session termination. | Same event schema is the intended Copilot target; `errorOccurred` and `postToolUseFailure` are the documented failure hooks. Preview status means confirm delivery in the deployed VS Code version. | No dedicated failure hook. `AfterTool.tool_response.error` can report a tool error. `AfterAgent` and `SessionEnd` do not provide a turn failure classification. |
| Agent asks for user input | No command hook for an agent question. Desktop's native question notifications can alert the user. The app-server API exposes `tool/requestUserInput` to a client that owns that session. | CLI `notification` has `elicitation_dialog`, which signals an agent information request. Do not confuse this with `userPromptSubmitted`, which is the user's prompt going in. | No documented question-wait command event: the relevant `notification` hook is explicitly CLI-only. VS Code Desktop has its own UI flow, but arbitrary hook delivery for this event is not established by the docs. | No question hook. Gemini's native terminal notification can report action required while it waits for user input, but this is an OSC 9/BEL terminal notification, not a command callback. |
| Approval wait | `PermissionRequest` runs immediately before Codex asks for approval. It can allow, deny, or defer to the normal prompt. It signals a request, not the user's eventual decision. Desktop also has native permission notifications. | `permissionRequest` runs before rules, auto-allow/deny, and user prompting, so it may fire without a visible wait. CLI `notification` type `permission_prompt` is the better signal for a surfaced prompt. | `permissionRequest` uses the shared Copilot hook format. The CLI-only `permission_prompt` notification is not documented for VS Code. | `Notification` exposes `notification_type: "ToolPermission"` with summary and details. It is observational only and cannot grant or deny. Native notification can alert on approval wait, but is not a command hook. |
| Cancellation | `Interrupt` runs when a user interrupts an active main-thread turn. It does not run for idle threads or subagents. `SessionEnd` is not a cancellation signal. | No dedicated turn-cancel hook. `sessionEnd.reason` can be `abort` or `user_exit`, but only when a session terminates; `/clear` emits `user_exit` while the CLI continues. `agentStop` does not distinguish cancellation. | No dedicated cancellation event documented for the Copilot target. `sessionEnd` is session-scoped, not a reliable per-turn cancellation signal. | No cancellation event. `SessionEnd.reason` is one of `exit`, `clear`, `logout`, `prompt_input_exit`, or `other`; none explicitly means a cancelled turn. |
| Externally reported stall | No native stall event. A separate producer can submit an explicit report. | No native stall event. A separate producer can submit an explicit report. | No native stall event. A separate producer can submit an explicit report. | No native stall event. A separate producer can submit an explicit report. |

## Provider details and boundaries

### Codex desktop and CLI

Codex command hooks receive one JSON object on stdin and run with the session working directory. The current catalog includes `PermissionRequest`, `Stop`, `Interrupt`, `SessionEnd`, and other lifecycle events. `Stop` includes `last_assistant_message` and `stop_hook_active`, not a result status. `Interrupt` is the direct signal for a user interrupt. `SessionEnd` fires when a main thread closes, is archived or deleted while open, or is idle and not open in any connected client for 30 minutes; its current `reason` is only `other`. [Official Hooks reference](https://learn.chatgpt.com/docs/hooks)

The separate CLI `notify` command receives one JSON argument and currently supports only `agent-turn-complete`; fields include thread id, turn id, cwd, input messages, and last assistant message, with no outcome. TUI notifications can filter built-in event types such as `agent-turn-complete` and `approval-requested`, but TUI notification settings do not invoke an external command. [Advanced configuration](https://learn.chatgpt.com/docs/config-file/config-advanced) documents `notify`; [desktop notification settings](https://learn.chatgpt.com/docs/notifications) separately expose turn-completion, question, and permission alerts.

For a product that owns a Codex client, `codex app-server` streams `turn/completed` with `status: completed | failed | interrupted`; failed turns include an error. It also exposes approval requests and `tool/requestUserInput`. Only `completed` is a documented success status. This is an API for a client that starts or connects to an app-server process, not a documented subscription point for an unrelated app to attach to a user's existing Codex Desktop conversation. [App-server API reference](https://learn.chatgpt.com/docs/app-server), [Codex app-server overview](https://developers.openai.com/blog/codex-as-a-platform).

The hooks reference says local hooks continue to work for local-only Codex/Work threads. Under cloud orchestration, local command/shell hooks are unsupported, even when tools execute locally; an enterprise-managed remote MCP hook is a separate exception for eligible Work Cloud setups. [Hooks reference](https://learn.chatgpt.com/docs/hooks).

### Copilot CLI and VS Code

Copilot CLI command hooks run on the developer machine in the same shell as the CLI. With the CLI session sandbox enabled, repository, user, and plugin hooks run inside that sandbox; policy hooks run on the host. The CLI reference documents `agentStop`, `errorOccurred`, `postToolUseFailure`, `permissionRequest`, `notification`, and `sessionEnd`, among others. [GitHub Copilot hooks reference](https://docs.github.com/en/copilot/reference/hooks-reference).

VS Code's Copilot session target shares the Copilot harness and hook format with Copilot CLI. The VS Code hooks experience is Preview, and VS Code says event lifecycles may vary by provider implementation. Select the Copilot target; the older `Local` harness has a separate schema and event set. The Copilot reference labels `notification` as CLI-only, so approval and elicitation notifications are not a documented VS Code command event. [VS Code hooks guide](https://code.visualstudio.com/docs/agent-customization/hooks).

`permissionRequest` is deliberately earlier than an actual user wait: it runs before the permission service evaluates rules and auto-allow/auto-deny. The asynchronous `notification` event reports `permission_prompt` and `elicitation_dialog` when the CLI emits those system notifications. `agentStop`'s `stopReason` is always `end_turn`; use `errorOccurred` for reported execution errors, not as proof that every ended turn failed. [GitHub Copilot hooks reference](https://docs.github.com/en/copilot/reference/hooks-reference).

The VS Code hook command follows the session's execution host. VS Code's remote extension host can run in a container, WSL, or remote location; the desktop UI can connect to a remote Agent Host beside the workspace. This means a command in WSL/SSH/container writes and runs there unless an explicit host bridge is added. Copilot Cloud Agent runs in an ephemeral Linux sandbox with no user notifications or permission prompts, so its hooks cannot deliver a local desktop alert. [Extension host locations](https://code.visualstudio.com/api/advanced-topics/extension-host), [Agent Host architecture](https://code.visualstudio.com/docs/agents/concepts/agent-host), [Copilot cloud environment](https://docs.github.com/en/copilot/reference/hooks-reference).

### Gemini CLI

Gemini command hooks receive JSON on stdin and use the shell command configured in `settings.json`. `BeforeAgent` sees a submitted user prompt; `AfterAgent` runs after the final response; `AfterTool` carries a `tool_response` that may include `error`; `SessionEnd` is best effort and covers exit or clear; `Notification` currently has only `ToolPermission` and is observational. The published hook reference page is dated April 10, 2026, so confirm exact delivery on the chosen CLI release before relying on it. [Gemini hooks reference](https://geminicli.com/docs/hooks/reference/), [official source reference](https://github.com/google-gemini/gemini-cli/blob/main/docs/hooks/reference.md).

Gemini's built-in terminal notifications are a separate feature: the docs describe "action required" while waiting for user input or tool approval and successful session completion. It is experimental, disabled by default, and uses terminal OSC 9 with BEL fallback rather than invoking a configured command. [Gemini Notifications](https://geminicli.com/docs/cli/notifications/).

For Gemini, Copilot CLI, or Codex hooks started inside WSL, SSH, or a container, the hook process follows that runtime's shell, cwd, filesystem, and available notification services. Treat host delivery from those environments as unsupported unless a separate, explicit bridge is provided. This is an inference from each provider's command execution model and VS Code's documented remote hosts, not a promise of built-in forwarding.

## Minimal event envelope recommendation

Keep a provider adapter's source event intact and normalize only these concepts:

- producer and surface/harness, such as Codex CLI `notify`, Codex local hook, Codex app-server client, Copilot CLI, VS Code Copilot target, or Gemini CLI;
- original provider event name plus a small category such as `turn_end`, `tool_failure`, `approval_wait`, `input_wait`, `cancel`, or `external_stall_report`;
- outcome only when the producer states one. Preserve `unknown` for generic `Stop`/`agentStop`/`AfterAgent` events;
- event time and available session/thread, turn, and agent identifiers;
- repository or cwd identity, plus execution environment/host such as local, WSL, SSH, container, or cloud;
- a bounded, redacted display summary. Do not default to storing raw prompts, tool arguments, full results, or environment variables.

An external stall report should carry its reporter and measured interval as supplied by that external source. No app-side timer or silence-based inference is part of this integration contract.

## Local repository evidence

- [Codex hook notes](../../../../../brain/codebase/hooks-codex.md), [Copilot hook notes](../../../../../brain/codebase/hooks-copilot.md), and [Gemini hook notes](../../../../../brain/codebase/hooks-gemini.md) were inspected. They already caution that `Stop`/`agentStop` is not a success field, that Copilot has distinct failure and notification events, and that Gemini lacks a dedicated tool-failure/session-error event.
- Checked-in samples include [.codex/hooks.json](../../../../../.codex/hooks.json), [.copilot/hooks/hooks.json](../../../../../.copilot/hooks/hooks.json), [.github/hooks/hooks.json](../../../../../.github/hooks/hooks.json), and [.gemini/settings.json](../../../../../.gemini/settings.json). These demonstrate command registrations only, not live event delivery.
- Local `codex --version` returned `codex-cli 0.163.0`. A Copilot version probe could not complete because the launcher tried to extract a package into the read-only user Library cache; a repository note records Copilot CLI 1.0.100 observed on 2026-10-20. Gemini CLI is absent on this host. No runtime event was tested.

## Source recency and verification limits

Official docs were checked on 2026-10-21. The Codex hooks and app-server references are current pages. GitHub's Copilot reference was crawled today; VS Code states its hook experience is Preview. Gemini's site reference carries a last-updated date of 2026-04-10, and the current upstream reference contains the same event catalog. No Gemini or VS Code runtime is installed here, and the local Copilot CLI probe was blocked by a read-only cache location. Verify actual command delivery and selected event coverage in disposable local sessions after choosing versions and execution hosts.
