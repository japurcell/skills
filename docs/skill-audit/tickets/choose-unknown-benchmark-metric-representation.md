# Choose Unknown Benchmark Metric Representation

**Type:** grilling
**Status:** open
**Blocked By:** review-skill-authoring-and-repository-guidance.md
**Research Dir:** not applicable

## Question

How can the three included graders distinguish unmeasured metrics from measured zero while preserving supported benchmark consumers and the exclusion of imported helpers?

The delegation/discovery review has found the same producer pattern in `skills/explore/evals/grade_benchmark.py:49,59-70` and `skills/official-sources/evals/grade_benchmark.py:38,47-58`. These are proposed additional consumer targets for this existing decision, awaiting that batch's live human disposition. Keep its original three targets and prior pending status intact. Evidence accumulation does not choose a representation or authorize producer/consumer edits.

[SAG-008](../findings.md#sag-008-unmeasured-metrics-become-zero) owns the evidence. The graders supply literal zero for several unmeasured counts and times. A bounded imported-consumer check found defaults that turn omitted values into zero and arithmetic that expects numbers. Omitting fields or using null is not a verified compatible solution. No actual aggregation or viewer run established behavior.

Choose an evidence-backed representation and its exact producer/consumer scope, or explicitly defer the proposal with residual risk and a revisit trigger. Verify the relevant schema/display path before placing a repair in executable plan scope. Any change to excluded imported helpers requires a separate scope decision; do not silently include it. Preserve grading identity, observable expectations, and honest unknown evidence.

---

<!-- Resolution will be appended here. -->
