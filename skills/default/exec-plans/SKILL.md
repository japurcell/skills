---
name: exec-plans
description: Mandatory when creating or modifying any 'exec-plan', 'ExecPlan', 'execution plan', '*ExecPlan*.md', or '*exec-plan*.md' file. Use for new features, multi-file refactors, or architectural changes - not small fixes. Load before inspecting or editing ExecPlan files.
---

# Execution Plans (ExecPlans)

An ExecPlan is the working contract for a feature or other multi-step change. Write it for a novice who has the current working tree and this plan, but no memory of earlier conversations or plans. The plan must explain what to do, how to verify it, and what remains current at every checkpoint.

## Invocation and pre-code gate

Load this skill before inspecting or editing an existing ExecPlan. Reuse its instructions within the same agent context; reload only when they change or are no longer available in context. If work [needs a plan](#triage-complexity), create the file at the requested location before the first code edit. When no location is specified, use the project's established plan location; if none exists, create `brain/<feature-slug>/ExecPlan.md`. Verify that the file exists before changing implementation code. Saying that you will write a plan later does not satisfy this gate.

When drafting or restructuring a plan, read the [annotated outline](references/outline.md) and adapt it using the relevant source and supplied requirements. Resolve ordinary ambiguities from the available evidence or by [gathering context with subagents](#gather-context-with-subagents); then record the choice and rationale in the plan. If ambiguities remain, ask the user for clarification to close every gap. When asking the user questions, use the host's structured input tool with concrete options when available, or concise direct questions otherwise. Provide your recommendation for each question. Close gaps in behavior, scope boundaries, edge cases, data shapes, error handling, non-goals, and acceptance bar. Batch related questions (no more than four at a time). Stop only when the remaining decisions are resolved or the user explicitly delegates them to your discretion. Do not leave key implementation decisions for a novice reader to guess.

When executing, proceed to the next planned milestone without asking the user for routine next steps. Resolve ordinary implementation ambiguities autonomously within the agreed scope. Honor explicit stopping points, required approvals, and owner-only actions; when one blocks progress, record the missing decision or permission and continue independent authorized work. Follow the project's commit workflow.

## Triage Complexity

Before starting any planning work, assess whether this task actually needs a plan:

**Trivially small (1-2 files, obvious approach):**

Tell the user this task doesn't need a plan and suggest implementing directly without the plan skill. **Stop here — do not implement.**

**Needs planning (proceed to [Load Principles](#load-principles)):**

- The change spans 3+ files or introduces new architecture
- There are multiple valid approaches and the user should weigh in
- The task has unclear scope or cross-cutting concerns
- The user explicitly asks for a plan

## Load Principles

Read `brain/principles.md`. Follow every link and read each linked principle file. These principles govern all plan decisions - cite them by name in the plan overview.

**Do NOT skip this. Do NOT use memorized principle content — always read fresh.**

## Gather Context with Subagents

Finding _facts_ is your job, never the user's. When a question needs a fact from the environment (filesystem, tools, etc.) or external sources, activate the `delegate-to-subagents` skill and dispatch a subagent to find it; don't ask the user for anything you could look up yourself. Don't block on it: a running exploration is an unsettled prerequisite, so only the questions downstream of it wait for the subagent to report.

Dispatch exploration subagents to:

- Read existing code in affected areas
- Identify patterns, conventions, and dependencies
- Map architecture relevant to the change
- Find tests, types, and related infrastructure

Dispatch research subagents to gather facts from external sources. Resolved by a subagent that activates the `research` skill. Use when knowledge outside the current working directory is required.

Run multiple background subagents in parallel when investigating independent areas.

## Size and reading scope

Start with one Markdown file. At creation and each implementation checkpoint, measure the entry and any new or changed files on routine reading paths (for example, `wc -c < "$plan_file"`). Split files exceeding **12 KiB (12,288 bytes)**. Apply this rule to an oversized existing plan at its first resumed checkpoint. Skip conversion if only recording completion remains.

Keep the original entry path. For a split plan, create a sibling directory named after the file stem, for example `ExportPlan.md` and `ExportPlan/milestone-1.md`. Treat the entry and its linked milestone and task files as one self-contained ExecPlan.

- **Entry file.** State the objective, governing constraints, next authorized action, owner and direct assignment link. If blocked, identify the blocker and who can clear it. Summarize milestone status, acceptance and dependencies. Keep the full open-task index here while it fits. When it grows too large, place task IDs, states, prerequisite edges and links in their owning milestones. Group larger indexes behind bounded, linked pages as needed. Keep the next action and decisions that govern it visible in the entry, with direct links to supporting detail.
- **Milestone files.** Give each milestone one file for its contract, implementation steps, granular Progress and integration proof. Before dispatch, give independently assigned tasks their own linked files. Other tasks can stay under milestone headings until the milestone exceeds the budget.
- **Task files.** Keep the assignment, instructions, acceptance criteria and current result together. Link directly to any prerequisite result or shared decision the worker needs, using a heading anchor where appropriate. Workers read the entry, their assignment and its explicit prerequisites. They update only their assigned plan file. The parent updates shared status, dependencies and the next action at checkpoints.

Extract tasks from an oversized milestone. Move accumulated evidence or history out of an oversized task, retaining its current instructions, acceptance criteria and concise proof. If active instructions alone exceed the budget, split independently verifiable steps or link the specific contract sections they require. Archive completed summaries under the evidence preservation rules below. After restructuring, measure the resulting files and repeat until each routine file fits.

Before removing original detail, verify that each open task, decision, acceptance criterion and unique piece of evidence has a retained home. After the moves and removals, resolve plan links from their referring files and check fragments against the final headings. Update references to moved targets. Verify that a fresh parent can identify the next action and owner from the entry alone and that a worker can execute and validate it using only the entry, assignment and cited prerequisites.

## Write a self-contained plan

Start with the user benefit and the behavior a person can observe when the work succeeds. Explain the relevant project structure, assumptions, unfamiliar terms, exact files and interfaces, commands, expected results, and safe recovery steps. Include the facts a novice needs directly in the plan. External references may supplement the instructions, but the plan must not depend on them for its current contract or next action.

Use milestones when work has distinct checkpoints. Each milestone must describe the work, how to verify it, and what observable result marks it complete. Add these state lines at the start of every milestone:

    Status: done | in progress | open
    Acceptance: met | not met

Keep the narrative precise and testable. Name the working directory for commands, show expected output where it helps, and describe behavior a person can verify rather than only internal code changes. Include idempotence, rollback, dependencies, interfaces, and evidence when they affect successful or safe execution. Define specialized terms in plain language.

A milestone is a delivery and acceptance outcome, not automatically one task. A **task** is an independently assignable unit of work with explicit prerequisites, required inputs and current design context, an outcome, verification, and a stopping boundary. Before dispatch, assess its behavioral scope, unresolved decisions, coupled state, and verification burden. Keep each task bounded by splitting independently deliverable behaviors into separate tasks. Preserve necessary negative cases and indivisible correctness rules. A difficult but inseparable task needs clear reasoning risks and entry points, not reduced acceptance. Resolve a design uncertainty through a bounded decision or feasibility task before dependent implementation.

Name files with full repository-relative paths, identify the exact functions or modules to edit, and say where new files belong. Explain how affected areas fit together. State environment assumptions and provide reasonable alternatives when commands or results vary by environment. Carry task-specific facts and decisions from references or prior plans into the active plan so the reader can execute its contract. Link reusable guidance at its canonical location in the repository's durable documentation instead of copying it into the plan.

Design steps to be repeatable. Explain how to detect and recover from a partial failure, including safe retries and backups or fallbacks for destructive work. Prefer additive, testable changes that can be validated before replacing existing behavior.

### Collaborate on the architecture

For architectural decisions, trace every system the change touches, then sketch 2-3 different shapes for it (types, signatures, module boundaries). Before you pick one, dispatch a fresh subagent and instruct it to: activate the `codebase-design` skill and critique, grade, and rank your designs. Use that feedback to pick the one where each piece of state has one owner, each task has one way to do it, and callers need to know least. If the best design isn't obvious, ask the user to pick.

Record each design considered in the plan's `Decision Log`. State which was chosen and why. This prevents premature commitment and documents the design space explored by applying exhaust-the-design-space.md.

### Redesign check

For changes touching existing code, apply redesign-from-first-principles:

> "If we were building this from scratch with this requirement, what would we build?"

Don't bolt changes onto existing designs - redesign holistically.

## Validation and observable acceptance

Validation is required. State the exact test commands for the project's toolchain, their working directories, expected results, and how to interpret failures. Cover new behavior, relevant error cases, and existing behavior that must remain intact. Include expected output and diagnostic messages so a novice can distinguish success, a product defect, and a missing environment prerequisite. Mark proposed results as expectations until they have actually been observed.

Explain how to start or exercise the system when applicable. Demonstrate useful behavior beyond compilation through a small end-to-end scenario, direct CLI invocation, or request/response example with specific inputs and outputs. For an internal change, identify a test or observable scenario that exposes its effect; for a bug fix, record how the reproducer fails before the change and passes after it. Successful compilation alone does not establish acceptance.

Run the relevant checks at each milestone and retain concise evidence of the actual result. If a check cannot run, state why and what remains unverified rather than treating planned verification as proof. Use small transcripts, file-scoped diffs, or focused excerpts that show what establishes success; keep full run logs behind evidence references.

When several tasks contribute to a milestone, name their shared invariants and the integration task or milestone check that proves their combined behavior. Run that proof against the integrated result, including relevant regression and negative cases. Passing individual tasks, clean Git merges, or checked progress entries do not establish milestone acceptance while that proof remains missing.

## Required living sections

Every ExecPlan keeps these sections current. In a split plan, keep shared state in the entry and local detail in its owning milestone or task file. Apply the outline across those files.

- `Purpose / Big Picture` explains the user outcome and how to observe it.
- `Progress` records completed work, current work, and the next action in a milestone-tagged checklist.
- `Surprises & Discoveries` records relevant findings with concise evidence.
- `Decision Log` records current decisions and why they were made.
- `Outcomes & Retrospective` states what is complete, what remains, and the task's outcomes and evidence, with links to separately persisted durable lessons.

Also include the project context, plan of work, concrete steps, validation and acceptance, and recovery guidance needed to carry out the task without prior context. Add interface, dependency, or artifact details when they materially help a novice proceed.

Plans are temporary and may be deleted. Persist reusable lessons and rules when identified, using the repository's existing knowledge base or documentation conventions. If no suitable destination exists, create a focused guidance document outside temporary plan directories and link it from the repository's documentation navigation. Keep only a link in the plan. Before archiving or deleting a plan, extract any durable guidance still stored only there and verify the saved document and its navigation links. Keep the plan's task-specific contract, decisions, and evidence intact.

Each milestone has matching Progress entries tagged `[milestone-X]`; split partially completed work into completed and remaining steps. A completed milestone uses `Status: done`, `Acceptance: met`, and checked entries such as `- [x] (YYYY-MM-DD) [milestone-X] ...`. Open or in-progress work keeps its remaining entries unchecked. Update the milestone's status, acceptance, and every affected Progress entry in the same edit. Do not mark work done without evidence that its acceptance is met.

Batch routine progress bookkeeping at meaningful checkpoints, preserving required checks and synchronized milestone state. Record material changes and blockers promptly, and honor host-required user-facing progress updates independently of plan edits.

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

Preserve useful task-specific decisions and unique evidence before moving material out of the active plan. Keep evidence needed for current status or acceptance inline. For historical material that can leave the active plan, first reuse an existing retained artifact or create a clearly labeled sibling snapshot. Add a link to it under a clearly titled historical section, verify that the target exists and still contains the unique dates, commands, results, or decisions being moved, and only then replace the inline material. A link to the active plan itself is not an archive. If the archive cannot be verified, keep the evidence inline and report the limitation.

Keep the current rationale concise in `Decision Log` and useful findings in `Surprises & Discoveries` or `Validation and Acceptance`. Move superseded run transcripts, outdated status statements, and revision narratives behind the verified historical reference when their provenance matters. Historical material is background only: it never authorizes work, overrides user instructions, or controls present state. Do not append a full revision narrative after every update, and do not make a reader search history to continue.

For substantive changes in scope or approach, record what changed and why in the relevant living sections, including a dated decision when needed. Routine progress or editorial corrections need only update the affected current sections; they do not require a separate revision footer.

## Formatting and evidence

Write a saved ExecPlan as plain Markdown. If delivering the plan in a response, use one fenced `md` block and indent any nested examples rather than adding inner fences. Use headings and readable prose; reserve checkboxes for `Progress`. Prefer prose to tables or long lists in narrative sections. Keep examples and captured output short and focused on proof.
