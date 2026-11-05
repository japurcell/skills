# Route models with selective effort overrides

This living ExecPlan is `brain/plans/25-router-effort-policy/exec-plan.md`. Follow the `exec-plans`, `brain`, and `execplan-implement` skills. The user authorized implementation and delegated work. Use isolated task branches and worktrees, make scoped implementation commits, and integrate completed work on `feat/router-task-effort`. Do not push.

## Purpose / Big Picture

The router should continue choosing the same catalog models while setting reasoning effort only for dedicated planning or architecture work, substantive or security review, or an explicit user effort request. Coding, ordinary work, exploration, mechanical review, and coordination should accept host default or inherited effort. A caller must distinguish intentional omission from a missing recommendation, and must explain the actual host check that blocks dispatch. Explicit user model selection takes precedence over advisory tier recommendations while preserving host restrictions, explicit effort requirements, and runtime deadlines.

## Progress

- [x] (2026-11-05) [milestone-1] P1: Read applicable instructions, relevant brain notes, router and caller contracts, and exact todos 25 and 26; reproduce current coding output.
- [x] (2026-11-05) [milestone-1] P1: Save this current contract before implementation edits and identify file ownership.
- [ ] [milestone-2] R1: Add failing public CLI tests, implement selective effort output and all fallback paths, then pass focused tests.
- [ ] [milestone-2] D1: Update router guidance, direct callers, and affected behavioral evals with minimal scoped edits.
- [ ] [milestone-3] V1: Integration coordinator runs CLI and documentation checks, inspects all changed-file diffs, and records acceptance evidence.
- [ ] [milestone-3] V1: Integration coordinator reflects, reconciles this plan, and reports completion without claiming live dispatch evidence from static tests.

## Surprises & Discoveries

- Current `--work coding` returns Standard `gpt-6-luna` with `reasoning_effort: "high"`; its fallback is the same model at `max`. This is the end-user CLI reproduction of unwanted effort override behavior, observed 2026-11-05 using `rtk proxy python3 skills/default/subagent-model-router/scripts/route.py --work coding`.
- Catalog rows classify model and effort pairs, not models independent of effort. The same model can occur in more than one tier. Omitting effort cannot establish capability at the host's actual default.
- A scoped search of live Markdown sources found only two direct callers: `skills/default/delegate-to-subagents/SKILL.md` and `skills/default/execplan-implement/SKILL.md`. Their current unconditional exact-effort gates conflict with the approved policy. Historical `*-workspace` artifacts are evidence, not active callers.
- Behavioral eval READMEs explicitly distinguish instruction coverage from live timers, cancellation, execution, and integration. Preserve that distinction.

## Decision Log

- 2026-11-05, planning agent: Preserve the existing catalog, pricing, tiers, floors, and model ranking. Select using existing catalog pairs, then represent the dispatch effort policy explicitly. This avoids inventing unverified host-default tier claims.
- 2026-11-05, planning agent: Use `effort_policy: "host_default" | "explicit"` in recommendations. An available host-default recommendation has `reasoning_effort: null` and `capability_at_host_default_verified: false`. An explicit recommendation carries its exact effort. `recommendation_available` continues to distinguish no recommendation from intentional effort omission. Fallback objects carry the same policy. On no recommendation, effort policy may remain the policy calculated for the task, but no model/effort is recommended.
- 2026-11-05, planning agent: Deduplicate omission-mode fallback candidates by model, so another effort of the selected model does not pretend to be a different fallback. Keep same-tier model order and restrictions. Exact-effort mode keeps existing pair semantics.
- 2026-11-05, planning agent: Explicit user effort constraints win for every task. Risk and failure flags may change the model tier but cannot cause excluded tasks to emit effort. Dedicated material planning uses `planning` or `execplan`; local design, debugging, and tests remain `coding`. A role title such as coordinator does not itself imply planning.
- 2026-11-05, planning agent: Honor todo 26 in caller orchestration guidance rather than weakening CLI model allowlist or tier semantics. Only an actual user instruction choosing an exact model activates the override path. Ordinary `constraints.models` filters and catalog recommendations do not activate it. A user-chosen exact model bypasses the advisory router tier choice, subject to host controls, permissions, verified availability, catalog restrictions where relevant, the same task-based effort policy, explicit user effort, and deadlines. Do not invent catalog entries for that choice or claim catalog/default-effort capability verification.

## Outcomes & Retrospective

Planning and baseline CLI evidence are complete. Implementation and integrated acceptance remain open. No live dispatch, availability probe, timer, or cancellation has been established by this plan. Next work belongs to the router implementation and caller documentation owners, followed by parent integration verification.

## Context and Orientation

Working directory for every command below is `/Users/adam/dev/skills`. Python's standard library is sufficient for the router and its unittest suite. Prefix shell commands with `rtk`; use `rtk proxy` where raw command semantics matter.

`skills/default/subagent-model-router/scripts/route.py` validates JSON/CLI requests, loads `reference/catalog.json`, computes a capability floor in `_floor`, ranks catalog pairs in `_rank_candidates`, and returns public JSON in `route`. Its argparse help is part of the user contract. `scripts/test_route.py` invokes the actual public CLI and also checks catalog behavior. `SKILL.md` adds host dispatch checks beyond catalog recommendations; the CLI itself does not dispatch agents.

The catalog currently selects coding Luna/high Standard, planning Sol/medium Standard, substantive review Luna/high Standard, and security review Terra/high Premium. These model selections and existing planning/review effort choices must remain. Do not expand catalog content, prices, or model tiers.

Exact pending backlog requirements:

- Todo 25 requires router guidance to distinguish tool support, permission to set overrides, and verified live availability. A catalog recommendation proves none, and failures must name the blocking check. Delegation must preflight host override feasibility before routing and must not confuse a router recommendation with explicit user selection. The approved effort policy narrows the preflight: effort support and permission matter only when effort is required.
- Todo 26 requires delegation to honor explicit user model overrides instead of enforcing the router tier recommendation. Preserve host restrictions and deadline enforcement. Apply normal routing constraints without explicit user override.

## Plan of Work

### Milestone 1: Establish an actionable contract
Status: done
Acceptance: met

P1, owned by the planning agent, had no prerequisites. It read applicable `AGENTS.md`, the planning/brain skills, `brain/todos.md`, `brain/codebase/skill-evaluation.md`, `brain/principles/cost-aware-delegation.md`, and relevant source/callers. The coding CLI reproduction above establishes the pre-change behavior. This file exists before source edits. P1 stops at planning and does not own source edits.

### Milestone 2: Deliver coherent router and caller behavior
Status: open
Acceptance: not met

R1, owned by the delegated router implementer, depends on P1. Own only `skills/default/subagent-model-router/scripts/route.py` and `skills/default/subagent-model-router/scripts/test_route.py`. Activate `tdd` before editing source. First add public CLI tests that fail on the pre-change implementation, then implement the interface above. Cover default and explicit effort, planning and execplan, substantive/security review, mechanical review, every excluded work class, risk/failure escalation, fallback semantics, no recommendation, JSON/CLI parity, malformed data, and unchanged model ranking. The red/green test must expose externally visible JSON behavior. Stop when focused tests pass and provide commands/results; do not edit caller docs or catalog.

D1, owned by the delegated documentation implementer, depends on P1 and the interface in this plan, but can run alongside R1. Own `skills/default/subagent-model-router/SKILL.md`, its `evals/evals.json`, `skills/default/delegate-to-subagents/SKILL.md` and `evals/evals.json`, and `skills/default/execplan-implement/SKILL.md` and `evals/evals.json`. Load the applicable skill-authoring guidance. Make concise caller edits; preserve unrelated prose, comments, isolation requirements, and deadlines. Update all primary, retry, fallback, dispatch-record, and agent-reuse paths. Omitted-effort work reuses only a same-model agent originally spawned without explicit effort; required-effort work reuses only the exact model/effort pair. Explicit user model choice bypasses advisory tier choice; without one, normal router selection applies. Preflight support and permission before routing; verify live acceptance separately and identify the specific blocking check. Required effort must be accepted and verified; omitted effort does not require an effort control. Stop after scoped guidance/eval updates and report static checks, without claiming live availability.

All workers share the repository and must preserve others' edits. D1 and R1 do not share source ownership. Both must use the common interface and report an actual mismatch before making unilateral contract changes.

### Milestone 3: Verify the integrated contract
Status: open
Acceptance: not met

V1, owned by the persistent integration coordinator, depends on R1 and D1. Run the commands below against the integrated branch tip, inspect full diffs for unintended changes, and reconcile any contradictions between CLI output and caller behavior. Check JSON evaluation files parse and expectations no longer impose unconditional effort. Review explicit user overrides, no-effort reuse, unavailable model handling, same-model fallback semantics, and retained deadline enforcement across both callers. Invoke `reflect` at the end of this code-changing session. If todos are completed, use the `todo` workflow to update and archive them rather than silently removing entries. This plan must be updated with actual results and milestone state before final reporting.

## Concrete Steps

Next unfinished authorized action: the parent dispatches R1 and D1 with the ownership boundaries above and a five-minute checkpoint/runtime limit. Parent-side deadline enforcement remains required by active delegation guidance. Both task worktrees must start from the integration branch tip; the integration coordinator merges their scoped changes and commits them on `feat/router-task-effort`.

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

Also parse the three affected `evals/evals.json` files with Python `json.loads` in one `rtk proxy python3 -c` invocation, inspect their assertions for policy consistency, and inspect `rtk git diff --` the nine owned source/guidance/eval files. Reading scenarios is instruction coverage only. No eval runner is claimed available from the examined READMEs, and no live dispatch success may be inferred from these static checks.

## Idempotence and Recovery

The CLI and checks are read-only and repeatable. Edits are reversible in version control. On partial failure, retain worker evidence, inspect `rtk git diff`, and fix only owned files. Do not reset shared changes or weaken tests. If the interface proves insufficient, report the concrete failing scenario to the parent and reconcile this plan before dependent edits continue. Scoped commits on task branches and the integration branch are part of the authorized workflow; never push.

## Interfaces and Dependencies

The existing CLI input schema and selection constraints remain. `constraints.efforts` or `--effort` count as explicit user effort requirements. Public recommendation JSON adds an explicit policy discriminator and a false host-default capability verification marker rather than inventing catalog capability evidence. Keep `availability_verified: false` for catalog recommendations because tool support, authorization, and live availability are separate host-level checks. `recommendation_available: false` remains a routing failure; a null effort with `effort_policy: "host_default"` and available model is intentional omission, never failure.

Required explicit effort dispatch confirms exact model and effort controls, authorization, restrictions, and live acceptance. Host-default dispatch confirms the exact model control, authorization, restrictions, and live acceptance, omits the effort argument, and documents that inherited/default effort capability is unverified. The caller must not silently convert omitted effort to a numeric default or reuse an explicitly configured agent. Explicit user-selected model handling remains caller policy because router catalog constraints do not themselves authorize a host override.
