# OKF Agent-KB Migration Handoff

## Goal

Finish an implementation-ready design for migrating the canonical documents under `.agents/instructions/` and `.agents/memory/` in place to OKF v0.2. Preserve the existing `AGENTS.md` → `.agents/memory/INDEX.md` loading path, teach OKF authoring through a repository skill, and enforce conformance through blocking GitHub Copilot CLI and Gemini CLI lint hooks.

## Status

- The user found a charter-level flaw in the closed map: its `.agents/okf/` sidecar and prompt-time selector would inject knowledge already discoverable through the mandatory `AGENTS.md` → `.agents/memory/INDEX.md` path.
- **In-Place OKF Migration Charter** records the corrected source-of-truth and enforcement model and is closed.
- All 18 tickets derived from the old sidecar/selector/provider-runtime design are `obsolete`. Their research may be reused as evidence, but their decisions are not authoritative.
- Four replacement tickets are open. **In-Place OKF Document Contract** is the sole frontier; **OKF Authoring Skill Contract** and **OKF Linter and Provider Hooks Contract** depend on it; **In-Place Migration Sequencing and Verification** depends on all three.
- `map.md` and `implementation-overview.md` now describe the corrected architecture. No implementation or implementation ExecPlan exists.

## Next Focus

Resolve **In-Place OKF Document Contract** only.

## Exact Next Step

Activate `handoff`, `wayfinder`, `grilling`, and `official-sources`; claim `tickets/in-place-okf-document-contract.md`; recheck the local OKF v0.2 primary-source summary against the current official specification where exact conformance matters; then grill the in-place bundle, metadata, reserved-name, link, uppercase-index/log, source-summary, and extension-field decisions. Do not start implementation.

## Decisions and Constraints

- Canonical `.agents/instructions/` and `.agents/memory/` documents become OKF documents in place; there is no generated knowledge sidecar.
- `AGENTS.md` and `.agents/memory/INDEX.md` remain the knowledge entry and routing path.
- No prompt-time selector, context injection, provider runtime, fallback path, qualification state, or promotion ladder belongs to this migration.
- A repository skill teaches OKF authoring. A linter validates authored documents and blocks failures through both providers' validation hooks.
- Lint hooks do not replace or duplicate current source-ingest freshness behavior. Immutable `.agents/sources/` remains out of bounds.
- Planning only: close the four replacement decisions before creating an implementation ExecPlan.

## Relevant Files

- `docs/okf-kb-migration/map.md` — corrected destination, authoritative decision index, and dependency graph.
- `docs/okf-kb-migration/tickets/in-place-okf-migration-charter.md` — user's correction captured as the only closed authoritative decision.
- `docs/okf-kb-migration/tickets/in-place-okf-document-contract.md` — sole frontier and next ticket.
- `docs/okf-kb-migration/tickets/okf-authoring-skill-contract.md` — blocked authoring-skill design.
- `docs/okf-kb-migration/tickets/okf-linter-and-provider-hooks-contract.md` — blocked linter and hook design.
- `docs/okf-kb-migration/tickets/in-place-migration-sequencing-and-verification.md` — final blocked sequencing decision.
- `docs/okf-kb-migration/implementation-overview.md` — concise corrected architecture for novice readers.
- `.agents/scratchpad/explore-okf-in-place-correction.md` — local evidence tracing the duplicate-context flaw.
- `docs/okf-kb-migration/research/okf-primary-sources.md` — prior OKF v0.2 research; its sidecar recommendation is obsolete, but specification facts remain reusable after verification.

## Verification State

- Ticket validation passed with one closed correction ticket, 18 obsolete tickets, four open replacements, no active claims, and **In-Place OKF Document Contract** as the sole frontier.
- All relative Markdown links in `map.md`, `implementation-overview.md`, and `handoff.md` resolve. Active-document searches found old runtime terms only where the rejected design is explicitly identified as obsolete.
- A delegated repository-wide stale-document audit found no other active references presenting the rejected design as current and no migration-relevant broken links. It identified `relocation-execplan.md` as the sole stale artifact; that completed plan now labels its counts as a 2026-09-03 relocation snapshot and routes current status to `map.md` and this handoff.
- `git diff --check` passed.
- The mandatory end-of-session `update-agent-docs` pass found no `.agents/instructions/` or `.agents/memory/` edit necessary. This session changed only the existing planning subtree; current repo guidance already routes long-lived design work there.
- No code, hook, skill, canonical KB document, or configuration was implemented or changed.

## Errors and Durable Learnings

- The old map optimized a second retrieval system without first reconciling it with the repository's mandatory loading contract. Before designing context injection, trace all always-loaded and progressively loaded entry points; migrate the canonical source in place when the goal is a format migration.
- Loading `improve-skill` first used an incorrect repo-local path and failed without changing files; use the configured skill-root map (`r0` → `/root/.agents/skills`) instead of assuming `.agents/skills/` is repo-local.
- One combined patch tried to delete and add the same path in a single `apply_patch` input and was rejected before changing files. Replace content with an update patch or use separate delete/add operations.

## Suggested Skills

- Resume with `handoff`, then use `wayfinder`, `grilling`, and `official-sources` for the frontier ticket.
- Use `writing-for-agents` when designing the authoring skill's instruction hierarchy.
- End every repository-changing session with `update-agent-docs`.
