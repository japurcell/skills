# Route models with selective effort overrides

This completed ExecPlan is `brain/archive/plans/25-router-effort-policy/exec-plan.md`. Follow the `exec-plans`, `brain`, and `execplan-implement` skills. The user authorized implementation and delegated work. Use isolated task branches and worktrees, make scoped implementation commits, and integrate completed work on `feat/router-task-effort`. Do not push.

## Purpose / Big Picture

The router should continue choosing the same catalog models while setting reasoning effort only for dedicated planning or architecture work, substantive or security review, or an explicit user effort request. Coding, ordinary work, exploration, mechanical review, and coordination should accept host default or inherited effort. A caller must distinguish intentional omission from a missing recommendation, and must explain the actual host check that blocks dispatch. Explicit user model selection takes precedence over advisory tier recommendations while preserving host restrictions, explicit effort requirements, and runtime deadlines.

## Progress

- [x] (2026-11-05) [milestone-1] P1: Read applicable instructions, relevant brain notes, router and caller contracts, and exact todos 25 and 26; reproduce current coding output.
- [x] (2026-11-05) [milestone-1] P1: Save this current contract before implementation edits and identify file ownership.
- [x] (2026-11-05) [milestone-2] R1: Added failing public CLI tests, implemented selective effort output and fallback paths, and passed all 26 focused tests in commit `38a81158`.
- [x] (2026-11-05) [milestone-2] D1: Updated router guidance, direct callers, and behavior evals; JSON cases (13/12/14), skill-source validation, and diff check passed in commit `f93b56b7`.
- [x] (2026-11-05) [milestone-3] V1: Integrated focused tests (26 passed), six CLI cases preserved primary model selection, three eval JSON files parsed, skill-source validation and `git diff --check` exited 0; merge base resolved to `d780499db4f8a16fdc74317b54bc44b5aa6df948` with a nonempty 10-file diff.
- [x] (2026-11-05) [milestone-3] V1: Ran six genuine old-skill/revised-skill pairs; deterministic exact-field assertions scored 22/35 old and 35/35 revised after normalizing `reused_worker` to the boolean representation present in both actual outputs. Saved raw outputs and grades under `/private/tmp/router-task-effort-eval/iteration-1/`, aggregate evidence in `deterministic-grade-summary.json`, and static viewer at `/private/tmp/router-task-effort-eval/router-review.html`. No timing or token metrics were supplied.
- [x] (2026-11-05) [milestone-2] D2: Integrated thin caller activation and the router's exact-user-model no-catalog correction in `a40cdbe4`; source validation, all three eval JSON parses, and diff check passed.
- [x] (2026-11-05) [milestone-3] V1: Prepared seven iteration-2 prompts and separate expected rubrics against immutable baseline and integrated sources; verified six reused prompts are byte-identical, all prompt/metadata hashes match the iteration manifest, and all output folders remain empty.
- [x] (2026-11-05) [milestone-3] V1: Graded seven paired cases with the deterministic grader: revised 43/43 expected-field checks passed; baseline 18/43. Reviewed raw rationales, noted baseline eval_id schema mismatches, preserved outputs, and generated the static viewer.

## Surprises & Discoveries

- Current `--work coding` returns Standard `gpt-6-luna` with `reasoning_effort: "high"`; its fallback is the same model at `max`. This is the end-user CLI reproduction of unwanted effort override behavior, observed 2026-11-05 using `rtk proxy python3 skills/default/subagent-model-router/scripts/route.py --work coding`.
- Catalog rows classify model and effort pairs, not models independent of effort. The same model can occur in more than one tier. Omitting effort cannot establish capability at the host's actual default.
- A scoped search of live Markdown sources found only two direct callers: `skills/default/delegate-to-subagents/SKILL.md` and `skills/default/execplan-implement/SKILL.md`. Their current unconditional exact-effort gates conflict with the approved policy. Historical `*-workspace` artifacts are evidence, not active callers.
- Behavioral eval READMEs explicitly distinguish instruction coverage from live timers, cancellation, execution, and integration. Preserve that distinction.
- Independent review found two apparent caller-spec gaps after D1: no standalone exact-user-model override path and generic wording that still required explicit effort. The current direction treats the router skill as the single policy source, reached through mandatory activation; callers apply its route and retain their orchestration and deadline responsibilities. The findings therefore call for removing duplicated policy from direct callers and verifying the pointer works, not restating policy there. Standards review found no issues.

## Decision Log

- 2026-11-05, planning agent: Preserve the existing catalog, pricing, tiers, floors, and model ranking. Select using existing catalog pairs, then represent the dispatch effort policy explicitly. This avoids inventing unverified host-default tier claims.
- 2026-11-05, planning agent: Use `effort_policy: "host_default" | "explicit"` in recommendations. An available host-default recommendation has `reasoning_effort: null` and `capability_at_host_default_verified: false`. An explicit recommendation carries its exact effort. `recommendation_available` continues to distinguish no recommendation from intentional effort omission. Fallback objects carry the same policy. On no recommendation, effort policy may remain the policy calculated for the task, but no model/effort is recommended.
- 2026-11-05, planning agent: Deduplicate omission-mode fallback candidates by model, so another effort of the selected model does not pretend to be a different fallback. Keep same-tier model order and restrictions. Exact-effort mode keeps existing pair semantics.
- 2026-11-05, planning agent: Explicit user effort constraints win for every task. Risk and failure flags may change the model tier but cannot cause excluded tasks to emit effort. Dedicated material planning uses `planning` or `execplan`; local design, debugging, and tests remain `coding`. A role title such as coordinator does not itself imply planning.
- 2026-11-05, planning agent: Honor todo 26 in the authoritative router guidance rather than weakening CLI allowlist or tier semantics. Only an actual user instruction choosing an exact model activates the override path. Ordinary `constraints.models` filters and catalog recommendations do not activate it. The exact user choice bypasses advisory tier selection subject to host controls, permission, live acceptance, applicable restrictions, the task effort policy, explicit user effort, and deadlines. Do not invent catalog entries or claim catalog/default-effort capability verification.
- 2026-11-05, integration coordinator: Keep `skills/default/subagent-model-router/SKILL.md` as the single source for routing and host-check policy. Evidence: merge `a40cdbe4` includes caller activation/apply-route guidance in both direct callers; the router carries the exact-user-model path, and its eval count is 14, including the no-catalog case. Callers retain their own orchestration, dispatch application, runtime records, and deadlines without copying the routing taxonomy or preflight rules. Standards and Spec reviews are clean on current behavior; the Spec reviewer withdrew the per-task activation wording finding. Paired evaluation passed; no additional per-task activation wording change was needed.

## Outcomes & Retrospective

R1, D1, and D2 are integrated at `a40cdbe4`; all three milestones are complete. The integrated router suite reported 26 passed, and post-merge source validation, three eval JSON parses, and diff check passed. Seven paired instruction cases scored 43/43 on revised guidance, including the no-catalog exact-user-model host-default case. Baseline raw scoring was 18/43, including seven eval_id type/value mismatches because the prompt did not define that field's format; this ambiguity did not affect revised results. Raw outputs, per-case grades, and aggregate summary are retained in `/private/tmp/router-task-effort-eval/iteration-2/`; the static viewer is `/private/tmp/router-task-effort-eval/router-review-iteration-2.html`. Reflection found no durable lesson to add beyond the existing single-owner principle. No live dispatch, timing, token cost, or repeated-run variance was established.

## Context and Orientation

Working directory for every command below is `/Users/adam/dev/skills`. Python's standard library is sufficient for the router and its unittest suite. Prefix shell commands with `rtk`; use `rtk proxy` where raw command semantics matter.

`skills/default/subagent-model-router/scripts/route.py` validates JSON/CLI requests, loads `reference/catalog.json`, computes a capability floor in `_floor`, ranks catalog pairs in `_rank_candidates`, and returns public JSON in `route`. Its argparse help is part of the user contract. `scripts/test_route.py` invokes the actual public CLI and also checks catalog behavior. `SKILL.md` adds host dispatch checks beyond catalog recommendations; the CLI itself does not dispatch agents.

The catalog currently selects coding Luna/high Standard, planning Sol/medium Standard, substantive review Luna/high Standard, and security review Terra/high Premium. These model selections and existing planning/review effort choices must remain. Do not expand catalog content, prices, or model tiers.

Exact pending backlog requirements:

- Todo 25 requires authoritative router guidance to distinguish tool support, permission to set overrides, and verified live availability. A catalog recommendation proves none, and failures must name the blocking check. Callers activate and follow that policy before dispatch; they must not copy its detailed preflight rules. Effort-control support and permission matter only when effort is required.
- Todo 26 requires honoring an exact user-selected model over the advisory tier recommendation, subject to host restrictions and deadline enforcement. The router skill defines that policy; callers apply its final route. Without an exact user selection, use normal routing constraints.

## Plan of Work

### Milestone 1: Establish an actionable contract
Status: done
Acceptance: met

P1, owned by the planning agent, had no prerequisites. It read applicable `AGENTS.md`, the planning/brain skills, `brain/todos.md`, `brain/codebase/skill-evaluation.md`, `brain/principles/cost-aware-delegation.md`, and relevant source/callers. The coding CLI reproduction above establishes the pre-change behavior. This file exists before source edits. P1 stops at planning and does not own source edits.

### Milestone 2: Deliver coherent router and caller behavior
Status: done
Acceptance: met

R1, owned by the delegated router implementer, depends on P1. Own only `skills/default/subagent-model-router/scripts/route.py` and `skills/default/subagent-model-router/scripts/test_route.py`. Activate `tdd` before editing source. First add public CLI tests that fail on the pre-change implementation, then implement the interface above. Cover default and explicit effort, planning and execplan, substantive/security review, mechanical review, every excluded work class, risk/failure escalation, fallback semantics, no recommendation, JSON/CLI parity, malformed data, and unchanged model ranking. The red/green test must expose externally visible JSON behavior. Stop when focused tests pass and provide commands/results; do not edit caller docs or catalog.

D1, owned by the delegated documentation implementer, depends on P1 and the interface in this plan, but can run alongside R1. Own `skills/default/subagent-model-router/SKILL.md`, its `evals/evals.json`, `skills/default/delegate-to-subagents/SKILL.md` and `evals/evals.json`, and `skills/default/execplan-implement/SKILL.md` and `evals/evals.json`. Load applicable skill-authoring guidance. The router skill is the authoritative source for task taxonomy, model/effort policy, host checks, exact-user-model overrides, fallback, and agent reuse. Direct callers must activate it and apply its final route, while preserving their own task graph, dispatch control application, runtime records, and deadlines. Do not repeat detailed routing policy in the callers. Do not claim live availability from static checks.

All workers share the repository and must preserve others' edits. D1 and R1 do not share source ownership. Both must use the common interface and report an actual mismatch before making unilateral contract changes.

D2 is complete in merge `a40cdbe4`. The router skill remains authoritative; both direct callers activate it and apply its final route while keeping their own task orchestration, dispatch application, runtime records, and deadlines. The router also handles an exact user-selected model when the catalog has no candidate, subject to host and effort checks; unresolved required effort still blocks dispatch. This resolves the duplicated caller prose. Final pointer behavior remains under Milestone 3 paired evaluation.

### Milestone 3: Verify the integrated contract
Status: done
Acceptance: met

V1, owned by the integration coordinator, depended on R1, D1, and D2. On integrated source `a40cdbe4`, skill-source validation, parsing all three eval JSON files, and `git diff --check` passed; the focused router suite had 26 passes before the final documentation/eval-only merge. Seven genuine old/revised pairs completed. The deterministic rubric scored revised instructions 43/43 and baseline 18/43; all revised rationales agreed with their decisions. Baseline outputs used a case-name string for `eval_id` although prompts only require the key and the rubric expects an integer; those seven schema mismatches remain in the raw score, with no rubric adjustment. No timing or token metrics were supplied. This evidence establishes instruction coverage only, not live dispatch or repeated-run performance.

## Concrete Steps

Completed: the seven paired cases were run and graded from `/private/tmp/router-task-effort-eval/iteration-2/`. Raw decision/response files at each `run-1/` root were preserved, and byte-identical copies under `outputs/` allow the canonical static viewer to read them. The aggregate grade summary records exact paths and the layout normalization. The remaining repository action is to archive this completed plan and commit the scoped documentation bookkeeping; do not push.

R1 reproduces the existing CLI behavior, adds failing cases in the existing CLI test module, records the failure, implements the contract, and runs:

    rtk proxy python3 -m unittest discover -s skills/default/subagent-model-router/scripts -p test_route.py

D1 updates only its owned guidance and eval expectations. Parent then runs the integrated validation commands below and records results. Do not edit historical `*-workspace` benchmark outputs or installed skill copies.

## Validation and Acceptance

Run these exact commands from the repository root:

    rtk proxy python3 skills/default/subagent-model-router/scripts/route.py --work coding
    rtk proxy python3 skills/default/subagent-model-router/scripts/route.py --work planning
    rtk proxy python3 skills/default/subagent-model-router/scripts/route.py --review substantive
    rtk proxy python3 skills/default/subagent-model-router/scripts/route.py --review security
    rtk proxy python3 skills/default/subagent-model-router/scripts/route.py --work coding --risk unusually_difficult
    rtk proxy python3 skills/default/subagent-model-router/scripts/route.py --work coding --effort high
    rtk proxy python3 -m unittest discover -s skills/default/subagent-model-router/scripts -p test_route.py
    rtk proxy python3 scripts/validate-skill-sources.py skills
    rtk git diff --check

Expected, not yet observed: coding remains Luna Standard but emits host-default policy and null effort; planning remains Sol/medium, substantive review Luna/high, security review Terra/high; risk changes coding model selection without adding effort; explicit `--effort high` emits explicit effort. Every fallback follows the same policy and host checks. The unittest suite must pass with exit 0. Catalog/schema errors remain exit 2 on stderr without a recommendation. Validation of skill sources and diff whitespace must exit 0.

Post-merge evidence on 2026-11-05: `rtk proxy python3 scripts/validate-skill-sources.py skills`, parsing the three active eval JSON files with `json.loads`, and `rtk git diff --check` exited 0. The focused router suite reported 26 passed. The seven genuine pairs were graded with `/private/tmp/router-task-effort-eval/grade_structured_output.py`; revised results are 43/43 and baseline results 18/43. Raw rationales, per-case deterministic grades, and `deterministic-grade-summary.json` remain under `/private/tmp/router-task-effort-eval/iteration-2/`. Some evaluator outputs were written at `run-1/` root instead of canonical `outputs/`; byte-identical copies were placed under `outputs/`, preserving the original files. The static review page is `/private/tmp/router-task-effort-eval/router-review-iteration-2.html`.

## Idempotence and Recovery

The CLI and checks are read-only and repeatable. Edits are reversible in version control. On partial failure, retain worker evidence, inspect `rtk git diff`, and fix only owned files. Do not reset shared changes or weaken tests. If the interface proves insufficient, report the concrete failing scenario to the parent and reconcile this plan before dependent edits continue. Scoped commits on task branches and the integration branch are part of the authorized workflow; never push.

## Interfaces and Dependencies

The existing CLI input schema and selection constraints remain. `constraints.efforts` or `--effort` count as explicit user effort requirements. Public recommendation JSON adds an explicit policy discriminator and a false host-default capability verification marker rather than inventing catalog capability evidence. Keep `availability_verified: false` for catalog recommendations because tool support, authorization, and live availability are separate host-level checks. `recommendation_available: false` remains a routing failure; a null effort with `effort_policy: "host_default"` and available model is intentional omission, never failure.

Required explicit effort dispatch confirms exact model and effort controls, authorization, restrictions, and live acceptance. Host-default dispatch confirms the exact model control, authorization, restrictions, and live acceptance, omits the effort argument, and documents that inherited/default effort capability is unverified. The router skill defines this policy; callers follow its route and must not silently convert omitted effort to a numeric default or reuse an explicitly configured agent. The exact user-model override still requires existing host controls and does not change router catalog constraints.
