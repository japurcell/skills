# OKF Agent-KB Migration Handoff

## Goal

Finish a planning-only, implementation-ready OKF v0.2 migration design with GitHub Copilot CLI as the primary supported agent. Preserve the standard interactive Copilot experience if its documented capabilities can meet an explicitly accepted assurance contract. Implementation and the implementation ExecPlan remain out of scope until the revised map closes.

## Status

- The earlier twelve-decision Gemini-first map was complete, but the user corrected its deployment premise: Gemini CLI is not the durable primary target; GitHub Copilot CLI is.
- The map destination and notes now state that Copilot CLI is primary.
- **Provider Integration and State**, **Rollout and Rollback**, and **Implementation Sequencing and Handoff** are `obsolete`; their provider-neutral evidence remains reusable, while their Copilot gating and Gemini-first rollout path must be replaced.
- **Copilot CLI Integration Surfaces** is closed from current primary-source research.
- **Copilot-First Runtime Contract** is closed and indexed after four accepted Grilling rounds and explicit shared-understanding confirmation.
- **Copilot-First Provider Integration and State** and **Dual-Provider Evaluation Amendment** are closed and indexed after explicit confirmation. **Copilot-First Rollout and Rollback** is now the sole unblocked frontier; **Copilot-First Implementation Sequencing and Handoff** remains blocked behind it.
- **Copilot-First Runtime Contract** round 1 is accepted: use the standard Copilot CLI project extension with atomic legacy fallback, deny-all-tools unsafe state, and explicitly labeled `advisory_stop` semantics instead of claiming pre-model enforcement.
- **Copilot-First Runtime Contract** round 2 accepted the fallback/advisory-stop matrix, capability-tested experimental enrollment, and exclusion of strict pre-inference tasks and a separate SDK host. The user corrected Q5: Gemini must remain a fully supported OKF provider for now, including its adapter, evidence, and rollout.
- **Copilot-First Runtime Contract** round 3 accepted Copilot `default` as the migration completion criterion. Gemini remains fully implemented and independently promotable, Gemini-only failures do not block Copilot, and shared-core failures block every provider.
- **Copilot-First Runtime Contract** round 4 accepted both adapters before promotion, Copilot-first independent rollout, exact provider-neutral parity with documented enforcement/envelope differences, and continued Gemini testing until a separate removal decision.
- **Dual-Provider Evaluation Amendment** round 1 accepted `agent-kb-evaluation@2.0.0`, one shared semantic corpus plus provider suites, three conjunctive-but-independent verdicts, exact-build qualification, exact provider-neutral parity with semantic envelope oracles, comprehensive lifecycle/failure gates, and separate selector versus full-path latency gates.
- **Dual-Provider Evaluation Amendment** round 2 accepted simulated-plus-live-host qualification, per-platform deployment tuples, compact committed qualification manifests backed by CI artifacts, sentinel-based privacy gates, and explicit full-runtime, adapter-overhead, and two-second subprocess limits.
- **Dual-Provider Evaluation Amendment** round 3 accepted deployed-input-only provider promotion cases, deterministic adapter-byte oracles plus privacy-safe live-host lifecycle probes, offline local enrollment, explicit `pass`/`fail`/`incomplete` results, byte-based gates with non-gating token and legacy-latency reports, and digest-scoped evidence invalidation.
- No migration implementation or implementation ExecPlan exists.

## Next Focus

Resolve **Copilot-First Rollout and Rollback** with the user.

## Exact Next Step

Activate `handoff`, `wayfinder`, and `grilling`; verify that `dual-provider-evaluation-amendment.md` is `closed`; claim `tickets/copilot-first-rollout-and-rollback.md`; and resolve only that ticket.

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
- `docs/okf-kb-migration/tickets/copilot-first-provider-integration-and-state.md` — closed replacement integration and state contract.
- `docs/okf-kb-migration/tickets/dual-provider-evaluation-amendment.md` — next unblocked frontier ticket.
- `docs/okf-kb-migration/research/copilot-cli-hooks-rollout.md` — earlier config-hook assessment; still accurate for config hooks but incomplete for the newly preferred project-extension boundary.
- `docs/okf-kb-migration/tickets/provider-integration-and-state.md` — obsolete Gemini-first integration decision with reusable provider-neutral details.
- `skills/handoff/SKILL.md` — minimally hardened to reread edit anchors and prefer independent patches when stale context could reject unrelated updates.

## Verification State

- No local `copilot` executable or version was available; actual extension behavior remains untested.
- Official documentation was checked on 2026-09-08 for CLI config hooks, project extensions, SDK prompt hooks, and SDK/CLI compatibility.
- Official SDK types, dispatch code, and extension lifecycle documentation were rechecked on 2026-09-09. They confirm the callback set required by the proposed in-memory lifecycle, while actual target-build ordering remains untested because no local Copilot CLI is available.
- Research subagent delegation was required by Wayfinder but unavailable because the session exposed no `spawn_agent` capability and no idle agents; the main agent performed and recorded the bounded primary-source research.
- `git diff --check` and ticket/link/frontier validation passed after the runtime contract closed: 11 closed tickets, four open replacement tickets, three obsolete tickets, and **Copilot-First Provider Integration and State** as the sole frontier.
- The mandatory end-of-session `update-agent-docs` pass found no `.agents/instructions/` or `.agents/memory/` change necessary. This session changed only ordinary planning documents under the existing `docs/okf-kb-migration/` effort, and the current architecture guidance already routes long-lived effort plans there.
- On resume, the runtime-contract prerequisite was verified `closed` and **Copilot-First Provider Integration and State** was claimed by `subagent-a7k2m9`. Two read-only exploration agents confirmed that no Copilot project extension exists yet, current Copilot and Gemini workspace discovery rules differ, and the existing source-ingest compatibility hooks can reconcile under their manifest lock. No implementation files were changed.
- After closure, ticket/link/frontier validation passed with 12 closed tickets, three open tickets, three obsolete tickets, and **Dual-Provider Evaluation Amendment** as the sole frontier. `git diff --check` and the unchanged handoff grader's Python compilation passed.
- On 2026-09-09, `copilot-first-provider-integration-and-state.md` was reverified `closed`; **Dual-Provider Evaluation Amendment** was claimed by `subagent-k3m8q2`, resolved across three accepted rounds, explicitly confirmed, closed, and indexed. `git diff --check` and ticket/link/frontier validation passed with 13 closed tickets, two open tickets, three obsolete tickets, and **Copilot-First Rollout and Rollback** as the sole frontier.
- The mandatory end-of-session `update-agent-docs` pass found no `.agents/instructions/` or `.agents/memory/` edit necessary: this session changed only ordinary planning documents, and the existing file map and repository instructions already cover the effort and its documentation location.
- The handoff skill's canonical validator could not run because its undeclared `PyYAML` dependency is absent; the documented body-only fallback confirmed unchanged frontmatter and a clean exact diff. `./scripts/install.sh` could not refresh installed copies because `/root/.agents/skills` is read-only and the installer has no destination override. No dependency was installed and `HOME` was not repurposed.

## Durable Learnings

- Provider priority is a destination-level constraint. Confirm the user's durable primary host before closing provider rollout and implementation-sequencing decisions.
- Distinguish config-file Copilot hooks from in-process project-extension SDK hooks; they have different prompt identity and output capabilities.
- Do not make a provider-neutral context migration depend on a stronger prompt-admission property than the user's primary host can provide without presenting that tradeoff explicitly.
- Removing duplicated compatibility hooks is a valid simplification only when the replacement owns their enrolled-provider behavior and unsupported-host limitations are stated explicitly.
- Three rejected patch attempts occurred while recording round 4: two malformed payloads and one stale context match. None changed files. For multi-file documentation patches, verify literal delimiters and current anchor text first, then prefer smaller independent patches.
- One empty patch targeted a mistyped ticket filename while recording the evaluation amendment; it failed before changing files. Copy the verified path from the active ticket rather than retyping it in patch headers. A later search also named an absent `.github/workflows` directory; treat its absence as repository state, not as evidence of a CI implementation.

## Suggested Skills

- Resume with `handoff`, then `wayfinder` and `grilling` for the open decision.
- Use `official-sources` whenever Copilot extension or hook behavior is reassessed.
- After the revised map closes, create the implementation ExecPlan with `exec-plans` and mandatory `tdd`.
- End repository-changing sessions with `update-agent-docs`.
