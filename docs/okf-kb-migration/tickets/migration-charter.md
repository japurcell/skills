# Migration Charter

**Type:** grilling
**Status:** obsolete
**Blocked By:** none
**Research Dir:** N/A

## Question

What destination, migration boundary, source-of-truth posture, consumer outcome, conformance policy, compatibility contract, and success hierarchy govern this Wayfinder effort?

---

## Resolution

The user accepted the recommended charter:

- End with an implementation-ready migration design and ExecPlan-ready handoff, not implementation or a narrow proof of concept.
- Cover `.agents/instructions`, `.agents/memory`, and their ingestion/routing machinery; leave `skills/`, `agents/`, and `references/` outside the migration boundary.
- Keep current documents canonical and introduce an additive generated OKF sidecar projection.
- Design both standards-compatible progressive navigation and deterministic automatic context selection with explainable choices and an explicit fallback.
- Use a portable OKF v0.2 core plus documented namespaced repository extensions; validate writers strictly and keep readers tolerant of unknown fields.
- Introduce no intended compatibility breaks: preserve provider envelopes, pending-ingest gating, immutable sources, standard-library/offline operation, and the current index path until equivalence is proven.
- Rank success as: preserve mandatory instructions and freshness gates; maintain or improve relevant recall; reduce irrelevant tokens; keep selection deterministic, explainable, and latency-bounded; minimize maintenance overhead.
