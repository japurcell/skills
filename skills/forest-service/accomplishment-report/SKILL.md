---
name: accomplishment-report
description: Create a concise Forest Service executive accomplishment report when all work in an ExecPlan is completed, or update its existing report. Use at ExecPlan closeout and when asked to report completed work, agency alignment, and estimated AI-assisted versus human-only time and cost savings.
---

# Accomplishment Report

## Confirm scope and completion

1. Activate the `exec-plans` skill before reading the plan. Identify the exact ExecPlan from the current task or repository context; ask which plan only when the evidence leaves multiple plausible targets.
2. Read the plan, repository overview, relevant changes, and recorded acceptance evidence. Confirm every in-scope task and milestone is complete and acceptance is met. Checked boxes alone do not override unresolved tests, verification, or owner actions. If work remains, state the gap and stop report generation; do not mark the plan complete to enable reporting. Reporting itself does not create a circular completion gate.
3. Use `<plan-directory>/accomplishment-report.md`. If a report exists, read and update it in place, preserving supported human edits. Identify the plan in the report. If that filename belongs to another plan, ask how to resolve the collision before overwriting it. Do not create dated duplicates or modify implementation files.

## Establish accomplishments and alignment

Describe what the repository does, who uses it, and the problem the completed work solves. Summarize observable outcomes and verification rather than commits or implementation minutiae. Distinguish delivered capability from deployment, adoption, and measured mission impact.

Activate the `agency-priorities` skill. Map only supported outcomes to its USDA strategic goals and Forest Service priorities. Explain the causal connection, cite its source attribution, and retain the snapshot date and fiscal-year limits. Label alignment as analysis, not agency endorsement. If the skill is unavailable, identify the missing dependency and leave alignment unverified rather than inventing priorities.

## Estimate comparable time and cost

Compare the same delivered scope and quality bar, including design, implementation, review, testing, rework, and documentation. Use low/base/high scenarios with explicit assumptions and evidence for every material input. Estimates are counterfactuals, not measured savings.

- **Human-only effort:** estimate person-hours by work package using complexity, analogous work, or qualified estimates. Explain the basis; neither lines changed nor an arbitrary AI speedup multiplier is sufficient alone.
- **AI-assisted effort:** include all human prompting, oversight, review, testing, correction, and integration time. Report agent runtime separately from human person-hours and elapsed delivery time. Concurrent agents' runtimes are not elapsed time; commit timestamps are not labor records.
- **Labor rates:** use supplied fully burdened rates and currency. When absent, use clearly labeled illustrative rates with a range, not an asserted agency salary. Use consistent role rates across both scenarios.
- **AI spend:** prefer scoped billing or usage records covering all agents, retries, and tools. Otherwise estimate from recorded token categories and dated, verified provider prices. For subscriptions, state the task allocation basis and distinguish allocated cost from marginal spend; avoid charging both the same included usage and subscription allocation. Missing usage is unknown, not zero. A labeled assumed spend range is acceptable when records are absent.
- **Other costs:** include material incremental tooling or infrastructure costs on the relevant side. State exclusions and keep ongoing operational benefits separate from implementation savings.

Calculate each scenario with these definitions (sum hours times rates across roles):

```text
human_only_cost = human_only_labor + human_only_other_cost
ai_assisted_cost = assisted_human_labor + ai_spend + assisted_other_cost
net_savings = human_only_cost - ai_assisted_cost
savings_percent = 100 * net_savings / human_only_cost
human_hours_saved = human_only_person_hours - assisted_human_person_hours
```

Define low/base/high as conservative/base/optimistic **net savings** and keep assumptions coherent: conservative savings combine lower human-only effort with higher assisted costs. Show the paired inputs, not an unexplained range. When the denominator is zero, report savings percent as not applicable. Preserve negative savings. Use a calculator or executable arithmetic and round only for presentation.

If evidence cannot support even a useful assumed range, show formulas and unknown inputs; state that net savings cannot yet be estimated. Never manufacture measurements or conclude that AI paid for itself from missing data. Distinguish estimated labor capacity released from realized budget reductions.

## Write and verify

Keep the report roughly 500-900 words, with compact tables and linked evidence:

1. **Executive summary:** repository purpose, completed benefit, and the estimated net savings range with confidence and caveats.
2. **Completed work:** a few outcomes, acceptance evidence, and any rollout or impact limits.
3. **Agency alignment:** outcome, relevant goal/priority, causal rationale, and evidence or measurement gap.
4. **Time and cost comparison:** scenario inputs, human-only and assisted costs, human person-hours, AI runtime/elapsed time when known, net savings, and savings percent.
5. **Assumptions and decision implications:** provenance, missing data, sensitivity drivers, and what the estimate supports about AI-assistant spending. Recommend measurement when uncertainty could reverse the conclusion; do not turn one task into a universal productivity claim.

Date the report and link the exact plan, relevant verification artifacts, and cost evidence. Use relative links for repository files. Recheck arithmetic, units, source claims, completion status, and destination before saving. Return the saved path and the most material estimation limitation.
