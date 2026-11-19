# Qualitative ExecPlan authoring evaluation

These cases supplement the three deterministic scenarios in `evals.json`. Use evidence review for these assertions; `grade_benchmark.py` intentionally supports only the named deterministic scenarios. Do not pass these cases to that CLI or infer these assertions from keyword matches.

## Before the first draft

Give a fresh plan author the skill snapshot under evaluation and this checkpoint. Keep its response so the named reader, missing files and order of actions can be checked.

    The user approved the architecture and asked you to create the ExecPlan.
    You have read the ExecPlan skill, project planning instructions, outline
    and principle index in full. A batched read of the linked principle files
    exited successfully, but the middle of one file was clipped. A reviewer
    read codebase-design and sent you a summary. No plan has been drafted.
    What do you do next, and when can you write the first paragraph?

Pass when the author personally reads the full `codebase-design` skill and retrieves the missing principle text before drafting. The author can reuse the complete reads from this pass. Fail if it starts a draft, accepts the reviewer's summary as its own read, or postpones either read until review or implementation.

## Prototype and migration planning

Copy `files/create-plan/project/` into a disposable run directory and supply `files/prototype-migration/brief.md`. Use the same input tree and prompt for both skill snapshots. Keep each run isolated and retain the resulting `ExecPlan.md` and transcript.

Prompt:

    Use the supplied exec-plans skill to create an implementation-ready ExecPlan for brief.md and the supplied project. Save outputs/ExecPlan.md. Do not edit project code.

Review the plan against these assertions using file and section evidence:

1. It names precise existing and proposed files, edit locations, and required function signatures or interface contracts. A novice can identify how the parser, CLI, and summary implementation connect.
2. It specifies independently runnable feasibility experiments for line parsing and streaming aggregation before integrating them. Each experiment has observable success and failure criteria.
3. It identifies what would promote each prototype into the implementation and what would cause it to be discarded or reworked. Planned results are clearly distinguished from measurements already obtained.
4. It validates the list and stream paths against the same valid, empty, and malformed input, then gates the default switch and legacy-path retirement on evidence. It includes a safe retry or rollback path.
5. It gives exact commands, working directories, expected successful output, invalid-input diagnostics and exit behavior, and how to interpret test failures. At least one demonstration exercises the CLI beyond compilation.
6. It leaves implementation and acceptance open, preserves the default output contract, and makes ordinary planning decisions without asking for routine next steps.

Record each pass/fail with quoted or paraphrased evidence from the produced plan. A passing authored plan is not evidence that the proposed parser, migration, or memory bound works. Single paired runs do not establish general agent-performance differences.

## Tasks and integrated acceptance

Use the same create-plan project and prototype/migration brief. Add this instruction to the authoring prompt for both baseline and revised runs:

    A later coordinator will distribute this work among workers. Keep the final
    delivery milestone meaningful while identifying useful task boundaries.
    The parser and aggregator have a shared invariant: list and stream modes must
    produce the same summaries and invalid-input outcomes. Required memory-bound
    measurements are unavailable until an owner supplies the target host.
    Save only outputs/ExecPlan.md. Do not implement or simulate measured results.

Review the generated plan against these additional assertions:

1. It distinguishes milestone acceptance from worker tasks and records actual prerequisites rather than inferring them from checklist order.
2. Each task supplies inputs, current design context, an outcome, checks, and a stopping boundary. Independent feasibility questions are bounded before dependent implementation.
3. Stable current headings or identifiers let workers find the active design without relying on historical decisions or unlisted documents.
4. It names the shared invariant, combined list/stream proof, and responsible integration task or milestone check. Passing individual worker tests or a clean merge cannot close acceptance.
5. It keeps the owner-host measurement pending with an owner and next action. It does not invent an approval, result, or runtime.
6. It preserves malformed-input and regression requirements rather than shrinking acceptance to create more tasks.

Run a separate fresh-worker reading with only the generated plan and selected task. Request its first authorized action, prerequisites, exact first check, completion condition, and stopping boundary without product edits. Record every additional document it needs. Missing critical context fails this review even if every required heading is present.

## From plan to first dispatch

Replay the following checkpoints independently with the original and revised skill in fresh contexts. Give both readers the same prompt. Grade their decisions against the evidence below. This exercise tests the instructions a coordinator takes from the skill.

    The user approved the outcomes and said "Create the plan, then implement it."
    A saved 8 KiB plan covers two worker runtimes. In each independent checkpoint,
    give the next concrete action and say when the first live-trial worker may start.
    Evaluate the scenarios on paper. Do not launch workers or edit a project.

    A. A batched read of the skill, outline and linked principles returned exit 0.
       The output shows the beginning and end with the middle truncated.
    B. All inputs are read. The plan leaves deadline ownership open between a
       host timer and a shared helper. The user has approved the timeout behavior.
       A trial operator is available.
    C. The architectural decision and independent review are recorded. Progress
       lists four milestones. Only the proposed worker message specifies that
       its first assignment ends after baseline capture. Later trials depend on
       a candidate that has not yet been selected.
    D. All required reads and the design review are complete. The plan names
       the baseline owner, inputs, evidence for prerequisites, first check, result
       and stopping point. Candidate selection is a separate downstream task.

Pass A when the coordinator recovers the missing text before relying on it. Pass B when it develops concrete alternatives, obtains a fresh `codebase-design` critique and ranking, and records its choice and rationale before the live trial. Pass C when it puts the bounded baseline and its dependencies and checks into the plan before dispatch and leaves candidate trials pending. Pass D when it starts only the baseline under the existing authorization. Repeating a completed review or requesting routine approval fails D.

## Size boundary and resumed conversion

Use disposable copies of a plan with two milestones, a completed prerequisite decision and an open task that links to the decision's heading. Pad with historical observations to reach the specified byte size. Review each case independently.

1. At creation, measure a 12,288-byte plan. It stays at its original path as one file.
2. At creation, finalize a 12,289-byte plan with work remaining. Repeat independently at the first resumed checkpoint. In both runs, verify that the original path is the entry, milestone detail moved into linked files, and each routine file is at most 12,288 bytes. Read the entry alone for the next action and owner. Follow the assignment and its cited prerequisite to recover the decision, steps and acceptance criteria.
3. Move the prerequisite heading during conversion. After removing the old heading, resolve the task's link to the decision at its new location. Check all final file and fragment targets, retained evidence and open work. Repeat the checkpoint and check for duplicate records and broken links.
4. Use a plan whose open-task index alone exceeds 12,288 bytes. Verify the entry still gives the next action and owner, every task and dependency remains reachable, and every routine index page fits the budget.
5. Resume an oversized plan whose only remaining action is recording completion. Verify that it can be closed in place. A dormant plan elsewhere in the project should remain untouched.

## Deterministic suite maintenance

Run from the repository root after grader changes:

    rtk proxy env PYTHONPYCACHEPREFIX=/private/tmp/execplan-grader-pycache python3 -m unittest discover -s skills/default/exec-plans/evals -p test_grade_benchmark.py

The three deterministic scenarios cover novice creation, two resumed code checkpoints, and completed code with pending owner approval and recovery. Keep their own fixtures, assertions, grader and public CLI tests independently usable. Use canonical iteration directories with one eval metadata file beside configuration runs. Exit 0 means grades were written, including failed assertions; inspect `expectations` and `summary.failed`. Invalid invocation or input errors exit nonzero.

Retain valid wording and line ranges alongside stale actions, missing archive evidence, history-only recovery, unauthorized agent actions and contradictory proof. Review conditional, comma-separated, coordinated and contrasting claims for independent factual assertions; wording checks remain scenario heuristics. Review the qualitative cases above manually for feasibility, both-path validation, prerequisites, shared invariants, integrated proof, owner boundaries and exact commands. Keep instruction coverage separate from sampled agent-performance claims.
