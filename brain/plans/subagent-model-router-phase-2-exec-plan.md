# Phase 2: Evaluate broader model-and-effort tradeoffs for the router

This ExecPlan is a living document governed by `.agents/skills/exec-plans/SKILL.md`. Its path is `brain/plans/subagent-model-router-phase-2-exec-plan.md`. Keep Progress, milestone states, Surprises & Discoveries, Decision Log, and Outcomes & Retrospective synchronized.

## Purpose / Big Picture

Determine which additional model-and-effort configurations deserve narrowly scoped eligibility or routing preferences after Phase 1 establishes the method. The user should receive reproducible comparisons of accepted-result quality, total cost through acceptance, actual elapsed time, and repair/escalation frequency. The outcome may be a justified routing change, a rejected substitution, or an inconclusive result for each experiment.

This phase contains all comparisons proposed after the original Terra-low versus Luna-high experiment: four core comparisons, the Luna xhigh/max extension, and two second-wave comparisons. It does not silently broaden the initial experiment or install new routing defaults before evidence supports them.

The user authorized authoring this plan, moving it into `brain/plans`, and committing it on the current branch. Implementation and live trials begin only when execution is requested. [Phase 1](subagent-model-router-phase-1-exec-plan.md) owns the routing mechanism, schema, and E1. Phase 2 consumes its delivered interfaces. The current contract needed to execute this phase is restated below so historical chat is unnecessary.

## Progress

- [ ] [milestone-1] P2-T1: Verify Phase 1 readiness, refresh public hypotheses, and freeze the seven experiment definitions.
- [ ] [milestone-1] P2-T2: Confirm exact-pair runtime support and extend fixtures/rubrics for the new workload profiles.
- [ ] [milestone-2] P2-T3: Complete E2, Terra high versus Sol medium, for coding and substantive review separately.
- [ ] [milestone-2] P2-T4: Complete E3, Terra medium versus Sol low, for ordinary coding.
- [ ] [milestone-2] P2-T5: Complete E4, Sol medium versus Terra xhigh, for general work and coding separately.
- [ ] [milestone-2] P2-T6: Complete E5, Sol xhigh versus Sol max, for difficult coding and reasoning.
- [ ] [milestone-3] P2-T7: Complete E6, Terra low versus Luna xhigh/max, with an honest E1 reuse decision.
- [ ] [milestone-3] P2-T8: Complete E7, Luna low versus Luna medium, for strictly mechanical tasks.
- [ ] [milestone-3] P2-T9: Complete E8, Terra max versus Sol max, for difficult coding.
- [ ] [milestone-4] P2-T10: Integrate supported decisions and verify routing, dispatch, scope, and uncertainty behavior together.
- [ ] [milestone-4] Record the final experiment matrix, retained baselines, limits, and outcomes.

## Surprises & Discoveries

- Public results suggest both directions are worth testing: a stronger model at lower effort may win, but more effort on a cheaper model may also be preferable. There is no general rule that increasing model size or increasing effort is always better value.
- Terra high and Sol medium have virtually equal public coding scores, while Sol medium has a higher general index. A coding result cannot establish a planning or review substitution.
- Sol xhigh saves roughly 41% of the public coding-task cost relative to Sol max, with a lower coding score. This is a tradeoff to characterize, not evidence that max is redundant.
- Luna low is absent from the current catalog. E7 is an eligibility experiment, not preservation of an existing option.
- Small differences such as the Terra-max versus Sol-max coding scores and costs do not establish a meaningful winner. Those results motivate examination of different failure patterns.

## Decision Log

- 2026-11-11: Include E2-E8 in this phase. E2-E5 are the core batch; E6-E8 are the second batch. Second-batch priority does not make them optional or silently complete them.
- 2026-11-11: Reuse Phase 1's evidence schema, summarizer, dispatch procedure, and uncertainty handling. Do not build another runner or change selection semantics in this phase without reconciling both plans.
- 2026-11-11: Separate coding, review, exploration/synthesis, material planning, difficult reasoning, and mechanical-task results. Public aggregate scores only nominate experiments.
- 2026-11-11: Preserve planning defaults throughout the experiments. Even a planning result does not automatically change the preferred starting model; a separately recorded planning-specific decision and its tests are required.
- 2026-11-11: Experimental pair selection may use explicit host model/effort controls even when that pair is absent from the router catalog. This does not authorize general routing eligibility or a bypass of host permissions.

## Outcomes & Retrospective

No Phase 2 implementation or live trial has started. All milestones are open. Phase 1 readiness and exact-pair support remain prerequisites. The next action, when Phase 2 execution is requested, is P2-T1; this plan does not assert that Phase 1 is already complete.

## Context and Orientation

Work from `/Users/adam/dev/skills`, read `AGENTS.md`, and prefix shell commands with `rtk`. Edit published sources under `skills/default/subagent-model-router/`, not installed copies. Preserve unrelated worktree changes.

Existing source files are `SKILL.md`, `reference/catalog.json`, `reference/maintenance.md`, `reference/review-routing.md`, `scripts/route.py`, `scripts/test_route.py`, and `evals/evals.json` under that bundle. Phase 1 is expected to add `reference/evidence.json`, `reference/evidence-routing.md`, `evals/README.md`, `evals/model-experiments.json`, `evals/fixtures/model-routing/`, `evals/grade_model_experiments.py`, and `evals/test_grade_model_experiments.py`. Verify these deliverables and their tests before using them; do not assume that this plan's anticipated paths prove implementation exists.

The router is a pure recommendation CLI. Its caller performs live dispatch checks. The catalog owns provisional eligibility, scope restrictions, prices, and planning defaults. Evidence is matched by exact model/effort, workload, runtime, context bucket, cache state, and protocol version. Capability fixtures measure the chosen model; `evals/evals.json` measures whether the router skill is followed. They are different tests.

Full run artifacts belong in fresh `skills/default/subagent-model-router-workspace/iteration-N/eval-e2/` through `eval-e8/` directories. Do not place generated transcripts inside the published bundle. Keep compact durable summaries and decisions in the maintained evidence file and evaluation guide. Preserve immutable source/rubric/configuration hashes and raw results.

## Current Contract and Entry Gate

Phase 1 must have delivered and verified the seven behaviors: preserve mandatory task/failure floors and user choices; select explicit effort when evidence depends on it; qualify new scopes before activation; allow qualified configurations above the floor to compete while retaining planning precedence; keep token pricing separate from completion cost; compare only matching evidence with deterministic uncertainty handling; and keep evidence separate from eligibility/prices with refresh/expiry rules. Its E1 outcome may be promotion, rejection, or inconclusive after completed valid trials. An unrun E1 does not satisfy the phase boundary.

The expected public request extension is optional `evidence_context` containing `workload_id`, `runtime_id`, `context_bucket`, and `cache_state`; partial objects fail with exit 2, and unmatched/expired complete objects produce an honest provisional recommendation. Evidence-based routes use explicit effort. `completion_cost_usd` and its basis/unknowns remain separate from `estimated_cost_usd`, the token-scenario estimate. `cost_minimum_verified` remains false. Update this plan if the delivered Phase 1 interface differs, preserving its behavioral contract rather than maintaining incompatible examples.

Qualification is scoped to the actual runtime and tested task family. Unknown host settings, unavailable pairs, or absent tool permissions are named blockers, not model-quality failures. Keep `host_default` performance unresolved; do not use it to approximate an explicit experimental arm. Native subagents must receive identical prompts in fresh contexts and isolated disposable fixture directories. The current Codex V2 pattern uses `fork_turns: none` plus exact `model` and `reasoning_effort`; verify the live schema and resolved settings. A top-level CLI experiment cannot be relabeled as native-subagent evidence.

Automatic routing never selects below the effective task/failure floor. Existing exact user-model choices follow the separately documented override contract without invented catalog capability. A higher selected tier does not rewrite the original floor merely because it was available or economical. Preserve same-tier fallback behavior and reject all efforts of an entirely unavailable model.

## Experiment Definitions

All public numbers below are from the previously inspected Slopalytics snapshot dated 2026-11-10. They are motivation, not success thresholds or assumed local outcomes. Costs are benchmark task costs. Time is estimated inference time, not observed completion time. Scores are index points, not task pass probabilities. Refresh the source snapshot once before freezing the run set and record any differences without silently changing the questions.

### E2: Terra high versus Sol medium

Exact arms: `gpt-6.1-terra`/`high` and `gpt-6.1-sol`/`medium`. Public coding scores were 39.24 versus 39.22, with costs $0.410 versus $0.492, approximately 17% less for Terra. These scores are effectively tied; do not call Terra more capable on this evidence.

Test two separate profiles. `ordinary-coding-v1` covers specified multi-file changes, test updates, and bounded debugging. `substantive-review-v1` uses authored defects and realistic clean changes, measuring important defect recall and false-positive findings independently. Omit security/high-stakes review from the initial profile. The review experiment is a hypothesis beyond the chart's coding composite, so report that distinction.

Decision: whether Terra high is a justified alternative to Sol medium for either profile. A review pass cannot be inferred from implementation results. Respect current tier floors and classify the selected higher tier separately from the task's minimum.

### E3: Terra medium versus Sol low

Exact arms: `gpt-6.1-terra`/`medium` and `gpt-6.1-sol`/`low`. Public coding scores were 33.65 versus 24.42 at costs $0.265 versus $0.274. The near-price observation motivates a quality comparison, not a robust 3% savings claim.

Use `ordinary-coding-v1`, with identical fixtures and rubrics to E2 when the recorded cohort matches. Test whether additional effort on Terra improves accepted-result quality relative to lower effort on Sol. Record important failures and repair needs. Sol low is an experimental arm even if not catalog eligible; do not activate it as a side effect of running the comparison.

Decision: choose a preference only within the validated workload/runtime scope. Do not generalize that a cheaper model at more effort always wins.

### E4: Sol medium versus Terra xhigh

Exact arms: `gpt-6.1-sol`/`medium` and `gpt-6.1-terra`/`xhigh`. The general index was 46.35 versus 45.25, with Sol about 10% lower in benchmark cost and 37% lower in estimated inference time. Coding instead scored Terra higher, 40.70 versus 39.22, with Sol costing less.

Use three separately graded profiles: `ordinary-coding-v1`; `analysis-synthesis-v1` for cross-file investigation and reconciling supplied evidence; and `material-planning-v1` for scoped architecture/sequence choices in synthetic repositories. Planning tasks must have explicit constraints, known failure modes, dependency checks, and blind rubric review. Do not combine these profiles into one score.

Decision: whether workload-specific selection is warranted. Planning results may nominate a later default change, but retain existing planning precedence unless the Phase 2 integration task explicitly records a planning-specific supported change and validates all planning constraints. A general index edge of 1.1 points alone never authorizes that change.

### E5: Sol xhigh versus Sol max

Exact arms: `gpt-6.1-sol`/`xhigh` and `gpt-6.1-sol`/`max`. Public coding scores were 44.73 versus 46.80 and costs $0.832 versus $1.407. The roughly 41% lower cost at xhigh comes with a lower score; there is no strict dominance.

Use `difficult-coding-v1` and `difficult-reasoning-v1` separately. Coding includes multi-step debugging with interacting constraints and meaningful tests. Reasoning includes conflicting requirements and evidence-based diagnosis with independently established answers. Preserve Premium floors for qualifying responsibilities. Report a failure taxonomy identifying which cases max repairs that xhigh does not, not only an average.

Decision: identify scopes where xhigh reliably meets the acceptance bar and scopes where max's additional success justifies its cost. The experiment must not downgrade a user request for max or best quality, nor treat a small average gain as proof that max is unnecessary.

### E6: Expand the original comparison to Luna xhigh and max

Exact arms: `gpt-6.1-terra`/`low`, `gpt-6-luna`/`xhigh`, and `gpt-6-luna`/`max`. E1's Luna-high arm remains a contextual baseline when reuse is valid. Public coding scores for Terra low and Luna max were 20.75 versus 20.16, with costs $0.107 versus $0.200. Treat the score difference as inconclusive.

Use E1's `narrow-coding-v1` and `substantive-exploration-v1` profiles. Reuse E1 trials only if the exact fixture/rubric/protocol/runtime/model identities and context/cache strata match, evidence is still within its validity window, and predeclared overlap requirements are met. Run at least three shared anchor tasks for every reused arm alongside new arms. Reject reuse if an anchor introduces an important miss absent from that arm's prior anchor results, an acceptance check formerly passed now fails, or settings/price/usage instrumentation no longer match. Create a fresh full paired cohort in those cases; do not merge unmatched old and new results. Reused attempts remain one observation with one ID and are never counted twice. These conservative anchor checks detect reasons to reject reuse; passing them is not proof of absence of drift.

Decision: whether increasing Luna's effort is useful before a model switch for these initial selection scopes. Diagnosed failures still trigger required capability escalation before the comparison can influence a subsequent route.

### E7: Luna low versus Luna medium for mechanical work

Exact arms: `gpt-6-luna`/`low` and `gpt-6-luna`/`medium`. The public general benchmark cost at low was approximately 88% lower, with a substantial capability reduction. This says nothing about mechanical-task sufficiency by itself.

Use `mechanical-v1`: deterministic structured extraction, exact file inventories, and checklist verification against supplied facts. Include distractors, malformed inputs, missing information, and requirements to abstain rather than invent an answer. Do not include substantive judgment, code review, design, or semantic code changes. Objective graders must reject missing/extra entries and unsupported assertions.

Decision: whether Luna low qualifies for this new Fast scope. It is absent from the current catalog and remains ineligible until the specific scope qualifies. Do not turn the experiment into a general lightweight-coding recommendation.

### E8: Terra max versus Sol max for difficult coding

Exact arms: `gpt-6.1-terra`/`max` and `gpt-6.1-sol`/`max`. Public coding scores were 47.61 versus 46.80, with costs $1.370 versus $1.407, only about a 3% difference. These near ties motivate different-failure-pattern analysis, not an expected winner. Sol's higher general index does not establish the coding outcome either.

Use `difficult-coding-v1`, sharing E5's fixture family and acceptance rubric when measurements are comparable. Reuse Sol-max attempts only under the same identity, freshness, and anchor requirements as E6. Inspect missed constraints, regression failures, and verification omissions.

Decision: retain the existing eligible preference if quality and cost remain indistinguishable. Add a specialized preference only when a reproducible workload difference supports it. Do not claim broad Terra/Sol superiority from a near tie.

## Shared Protocol and Promotion Rules

Use Phase 1's frozen method and report version. Before each experiment, specify the workloads, important-error definitions, context/cache strata, allowed tools, attempt timeout, repair/rescue procedure, graders, sample count, and stop conditions in `evals/model-experiments.json`. Do not select these after seeing arm results.

For each new workload/pair, run a pilot of three distinct tasks, two repetitions per arm. Inspect raw evidence and fix only proven fixture/protocol defects under a new version. A passing pilot permits confirmation, not catalog activation. Confirmation uses 12 held-out distinct tasks per workload and three fresh repetitions per arm; use six tasks at up to 16K input tokens and six over 16K through 64K. Report each context/cache stratum separately. An experiment with three arms uses the same matched tasks/order balancing, not unrelated task sets. Do not extend the experiment to larger contexts without a separately versioned scope.

Use matched cache conditions where controllable and observable; otherwise retain `uncontrolled` as a scope limitation. Balance execution order and avoid competing concurrent runs for the same resources. Bound each attempt at 900 seconds, with one standardized repair turn only if permitted by its frozen protocol. Record first-attempt quality before repair and use the same verified rescue configuration/prompt for both arms. Important flaws cannot be hidden by eventual rescue. At most one replacement per pair is allowed for proven infrastructure failure, with all records retained; valid model failures and timeouts remain scored.

Grade against predefined acceptance checks, blind to configuration identity wherever human/model judgment is needed. Use executable checks for coding and exact extraction. For review, record important-miss and false-positive counts separately. For planning/synthesis, retain the rubric judgments and source evidence so a second reviewer can audit disputed outcomes. Reviewers must not implement repairs in the scored artifact.

Qualification requires the mandatory acceptance checks, no candidate-only important miss, and no lower observed accepted-result rate than the baseline on the held-out paired set. Report that this is finite, scoped evidence rather than a proof of general equivalence. For any claimed cost preference, require complete comparable monetary attribution and a fixed-seed, 10,000-resample task-clustered 95% paired bootstrap interval favoring lower cost per accepted result. If that interval includes zero, report cost as inconclusive. Separate observed billing from prices applied to observed usage. Missing prices or usage remain null, and reasoning tokens must not be double-counted. With no accepted results, cost per accepted result is unusable rather than free.

Claim a measured quality advantage only when the task-clustered 95% paired bootstrap interval for accepted-result-rate improvement excludes zero and no new important miss appears. When quality is indistinguishable and cost inconclusive, preserve the eligible baseline. Lower measured elapsed time changes preference only where a latency objective was registered before running. Do not adopt an arbitrary cost-tolerance percentage. A public benchmark score is never treated as a local success probability.

Each experiment ends with `qualified/preferred for named scopes`, `qualified/no preference`, `rejected`, or `inconclusive`, with separate `unrun` blockers when required trials could not execute. Completed valid inconclusive results are useful outcomes; unavailable arms or insufficient required evidence are unfinished work. Do not expand repetitions indefinitely to force a preferred result. Scope any qualification to the verified runtime/model identities and actual context/cache conditions; Phase 1's 30-day evidence expiry and immediate mismatch invalidation apply.

## Plan of Work

### Milestone 1: Freeze the expanded matrix and prove its entry conditions
Status: open
Acceptance: not met

P2-T1 depends on Phase 1 completion. Inspect its final integrated tests, E1 report, current evidence records, and runtime limitations. Compare the current worktree with these assertions, then extend `evals/model-experiments.json` with E2-E8. Refresh public source evidence and retain dated snapshots. Map every experiment to an exact question, pair(s), profile(s), and decision gate. Stop after the matrix is executable and the baseline/preference for each scope is explicit; do not change eligibility.

P2-T2 depends on P2-T1. Check current native controls and resolved settings for all new arms. Prepare the additional synthetic fixture families and graders under `evals/fixtures/model-routing/` and extend `evals/grade_model_experiments.py` only when a genuinely new result type requires it. Activate TDD before source changes and verify the public grader boundary, including missing evidence, important misses, false positives, and incomparable cohorts. Reuse identical controls from Phase 1 rather than creating a parallel framework. Record per-arm blockers independently so an unavailable arm does not erase completed independent work.

Milestone acceptance requires valid experiment definitions, tested fixtures/grading, and a recorded supported or blocked status for every arm. A blocked arm still leaves its own later experiment task open.

### Milestone 2: Complete the four core experiments
Status: open
Acceptance: not met

P2-T3, P2-T4, P2-T5, and P2-T6 depend on Milestone 1 and own E2, E3, E4, and E5 respectively. Each task owns only its fresh run directories and experiment-specific report; shared fixture, grader, and catalog files remain serialized. Each task runs its pilot, checks validity, completes the held-out stage, grades retained artifacts, and produces the scoped outcome and limitations described above.

These experiments are logically independent after fixture preparation. Schedule them without resource contention that would invalidate elapsed-time comparisons. Runtime subagent limits and cost controls apply. Do not use early results from one arm to alter another's frozen rubric.

Milestone acceptance requires valid reports for all four experiments and all their declared workload profiles. The integrated review checks whether apparent coding/general/planning differences are supported by separate outcomes. No model becomes eligible solely because its report was produced.

### Milestone 3: Complete the extension and second-wave experiments
Status: open
Acceptance: not met

P2-T7, P2-T8, and P2-T9 depend on Milestone 1. Prefer scheduling the core batch first, but this priority is not a dependency: independent second-batch work may proceed if a core arm is unavailable. P2-T7 owns E6 and requires E1 artifacts or a fresh full cohort. P2-T8 owns E7 and has no empirical dependency on a core comparison. P2-T9 owns E8; it additionally depends on P2-T6 only if reusing that task's Sol-max observations. Reuse must pass the explicit checks. If those checks fail or P2-T6 is unavailable, run fresh paired trials instead of blocking on historical compatibility.

Each task follows the same pilot/confirmation/report boundary. Do not make E7 optional because Luna low is currently absent from the catalog, and do not force E8 to distinguish models when the observations remain a near tie.

Milestone acceptance requires completed valid outcomes for E6-E8 and a ledger showing which attempts were reused, which anchor checks permitted reuse, and that no observation was counted twice.

### Milestone 4: Integrate only supported routing decisions
Status: open
Acceptance: not met

P2-T10 depends on Milestones 2 and 3. Review all seven outcome reports and update `reference/evidence.json` with compact provenance, qualification, uncertainty, and preference records. Add or adjust `qualification_ids` and scopes in `reference/catalog.json` only when evidence supports them. Keep unsupported pairs out of automatic selection. Update `reference/maintenance.md`, `reference/evidence-routing.md`, `evals/README.md`, and skill examples only where current supported behavior changes.

For material planning, preserve existing starting-model precedence by default. A change requires an explicit planning-specific decision in this milestone, supported by E4's planning results, that states the exact affected profile and preserves risk floors and explicit user constraints. It must have public-CLI and instruction-following proof. If evidence is insufficient, record that planning defaults remain unchanged; do not infer permission from a coding win.

Run integrated router and grader tests plus affected live skill instruction-following scenarios against preserved and updated snapshots. Verify every promoted configuration is selected only in its matched context, required effort is explicit, expired/mismatched records fall back honestly, and security/failure floors cannot be bypassed. Record unchanged baselines where experiments rejected or failed to distinguish candidates.

Milestone acceptance requires an auditable E2-E8 outcome matrix, integrated checks, and preserved recovery paths. No installation, blanket model-tier rewrite, provider migration, or unrelated skill edits are part of this milestone.

## Concrete Steps

Next unfinished action, owned by the Phase 2 implementer when execution is requested: P2-T1. From `/Users/adam/dev/skills`, verify Phase 1's delivered state before creating any run directory:

    rtk git status --short
    rtk read skills/default/subagent-model-router/evals/README.md
    rtk proxy python3 skills/default/subagent-model-router/scripts/test_route.py
    rtk proxy python3 skills/default/subagent-model-router/evals/test_grade_model_experiments.py

If Phase 1's expected files are absent, return to the Phase 1 entry gate and record the exact missing prerequisite. Do not write placeholder results or mark this phase started solely because a plan exists.

After each experiment, run the delivered summary interface on its immutable manifest and a fresh output directory:

    rtk proxy python3 skills/default/subagent-model-router/evals/grade_model_experiments.py --manifest <experiment-manifest.json> --output <fresh-report-directory>

The manifest must identify a specific E2-E8 experiment, participants, frozen protocol/rubric, runtime/model settings, attempts, exclusions, and required artifacts. Exit 0 means a structurally valid report, not a model win. Exit 2 means invalid/missing evidence. Inspect reports and raw failures before recording completion.

After integrating supported source changes:

    rtk proxy python3 skills/default/subagent-model-router/scripts/test_route.py
    rtk proxy python3 skills/default/subagent-model-router/evals/test_grade_model_experiments.py
    rtk proxy env PYTHONPATH=scripts/vendor python3 skills/default/skill-creator/scripts/quick_validate.py skills/default/subagent-model-router
    rtk git diff --check

Keep immutable baseline and changed-skill snapshots for instruction-following eval runs. They do not replace native model-capability trials. Run the registry suite if changing `scripts/test-all.py`; do not expand to unrelated full-repository checks without a relevant change or failure.

## Validation and Acceptance

All verification here is planned. Phase 2 is complete only when each of E2-E8 has a completed valid report, including negative or inconclusive outcomes, and the integrated router reflects only supported changes. An unrun experiment remains unfinished with its blocker recorded. Model availability, lack of billing telemetry, and missing grading evidence must be distinguishable from a valid failed task.

The final report must answer: which profile each experiment tested; which exact runtime/model settings were observed; whether quality met its bar; important misses and false positives; first-attempt and eventual acceptance; repair/rescue frequency; total cost basis and unknowns; actual elapsed-time definition; confidence/uncertainty; the selected or retained baseline; and the exact scope of any catalog change. It must not claim a universal model ranking.

Include direct CLI acceptance scenarios for a qualified higher-tier option beating a provisional lower-tier baseline in a matching cohort, a rejected or expired record failing to activate a scope, explicit model/effort constraints, preserved planning precedence, and a mandatory Premium escalation refusing a Standard-only candidate. Use synthetic test values rather than claiming public benchmark values are local measurements.

## Idempotence and Recovery

Use fresh iteration/run IDs and retain every failed or timed-out attempt. Reuse existing evidence only with complete identity/freshness/anchor checks and explicit ledger entries. Re-running a summarizer into a fresh directory must reproduce the same conclusions from the same manifest; it must not launch models, change fixture outputs, or update catalog eligibility.

When a runtime version, model snapshot, fixture, or rubric changes, start a new cohort. If a source comparison was wrong, correct the hypothesis and record the correction before more trials, without rewriting completed raw outcomes. If a promoted scope later loses support, disable only the affected comparison/qualification, restore the preserved eligible baseline, and retain the withdrawal record. Never weaken valid acceptance checks, reset unrelated work, modify installed skills, or erase evidence to recover.

## Artifacts and Notes

Public source pointers: [selected chart](https://slopalytics.com/?models=gpt-6-1-sol,gpt-6-1-terra,gpt-6-luna), [inspected November 10 bundle](https://slopalytics.com/assets/index-Cx6N5DX8.js), [Terra high](https://artificialanalysis.ai/models/gpt-6-1-terra-high), [Terra medium](https://artificialanalysis.ai/models/gpt-6-1-terra-medium), [Terra xhigh](https://artificialanalysis.ai/models/gpt-6-1-terra-xhigh), [Sol low](https://artificialanalysis.ai/models/gpt-6-1-sol-low), [Sol medium](https://artificialanalysis.ai/models/gpt-6-1-sol-medium), [Sol xhigh](https://artificialanalysis.ai/models/gpt-6-1-sol-xhigh), [Sol max](https://artificialanalysis.ai/models/gpt-6-1-sol), and [Luna low](https://artificialanalysis.ai/models/gpt-6-luna-low). Public pages may change; retain a dated source snapshot and methodology/version with the experiment definitions.

The plans are temporary. Durable methodology and current supported scope belong in the maintained evaluation and routing references. Preserve compact decisions there before archiving these plans. Run the applicable reflection workflow after implementation, recording only durable findings and leaving task status in the active plans.
