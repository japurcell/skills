# OKF Agent-KB Migration Handoff

## Goal

Research Open Knowledge Format (OKF), understand this repository's `.agents/{instructions,memory}` and source-ingestion system, then use Wayfinder to decide an implementation-ready migration that improves task-specific context selection.

## Status

- Primary-source research and current-system exploration are complete.
- `wayfinder`, `grilling`, `research`, `official-sources`, `explore`, delegation/model-routing, `update-agent-docs`, `improve-skill`, and `commit` instructions were loaded in the prior session.
- The resume session reloaded `handoff`, `wayfinder`, and `grilling`; `domain-modeling` remains unavailable, so repository research is the disclosed fallback.
- The user selected destination **A**: an implementation-ready migration design and ExecPlan-ready handoff. Design-plus-implementation and a narrow proof of concept are outside this Wayfinder effort.
- The user accepted all six breadth-first charter recommendations: migration boundary, source of truth, consumer behavior, OKF conformance, compatibility posture, and success hierarchy.
- The complete effort has moved from ignored scratchpad storage into the version-controlled `docs/okf-kb-migration/` tree.
- The Wayfinder map is charted at `docs/okf-kb-migration/map.md` with two closed decisions and ten dependency-wired open design tickets.
- **Bundle Publication and Lifecycle** is closed after three live Grilling rounds. The accepted contract uses a committed deterministic `.agents/okf/` bundle, repo-local distribution, manifest-backed freshness with legacy fallback, generator-only full rebuilds, generated indexes without an initial `log.md`, case-fold collision rejection, explicit regeneration, one stable current bundle, and Git rollback.
- **Concept Profile and Taxonomy** is now the sole open, unblocked frontier ticket.
- No migration implementation code or implementation ExecPlan was created; `relocation-execplan.md` records only this documentation move.
- The relocation created expected uncommitted changes: `docs/okf-kb-migration/` is visible to Git, and `.agents/{instructions/repo.md,memory/ARCHITECTURE.md,memory/FILE_MAP.md}` record the durable documentation layout. HEAD remains `a9328fd2`.

## Next Focus

Work through the charted Wayfinder map one decision ticket per session.

## Exact Next Step

Invoke Wayfinder with `docs/okf-kb-migration/map.md`, claim `concept-profile-and-taxonomy.md`, then resolve only **Concept Profile and Taxonomy** through the required live Grilling exchange.

## Established Facts and Constraints

- The Wayfinder destination is an implementation-ready design covering the OKF profile/taxonomy, bundle topology, producer/consumer architecture, routing policy, compatibility and rollout strategy, evaluation thresholds, rollback, and ExecPlan-ready handoff; implementation and proof-of-concept delivery are out of scope.
- The requested `knowledge-catalog/okf` subtree is frozen. The canonical source is `GoogleCloudPlatform/open-knowledge-format`; assessed version is OKF v0.2. See `research/okf-primary-sources.md:7-27`.
- OKF is a representation/interchange and progressive-navigation format, not a task router, relevance ranker, retrieval runtime, or access-control system. Efficient context gathering therefore requires both an OKF profile and a repository-owned consumer/router. See `research/okf-primary-sources.md:29-40` and `:61-77`.
- Normative minimum: every non-reserved Markdown concept needs parseable YAML frontmatter and non-empty `type`; `index.md` and `log.md` are lowercase reserved files; paths are concept IDs; unknown types/keys, broken links, and missing optional metadata must be tolerated. See `research/okf-primary-sources.md:79-110` and `:153-165`.
- Provenance/trust/lifecycle fields are optional: `sources`, `generated`, `verified`, `status`, and `stale_after`. Do not manufacture verification or treat trust tiers as security. See `research/okf-primary-sources.md:112-121` and `:280-287`.
- The reference tooling and samples are illustrative, not normative. GA4 shows dense enrichment, Stack Overflow cross-cutting references, Bitcoin explicit join concepts, and Acme Retail trust/lifecycle/attestation. See `research/okf-primary-sources.md:168-203`.
- The current compiled KB has 31 Markdown documents totaling 106,004 bytes. Hooks enforce pending source ingestion but do not select task-relevant KB concepts; agents currently route manually from `.agents/memory/INDEX.md`. See `research/explore-okf-kb-migration.md:16-40`.
- In-place conversion risks case collisions between current `INDEX.md`/`LOG.md` and OKF's reserved `index.md`/`log.md`, especially on case-insensitive filesystems. See `research/explore-okf-kb-migration.md:50-58`.
- The user approved an additive generated sidecar, a portable OKF core with documented namespaced extensions and strict writer validation, both progressive navigation and deterministic selection, a compatibility-preserving rollout, and safety-first evaluation. The sidecar publication lifecycle is settled; exact profile, selector, and rollout details remain open tickets. See `tickets/migration-charter.md` and `tickets/bundle-publication-and-lifecycle.md`.
- Neither installer copies repository `.agents/` content. Source-ingest hooks resolve the active workspace, while required-skill loaders use global `~/.agents/skills`; the accepted sidecar therefore remains repo-local and is not copied into global storage.
- Preserve immutable `.agents/sources/`, pending-ingest gating, orphan cleanup, and provider-specific hook envelopes. Copilot and Gemini helper implementations are intentionally duplicated and must remain behaviorally synchronized.
- Follow `AGENTS.md`: load `.agents/memory/INDEX.md` first, use an ExecPlan before multi-file/layer code changes, and run `update-agent-docs` at the end.
- Wayfinder asks for `domain-modeling`, but that skill was not available. Prior session used Grilling plus codebase exploration as a disclosed fallback; reassess availability on resume.

## Current Architecture Anchors

- Copilot source state: `.github/hooks/scripts/helpers/auto_ingest.py:63` (summary naming), `:352` (reconciliation), `:537` (lock), `:596` (context rendering).
- Gemini equivalent: `.gemini/hooks/scripts/helpers/source_ingest.py:30`, `:372`, `:557`, `:616`.
- Copilot event adapter: `.github/hooks/scripts/auto-ingest-source.py:37-81`; prompt/final gate: `.github/hooks/scripts/inject-auto-ingest-context.py:73-104`.
- Gemini startup adapter: `.gemini/hooks/scripts/auto-ingest.py:45-118`; prompt/final gate: `.gemini/hooks/scripts/inject-auto-ingest-context.py:54-99`.
- Recorded source-summary defect: `.agents/memory/known-issues/hooks.md:9-13`.

## Relevant Artifacts

- `docs/okf-kb-migration/map.md` — active Wayfinder map and destination.
- `docs/okf-kb-migration/tickets/` — two closed decisions plus ten open decision tickets; blocker filenames were validated.
- `docs/okf-kb-migration/research/okf-primary-sources.md` — detailed, cited OKF v0.2 research, samples, migration mapping, rollout proposal, and unresolved format risks.
- `docs/okf-kb-migration/research/explore-okf-kb-migration.md` — current KB/hook code map, migration seams, likely edit targets, and validation targets.
- `docs/okf-kb-migration/relocation-execplan.md` — completed relocation plan and verification record.
- Canonical spec: `https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md`.
- Frozen-copy notice: `https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/README.md`.

## Verification State

- Canonical repo inspected at commit `ad30107c31c06aec8a7d5636e0d1058118604e6f`; requested frozen snapshot inspected at `fbbc7975388288244dfc62aea0066600b25b7c47`.
- Research covers the complete spec, reference implementation shape, tests, and all four meaningful first-party bundles.
- Relocated Markdown was checked for trailing whitespace; `git diff --check` passed.
- The map contains exactly one open unblocked ticket, **Concept Profile and Taxonomy**, and every `Blocked By` filename resolves to an existing ticket.
- `git diff --check` and targeted trailing-whitespace checks passed after closing **Bundle Publication and Lifecycle** and updating the map.
- The effort now contains seventeen Markdown documents under `docs/okf-kb-migration/` including the relocation ExecPlan; Git visibility and link checks are recorded in that plan.
- Nine committed verified summary files were measured as missing their opening `---`; the defect is documented but not repaired.
- No product tests/builds were run because no code or configuration was changed.
- Current `git status --short --branch`: modified `.agents/instructions/repo.md`, `.agents/memory/{ARCHITECTURE.md,FILE_MAP.md}`, and untracked `docs/okf-kb-migration/` on `main...origin/main`.

## Errors, Corrections, and Durable Learnings

- Initial skill reads used the repository path for shared `r0` skills and failed. Resolve catalog aliases exactly: shared skills used here live under `/root/.agents/skills/`; repo-local maintenance skills live under `/Users/adam/dev/skills/.agents/skills/`.
- The initial shallow file inventory preceded loading `explore`; on resume, load all triggered skills before task actions.
- `gh` is unavailable in this environment. Use the web tool, public URLs, or a temporary `git clone`; check optional CLI availability first.
- The research draft initially cited the frozen subtree for normative claims after discovering the canonical repo. It was corrected: normative citations now point to `open-knowledge-format`; the old repo is cited only for relocation evidence.
- Derive file and ticket totals programmatically with `rg --files` and status searches; manual aggregation twice produced an off-by-one count that was corrected before completion.
- Git author configuration appeared unset when the prior session attempted the mandated doc commit, so it stopped safely. An external/user commit subsequently landed as `a9328fd2`; the human will have to run git commits.
- Current verified source summaries are not valid YAML-frontmatter documents because they omit the opening delimiter even though the ingest state machine treats them as resolved. Do not build routing on their current metadata until this is repaired and tested.
- Scratchpad artifacts are ignored by Git and will not appear in normal `git status`; inspect them directly.
- The user explicitly chose this version-controlled, feature-scoped handoff over an ignored `.agents/scratchpad/handoff.md`; keep a single handoff here for this long-lived effort.
- A consolidation patch initially failed because it matched an outdated sentence variant. No files changed in that attempt; subsequent edits were narrowed against exact current text.

## Suggested Skills for Resume

- First: `handoff` (this file), then `wayfinder` and `grilling`.
- Before implementation: `exec-plans` and mandatory `tdd`; use `official-sources` to re-check the canonical OKF commit/version.
- End every work session with repo-local `update-agent-docs`.

## Briefing

The migration charter and sidecar publication lifecycle are settled. OKF alone will not improve retrieval, so the remaining route separately decides the profile, concept identity, producer, selector, mandatory fallback, provider integration, evaluation, rollout, and implementation sequencing. Start with **Concept Profile and Taxonomy**; do not implement while working the map.
