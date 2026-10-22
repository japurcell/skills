# Provider protocol preflight, 2026-10-21

These primary-source entry points prepare T7/T8 while T6 is implemented. They do not qualify a provider, select an installed version, establish credentials or authorize broader permissions. Recheck each exact installed version's help and machine protocol before implementation. No live call was made for this note.

## Codex CLI

The [official non-interactive reference](https://learn.chatgpt.com/docs/non-interactive-mode), redirected from the former developers.openai.com URL on 2026-10-22, documents `exec --json` events and separate final-message/schema channels. Completed assistant-message items must be distinguished from tool text, errors and turn completion. A final-message file may supply the qualified result channel; validate its freshness, bounded size and schema alongside exit status. The removed `--full-auto` option must not be generated.

Local Codex 0.163.0 `exec --help` confirms `--json`, `--output-schema`, `--output-last-message`, explicit sandbox selection and optional `--ignore-user-config`. Ignoring user configuration still uses CODEX_HOME authentication. The adapter must explicitly control effective configuration and native permissions without bypassing hook trust or sandboxing. Help establishes options, not denied-operation, result or stop proof. Fresh calls must not select resume/fork/implicit-last sessions; only compatible corrections may reuse a native conversation within one invocation.

After the desktop update, read-only inventory on 2026-10-21 PDT still finds CLI 0.163.0 at `/Users/adam/homebrew/Caskroom/codex/0.163.0/bin/codex`, SHA256 `8813367285524ac798dd96d1b071aea30d58708c7226fd236cd275cf1cfdee31`. Version/help succeeded while warning that PATH aliases could not be created under the sandbox. No escalation, installation or live call was made. Desktop update does not establish that the separately installed CLI changed.

## Copilot CLI

The [official programmatic reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-programmatic-reference) documents prompt mode, JSONL output, explicit tool permissions and suppression of user questions. Its separate `workflow run` result protocol does not establish the protocol of ordinary prompt mode. Qualify prompt-mode terminal events directly rather than borrowing workflow-result fields.

Read-only inspection on 2026-10-22 found that invoking the launcher without update controls attempted to extract version 1.0.102 into the user cache, which the sandbox rejected. No escalation or global update was performed. Running the already cached 1.0.101 `index.js` with pinned Node, `COPILOT_AUTO_UPDATE=false` and `--no-auto-update --help` succeeded. Help says `--no-auto-update` selects the executable's bundled version instead of a newer cached version. T8 must pin the actual launched artifact and suppress updates before version/help and live qualification. Do not rely on an earlier launcher version inventory.

The cached help confirms model/reasoning options, selected tool allow/deny/availability controls, `--no-ask-user`, JSONL, MCP controls and no-remote options. Its broad-tools example is not an authorization or required implementation default. Prove the selected narrow permissions in harmless denied-operation fixtures. Repository hooks, MCP, plugins, discovered instructions and native child authority require explicit compatibility checks; do not trust a folder merely to bypass startup interaction.

## Gemini CLI

The [official headless reference](https://geminicli.com/docs/cli/headless/) describes explicit prompt mode and JSON/streaming JSON output. Single JSON contains response, statistics and optional error. Streaming output distinguishes initialization, messages, tools, errors and terminal result events. Documented statuses distinguish success, general/API failure, bad input and turn exhaustion. The adapter must identify the actual final assistant payload rather than parse arbitrary tool/log text. Permissions, native session reuse, loaded skills and stop behavior still need exact-version qualification.

## OpenCode

Current [V2 CLI documentation](https://opencode.ai/v2/docs/cli/commands) describes `run --format json` and private standalone execution. It separately exposes session continuation. Fresh factory calls must not select implicit continuation. Pin the CLI major version before deriving its launch/configuration contract.

The [V2 permission reference](https://opencode.ai/v2/docs/permissions/) explicitly differs from V1: ordered `permissions` rules use action/resource/effect; shell and subagent action names changed. Later matching rules win. Child agents have their own rules, not a subset of parent permissions. Shell authority is the host user's, so tool policy is not an OS sandbox. Required restrictions must be tested through actual child and denied-tool scenarios. Never combine V1 configuration with V2 assumptions, broaden permissions to bypass interaction, or adopt a documentation example's global installer into factory startup.

## Pi

The former `badlogic/pi-mono` repository redirects to the [canonical upstream](https://github.com/earendil-works/pi). Its [CLI reference](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/cli.md) distinguishes one-shot print/JSON from long-lived RPC. JSON reserves stdout for protocol records; session flags and resource discovery are separate controls. Exact model IDs avoid fuzzy selection. A plain tool list replaces defaults, but MCP tools need separate restrictions; disabling extensions or skills does not disable explicitly supplied resources. Qualification must account for discovered resources and MCP access rather than treating a read-only tool list as a universal permission boundary. Required native restrictions may remain unsupported.

The [JSON event protocol](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/json.md) uses LF-delimited records. Completed messages arrive as `message_end`; `agent_end` can precede retry or recovery, while `agent_settled` indicates no remaining automatic work. Validate the final assistant payload only after the qualified terminal sequence and process status. Preserve emitted telemetry without counting harness-owned retry as a new factory launch. Exact version/package identity still needs confirmation; current upstream types use `@earendil-works/pi-coding-agent`.

## Remaining evidence

The current session's initial read-only CLI inventory found Codex 0.163.0 and Copilot 1.0.101; the later launcher discrepancy is recorded above. Gemini, OpenCode and Pi were not on PATH at that inventory. T8 must obtain a reviewed exact executable in a disposable development environment when necessary, inspect its help, and qualify harmless authorized calls with credentials supplied outside code and logs. T7's common contract and T6's lifecycle still govern every provider. Documentation alone cannot prove an unambiguous final channel, denied permissions or descendant quiescence.
