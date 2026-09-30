# Revisit Design After Existing Repositories

**Type:** grilling
**Status:** closed
**Blocked By:** evaluate-apm-reuse.md, evaluate-ecc-ownership.md, evaluate-distribution-references.md
**Research Dir:** none

## Question

Given verified findings from the six existing distribution repositories supplied by the user, should the approved contract or implementation design change before implementation? Present only evidence-backed changes and real alternatives. Decide reuse of APM versus the planned lifecycle engine, worthwhile ownership or reproducibility refinements, and whether native package timing changes. Preserve settled requirements unless the user explicitly changes them. Implementation remains on hold.

---

## Decision discussion

All three exact blocking research tickets are closed. The evidence and refined design are in [Review Existing Agent Asset Distributors](../existing-repos-review.md). The user accepted the architecture and strict verification first, then accepted the remaining checkout line-ending policy after it was identified as the only open question.

## Resolution

On 2026-09-29 the user accepted all three recommendations through the live exchange:

1. Retain the current architecture: a selective installer with one Python lifecycle engine, committed copied payloads as the team default, local and personal scopes, and native packages as a later additional channel. Do not adopt APM or ECC as the initial lifecycle runtime. Their examples inform the implementation while the approved conflict, ownership, pruning, and recovery guarantees remain authoritative.
2. Add strict offline, read-only `status --check`. Validate desired-selection/lock agreement, schema and ownership, missing or changed payloads, and owned configuration values. Fail on drift without fetching, installing, repairing, updating refs, or modifying records or Git configuration. CI checks the committed checkout before any installation or restoration. Deliberate retained edits remain preserved by updates and are reported by strict verification.
3. Declare checkout line-ending policy for committed team assets. Preserve exact rendered hashes with narrowly scoped, installer-owned `.gitattributes` entries for declared LF/CRLF text and binary files. Preserve unrelated rules and apply normal configuration ownership, conflict-before-writes, and unchanged-only pruning. Do not normalize arbitrary whitespace, renormalize the repository, or modify personal Git settings. Prove fresh clones across operating systems and `core.autocrlf` settings.

The [implementation ExecPlan](../../agent-asset-installer/ExecPlan.md) incorporates these refinements into interfaces, records, catalog policy, lifecycle acceptance, clone/CI checks, and usage documentation. No new installation channel or command family is added, and no rollback/history feature is introduced. Original contract requirements and accepted test seams remain unchanged.

This closes the decision interview with no remaining in-scope question or fog. Planning acceptance does not lift the user's explicit implementation hold. No source, tests, scaffolding, or installed assets were changed.
