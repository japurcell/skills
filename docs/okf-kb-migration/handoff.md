# OKF Agent-KB Migration Handoff

## Goal

Finish a planning-only, implementation-ready OKF v0.2 migration design with GitHub Copilot CLI as the primary supported agent. Preserve the standard interactive Copilot experience if its documented capabilities can meet an explicitly accepted assurance contract. Implementation and the implementation ExecPlan remain out of scope until the revised map closes.

## Status

- The earlier twelve-decision Gemini-first map was complete, but the user corrected its deployment premise: Gemini CLI is not the durable primary target; GitHub Copilot CLI is.
- The map destination and notes now state that Copilot CLI is primary.
- **Provider Integration and State**, **Rollout and Rollback**, and **Implementation Sequencing and Handoff** are `obsolete`; their provider-neutral evidence remains reusable, while their Copilot gating and Gemini-first rollout path must be replaced.
- **Copilot CLI Integration Surfaces** is closed from current primary-source research.
- **Copilot-First Runtime Contract** is closed and indexed after four accepted Grilling rounds and explicit shared-understanding confirmation.
- Four replacement decisions are now specified. **Copilot-First Provider Integration and State** is the sole unblocked frontier ticket; **Dual-Provider Evaluation Amendment**, **Copilot-First Rollout and Rollback**, and **Copilot-First Implementation Sequencing and Handoff** are blocked in dependency order.
- **Copilot-First Runtime Contract** round 1 is accepted: use the standard Copilot CLI project extension with atomic legacy fallback, deny-all-tools unsafe state, and explicitly labeled `advisory_stop` semantics instead of claiming pre-model enforcement.
- **Copilot-First Runtime Contract** round 2 accepted the fallback/advisory-stop matrix, capability-tested experimental enrollment, and exclusion of strict pre-inference tasks and a separate SDK host. The user corrected Q5: Gemini must remain a fully supported OKF provider for now, including its adapter, evidence, and rollout.
- **Copilot-First Runtime Contract** round 3 accepted Copilot `default` as the migration completion criterion. Gemini remains fully implemented and independently promotable, Gemini-only failures do not block Copilot, and shared-core failures block every provider.
- **Copilot-First Runtime Contract** round 4 accepted both adapters before promotion, Copilot-first independent rollout, exact provider-neutral parity with documented enforcement/envelope differences, and continued Gemini testing until a separate removal decision.
- No migration implementation or implementation ExecPlan exists.

## Next Focus

Resolve **Copilot-First Provider Integration and State** with the user.

## Exact Next Step

Activate `handoff`, `wayfinder`, and `grilling`; verify that `copilot-first-runtime-contract.md` is `closed`; claim `tickets/copilot-first-provider-integration-and-state.md`; and resolve only that ticket. Use the existing Copilot research and obsolete provider ticket as evidence without reviving their superseded rollout premise.

## Current Evidence and Recommendation

- A repository extension at `.github/extensions/<name>/extension.mjs` can use the CLI-bundled `@github/copilot-sdk/extension`, register `onUserPromptSubmitted`, and return `additionalContext` for each submitted prompt. This preserves the normal CLI and requires no package installation.
- This SDK hook avoids the config-file `userPromptSubmitted` output-discard behavior and the batched-message ambiguity of config-file `userPromptTransformed`.
- GitHub documents extensions as experimental and currently requires experimental CLI mode.
- GitHub explicitly states that `onUserPromptSubmitted` cannot reject a prompt or enforce policy. A project extension can deny tools through `onPreToolUse`, but it cannot prevent the model from reading the prompt or emitting text.
- The current Copilot auto-ingest integration already uses advisory prompt context plus post-turn stop hooks and explicitly fails open on unexpected prompt-rewrite exceptions. Pre-model denial was an added assurance goal in the old map, not part of the compatibility baseline.
- The recommended map change separates context integrity from prompt admission. Copilot can guarantee one complete OKF or legacy context block and deny tools in unsafe state; it must label the remaining response-level condition `advisory_stop`, never `hard_stop`.
- A standalone SDK host can enforce before calling `session.send()`, but GitHub documents several standard TUI features as unavailable through the SDK.

## Preserved Decisions

- Authored `.agents/instructions/` and `.agents/memory/` documents remain canonical. A deterministic producer owns the committed `.agents/okf/` sidecar and projection manifest.
- The current inventory is 29 canonical inputs and 42 concepts. Immutable `.agents/sources/`, freshness reconciliation, offline selection, deterministic output, explicit typed relationships, mandatory context, atomic legacy fallback, and privacy-safe diagnostics remain required.
- The selector, producer, profile, source-summary transition, and provider-neutral evaluation decisions remain closed unless the Copilot contract reveals a direct conflict.
- Safety and relevant-context recall outrank token reduction. The revised contract must state precisely which safety properties the Copilot host enforces and which are advisory.

## Relevant Artifacts

- `docs/okf-kb-migration/map.md` — active destination, closed decisions, fog, and scope.
- `docs/okf-kb-migration/tickets/copilot-cli-integration-surfaces.md` — closed capability research ticket.
- `docs/okf-kb-migration/research/copilot-cli-integration-surfaces.md` — current source-backed surface comparison and recommended contract split.
- `docs/okf-kb-migration/tickets/copilot-first-runtime-contract.md` — sole open decision.
- `docs/okf-kb-migration/research/copilot-cli-hooks-rollout.md` — earlier config-hook assessment; still accurate for config hooks but incomplete for the newly preferred project-extension boundary.
- `docs/okf-kb-migration/tickets/provider-integration-and-state.md` — obsolete Gemini-first integration decision with reusable provider-neutral details.

## Verification State

- No local `copilot` executable or version was available; actual extension behavior remains untested.
- Official documentation was checked on 2026-09-08 for CLI config hooks, project extensions, SDK prompt hooks, and SDK/CLI compatibility.
- Research subagent delegation was required by Wayfinder but unavailable because the session exposed no `spawn_agent` capability and no idle agents; the main agent performed and recorded the bounded primary-source research.
- `git diff --check` and ticket/link/frontier validation passed after the runtime contract closed: 11 closed tickets, four open replacement tickets, three obsolete tickets, and **Copilot-First Provider Integration and State** as the sole frontier.
- The mandatory end-of-session `update-agent-docs` pass found no `.agents/instructions/` or `.agents/memory/` change necessary. This session changed only ordinary planning documents under the existing `docs/okf-kb-migration/` effort, and the current architecture guidance already routes long-lived effort plans there.

## Durable Learnings

- Provider priority is a destination-level constraint. Confirm the user's durable primary host before closing provider rollout and implementation-sequencing decisions.
- Distinguish config-file Copilot hooks from in-process project-extension SDK hooks; they have different prompt identity and output capabilities.
- Do not make a provider-neutral context migration depend on a stronger prompt-admission property than the user's primary host can provide without presenting that tradeoff explicitly.

## Suggested Skills

- Resume with `handoff`, then `wayfinder` and `grilling` for the open decision.
- Use `official-sources` whenever Copilot extension or hook behavior is reassessed.
- After the revised map closes, create the implementation ExecPlan with `exec-plans` and mandatory `tdd`.
- End repository-changing sessions with `update-agent-docs`.
