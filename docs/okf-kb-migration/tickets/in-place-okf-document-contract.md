# In-Place OKF Document Contract

**Type:** grilling
**Status:** closed
**Blocked By:** none
**Research Dir:** N/A

## Question

How should the existing canonical Markdown documents under `.agents/instructions/` and `.agents/memory/` conform to OKF v0.2 in place, including bundle boundaries, required metadata, document types, links, reserved `index.md` and `log.md` semantics, current uppercase routing files, source summaries, and any justified repository extension fields?

---

<!-- Resolution will be appended here -->

## Resolution

The repository adopts this in-place OKF v0.2 document contract:

### Bundle and identity boundaries

- `.agents/memory/` and `.agents/instructions/` are separate physical OKF bundles. `.agents/` is not a bundle with profile exclusions, so immutable raw-source Markdown, repo-local skills, and scratchpad documents stay outside the concept set.
- Existing concept paths remain stable because a concept's bundle-relative path without `.md` is its OKF identity. The migration does not move or rename canonical documents.
- Exact lowercase `index.md` and `log.md` are prohibited throughout both initial bundles. Reconsidering them requires a later contract change.
- Uppercase `.agents/memory/INDEX.md` and `.agents/memory/LOG.md` remain ordinary concepts at their exact paths, with types `Knowledge Index` and `Source Ingestion Log`. Their current routing and ingestion-history bodies remain authoritative; no lowercase sibling or second navigation/history convention is introduced.
- Because neither bundle has a lowercase root `index.md`, the target OKF version is pinned in authoring and lint tooling rather than document metadata.

### Concept metadata and types

- Every canonical Markdown concept begins with parseable YAML frontmatter containing non-empty string `type` and `description` values. Existing `coverage` values migrate to `description`; `coverage` is not retained as a required extension.
- The repository profile enforces this path-derived type vocabulary: `Agent Instruction`, `Agent Memory`, `Knowledge Index`, `Source Ingestion Log`, `Known Issue`, `Testing Guidance`, `Architecture Decision`, and `Source Summary`.
- `title`, `resource`, and `tags` remain optional. The existing Markdown body and heading structure remain valid without a content rewrite.
- The initial profile defines no custom frontmatter fields. Authoring and lint tooling must not depend on an extension without a documented contract amendment. Consumers still tolerate unknown fields as OKF requires.

### Links and sources

- Repository-local Markdown links and path-valued fields use file-relative paths rather than bundle-root-relative `/...` paths. They may cross between the two bundles or point to other repository files, including immutable raw sources, but must stay inside the repository and resolve. External URLs remain allowed.
- Each completed source summary is a `Source Summary` concept with routing-oriented `description` metadata and exactly one `sources` entry whose required `resource` points to the matching immutable raw source.
- Completed source summaries remove the unsupported legacy `status: verified` claim, omit lifecycle `status` to use OKF's stable default, and do not fabricate `verified` metadata. Source IDs and per-claim footnotes are optional and appear only when the body uses them.
- Unresolved source-summary scaffolds remain conforming concepts with `type: Source Summary`, a pending description, source provenance, and standard `status: draft`. Successful integration removes `draft`; the source-ingest workflow no longer uses non-standard `status: scaffold`.

### Optional provenance, trust, and lifecycle

- Migration does not synthesize `generated`, `verified`, or `stale_after` from Git history, migration time, or unsupported assumptions.
- When `generated` is present, the repository profile requires both `by` and `at`. `verified` is authored canonically as a list of `{ by, at }` events even though OKF consumers also accept a bare mapping. Every timestamp-valued field requires an explicit UTC offset.
- Stable documents omit `status`; `draft`, `deprecated`, and `stale_after` appear only when their real lifecycle semantics apply.
- Present `sources` entries follow OKF v0.2, including a valid `resource`; optional IDs are required only when joined to body footnotes.

This contract changes document representation only. It preserves `AGENTS.md` → `.agents/memory/INDEX.md` progressive loading, immutable `.agents/sources/`, and source-ingest freshness/orphan behavior apart from the conforming scaffold metadata shape. It introduces no sidecar, context selector, prompt injection, provider runtime, or authorization semantics.
