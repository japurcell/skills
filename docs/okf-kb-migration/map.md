## Destination

An implementation-ready migration design and ExecPlan-ready handoff for converting the canonical documents under `.agents/instructions/` and `.agents/memory/` in place to OKF v0.2, while preserving the established `AGENTS.md` → `.agents/memory/INDEX.md` progressive-loading path. The design includes an OKF authoring skill and blocking OKF lint validation hooks for both GitHub Copilot CLI and Gemini CLI, with no second context-loading path.

## Notes

- [Corrected implementation overview](implementation-overview.md) explains the one-path architecture and remaining decision sequence. This map remains the authoritative decision index.
- This map is planning-only. Implementation and proof-of-concept delivery are outside the destination.
- Every session should activate `wayfinder`; grilling tickets also activate `grilling`. `domain-modeling`, requested by Wayfinder, is unavailable, so use repository evidence and the user's explicit source-of-truth decisions as the disclosed fallback.
- Use `official-sources` and `research` for new external investigation, and `explore` for local codebase facts. The external baseline is OKF v0.2 from `GoogleCloudPlatform/open-knowledge-format`.
- The canonical documents are the OKF documents. Preserve their existing progressive discovery through `AGENTS.md` and `.agents/memory/INDEX.md`; do not create a generated knowledge sidecar or inject selected context at prompt time.
- The OKF authoring skill teaches agents how to create and maintain a conforming canonical document. The linter is the enforcement boundary and runs as a blocking validation hook for both Copilot and Gemini.
- Preserve immutable `.agents/sources/`, pending-ingest gating, orphan cleanup, provider-specific hook envelopes, and behavioral parity between intentionally duplicated Copilot and Gemini helpers unless a later ticket proves a narrowly scoped integration change is required.
- Existing research remains evidence only. Decisions recorded under the rejected sidecar-and-selector charter are obsolete and cannot be carried forward without being reconsidered under this destination.

## Decisions so far

- [In-Place OKF Migration Charter](tickets/in-place-okf-migration-charter.md): Convert the canonical knowledge documents themselves to OKF, retain the existing indexed loading path, teach authors with a skill, and enforce conformance through blocking Copilot and Gemini lint hooks without context injection.
- [In-Place OKF Document Contract](tickets/in-place-okf-document-contract.md): Use separate in-place memory and instruction bundles with standard metadata, stable uppercase routing paths, a small path-derived type vocabulary, resolvable file-relative links, conforming source summaries, and no required extension fields.

## Not yet specified

<!-- FOG START -->
<!-- FOG END -->

## Out of scope

- Implementing the migration or delivering a proof of concept in this Wayfinder effort.
- Generating or maintaining a second `.agents/okf/` knowledge copy: the [Migration Charter](tickets/obsolete/migration-charter.md), [Bundle Publication and Lifecycle](tickets/obsolete/bundle-publication-and-lifecycle.md), [Concept Profile and Taxonomy](tickets/obsolete/concept-profile-and-taxonomy.md), [Concept Identity and Links](tickets/obsolete/concept-identity-and-links.md), [Source Summary Transition Policy](tickets/obsolete/source-summary-transition-policy.md), and [Projection Producer and Linter](tickets/obsolete/projection-producer-and-linter.md) decisions are obsolete.
- Selecting or injecting repository knowledge at prompt time: the [Selector Contract and Ranking](tickets/obsolete/selector-contract-and-ranking.md), [Mandatory Context and Fallback](tickets/obsolete/mandatory-context-and-fallback.md), [Copilot CLI Integration Surfaces](tickets/obsolete/copilot-cli-integration-surfaces.md), [Copilot-First Runtime Contract](tickets/obsolete/copilot-first-runtime-contract.md), and [Copilot-First Provider Integration and State](tickets/obsolete/copilot-first-provider-integration-and-state.md) decisions are obsolete.
- Qualifying or promoting a second runtime path: the [Evaluation Corpus and Promotion Gates](tickets/obsolete/evaluation-corpus-and-promotion-gates.md), [Dual-Provider Evaluation Amendment](tickets/obsolete/dual-provider-evaluation-amendment.md), [Copilot-First Rollout and Rollback](tickets/obsolete/copilot-first-rollout-and-rollback.md), and [Copilot-First Implementation Sequencing and Handoff](tickets/obsolete/copilot-first-implementation-sequencing-and-handoff.md) decisions are obsolete. Earlier [Provider Integration and State](tickets/obsolete/provider-integration-and-state.md), [Rollout and Rollback](tickets/obsolete/rollout-and-rollback.md), and [Implementation Sequencing and Handoff](tickets/obsolete/implementation-sequencing-and-handoff.md) tickets remain obsolete as well.
- Replacing `AGENTS.md` or `.agents/memory/INDEX.md` as the repository knowledge entry point.
- Migrating published `skills/`, `agents/`, or `references/` content; the new repository-local OKF authoring skill is part of the migration tooling, not migrated knowledge.
- Treating OKF trust metadata as authorization, replacing repository access controls, or designing a general attested-computation runtime.
