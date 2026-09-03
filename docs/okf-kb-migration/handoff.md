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
- The Wayfinder map is charted at `docs/okf-kb-migration/map.md` with three closed decisions and nine dependency-wired open design tickets.
- **Bundle Publication and Lifecycle** is closed after three live Grilling rounds. The accepted contract uses a committed deterministic `.agents/okf/` bundle, repo-local distribution, manifest-backed freshness with legacy fallback, generator-only full rebuilds, generated indexes without an initial `log.md`, case-fold collision rejection, explicit regeneration, one stable current bundle, and Git rollback.
- **Concept Profile and Taxonomy** is closed after its live Grilling exchange.
- The user accepted profile identity `agent-kb@1.0.0`, a single `x-agent-kb` extension mapping, and 30 in-scope canonical inputs that exclude `INDEX.md` and `LOG.md` while retaining `FILE_MAP.md`. The output cardinality is not fixed: one input may emit multiple independently retrievable concepts.
- The user rejected prematurely freezing the six seed types and accepted a semantic decomposition audit before the profile `1.0.0` registry is closed. Split only when concepts can be selected, maintained, or deprecated independently; length or multiple headings alone is insufficient.
- The delegated audit recommends keeping 27 inputs whole and decomposing only `.agents/instructions/hooks.md`, `.agents/memory/adrs/hooks.md`, and `.agents/memory/known-issues/hooks.md`. The splits expose a new `Hook Contract` role while reusing the seed roles for instructions, testing, known issues, and ADRs.
- The user accepted that decomposition boundary: four concepts from `instructions/hooks.md`, eight concepts from `adrs/hooks.md`, four concepts from `known-issues/hooks.md`, and one concept from each other input, for 43 projected concepts total.
- The user accepted the profile `1.0.0` type registry: `Agent Instruction`, `Repository Knowledge`, `Testing Guidance`, `Known Issue`, `Architecture Decision`, `Source Summary`, and `Hook Contract`. Later type additions require a profile minor-version bump.
- Every concept must have non-empty `type`, `title`, and selection-oriented `description`, plus normalized `x-agent-kb.source.path`; split concepts also require a stable `x-agent-kb.source.anchor`. Standard `tags`, `resource`, and `sources` remain conditional recommendations.
- The user accepted deterministic routing metadata: whole-file `coverage` seeds `description`, split descriptions come from explicit profile mappings, and `x-agent-kb.areas` plus optional `paths` come from a versioned mapping rather than heuristic prose parsing. Task kinds, priority, and mandatory-load policy remain for later tickets.
- The user accepted conservative provenance/lifecycle rules: source summaries require raw-source references; projection time does not become `generated`; `verified`, `deprecated`, and `stale_after` require explicit canonical evidence; malformed summary status and operational ingest states never become OKF trust claims.
- The user accepted the strict writer allowlist: required `type`, `title`, `description`, and `x-agent-kb`; conditional `tags`, `resource`, `sources`, `status`, `stale_after`, `generated`, and `verified`; and only `source`, `areas`, and `paths` inside the extension. Writers reject unknown fields while readers tolerate them.
- The user accepted deterministic reserved-file behavior: generate sorted lowercase `index.md` files, put only `okf_version: "0.2"` frontmatter on the root index, emit no `log.md`, never project canonical `INDEX.md` or `LOG.md`, and reject case-folded collisions.
- The user accepted contract-based profile SemVer: patch for compatible corrections, minor for additive optional fields/types/area values, and major for removals, renames, new requirements, meaning changes, or other incompatibilities. OKF versioning remains independent.
- No migration implementation code or implementation ExecPlan was created; `relocation-execplan.md` records only this documentation move.
- The prior relocation and lifecycle work is committed. This session began from a clean worktree at `e1477924`; the profile ticket claim and this handoff update are the current expected changes.

## Next Focus

Work through the charted Wayfinder map one decision ticket per session.

## Exact Next Step

In a new session, claim and resolve exactly one newly unblocked frontier ticket. Prefer **Concept Identity and Links** in map order unless the user explicitly selects **Source-Summary Transition Policy**.

## Established Facts and Constraints

- The Wayfinder destination is an implementation-ready design covering the OKF profile/taxonomy, bundle topology, producer/consumer architecture, routing policy, compatibility and rollout strategy, evaluation thresholds, rollback, and ExecPlan-ready handoff; implementation and proof-of-concept delivery are out of scope.
- The requested `knowledge-catalog/okf` subtree is frozen. The canonical source is `GoogleCloudPlatform/open-knowledge-format`; assessed version is OKF v0.2. See `research/okf-primary-sources.md:7-27`.
- OKF is a representation/interchange and progressive-navigation format, not a task router, relevance ranker, retrieval runtime, or access-control system. Efficient context gathering therefore requires both an OKF profile and a repository-owned consumer/router. See `research/okf-primary-sources.md:29-40` and `:61-77`.
- Normative minimum: every non-reserved Markdown concept needs parseable YAML frontmatter and non-empty `type`; `index.md` and `log.md` are lowercase reserved files; paths are concept IDs; unknown types/keys, broken links, and missing optional metadata must be tolerated. See `research/okf-primary-sources.md:79-110` and `:153-165`.
- Provenance/trust/lifecycle fields are optional: `sources`, `generated`, `verified`, `status`, and `stale_after`. Do not manufacture verification or treat trust tiers as security. See `research/okf-primary-sources.md:112-121` and `:280-287`.
- The reference tooling and samples are illustrative, not normative. GA4 shows dense enrichment, Stack Overflow cross-cutting references, Bitcoin explicit join concepts, and Acme Retail trust/lifecycle/attestation. See `research/okf-primary-sources.md:168-203`.
- Prior research measured 31 Markdown documents totaling 106,004 bytes; the current read-only inventory finds 32 after subsequent repository changes. Hooks enforce pending source ingestion but do not select task-relevant KB concepts; agents currently route manually from `.agents/memory/INDEX.md`. See `research/explore-okf-kb-migration.md:16-40`.
- In-place conversion risks case collisions between current `INDEX.md`/`LOG.md` and OKF's reserved `index.md`/`log.md`, especially on case-insensitive filesystems. See `research/explore-okf-kb-migration.md:50-58`.
- The user approved an additive generated sidecar, a portable OKF core with documented namespaced extensions and strict writer validation, both progressive navigation and deterministic selection, a compatibility-preserving rollout, and safety-first evaluation. The sidecar publication lifecycle is settled; exact profile, selector, and rollout details remain open tickets. See `tickets/migration-charter.md` and `tickets/bundle-publication-and-lifecycle.md`.
- Neither installer copies repository `.agents/` content. Source-ingest hooks resolve the active workspace, while required-skill loaders use global `~/.agents/skills`; the accepted sidecar therefore remains repo-local and is not copied into global storage.
- The current canonical KB contains 32 Markdown files: six area instructions, seven root memory docs, one ADR, five known-issue docs, four testing docs, and nine source summaries. The 23 non-summary files use only valid free-form `coverage`; the nine summaries still have malformed `status: verified` pseudo-frontmatter. See `.agents/memory/known-issues/hooks.md:9-13`.
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
- The map contains exactly two open unblocked tickets, **Concept Identity and Links** and **Source-Summary Transition Policy**, and every `Blocked By` filename resolves to an existing ticket.
- A read-only inventory confirmed the six plausible subject concept classes are agent instructions, repository knowledge, testing guidance, known issues, architectural decisions, and source summaries. `INDEX.md`/`FILE_MAP.md` are navigation candidates; `LOG.md` and the JSON ingest manifest are operational artifacts.
- The semantic audit found no split justification for source summaries or general instruction/testing files. It found independently selectable concerns in `instructions/hooks.md`, independently supersedable ADRs in `adrs/hooks.md`, and independently triggered issue domains in `known-issues/hooks.md`.
- `git diff --check` and targeted trailing-whitespace checks passed after closing **Bundle Publication and Lifecycle** and updating the map.
- `git diff --check`, targeted trailing-whitespace checks, blocker-link validation, ticket counts, and frontier derivation passed after closing **Concept Profile and Taxonomy**.
- The effort now contains seventeen Markdown documents under `docs/okf-kb-migration/` including the relocation ExecPlan; Git visibility and link checks are recorded in that plan.
- Nine committed verified summary files were measured as missing their opening `---`; the defect is documented but not repaired.
- No product tests/builds were run because no code or configuration was changed.
- The mandatory agent-doc pass found no durable `.agents/instructions/` or `.agents/memory/` update: only version-controlled migration-planning documents changed.
- Current tracked changes close the profile ticket and synchronize the map and handoff on `main...origin/main`.

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
- A later multi-hunk handoff patch also failed on one inexact context sentence; no files changed, and the retry used freshly matched exact lines.
- One decomposition worker's bulk read was truncated; it corrected this by rereading long files individually with numbered lines before reporting.

## Suggested Skills for Resume

- First: `handoff` (this file), then `wayfinder` and `grilling`.
- Before implementation: `exec-plans` and mandatory `tdd`; use `official-sources` to re-check the canonical OKF commit/version.
- End every work session with repo-local `update-agent-docs`.

## Briefing

The migration charter, sidecar publication lifecycle, and `agent-kb@1.0.0` concept profile are settled. The current frontier contains **Concept Identity and Links** and **Source-Summary Transition Policy**. In a new session, claim exactly one—prefer **Concept Identity and Links** in map order—and do not implement while working the map.
