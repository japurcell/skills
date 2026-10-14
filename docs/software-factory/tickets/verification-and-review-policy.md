# Verification and review policy

**Type:** grilling
**Status:** closed
**Blocked By:** workflow-authoring-and-task-contract.md
**Research Dir:** not applicable

## Question

How does a workflow configure verification and review/refactor cycles while keeping evidence, token use, and termination understandable?

Apply the accepted [Task scheduling and integration](task-scheduling-and-integration.md#resolution) contract: default reviewers return findings against a fixed revision, a separate repair step owns edits, conflicts use bounded visible repair, and stale work is preserved for refresh. Do not reopen those decisions or the already configurable per-task/aggregate review and optional interactive verification requirements. This ticket selects the remaining verification and budget policies.

Separate deterministic lint/unit/E2E commands from agent-led UI exploration. Decide enablement, when to ask before expensive checks, budgets, and the representation of disabled or unavailable checks.

Define per-task, whole-diff, combined, and disabled review modes; parallel reviewer aggregation; repair ownership; rerun rules after edits; infrastructure retries versus quality repairs; per-loop and run-wide limits; and terminal outcomes.

Resolution should compare the user's quick-change and task-graph scenarios and show what can satisfy acceptance in each. The earlier three-repair example is not a chosen default.

---

## Decision record

Claimed on 2026-10-13 after verifying the exact prerequisite, `workflow-authoring-and-task-contract.md`, is closed. The user requested this ticket explicitly. This remains a planning conversation; no implementation is authorized.

### Prior answers applied

- [Confirmed factory requirements](confirmed-factory-requirements.md#confirmed-requirements) already requires configurable lint, unit, E2E, and interactive UI verification; the human controls token-intensive interactive verification. Per-task and aggregate review/refactor cycles and optional pre-PR human review are settled capabilities. The six-stage recipe is not a fixed pipeline.
- [Workflow authoring and task contract](workflow-authoring-and-task-contract.md#resolution) gives TypeScript code control of orchestration, with managed operations and bounded loops. Acceptance criteria may be prose; their text does not automatically select or constitute verification evidence.
- [Agent execution profiles](agent-execution-profiles.md#resolution) owns per-step harness/model/reasoning/prompt/skills, explicit fallbacks, fresh independent reviews, compatible repair-session reuse, and schemas for execution-controlling results. Missing or malformed required output fails the attempt; correction requires a visible bounded policy. Do not ask those questions again.
- [Task scheduling and integration](task-scheduling-and-integration.md#resolution) already establishes findings-only default reviewers against a fixed revision, a separate repair writer, configured task and combined-candidate checks, bounded conflict repair, and preservation of stale work for refresh. Shared capacity is two agent sessions and two managed command steps per repository by default; parallel reviewers share that capacity.
- That scheduling contract also distinguishes a parked unintegrated candidate from stale content already in the combined result. Parking permits eligible independent integrations; integrated stale content pauses ordinary scheduling during refresh. Neither refresh nor another attempt resets existing budgets.
- [Session events and live progress](session-events-and-live-progress.md#resolution) owns durable visible attempts and immutable registered evidence. Historical evidence remains inspectable but cannot silently certify changed content. Rich usage telemetry may be unavailable; absence is not zero usage.
- [Operating and installation model](operating-and-installation-model.md#selected-executor-and-continuation) owns human-triggered Continue after interruption. Continue does not approve a checkpoint, reset a budget, or authorize blindly repeating uncertain effects.

### Confirmed answers, round one

On 2026-10-13, the human explicitly accepted all five recommendations:

1. **Check selection:** repository-defined task, integration, and final-result check sets with explicit required/advisory roles. Required failures block the associated gate; advisory failures remain visible. Agents may propose changes without silently weakening the configured checks. Agent-proposed check sets for each run were not selected as the default.
2. **Agent-led UI verification enablement:** off unless explicitly enabled through workflow settings or a run override, then run within budget without repeated permission prompts. A custom workflow may include an ask-first checkpoint. Deterministic browser E2E commands remain ordinary configured checks. Asking whenever applicable and automatically enabling exploration for UI changes were not selected as defaults.
3. **Parallel review aggregation:** require valid results from every required reviewer and block on any finding classified as blocking by the configured policy. Advisory findings do not block; missing or invalid required results cannot pass. Another reviewer's pass cannot outvote a blocking finding. Majority voting and a separate aggregate adjudicator were not selected.
4. **Checks after repair:** rerun all configured checks and reviewers at the affected gate by default. Explicit custom evidence-reuse rules must establish validity for unchanged inputs and relevant conditions, preserving the original evidence identity. Do not relabel reused evidence as a fresh run. Preferring selective reruns was not selected as the default. This does not enable previously disabled checks or repeat unrelated workflow stages.
5. **Budget structure:** per-loop repair limits plus a shared run-wide cap on additional agent attempts, including format corrections and fresh recovery sessions. Reconnecting to the same attempt does not consume another attempt. Per-loop limits alone were not selected. Round two below settles the starting numerical defaults; the resolution specifies accounting obligations.

These choices are settled and must not be asked again. They define configurable defaults and enforcement for the selected recipe, without replacing the accepted fully customizable workflow contract. Their practical tradeoffs are explicit: repository-defined checks need maintenance, opt-in exploration can leave UI behavior unexamined, any blocking finding can hold a gate, full affected-gate reruns cost more, and a shared limit can stop a run whose individual loops still have allowance.

### Confirmed answers, round two

On 2026-10-13, the human explicitly accepted all five recommendations:

1. **Default review placement:** review the final combined diff in the supplied recipe, retaining configured task and integration checks. Per-task, combined per-task/final, and disabled modes remain supported. Final-only review spends fewer review sessions but delays feedback. Per-task plus final by default and requiring an explicit selection on every run were not selected.
2. **Blocking findings:** actionable defects, unmet acceptance criteria, and violations of required repository rules block by default. Require evidence and an actionable explanation. Optional improvements and personal style preferences are advisory; repositories may customize the policy. Blocking only high-severity defects or every suggestion were not selected as defaults.
3. **Disputed or contradictory findings:** allow one visible clarification round with the relevant reviewer or reviewers, who may revise their findings with recorded reasons. Request human input if the conflict remains; the repair agent cannot dismiss blockers itself. Clarification sessions count against the shared agent limit. Going directly to human input without this bounded clarification was not selected as the default. This permits an attributed revision of a finding, not majority voting or silently dropping an unresolved blocker.
4. **Starting repair limits:** two code-repair attempts per loop and twenty additional agent attempts per run, both configurable. Additional attempts include repairs, repeated reviews, clarification, format correction, and fresh recovery sessions; initial planned attempts are separate. One repair/ten additional attempts and three repairs/thirty additional attempts were not selected. These are accepted starting defaults, not measured optimal values.
5. **Transient infrastructure retry:** at most one automatic retry per step for a recognized transient infrastructure failure, after reconciling prior effects. Test assertion failures follow quality repair rather than repeated execution until a pass. Preserve both attempts; a newly started agent session also consumes the shared agent allowance. Zero or two automatic infrastructure retries were not selected as defaults. This policy applies to a live managed run; it does not replace human-triggered Continue after runner interruption.

These choices are settled and must not be asked again. The shared allowance can be exhausted before any particular repair loop reaches its own cap. Neither an infrastructure retry nor a clarification may bypass the accepted recording, effect-reconciliation, freshness, or failure-isolation contracts.

### Confirmed answers, round three

On 2026-10-13, the human explicitly accepted all four remaining recommendations:

1. **Repair routing:** repairs from the final combined-diff review use one writer in a separate combined-candidate workspace, the configured repair profile, and a rerun of the final gate. Per-task review repairs stay in their task workspace and may reuse the compatible implementing session. Changed task versions still follow the accepted freshness rules. Routing every final finding back through its original task was not selected as the default.
2. **Malformed structured output:** allow one format-correction attempt using the saved output and validation errors, without rerunning implementation or authorizing code edits. It consumes an additional agent attempt, not a code-repair slot. If the corrected result remains invalid, the step remains unsuccessful. Stopping immediately without this correction was not selected as the default.
3. **Elapsed-time limits:** start with sixty minutes per agent attempt and thirty minutes per managed command step, configurable per step, plus an optional run-wide limit. Queue time and recorded human waits are excluded. Expiry requests interruption and preserves unfinished work; it does not silently renew the attempt. Requiring an explicit timeout for every step and having no default timeouts were not selected. These are starting defaults, not measured workload limits or guarantees of immediate process termination.
4. **Acceptance coverage:** link each acceptance criterion to a check, structured agent assessment, or configured human decision. Missing or unsatisfied evidence blocks acceptance; one result may support several criteria. Prose criteria remain supported and human review is not mandatory. An overall acceptance assessment without criterion-level links was not selected.

## Resolution

Closed on 2026-10-13 after fourteen explicit human decisions across three rounds. The exact prerequisite, `workflow-authoring-and-task-contract.md`, is closed. The confirmed-answer sections own the policy choices; the following contract applies them without changing the accepted authoring, scheduling, profiles, or human-triggered Continue policies. No next ticket is claimed.

### Gate contract and ownership

A verification gate is a workflow-selected set of checks, reviews, and acceptance obligations for a particular task, integration candidate, or final result. It is not a mandatory new workflow stage. Workflow code selects the gate, its required/advisory checks, and enabled review mode. The executor records and enforces attempts, limits, and outcomes; agents assess evidence and propose or perform the explicitly assigned work.

Each configured check has a stable logical identity, applicability/scope, required or advisory role, declared inputs, execution settings, and a result/evidence contract. Commands report their actual exit and structured results where configured. Agent-produced decisions use the accepted result-schema policy. An agent's clean exit or valid JSON alone cannot satisfy acceptance. A prerequisite failure may prevent later checks or reviews from starting, but work that did not run cannot count as a pass.

The recipe defaults to a final combined-diff review/refactor loop. Per-task-only, per-task plus final, and disabled reviews remain selectable; they do not remove configured command checks or acceptance obligations. Agent-led UI exploration is separately opt-in. Enabling it authorizes its configured managed attempts within the applicable limits, without a new permission prompt for every attempt.

Reviewers receive fixed input revisions and return findings with evidence, actionable explanations, and policy-relevant classification. Workflow code applies the configured blocking policy; no majority vote erases an outstanding blocker. Reviewer clarification can revise or withdraw a finding with an attributed reason while retaining its history. The repair writer may supply counter-evidence, but cannot approve its own dismissal of a blocking finding. An unresolved dispute after the selected clarification round requires human input.

Task repairs preserve their task lineage. Aggregate repairs create a separately recorded combined candidate; they do not edit the user's checkout or overwrite the reviewed evidence. Identify contributions superseded by a repair and apply the scheduling contract's consumer invalidation and refresh rules. Passing a final gate is not a shortcut around required refresh. Exact version representation and atomic acceptance remain with versioning and recovery.

### Accounting and termination

These are accounting obligations derived from the accepted limits, not new numerical policies:

| Managed work | Local limit | Shared additional-agent allowance |
| --- | --- | --- |
| First planned implementation, review, or other agent operation | Its configured attempt timeout | Not an additional attempt merely because it is discovered later in the admitted workflow |
| Code repair, including another repair turn in a reused session | Two code-repair attempts per configured loop by default | One for each new repair attempt |
| Repeat agent review or agent-led verification after repair | Governed by the loop and its own timeout | One per repeated agent attempt |
| Reviewer clarification | One round for the disputed finding set | One per participating agent attempt, not one for the entire parallel round |
| Format correction | One correction for the invalid result, using its saved output | One per correction attempt; no code-repair slot |
| Recognized transient infrastructure retry | One retry per logical step execution by default | One if another agent attempt is started; command-only retries use no agent allowance |
| Fresh-session recovery | Accepted explicit recovery policy and retained budgets | One for the new attempt |
| Reconnect to the same interrupted attempt | Continue and effect reconciliation still apply | No new attempt debit |

The shared default is twenty additional agent attempts per run. Preserve counters across Pause, Continue, process restart, session reuse, and refresh. Record attempt purpose and lineage so a retry, repair, repeated reviewer, or correction cannot become a supposedly initial operation merely by changing its ID. A repaired revision can require a new check execution, but repeating a failed execution against the same inputs does not reset its infrastructure retry allowance. Corrections do not recursively receive fresh correction budgets.

A repair attempt consumes allowance even if it makes no useful change; a failed repair must not become free work. Multiple findings handled by one repair attempt do not create multiple repair debits. Admitting parallel work must respect shared remaining capacity and budget before launch; recovery must reconcile uncertain launches without permitting duplicate spending or effects. Exact reservation and reconciliation transactions belong to the recovery ticket.

Exhausting two repair attempts prohibits a third repair; it does not skip the checks needed to evaluate the second repair. Those checks and reviewer attempts still require their own remaining allowance. For example, two initial reviewers followed by two repair rounds cost six additional agent attempts: two repairs and four repeated reviews. Deterministic command reruns do not consume agent attempts. A separate clarification or correction adds its own debit.

Exhaustion blocks further work requiring that allowance. Already admitted work remains governed by its existing limits. Follow the accepted independent-branch failure policy; a required incomplete gate still prevents run success. Continue alone never extends or resets a limit. Authorization and recording for deliberate budget changes belong to human control and workflow versioning.

Attempt timeout accounting starts with the managed execution, excluding queued capacity/resource waits and recorded human waits. Silence is not a recorded human wait. Preserve consumed time when reconnecting to the same attempt; restarting the runner does not renew that attempt's timer. A genuinely new, authorized attempt has its own timeout and consumes the applicable attempt allowance. Expiry requests graceful interruption and reconciliation; do not automatically classify a timeout as a recognized transient infrastructure error. Signal escalation and unresolved child-process ownership retain their human-control/recovery owners.

The extra-attempt cap does not bound initial planned work, exact tokens, or monetary cost. A run-wide time limit is optional, not silently set by this ticket. Show available usage as reported, estimated, or unknown under the accepted profile contract. If a workflow requires a hard token/cost limit the adapter cannot enforce, reject that unmet requirement unless an explicit alternative policy applies. Delayed or estimated usage cannot be presented as a guaranteed spending ceiling.

### Evidence, disabled checks, and outcomes

Criterion coverage records the criterion, its scope, the evidence/assessment/decision, the evaluated content and relevant inputs, and the outcome. One retained result may cover several criteria without repeating the work. Label a reasoned agent assessment as such; it is not an executed test or a human sign-off. Human decisions are required only where configured. Task-scoped acceptance and final combined-result acceptance remain distinguishable.

After code repair, rerun the configured affected gate by default. A custom reuse rule must establish that the earlier evidence still applies to the declared inputs and relevant conditions, including the check/review definition, relevant content, tools/settings, and any external state on which it depends. Unknown validity requires fresh work. A revision-wide review cannot certify a changed reviewed diff. Preserve the original evidence identity, revision, and time, and explicitly record why it was reused. Historical task checks can remain valid evidence of their original scope without being mislabeled as checks of a newer combined revision. Ordinary unrelated integrations still do not blanket-invalidate all tasks; the scheduling freshness policy and configured combined-candidate checks remain in force.

The following distinctions follow from required/advisory checks and criterion coverage; the labels describe outcomes rather than finalize database enums:

| Situation | Acceptance consequence |
| --- | --- |
| All applicable required checks, reviews, and criterion evidence are satisfied for the current scope | The gate may accept; subsequent workflow gates and publication authorization still apply |
| Advisory finding/failure remains | Show it in the result; it does not alone block acceptance |
| Optional check or UI exploration is disabled, or declared applicability excludes a check | Record that it did not run and why; never call it passed. Another valid evidence route must cover any criterion that still requires evidence |
| Required check is unavailable, failed, invalid, or interrupted | The gate remains unsatisfied; an unavailable tool is not equivalent to disabled policy |
| Evidence is missing, stale, or fails a criterion | Preserve it for inspection; the affected scope cannot be accepted as current |
| Dispute, exhausted budget, or unreconciled interruption prevents progress | Preserve the incomplete result and the reason; human input or an authorized recovery/policy change may be needed |

A successfully finished workflow report names the configured checks it satisfied and the advisory or unperformed work. It does not claim universal verification. An intentionally disabled review mode does not erase an existing required acceptance criterion. Failures cannot be concealed by silently disabling, weakening, or repeatedly rerunning a failing test until it passes.

### Scenario checks

**Quick change:** a prompt produces one task with explicit acceptance criteria. Run its declared checks, then the configured combined-candidate checks. Review the final diff using the selected reviewers. If an input-validation bug blocks acceptance, a separate repair writer fixes the combined candidate and the final gate reruns on that revision. Link a relevant test and, where appropriate, a structured assessment to each criterion. Agent-led browser exploration stays visibly disabled unless enabled; a deterministic browser test may still run if configured. Optional human pre-PR review and publication remain separate workflow choices.

**Task graph:** A and B are independent; C depends on both. A and B use isolated worktrees and integrate in ready-result order after their configured gates. C receives the accepted combined revision. Default review examines the final combined diff after all required tasks integrate. If the workflow selects per-task plus final review, each task also runs its own review/repair loop; all additional attempts share the twenty-attempt default. A final cross-task defect is repaired in a separate combined candidate, with freshness/refresh rules applied and the final gate rerun. Required criterion coverage must be satisfied at its declared scope; passing an earlier task gate alone does not prove a later cross-task interaction.

**Interrupted or disputed work:** after a crash, old checks and findings remain visible. Human-triggered Continue reconciles work and uses the retained counters, inputs, and evidence-validity rules. A disputed blocking finding gets its one recorded reviewer-clarification round if allowance remains. An unresolved dispute waits for human input. Neither Continue nor a prior approval converts an old finding, stale check, or incomplete criterion into a current pass.

### Implementation acceptance obligations

These are future proof obligations, not completed runtime tests:

- Exercise final-only, per-task-only, combined, and disabled review modes; task/integration/final check sets; and required versus advisory outcomes. Demonstrate optional agent-led UI exploration without repeated permission prompts when enabled.
- Run parallel reviewers against the same revision. A blocker survives another reviewer's pass, a malformed required result cannot pass, and a repair agent cannot silently dismiss a finding. Retain one clarification round and any attributed revision of findings.
- Enforce two repair attempts per loop and twenty additional agent attempts across nested/parallel work. Include repeated reviews, session reuse, format corrections, fresh recovery, no-op repairs, and crash-adjacent launches. Renaming operations must not reset budgets.
- Retry a recognized transient infrastructure failure at most once; do not retry an assertion failure until green. Exercise invalid-output correction without repeating implementation or granting code-edit authority. Preserve failure history and uncertain effects.
- Exercise attempt timeout, queue time, recorded human wait, Pause, and Continue. Preserve elapsed-time and attempt accounting; show unsupported hard spending limits honestly. Native process-stop behavior requires its own platform evidence.
- Change code after review and verify affected-gate reruns, retained historical evidence, explicit valid reuse, and rejection of stale or unverifiable reuse. Exercise combined repair without bypassing stale-consumer refresh.
- Show criterion-level coverage using command results, structured assessments, and optional human decisions. Missing evidence and required unavailable/disabled work cannot create a false pass; advisory or deliberately unperformed optional work stays visible.
- Run the quick-change and task-graph scenarios, including a shared budget exhausted before a local loop cap, and confirm required unfinished work prevents overall success while eligible independent branches follow the accepted scheduling policy.

### Downstream owners and limits

- [Human control and publication](human-control-and-publication.md) owns responses to unresolved disputes and exhausted limits, checkpoint controls and authorization, stale/duplicate human answers, publication identity, and process-stop escalation. Optional pre-PR approval remains optional.
- [Workflow versioning and run changes](workflow-versioning-and-run-changes.md) owns authorized edits to policies, budgets, criteria, profiles, and plans in unfinished runs, retained versions, and repair-output representation. An agent cannot silently rewrite a gate to pass it.
- [Recovery guarantees and runtime selection](recovery-and-runtime-selection.md) owns durable counter/timeout enforcement, launch reconciliation, fencing, atomic candidate acceptance, and evidence/version compatibility under Continue.
- [Swimlane interaction design](swimlane-interaction-design.md) owns presentation of coverage, gates, findings, budgets, retries, warnings, and disabled/unavailable work using the accepted saved-event model.
- [Specification readiness and acceptance](specification-readiness-and-acceptance.md) assembles these defaults and obligations with the other closed contracts. Check commands, reviewer count, model choices, and numerical overrides remain repository/workflow configuration rather than universal prescribed values.

No new ticket is needed: remaining implementation mechanisms already have downstream owners. No outside capability claim required new research. No executor, adapter, browser, timeout, budget, or recovery behavior was implemented or tested in this planning conversation.

