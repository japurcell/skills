# Skill Authoring Audit Handoff

## Goal and Status

Complete the evidence-backed audit of non-imported maintained skills, then write `docs/skill-audit/audit.md` and self-contained `docs/skill-audit/ExecPlan.md`. Neither exists. Implementation, installation and publication remain later work.

The [map](map.md) has 36 tickets: eleven closed, twenty-four open and one claimed. [Review Requirements and Task Planning](tickets/review-requirements-and-task-planning.md) is claimed by `subagent-P6r3T8`. Static investigation and parent reconciliation are complete; live human proposal review is pending. No native audit baseline ran.

Scope remains 37 candidates: 32 published plus five repository-local skills; 23 configured imports excluded. [Coverage](coverage.md) owns current totals: twenty-seven statically reviewed candidates, 1,566 rows, 114 primary hashes and twenty-seven separately declared fixture hashes. The first report's 45-file primary inventory includes bundled fixtures, so the later fixture count is not the whole audit's fixture total. Human proposal review covers twenty-three candidates and thirty-two earlier findings. Four candidates await live review; ten remain unstarted.

## Exact Next Step

Obtain answers to the three pending Requirements and Task Planning questions, then record the live dispositions and close this claimed batch only. Do not start another ticket. Both exact blockers, `choose-audit-batches-and-evidence-format.md` and `set-audit-completion-and-implementation-gates.md`, were rechecked closed before this claim. The reviewer completed and released report ownership; no further source delegation is pending.

The recommended round is:

1. Accept RPT-001/RPT-004 as later evaluation repairs: align Spec prompts/oracles with current tasks.json/T001/vertical-slice contracts; provision portable Architecture fixtures. Preserve useful checks, two Spec fixture behavior requirements, output precedence/defaults, controls, approvals, required roles and design-only scope. Exact fixture/oracle choices and genuine protocol prerequisites precede executable readiness.
2. Retain RPT-002/RPT-003/RPT-005 in their three separate decision routes below, alongside thirteen earlier routes. This does not choose setup, explorer precedence or browser-helper mapping, authorize execution, or waive evidence.
3. Add exactly `skills/spec-to-tasks/evals/grade_benchmark.py` to SAG-008 metric-producer and DD-004 protocol scope, retaining accepted targets. Current accepted counts remain eight producers/five graders until live approval. Representation, statuses, exits, schemas and consumer compatibility remain unresolved.

These are planning questions, not permission to implement. No answer is recorded yet. After live acceptance update shared records, exact target lists and knowledge pointers as applicable; retain all actual behavior questions. The batch closes only after the live review and its recorded Resolution. At most one non-research ticket may close per logical session.

## Findings and Visible Routes

The [single register](findings.md) owns thirty-seven findings: twenty-one major, thirteen minor and three observations. Thirty-two earlier findings have dispositions; five new RPT findings await live review. Static mechanisms and predicted consequences are not observed native failures.

New proposed routes are open and blocked by this batch:

- RPT-002: [Resolve To Issues Tracker Setup](tickets/resolve-to-issues-tracker-setup.md).
- RPT-003: [Resolve Architecture Contest Narrow Exploration](tickets/resolve-architecture-contest-narrow-exploration.md).
- RPT-005: [Resolve Planning Browser Verification Prerequisite](tickets/resolve-planning-browser-verification-prerequisite.md).

Thirteen earlier routes remain open and unblocked. The [register](findings.md#pending-decisions-and-approval) links all owners: SAG-002/003/008/013, RLW-002, DD-004, QH-002/003/004, QH-005/QH-006 together, QH-008/009/010. Both final documents must expose every pending ID and route, including the three new proposed questions. Genuinely dependent work stays pending. Deferral requires rationale, affected work, remaining risk and revisit trigger; evidence waivers and residual-risk acceptance are separate.

Earlier accepted scopes are unchanged: SAG-001/009/010/011/012/014 plus SAG-013 documentation cleanup; SAG-004 through SAG-007; RLW-001/RLW-003; DD-001/DD-002/DD-003/DD-005; QH-001/QH-007. SAG-011 includes only Create AgentsMD and Harness Analysis sidecar wording. Improve Repo Harness stays pending QH-009. Existing SAG-008 eight producers/DD-004 five graders retain their accepted scope and pending design. No source repair or underlying behavior choice occurred. Exact SAG-004 and other fixture/oracle choices remain prerequisites; do not invent successors, broaden approved targets, make dependencies optional or equate text with performed workflow.

The bounded retry-counting check remains in [Review Execution and Handoff](tickets/review-execution-and-handoff.md): distinguish successive task runs from failed-subtask replacements under the loop's three-failure budget and delegation's one-replacement exception. No contradiction or behavior choice is established yet.

## Latest Source Evidence and Dispatch

The [requirements/planning report](reports/review-requirements-and-task-planning.md) records baseline `b4d0b428aaccdc1d4f7661129c7e4c78ef85425f`: four skills, twelve primary files, two fixtures, fourteen bounded dependency fingerprints and 232 rows. All 28 source/fixture/dependency fingerprints match baseline bytes. Sixteen audit-record hashes identify the review checkpoint only; parent record edits can change them. Nine primary files ship; three primary eval resources and two fixtures are pruned. No entry requires a pruned runtime resource. Two role definitions exist; installed access remains unverified.

Main mechanisms: Spec evals/grader use obsolete prd.json/userStories/horizontal oracles; To Issues names an unshipped setup helper; Architecture's narrow existing-code contest conflicts with Explore's required no-agent branch; four Architecture cases use nonportable absolute source paths; UI planning prescribes an unshipped browser helper. Browser wording is downstream acceptance text, not an instruction to invoke a browser during planning. Repository absence does not prove universal host unavailability. PRD's save default adapts to this checkout's higher-priority active-doc placement while retaining no-overwrite/suffix/final-path rules; this is scoped, not a global output rewrite.

Reviewer `/root/requirements_planning_static`: selected/submitted `gpt-6.1-sol`/`high`, unused fallback `gpt-6-sol`/`high`. Executed settings and usage are unconfirmed. Routing metadata stayed outside the prompt. First post-dispatch clock bound 2026-10-06 20:37:58 UTC; initial twenty-minute deadline 20:57:58 UTC. Saved initial/complete checkpoints were read. Five-minute running-status check observed 20:43:08 UTC, ten seconds after the nominal checkpoint. Completion and ownership release were observed by 20:46:21 UTC, before the limit; exact completion time is unconfirmed. No interruption, replacement or extension occurred. Prior dispatch histories remain in their owning reports; none is native evidence.

## Standing Constraints and Native Evidence

Keep artifacts under `docs/skill-audit/`. Domain-modeling remains waived. Apply Wayfinder/Grilling and Create Skill/Skill Creator for authoring/evaluation choices; load ExecPlans before plan authoring. Preserve intended triggers, controls, approvals, dependencies/delegation, stops, outputs and names. Missing evidence is unresolved, not incompatibility or passing compliance. Advisory length or absent eval files alone do not establish a defect.

Exclude imports, provenance recovery and ledgers. Read shared/imported resources only as necessary dependencies. Static batches allow no implementation, installer/import refresh, packaging, audited grader/validator execution or native baseline. Documentation maintenance cannot edit protected skill bundles. Dotnet Upgrade has only its narrow paper-reading exception; retain all other restrictions. Finish twelve scopes and reconciliation before sample selection; split bundles remain partial until both parts/integration are complete.

[Native evidence contract](tickets/set-audit-evidence-and-model-coverage.md#resolution): native Codex CLI; up to three safe risk-selected skills after static review; explicit/allowed-automatic/adjacent-negative/safe-boundary cases; identical cases across seven models at medium; three fresh runs per configuration. Exact IDs: `gpt-5.6-sol`, `gpt-6-sol`, `gpt-6.1-sol`, `gpt-5.6-luna`, `gpt-6-luna`, `gpt-6-astra`, `gpt-5.6-terra`. Dated catalog advertising does not prove access or execution; no substitutions. Copilot/Gemini comparison stays static.

Require isolated discovery/tools, unchanged snapshots, prompt/config/hash/version/permission/timing/usage records and usable traces. Define outcomes before launch; grade activation/workflow/output separately. Self-reports do not prove compliance. Usable failed runs are diagnostic evidence; unavailable models, unsafe fixtures and missing traces block completion unless explicitly waived. No sample or launch recipe exists. Handoff/Spec/OKF inputs are promising, not certified fixtures. `--ignore-user-config` alone does not prove isolation; dated help lacks `--full-auto`.

## Verification and Documentation Pass

`rtk proxy python3 /private/tmp/skill-audit-verify-requirements.py` passed: four exact 58-row matrices, twelve primary/two fixture/fourteen dependency source hashes, 36-ticket acyclic graph, closed blockers/current claim, thirty-seven unique findings/index, 23 human-reviewed plus four static-reviewed and ten unstarted candidates, links/anchors/formatting/fog and unchanged protected sources. Prior reports retain their verified source inventories; older hardcoded graph/totals are superseded. JSON/YAML/AST parsing is static only. Scoped diff checks passed. No model run, target grader, installer or publication occurred.

Formal Update Agent Docs changed existing grader/caller-helper pointers and added a focused planning-prerequisite issue in `.agents/memory/known-issues/skills.md`, type Known Issue. Existing INDEX/FILE_MAP/instruction routes cover the added audit records; no API, test strategy, source or skill changed. OKF used profile only; `rtk proxy ./scripts/lint-okf.py` exited 0 across both bundles. Scoped canonical diff contains only this authorized file. Added: planning prerequisite issue. Changed: grader/caller-helper pointers. Split/moved: None. Deduplicated: None. Index updates: None. Remaining doc quality TODOs: None.

Process notes: reviewer replaced a Tool Guardian command-token rejection with inspectable patches before execution. Parent corrected guessed `references/` paths to the updater's exact linked `refs/` paths, fixed a blank line splitting the finding index, and reran record checks. Resolve references from loaded skill links; use short inspectable commands/patches. Correct workspace exclusion searches to `!**/*-workspace/**`; an initial shallow glob listed snapshot names but no snapshot content was read or counted. Earlier dynamic-execution inspection failures remain in prior reports. RTK works; gain database remains unavailable. `design-map.html` is dated discussion material; no annotations or approval were supplied.
