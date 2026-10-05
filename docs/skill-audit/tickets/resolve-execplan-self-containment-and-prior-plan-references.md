# Resolve ExecPlan Self-containment and Prior-plan References

**Type:** grilling
**Status:** open
**Blocked By:** review-repository-local-workflows.md
**Research Dir:** not applicable

## Question

What role may a checked-in predecessor plan play in an ExecPlan that must support a novice restart from the current single file?

The repository-local `exec-plans` entry requires single-file self-containment and restart-only knowledge at `SKILL.md:8,18,26`, permits incorporating a checked-in predecessor by reference at `:34`, and tells the skeleton reader not to refer to prior plans at `:129`. These instructions do not define whether predecessor links can supply required executable knowledge or serve only as optional historical/evidence context. The repository-local review owns the static evidence; no broken restart was observed.

Choose and document the intended output contract before aligning the two clauses. Preserve the plan-before-code gate, novice guidance, living sections, progress/milestone synchronization, standalone-file envelope, and authorized implementation scope. Do not infer approval from the audit's separate requirement for a self-contained final implementation plan, or silently remove a prior-plan exception in an authoring cleanup.

The batch may retain and route this question without choosing its answer. Dependent authoring work stays pending until the decision is resolved, or an explicit deferral identifies independent scope, remaining risk, affected work, and revisit trigger. Both final audit and ExecPlan must retain the unresolved finding ID and this route. No plan execution or skill edit is authorized by this ticket.

---

<!-- Resolution will be appended here. -->
