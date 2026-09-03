## Destination

An implementation-ready migration design and ExecPlan-ready handoff for adopting OKF v0.2 across `.agents/instructions`, `.agents/memory`, and their ingestion/routing machinery, improving task-specific context selection without breaking current loaders, hooks, installers, or offline operation.

## Notes

- This map is planning-only. Implementation and proof-of-concept delivery are outside the destination.
- Every session should activate `wayfinder`; grilling tickets also activate `grilling`. `domain-modeling`, requested by Wayfinder, is unavailable, so use the existing repository research and local architecture evidence as the disclosed fallback.
- Use `official-sources` and `research` for any new external investigation, and `explore` for local codebase facts. The canonical external baseline is OKF v0.2 from `GoogleCloudPlatform/open-knowledge-format`.
- The accepted charter keeps current authored documents canonical, produces an additive sidecar projection, supports both progressive navigation and deterministic automatic selection, uses a portable OKF core plus documented namespaced extensions, and preserves compatibility.
- Safety and correctness outrank token reduction: mandatory instructions and freshness gates cannot be omitted; relevant-context recall must not regress.
- Preserve immutable `.agents/sources/`, pending-ingest gating, orphan cleanup, provider-specific hook envelopes, and behavioral parity between intentionally duplicated Copilot and Gemini helpers.
- Existing evidence: [OKF primary-source research](research/okf-primary-sources.md), [current-system exploration](research/explore-okf-kb-migration.md), and [research handoff](handoff.md).

## Decisions so far

- [Migration Charter](tickets/migration-charter.md): Produce an implementation-ready, additive OKF migration design for the core agent KB, with deterministic selection, strict compatibility, and safety-first success criteria.
- [Bundle Publication and Lifecycle](tickets/bundle-publication-and-lifecycle.md): Commit one deterministic repo-local `.agents/okf/` projection with manifest-backed freshness, generated indexes, collision-safe paths, legacy fallback, and Git-based rollback.
- [Concept Profile and Taxonomy](tickets/concept-profile-and-taxonomy.md): Adopt `agent-kb@1.0.0` with seven concept types, explicit deterministic mappings, 42 semantically bounded concepts, conservative provenance, strict writer validation, tolerant readers, and reserved-file-safe indexes.
- [Concept Identity and Links](tickets/concept-identity-and-links.md): Use an explicit stable 42-concept logical path map, deliberate tombstones for semantic replacement, and validated `agent-kb@1.1.0` typed relationships with distinct routing semantics.
- [Source Summary Transition Policy](tickets/source-summary-transition-policy.md): Repair misleading summary metadata before routing, retain manifest v1 as freshness and provenance binding, admit only current active summaries, and stage selection behind strict cross-provider validation.

## Not yet specified

<!-- FOG START -->
- The profile, selector, and evaluation decisions may expose additional relationship semantics, diagnostics, or safety gates that cannot yet be phrased precisely.
- Provider integration may expose distribution or installation constraints beyond the currently known hook and helper boundaries.
<!-- FOG END -->

## Out of scope

- Implementing the migration or delivering a proof of concept in this Wayfinder effort.
- Migrating published `skills/`, `agents/`, or `references/` content; they remain consumers or adjacent surfaces.
- Treating OKF trust metadata as authorization, replacing repository access controls, or designing a general attested-computation runtime.
