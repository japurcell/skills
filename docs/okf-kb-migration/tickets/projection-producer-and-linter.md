# Projection Producer and Linter

**Type:** grilling
**Status:** closed
**Blocked By:** bundle-publication-and-lifecycle.md, concept-profile-and-taxonomy.md, concept-identity-and-links.md, source-summary-transition-policy.md
**Research Dir:** N/A

## Question

What are the producer and linter contracts: inputs and outputs, idempotency, deterministic ordering, profile validation beyond OKF minimum conformance, freshness checks, manifest/state versioning, invocation points, failure behavior, and the boundary that prevents prompt-time writes?

---

<!-- Resolution will be appended here -->

## Resolution

Adopt producer contract `agent-kb-producer@1.0.0` and integer `projection_manifest_version: 1`. Implement one standard-library-only Python entry point, `scripts/okf-projection.py`, with public `generate` and `check` modes. The producer and its linter share one parsing, normalization, rendering, and validation path so check mode cannot drift from generation.

### Inputs and outputs

The authoritative producer inputs are a closed set:

- `.agents/okf-profile.json`, including every concept mapping, typed relationship, selector path-prefix table, and generated-index title and description;
- every canonical Markdown path and exact heading selection mapped by that profile;
- `.agents/memory/sources/source-ingest-manifest.json` plus the raw source needed to validate each mapped Source Summary binding; and
- the producer, profile, manifest-schema, selector-data, and OKF versions declared by those contracts.

Fail when a mapped input is absent, duplicated, ambiguous, or outside its allowed repository root. Also fail when an eligible canonical document is not explicitly mapped or excluded. Discovery is only a completeness check; it never invents identity, metadata, headings, areas, paths, task kinds, or relationships.

The producer exclusively owns `.agents/okf/`. Its complete output consists of the 42 current or later explicitly registered concept documents, lowercase `index.md` files for the root and every included directory, and `.projection-manifest.json`. It emits no `log.md`, undeclared file, cache, lock, or persistent staging state.

### Extraction and deterministic rendering

Require UTF-8 canonical inputs. Remove canonical YAML frontmatter from projected concept bodies. Otherwise preserve a whole-file Markdown body; for a split concept, select only the exact registered ATX headings outside fenced code, retain their canonical source order, and reproduce every registered section completely. Reject missing, duplicate, ambiguous, reordered, or overlapping heading selections rather than guessing.

Render through a closed-schema serializer with deterministic field order and quoting. Emit LF line endings and exactly one terminal newline. Sort every unordered collection by its normalized contract key; preserve only source order that the profile explicitly makes meaningful, such as sections within one split concept. Do not emit timestamps, mtimes, absolute machine paths, Git state, random values, or other environment-dependent content.

The profile contains an explicit table for every generated index, including its path, title, and description. Each index lists only immediate child indexes and concepts, ordered by normalized relative link path ascending. Only the root `index.md` has frontmatter, containing exactly `okf_version: "0.2"`. Generated links and descriptions must match the registered concepts and index table.

### Projection manifest and freshness

Serialize `.projection-manifest.json` as deterministic UTF-8 JSON with stable key ordering, two-space indentation, LF endings, and one terminal newline. It contains:

- `projection_manifest_version`, OKF version, profile identity, producer identity, and selector-data identity;
- sorted input records with repository-relative path, role, and SHA-256 digest, including the profile, mapped canonical documents, source-ingest manifest, and raw sources relevant to mapped summaries;
- sorted concept inventory records with logical path, canonical source path and registered section identity, normalized selection metadata, relationships, lifecycle metadata, output SHA-256 digest, and rendered UTF-8 byte count;
- sorted generated-index records and hashes; and
- one bundle digest over the ordered generated-output records, excluding the manifest itself to avoid recursive hashing.

The JSON inventory is the selector's machine-readable metadata source, but it is not independently canonical. The linter proves that its records exactly match the emitted concept frontmatter and registered canonical inputs. Before rendering, record all authoritative input hashes; immediately before publication, rehash the same set and abort if any changed. `check` recomputes this evidence. Do not use Git, mtimes, network access, subprocesses, or wall-clock data as freshness evidence.

For a mapped Source Summary, require exactly one live `active` source-ingest binding and matching recorded/live raw and summary hashes. A `needs_summary`, `stale`, or mapped `orphan` state is fatal. An unrelated, unmapped source-summary orphan is the only advisory warning in v1.

### Linter contract

Both modes validate, in deterministic order:

1. Supported contract versions, profile shape and closed keys, complete source coverage, normalized logical paths, selector tables, index table, and glob syntax.
2. UTF-8 canonical inputs, valid canonical frontmatter, stable input hashes, and exact whole/split extraction.
3. Source Summary bindings, operational states, provenance, and freshness.
4. OKF v0.2 minimum conformance and every stricter `agent-kb@1.2.0` field, type, area, task-kind, lifecycle, and writer-allowlist rule.
5. Stable identities, reserved names, case-folded collisions, tombstone symmetry, internal targets, and relationship graph constraints.
6. Complete sorted indexes, producer-owned link integrity, and matching descriptions.
7. Manifest records, metadata equivalence, hashes, byte counts, bundle digest, and absence of undeclared output.

Report all independently detectable violations rather than stopping at the first. A targeted producer test must generate twice from identical inputs and prove byte-for-byte identical trees. Ordinary body Markdown links retain OKF's tolerant behavior; producer-owned indexes, typed relationships, profile references, and internal source references remain strict.

### Modes, publication, and failure behavior

`generate` validates all inputs and constructs and lints the complete output in a temporary sibling directory before modifying `.agents/okf/`. Validation failure removes staging state and leaves the committed bundle unchanged. Once staging passes, atomically replace individual concept and index files, prune orphaned generated files, and atomically replace `.projection-manifest.json` last as the commit marker. A process or I/O interruption during publication may leave mismatched files, but never a falsely usable projection: readers validate the last manifest and hashes, reject the bundle atomically, emit an explainable diagnostic, and use legacy fallback.

`check` performs the same generation and linting without changing tracked workspace files, then byte-compares the expected complete tree with `.agents/okf/`. Ephemeral system temporary storage is allowed and must be cleaned up. Neither mode repairs canonical documents, source-ingest state, or profile mappings.

Diagnostics have a stable code, phase, applicable path or concept, and human-readable message, sorted deterministically. Default output is readable stderr; `--format json` provides a machine-readable form. Exit statuses are:

- `0`: generation or check succeeded;
- `1`: the committed projection differs from expected output;
- `2`: canonical input, profile, source state, or projection validation failed; and
- `3`: invocation, I/O, or unexpected internal failure.

Patch producer releases may make compatible corrections; minor releases may add compatible optional output or diagnostics; a breaking input, output, diagnostic-meaning, or behavior change requires a major release. Manifest readers tolerate unknown additive fields within version 1, while incompatible schema meaning increments `projection_manifest_version`. The producer rejects unsupported profile or manifest versions rather than guessing.

### Invocation and read-only runtime boundary

Contributors explicitly run `generate` after relevant canonical KB, profile, or selector-data edits. Repository validation and future CI run `check`. Contributor and agent instructions may require those commands, but no documentation-maintenance skill silently runs them. Installers distribute the committed workspace bundle unchanged. Installers, startup hooks, prompt hooks, selectors, and provider adapters never invoke the producer or mutate `.agents/okf/`.

The selector reads normalized candidate metadata from the manifest, verifies a selected concept's hash and byte count before rendering its body, and treats any disagreement as a fatal projection-integrity error. To make OKF `stale_after` compatible with deterministic selection, amend `agent-kb-selector@1.0.0` to require an explicit normalized RFC 3339 UTC evaluation-time input. Provider adapters obtain that value; the selector never reads the system clock and records the normalized value in its result.
