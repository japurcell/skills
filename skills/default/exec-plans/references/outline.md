# Annotated ExecPlan outline

## Contents

- [Purpose, progress, and decisions](#purpose-progress-and-decisions)
- [Milestones, tasks, and integration](#milestones-tasks-and-integration)
- [Verification, recovery, and interfaces](#verification-recovery-and-interfaces)

Use this annotated outline and adapt detail to the work. The note-lookup example shows how a milestone, tasks, and Progress entries relate. Its paths and commands describe a hypothetical Python CLI; replace them and the instructional placeholders with verified project facts.

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

    - [ ] [milestone-1] T1: Build a candidate title index beside the existing lookup.
    - [ ] [milestone-1] T1: Compare both lookups on the same notes and record the results.
    - [ ] [milestone-1] T2: Connect the verified index to the notes command.
    - [ ] [milestone-1] Verify the integrated command on unique, missing, and duplicate titles.

    ## Surprises & Discoveries

    Record unexpected behavior, bugs, tradeoffs, or insights that affect
    the current approach. Include a concise evidence snippet or result.

    - Observation: <finding>
      Evidence: <actual command, output, or source location>

    ## Decision Log

    Record current decisions and the rationale needed to continue safely.
    For an architectural decision, identify the alternatives, the fresh
    reviewer's ranking, and why the selected design meets the requirements.
    Explain substantive changes in scope or approach here.

    - Decision: <choice>
      Rationale: <why it meets the requirements or resolves an ambiguity>
      Date/Author: <actual date and contributor>

    ## Outcomes & Retrospective

    Compare achieved results with the purpose at major milestones and
    completion. State remaining work and task-specific evidence. Link durable
    lessons saved in the repository's durable documentation. Distinguish
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

    ### Milestone 1: Use an index to find a note by title
    Status: open
    Acceptance: not met

    The notes command currently searches a list. Replace that search with
    a title index while preserving its behavior. A unique title prints the
    note's path and exits 0. A missing or duplicate title prints its existing
    diagnostic to stderr, leaves stdout empty, and exits 1.

    #### Task T1: Compare a candidate index with the working lookup

    Prerequisites: the project contains the current lookup and its passing
    contract tests. The index developer adds build_index and find_indexed
    in a separate src/title_index.py. Keep src/notes.py:find_title and the
    command that calls it unchanged throughout this task.

    In tests/test_title_index.py, add one comparison test each for a unique,
    missing, and duplicate title. Call find_indexed and find_title on the
    same collection in each test. From the project root, run
    `python3 -m unittest discover -v -s tests -p test_title_index.py`.
    Confirm that all three named comparisons ran and passed with identical
    results or errors. Record the comparison and stop with both functions
    available. If a case disagrees, rework the candidate and repeat T1.

    #### Task T2: Use the verified index in the command

    Prerequisites: T1's passing comparison and tested index. The CLI
    developer updates src/notes_cli.py to build the index and call
    find_indexed. Preserve the existing output and exit behavior.

    Add subprocess coverage for all three title cases in tests/test_notes_cli.py.
    From the project root, run
    `python3 -m unittest discover -v -s tests -p test_notes_cli.py`.
    Confirm that each case ran and passed. Record the result and stop after integration;
    the coordinator owns milestone acceptance. If behavior changes, restore
    the call to find_title and rerun the command tests.

    #### Milestone integration check

    After T2, the coordinator runs `python3 -m unittest discover -s tests`
    from the project root. The CLI tests exercise the actual command and
    check stdout, stderr, and exit status for all three title cases. Record
    the integrated result before checking the final Progress entry and
    setting Status: done and Acceptance: met.

    For other milestones, adapt the tasks and combined proof to their
    actual outcomes. A task may map to one or several Progress entries;
    update those entries as its work advances without changing its scope.
    For each independent feasibility question, name its candidate, comparison,
    stopping point, and the later task that can use the result. For a migration,
    explain the gate for switching or retiring a path.

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

    In src/title_index.py, define:

        def find_indexed(index: dict[str, list[str]], title: str) -> str:
            ...

    Explain the inputs, outputs, and failure behavior required by callers.

    ## Artifacts and Notes

    Include concise transcripts, diffs, or snippets that establish current
    acceptance. Link larger evidence artifacts with an explanation of what
    they prove. Put superseded material under Historical Records only after
    verifying the retained target and preserving current requirements inline.

Keep the required living sections present throughout the work. Add `Artifacts and Notes` only when transcripts, outputs, or other evidence materially help the next contributor.
