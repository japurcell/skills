# OKF Agent-KB Migration Handoff

## Goal

Begin the approved OKF v0.2 migration through a dependency-ordered implementation ExecPlan, with GitHub Copilot CLI as the primary supported agent and Gemini retained as a fully supported, independently promotable provider. The planning map is closed; implementation has not started.

## Status

- The earlier twelve-decision Gemini-first map was complete, but the user corrected its deployment premise: Gemini CLI is not the durable primary target; GitHub Copilot CLI is.
- The map destination and notes now state that Copilot CLI is primary.
- **Provider Integration and State**, **Rollout and Rollback**, and **Implementation Sequencing and Handoff** are `obsolete`; their provider-neutral evidence remains reusable, while their Copilot gating and Gemini-first rollout path must be replaced.
- **Copilot CLI Integration Surfaces** is closed from current primary-source research.
- **Copilot-First Runtime Contract** is closed and indexed after four accepted Grilling rounds and explicit shared-understanding confirmation.
- **Copilot-First Provider Integration and State**, **Dual-Provider Evaluation Amendment**, **Copilot-First Rollout and Rollback**, and **Copilot-First Implementation Sequencing and Handoff** are closed and indexed after explicit confirmation. The revised map has no open tickets or remaining fog.
- A novice-facing implementation overview now summarizes the accepted design, prompt flow, safety outcomes, ten gates, unchanged surfaces, and proof strategy with Mermaid diagrams. It is linked from `map.md`; it does not replace the closed tickets as the source of truth.
- **Copilot-First Runtime Contract** round 1 is accepted: use the standard Copilot CLI project extension with atomic legacy fallback, deny-all-tools unsafe state, and explicitly labeled `advisory_stop` semantics instead of claiming pre-model enforcement.
- **Copilot-First Runtime Contract** round 2 accepted the fallback/advisory-stop matrix, capability-tested experimental enrollment, and exclusion of strict pre-inference tasks and a separate SDK host. The user corrected Q5: Gemini must remain a fully supported OKF provider for now, including its adapter, evidence, and rollout.
- **Copilot-First Runtime Contract** round 3 accepted Copilot `default` as the migration completion criterion. Gemini remains fully implemented and independently promotable, Gemini-only failures do not block Copilot, and shared-core failures block every provider.
- **Copilot-First Runtime Contract** round 4 accepted both adapters before promotion, Copilot-first independent rollout, exact provider-neutral parity with documented enforcement/envelope differences, and continued Gemini testing until a separate removal decision.
- **Dual-Provider Evaluation Amendment** round 1 accepted `agent-kb-evaluation@2.0.0`, one shared semantic corpus plus provider suites, three conjunctive-but-independent verdicts, exact-build qualification, exact provider-neutral parity with semantic envelope oracles, comprehensive lifecycle/failure gates, and separate selector versus full-path latency gates.
- **Dual-Provider Evaluation Amendment** round 2 accepted simulated-plus-live-host qualification, per-platform deployment tuples, compact committed qualification manifests backed by CI artifacts, sentinel-based privacy gates, and explicit full-runtime, adapter-overhead, and two-second subprocess limits.
- **Dual-Provider Evaluation Amendment** round 3 accepted deployed-input-only provider promotion cases, deterministic adapter-byte oracles plus privacy-safe live-host lifecycle probes, offline local enrollment, explicit `pass`/`fail`/`incomplete` results, byte-based gates with non-gating token and legacy-latency reports, and digest-scoped evidence invalidation.
- No migration implementation or implementation ExecPlan exists.

## Next Focus

Create the implementation ExecPlan from the closed map, then begin only gate 1 under explicit ownership and test-first execution.

## Exact Next Step

Activate `handoff`, `exec-plans`, mandatory `tdd`, and `official-sources`; recheck the OKF v0.2 baseline; write `docs/okf-kb-migration/implementation-execplan.md`; assign gate 1 ownership; and begin only gate 1. Do not reopen closed design decisions without contradictory implementation evidence.

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
- `docs/okf-kb-migration/implementation-overview.md` — novice-facing summary and diagrams of the planned architecture, prompt flow, and ten-gate rollout.
- `docs/okf-kb-migration/tickets/copilot-cli-integration-surfaces.md` — closed capability research ticket.
- `docs/okf-kb-migration/research/copilot-cli-integration-surfaces.md` — current source-backed surface comparison and recommended contract split.
- `docs/okf-kb-migration/tickets/copilot-first-provider-integration-and-state.md` — closed replacement integration and state contract.
- `docs/okf-kb-migration/tickets/dual-provider-evaluation-amendment.md` — closed prerequisite defining exact-build qualification, independent verdicts, invalidation, and evidence requirements.
- `docs/okf-kb-migration/tickets/copilot-first-rollout-and-rollback.md` — closed replacement rollout contract with independent ladders, evidence windows, scoped rollback, upgrade requalification, and hook cutover.
- `docs/okf-kb-migration/tickets/copilot-first-implementation-sequencing-and-handoff.md` — closed canonical ten-gate sequencing, ownership, validation, evidence, rollback, and implementation-handoff contract.
- `.agents/scratchpad/explore-okf-copilot-first-sequencing.md` — concise path, ownership, test-surface, and cutover facts gathered for the active ticket.
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
- On resume, `dual-provider-evaluation-amendment.md` was reverified `closed` and **Copilot-First Rollout and Rollback** was claimed by `subagent-r8k4m2`. A bounded read-only exploration found no new external research need and confirmed that the obsolete pre-model-denial rollout gate conflicts with, and must be superseded by, the accepted Copilot `advisory_stop` contract. No implementation files were changed.
- **Copilot-First Rollout and Rollback** was resolved across three accepted rounds, explicitly confirmed, closed, and indexed. `git diff --check` and ticket dependency/link validation passed with 14 closed tickets, one open ticket, three obsolete tickets, and **Copilot-First Implementation Sequencing and Handoff** as the sole frontier.
- The mandatory end-of-session `update-agent-docs` pass found no canonical agent-doc change necessary: only the existing planning subtree under `docs/okf-kb-migration/` changed, and current repository architecture and workflow guidance already covers that location.
- The mandatory end-of-session `update-agent-docs` pass found no `.agents/instructions/` or `.agents/memory/` edit necessary: this session changed only ordinary planning documents, and the existing file map and repository instructions already cover the effort and its documentation location.
- On 2026-09-09, `copilot-first-rollout-and-rollback.md` was reverified `closed` and **Copilot-First Implementation Sequencing and Handoff** was resolved across three accepted rounds, explicitly confirmed, closed, and indexed. Local exploration grounded the ten-gate path ledger in current provider-specific auto-ingest ownership and tests. Validation found 15 closed tickets, three obsolete tickets, no open claims, and no remaining fog. No implementation files were changed.
- On 2026-09-09, `implementation-overview.md` was added and linked from `map.md` to explain the already accepted design to novices. No implementation or design decision changed. All 26 local Markdown links across the overview and map resolve, Mermaid fences were checked structurally, and `git diff --check` passed; no local Mermaid renderer was available for image rendering.
- The mandatory end-of-session `update-agent-docs` pass found no `.agents/instructions/` or `.agents/memory/` edit necessary: this session added only an orientation page inside the existing long-lived planning subtree, and the current architecture and routing guidance already covers `docs/<effort>/` artifacts.
- The mandatory end-of-session `update-agent-docs` pass found no `.agents/instructions/` or `.agents/memory/` edit necessary: this session changed only the existing long-lived planning subtree, and current repository architecture already routes that material under `docs/<effort>/`.
- The handoff skill's canonical validator could not run because its undeclared `PyYAML` dependency is absent; the documented body-only fallback confirmed unchanged frontmatter and a clean exact diff. `./scripts/install.sh` could not refresh installed copies because `/root/.agents/skills` is read-only and the installer has no destination override. No dependency was installed and `HOME` was not repurposed.

## Durable Learnings

- Provider priority is a destination-level constraint. Confirm the user's durable primary host before closing provider rollout and implementation-sequencing decisions.
- Distinguish config-file Copilot hooks from in-process project-extension SDK hooks; they have different prompt identity and output capabilities.
- Do not make a provider-neutral context migration depend on a stronger prompt-admission property than the user's primary host can provide without presenting that tradeoff explicitly.
- Removing duplicated compatibility hooks is a valid simplification only when the replacement owns their enrolled-provider behavior and unsupported-host limitations are stated explicitly.
- Three rejected patch attempts occurred while recording round 4: two malformed payloads and one stale context match. None changed files. For multi-file documentation patches, verify literal delimiters and current anchor text first, then prefer smaller independent patches.
- One empty patch targeted a mistyped ticket filename while recording the evaluation amendment; it failed before changing files. Copy the verified path from the active ticket rather than retyping it in patch headers. A later search also named an absent `.github/workflows` directory; treat its absence as repository state, not as evidence of a CI implementation.
- During the sequencing ticket, two invalid JavaScript tool wrappers failed before filesystem access, one search accidentally executed backticked text through the shell, two malformed handoff patches were rejected, and one accepted-round patch briefly inserted a malformed path before immediate repair. Use the minimal `const r = await ...; text(r.output);` wrapper, never place backticks in shell command strings, reread exact patch anchors, and review newly appended planning text immediately.

## Suggested Skills

- Resume with `handoff`, then activate `exec-plans`, mandatory `tdd`, and `official-sources` for the implementation ExecPlan and gate 1.
- Use `official-sources` whenever Copilot extension or hook behavior is reassessed.
- End repository-changing sessions with `update-agent-docs`.
