# OKF Agent-KB Migration Handoff

## Goal

Finish the planning-only Wayfinder map in `docs/okf-kb-migration/` and produce an implementation-ready migration design plus ExecPlan-ready handoff. Implementation and proof-of-concept delivery remain out of scope.

## Status

- Primary-source OKF v0.2 research and current-system exploration are complete.
- Five decisions are closed: **Migration Charter**, **Bundle Publication and Lifecycle**, **Concept Profile and Taxonomy**, **Concept Identity and Links**, and **Source Summary Transition Policy**.
- Seven tickets remain open. The current frontier is **Projection Producer and Linter** and **Selector Contract and Ranking**.
- The latest verified inventory is 29 eligible canonical inputs: 26 remain whole and three hook documents split into 16 concepts, producing 42 concepts total.
- No migration implementation or implementation ExecPlan exists. `relocation-execplan.md` records only the completed move of planning artifacts into `docs/`.
- Worktree was clean at `10263738` before this handoff consolidation.

## Next Focus

Resolve one Wayfinder decision ticket per session. Prefer **Selector Contract and Ranking** next.

## Exact Next Step

Read `map.md`, verify the blockers for `tickets/selector-contract-and-ranking.md` are closed, claim it, and run its live Grilling rounds. Do not implement the migration.

## Settled Decisions and Constraints

- **Source Summary Transition Policy:** replace unsupported completed-summary `status: verified` and stale-reason text with canonical selection-oriented `coverage`, keep manifest v1 as the raw-to-summary freshness binding, project only exactly bound current `active` summaries, stage repair/production/selection, and require strict cross-provider and negative-path validation. Emit no OKF `verified` field until a separately specified actor/timestamp evidence contract exists.
- Authored `.agents/instructions/` and `.agents/memory/` documents remain canonical. A generator exclusively owns a committed, deterministic `.agents/okf/` sidecar and `.projection-manifest.json`; invalid freshness evidence causes an explainable legacy-loader fallback.
- The sidecar is repo-local, uses generated lowercase `index.md` files, emits no `log.md`, excludes canonical `INDEX.md` and `LOG.md`, rejects case-fold collisions, and relies on Git for rollback.
- The profile starts at `agent-kb@1.0.0` with seven concept types. **Concept Identity and Links** adds optional typed relationships, advancing the planned contract to `agent-kb@1.1.0`.
- A committed `.agents/okf-profile.json` explicitly maps every source path/heading to a stable logical concept path. Source moves preserve identity; semantic replacement creates new identities plus deprecated tombstones.
- Typed relationships are explicit `{kind, target}` registry entries only. Never infer them from Markdown links, hierarchy, tags, names, or prose. `requires` drives mandatory transitive loading; other accepted semantics are recorded in `tickets/concept-identity-and-links.md:92`.
- Preserve immutable `.agents/sources/`, pending-ingest gating, orphan cleanup, provider-specific hook envelopes, offline operation, and parity between intentionally duplicated Copilot and Gemini helpers.
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
- `docs/okf-kb-migration/tickets/selector-contract-and-ranking.md:1` — preferred next ticket.
- `docs/okf-kb-migration/research/okf-primary-sources.md` — cited OKF v0.2 findings.
- `docs/okf-kb-migration/research/explore-okf-kb-migration.md` — loader, hook, and manifest architecture map; verify mutable facts against the current tree.
- `.agents/memory/sources/source-ingest-manifest.json` — current operational ingest state.

## Verification State

- **Concept Identity and Links** is closed and listed in the map.
- **Source Summary Transition Policy** is closed and listed in the map.
- The **Concept Identity and Links** resolution contains exactly 42 unique concept paths.
- `git diff --check`, blocker-link validation, and the 29-input/42-concept calculation passed when that ticket closed.
- All nine current source summaries have opening frontmatter delimiters; the manifest contains nine `active` entries.
- Live exploration confirmed that `status: verified` is now parseable but still has no actor/timestamp evidence; reconciliation proves only freshness, not factual verification. See `.agents/scratchpad/explore-source-summary-transition.md`.
- Live reconciliation found nine sources, nine summaries, nine `active` manifest entries, and no pending or orphan entries.
- `bash scripts/test-hooks-auto-ingest.sh` passed during the live exploration; the Gemini parity suite was not rerun.
- Handoff consolidation passed `git diff --check`; `.agents/scratchpad/handoff.md` is absent and this file is the only OKF migration handoff.
- Ticket closure validation passed: five closed tickets, seven open tickets, all blocker filenames resolve, the map has one Source Summary Transition Policy entry, and `git diff --check` is clean.
- No product build ran because this session changed planning documentation only; the targeted Copilot auto-ingest test above supplied current-system evidence.
- The final mandatory agent-doc pass found no durable `.agents/instructions/` or `.agents/memory/` update needed; this session changed planning state and a transient exploration note only.

## Durable Learnings

- The refreshed `update-agent-docs` skill runs once after all tasks and subagents in a work session, not repeatedly between related tasks.
- Recompute mutable inventories and ticket frontiers from the current tree when resuming; historical handoffs and research can drift.
- Resolve shared-skill aliases under `/root/.agents/skills/` and repo-local maintenance skills under `.agents/skills/`.
- Derive counts programmatically. Manual aggregation previously caused the corrected off-by-one baseline.
- Keep a single handoff and update it in place whenever status, blockers, or the next step changes.
- `apply_patch` cannot delete and re-add the same path in one patch; a rejected consolidation attempt changed nothing, and the successful retry used separate delete and add operations.
- A handoff patch using stale surrounding context failed without changing files; re-reading the exact block and applying narrower hunks succeeded.
- Scope duplicate-handoff checks to this effort; `.agents/scratchpad/codex-cli-support/handoff.md` belongs to an unrelated feature.
- Do not treat a changed non-scaffold summary hash as semantic verification; that transition is only the manifest's operational freshness rule.

## Suggested Skills

- Resume with `handoff`, then `wayfinder` and `grilling`.
- Before implementation, use `exec-plans`, mandatory `tdd`, and `official-sources` to re-check the OKF baseline.
- End repository-changing sessions with repo-local `update-agent-docs`.
