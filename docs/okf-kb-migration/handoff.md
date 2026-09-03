# OKF Agent-KB Migration Handoff

## Goal

Finish the planning-only Wayfinder map in `docs/okf-kb-migration/` and produce an implementation-ready migration design plus ExecPlan-ready handoff. Implementation and proof-of-concept delivery remain out of scope.

## Status

- Primary-source OKF v0.2 research and current-system exploration are complete.
- All twelve decisions are closed. **Implementation Sequencing and Handoff** completed after three accepted Grilling rounds and explicit shared-understanding confirmation; the planning-only Wayfinder destination is reached.
- The latest verified inventory is 29 eligible canonical inputs: 26 remain whole and three hook documents split into 16 concepts, producing 42 concepts total.
- No migration implementation or implementation ExecPlan exists. `relocation-execplan.md` records only the completed move of planning artifacts into `docs/`.
- Worktree was clean at `10263738` before this handoff consolidation.

## Next Focus

Create the implementation ExecPlan from the completed Wayfinder design in a fresh session.

## Exact Next Step

Activate `exec-plans`, mandatory `tdd`, and `official-sources`; re-check the OKF v0.2 baseline; create `docs/okf-kb-migration/implementation-execplan.md`; and scope its first execution session to gate 1. Do not begin migration implementation before the ExecPlan is written.

## Settled Decisions and Constraints

- **Implementation Sequencing and Handoff round 1:** the user accepted an implementation ExecPlan spanning the complete Gemini rollout through `default`, dependency-ordered vertical acceptance gates, one owner per non-overlapping milestone/path group with independent gate review, and one atomic rollback-capable commit per accepted gate. Canonical inputs and synchronized generated evidence land together; each provider-mode promotion is a separate configuration-only commit. Copilot remains on legacy pending its separate capability gate.
- **Implementation Sequencing and Handoff round 2:** the user accepted nine gates: canonical summary readiness; profile/producer/projection; frozen evaluation contract and legacy baseline; selector/fallback core; Gemini adapter plus Copilot capability tests in legacy mode; promotion harness/CI/budget/runtime configuration; then separate Gemini shadow, canary, and default promotions. New shared code lives under `scripts/agent_kb/`, tests under `scripts/tests/agent_kb/`, the required producer CLI remains `scripts/okf-projection.py`, human-reviewed evaluation definitions live under `docs/okf-kb-migration/evaluation/`, and adapters stay in their provider-local hook trees. Documentation travels with every gate, targeted checks accumulate, and the complete exact-commit promotion suite runs before every forward mode transition.
- **Implementation Sequencing and Handoff round 3:** the user accepted explicit ownership transfers across the nine gates with no concurrent path writers; stable public commands for projection generation/checking, standard-library unit discovery, and a new `scripts/agent-kb-evaluate.py` promotion runner; gate-specific acceptance evidence and atomic rollback rules; and `docs/okf-kb-migration/implementation-execplan.md` as the future plan path. The completed ticket and this existing feature handoff will be the only sequencing handoff artifacts; the implementation ExecPlan is created only in the next session using `exec-plans`, `tdd`, and `official-sources`.
- **Implementation Sequencing and Handoff final confirmation:** the user confirmed the shared summary without changes. The ticket is closed and indexed; no implementation or implementation ExecPlan was created in this planning session.

- **Rollout and Rollback round 1:** the user accepted independent Gemini staging through shadow/canary/default; ordinary Copilot CLI remains on legacy until every documented and behavioral capability gate passes, after which it starts its own ladder at shadow. Shadow always serves legacy while comparing OKF read-only. Rollout state is committed per-provider configuration, canaries use explicit branches/worktrees, and promotion requires the complete CI gates plus one normal work cycle and at least 50 eligible prompts, restarted by candidate/configuration changes. A standalone Copilot SDK wrapper remains a separate possible effort.
- **Rollout and Rollback round 2:** the user accepted immediate rollback for any safety, integrity, parity, determinism, privacy, or disposition invariant violation; operational degradation first freezes promotion and rolls back only after exceeding a shadow-derived envelope for a full rolling 50-prompt window. Rollback is a minimal reviewed provider-mode configuration change, widened to every enrolled provider only for shared defects. Runtime never changes rollout state. Every corrected release requires root-cause documentation, regression coverage, exact-commit CI evidence, and the full rollout ladder again.
- **Rollout and Rollback round 3:** the user accepted provider-specific canary envelopes frozen from shadow evidence; privacy-safe event storage plus promotion-PR evidence; mechanically gated forward mode transitions with immediate rollback to legacy; no legacy-loader retirement in this migration; and a separate future major-contract gate before retirement can be reconsidered.
- **Copilot CLI hook research:** current documented config-file hooks cannot meet the complete safety contract. `userPromptSubmitted` uniquely sees the submitted prompt but discards command/HTTP output; `userPromptTransformed` can inject context but is mutation-only and has no current-message discriminator for batched submissions; tool and stop hooks act too late. A Copilot CLI extension improves prompt identity/injection but still cannot deny the model turn. A standalone Copilot SDK wrapper could validate before calling `session.send()`, but changes the integration boundary and requires separate dependency approval and design.

- **Source Summary Transition Policy:** replace unsupported completed-summary `status: verified` and stale-reason text with canonical selection-oriented `coverage`, keep manifest v1 as the raw-to-summary freshness binding, project only exactly bound current `active` summaries, stage repair/production/selection, and require strict cross-provider and negative-path validation. Emit no OKF `verified` field until a separately specified actor/timestamp evidence contract exists.
- Authored `.agents/instructions/` and `.agents/memory/` documents remain canonical. A generator exclusively owns a committed, deterministic `.agents/okf/` sidecar and `.projection-manifest.json`; invalid freshness evidence causes an explainable legacy-loader fallback.
- The sidecar is repo-local, uses generated lowercase `index.md` files, emits no `log.md`, excludes canonical `INDEX.md` and `LOG.md`, rejects case-fold collisions, and relies on Git for rollback.
- The profile starts at `agent-kb@1.0.0` with seven concept types; typed relationships and selector task kinds advance it through `agent-kb@1.2.0`, and the explicit mandatory-context policy advances the planned contract to `agent-kb@1.3.0`.
- A committed `.agents/okf-profile.json` explicitly maps every source path/heading to a stable logical concept path. Source moves preserve identity; semantic replacement creates new identities plus deprecated tombstones.
- Typed relationships are explicit `{kind, target}` registry entries only. Never infer them from Markdown links, hierarchy, tags, names, or prose. `requires` drives mandatory transitive loading; other accepted semantics are recorded in `tickets/concept-identity-and-links.md:92`.
- **Mandatory Context and Fallback:** require caller-supplied trivial/nontrivial scope; derive mandatory roots only from explicit scope-and-area policy and `requires`; charge mandatory closure before relevance context; use atomic legacy fallback for `no_match`, projection failures, and mandatory budget exhaustion; hard-stop on unsafe input, pending ingest, access violations, or invalid mandatory lifecycle; and log no task or concept content.
- Preserve immutable `.agents/sources/`, pending-ingest gating, orphan cleanup, provider-specific hook envelopes, offline operation, and parity between intentionally duplicated Copilot and Gemini helpers.
- **Provider Integration and State:** use a shared read-only runtime core, repository-owned thin adapters, committed versioned runtime configuration, atomic legacy fallback, JSON-only envelopes, and privacy-safe diagnostics. Gemini can enforce the planned hard stop; keep Copilot on legacy loading until tested host capabilities provide true pre-turn denial and unambiguous current-prompt identification.
- Safety and relevant-context recall outrank token reduction. OKF is a representation format, not a router, ranker, access-control system, or trust authority.
- `domain-modeling`, requested by Wayfinder for Grilling tickets, remains unavailable; use the existing research and repository evidence as the disclosed fallback.

## Current-State Corrections

- Earlier 30-input/43-concept and 27-whole counts were wrong. Current-tree enumeration verified 29 inputs, 26 whole inputs, and 42 concepts; the profile ticket and map are corrected.
- The earlier malformed-summary-frontmatter defect is no longer current: all nine summary files now begin with `---`, and the manifest reports nine `active` entries. Re-check current files rather than relying on the older research note when resolving **Source-Summary Transition Policy**.
- Keep this single feature-scoped handoff at `docs/okf-kb-migration/handoff.md`; the user explicitly rejected `.agents/scratchpad/handoff.md` for this effort.

## Relevant Artifacts

- `docs/okf-kb-migration/map.md:1` — active destination, decisions, fog, and scope.
- `docs/okf-kb-migration/tickets/concept-profile-and-taxonomy.md:16` — profile and 42-concept decomposition.
- `docs/okf-kb-migration/tickets/concept-identity-and-links.md:16` — complete identity, path, tombstone, and relationship contract.
- `docs/okf-kb-migration/tickets/source-summary-transition-policy.md:16` — complete repair, provenance, eligibility, staging, and acceptance contract.
- `docs/okf-kb-migration/tickets/selector-contract-and-ranking.md:16` — closed deterministic selector, ranking, budgeting, result, and offline-failure contract.
- `docs/okf-kb-migration/tickets/projection-producer-and-linter.md:16` — closed producer, linter, manifest, publication, and invocation contract.
- `docs/okf-kb-migration/tickets/mandatory-context-and-fallback.md:16` — closed mandatory policy, closure, budgets, disposition, fallback, and sensitive-content contract.
- `docs/okf-kb-migration/research/okf-primary-sources.md` — cited OKF v0.2 findings.
- `docs/okf-kb-migration/research/explore-okf-kb-migration.md` — loader, hook, and manifest architecture map; verify mutable facts against the current tree.
- `.agents/memory/sources/source-ingest-manifest.json` — current operational ingest state.

## Verification State

- **Completed Wayfinder validation:** `git diff --check` passed; all 12 tickets are `closed`; the map contains exactly 12 decision links; every blocker filename and map ticket link resolves; and no open or claimed ticket remains. The final `update-agent-docs` pass found no `.agents/instructions/` or `.agents/memory/` edit necessary because this session changed only the existing long-lived planning artifacts and introduced no implementation interface yet.
- Read-only sequencing inventory confirmed there is no existing OKF profile/runtime configuration, generated bundle, producer, selector/runtime core, evaluation harness, CI workflow, or repo-wide test runner. Existing integration points are `.github/hooks/hooks.json` plus its auto-ingest scripts, `.gemini/settings.json` plus its auto-ingest scripts, targeted `scripts/test-*.sh` checks, and the installers. The implementation must introduce explicit paths without crossing the installed/global hook boundary.

- **Rollout and Rollback** closure validation passed: `git diff --check`; 11 closed tickets and one open ticket; 11 map decision links exactly matching the closed set; and **Implementation Sequencing and Handoff** as the sole open ticket whose only blocker is closed.
- The Copilot research report is present in `HEAD` at externally created commit `243a8db1`; this session did not create that commit. The ticket closure, map index entry, and latest handoff updates remain uncommitted on top of it.
- The mandatory end-of-session `update-agent-docs` pass found no durable `.agents/instructions/` or `.agents/memory/` edit needed. Existing hook guidance already records Copilot's mutation-only prompt transformation and relevant failure semantics; the narrower rollout evidence remains in the linked effort research.
- **Rollout and Rollback** is closed and indexed in the map after three accepted Grilling rounds and final shared-understanding confirmation. **Implementation Sequencing and Handoff** is now the sole open, unblocked ticket; it was not claimed because Wayfinder permits resolving only one non-research ticket per session.
- `research/copilot-cli-hooks-rollout.md` records the 2026-09-03 official GitHub hooks/release assessment. No local `copilot` executable or version was available. The researcher had one initial web-result shape error, retried successfully, and lost no evidence. `git diff --check` passed after the report was written.

- **Provider Integration and State** is closed and indexed in the map; both exact blockers were verified `closed`. Read-only Copilot/Gemini exploration confirmed repo-local prompt/final hook timing, JSON-only provider envelopes, active-workspace versus installed-hook separation, and three distinct state concerns (source-ingest manifest, projection manifest, provider-local observability). No tests ran for that evidence pass.
- **Provider Integration and State** round 1 accepted a provider-neutral core with thin prompt-time adapters, conservative `nontrivial` scope and omitted task kind absent structured metadata, active-workspace-only KB discovery, and independent source-ingest/projection/observability state contracts with no prompt-time schema migration.
- **Provider Integration and State** round 2 corrected event ownership: every prompt path establishes current pending-ingest state before selection, while startup and final reconciliation remain; source manifest v1 may be updated, but selector/projection stay read-only. It also accepted a shared deterministic legacy loader, one delimited context block before untouched task content, and one normalized UTC event timestamp per invocation with an injectable test clock.
- Official hook contracts expose a promotion constraint for round 3: Gemini `BeforeAgent` can deny a turn, while Copilot `userPromptTransformed` is mutation-only and cannot block it; Copilot `agentStop`/`subagentStop` can only force continuation and are subject to a runaway guard.
- **Provider Integration and State** round 3 accepted withholding Copilot OKF promotion until true pre-turn hard-stop enforcement exists, repository-owned project adapters with no global project-KB selection, and strict JSON-only stdout plus privacy-safe diagnostics. Gemini may advance independently; provider staging remains for **Rollout and Rollback**.
- **Provider Integration and State** round 4 accepted the complete disposition/error matrix, final-response source-ingest-only recheck, short-lived reconciliation lock plus projection snapshot validation, byte-identical provider-neutral parity with provider-specific envelope snapshots, and behavioral capability gates for any future Copilot promotion.
- **Provider Integration and State** final round accepted committed `agent-kb-runtime@1.0.0` configuration, corpus-calibrated budgets, empty paths absent structured metadata, no prompt-time configuration migration, and runtime-contract evolution rules.

- **Evaluation Corpus and Promotion Gates** round 1 is accepted: use a committed provider-neutral task corpus with explicit coverage obligations; semantic `required`/`allowed`/`forbidden` oracles plus exact contract assertions; a deterministic same-revision legacy baseline; and zero-tolerance safety/compatibility gates before aggregate efficiency gates.
- **Evaluation Corpus and Promotion Gates** round 2 is accepted: freeze development/promotion partitions under an evaluation-contract version; require 100% required recall and no per-case recall regression; require no per-case irrelevant-byte increase plus 30% aggregate and 20% median reduction; require perturbation-stable byte equality; and gate cold selector latency at p95 <=100 ms and max <=250 ms on declared reference CI.
- **Evaluation Corpus and Promotion Gates** round 3 is accepted: require deterministic single-fault negative mutations, exact Copilot/Gemini adapter replay parity, complete same-commit machine-readable CI evidence, and human-reviewed versioned corpus governance.
- **Evaluation Corpus and Promotion Gates** is closed and indexed in the map. The initial `agent-kb-evaluation@1.0.0` contract defines exact metric formulas, fresh-process timing methodology, and a conjunctive fail-closed promotion verdict.
- Current planning validation passed: `git diff --check`; ten closed tickets and two open tickets; ten map links exactly matching the closed set; and **Rollout and Rollback** as the sole open ticket whose blockers are all closed.
- The mandatory end-of-session `update-agent-docs` pass found no durable `.agents/instructions/` or `.agents/memory/` update needed; existing guidance already covers long-lived effort plans under `docs/<effort>/`.

- **Concept Identity and Links** is closed and listed in the map.
- **Source Summary Transition Policy** is closed and listed in the map.
- The **Concept Identity and Links** resolution contains exactly 42 unique concept paths.
- `git diff --check`, blocker-link validation, and the 29-input/42-concept calculation passed when that ticket closed.
- All nine current source summaries have opening frontmatter delimiters; the manifest contains nine `active` entries.
- Live exploration confirmed that `status: verified` is now parseable but still has no actor/timestamp evidence; reconciliation proves only freshness, not factual verification. See `.agents/scratchpad/explore-source-summary-transition.md`.
- Live reconciliation found nine sources, nine summaries, nine `active` manifest entries, and no pending or orphan entries.
- `bash scripts/test-hooks-auto-ingest.sh` passed during the live exploration; the Gemini parity suite was not rerun.
- Handoff consolidation passed `git diff --check`; `.agents/scratchpad/handoff.md` is absent and this file is the only OKF migration handoff.
- Read-only invocation exploration found no existing CI workflow or projection command. The future explicit contributor/CI tool should align with deterministic helpers under `scripts/`; installers and provider hooks remain outside the producer boundary, and prompt-time OKF consumption stays read-only.
- **Projection Producer and Linter** round 1 is accepted: use a closed authoritative input set; one standard-library Python tool with `generate` and read-only `check` modes; strict deterministic whole/split Markdown extraction and rendering; and an independently versioned projection manifest containing the selector's complete normalized inventory plus input/output integrity evidence.
- **Projection Producer and Linter** round 2 is accepted: generate through a fully validated staging tree and publish the manifest last; lint every profile, source, freshness, OKF, graph, index, and integrity layer; use `agent-kb-producer@1.0.0` plus integer projection-manifest version 1; return stable sorted diagnostics and four exit classes; and permit generation only through explicit contributor/CI workflows, never installers or prompt-time consumers.
- **Projection Producer and Linter** round 3 is accepted: use explicit selector evaluation time for `stale_after`; hash and rehash the complete input snapshot; drive every generated index from explicit profile metadata; require manifest/concept metadata agreement; and allow only unrelated unmapped source-summary orphans as advisory warnings.
- **Projection Producer and Linter** is closed and indexed in the map. The selector contract now requires an explicit normalized RFC 3339 UTC evaluation time and never reads the system clock, resolving the stale-selection determinism conflict.
- **Mandatory Context and Fallback** closed after three accepted live Grilling rounds. Its resolution refines the unimplemented selector v1 input with required `task-scope`, advances the profile to `agent-kb@1.3.0`, and defines deterministic closure order, lifecycle substitution, shared-budget behavior, dispositions, fallback/hard-stop conditions, and sensitive-content boundaries.
- Current planning validation passed: `git diff --check`; eight closed tickets, four open tickets, and no claimed tickets; eight map links exactly matching the closed set; and two frontier tickets, **Evaluation Corpus and Promotion Gates** and **Provider Integration and State**.
- The exact blockers for **Selector Contract and Ranking** were closed, and the ticket is now closed and indexed in the map.
- **Selector Contract and Ranking** round 1 is accepted: inputs are task text plus optional normalized repository paths and task kind; the projection manifest is the candidate inventory; the profile adds optional task kinds but no priority/mandatory flags; ranking is lexicographic; deprecated/stale concepts are filtered; and selection uses caller-supplied byte and concept-count budgets with whole documents only.
- **Selector Contract and Ranking** round 2 is accepted: use seven caller-supplied task kinds; strict repository-relative path normalization with exact/glob specificity and committed area mapping; deterministic metadata-only lexical matching; eligibility requires a non-task-kind relevance signal; ranking uses an integer tuple with stable path tie-break; `depends-on` expands one budgeted hop; and greedy whole-concept packing returns an explicit empty `no_match` result rather than guessing.
- **Selector Contract and Ranking** round 3 is accepted: adopt independently versioned `agent-kb-selector@1.0.0` and profile `agent-kb@1.2.0`; use the agreed exact integer tuple; return provider-neutral rendered context plus a complete candidate audit and closed reason codes; use no cache in v1; and require standard-library-only, read-only, offline, atomic failure with no partial context from an invalid projection.
- No product build ran because this session changed planning documentation only; the targeted Copilot auto-ingest test above remains the applicable current-system evidence.
- The latest mandatory agent-doc pass found no durable `.agents/instructions/` or `.agents/memory/` update needed; ordinary project-doc changes do not require an agent-doc update, and existing guidance already routes long-lived planning artifacts under `docs/<effort>/`.

## Durable Learnings

- The refreshed `update-agent-docs` skill runs once after all tasks and subagents in a work session, not repeatedly between related tasks.
- Recompute mutable inventories and ticket frontiers from the current tree when resuming; historical handoffs and research can drift.
- Resolve shared-skill aliases under `/root/.agents/skills/` and repo-local maintenance skills under `.agents/skills/`.
- Derive counts programmatically. Manual aggregation previously caused the corrected off-by-one baseline.
- Keep a single handoff and update it in place whenever status, blockers, or the next step changes.
- `apply_patch` cannot delete and re-add the same path in one patch; a rejected consolidation attempt changed nothing, and the successful retry used separate delete and add operations.
- Handoff patches using assumed or stale surrounding context have failed atomically without changing files; re-read the exact block and apply narrow hunks anchored to current text.
- Scope duplicate-handoff checks to this effort; `.agents/scratchpad/codex-cli-support/handoff.md` belongs to an unrelated feature.
- Do not treat a changed non-scaffold summary hash as semantic verification; that transition is only the manifest's operational freshness rule.
- Large multi-file resolution patches are fragile: one malformed patch and one stale-context patch were rejected atomically without changing their targets; re-read current text and apply narrow per-file hunks.
- Do not draft `apply_patch` hunks with placeholder or nonstandard headers; one malformed combined resolution patch was rejected before changing files. Use only standard `@@` hunks and split large documentation updates by file.
- Re-check the live GitHub Copilot hooks reference before provider promotion: the contract is evolving, and current config-file `userPromptSubmitted` output is explicitly discarded even though SDK programmatic hooks honor it.

## Suggested Skills

- Resume with `handoff`, then `wayfinder` and `grilling`.
- Before implementation, use `exec-plans`, mandatory `tdd`, and `official-sources` to re-check the OKF baseline.
- End repository-changing sessions with repo-local `update-agent-docs`.
