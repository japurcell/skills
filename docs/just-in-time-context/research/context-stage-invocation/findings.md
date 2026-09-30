# Semantic stage invocation interfaces

Checked current official documentation on 2026-09-29. No provider session, installation, configuration change, or live probe was run. Installed versions and surface certification remain Adoption work. Documentation is rolling, not tied to an established deployed release here. This research assumes the accepted shared executable runtime, one semantic lifecycle skill, and repository-local indexed Markdown; it selects no further architecture.

## CLI process interfaces

The commands below are illustrative documented-interface compositions, not executed or certified launch recipes. `STAGE_PROMPT` must identify the semantic stage and scope. Process working directory must be the intended repository; inherited user configuration and hook registrations still matter.

| Provider | Launch/result interface | Continuation and bound |
| --- | --- | --- |
| Codex CLI | `codex exec --json --sandbox workspace-write --output-schema stage-result.schema.json -o stage-result.json "STAGE_PROMPT"` | `codex exec resume SESSION_ID "FOLLOWUP_PROMPT"`. No general execution/turn ceiling was established in inspected docs; runner deadline/cancellation is separate supervision. |
| Copilot CLI | `copilot -C REPO -p "STAGE_PROMPT" --output-format json --allow-tool='write'` | `--resume=SESSION-ID` avoids TTY picker; `--continue` can select another latest session. Optional autopilot uses `--max-autopilot-continues=COUNT`, default unlimited. |
| Gemini CLI | `gemini -p "STAGE_PROMPT" --output-format stream-json` with process cwd set to REPO | `--resume latest` or an explicit index is documented; latest is selection, not stable job identity. `model.maxSessionTurns` is configurable; headless turn-limit exit is `53`. |

Codex sources: [Noninteractive mode](https://learn.chatgpt.com/docs/non-interactive-mode), [Command reference](https://learn.chatgpt.com/docs/developer-commands?surface=cli). Copilot: [Command reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference), [Permissions](https://docs.github.com/en/copilot/how-tos/copilot-cli/use-copilot-cli/allowing-tools). Gemini: [Headless reference](https://geminicli.com/docs/cli/headless/), [Flags](https://geminicli.com/docs/cli/cli-reference/), [Configuration](https://geminicli.com/docs/reference/configuration/).

### Codex CLI facts

`exec` accepts an explicit prompt; piped stdin becomes additional context when a prompt argument exists. Default sandbox is read-only; `workspace-write` permits edits. Saved CLI auth is reused. JSONL exposes `thread.started`, `turn.started`, `turn.completed`, `turn.failed`, items and errors. `--output-schema` constrains the final response, while `-o` saves it. `--ephemeral` suppresses persisted rollout files, which conflicts with relying on those files for recovery. A Git repository is required unless explicitly overridden. Successful model completion and valid stage-result JSON do not prove correct knowledge edits. [Noninteractive contract](https://learn.chatgpt.com/docs/non-interactive-mode).

UNVERIFIED: complete `exec` exit-code taxonomy, graceful signal semantics, generic execution budget, and installed-version compatibility of combined resume/output flags. Use captured IDs rather than `--last` for concurrent jobs. The latter is a runner inference, not a provider guarantee.

### Copilot CLI facts

`-p` runs then exits. `-C` sets cwd before other work; `--attachment` supplies initial files. JSON output is JSONL. Explicit resume accepts ID/name/prefix; bare resume may require a TTY and errors rather than starting anew when selection is ambiguous. `--no-ask-user` disables that tool. Tool allow/deny rules and available/excluded tool sets are separate controls. [Command reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference), [Permission layers](https://docs.github.com/en/copilot/how-tos/copilot-cli/use-copilot-cli/allowing-tools).

Official docs have a permission wording conflict: command reference calls `--allow-all-tools` required programmatically, while the programmatic reference demonstrates scoped `--allow-tool` launches. Do not infer full permission is necessary; certify scoped launches. [Programmatic reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-programmatic-reference).

UNVERIFIED: full `-p` JSONL terminal-result schema and exit-code taxonomy. The documented `0/1/130` codes on the command page apply to `workflow run`, not automatically to `-p`. No native final-answer JSON Schema flag was established. Prompt-requested JSON needs independent validation. Autopilot continuation bounds and the previously researched eight stop-hook block cap are different mechanisms.

### Gemini CLI facts

`-p` or non-TTY starts headless mode. JSON output contains `response`, `stats`, optional `error`; stream-json emits init/session metadata, messages, tool requests/results, errors and final `result`. Headless exit codes are `0` success, `1` general/API failure, `42` invalid input, `53` turn limit. The page reports last update 2026-03-10. [Headless contract](https://geminicli.com/docs/cli/headless/).

Stdin supplies explicit context alongside `-p`. [Automation tutorial](https://geminicli.com/docs/cli/tutorials/automation/). Approval modes include default, auto_edit, yolo and plan; deprecated `--allowed-tools` is replaced by the policy engine. Extra workspace roots use `--include-directories`. [Flags](https://geminicli.com/docs/cli/cli-reference/). `model.maxSessionTurns` defaults to unlimited (`-1`). [Configuration](https://geminicli.com/docs/reference/configuration/).

UNVERIFIED: native JSON Schema enforcement for the semantic response, graceful signal completion, exact headless stable-ID resume syntax across docs, and policy settings sufficient for unattended stage edits. Output-format JSON structures the envelope, not the semantic `response` string.

## Codex desktop and programmatic control

Existing [hook findings](../provider-lifecycle-capabilities/findings.md) establish documented `Stop` continuation using `decision: block` plus reason; `stop_hook_active` identifies retries. This can request the current agent execute the skill stage. It does not launch an independent runner or establish successful stage edits. Async completion cannot start an idle turn, and SessionEnd is advisory. [Hooks](https://learn.chatgpt.com/docs/hooks).

Codex app-server is a documented client interface: `codex app-server`, initialize/initialized handshake, `thread/start` or `thread/resume`, then `turn/start`. It supports explicit cwd/approval/sandbox settings and per-turn `outputSchema`; skill invocation uses text `$skill-name` plus a skill item containing name/path. Read streamed items and `turn/completed` status (`completed`, `interrupted`, `failed`); `turn/interrupt` requests cancellation, and `turn/steer` requires the expected active turn. `thread/read` reads stored history without loading a thread. Version-specific schemas can be generated with `codex app-server generate-json-schema --out DIR`. [App-server reference](https://learn.chatgpt.com/docs/app-server).

The same reference documents stdio and Unix-socket transports, but labels the app-server command/WebSocket transport experimental and unsupported for production workloads. It does not, in the inspected material, establish a supported way for this shared runner to discover, authenticate to, and supervise the desktop app's existing conversation. Starting a separate server or CLI does not prove ownership or interception of desktop tools/conclusions. Desktop attestation mentions are not an attachment contract. UNVERIFIED: a supported desktop control endpoint and its ownership, subscriptions, approval responsibilities and concurrent-client rules. [App-server reference](https://learn.chatgpt.com/docs/app-server).

## Integration inferences and remaining gaps

The CLI interfaces can support a runner-owned semantic job with explicit prompt/context and machine-readable observations. Fresh bounded jobs do not require resuming the foreground user's conversation if the stage input packet contains the necessary evidence; that is an integration inference, not proof of information completeness.

The runner must distinguish transport/process completion, model turn completion, validated semantic result, and verified repository changes. A deadline or cancellation can bound supervision but does not undo partial edits or guarantee graceful cleanup. Hook-triggered secondary provider sessions may themselves run hooks; stage reentry, recursion, concurrent repository edits and feedback into the foreground session remain unspecified. No implicit child inheritance, CLI/desktop parity, unlimited stop gate, shutdown guarantee or automatic cross-repository sharing is established.

Still needed before executable wiring is promised: each provider's pinned-version flags/result schema and permissions; semantic success validation and partial-edit recovery; bounded retry rules; stage-run identity; and either a documented desktop attachment contract or a separately chosen foreground continuation path. Architecture and support choices remain with the active decision ticket.
