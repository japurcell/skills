# Revisit Design After Existing Repositories

**Type:** grilling
**Status:** claimed by subagent-pif1tm
**Blocked By:** evaluate-apm-reuse.md, evaluate-ecc-ownership.md, evaluate-distribution-references.md
**Research Dir:** none

## Question

Given verified findings from the six existing distribution repositories supplied by the user, should the approved contract or implementation design change before implementation? Present only evidence-backed changes and real alternatives. Decide reuse of APM versus the planned lifecycle engine, worthwhile ownership or reproducibility refinements, and whether native package timing changes. Preserve settled requirements unless the user explicitly changes them. Implementation remains on hold.

---

## Decision discussion

All three exact blocking research tickets are closed. The recommendation and two proposed refinements are in [Review Existing Agent Asset Distributors](../existing-repos-review.md). Recommend retaining the planned lifecycle engine and committed-copy default, adding read-only `status --check`, and defining owned, path-specific checkout line-ending rules. The architecture recommendation and refinements remain unapproved until the user responds. No `## Resolution` is recorded yet, and implementation remains on hold.
