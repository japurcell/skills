# Concept Profile and Taxonomy

**Type:** grilling
**Status:** closed
**Blocked By:** none
**Research Dir:** N/A

## Question

What versioned repository profile maps the current agent knowledge base into OKF concepts: concept types, required/recommended/forbidden fields, extension namespace and semantics, current `coverage` mapping, source/provenance/trust/lifecycle rules, and reserved-file constraints?

---

## Resolution

Adopt repository profile `agent-kb@1.0.0`, independently versioned from `okf_version: "0.2"`. The profile uses one namespaced extension mapping, `x-agent-kb`, and initially projects 30 canonical Markdown inputs from `.agents/instructions/` and `.agents/memory/`. Exclude the navigational `.agents/memory/INDEX.md` and operational `.agents/memory/LOG.md`; retain `.agents/memory/FILE_MAP.md` as repository knowledge.

Projection cardinality is semantic rather than one-to-one. Split a source only when the resulting concepts can be selected, maintained, or deprecated independently because they differ in trigger, scope, audience, provenance, or lifecycle. Length and heading count alone do not justify a split. Under that rule, keep 27 inputs whole and split three hook documents:

- `.agents/instructions/hooks.md` into runtime and maintenance guidance, output and compatibility contract, repository hook issues, and validation guidance.
- `.agents/memory/adrs/hooks.md` into eight concepts, one per ADR.
- `.agents/memory/known-issues/hooks.md` into source ingestion, hook development, observability, and platform portability.

This produces 43 projected concepts. An official-reference section contributes `sources` metadata rather than a standalone concept, and source summaries remain whole.

The closed `1.0.0` type registry is `Agent Instruction`, `Repository Knowledge`, `Testing Guidance`, `Known Issue`, `Architecture Decision`, `Source Summary`, and `Hook Contract`. Adding a type is additive and requires a profile minor-version bump.

Every emitted concept requires non-empty `type`, `title`, and selection-oriented `description`, plus normalized `x-agent-kb.source.path`. Split concepts additionally require a stable `x-agent-kb.source.anchor`. The writer allowlist is:

- Always allowed and required: `type`, `title`, `description`, and `x-agent-kb`.
- Conditionally allowed OKF fields: `tags`, `resource`, `sources`, `status`, `stale_after`, `generated`, and `verified`.
- Allowed inside `x-agent-kb`: `source`, `areas`, and `paths` only.

`Source Summary` requires `sources`; every split concept requires `source.anchor`. Do not emit legacy `coverage` or `timestamp`, or attested-computation fields `runtime`, `parameters`, `computation`, `executor`, and `attester`. Writers reject unknown fields; readers tolerate them for forward compatibility.

For routing, whole-file `coverage` seeds `description`, while split descriptions come from explicit profile mappings; never heuristically parse coverage prose. Every concept requires one or more `x-agent-kb.areas` values from the closed initial vocabulary `repo`, `agents`, `skills`, `hooks`, `scripts`, `powershell`, and `source-ingest`. Optional `x-agent-kb.paths` contains normalized repository-relative globs. All mappings are explicit and versioned. Task kinds, priority, and mandatory-load policy remain decisions for selector and fallback tickets.

Provenance and lifecycle are conservative. `Source Summary` concepts reference immutable raw sources through `sources`; other concepts use `sources` only for explicit authoritative references. Projection time does not imply `generated`. Emit `verified` only with real actor and timestamp evidence. The malformed canonical `status: verified` summaries do not map to OKF `verified` or `status`. Omit `status` for current canonical documents, accepting OKF's stable default; emit `deprecated` or an absolute UTC `stale_after` only from an explicit canonical signal. Source-ingestion workflow states and gates stay operational and do not become OKF trust metadata.

Each included bundle directory receives a generated lowercase `index.md`. Only the root index has frontmatter, containing only `okf_version: "0.2"`; indexes list deterministic sorted links with descriptions. Do not generate `log.md`, and never project canonical `INDEX.md` or `LOG.md` as concepts. Reject case-folded path collisions throughout the bundle.

Profile semantic versioning is contract-based: patch releases cover documentation, validation, or generator corrections that preserve the contract; minor releases add optional fields, types, or area values; major releases remove or rename vocabulary, add required fields, change established meaning, or otherwise break compatibility. OKF versioning remains independent, though an incompatible OKF upgrade can require a profile major release.
