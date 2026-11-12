# Phase 1: Establish evidence-based routing and evaluate Terra low against Luna high

This ExecPlan is a living document governed by `.agents/skills/exec-plans/SKILL.md`. Its path is `brain/plans/subagent-model-router-phase-1-exec-plan.md`. Keep Progress, milestone states, Surprises & Discoveries, Decision Log, and Outcomes & Retrospective synchronized.

## Purpose / Big Picture

Make the subagent model router choose reproducible model-and-reasoning-effort configurations without weakening task requirements. A caller should be able to distinguish a provisional catalog recommendation, a recommendation supported by comparable local results, and an explicit user model choice. Token-price calculations must remain distinct from measured or estimated completion cost.

Phase 1 delivers all seven agreed recommendations, plus experiment E1 comparing `gpt-6.1-terra` at `low` with `gpt-6-luna` at `high`. It establishes the evaluation procedure reused by [Phase 2](subagent-model-router-phase-2-exec-plan.md). A completed experiment may support promotion, rejection, or an inconclusive finding; a successful implementation does not require Terra to win.

The user authorized authoring these plans, moving them into `brain/plans`, and committing them on the current branch. Implementation, live model experiments, installation, and publication have not been started. The next implementation owner follows this plan when the user starts Phase 1. Do not infer runtime permission or model availability from this document.

## Progress

- [ ] [milestone-1] P1-T1: Record the baseline and freeze the policy, public interfaces, and experimental protocol.
- [ ] [milestone-1] P1-T2: Prove that the selected runtime exposes exact model/effort control and the required evidence; record any missing measurements.
- [ ] [milestone-2] P1-T3: Implement evidence records and workload-specific qualification through the existing public router CLI.
- [ ] [milestone-2] P1-T4: Implement effort-dependent dispatch recommendations and candidate selection above the required floor.
- [ ] [milestone-2] Verify the integrated CLI against the seven policy requirements and negative cases.
- [ ] [milestone-3] P1-T5: Build and verify the bounded experiment fixtures, grading, and result summary.
- [ ] [milestone-3] P1-T6: Run E1's pilot and confirmation stages and record its outcome separately for each workload.
- [ ] [milestone-4] P1-T7: Publish only supported qualification/preference records and reconcile runtime instructions and evaluations.
- [ ] [milestone-4] Verify the integrated bundle, record evidence and limitations, and establish Phase 2 readiness.

## Surprises & Discoveries

- The current router returns Luna with `host_default` and null effort for ordinary coding, but Luna `high` for substantive review, when restricted to the three chart families. This was observed through the public CLI during the preceding investigation. These are catalog recommendations, not evidence of a live child using either configuration.
- `catalog.json` includes Terra `medium` in Standard and Terra `high` in Premium. It includes Luna `medium` in Fast and `high+` in Standard. It has neither Terra `low` nor Luna `low` as selectable candidates. An experiment configuration is not automatically a catalog entry.
- `route.py` selects the lowest eligible tier before ranking candidates. Planning additionally has a restricted pool and a preferred starting model. Merely adding benchmark scores would not change either gate.
- The chart's time metric is estimated inference time. It is not measured time to complete, verify, and accept a delegated assignment. Raw benchmark cost is not cost per accepted result.
- The repository's existing `evals/evals.json` evaluates router instruction-following, not the capability of the models being routed. Both kinds of evaluation are needed and must remain separate.
- Some existing evaluation prose names an effort while also claiming `host_default`. Reconcile these cases against the intended contract; do not preserve contradictory expected outputs.

## Decision Log

- 2026-11-11: Put the seven routing recommendations and only E1 in Phase 1. Phase 2 owns the remaining seven comparisons, including the Luna xhigh/max extension. This keeps the first empirical change narrow while delivering a reusable method.
- 2026-11-11: Keep automatic task/failure floors and the existing exact-user-model override contract. A user-selected out-of-catalog model may follow the existing host-verification path, but the router must not invent catalog qualification for it.
- 2026-11-11: Preserve planning's restricted pool and preferred starting configuration in Phase 1. Cross-tier competition applies within the permitted pool and cannot silently replace planning policy.
- 2026-11-11: Keep public benchmark evidence advisory. New candidate scopes require local evidence before activation. Lack of dollar measurements is an explicit unknown, not a zero cost or a reason to substitute unrelated API prices.
- 2026-11-11: Reuse native subagent dispatch for capability experiments. A top-level CLI run does not by itself validate a subagent runtime.
- 2026-11-11: Prefer a small evidence file and deterministic offline summarizer to a live benchmark service, automatic scraper, or new provider orchestration framework.

## Outcomes & Retrospective

Planning is complete; implementation and experiments have not started. No routing behavior, skill source, installed skill, or model eligibility has changed. All implementation acceptance remains unmet. The next action is P1-T1 when Phase 1 implementation is requested.

## Context and Orientation

Work from `/Users/adam/dev/skills`. Published source is `skills/default/subagent-model-router/`; installed copies under `/Users/adam/.agents/skills/` are not the edit target. Read the root `AGENTS.md` and relevant brain guidance before implementation. Shell commands use `rtk`, using `rtk proxy` when unfiltered command behavior is needed.

The source bundle currently contains:

- `skills/default/subagent-model-router/SKILL.md`: task classification, routing and dispatch instructions.
- `skills/default/subagent-model-router/reference/catalog.json`: provisional model-effort candidates, capability tiers, restrictions, Copilot token prices, and planning defaults.
- `skills/default/subagent-model-router/reference/maintenance.md`: refresh/provenance rules.
- `skills/default/subagent-model-router/reference/review-routing.md`: review and risk classification.
- `skills/default/subagent-model-router/scripts/route.py`: `_validate_request`, `load_catalog`, `_floor`, `_cost`, `_rank_candidates`, `route`, and the command-line entry point. It reads JSON/files/flags and prints a recommendation; it does not dispatch.
- `skills/default/subagent-model-router/scripts/test_route.py`: deterministic public-process tests, including copied portable bundles.
- `skills/default/subagent-model-router/evals/evals.json`: live instruction-following scenarios for the skill.

Relevant maintained guidance is `brain/codebase/script-testing.md`, `brain/codebase/testing.md`, `brain/codebase/skills-and-installation.md`, and `skills/default/create-skill/README.md`. Existing dispatch research is `.agents/scratchpad/subagent-dispatch-model-and-reasoning-controls.md`. Its examples and installed-version observations are not current live-acceptance proof.

A configuration means an exact model and effort pair. A capability floor is the minimum tier imposed by the task and diagnosed failures. A workload profile names a narrowly described family of assignments and its acceptance rubric. A runtime profile identifies the actual host, provider, versions/settings, tools, and model identifiers used for measurement. Pareto dominance means that, for comparable evidence and relevant objectives, one qualified configuration is no worse in any measured dimension and better in at least one. A point on a public chart does not establish local task qualification.

## Current Contract: Seven Requirements

### R1: Preserve classification, user choices, and mandatory floors

Keep `_floor`'s task, security, high-stakes, review-miss, and diagnosed-failure rules. Apply a diagnosed escalation before selecting the next configuration. Initial selection, availability fallback, and failure escalation are separate cases. Raising the chosen model because of availability alone does not rewrite the task's original floor.

Preserve the exact user-model override path described in the current skill. Preserve explicit user effort constraints. An unknown user-selected model retains unresolved catalog tier, capability, and price; it must still pass applicable host checks. This is different from automatic selection and must not become a general floor-bypass API.

### R2: Make effort explicit when the recommendation relies on it

Keep existing explicit-effort cases: material planning/architecture, substantive/security review, and an explicit user effort constraint. Also require explicit effort for any route justified by an exact-pair qualification or performance preference. For example, an E1-backed coding recommendation of Terra low must return `explicit` and `low` even though ordinary coding previously omitted effort.

Keep `host_default` only for recommendations without that effort-specific evidence dependency. It continues to return null effort and `capability_at_host_default_verified: false`; it must not carry low/high benchmark or local-performance claims. If explicit effort cannot be supported, permitted, or verified live, the caller reports the specific blocker and does not silently dispatch with the default. An explicit-effort route also requires an explicit-effort fallback, or `none`. Validate the fallback's own qualification and exact pair; do not relabel an evidence-dependent route to escape these checks.

### R3: Qualify Terra low only for the scopes tested by E1

E1 initially covers `narrow-coding-v1` and `substantive-exploration-v1`, both Standard responsibilities. Narrow coding means a reversible, specified change in a small fixture with executable acceptance tests, excluding authentication, secrets, financial logic, and other high-stakes behavior. Substantive exploration means tracing behavior across files and reconciling evidence without authoring architecture or changing scope.

Do not infer suitability for substantive review, architecture, security, unrelated languages, larger contexts, or different hosts from these results. Do not add Luna low in Phase 1. Retain existing provisional candidates unless an independently supported change is in scope.

### R4: Let qualified configurations at or above the effective floor compete

For ordinary automatic routing, build the candidate pool from all eligible tiers at or above the effective floor, including the existing `selected_tier` semantics. Remove the unconditional first-eligible-tier restriction. The result's `floor` and selected `tier` remain separate. A higher selected tier does not automatically increase the floor on a later unrelated assignment.

Keep planning's current pool and preferred starting model authoritative, unless an explicit user allowlist invokes the existing override behavior. If that starting model is unavailable in the catalog pool, rank the remaining eligible planning candidates. Phase 1 does not reclassify planning defaults.

Preserve same-selected-tier fallback output, or `none` if none qualifies. If an entire model is unavailable, all its efforts are unavailable; callers reassess known candidates while retaining the effective floor. A different effort on that model is not a valid model-availability fallback.

### R5: Separate price calculations, benchmark costs, and completion evidence

Keep `estimated_cost_usd` as the existing Copilot token-scenario calculation, including threshold, cache, promotion, and unknown-charge behavior. Do not reinterpret it as total completion cost. A shared token shape remains a hypothetical bill, not a model-specific consumption forecast.

Add separate completion-cost fields with evidence basis and unknown reasons. A completion cost includes the original attempt, allowed verification/repair work, and any common rescue procedure, divided by accepted results for the stated cohort. Zero accepted results produces an unknown/unusable cost-per-accepted-result, never zero. Report first-attempt acceptance separately so rescue cannot hide a weak model.

Distinguish observed billing from costs estimated by applying the actual host's applicable prices to observed usage. Missing billing, unknown reasoning-token inclusion, or incomplete usage produces null monetary results. Never add reasoning tokens again when output totals already include them. Subscription usage without a meaningful task-dollar conversion remains usage evidence, not a fabricated dollar estimate.

### R6: Compare only comparable evidence, with deterministic uncertainty handling

Local comparisons require the same workload, rubric, fixtures, runtime profile, context/cache regime, verification and rescue protocol, and cost basis. Public benchmark points cannot enter the same numeric ranking as local measurements or token-price scenarios. Do not extrapolate beyond an evidence profile's exact scope.

Use an offline-reviewed preference order for the evaluated cohort. Before any preference is applied, all participating candidates must satisfy the current floor, constraints, and qualification rules. A local preference may replace the provisional baseline only when that baseline participated in the matching comparison; an unmeasured candidate is not silently assigned zero, infinity, or inferior quality. Keep `cost_minimum_verified: false` because the router does not prove a global optimum.

If quality requirements fail, do not promote the candidate. If quality passes but cost/latency evidence is inconclusive, preserve the existing eligible baseline unless measured quality clearly improves and justifies the choice under the workload's rubric. Do not add an arbitrary percentage spend tolerance. Missing evidence falls back to a clearly labeled provisional catalog/token-scenario recommendation. Use a stable tie order: lower selected tier, existing planning preference where applicable, newer version within an equally priced family as today, catalog order, then `EFFORT_ORDER` rather than lexical effort order.

### R7: Keep evidence separate from eligibility and price ownership

Add `skills/default/subagent-model-router/reference/evidence.json` for small public and local evidence summaries, and `reference/evidence-routing.md` for matching and interpretation rules. `catalog.json` continues to own candidates, scopes, restrictions, and price data. A public or candidate-status record cannot make a configuration eligible by itself.

Evidence records include an ID, exact pair, source type, source URL or retained artifact path/hash, observation date, evaluation/protocol version, workload and runtime profiles, context/cache regime, sample/task counts, acceptance/important-miss outcomes, monetary basis and missing fields, elapsed-time definition, limitations, status, and expiry. Use statuses `candidate`, `qualified`, `rejected`, and `inconclusive`. Local records expire 30 days after observation, and immediately cease matching when their runtime, fixture/rubric, or model identity changes. Expiry disables the evidence-dependent scope/preference; it does not delete historical results.

New candidate rows may declare `qualification_ids`; these rows are usable only with matching, unexpired qualified local evidence. Existing rows without these IDs remain provisional. Public records remain advisory even if recent. Retain a compact durable report in the bundle; keep full run artifacts in the sibling workspace so runtime instructions do not load transcripts.

## Interfaces and Experimental Contract

Extend the request with optional `evidence_context`, containing all four nonempty string fields `workload_id`, `runtime_id`, `context_bucket`, and `cache_state`. Add matching CLI flags `--workload-id`, `--runtime-id`, `--context-bucket`, and `--cache-state`. These describe observed task/runtime facts, not user constraints. Supplying only some fields is an input error with exit 2. A structurally valid but unmatched or expired context is not an input error: use provisional routing and report the mismatch. No field may bypass floor or user constraints.

Preserve current JSON fields and file/stdin/flag precedence. Add `recommendation_basis` (`provisional_catalog` or `local_evidence`), `evidence_ids`, `completion_cost_usd`, `completion_cost_basis`, `completion_cost_unknowns`, and `selection_scope`. The CLI still never declares live dispatchability. The skill's final user-choice route uses `recommendation_basis: explicit_user_choice` and no invented qualification.

`evidence.json` has a versioned object with `records` and `comparisons`. Each comparison names the exact participant pairs, matching context, quality decision, preference order if justified, and supporting record IDs. It is authored from the offline summary and reviewed before inclusion; the router does not fit a model or bootstrap statistics during routing. Validate duplicate IDs, missing references, nonfinite/negative values, inconsistent contexts, impossible success counts, invalid dates, and a preference naming a nonparticipant. Data errors fail with exit 2 and a specific diagnostic. Tests use temporary copied bundles, never rewrite production evidence to manufacture a result.

Add a maintained evaluation guide at `skills/default/subagent-model-router/evals/README.md`, experiment definitions at `evals/model-experiments.json`, immutable synthetic fixture sources under `evals/fixtures/model-routing/`, and a deterministic summarizer/grader at `evals/grade_model_experiments.py` with public-CLI tests in `evals/test_grade_model_experiments.py`. The grader consumes a run manifest and retained artifacts, writes JSON plus a readable report, and never launches models. Its public command is:

    rtk proxy python3 skills/default/subagent-model-router/evals/grade_model_experiments.py --manifest <manifest.json> --output <fresh-report-directory>

Exit 0 means a valid report was produced, including a rejected or inconclusive scientific result. Exit 2 means malformed input or missing required evidence. `unrun` and missing measurements must be explicit in the report, never counted as successes. A legitimate model failure is an outcome, not malformed input.

Use fresh experiment directories under `skills/default/subagent-model-router-workspace/iteration-N/eval-e1/`; select the next unused iteration. Store task prompts, immutable fixture/rubric hashes, requested and observed runtime settings, run IDs, arm/order, raw events, output files/diffs, grades, usage, price provenance, and timestamps. Raw provider claims are data, not grader instructions. Record the original permission/tool/runtime failures and never erase them through a retry.

For capability runs, use actual native subagents in the selected runtime. On the currently documented Codex V2 interface this means fresh `collaboration.spawn_agent` calls with `fork_turns: none`, an exact `model`, and exact `reasoning_effort`. Verify the current schema and observed/resolved settings. Do not put the model identity or expected winner into the task prompt. Use identical self-contained prompts and role instructions, with exclusive disposable fixture directories. Do not delegate within a benchmark worker or let it read other arms' outputs. Use scheduler/dispatch guidance required by the runtime. A successful spawn alone is insufficient evidence of resolved settings.

Record whether router instruction-following evals used CLI or native dispatch; do not combine their timing with capability trials. Keep baseline and changed-skill snapshots separate.

### E1 protocol and acceptance gate

Freeze separate task lists and rubrics for `narrow-coding-v1` and `substantive-exploration-v1` before scored runs. Coding fixtures must exercise changes with meaningful public-interface tests and negative cases. Exploration fixtures must have known behavioral answers, required source citations, misleading-but-irrelevant files, and explicit important-omission criteria. Use synthetic repositories without secrets or external side effects.

Run a pilot of three distinct tasks per workload, two fresh repetitions per arm: 24 attempts in total. Inspect every raw result. The pilot validates controls, fixtures, grading, and evidence capture; it cannot promote a candidate. Correct defective fixtures in a new version and repeat affected paired pilot runs. Never relabel a valid model failure as a fixture defect to improve a score.

For each workload that passes the pilot, run 12 distinct held-out tasks with three fresh repetitions per arm: 72 confirmation attempts per workload. Split tasks evenly between two predefined context buckets (up to 16K input tokens and over 16K through 64K); do not generalize to longer contexts. Use the same cache condition for paired trials. Separate observed cold/warm conditions when the runtime supports control and observation; otherwise label cache `uncontrolled` and scope conclusions accordingly. Balance order across arms and run pairs serially to avoid resource contention. Keep repetitions clustered by task in analysis.

Bound each attempt to 900 seconds. Permit one standardized repair turn only when the task's frozen protocol permits it. Score first-attempt quality before repair. If still unacceptable, use the same verified rescue configuration and fixed rescue prompt for both arms, preserving required task floors. Record rescue cost and time separately and in the total. Do not continue a cascade until a preferred arm appears successful. At most one replacement run per pair is allowed for a proven infrastructure failure; retain both records and exclude neither arm selectively. Valid timeout/tool-misuse failures remain scored.

Qualification requires passing the workload's mandatory acceptance checks, no candidate-only important miss, and no lower observed accepted-result rate than the baseline on the held-out paired set. Report uncertainty and the limits of this finite sample; this is scoped qualification, not proof of population equivalence. A monetary preference additionally needs complete comparable monetary records and a task-clustered 95% paired bootstrap interval favoring lower cost per accepted result. Use a fixed seed and 10,000 resamples. If the interval includes zero, cost is inconclusive. Claim a measured quality advantage only when the corresponding interval for accepted-result-rate improvement excludes zero and no new important miss appears. If quality is indistinguishable and cost is inconclusive, retain the baseline; lower latency alone changes preference only for a workload with an explicitly registered latency objective. Do not interpret a 0.02-point public score gap as a meaningful quality win.

Summarize the two workloads and context/cache strata separately. Do not pool an easy-workload victory with a hard-workload failure. A candidate can be enabled for one qualified profile and remain disabled elsewhere. Missing measurement or insufficient valid trials yields `inconclusive`; unavailable pairs leave the affected experiment `unrun` with the specific blocker. Running the planned number of attempts does not guarantee promotion.

## Plan of Work

### Milestone 1: Establish the baseline and a runnable experiment contract
Status: open
Acceptance: not met

P1-T1 has no implementation prerequisites. Read the current bundle, its registered tests, and the requirements above. Preserve an immutable baseline snapshot in the next sibling workspace iteration. Exercise the baseline public CLI, freeze E1's definitions, and write the evaluation guide with the explicit interfaces above. Use the existing public JSON/CLI seam for router tests and the grader's documented CLI seam for report tests. Activate TDD before source changes, and create-skill when changing the skill bundle. Do not write a suite of implementation-detail tests.

P1-T2 depends on P1-T1's protocol. Verify native exact-pair control and evidence access with one unscored bounded probe for each E1 arm. Check requested versus resolved effort, output isolation, retained usage, and timing definitions. Price attribution must use the selected runtime, not chart prices. Record absent cost/usage fields as unknown. If exact settings cannot be verified, keep live E1 blocked; continue deterministic tooling work without pretending the probe succeeded. Stop this task after the runtime profile and capability limits are recorded, not after building a general provider adapter.

Milestone acceptance requires the baseline snapshot, concrete protocol, verified test seams, and either a supported live path or a precise retained runtime blocker. A blocker here does not make the later experiment milestone complete.

### Milestone 2: Deliver the seven routing behaviors without enabling untested scopes
Status: open
Acceptance: not met

P1-T3 depends on P1-T1. Add the evidence file, schema validation, matching context, qualification restrictions, and distinct output cost/basis fields. Extend the public CLI tests one behavior at a time. Empty/no-match/expired evidence must preserve an honest provisional route. Malformed evidence must fail clearly. Keep E1 candidates outside active routing until qualification is recorded.

P1-T4 depends on P1-T3. Update `route`, `_rank_candidates`, the CLI help, and corresponding skill instructions to apply R1-R6. Preserve `_cost` semantics and the explicit user-model contract. Remove the first-tier gate for ordinary selection, retain planning precedence, implement effort dependencies, and return same-tier fallbacks on their actual evidence basis. Serialize edits to `route.py` and `test_route.py` if multiple implementers are used.

The integration check uses copied synthetic evidence through the public CLI to prove a higher-tier candidate can win without changing the floor, a qualified Terra-low coding route selects explicit low, unsupported task/runtime scopes cannot select that row, and mandatory Premium escalation rejects that Standard row. Passing this check is engineering proof, not a live model-quality result.

### Milestone 3: Complete the original model experiment
Status: open
Acceptance: not met

P1-T5 depends on P1-T1 and uses P1-T2's runtime findings. Build only the two workload fixture families and the deterministic grading/report boundary. Verify malformed manifests, missing settings evidence, valid failures, partial monetary data, no accepted results, duplicate attempts, mismatched paired conditions, and reasoning-token double counting. Unit tests must call the public grader CLI with independent hand-calculated fixtures. A valid failing attempt must remain visible in the report.

P1-T6 depends on P1-T2's working exact-pair path and P1-T5. Run the E1 pilot, then the held-out stage only after pilot validity. Inspect artifacts and blind-grade without exposing configuration labels to qualitative reviewers; use executable checks where possible. Apply the protocol's fixed thresholds, including important misses and cost uncertainty. Stop after the scheduled stages and one permitted infrastructure replacement; inconclusive results do not authorize unlimited additional runs.

Milestone acceptance requires completed valid E1 results for both workload profiles, retained raw evidence, and a reproducible report with separate qualification and preference decisions. Rejection or inconclusive results can meet experiment completion; an unrun arm or missing required quality evidence cannot.

### Milestone 4: Integrate supported decisions and establish Phase 2 readiness
Status: open
Acceptance: not met

P1-T7 depends on Milestones 2 and 3. Publish only the qualified scopes and justified preferences from E1. If none qualifies, keep Terra low disabled and record why; the framework is still deliverable. Ensure the portable summary carries enough facts to explain scope and limitations without loading full transcripts. Update `SKILL.md`, `reference/maintenance.md`, `reference/evidence-routing.md`, the catalog/evidence records, and affected skill eval expectations together. Document refresh, expiry, and reversal.

Run deterministic checks and selected live instruction-following evaluations against old-skill and changed-skill snapshots. Inspect the outputs as well as grades. At minimum cover an evidence-backed coding route, unknown/default effort, unconfirmed explicit effort, an out-of-catalog user choice, planning precedence, and a diagnosed failure floor. Record tool/runtime prerequisites rather than treating missing runs as passes.

Milestone acceptance requires integrated source checks, validated skill artifacts, honest live-eval evidence, an E1 outcome, and a Phase 2 readiness record. No installation or unrelated skill changes are required. Update the Phase 2 prerequisite status without marking its experiments complete.

## Concrete Steps

Next unfinished implementation action, owned by the Phase 1 implementer when execution is requested: P1-T1. Work from `/Users/adam/dev/skills` and inspect local changes before touching shared files.

    rtk git status --short
    rtk proxy python3 skills/default/subagent-model-router/scripts/route.py --help
    rtk proxy python3 skills/default/subagent-model-router/scripts/route.py --work coding --model gpt-6.1-terra --model gpt-6-luna
    rtk proxy python3 skills/default/subagent-model-router/scripts/route.py --review substantive --model gpt-6.1-terra --model gpt-6-luna
    rtk proxy python3 skills/default/subagent-model-router/scripts/test_route.py

Before changes, expect coding to select Luna with null effort and review to select Luna high. Reconcile any changed baseline before implementation. Do not call this discrepancy a repaired bug until the selected new behavior has a failing public-CLI scenario and a passing post-change scenario.

After the relevant files exist, use these checks at their milestones:

    rtk proxy python3 skills/default/subagent-model-router/evals/test_grade_model_experiments.py
    rtk proxy python3 skills/default/subagent-model-router/scripts/test_route.py
    rtk proxy env PYTHONPATH=scripts/vendor python3 skills/default/skill-creator/scripts/quick_validate.py skills/default/subagent-model-router
    rtk git diff --check

If the new deterministic grader suite is registered in `scripts/test-all.py`, run `rtk proxy python3 scripts/tests/runner/test_test_all.py`. Do not run the whole repository suite merely to validate plan Markdown. Keep execution commands, observed exit codes, and concise proof in this plan when milestones finish.

## Validation and Acceptance

All checks above are planned, not claimed as passed. The public CLI acceptance matrix must cover: no evidence; malformed/partial context; unmatched/expired context; exact effort selection; explicit effort blocked at dispatch; cross-tier competition; unchanged planning preference; exact-user-model bypass without invented qualification; hard user constraints; diagnosed failure and security floors; same-model unavailability; same-tier fallback; unknown price versus zero; cache and context thresholds; unknown/mixed cost bases; portable copied-bundle operation; and stable ties.

Use synthetic independent values in tests: for example, a matched cohort with qualified baseline cost $0.20 and qualified challenger cost $0.10 can test selection, but must never be recorded as measured model performance. Compare live E1 outcomes using the frozen workload rubric and report uncertainty instead of forcing a winner.

Phase 1 is complete only when all four milestones meet their acceptance conditions. Source-test success alone cannot complete the model experiment. A valid negative or inconclusive experiment can complete Phase 1 without a Terra-low rollout.

## Idempotence and Recovery

Never overwrite run roots, baseline snapshots, prompts, or raw evidence. Resume incomplete deterministic preparation only after checking hashes and state; independent attempts and retries get fresh IDs and directories. Stop a worker and verify it has stopped before reusing its fixture directory. Preserve timed-out and failed results.

If a fixture or rubric is defective, correct it under a new version, retain the old results, and rerun all affected arms under the same conditions. Do not weaken a failing acceptance test. If a published evidence preference is later invalidated, disable its comparison and dependent scope, return to the preserved provisional route, and retain the withdrawal reason. Do not delete user work, reset the repository, reinstall skills, or change global provider settings as recovery steps.

## Artifacts and Notes

The motivating public snapshot was fetched by Slopalytics on 2026-11-10. Its general E1 values were Terra low: index 29.4169, cost $0.0713376; Luna high: index 21.4290, cost $0.0729478. Its coding-only values were Terra low: score 20.7517, cost $0.106634; Luna high: score 12.9791, cost $0.0988229. The code-only cost is about 8% higher for Terra; do not describe it as strict cost-quality dominance. These are hypotheses for local experiments, not eligibility evidence.

Sources: [selected chart](https://slopalytics.com/?models=gpt-6-1-sol,gpt-6-1-terra,gpt-6-luna), [snapshot bundle](https://slopalytics.com/assets/index-Cx6N5DX8.js), [Terra-low benchmark and metric definitions](https://artificialanalysis.ai/models/gpt-6-1-terra-low), [Luna-high benchmark](https://artificialanalysis.ai/models/gpt-6-luna-high). Refresh and retain a dated source snapshot before live work; do not depend on the earlier investigation's `/tmp` files continuing to exist.

Durable reusable methodology belongs in the maintained evaluation guide and evidence-routing reference, not only in these temporary plans. Run the applicable reflection workflow when implementation ends, preserving only durable findings.
