# Success Criteria

**Type:** grilling
**Status:** closed
**Blocked By:** none
**Research Dir:** not applicable

## Question

What observable results prove that autonomous context management improves relevant context and knowledge freshness without losing authoritative guidance?

Choose the required correctness, completion, recoverability, latency, and context-size criteria; how to measure the existing baseline; and which failures make the first version unacceptable. Establish priority when context savings conflict with necessary guidance. This ticket defines the quality bar, not the pilot implementation.

Use [Reference Evidence](reference-evidence.md) when choosing longitudinal checks: retained context can collapse or degrade through harmful updates even when individual maintenance steps complete.

---

## Resolution

The user confirms this acceptance contract on 2026-09-29 after accepting the recommendations and reviewing how the quality gates are measured.

### Priority and completion

Preserve authoritative guidance and task quality before optimizing context volume. Freshness and context savings are required results; a failed performance target requires improving the design, never omitting required guidance. Complete required maintenance before normal task completion, including a verified no-change result when appropriate. After an interruption, pending work must be detectable and recovered at the next eligible opportunity. A shutdown hook is not proof of completion. Lifecycle boundaries and the meaning of an eligible opportunity remain decisions for Lifecycle Guarantees.

### Correctness, freshness, and recovery

All predefined critical checks must pass on every supported provider surface, including after repeated learning and pruning cycles. This is a tested-case gate, not a claim that all possible failures are covered.

- Guidance checks define expected instructions independently before a run, verify delivery before the governed action, and assert compliant behavior in the resulting artifacts. Reading alone is insufficient.
- Freshness checks introduce known authoritative source changes, complete maintenance, then verify that a fresh session retrieves and applies the corrected knowledge.
- Maintenance checks exercise additions, corrections, reorganization, and pruning. Verify supporting evidence, valid links, and retention of authoritative guidance and important counterexamples.
- Recovery checks interrupt different maintenance stages, then verify pending-work detection, completion or restoration of a valid prior state, and preservation of unrelated user edits. Include recovery from a harmful update or prune.
- Compare task results with the current workflow. Investigate every baseline success that becomes a failure; no unresolved regression caused by the context system may remain.

Lost authoritative guidance, harmful unsupported updates, silent unfinished maintenance, unrecoverable changes, and broken knowledge links block acceptance. Deterministic assertions and observable artifacts establish mechanical checks. Independent human review establishes semantic correctness where assertions are insufficient. Agent self-reports alone do not establish success.

### Context and latency measurements

Count repository instructions, knowledge content, routing guidance, and context-management prompts delivered during a task and its attributable maintenance, including native loading, dynamic reads, repeated deliveries, and maintenance-agent work. Measure delivered guidance content, not total billed model-input tokens. Exclude identical user task text, task source code, unrelated tool output, and unchanged provider/system scaffolding. Do not hide work outside the measurement window. Record tokenization and delivery coverage; an unobserved delivery is a measurement gap, not zero. A token-count proxy must be documented and validated before it establishes a pass.

For each supported surface, compare the candidate with the current workflow using the same tasks, model and provider configuration, equivalent active knowledge, and a fixed measurement method. The candidate median guidance tokens per task must be at most 75% of baseline; its 95th percentile must be no higher than baseline.

Measure additional blocking retrieval time across each task, rather than averaging individual lookups. Its 95th percentile must be at most 5 seconds. Measure total elapsed task duration through required maintenance completion for both workflows; the candidate 95th percentile must be at most 120% of baseline. Record timing boundaries and attribute triggered learning and pruning work to the measured workload.

### Evidence and remaining scope

Freeze evaluation inputs and expected checks before comparing results. Retain paired outcomes, guidance-delivery traces, changes, checks, timing, and independent semantic review. Evaluate each supported surface separately; aggregate results cannot conceal a failing surface. Repeat learning and pruning cycles to test retained knowledge and future-session use, rather than judging only individual maintenance steps.

Baseline values have not been measured. The percentages and latency limits are agreed product targets, not claims established by the research. Adoption and Validation Contract selects concrete pilot cases, repetitions, instrumentation, and provider versions. Other tickets determine lifecycle boundaries, evidence policy, representation, scheduling, and recovery mechanisms. This ticket sets their observable acceptance bar without implementing them.
