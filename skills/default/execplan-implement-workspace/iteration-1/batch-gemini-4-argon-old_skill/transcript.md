# Copilot CLI Session

> [!NOTE]
> - **Session ID:** `07e838b8-63a1-4833-be3b-d8588dd487b9`  
> - **Started:** 10/19/2026, 1:11:07 PM  
> - **Duration:** 38s  
> - **Exported:** 10/19/2026, 1:11:46 PM  

---

<sub>1s</sub>

### User

Evaluate the scenarios below using ONLY the supplied source skill /Users/adam/dev/skills/skills/default/execplan-implement-workspace/skill-snapshot/SKILL.md. Ignore all installed copies of execplan-implement. This is read-only document interpretation, not workflow execution. Do not run tools, change files, commit, or dispatch. Treat each scenario independently. Answer each under exactly ## Eval \<id>, max 220 words per scenario. Do not grade yourself.

FILE: /Users/adam/dev/skills/skills/default/execplan-implement-workspace/skill-snapshot/SKILL.md
---
name: execplan-implement
description: Implement an ExecPlan in code.
disable-model-invocation: true
---

You have been provided an ExecPlan with milestone acceptance and a Progress checklist.

The goal is to implement and verify the authorized ExecPlan work on one branch, with commits for implementation changes and evidence for milestone acceptance.

Before creating any commit, read and follow [commit message guidelines](references/message.md). Apply them to every commit created by the primary agent or a subagent.

The **frontier** of the plan's task graph contains unfinished tasks whose prerequisites are verified and whose execution is authorized. If none are ready, report the blockers and next owner action instead of inventing work.

Run independent **implementer subagents** concurrently when useful. Serialize shared files, shared state, and integration.

## Steps

1. Activate the `exec-plans` and `delegate-to-subagents` skills.

2. Read and reconcile the ExecPlan using `exec-plans`, then select the frontier.

3. (optional) Use an **exploration subagent** to conduct any exploration required by the progress checklist items - relevant codebase files or external documentation. Ensure the exploration subagent can save files - it should save its markdown notes beside the ExecPlan, accessible by all future subagents. This lets **implementer subagents** focus on implementation rather than exploration.

4. If current branch is `main` or `master`, create a new **base topic branch**.

5. Repeat steps 5-7 while authorized tasks are ready. You - the primary agent - coordinate this loop; subagents perform implementation. Add or reopen a task only to satisfy an authorized requirement or repair a reproduced failure within that scope. Record unrelated improvements as deferred; keep them outside the execution frontier. When authorized acceptance criteria are met, finish the task. Record necessary repairs with prerequisites, then delegate them through this step.

   Assign each distinct task to a fresh implementer subagent. Do not reuse an implementer for a different node, even with a new worktree. Reuse is allowed only for repairs or follow-up work on that implementer's original node. This preserves context isolation, ownership clarity, and independent task results.

   Before dispatch, apply `delegate-to-subagents` ownership rules to shared canonical docs, even across private worktrees.

   Pass each implementer its full task and current plan context as required by `exec-plans`, plus prerequisite evidence and explicit file ownership. Instruct it to:
   1. Activate the `tdd` skill for source changes. Use task-appropriate evidence for decision, verification, integration, or documentation work; do not invent product tests or code changes for a read-only outcome.
   2. Make repository changes in its own worktree and branch (see [Working with Worktrees](#working-with-worktrees)). A read-only task needs a retained evidence result, not an empty commit.
   3. Follow [commit message guidelines](references/message.md).
   4. Keep its branch private and unpushed because integration rebases it.

6. Integrate completed **implementer subagent** branches into the **base topic branch** one at a time:
   1. Confirm the implementer's worktree is clean, then rebase its branch onto the latest **base topic branch**.
   2. If there are conflicts, resolve them and rerun the affected tests. For a conflict-prone rebase, stop the implementer and give a **merger subagent** exclusive ownership of the existing implementer's worktree before the rebase starts. The merger rebases the implementer branch and does not mutate the base branch. A conflict-free rebase does not waive required integration checks: reuse evidence only when it covers the resulting tree and relevant interactions; otherwise run the affected checks.
      If affected tests fail, pause integration of that branch. Record the required repair as unfinished work in the ExecPlan and delegate it to an **implementer subagent** through step 5. Resume integration after the repair passes the affected tests.
   3. Update and commit any ExecPlan references to SHAs changed by the rebase, then confirm the implementer's worktree is clean.
   4. Confirm the base worktree is clean, then fast-forward the base branch with `git merge --ff-only \<implementer-branch>`.
   5. Confirm the base branch tip matches the verified implementer branch tip. Once related prerequisites are integrated, execute the plan's composed-behavior proof on base, or delegate it as the named integration task. If it fails or remains unrun, keep milestone acceptance unmet and record the repair or blocker.
   6. After each fast-forward, remove clean worktrees and local branches for the integrated node, including superseded repair/merger branches once their changes are verified on base. Preserve base and unrelated worktrees.

   Serialize this integration sequence so concurrent completions cannot race to update the base branch.

7. After each task result or integration, reconcile the plan using `exec-plans`; verify retained evidence for read-only tasks before marking them complete. Reassess the **frontier**, including repairs, and return to step 5 for ready items. Independent authorized work may continue while repairs or owner actions are pending.

8. When authorized work is complete or blocked, reconcile and report the plan using `exec-plans`, including the base branch's actual state. Preserve unfinished work and evidence; clean up only verified clean integrated worktrees.

## Working with Worktrees

For parallel AI agent work, use git worktrees to run multiple branches simultaneously:

```bash
# Create a worktree for a feature branch
git worktree add ../project-feature-a feature/task-creation
git worktree add ../project-feature-b feature/user-settings

# Each worktree is a separate directory with its own branch
# Agents can work in parallel without interfering
ls ../
  project/              ← main branch
  project-feature-a/    ← task-creation branch
  project-feature-b/    ← user-settings branch

# After integration, clean up the worktree and it's associated branch
git worktree remove ../project-feature-a
git branch -d feature/task-creation
git worktree remove ../project-feature-b
git branch -d feature/user-settings
```

Benefits:

- Multiple agents can work on different features simultaneously
- No branch switching needed (each directory has its own branch)
- Preserve unfinished changes and evidence before removing an experimental worktree
- Changes are isolated until explicitly fast-forwarded into the base branch


FILE: /Users/adam/dev/skills/skills/default/execplan-implement-workspace/skill-snapshot/references/message.md
# Commit message

## First line

Use Conventional Commit format:

```text
<type>: <subject>
```

or:

```text
<type>(<scope>): <subject>
```

Rules:

- Subject is imperative.
- Max 72 characters.
- No trailing period.

## Type

Choose the first matching type:

1. `docs`
2. `test`
3. `fix`
4. `feat`
5. `refactor`
6. `perf`
7. `chore`

Use `fix` only for bug fixes.

## Subject fallback

If no better subject is clear:

1. `update <file-basename>`
2. `update <directory>`
3. `update changed files`

## Body format

```text
<type>(<scope>): <subject>

Summary:
- <what changed>

Rationale:
- <why>

Tests:
- <command or "not run (reason)">

Session: <optional session note>
Refs #123
Fixes #456
Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
Co-authored-by: Jane <jane@example.com>
```

Rules:

- Keep one blank line after the subject.
- `Summary`, `Rationale`, and `Tests` are required.
- Each required section needs at least one bullet.
- Omit `Session:` if no reliable session data exists.
- Use `Fixes` only when the user explicitly says fix, close, bug, or bugfix.
- Otherwise use `Refs`.
- Keep issue trailers and co-author trailers contiguous.
- Do not add blank lines between trailers.
- Add default Copilot co-author unless explicitly declined.
- Add extra co-authors after the Copilot trailer.


FILE: /Users/adam/dev/skills/.agents/skills/exec-plans/SKILL.md
---
name: exec-plans
description: Mandatory when starting, resuming, executing, orchestrating, reading, modifying, discussing, or touching any 'exec-plan', 'ExecPlan', 'execution plan', '*ExecPlan*.md', or '*exec-plan*.md' file. Always use for complex tasks across multiple layers, multiple scripts, system-wide refactors, multi-milestone features, or phased work without a plan. Load before inspecting or editing ExecPlan files.
---

# Execution Plans (ExecPlans)

An ExecPlan is the working contract for a feature or other multi-step change. Write it for a novice who has the current working tree and this plan, but no memory of earlier conversations or plans. The plan must explain what to do, how to verify it, and what remains current at every checkpoint.

## Invocation and pre-code gate

Load this skill before inspecting or editing an existing ExecPlan. If work needs a plan, create the file at the requested location before the first code edit. When no location is specified, use the project's established plan location; if none exists, create `docs/<feature-slug>/ExecPlan.md`. Verify that the file exists before changing implementation code. Saying that you will write a plan later does not satisfy this gate.

When authoring, read the relevant source and supplied requirements, start from the annotated outline below, and fill it in as you research. Resolve ordinary ambiguities from the available evidence and record the choice and rationale in the plan. Do not leave key implementation decisions for a novice reader to guess.

When executing, proceed to the next planned milestone without asking the user for routine next steps. Resolve ordinary implementation ambiguities autonomously within the agreed scope. Honor explicit stopping points, required approvals, and owner-only actions; when one blocks progress, record the missing decision or permission and continue independent authorized work. Follow the project's commit workflow.

## Write a self-contained plan

Start with the user benefit and the behavior a person can observe when the work succeeds. Explain the relevant project structure, assumptions, unfamiliar terms, exact files and interfaces, commands, expected results, and safe recovery steps. Include the facts a novice needs directly in the plan. External references may supplement the instructions, but the plan must not depend on them for its current contract or next action.

Use milestones when work has distinct checkpoints. Each milestone must describe the work, how to verify it, and what observable result marks it complete. Add these state lines at the start of every milestone:

    Status: done | in progress | open
    Acceptance: met | not met

Keep the narrative precise and testable. Name the working directory for commands, show expected output where it helps, and describe behavior a person can verify rather than only internal code changes. Include idempotence, rollback, dependencies, interfaces, and evidence when they affect successful or safe execution. Define specialized terms in plain language.

A milestone is a delivery and acceptance outcome, not automatically one task. A **task** is an independently assignable unit of work with explicit prerequisites, required inputs and current design context, an outcome, verification, and a stopping boundary. Before dispatch, assess its behavioral scope, unresolved decisions, coupled state, and verification burden. Keep each task bounded by splitting independently deliverable behaviors into separate tasks. Preserve necessary negative cases and indivisible correctness rules. A difficult but inseparable task needs clear reasoning risks and entry points, not reduced acceptance. Resolve a design uncertainty through a bounded decision or feasibility task before dependent implementation.

Name files with full repository-relative paths, identify the exact functions or modules to edit, and say where new files belong. Explain how affected areas fit together. State environment assumptions and provide reasonable alternatives when commands or results vary by environment. Carry required knowledge from references or prior plans into the active plan in your own words, so the reader can proceed without retrieving them.

Design steps to be repeatable. Explain how to detect and recover from a partial failure, including safe retries and backups or fallbacks for destructive work. Prefer additive, testable changes that can be validated before replacing existing behavior.

## Validation and observable acceptance

Validation is required. State the exact test commands for the project's toolchain, their working directories, expected results, and how to interpret failures. Cover new behavior, relevant error cases, and existing behavior that must remain intact. Include expected output and diagnostic messages so a novice can distinguish success, a product defect, and a missing environment prerequisite. Mark proposed results as expectations until they have actually been observed.

Explain how to start or exercise the system when applicable. Demonstrate useful behavior beyond compilation through a small end-to-end scenario, direct CLI invocation, or request/response example with specific inputs and outputs. For an internal change, identify a test or observable scenario that exposes its effect; for a bug fix, record how the reproducer fails before the change and passes after it. Successful compilation alone does not establish acceptance.

Run the relevant checks at each milestone and retain concise evidence of the actual result. If a check cannot run, state why and what remains unverified rather than treating planned verification as proof. Use small transcripts, file-scoped diffs, or focused excerpts that show what establishes success; keep full run logs behind evidence references.

When several tasks contribute to a milestone, name their shared invariants and the integration task or milestone check that proves their combined behavior. Run that proof against the integrated result, including relevant regression and negative cases. Passing individual tasks, clean Git merges, or checked progress entries do not establish milestone acceptance while that proof remains missing.

## Required living sections

Every ExecPlan keeps these sections current:

- `Purpose / Big Picture` explains the user outcome and how to observe it.
- `Progress` records completed work, current work, and the next action in a milestone-tagged checklist.
- `Surprises & Discoveries` records relevant findings with concise evidence.
- `Decision Log` records current decisions and why they were made.
- `Outcomes & Retrospective` states what is complete, what remains, and lessons that affect the work.

Also include the project context, plan of work, concrete steps, validation and acceptance, and recovery guidance needed to carry out the task without prior context. Add interface, dependency, or artifact details when they materially help a novice proceed.

Each milestone has matching Progress entries tagged `[milestone-X]`; split partially completed work into completed and remaining steps. A completed milestone uses `Status: done`, `Acceptance: met`, and checked entries such as `- [x] (YYYY-MM-DD) [milestone-X] ...`. Open or in-progress work keeps its remaining entries unchecked. Update the milestone's status, acceptance, and every affected Progress entry in the same edit. Do not mark work done without evidence that its acceptance is met.

Milestones describe the goal, work, result, and proof in prose; Progress tracks the granular steps. Make each milestone independently verifiable and useful toward the overall outcome. Include the context needed for that milestone even when brevity would suggest dropping it. At major milestones or completion, compare the results with the original purpose in `Outcomes & Retrospective`.

Record tasks, their prerequisites, and completion evidence in the plan, mapped to milestones and Progress. A **task graph** records tasks and their explicit prerequisite relationships; named tasks with prerequisite lists are sufficient to describe it. Progress entries track a task's state, and one task may span several entries. Do not infer dependencies from checklist order or duplicate work as both a whole-milestone task and its component tasks. A ready task still requires current authorization. Shared files or state can require serialization even without a dependency edge.

## Prototypes and migration paths

Use explicit prototyping milestones when a significant unknown could invalidate the design. Read relevant dependency source or documentation and capture the findings needed to assess feasibility. Keep prototypes additive and testable, label their limited scope, give exact commands and observable results, and state the criteria for promoting, reworking, or discarding them. When several new libraries or feature areas are involved, consider independent feasibility experiments so a failure in one does not hide the behavior of another.

During a migration, keep old and new implementations alongside one another when that reduces risk or preserves working tests. Specify how to validate both paths on the same relevant inputs, what differences are acceptable, and what evidence permits switching the default. Describe how to retire the old path safely with tests and a recovery strategy. Prefer additive changes followed by removal only after the replacement has met its acceptance criteria.

## Reconcile the plan as work changes

Reconcile an existing plan whenever you resume work, change scope or approach, complete a milestone, or stop work for a checkpoint. Compare the active plan with the current source, tests, task status, and user instructions. Correct the plan from current evidence; a plan's earlier status, transcript, or approval claim does not establish what is true now.

Replace outdated statements wherever they appear in active sections. A correction only in a new note is insufficient. Update the sections affected by the change, including milestone states and Progress, Concrete Steps, Validation and Acceptance, Decision Log, Outcomes, and the next action. When scope or approach changes, also update the purpose, acceptance, dependencies, and remaining milestones as needed.

In Concrete Steps, lead with the next unfinished, authorized action. Remove completed implementation instructions or label them explicitly completed. A completed milestone and an unqualified instruction to implement it cannot remain current together. Keep past command results as verification evidence rather than presenting them as work still to do.

At a stop, leave a reader able to tell what has been verified, what remains unfinished, who owns the next action, and what to do next. If current evidence cannot be inspected, state that limit instead of claiming the work is complete or unchanged. Continue to the next planned milestone only while it remains within the user's scope and authorization.

## Keep the current contract separate from history

The active plan is the single place to learn current requirements, decisions, status, safety limits, and next steps. Keep pending recovery instructions, security and authorization boundaries, owner actions, and external validation inline in active sections whenever they constrain the work. State who must act, what approval is required, what has or has not happened, and the condition for recovery. Never rely on an old transcript or a separate history file to establish current permission or status.

Give current requirements and active decisions stable headings or identifiers when tasks reference them. Keep the required facts inline in the self-contained plan and update affected task references when a decision changes. References help a worker locate the current rule; they must not force the worker to reconstruct it from superseded history.

Preserve useful current decisions, lessons, and unique evidence before moving material out of the active plan. Keep evidence needed for current status or acceptance inline. For historical material that can leave the active plan, first reuse an existing retained artifact or create a clearly labeled sibling snapshot. Add a link to it under a clearly titled historical section, verify that the target exists and still contains the unique dates, commands, results, or decisions being moved, and only then replace the inline material. A link to the active plan itself is not an archive. If the archive cannot be verified, keep the evidence inline and report the limitation.

Keep the current rationale concise in `Decision Log` and useful findings in `Surprises & Discoveries` or `Validation and Acceptance`. Move superseded run transcripts, outdated status statements, and revision narratives behind the verified historical reference when their provenance matters. Historical material is background only: it never authorizes work, overrides user instructions, or controls present state. Do not append a full revision narrative after every update, and do not make a reader search history to continue.

For substantive changes in scope or approach, record what changed and why in the relevant living sections, including a dated decision when needed. Routine progress or editorial corrections need only update the affected current sections; they do not require a separate revision footer.

## Formatting and evidence

Write a saved ExecPlan as plain Markdown. If delivering the plan in a response, use one fenced `md` block and indent any nested examples rather than adding inner fences. Use headings and readable prose; reserve checkboxes for `Progress`. Prefer prose to tables or long lists in narrative sections. Keep examples and captured output short and focused on proof.

## Outline

Use this annotated outline and adapt detail to the work. The file-reporting example shows how a milestone, tasks, and Progress entries relate. Its paths and commands describe a hypothetical Python CLI; replace them and the instructional placeholders with verified project facts.

    # <Action-oriented title>

    This ExecPlan is a living document. Keep Progress, Surprises & Discoveries,
    Decision Log, and Outcomes & Retrospective current. Name this plan's
    repository-relative path and the applicable planning guidance.

    ## Purpose / Big Picture

    Explain what a user gains and how to see the new behavior working.
    State the scope and constraints that define success.

    ## Progress

    Use milestone-tagged checkboxes for granular work. At each checkpoint,
    split partly completed work into completed and remaining entries.
    Date completed entries using actual dates; leave unstarted work unchecked.
    Name the task when an entry tracks part of its work. Here the first
    two entries track T1; the final entry tracks the milestone's combined proof.

    - [ ] [milestone-1] T1: Implement list-backed file reporting.
    - [ ] [milestone-1] T1: Verify valid, empty, and malformed inputs; record evidence.
    - [ ] [milestone-1] T2: Implement stream mode and verify the same input cases.
    - [ ] [milestone-1] Verify both modes together on the integrated CLI; record evidence.

    ## Surprises & Discoveries

    Record unexpected behavior, bugs, tradeoffs, or insights that affect
    the current approach. Include a concise evidence snippet or result.

    - Observation: <finding>
      Evidence: <actual command, output, or source location>

    ## Decision Log

    Record current decisions and the rationale needed to continue safely.
    Explain substantive changes in scope or approach here.

    - Decision: <choice>
      Rationale: <why it meets the requirements or resolves an ambiguity>
      Date/Author: <actual date and contributor>

    ## Outcomes & Retrospective

    Compare achieved results with the purpose at major milestones and
    completion. State remaining work and useful lessons. Distinguish
    completed implementation from pending acceptance or owner actions.

    ## Context and Orientation

    Explain the relevant current state to a reader unfamiliar with the
    project. Name key files and modules by full repository-relative path,
    explain how they connect, and define non-obvious terms and assumptions.
    Include needed context from earlier work directly here.

    ## Plan of Work

    Describe the sequence of edits in prose. For each edit, identify the
    file, function or module, and what to insert or change. Name new files.
    Use milestones for distinct outcomes, including prototypes when needed.

    ### Milestone 1: Report file summaries through list and stream modes
    Status: open
    Acceptance: not met

    Users can summarize a UTF-8 file containing one signed decimal integer
    per line with --input PATH and --engine list or --engine stream. Both
    modes print count=N total=S; empty input produces count=0 total=0.
    A blank or malformed line causes exit 2, a one-based line diagnostic
    on stderr, and no stdout summary. This shared contract applies to both
    tasks. The milestone requires matching outcomes from the integrated
    CLI, including negative cases, before acceptance is met.

    #### Task T1: Deliver list-backed file reporting

    Prerequisites: none. Inputs and current context: the shared contract above,
    summarize(rows) in src/reporting.py, and the CLI in src/report_cli.py.
    Add line parsing and list-backed --input handling through the CLI, with
    tests in tests/test_file_reporting.py. The outcome is usable file reporting
    that satisfies the full success and error contract for --engine list.

    Verification: from the project root, run
    `python3 -m unittest discover -s tests -p test_file_reporting.py`.
    Expect exit 0, with valid, empty, blank-line, and malformed-line cases
    checking stdout, stderr, and exit status. Record actual results here.
    Stop after list-backed reporting and its checks pass; stream mode is T2.
    The two T1 Progress entries track implementation and proof of this one
    task. Both are needed before T1 is complete.

    #### Task T2: Add stream mode with the same behavior

    Prerequisites: T1 is complete with recorded evidence. Inputs and current
    context: the shared contract above and T1's parser, CLI, and tests.
    Add single-pass aggregation in src/reporting.py and --engine stream in
    src/report_cli.py. Extend tests/test_file_reporting.py to cover both modes
    and a one-pass input that cannot be sized or iterated twice.

    Verification: run the same focused command from the project root; expect
    exit 0 and the same required success and error outcomes for both modes.
    Record actual results here. Stop after stream mode and these checks pass;
    additional input formats and performance targets are outside this task.

    #### Milestone integration check

    After T1 and T2, the coordinator runs the full suite from the project root:
    `python3 -m unittest discover -s tests`. Its CLI checks run identical valid,
    empty, blank-line, and malformed-line fixtures through both modes, compare
    stdout, stderr, and exit status, and assert the expected contract as well
    as parity. Expect exit 0. Record the integrated result before checking the
    final Progress entry and setting Status: done and Acceptance: met.

    For other milestones, adapt the tasks and combined proof to their
    actual outcomes. A task may map to one or several Progress entries;
    update those entries as its work advances without changing its scope.
    For a prototype, state promotion/discard criteria. For a migration,
    explain both-path validation and the gate for switching or retiring a path.

    ## Concrete Steps

    Lead with the next unfinished, authorized action and its owner.
    State exact commands and working directories, followed by short expected
    output where useful. Mark observed results as evidence. Remove completed
    implementation instructions or label them completed as work proceeds.

    ## Validation and Acceptance

    Describe how to exercise the behavior with specific inputs and outputs.
    Give the exact test command, expected result, and interpretation of
    failures, including relevant error messages and exit codes. Where known,
    name the test that fails before a fix and passes after it. Distinguish
    expected results from actual evidence and pending external validation.

    ## Idempotence and Recovery

    State which steps can be repeated safely. Give retry, cleanup, backup,
    or rollback instructions for partial failures or risky changes, including
    the trigger, responsible owner, and any approval or retention condition.

    ## Interfaces and Dependencies

    Name required libraries, modules, and services and explain why they fit.
    Specify the types, interfaces, and function signatures that must exist,
    using stable names and paths. Include an exact declaration when useful:

    In src/reporting.py, define:

        from collections.abc import Iterable

        def summarize(rows: Iterable[int]) -> dict[str, int]:
            ...

    Explain the inputs, outputs, and failure behavior required by callers.

    ## Artifacts and Notes

    Include concise transcripts, diffs, or snippets that establish current
    acceptance. Link larger evidence artifacts with an explanation of what
    they prove. Put superseded material under Historical Records only after
    verifying the retained target and preserving current requirements inline.

Keep the required living sections present throughout the work. Add `Artifacts and Notes` only when transcripts, outputs, or other evidence materially help the next contributor.


FILE: /Users/adam/dev/skills/skills/default/delegate-to-subagents/SKILL.md
---
name: delegate-to-subagents
description: Use subagents when parallel execution, specialized expertise, or context isolation is likely to improve results enough to justify coordination overhead. Also use when the user explicitly asks to delegate, create, spawn, dispatch, or fan out subagents.
---

# Delegate to Subagents

Delegate when parallel work, specialized expertise, or context isolation outweighs coordination overhead.

## 1. Define assignments

For each subtask, specify an identifier, objective, necessary context, constraints, deliverable, verification criteria, allowed resources, write ownership, dependencies, and runtime limit. Resolve applicable fields before dispatch; mark others `none` or `not applicable`.

Run independent work in parallel and dependent work in waves. Serialize edits to shared files. Give each shared canonical document one integration owner or an explicit serial dependency. Workers retain scoped evidence and promptly notify the owner of durable findings, including critical guidance. Exclusive area documentation remains worker-owned. The coordinator reconciles admitted findings and completes the final documentation pass after all tasks finish.

Ask only for essential missing task facts. Avoid duplicate reads and context gathering; consider one exploration worker when several workers need the same context. The coordinator may read files to plan, coordinate, resolve conflicts, and verify results.

## 2. Route

Activate the `subagent-model-router` skill for each materially different subtask. Supply its required task facts, existing user model/effort constraints (or `none`), and exact supported values discovered from runtime metadata or the dispatch interface. The router owns capability, cost, fallback, and route-reuse rules.

This workflow authorizes selecting and explicitly applying the router's model and reasoning effort without separate model-selection confirmation. Missing preferences are not ambiguity. Do not solicit a model or effort before routing. Configured defaults apply only when the user explicitly requests them; resolve and validate concrete values through the router.

Keep the complete router decision available for dispatch and verification. A separate route file or completion ledger is not required. Persist decisions only when requested or needed for recovery or an existing audit requirement; use one session artifact outside maintained source and reuse it for revisions and results.

Dispatch requires all of the following:

- `dispatchable: true` and exact runtime-supported `model` and `reasoning_effort` values;
- task facts, capabilities, and user constraints valid for the current routing attempt;
- explicit submission of both values outside the worker prompt;
- an explicit runtime limit and a mechanism to monitor it;
- satisfied dependencies and no pending required approval.

Omitted, null, inherited, placeholder, ranged, or runtime-selected values do not qualify. If no exact route is possible, inspect accepted values, reroute with new evidence, and report any unresolved limitation without dispatching. If an explicit user constraint blocks routing, explain the limitation before asking the user to revise it.

Reuse routes only under the router's reuse criteria; still apply and check every dispatch. Reroute when work class, stakes, security sensitivity, ambiguity, affected behavior, review history, context, verification requirements, user constraints, or runtime capabilities materially change. If a configuration becomes unavailable, exclude it and let the router choose a complete replacement without lowering the capability floor.

## 3. Announce and dispatch

Announce roles and scope in one concise sentence. Show raw routing or audit data only on request; explain blockers and material failures briefly.

Route before any approval. Pause only for preexisting user-requested or runtime-required approval, then dispatch the completed route after approval. A new model/effort constraint or changed runtime capability invalidates the route; begin a fresh attempt instead of modifying values to match an approval response.

If you improperly solicited a preference before routing, invalidate routes derived from it and disclose the sequencing error. Start again with the original constraints; include the solicited value only if the user clearly makes it a new requirement.

Give workers their assignment, required dependency results, and nested-delegation policy. Prohibit nested delegation unless intentionally authorized. Tell workers they share the codebase, must preserve others' edits, and must stay within their write ownership.

Keep workflow-generated routing and audit metadata out of worker prompts: model, effort, tier, rationale, fallback, escalation trigger, and instructions to identify or report execution settings or dispatch compliance. Task-relevant source material may mention these subjects. The coordinator owns configuration and verification.

Submit the exact routed model and effort through dispatch controls. Start every ready, independent, compliant assignment before waiting.

## 4. Verify and coordinate

Inspect actual dispatch arguments and runtime-control state. Compare submitted model/effort with the route and check runtime monitoring. Distinguish selected, submitted, and executed settings: only runtime metadata confirms executed values; otherwise they remain `unconfirmed`. Worker self-reports are not runtime confirmation.

If submitted values are missing or differ from the route, mark the dispatch noncompliant and do not describe it as router-selected. Cancel it if supported and safe; otherwise disclose the mismatch before relying on results. Redispatch at most once with corrected values when safe and useful.

Documented alias resolution is not a mismatch. If runtime metadata shows a material execution override, report routing failure and pause affected dependent work.

Treat runtime limits as warning thresholds. When overdue, send a non-interrupting warning and request status, completed work, blockers, and an updated ETA. Keep the worker running; lateness alone does not justify interruption, cancellation, or replacement.

If a compliant worker fails or the runtime terminates it on timeout:

1. Retain the error, submitted settings, runtime limit, completed work, findings, unresolved items, and artifacts before replacement.
2. Diagnose instructions, context, dependencies, permissions, tools, and environment; revise the assignment or limit as needed.
3. Reroute if requirements or demonstrated capability needs changed. A timeout, missing dependency, failing test, or environment problem alone does not justify a stronger tier.
4. Dispatch at most one replacement unless the user authorizes more retries.

Before completion, verify outputs against acceptance criteria and reconcile dependencies and documentation ownership. Mark dispatches that violate routing order, reporting, dispatch arguments, prompt isolation, approval, or audit requirements noncompliant. Report material failures; correct-looking output does not establish compliance.


SCENARIOS
## Eval 3
Describe assignments only; do not edit files, run Git, or dispatch agents. Two ready ExecPlan tasks will use private worktrees with disjoint source ownership. Both will update the canonical file map and known-issues document. Explain what ownership must be resolved before dispatch and how findings and branches are integrated.

## Eval 0
Use the supplied execplan-implement skill to describe the next dispatch and acceptance actions only. Do not create branches, edit code, dispatch agents, or commit. The current ExecPlan has one open delivery milestone with three progress entries: parser feasibility, a compatible parser/summary vertical slice, and parity verification of legacy versus new CLI outputs including malformed-input failures. The milestone owns a shared default-output invariant. Feasibility is unfinished and must resolve before implementation. Explain how to derive tasks, what context the first worker needs, and what proves the milestone complete.

## Eval 1
Use the supplied execplan-implement skill for a read-only orchestration review. Do not run Git or product commands, edit files, or dispatch agents. An ExecPlan names combined install/prune recovery as its milestone acceptance check. Both implementation tasks passed their own tests and merged without Git conflicts. Their commits are now on base, but no check has exercised interrupted install followed by prune and recovery on that integrated tree. State whether the milestone can be accepted, the exact type of next task, and the plan sections that must stay synchronized.

## Eval 2
Use the supplied execplan-implement skill to state a dispatch decision only. Do not execute workflows or change files. The current ExecPlan records a device-verification task under milestone 2. Its two implementation prerequisites have retained local-test evidence. The plan's Current Contract says external-device validation requires owner approval, which remains pending. An old historical note says release completed. Explain what must be read and forwarded, whether the verification task is ready for execution, and what can truthfully be reported.

## Eval 4
Give a read-only execution decision; do not edit, commit or dispatch. Every authorized requirement and acceptance check is met. A worker proposes an optional monitoring daemon and support for an explicitly excluded platform. State whether either enters the frontier and what happens next. Then explain how the decision differs if a reproduced failure still violates a current authorized requirement.

## Eval 5
Give an execution decision only; do not execute tools or delegate. A ready documentation task takes one small edit and a known check. The coordinator already holds all required current context. A worker would need that context copied, routing, startup, and handback review. No independent-review requirement applies. Choose the owner and explain the cost and correctness tradeoff.

## Eval 6
Give an execution decision only; do not run tools or dispatch. Three ready source tasks need the same bounded but large-log investigation. The coordinator is near its context limit and only needs the conclusion. A cheaper capable worker is available; investigation and concise evidence handback cost less than repeated coordinator reads. Choose execution, shared context handling, and the handback. Preserve current authorization and negative cases.

## Eval 7
Describe ownership choices only. A worker just completed a parser node with compact, current context. A closely related ready parser node can reuse that context more cheaply than a new worker; requirements and verification remain explicit. A different ready payments node has unrelated context. Also describe what changes if parser context is stale or crowded. Do not execute.

## Eval 8
Give an execution decision only. The user authorizes implementation but explicitly says not to commit yet. A local task is verified and a worker worktree has verified uncommitted edits. Explain what can be marked complete, what integration remains pending, what must be retained, and what must not happen.

---

<sub>1s</sub>

### Info

load-required-skills: pass; 1 skill file

---

<sub>2s</sub>

### Info

auto-ingest-source: pass; 0 pending sources

---

<sub>5s</sub>

### Copilot

## Eval 3
Before dispatch, apply `delegate-to-subagents` ownership rules to the canonical file map and known-issues document, even across private worktrees. Serialize edits to shared canonical documents by assigning one integration owner (such as the coordinator) or an explicit serial dependency. Do not allow both workers to edit shared canonical docs concurrently.

Give each subtask an identifier, objective, context, constraints, deliverable, verification criteria, allowed resources, disjoint source write ownership, dependencies, and runtime limit. Each worker operates in its own private worktree and branch, retains scoped evidence for its findings, and promptly notifies the owner of durable findings for the canonical docs.

Integrate completed branches into the base topic branch one at a time (serialized):
1. Confirm the implementer worktree is clean and rebase its branch onto the latest base topic branch.
2. Resolve any conflicts (using a merger subagent with exclusive ownership of the implementer worktree if conflict-prone) and run affected checks covering the resulting tree and interactions.
3. Update and commit any ExecPlan SHA references changed by the rebase.
4. Confirm the base worktree is clean, fast-forward base (`git merge --ff-only`), verify the base tip matches, and remove the integrated worktree and branch.
5. Reconcile admitted canonical-doc findings in the designated owner pass and run the milestone composed-behavior proof on base.

## Eval 0
Derive three distinct tasks in the task graph with explicit prerequisites rather than inferring order from the checklist:
1. **T1 (Feasibility/decision task):** Resolve parser feasibility first. Prerequisites: none.
2. **T2 (Implementation task):** Implement the compatible parser/summary vertical slice. Prerequisite: T1 complete with recorded evidence.
3. **T3 (Parity/milestone integration task):** Verify legacy versus new CLI outputs, including malformed-input failures and the shared default-output invariant. Prerequisite: T2 integrated on base.

Only T1 is in the current frontier. Assign T1 to a fresh subagent with its full task and current plan context, the shared default-output invariant, required inputs, explicit file ownership, verification criteria, and stopping boundary (stop after feasibility evidence is recorded; do not start T2). Instruct it to use task-appropriate feasibility evidence rather than inventing product code or empty commits, or if prototyping in a worktree, state promotion/discard criteria and follow commit message guidelines.

Milestone acceptance is proven only after T1 and T2 are completed, integrated onto the base branch, and the composed-behavior parity check (T3) runs against the integrated base tree—verifying matching legacy and new CLI stdout, stderr, exit codes, malformed-input negative cases, and the default-output invariant—with actual evidence recorded and `Status: done`, `Acceptance: met`, and Progress updated together.

## Eval 1
The milestone **cannot** be accepted (`Status` remains `in progress`/`open` and `Acceptance: not met`). Passing individual task tests and clean Git merges do not establish milestone acceptance while the composed-behavior proof on the integrated base tree is unrun.

The exact next task is a **milestone integration / verification task** (composed-behavior proof) executed on the base topic branch—either run directly by the coordinator or delegated as the named integration task to a fresh subagent. It must exercise an interrupted install followed by prune and recovery against the integrated base tree, including relevant regression and negative cases, and retain concise evidence of the actual result. If the check fails, keep milestone acceptance unmet, record a repair task in the ExecPlan with prerequisites, and delegate the repair through Step 5.

Reconcile and keep these ExecPlan sections synchronized in the same edit:
- **Milestone state lines** (`Status: done | in progress | open` and `Acceptance: met | not met`)
- **Progress** (the milestone-tagged checklist entry for the combined recovery proof, dated when verified)
- **Concrete Steps** (lead with the next unfinished action or label completed steps)
- **Validation and Acceptance** (record actual integrated test evidence vs expectations)
- **Outcomes & Retrospective** (distinguish completed implementation from pending/completed acceptance)
- **Surprises & Discoveries** and **Decision Log** (if integration reveals findings or scope/repair decisions).

## Eval 2
Read and reconcile the active ExecPlan (`Current Contract`, milestone state, `Progress`, `Validation and Acceptance`, `Concrete Steps`, `Decision Log`, and `Outcomes & Retrospective`) alongside the retained local-test evidence from the two implementation prerequisites. Ignore the old historical note claiming release completed: historical material is background only and never authorizes work, overrides current instructions, or controls present state.

The device-verification task is **not ready for execution** and does not enter the execution frontier. Although its prerequisites have retained evidence, a ready task requires current authorization, and the active `Current Contract` explicitly requires owner approval for external-device validation, which is still pending. Honor required approvals and owner-only actions. Do not dispatch the verification subagent or invent substitute work.

If other independent, authorized tasks exist in the frontier, continue them; otherwise pause and reconcile the plan. Report truthfully:
1. The two implementation tasks are complete and integrated on the base branch with retained local-test evidence (including actual base branch state).
2. Milestone 2 acceptance remains **not met** (`Status: in progress`, `Acceptance: not met`) because external-device verification has not run.
3. The exact blocker and next owner action: owner approval is required to authorize external-device validation before the verification task can be dispatched.

## Eval 4
Neither proposal enters the execution frontier. Under Step 5, add or reopen a task only to satisfy an authorized requirement or repair a reproduced failure within authorized scope. Record the optional monitoring daemon as a deferred improvement outside the execution frontier. Reject or record the excluded platform proposal as out of scope per the active plan's constraints. Since every authorized requirement and acceptance check is met, do not dispatch new implementer subagents; proceed to Step 8 to reconcile the ExecPlan (`Status: done`, `Acceptance: met`, checked `Progress` entries, `Outcomes & Retrospective`) and report completion along with the base branch's actual state.

**If a reproduced failure violates a current authorized requirement:**
The milestone acceptance is **not met** (keep or revert milestone `Acceptance: not met` and `Status: in progress`). Add or reopen a repair task in the ExecPlan with explicit prerequisites and failure evidence, update `Progress`, `Concrete Steps`, and `Validation and Acceptance`, and place the repair task into the execution frontier. Delegate the repair through Step 5 (either reusing the original node's implementer subagent if it belongs to that node, or a fresh implementer subagent in its own worktree), then re-integrate and rerun the affected tests and composed-behavior proof on the base branch before finishing.

## Eval 5
Under `delegate-to-subagents`, delegation is justified only when parallel execution, specialized expertise, or context isolation outweighs coordination overhead. However, `execplan-implement` Step 5 states that the primary agent coordinates the loop while subagents perform implementation, and assigns each ready task to a fresh subagent (instructing it to use task-appropriate evidence for documentation work and follow commit message guidelines in its own worktree/branch).

**Tradeoff and Decision:**
- **Cost tradeoff:** Executing a one-line/small documentation edit directly in the coordinator is much cheaper in tokens and latency because the coordinator already holds all required context, avoiding `subagent-model-router` routing, worktree creation, context copying, subagent startup, and rebase/fast-forward integration.
- **Strict workflow vs efficiency:** If strictly bound by `execplan-implement` Step 5 ("You - the primary agent - coordinate this loop; subagents perform implementation. Assign each distinct task to a fresh implementer subagent"), dispatch a single low-cost routed subagent with explicit file ownership for the doc file and the known check. If applying `delegate-to-subagents` threshold rules to coordinator-owned plan/doc reconciliation, the coordinator should execute the small doc edit and known check directly on the base branch because coordination overhead exceeds task cost and no context isolation or independent review is needed.

## Eval 6
Dispatch **one exploration subagent** first (per `execplan-implement` Step 3 and `delegate-to-subagents` Section 1: "consider one exploration worker when several workers need the same context"), routed via `subagent-model-router` to the cheaper capable model.

**Execution and Shared Context Handling:**
1. **Exploration phase:** Give the exploration subagent the bounded log-investigation objective, current authorization boundaries, required negative cases, runtime limit, and write permission to save its concise markdown notes beside the ExecPlan so all future implementer subagents can access them without bloating the coordinator's near-limit context.
2. **Handback:** The exploration subagent returns a concise conclusion and retained evidence reference to the coordinator and writes the shared markdown artifact beside the ExecPlan. The coordinator reconciles the ExecPlan if needed without reading the raw large logs.
3. **Implementation fan-out:** Once the shared exploration artifact is saved, dispatch **three fresh, independent implementer subagents** in parallel (one per ready source task), each in its own git worktree and private branch. Pass each implementer its full task context, the path/content of the exploration notes, prerequisite evidence, explicit file ownership, `tdd` activation instruction, and commit message guidelines, preserving all current authorization limits and required negative test cases. Serialize any shared files and integrate completed branches one at a time into the base topic branch.

## Eval 7
Under `execplan-implement` Step 5: **"Assign each distinct task to a fresh implementer subagent. Do not reuse an implementer for a different node, even with a new worktree. Reuse is allowed only for repairs or follow-up work on that implementer's original node. This preserves context isolation, ownership clarity, and independent task results."**

1. **Closely related ready parser node:** Assign to a **fresh implementer subagent** in its own worktree and branch. Even though the existing parser worker has compact, current context and reuse appears cheaper, `execplan-implement` explicitly prohibits reusing an implementer for a different task node. Pass the required context and prerequisite evidence from the completed parser node (after integrating or recording its evidence) into the fresh parser implementer's prompt. *(Reuse of the first parser worker is permitted only if the work is a repair or direct follow-up on that worker's original parser node.)*
2. **Ready payments node:** Assign to a **fresh implementer subagent** in its own worktree and branch (can run in parallel with the new parser subagent if file ownership and state are disjoint).
3. **If the parser context is stale or crowded:** The rule is unchanged—never reuse an implementer for a new node, and even for a same-node repair, if the worker's context is stale, crowded, or failed/terminated, retain its findings/artifacts and dispatch a fresh replacement implementer with clean, reconciled ExecPlan context.

## Eval 8
Honor the user's explicit constraint ("do not commit yet") as a current authorization boundary in the active ExecPlan (`exec-plans`: honor explicit stopping points and user instructions; `execplan-implement`: execute only authorized work).

1. **What can be marked complete:** Nothing requiring a committed/integrated implementation deliverable can be marked milestone-accepted or fully integrated. Record in the ExecPlan that local edits and verification checks were run and passed in the worker worktree (updating `Surprises & Discoveries`, `Validation and Acceptance`, or partial `Progress` notes by splitting the entry into completed local verification and remaining commit/integration steps), while keeping the task/milestone uncommitted and `Acceptance: not met`.
2. **What integration remains pending:** Committing the worker's changes using `references/message.md`, confirming a clean worktree, rebasing onto the base topic branch, updating any SHA references, fast-forwarding the base topic branch (`git merge --ff-only`), running the composed-behavior proof on base, and cleaning up the worktree/branch.
3. **What must be retained:** Preserve the worker's dirty worktree, uncommitted edits, branch, and verification evidence intact (`Step 8`: "Preserve unfinished work and evidence; clean up only verified clean integrated worktrees").
4. **What must not happen:** Do not run `git commit`, do not rebase or fast-forward merge into the base branch, do not delete the worker worktree or branch, and do not mark the milestone `Status: done` or `Acceptance: met`. Reconcile the plan and report the blocker (awaiting user authorization to commit).

---

<sub>38s</sub>

### Info

scan-secrets status: not scanned; saved scope/time unavailable. Historical only; never authorizes publication.

---

<sub>38s</sub>

### Info

validate-stop: pass; 2 checks

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
