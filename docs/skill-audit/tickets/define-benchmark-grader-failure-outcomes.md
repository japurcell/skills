# Define Benchmark Grader Failure Outcomes

**Type:** grilling
**Status:** open
**Blocked By:** review-delegation-and-discovery.md
**Research Dir:** not applicable

## Question

How should the five included Explore, Official Sources, Adversarial Review, Code Review and Harness Analysis graders distinguish a gradeable failed model output from invalid run metadata/timing, an unsupported evaluation, or an empty/mislaid iteration, without falsely reporting completed grading or breaking supported consumers?

[DD-004](../findings.md#dd-004-graders-can-announce-success-without-grading-runs-and-do-not-validate-json-shape) owns the static evidence. Determine which conditions produce failed expectations in the retained grading format and which make grading incomplete; define diagnostic records, exit status, partial-run handling and consumer compatibility. Existing source can return zero with no eligible runs and assumes JSON shapes, but no observed grader or consumer execution establishes a compatible replacement contract.

Keep valid artifact predicates and grading identity. Missing required evidence must not become a pass. Coordinate unmeasured timing with [Choose Unknown Benchmark Metric Representation](choose-unknown-benchmark-metric-representation.md); do not select a null, omitted-key or zero representation here. Preserve the exclusion of imported helpers. Broader helper changes need separate scope approval.

The human accepted retention of this route on 2026-10-06 in [Review Delegation and Discovery](review-delegation-and-discovery.md#resolution), which is now closed and unblocks this ticket. Retention does not select failure outcomes or authorize execution. Exact dependent protocol changes remain outside executable plan scope until the decision and necessary compatibility evidence are settled. Both final audit and ExecPlan must expose DD-004 and its route.

The human accepted three additional targets on 2026-10-06 in [Review Quality and Harness Skills](review-quality-and-harness-skills.md#resolution): `skills/adversarial-review/evals/grade_benchmark.py`, `skills/code-review/evals/grade_benchmark.py` and `skills/harness-analysis/evals/grade_benchmark.py`. Retain `skills/explore/evals/grade_benchmark.py` and `skills/official-sources/evals/grade_benchmark.py`, for five graders. Include their recorded JSON shape, eligible-run accounting, canonical evaluation/output identity and supported configuration discovery evidence in protocol design. Preserve valid predicates and distinguish supported baselines from unsupported layouts. Exact statuses, exits, schemas and compatibility remain pending; scope acceptance authorizes no grader/consumer edits or execution.

---

<!-- Resolution will be appended here. -->
