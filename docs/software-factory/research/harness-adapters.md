# Harness adapter feasibility

Research date: 2026-10-08. These are documented integration surfaces, not implemented or conformance-tested factory adapters. Model choice and harness choice are separate: a provider/model available in Pi does not mean the Codex or Gemini CLI harness is supported.

For the 2026-10-14 permission/approval investigation, use [Native permission interaction design](native-permissions/findings.md) and its pinned per-harness reports. They refine this historical survey's approval, scope and lifecycle questions; they still do not establish live adapter conformance.

| Harness | Evidence-backed entry point | What remains to prove |
| --- | --- | --- |
| Codex | Local `codex-cli 0.160.1` help confirms `codex exec --json`, model selection, structured final output via `--output-schema`, and resume. OpenAI distinguishes bounded CLI jobs, SDK integration, and app-server for persistent conversations, streamed events, and approvals. [Official integration guide](https://developers.openai.com/blog/codex-as-a-platform) | Confirm which protocol fits interactive approvals; pin version and fixtures; test cancellation and interruption recovery. |
| GitHub Copilot | Programmatic CLI supports JSONL via `--output-format json`, explicit models, and session transcript export. Dynamic workflows have their own run/result and exit-code contract. [Programmatic reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-programmatic-reference) | Do not confuse prompt mode with the separate workflow API. Prove complete tool/usage extraction and approval behavior under chosen permissions. |
| Gemini CLI | Headless mode documents a JSONL stream covering initialization, messages, tool requests/results, errors, and final usage/outcome. [Headless reference](https://geminicli.com/docs/cli/headless/) | Verify installed-version flags and stream fixtures, cancellation, model routing, and whether skill loading is explicitly observable. |
| OpenCode | `opencode run --format json` produces newline-delimited events. Current v2 docs also describe model/agent selection and session export. [Command reference](https://opencode.ai/v2/docs/cli/commands/) | Pin the CLI generation; prove stable event normalization and cancellation/resume semantics for that version. |
| Pi | RPC runs a subprocess with JSONL commands, responses, and events; the project also exposes an SDK. The earlier badlogic/pi-mono link redirects to earendil-works/pi. [RPC source documentation](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/rpc.md) | Decide whether bounded JSON mode or RPC fits each step; verify version-specific tool, retry, compaction, and usage events. |

## Proposed portable port

The runtime should ask an adapter for capabilities before launching work. Required capabilities come from the workflow step, not from a model's suggested command. An adapter advertises structured results, streaming, interrupt, resume, approval requests, tool events, usage, and skill events with explicit `supported`, `partial`, or `unavailable` values. Reject an incompatible route before work begins.

The launch request contains a run/step/attempt ID, exact harness and version, model and effort when supported, workspace, task prompt reference, input artifacts, output schema, and permission profile. Launch the executable with an argument array; never concatenate agent-produced shell text into a command. Keep native approval and sandbox controls enabled according to the chosen execution profile.

The output is a stream plus a terminal result. Normalize messages and tool calls without pretending all harnesses expose identical detail. Store original event provenance and payload references. Preserve unknown token counts as unknown; do not display zero or calculate a fabricated cost. Distinguish a model retry from a process retry, a failed quality gate, and a user cancellation.

## Observability truthfulness

Record requested skills and their hashes at dispatch. Only mark a skill as loaded when the harness emits reliable evidence. Reading a file named `SKILL.md` is at most an inferred use, not proof of activation. Show this distinction in the UI. Expose the exact visible prompt, responses, tool arguments/results, errors, artifacts, and usage that the harness permits; do not promise private model reasoning.

Live and historical views should read the same persisted event contract. A live transport merely delivers new records after a cursor. Replaying recorded events must never rerun tools. Preserve code revision, workflow revision, adapter version, and context bundle hash so the user can explain differences between runs.

## First implementation experiment

Before adopting any factory architecture, run one small change through Codex and one through a second harness in disposable workspaces. Verify a common trace, structured result, failed gate, cancellation, and restart. Compare normalized events against the original native output. Add the remaining adapters only after they pass the same contract scenarios. This is a proposed experiment; no live agent invocation occurred in this research.
