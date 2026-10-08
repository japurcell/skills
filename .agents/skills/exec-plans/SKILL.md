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
