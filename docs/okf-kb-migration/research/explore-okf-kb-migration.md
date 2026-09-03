# OKF KB Migration — Current-System Exploration

## Topic

Map the existing agent knowledge base and source-ingestion hooks before planning a migration to Open Knowledge Format (OKF) v0.2.

## Current Knowledge Surfaces

- `AGENTS.md` defines the loading contract: always read `.agents/memory/INDEX.md`, then load core and area-scoped documents on demand.
- `.agents/instructions/` stores area-scoped operational rules.
- `.agents/memory/` stores the loading index, architecture, conventions, file/API maps, testing guidance, known issues, ADRs, source summaries, and the ingestion log.
- `.agents/sources/` stores immutable raw source inputs.
- `.agents/skills/{clean-agent-docs,update-agent-docs,ingest-source}/` governs cleanup, durable-memory updates, and source integration.
- `.github/hooks/` and `.gemini/hooks/` independently implement the same source-staleness and pending-ingest behavior for Copilot and Gemini.

## Current Flow

```text
.agents/sources/**/*.md
  -> startup/prompt scan + SHA-256 fingerprint
  -> source-ingest-manifest.json reconciliation
  -> scaffold or stale summary under .agents/memory/sources/
  -> pending-ingest context injected into the agent turn
  -> /ingest-source reads raw source and updates its summary
  -> durable facts are woven into instructions/memory
  -> INDEX.md and LOG.md are updated manually
```

The hooks enforce freshness of source summaries, but they do not select task-relevant knowledge from the wider KB. Task-specific loading currently depends on agents following the routing table in `INDEX.md`.

## Data and Path Contracts

- The manifest schema is version `1`; entry states are `active`, `needs_summary`, `stale`, and `orphan`.
- Only `needs_summary` and `stale` block normal completion.
- Source identity is its relative path; content hashes provide rename heuristics.
- Summary names flatten source paths by replacing `.` and joining components with `__`, then adding `.summary.md`.
- Summary resolution is inferred from a changed summary hash plus a non-scaffold frontmatter status; it is not semantic validation.
- Copilot and Gemini helpers are intentionally duplicated and must remain behaviorally synchronized.
- Existing memory/instruction frontmatter generally exposes only `coverage`; source summaries expose `status`.
- The nine committed verified summaries currently omit the opening `---` delimiter, so generic YAML-frontmatter and OKF parsers see no frontmatter even though the ingest state machine treats them as resolved.

## OKF Fit and Gaps

Strong fit:

- Both systems use Markdown, YAML frontmatter, Git, hierarchy, index pages, logs, and links.
- Current raw-source and summary layers map naturally to OKF provenance and concept relationships.
- Area-scoped loading maps naturally to progressive-disclosure `index.md` files and producer-defined routing metadata.

Gaps that require design decisions:

- OKF v0.2 requires every non-reserved concept document to have a non-empty `type`; current documents do not.
- OKF reserves lowercase `index.md` and `log.md`; the current KB uses uppercase `INDEX.md` and `LOG.md` as ordinary files. In-place conversion is especially risky on case-insensitive filesystems.
- OKF paths are concept identities, while the current system already treats paths as identities and uses heuristic rename handling. Stable moves and redirects are not solved by the format.
- OKF defines a representation and traversal conventions, not task retrieval. Efficient context selection needs an explicit consumer/router.
- Current `coverage` text is too coarse for deterministic task routing unless it is normalized into producer-defined extensions such as scopes, paths, task kinds, priorities, or load conditions.
- Current freshness is source-summary state in a JSON manifest; OKF lifecycle is per concept (`status`, `stale_after`) and provenance/trust is expressed through `sources`, `generated`, and `verified`.
- `index.md` may be generated, but the migration must decide which artifacts are canonical and which are projections to avoid dual sources of truth.

## Likely Migration Seams

- Introduce an OKF domain model at the shared logical boundary `scan sources -> reconcile state -> render context`, while keeping provider-specific hook envelopes unchanged.
- Version the manifest/state migration instead of silently repurposing manifest v1.
- Treat context rendering as a consumer adapter: query OKF metadata and indexes, rank/select concepts, then emit only the bounded context needed for the task.
- Preserve immutable raw inputs and explicit source-to-concept provenance.
- Stage compatibility so current `AGENTS.md`, ingestion gating, orphan cleanup, and final-response backstops keep working until the OKF consumer is proven.

## Validation Targets for a Future Implementation

- OKF v0.2 conformance for every concept and reserved file.
- Cross-link and source-footnote integrity beyond OKF's permissive minimum.
- Parity for new, changed, renamed, deleted, and orphaned sources.
- Copilot and Gemini hook registration/output parity.
- Retrieval evaluations measuring relevant-context recall, irrelevant-token reduction, routing latency, stale/deprecated exclusion, and required-instruction preservation.

## Likely Edit Targets

- `AGENTS.md`
- `.agents/instructions/` and `.agents/memory/`
- `.agents/skills/{clean-agent-docs,update-agent-docs,ingest-source}/SKILL.md`
- `.github/hooks/scripts/{auto-ingest-source,inject-auto-ingest-context}.py`
- `.github/hooks/scripts/helpers/auto_ingest.py`
- `.gemini/hooks/scripts/{auto-ingest,inject-auto-ingest-context}.py`
- `.gemini/hooks/scripts/helpers/source_ingest.py`
- Corresponding hook and helper test scripts under `scripts/`

## Gotchas

- User changes already exist in `.agents/memory/FILE_MAP.md` and `docs/research/`; migration work must not overwrite them.
- Prompt-time injection is required because Copilot may run `userPromptTransformed` before `sessionStart`.
- Gemini's final gate belongs at `AfterAgent`, not `AfterModel`.
- Hook stdout must remain JSON-only.
- The dedicated `GoogleCloudPlatform/open-knowledge-format` repository is now canonical; the requested `knowledge-catalog/okf` subtree is a frozen snapshot.
