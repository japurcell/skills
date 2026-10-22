# Provider protocol preflight, 2026-10-21

These primary-source entry points prepare T7/T8 while T6 is implemented. They do not qualify a provider, select an installed version, establish credentials or authorize broader permissions. Recheck each exact installed version's help and machine protocol before implementation. No live call was made for this note.

## Gemini CLI

The [official headless reference](https://geminicli.com/docs/cli/headless/) describes explicit prompt mode and JSON/streaming JSON output. Single JSON contains response, statistics and optional error. Streaming output distinguishes initialization, messages, tools, errors and terminal result events. Documented statuses distinguish success, general/API failure, bad input and turn exhaustion. The adapter must identify the actual final assistant payload rather than parse arbitrary tool/log text. Permissions, native session reuse, loaded skills and stop behavior still need exact-version qualification.

## OpenCode

Current [V2 CLI documentation](https://opencode.ai/v2/docs/cli/commands) describes `run --format json` and private standalone execution. It separately exposes session continuation. Fresh factory calls must not select implicit continuation. Pin the CLI major version before deriving its launch/configuration contract.

The [V2 permission reference](https://opencode.ai/v2/docs/permissions/) explicitly differs from V1: ordered `permissions` rules use action/resource/effect; shell and subagent action names changed. Later matching rules win. Child agents have their own rules, not a subset of parent permissions. Shell authority is the host user's, so tool policy is not an OS sandbox. Required restrictions must be tested through actual child and denied-tool scenarios. Never combine V1 configuration with V2 assumptions, broaden permissions to bypass interaction, or adopt a documentation example's global installer into factory startup.

## Pi

The former `badlogic/pi-mono` repository redirects to the [canonical upstream](https://github.com/earendil-works/pi). Its [CLI reference](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/cli.md) distinguishes one-shot print/JSON from long-lived RPC. JSON reserves stdout for protocol records; session flags and resource discovery are separate controls. Exact model IDs avoid fuzzy selection. A plain tool list replaces defaults, but MCP tools need separate restrictions; disabling extensions or skills does not disable explicitly supplied resources. Qualification must account for discovered resources and MCP access rather than treating a read-only tool list as a universal permission boundary. Required native restrictions may remain unsupported.

## Remaining evidence

The current session's read-only CLI inventory found Codex0.163.0 and Copilot1.0.101; their earlier official protocol findings remain in session/task evidence. Gemini, OpenCode and Pi were not on PATH at that inventory. T8 must obtain a reviewed exact executable in a disposable development environment when necessary, inspect its help, and qualify harmless authorized calls with credentials supplied outside code and logs. T7's common contract and T6's lifecycle still govern every provider. Documentation alone cannot prove an unambiguous final channel, denied permissions or descendant quiescence.
