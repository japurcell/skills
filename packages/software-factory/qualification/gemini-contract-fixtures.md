# Gemini 0.65.0 synthetic contract fixtures

Status: deterministic test-only proposals. Gemini provider qualification remains blocked. No runtime adapter, provider registration, installation binding, or supported permission mode is established.

## Provenance and source boundary

The official [v0.65.0 release](https://github.com/google-gemini/gemini-cli/releases/tag/v0.65.0) resolves to commit `6006c14a4decfe4b891c6263ad6ad5992e404b5b`. Read-only official source text at that commit supplies the event fields:

- [Legacy branch](https://github.com/google-gemini/gemini-cli/blob/6006c14a4decfe4b891c6263ad6ad5992e404b5b/packages/cli/src/nonInteractiveCli.ts#L232-L582): init; user and assistant messages; tools; stopped/blocked handling; terminal emission. Lines 69-75 select the agent-session branch using effective settings.
- [Agent-session branch](https://github.com/google-gemini/gemini-cli/blob/6006c14a4decfe4b891c6263ad6ad5992e404b5b/packages/cli/src/nonInteractiveCliAgentSession.ts): `runNonInteractive`, `emitFinalResult`, and switch cases `tool_request`, `tool_response`, `error`, `agent_end` supply the corresponding stream records.
- [Output types](https://github.com/google-gemini/gemini-cli/blob/6006c14a4decfe4b891c6263ad6ad5992e404b5b/packages/core/src/output/types.ts#L28-L103): six event types, `tool_id` correlation, optional error payloads, and result status without final response or phase.
- [Tool errors](https://github.com/google-gemini/gemini-cli/blob/6006c14a4decfe4b891c6263ad6ad5992e404b5b/packages/core/src/tools/tool-error.ts): enum `ToolErrorType.STOP_EXECUTION` serializes as `stop_execution`.

The earlier research's retained `/tmp/factory-gemini-0.65.0-bundle` is absent. This task did not obtain, execute, or compare a binary or bundle, change a pin, or establish source-to-binary correspondence. These are newly authored synthetic records, not observed native transcripts. Branch labels are fixture metadata only; the source emits no branch discriminator, and the tests do not execute either native branch.

## Test-only seams

`test/fixtures/gemini-contract.mjs` exports two isolated in-memory helpers. Neither imports product modules or launches a process, reads files/configuration, or constructs a native invocation.

`inspectSyntheticGeminiTranscript` consumes complete stdout bytes, native exit/signal facts supplied by the fixture, and an expected init session ID. It rejects malformed JSONL, unsupported record shapes, unknown fields, contradictory/missing/duplicate terminals, missing/mismatched/duplicate init, tool mismatches/duplicates/pending calls, tool errors, error events, all warning events, nonzero/unknown exits, signals, and empty final segments. All warnings remain unresolved conservatively; no warning whitelist is claimed. Rejections return only fixed categories, without copying private-looking payload text.

The proposed selection resets assistant text on tool use and tool completion, ignores user/tool output and assistant text while tools remain pending, and joins only later assistant deltas. A valid-looking transcript returns `state: candidate`, never provider success. Stats are unused and establish no usage or cost. A future adapter would still need the original workflow result validator and all accepted native gates; this helper supplies neither.

`inspectSyntheticPromptData` checks a Buffer as UTF-8 and returns its literal text as `state: data`. Fixtures preserve leading slash, file/agent at-sign references, MCP-like tokens, shell-like text, CRLF and Unicode. This proves only in-memory byte handling. It does not exercise Gemini preprocessing, prompt files, stdin/argv composition, recursive references, trust, permissions, hooks, extensions/MCP, sandboxing, or model delivery. No prompt-file/native-delivery proof is claimed.

## Unobservable stop limitation

Legacy `AgentExecutionStopped` emits `result: success` while its stop message is written only for text output. Agent-session `agent_end` can likewise emit success while an internal stop message is text-only. Consequently ordinary completion and an internal stop can produce identical assistant-plus-terminal JSONL. Paired synthetic fixtures retain those identical bytes and both yield only a candidate. No invented stop flag, phase field, or branch marker repairs that missing evidence. Visible hook-block warnings and `stop_execution` tool errors reject even if a later terminal says success.

## Conservative fixture budgets

These are local test proposal limits, not documented Gemini maxima or measured native allowances:

| Input | Inclusive limit |
| --- | --- |
| Complete transcript or prompt data | 1,048,576 bytes |
| One JSONL record, excluding LF | 65,536 bytes |
| Transcript records | 4,096 |
| Candidate assistant segment across chunks | 65,536 UTF-8 bytes |

JSONL requires a final LF and no empty records. UTF-8 decoding is fatal on invalid byte sequences; assistant text with escaped lone surrogates is rejected. Literal replacement characters remain data. Unknown source shapes refuse rather than become support assumptions.

## Verification and integration handoff

From `packages/software-factory`, the focused command uses the accepted runtime directly and needs no dependencies, package installation, build, native CLI, or product load:

    /Users/adam/homebrew/bin/rtk proxy /private/tmp/factory-qualified-node-342t16a/node-v24.22.1-darwin-arm64/bin/node --test test/gemini-contract.test.mjs

Observed 2026-11-04 UTC: 83/83 pass, zero failures/skips/cancelled/todo, 49.456 ms. Log: `/tmp/factory-gemini-contract-focused-green.log`. Earlier red/green slices demonstrated missing consumer, incorrect tool segmentation, accepted tool failures, accepted invalid terminal/session/exit records, and missing encoding/bounds handling. The final bounds red run retained 68 passes/15 failures in `/tmp/factory-gemini-contract-bounds-red.log` before the fix.

Coordinator integrated source9e8530d6 through handback519c618d and registers only `qualification --area gemini-contract`, with no provider metadata. Canonical `adapters --provider gemini` and provider-filtered qualification still refuse. The public selector regression lives in qualification/ci.test.mjs, keeping original31fixture/36notification/13learning baseline cases and registrations byte-unchanged. Coordinator pinned proof83fixtures+13CI=96/96,zero skips,530.134ms; release descriptor guards3/3,1552.142ms, fiveJS syntax/actionlint pass. Logs `/tmp/factory-gemini-contract-integration-focused.log` and `/tmp/factory-gemini-contract-release-providers.log`; registration red retained separately. No runtime provider adapter, support binding or native acceptance is established. Broad composition/native proof waits for candidate handback and coordinator freeze.

Reflection: the missing stop discriminator is retained structurally in paired ambiguity tests and this scoped note. No separate brain or skill edit is needed; coordinator owns canonical plan/handoff updates.
