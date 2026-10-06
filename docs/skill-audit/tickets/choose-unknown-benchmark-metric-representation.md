# Choose Unknown Benchmark Metric Representation

**Type:** grilling
**Status:** open
**Blocked By:** review-skill-authoring-and-repository-guidance.md
**Research Dir:** not applicable

## Question

How can the eight included graders distinguish unmeasured metrics from measured zero while preserving supported benchmark consumers and the exclusion of imported helpers?

The human accepted the additional producer scope on 2026-10-06 in [Review Delegation and Discovery](review-delegation-and-discovery.md#resolution). That review accepted five targets: `skills/create-skill/evals/grade_benchmark.py`, `skills/improve-skill/evals/grade_benchmark.py`, `skills/self-improve/evals/grade_benchmark.py`, `skills/explore/evals/grade_benchmark.py` and `skills/official-sources/evals/grade_benchmark.py`. The original three targets remain included. Additional source anchors are Explore :49,59-70 and Official Sources :38,47-58. This scope acceptance does not choose a representation or authorize producer/consumer edits; the underlying decision remains pending.

The human accepted three more producer targets on 2026-10-06 in [Review Quality and Harness Skills](review-quality-and-harness-skills.md#resolution): `skills/adversarial-review/evals/grade_benchmark.py`, `skills/code-review/evals/grade_benchmark.py` and `skills/harness-analysis/evals/grade_benchmark.py`. Retain all five earlier targets, making eight. Additional anchors are Adversarial :28,37-41, Code Review :38,48-58 and Harness :166-177. Preserve actually computed output/transcript character counts. Scope acceptance does not choose unknown representation, extend excluded helper scope or authorize execution; this ticket remains open and unblocked.

[SAG-008](../findings.md#sag-008-unmeasured-metrics-become-zero) owns the evidence. The graders supply literal zero for several unmeasured counts and times. A bounded imported-consumer check found defaults that turn omitted values into zero and arithmetic that expects numbers. Omitting fields or using null is not a verified compatible solution. No actual aggregation or viewer run established behavior.

Choose an evidence-backed representation and its exact producer/consumer scope, or explicitly defer the proposal with residual risk and a revisit trigger. Verify the relevant schema/display path before placing a repair in executable plan scope. Any change to excluded imported helpers requires a separate scope decision; do not silently include it. Preserve grading identity, observable expectations, and honest unknown evidence.

---

<!-- Resolution will be appended here. -->
