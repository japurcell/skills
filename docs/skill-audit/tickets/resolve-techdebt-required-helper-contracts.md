# Resolve Techdebt Required Helper Contracts

**Type:** grilling
**Status:** open
**Blocked By:** review-quality-and-harness-skills.md
**Research Dir:** not applicable

## Question

Are Techdebt's unconditional explorer dispatch and test-edit-only TDD activation intentional caller exceptions, or should it retain the required helpers' narrow direct-read and mandatory source-edit activation branches?

[QH-005](../findings.md#qh-005-techdebt-unconditional-exploration-conflicts-with-explores-narrow-branch) and [QH-006](../findings.md#qh-006-techdebt-limits-tdd-activation-contrary-to-its-required-helper) own the two distinct consumer tensions. Resolve each explicitly: Explore forbids narrow-scope subagents, while Techdebt asks for 1-3; TDD activation covers source edits, while Techdebt conditions loading on test changes. Loading TDD is distinct from creating tests. Do not silently make either dependency optional, invent unnecessary tests, or change an excluded imported helper.

Preserve relevant duplication search, broad-area independence, supplied-candidate discovery bypass, bounded changed scope, no redundant exploration, meaningful validation and TDD's existing seam approval. Keep user-approved exceptions scoped. Validate narrow/provided/multi-area cases and source-only/test-edit/non-code cases separately. Both final documents retain both IDs and this route; dependent consumer changes remain pending until each actual choice is resolved.

---

<!-- Resolution will be appended here. -->
