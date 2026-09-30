# Maintenance Scheduling and Pruning

**Type:** grilling
**Status:** closed
**Blocked By:** knowledge-evidence-policy.md, lifecycle-guarantees.md
**Research Dir:** not applicable

## Question

When is maintenance due, and how does it apply the agreed eligibility rules for refresh, consolidation, relocation, and pruning?

Define scheduling signals, maintenance scope, stale-knowledge detection, retention rules, and reversible change records. Decide how maintenance proceeds when no agent session is active or no semantic changes are needed. Apply the closed [Knowledge Evidence Policy](knowledge-evidence-policy.md), including compact proportional evidence, preserved policy meaning, and inactivity as a review signal only. Avoid depending on a voluntary periodic reminder.

Preserve the required work-session learning/refresh and verified no-change behavior in [Lifecycle Guarantees](lifecycle-guarantees.md). Select periodic consolidation/pruning schedules and how due work joins the automatic lifecycle. Next-event recovery is already agreed; decide separately whether periodic maintenance needs validated execution when no session is active. Do not assume a shutdown hook or a voluntary reminder executes semantic maintenance.

Apply [Context Organization and Skill Boundary](context-organization-and-skill-boundary.md): dream performs semantic pruning and maintenance in an eligible foreground agent through the cooperative agent-brain skill/CLI. Distinguish recording due work while idle from executing it. The selected core requires no daemon, maintenance subagent, or independent model job; any additional autonomous execution path needs an explicit scope decision. Select retention for versioned candidates and ignored operational records without losing unfinished obligations or treating inactivity as deletion authority.

---

## Resolution

The user confirms this contract on 2026-09-29 after accepting Q1-Q6 and the Q7 final shared-understanding confirmation. This ticket defines scheduling and retention; it does not implement or activate maintenance.

### Execution timing

Detect due dream work at supported startup, resume, and task events. Execute it automatically in the eligible foreground agent before work-session completion. While idle, leave work pending until the next eligible event; do not launch background model jobs. Preserve the existing timing for required learning, affected-knowledge refresh, and urgent factual repair before dependent work.

### Review signals and eligibility

Put knowledge into the review queue when sources, versions, or applicability change; conflicts or broken references appear; duplication is suspected; or unresolved candidates need evaluation. Age and inactivity may prioritize periodic review. Signals initiate investigation, not automatic retirement. Pruning still requires evidence of error, obsolescence, or complete redundancy under the closed Knowledge Evidence Policy.

### Periodic cadence

Routine dream becomes due every seven calendar days by default, configurable per repository. Coalesce missed intervals into one pending review rather than replaying a review for every missed interval. Urgent repair retains its existing timing.

Reset the periodic clock only after the review cycle is verified complete. An individual completed batch does not reset the cycle clock or erase unfinished coverage.

### Review scope

Run cheap structural checks across mapped knowledge, then perform focused semantic review of flagged units and required references, relevant unresolved candidates, and a rotating portion of the remaining knowledge. Quiet areas must eventually receive review. Track coverage and unfinished work rather than rereading the entire KB every time. A verified no-change result applies only to the reviewed scope.

### Bounded progress and verified outcomes

Assign one bounded routine batch at each eligible work-session completion while a review cycle remains due. Keep remaining coverage pending and ensure quiet areas make progress despite new review signals. [Adoption and Validation Contract](adoption-and-validation-contract.md) selects the concrete batch limit against the accepted guidance-token and timing targets.

Each assigned batch must complete its required checks before successful work-session completion. Verify a scoped no-change result when no eligible semantic change is needed; do not invent an addition or prune. Routine cycle coverage outside the assigned batch remains explicitly pending for a later eligible work session. An unfinished required batch leaves the work session explicitly incomplete, preserving its obligation for recovery. Urgent repair cannot wait for routine batching.

Review completion and factual verification are distinct. Apply [Knowledge Evidence Policy](knowledge-evidence-policy.md) to source changes, uncertainty, and inaccessible evidence. Do not claim unavailable facts are verified or treat missing access as evidence for pruning. Preserve the closed retrieval and lifecycle rules for affected dependent work.

### Retention and reversible change records

Remove completed, unreferenced operational records 30 days after closure. Retain them longer when recovery or pilot validation still requires them. Rebuildable caches may be regenerated, but cache cleanup must not discard pending obligations or their evidence.

Retain pending obligations, unresolved candidates, and active recovery records until resolved. Keep authoritative knowledge, required evidence, and reversible history. Remove resolved candidates from the active queue only after recording their disposition; preserve version history. Age alone never authorizes deletion of established knowledge, pending work, or unresolved candidates.

Use the compact colocated evidence and versioned history selected in [Context Organization and Skill Boundary](context-organization-and-skill-boundary.md). A coherent correction, relocation, consolidation, or prune retains the attributable change rationale, supporting evidence, and affected identities/references needed to restore prior guidance. Preserve policy meaning, useful qualifications, and required links. Routine maintenance does not require archived full transcripts or a separate reproduction for every low-risk tip.

### Remaining decisions and validation

[Failure and Concurrency Contract](failure-and-concurrency-contract.md) selects concrete ownership, invocation identity, deduplication, reentry, atomic publication, bounded retries, and recovery mechanisms for due cycles and assigned batches. [Adoption and Validation Contract](adoption-and-validation-contract.md) selects configuration details, initialization, concrete batch limits, provider certification, pilot workloads, usage collection, and rollback checks.

Preserve all quality, policy, completion, recovery, delivered-guidance, timing, and usage-visibility contracts. Attribute dream work to the measured workload; routine batching does not hide maintenance cost. This decision performs no implementation, installation, live provider probe, or acceptance measurement.
