# Set Audit Evidence and Model Coverage

**Type:** grilling
**Status:** open
**Blocked By:** extract-complete-authoring-checklist.md, establish-provider-compatibility-constraints.md
**Research Dir:** not applicable

## Question

What exact evidence makes this audit complete, and which OpenAI models, client surfaces, scenarios, and repetitions must that evidence cover?

The human chose static review of all in-scope skills plus targeted OpenAI baselines, with broader validation in the ExecPlan. Imported skills are excluded by the ownership decision; do not choose them for this effort's baselines. The requested models are 5.6, 6, and 6.1 Sol; 5.6 and 6 Luna; Astra; and Terra. Set exact model IDs and effort values from verified availability, baseline selection criteria, safe fixtures, trigger and negative-case coverage, grading criteria, and reporting for unavailable execution. Separate audit baselines from later candidate comparisons. Reconcile provider constraints and existing eval coverage. Preserve `dotnet-upgrade` document-only acceptance; do not run privileged workflows to fill a gap or report an unrun test as passing.

The decision must specify a reproducible evidence contract, exact supported model choices or an explicit unresolved prerequisite, and what constitutes a blocking audit gap.

---

<!-- Resolution will be appended here. -->
