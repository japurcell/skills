# Route routine subagent work through lower-cost Luna configurations

This ExecPlan is a living document. Keep `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` current while executing it. Follow `.agents/skills/exec-plans/SKILL.md`. This plan was created before implementation; all milestones remain open.

## Purpose / Big Picture

The subagent router currently chooses `gpt-5.6-terra` for broad Standard work, even when `gpt-5.6-luna` at maximum reasoning effort may complete routine work at lower cost. After this change, a user can request a routine, testable implementation or reproducible bug fix and receive an explicit `model` and `reasoning_effort` route that favors Luna where the runtime supports it. Ordinary code review can use Luna at maximum effort only after representative evaluations show no missed material findings, comparable feedback, and lower observed total cost. Security-sensitive and subtle-contract reviews retain their higher capability requirements. A human can verify the behavior through the router evaluation cases and their decision JSON files.

## Progress

- [ ] [milestone-1] Confirm runtime support and collect comparable task outcomes and billed usage for Luna at `max`, current routine routes, and current ordinary review routes. Save reproducible evidence beside this plan.
- [ ] [milestone-2] Add explicit `(model, reasoning_effort)` routing and make Luna at `max` the supported-runtime default for routine, testable implementation and reproducible debugging. This depends on milestone 1's runtime findings.
- [ ] [milestone-3] Evaluate ordinary code review on completed repository diffs with known outcomes. Promote Luna at `max` only if the agreed quality and total-cost gate passes. This depends on milestone 1's evidence format and may proceed alongside milestone 2.
- [ ] [milestone-4] Update the review route, grader, evaluation prompts, and related references according to milestone 3's result; run all targeted validation and the mandatory agent-doc pass. This depends on milestones 2 and 3.

## Surprises & Discoveries

At plan creation, `skills/subagent-model-router/reference/model-catalog.md` assigns Luna only to Fast but names Terra the general Standard default. `skills/subagent-model-router/SKILL.md` does not return a reasoning-effort setting. Existing `evals/evals.json` and `evals/grade_benchmark.py` test routing compliance, not model task quality. Record new runtime, evaluation, or cost surprises here with concise evidence as work proceeds.

## Decision Log

- Decision: Optimize expected total cost of successful completion, including model usage, retries, and verification, rather than enforcing a fixed per-task spending cap. Rationale: A cheap first attempt is not a saving if it causes expensive retries. Date/Author: 2026-09-22, user and Codex.
- Decision: Prefer GPT-5.6 Luna at `max` for routine, testable implementation and reproducible debugging where the runtime supports that effort and usage can be estimated. Rationale: The user observed better capability than the current Fast label implies; the route still needs explicit verification. Date/Author: 2026-09-22, user and Codex.
- Decision: Express model and effort as a pair; never silently turn Luna at `max` into Luna at default effort. If `max` is unavailable, use Luna at `xhigh` only after that pair has passed relevant evaluations; otherwise use the current Standard fallback. Rationale: The effort setting is material to capability. Date/Author: 2026-09-22, user and Codex.
- Decision: Gate Luna's ordinary-review default on evaluations of recent completed repository work. Require no missed material findings versus the current route, comparable useful feedback, and lower observed total cost. If evidence is inconclusive, keep the current review route. Rationale: Existing router tests establish tier compliance only. Date/Author: 2026-09-22, user and Codex.
- Decision: Keep security, sensitive data, subtle contracts, prior missed issues, and similarly high-risk review on existing Premium or otherwise justified routes. Escalate routine work for a substantive reasoning miss, not for missing dependencies or other environment failures. Date/Author: 2026-09-22, user and Codex.

## Outcomes & Retrospective

Plan authored. No skill implementation, benchmark, branch change, or commit has started. At each milestone, record observed routing behavior, measured cost, remaining gaps, and any justified change to the design.

## Context and Orientation

Work from repository root `/Users/adam/dev/skills`. `skills/subagent-model-router/SKILL.md` sets agent-type floors, routing workflow, and decision output. `skills/subagent-model-router/reference/model-catalog.md` owns tier membership and the single task-default table. `reference/review-routing.md`, `reference/escalation-policy.md`, and `reference/patterns.md` use those named defaults. `reference/pricing.md` records Copilot token rates. `skills/subagent-model-router/evals/evals.json` provides routing scenarios, while `evals/grade_benchmark.py` parses the catalog's `## Fast`, `## Standard`, and `## Premium` tables and grades `outputs/decision.json`; `evals/test_grade_benchmark.py` tests that grader. Preserve those table headings unless the parser and its tests change together.

Here, a **route** is the selected agent type, capability tier, model, and reasoning effort. A **material finding** is a correctness, security, or contract issue that a reviewer would need to fix before accepting a change; formatting advice alone does not count. **Total cost** means observed billable model usage plus usage from retries and verification in the same runtime. At Copilot's published rates for inputs at or below 200K tokens, Luna input/output rates are $0.20/$1.20 per million tokens and Terra's are $2.00/$12.00; cache writes also differ. Maximum effort can increase billed reasoning output, so the 10-to-one rate ratio is not a measured task-cost ratio. GitHub's current pricing is at https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing. OpenAI documents Luna's `max` effort at https://developers.openai.com/api/docs/models/gpt-5.6-luna. GitHub documents configurable reasoning in some Copilot surfaces at https://docs.github.com/en/copilot/reference/ai-models/supported-models, but runtime support for Luna at `max` must be confirmed before routing.

The working tree had staged edits to `docs/ideas.md` and the router skill/catalog/pricing at plan creation. Treat them as existing work. Inspect status and diffs before branching, copying, staging, or committing; preserve unrelated changes. Future implementation should use a topic branch and the implementer worktree flow required by `/Users/adam/.agents/skills/execplan-implement/SKILL.md`. Keep implementer ownership separate: evaluation evidence and runtime checks; router/catalog/reference edits; grader/eval edits. Agents editing source code must activate `tdd`, and commits must follow that skill's `references/message.md`.

## Plan of Work

### Milestone 1: Establish capability and cost evidence

Status: open  
Acceptance: not met

Inspect available runtime model IDs and effort controls without assuming a provider's API setting is supported by every Copilot surface. Save a small evaluation note beside this plan with exact runtime, model ID, effort, task, baseline model, billable usage or credits, retries, verification, outcome, and limitations. Select recent completed repository tasks with known fixes: routine implementation, a reproducible bug, and ordinary review diffs. Compare each route on the same task and input, in separate disposable worktrees when code may change. Record whether the runtime actually honored `max`; do not infer it from a prompt. If `xhigh` is to be a fallback, test it separately. This milestone is complete when another contributor can reproduce the selected cases and distinguish measured cost from an estimate. Do not install dependencies to run evaluations without approval.

### Milestone 2: Route routine coding and debugging with explicit effort

Status: open  
Acceptance: not met

Edit `skills/subagent-model-router/SKILL.md` to require an explicit `reasoning_effort` output and to compare feasible `(model, effort)` pairs before accepting a task default. Make routine, testable implementation (including connected files) and reproducible debugging eligible for Luna at `max` when milestone 1 confirms runtime support. Keep deterministic test/build/search work cheap without forcing maximum effort. Edit `reference/model-catalog.md` so its task-default table expresses the Luna pair without copying preferred IDs throughout references. Preserve the Fast/Standard/Premium distinction as task capability requirements; document exactly why a validated Luna-at-`max` pair can satisfy routine Standard work, while Luna at an unspecified effort cannot. Update `reference/escalation-policy.md` and `reference/patterns.md` only where needed for reasoning misses and missing-effort fallback. A targeted routing example should choose Luna at `max` for a routine, verifiable connected edit and a reproducible bug, but retain escalation for ambiguous contracts and avoid escalation on an environment failure.

### Milestone 3: Gate ordinary review on measured results

Status: open  
Acceptance: not met

Use completed repository diffs with known outcomes, including ordinary multi-file reviews with material findings and clean diffs. Compare Luna at `max` against the existing budget-review and broader-review defaults under the same scope. Record issue detection, unsupported claims, useful feedback, billable usage or credits, retries, and verification. Do not declare a pass from router-decision tests. Pass only if Luna misses no material finding found by the current route or established ground truth, gives comparable useful feedback, and costs less in observed total across representative cases. If the runtime cannot expose or confirm `max`, lacks usable cost data, or cases are too weak to support the comparison, mark the gate inconclusive and retain existing ordinary-review defaults. High-risk review is outside this promotion gate.

### Milestone 4: Synchronize routing references and validation

Status: open  
Acceptance: not met

If milestone 3 passes, update `reference/review-routing.md` and the catalog's review default to select Luna at `max` for ordinary review, including clear-scope multi-file diffs. If it does not pass, keep existing review defaults and state the unmet gate in the reference. In either case, update `evals/evals.json`, `evals/grade_benchmark.py`, and `evals/test_grade_benchmark.py` so decisions include effort, valid model-effort pairs are checked, unsupported or omitted effort fails where material, and high-risk review remains Premium. Avoid a parser that accepts Luna solely from tier membership regardless of effort. Update `reference/pricing.md` only for verified pricing facts; describe actual task cost as measured rather than assuming a fixed effort surcharge. Confirm every named default and local link remains valid. Run the skill validator and targeted grader tests, then the formal `update-agent-docs` pass. Follow `okf-authoring` only if that pass changes `.agents/instructions/` or `.agents/memory/` Markdown.

## Concrete Steps

Run commands from `/Users/adam/dev/skills`. Use `rtk` for shell commands by default, per `AGENTS.md`; use a raw command only when `rtk` changes required behavior. Before implementation, inspect `rtk git status --short` and `rtk git diff --cached -- skills/subagent-model-router docs/ideas.md` so existing staged changes remain intact. Read `.agents/memory/INDEX.md`, `.agents/memory/ARCHITECTURE.md`, `.agents/memory/CONVENTIONS.md`, `.agents/instructions/skills.md`, and matching skill known-issue/testing guidance before editing. For source edits, follow `skills/create-skill/SKILL.md` and the `tdd` skill. Use the explicit task graph in `Progress` when assigning isolated implementer worktrees.

For router validation, run:

    rtk test env PYTHONPATH=scripts/vendor python3 skills/skill-creator/scripts/quick_validate.py skills/subagent-model-router
    rtk test python3 -m unittest discover -s skills/subagent-model-router/evals -p 'test_*.py'
    rtk test python3 -m py_compile skills/subagent-model-router/evals/grade_benchmark.py
    rtk git diff --check

Expect `Skill is valid!`, all targeted tests to pass, successful compilation, and no whitespace errors. The current test suite has nine tests; update the expected count after adding pair and fallback tests. If live benchmark artifacts exist in a new `skills/subagent-model-router-workspace/iteration-N/`, grade that iteration with `rtk test python3 skills/subagent-model-router/evals/grade_benchmark.py skills/subagent-model-router-workspace/iteration-N/`. Keep generated run output in that workspace, not in the skill source. Inspect the decision JSON for each representative scenario and the evaluation note for task quality and cost. Re-run a gate only when a change or unresolved risk justifies it.

## Validation and Acceptance

Milestone 2 is accepted when a routine connected implementation and reproducible bug case produce `gpt-5.6-luna` with `reasoning_effort: max` on a confirmed runtime; unsupported `max` leads to an evaluated `xhigh` route or an explicit Standard fallback. A missing dependency remains an environment diagnosis. Security-sensitive review still routes to Premium. Milestone 3 is accepted only with recorded comparative outcomes and billable usage; absence of evidence means the review default stays unchanged. Milestone 4 is accepted when grader tests reject a Luna route with omitted or unsupported effort, the skill validator passes, reference links resolve, and the final diff touches only intended files plus any required synchronized agent docs. No project build is applicable to this Markdown/Python skill; targeted Python validation replaces it.

## Idempotence and Recovery

Evaluation runs should use separate worktrees and uniquely named output directories so reruns do not overwrite evidence. Preserve pre-existing staged changes; never reset or discard them. If live runtime or billing data is unavailable, record the exact gap, complete independently verifiable routine routing work where support is confirmed, and leave review promotion gated. If a routing change breaks grader tests, keep the failing test, repair the parser or policy, and rerun the targeted suite. Do not install dependencies or weaken tests to obtain a pass.

## Artifacts and Notes

At creation, the decisive source lines were the Terra general-work default in `reference/model-catalog.md`, the absence of effort in `SKILL.md` output, and review-routing's use of the general-work default for broad reviews. Existing router tests passed in the preceding catalog-update session, but they do not measure Luna's task quality. Add compact transcripts, measured usage, and evaluation conclusions here as milestones finish.

## Interfaces and Dependencies

The route's user-facing fields remain `agent_type`, `tier` (or the evaluation fixture's `model_tier`), `model`, reason/justification, escalation trigger, and fallback; add `reasoning_effort` with an explicit supported value such as `max` or `xhigh` when that value is material. Keep the runtime's exact model ID separate from the catalog's routing shorthand. `evals/grade_benchmark.py` must recognize permitted model-effort combinations without treating a model name alone as proof of capability. No new package dependency, database change, or public service API is needed.

Plan creation note, 2026-09-22: Created this plan to capture the user's confirmed cost objective, Luna-at-max preference, runtime fallback, and evidence gate before any implementation. No prior plan existed for this effort.
