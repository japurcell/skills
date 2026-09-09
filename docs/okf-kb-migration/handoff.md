# OKF Agent-KB Migration Handoff

## Goal

Finish an implementation-ready design for migrating the canonical documents under `.agents/instructions/` and `.agents/memory/` in place to OKF v0.2. Preserve the existing `AGENTS.md` → `.agents/memory/INDEX.md` loading path, teach OKF authoring through a repository skill, and enforce conformance through blocking GitHub Copilot CLI and Gemini CLI lint hooks.

## Status

- The user found a charter-level flaw in the closed map: its `.agents/okf/` sidecar and prompt-time selector would inject knowledge already discoverable through the mandatory `AGENTS.md` → `.agents/memory/INDEX.md` path.
- **In-Place OKF Migration Charter** records the corrected source-of-truth and enforcement model and is closed.
- All 18 tickets derived from the old sidecar/selector/provider-runtime design are `obsolete`. Their research may be reused as evidence, but their decisions are not authoritative.
- **In-Place OKF Document Contract** is closed after three accepted grilling rounds and explicit shared-understanding confirmation. Its resolution defines the two-bundle, standard-metadata, stable-path, link, source-summary, lifecycle, and no-extension contract.
- Three replacement tickets remain open. **OKF Authoring Skill Contract** and **OKF Linter and Provider Hooks Contract** are both frontier tickets; **In-Place Migration Sequencing and Verification** remains blocked by both.
- The 18 obsolete tickets are archived under `tickets/obsolete/`; the direct `tickets/` directory contains exactly five non-obsolete tickets (two closed and three open).
- `map.md` and `implementation-overview.md` now describe the corrected architecture. No implementation or implementation ExecPlan exists.

## Next Focus

Resolve one newly unblocked frontier ticket. Prefer **OKF Authoring Skill Contract** next because it is first in map order; **OKF Linter and Provider Hooks Contract** is independently eligible.

## Exact Next Step

Activate `handoff`, `wayfinder`, `grilling`, and `writing-for-agents`; claim `tickets/okf-authoring-skill-contract.md`; inspect the current `update-agent-docs` responsibility and repository skill conventions; then grill trigger scope, authoring workflow, progressive references, coordination with `update-agent-docs`, and completion checks. Do not start implementation or claim the linter ticket in the same session.

## Decisions and Constraints

- Canonical `.agents/instructions/` and `.agents/memory/` documents become OKF documents in place; there is no generated knowledge sidecar.
- `AGENTS.md` and `.agents/memory/INDEX.md` remain the knowledge entry and routing path.
- No prompt-time selector, context injection, provider runtime, fallback path, qualification state, or promotion ladder belongs to this migration.
- A repository skill teaches OKF authoring. A linter validates authored documents and blocks failures through both providers' validation hooks.
- Lint hooks do not replace or duplicate current source-ingest freshness behavior. Immutable `.agents/sources/` remains out of bounds.
- Planning only: close the four replacement decisions before creating an implementation ExecPlan.
- Use two physical OKF bundles rooted at `.agents/memory/` and `.agents/instructions/`; do not define `.agents/` as a bundle with exclusions.
- Every canonical concept requires the standard `type` and `description` fields. Translate the current `coverage` values into `description`; do not preserve `coverage` as a required extension.
- Enforce the path-derived type vocabulary `Agent Instruction`, `Agent Memory`, `Knowledge Index`, `Source Ingestion Log`, `Known Issue`, `Testing Guidance`, `Architecture Decision`, and `Source Summary`.
- Preserve uppercase `.agents/memory/INDEX.md` and `.agents/memory/LOG.md` as ordinary `Knowledge Index` and `Source Ingestion Log` concepts. Create no lowercase siblings, and pin the target OKF version in migration tooling rather than reserved-file frontmatter.
- Use file-relative local links. They may cross the two bundle roots or point to other repository files, but must stay within the repository and resolve; external URLs remain allowed.
- Give every completed source summary one `sources` entry pointing to its matching immutable raw source, omit unsupported `verified` metadata and lifecycle `status`, and use `status: draft` for unresolved scaffolds until integration removes it. Per-claim source footnotes remain optional.
- Do not synthesize provenance, trust, or freshness metadata during migration. When used, `generated` requires `by` and `at`; `verified` uses a list of `{ by, at }` events; timestamps require explicit UTC offsets; stable status is omitted; and draft/deprecated/stale states require genuine semantics.
- Forbid exact lowercase `index.md` and `log.md` throughout both initial bundles. The profile defines no required repository extension fields, tolerates unknown fields as OKF requires, and pins OKF v0.2 in authoring/lint tooling rather than document metadata.

## Relevant Files

- `docs/okf-kb-migration/map.md` — corrected destination, authoritative decision index, and dependency graph.
- `docs/okf-kb-migration/tickets/in-place-okf-migration-charter.md` — closed source-of-truth and enforcement charter.
- `docs/okf-kb-migration/tickets/in-place-okf-document-contract.md` — closed in-place bundle and concept contract.
- `docs/okf-kb-migration/tickets/okf-authoring-skill-contract.md` — frontier authoring-skill design and recommended next ticket.
- `docs/okf-kb-migration/tickets/okf-linter-and-provider-hooks-contract.md` — independently eligible linter and hook-design frontier.
- `docs/okf-kb-migration/tickets/in-place-migration-sequencing-and-verification.md` — final blocked sequencing decision.
- `docs/okf-kb-migration/implementation-overview.md` — concise corrected architecture for novice readers.
- `.agents/scratchpad/explore-okf-in-place-correction.md` — local evidence tracing the duplicate-context flaw.
- `docs/okf-kb-migration/research/okf-primary-sources.md` — prior OKF v0.2 research; its sidecar recommendation is obsolete, but specification facts remain reusable after verification.

## Verification State

- Ticket validation now shows two closed authoritative tickets, 18 obsolete tickets in `tickets/obsolete/`, five non-obsolete tickets directly under `tickets/` (two closed and three open replacements), no active claims, and two frontier tickets: **OKF Authoring Skill Contract** and **OKF Linter and Provider Hooks Contract**. **In-Place Migration Sequencing and Verification** remains blocked by both.
- All relative Markdown links in `map.md`, `implementation-overview.md`, and `handoff.md` resolve. Active-document searches found old runtime terms only where the rejected design is explicitly identified as obsolete.
- A delegated repository-wide stale-document audit found no other active references presenting the rejected design as current and no migration-relevant broken links. It identified `relocation-execplan.md` as the sole stale artifact; that completed plan now labels its counts as a 2026-09-03 relocation snapshot and routes current status to `map.md` and this handoff.
- `git diff --check` passed.
- No code, hook, skill, canonical KB document, or configuration was implemented or changed.
- Rechecked canonical OKF v0.2 at `GoogleCloudPlatform/open-knowledge-format` main commit `ad30107c31c06aec8a7d5636e0d1058118604e6f`; the local research remains version-current. The upstream `SPEC.md` SHA-256 is `26aa5da029278939f914e578107242d9607d4f2dc5fe153272b82f9ed1030101`.
- Corpus inventory: 31 canonical Markdown documents (6 instructions, 16 non-summary memory documents, 9 source summaries). Exact lowercase `index.md`/`log.md` do not exist; uppercase `INDEX.md` and `LOG.md` are current ordinary concept candidates and exact loading/history paths.
- Corrected `research/okf-primary-sources.md` so it no longer overstates `generated.at` as explicitly required by OKF minimum conformance. The spec explicitly requires `generated.by` and specifies `generated.at`; requiring both is a repository-profile decision.
- The confirmed document contract is recorded in `tickets/in-place-okf-document-contract.md`; its new map link resolves, and the ticket has no remaining claim.
- The current end-of-session `update-agent-docs` pass synchronized the durable archive convention in `.agents/memory/FILE_MAP.md` and `.agents/instructions/repo.md`.

## Errors and Durable Learnings

- The old map optimized a second retrieval system without first reconciling it with the repository's mandatory loading contract. Before designing context injection, trace all always-loaded and progressively loaded entry points; migrate the canonical source in place when the goal is a format migration.
- Loading `improve-skill` first used an incorrect repo-local path and failed without changing files; use the configured skill-root map (`r0` → `/root/.agents/skills`) instead of assuming `.agents/skills/` is repo-local.
- One combined patch tried to delete and add the same path in a single `apply_patch` input and was rejected before changing files. Replace content with an update patch or use separate delete/add operations.
- A shell search placed Markdown backticks inside a double-quoted command string, causing harmless command-substitution attempts and two `command not found` messages. No files changed. Use a single-quoted search pattern or otherwise keep backticks out of shell-interpreted strings.

## Suggested Skills

- Resume with `handoff`, then use `wayfinder` and `grilling` for the selected frontier ticket.
- Use `writing-for-agents` for **OKF Authoring Skill Contract**; use `official-sources` when exact external conformance facts need rechecking.
- End every repository-changing session with `update-agent-docs`.
