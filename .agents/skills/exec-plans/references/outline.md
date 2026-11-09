# Annotated ExecPlan outline

## Contents

- [Purpose, progress, and decisions](#purpose-progress-and-decisions)
- [Milestones, tasks, and integration](#milestones-tasks-and-integration)
- [Verification, recovery, and interfaces](#verification-recovery-and-interfaces)

Use this annotated outline and adapt detail to the work. The file-reporting example shows how a milestone, tasks, and Progress entries relate. Its paths and commands describe a hypothetical Python CLI; replace them and the instructional placeholders with verified project facts.

## Purpose, progress, and decisions

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

## Milestones, tasks, and integration

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

## Verification, recovery, and interfaces

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
