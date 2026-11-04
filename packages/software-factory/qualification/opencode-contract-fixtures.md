# OpenCode V2 2.1.3 synthetic source-contract fixtures

Status: deterministic test-only proposals. Native OpenCode qualification remains **USER BLOCKED**. No provider execution, adapter registration, runtime source binding, supported permission mode, or source-to-binary correspondence is established.

## Provenance

Read-only official immutable source at commit `bb25a2f4a3f3f04d7c344bec0c0574ea3510b3b1` was inspected directly. The [CLI manifest](https://github.com/anomalyco/opencode/blob/bb25a2f4a3f3f04d7c344bec0c0574ea3510b3b1/packages/cli/package.json#L1-L5) identifies `@opencode/cli@2.1.3`. The earlier source archive was absent; only HTTPS source text and directory metadata were retrieved. No package, native executable, authentication state, credentials, user configuration, server, or model was accessed.

Inspected contracts:

- [JSONL envelope and text writers](https://github.com/anomalyco/opencode/blob/bb25a2f4a3f3f04d7c344bec0c0574ea3510b3b1/packages/cli/src/run/noninteractive.ts#L100-L120): JSON serialization and platform EOL.
- [Step, text and optional reasoning parts](https://github.com/anomalyco/opencode/blob/bb25a2f4a3f3f04d7c344bec0c0574ea3510b3b1/packages/cli/src/run/noninteractive.ts#L267-L339), [completed/failed tool parts and execution branches](https://github.com/anomalyco/opencode/blob/bb25a2f4a3f3f04d7c344bec0c0574ea3510b3b1/packages/cli/src/run/noninteractive.ts#L390-L544), and [projected text suffix/tool reconciliation](https://github.com/anomalyco/opencode/blob/bb25a2f4a3f3f04d7c344bec0c0574ea3510b3b1/packages/cli/src/run/noninteractive.ts#L548-L668) supply the synthetic record shapes.
- [Step-end schema](https://github.com/anomalyco/opencode/blob/bb25a2f4a3f3f04d7c344bec0c0574ea3510b3b1/packages/schema/src/session-event.ts#L369-L383), [finish reasons](https://github.com/anomalyco/opencode/blob/bb25a2f4a3f3f04d7c344bec0c0574ea3510b3b1/packages/schema/src/llm.ts#L5-L6), [token fields](https://github.com/anomalyco/opencode/blob/bb25a2f4a3f3f04d7c344bec0c0574ea3510b3b1/packages/schema/src/token-usage.ts#L5-L14), and [error shape](https://github.com/anomalyco/opencode/blob/bb25a2f4a3f3f04d7c344bec0c0574ea3510b3b1/packages/schema/src/session-error.ts#L6-L14) constrain the sample values. Zero cost/tokens are synthetic placeholders and provide no usage or cost evidence.

The JSON file contains authored records, not native observations. Scenario names and ending-branch labels are fixture metadata; they are never inserted into provider output.

## Explicit test seams

`test/fixtures/opencode-contract.mjs` is an isolated test-only helper. It imports no product module and never launches a process, constructs native argv, loads configuration, reads a referenced resource, or registers an adapter.

`inspectSyntheticOpenCodeTranscript` consumes an array of byte chunks representing one complete captured stdout, fixture-supplied exit/signal facts, and an external attempt envelope. It requires matching outer/part session IDs and unique part identities. Tool IDs are scoped by native message ID. Each invocation owns fresh identity state; an attempt ID is a factory-side label, never a claimed OpenCode field. The source [filters ordinary events to its root session](https://github.com/anomalyco/opencode/blob/bb25a2f4a3f3f04d7c344bec0c0574ea3510b3b1/packages/cli/src/run/noninteractive.ts#L221-L236) and [keys tool state by message and tool ID](https://github.com/anomalyco/opencode/blob/bb25a2f4a3f3f04d7c344bec0c0574ea3510b3b1/packages/cli/src/run/noninteractive.ts#L808-L821); it emits no attempt identity or complete child-session tree.

Selection resets assistant text at tool outcomes, new steps and new assistant messages, appends same-message text including projected suffixes, and ignores reasoning/tool output. Revisiting an older message refuses ambiguous selection. Malformed/truncated JSONL, unknown record fields/shapes, mismatched sessions, repeated identities, native errors, every failed tool, nonzero/unknown exits, signals and empty candidate segments reject using fixed categories without echoing payloads. This is a conservative subset proposal, not a full native protocol decoder. A candidate is arbitrary text, not a validated factory result.

`inspectSyntheticOpenCodePromptData` checks only literal in-memory UTF-8 data. Tests preserve slash/at-sign commands, resource-looking URIs, shell-looking bytes, CRLF, Unicode and replacement characters. This does not exercise native prompt preprocessing, stdin/file preparation, resource expansion, skill delivery, tool permissions, hooks/plugins/MCP, configuration or model delivery.

## Terminal and denial limits

There is no emitted execution-success record. A `step_finish` is per-step, and repeated step finishes cannot certify completion. [Execution branches](https://github.com/anomalyco/opencode/blob/bb25a2f4a3f3f04d7c344bec0c0574ea3510b3b1/packages/cli/src/run/noninteractive.ts#L494-L544) allow source success and a user-reason interruption with the local interruption flag false to return without another JSONL record. Paired fixtures therefore retain identical plausible assistant bytes and fixture exit zero for both branch labels. Both yield only `state: candidate` with `terminal: unknown`; this is branch-level source ambiguity, not observed native interruption behavior. Local SIGINT is separately [assigned exit 130](https://github.com/anomalyco/opencode/blob/bb25a2f4a3f3f04d7c344bec0c0574ea3510b3b1/packages/cli/src/run/noninteractive.ts#L677-L684) and its exit fixture rejects.

Noninteractive V2 [rejects asks with model-visible feedback and permits continuation](https://github.com/anomalyco/opencode/blob/bb25a2f4a3f3f04d7c344bec0c0574ea3510b3b1/packages/cli/src/run/noninteractive.ts#L158-L185). The denial fixture uses the source's failed-tool shape with a synthetic message, followed by plausible text and exit zero. All failed tools reject without guessing permission-error vocabulary or converting refusal to factory `needs_input`.

Pure API parent/child pagination mapping is deferred. This slice inspects only the CLI's root-session filter, recursive ask ownership and message reconciliation; it does not establish the full session-list API or concurrent pagination contract. Child-inclusive telemetry, native stop/exit behavior, released binary equivalence, configuration preservation, requested permission profiles, startup effects and whole-process cleanup remain unqualified. No transcript in this suite can produce provider success.

## Local fixture budgets and verification

These inclusive budgets are local proposals, not OpenCode maxima: 1,048,576 bytes per complete capture or prompt; 65,536 bytes per JSONL record excluding LF/CRLF; 4,096 records; 65,536 UTF-8 bytes in the candidate segment. Decoding is fatal on malformed UTF-8, source JSONL requires its final LF, and escaped lone surrogates in surfaced text refuse. Chunk segmentation includes splits inside multibyte UTF-8; it is an in-memory complete-capture test, not a native streaming transport proof.

From `packages/software-factory`, run only the focused dependency-free suite:

    rtk proxy /private/tmp/factory-qualified-node-342t16a/node-v24.22.1-darwin-arm64/bin/node --test test/opencode-contract.test.mjs

Observed 2026-11-04 UTC after the coordinator released the composition pause: 68/68 pass, zero failures/skips/cancelled/todo, 71.914583 ms. Log: `/private/tmp/factory-opencode-contract-focused-green.log`. Initial missing-helper red/green and selection red/green are retained under `/private/tmp/factory-opencode-contract-first-{red,green}.log` and `/private/tmp/factory-opencode-contract-selection-{red,green}.log`. The identity slice passed 43/43, zero failures/skips/cancelled/todo, 37.233167 ms in `/private/tmp/factory-opencode-contract-identity-green.log`; its preceding red is retained. The bounds slice first failed for its missing prompt helper export, before encoding/bounds implementation. Coordinator owns registry/CI, canonical plan/handoff and integrated proof. Original fixture/notification/learning baseline files are untouched by this four-file slice.

Reflection: terminal ambiguity and attempt isolation are encoded in focused tests and this qualification note. No additional brain or skill edit is needed; canonical plan reconciliation belongs to the coordinator.
