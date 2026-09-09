# Source Summary Transition Policy

**Type:** grilling
**Status:** obsolete
**Blocked By:** none
**Research Dir:** N/A

## Question

How must the migration repair and transition the currently malformed verified source summaries before routing depends on their metadata, while preserving manifest reconciliation, immutable raw inputs, source-to-summary provenance, rename/delete/orphan behavior, and honest verification semantics?

---

<!-- Resolution will be appended here -->

## Resolution

Repair the nine current canonical Source Summaries before generating or selecting any Source Summary concept. Their YAML is structurally parseable now, but `status: verified` has no actor or timestamp evidence and must not be treated as trust metadata. Replace it with non-empty, selection-oriented `coverage` frontmatter, initialized from the matching `When to load` guidance in `.agents/memory/INDEX.md`. The summary owns that coverage text; keep the legacy index aligned while it remains a routing surface. Remove completed-document `Stale Reason` text. Reserve `status: scaffold` for unresolved scaffolds only.

Do not define or emit a replacement verification claim in this migration. Completed summaries omit OKF `verified`; absence means unknown, not false. Supporting `verified` later requires a separately specified canonical evidence schema with a real actor and timestamp plus linter enforcement. A changed non-scaffold summary hash remains operational freshness evidence only, never semantic or factual verification.

Keep source-ingest manifest v1 and its four states unchanged. The manifest is the authoritative operational binding between an immutable raw source and its canonical summary; `.agents/okf-profile.json` owns stable concept identity, and paths repeated in summary bodies are human-readable documentation only. Semantic schema, provenance, and trust checks belong to the projection linter rather than manifest reconciliation. Preserve the existing pending-ingest gates, provider-specific but behaviorally aligned helpers, rename heuristic, manual orphan cleanup, and immutable `.agents/sources/` inputs.

Project a Source Summary only when exactly one manifest entry binds it to an existing raw source, the entry is `active`, and its recorded raw and summary hashes match the live files. `needs_summary` and `stale` retain their current hard gate. An orphan that is still mapped as a current concept makes the projection unusable until a human updates the source/profile binding or applies the explicit tombstone policy; unrelated unmapped orphans remain advisory cleanup and do not change the legacy gate. Rename hashes may suggest a move but never choose concept identity or silently transfer verification, particularly when duplicate source content makes the match ambiguous.

Land the transition in three gates:

1. Repair all nine summaries, synchronize their committed manifest hashes through the existing reconciliation contract, verify raw hashes are unchanged, and leave legacy routing authoritative.
2. Add the deterministic projection producer and linter, then require a clean projection check.
3. Enable OKF selection only after both earlier gates pass.

No generator, installer, or prompt-time hook may repair canonical inputs or silently rewrite the committed bundle. A failed gate leaves OKF routing disabled; a missing, invalid, stale, or mapped-orphan projection emits an explainable diagnostic and uses the already-decided legacy fallback.

Before Source Summary routing is eligible, validation must prove all of the following:

- All nine summaries parse with non-empty, selection-oriented `coverage`; no completed summary contains `status: verified`, `status: scaffold`, or completed-document stale-reason text.
- Every projected summary has exactly one live `active` manifest binding with matching raw and summary hashes, and the repair changes no raw-source hash.
- Every emitted `Source Summary` uses standard OKF `sources` to reference the raw input selected by that binding and emits no `verified` field.
- Copilot and Gemini parity tests cover new, stale, renamed, deleted, orphaned, and pending states.
- Negative checks prove invalid summary metadata and mapped orphans make the projection unusable, produce an explainable diagnostic, and preserve legacy fallback.
- Repository checks prove generation, installation, and prompt-time loading perform no silent repair writes.
