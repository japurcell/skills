# Skill workflow improvements handoff

## Goal and status

Completed the authorized revisions to [the plan](exec-plan-tasks-improvements.md), `.agents/skills/exec-plans/`, `skills/execplan-implement/`, `skills/spec-to-tasks/`, `skills/prd-ralph/`, and `skills/prd-ralph-loop/`. Final source review, paired comparisons, fresh-reader exercises and documentation pass finished on 2026-10-07. All changes remain uncommitted.

This is a feature-scoped handoff retained beside the plan at the user's explicit request. No implementation step remains. Next review action: inspect [the existing review viewer](/private/tmp/exec-plan-tasks-improvements/comparison/review.html) and the uncommitted diff from `/Users/adam/.codex/worktrees/3e77/skills`. Do not repeat completed revisions, reset the working tree, or install personal copies to resume. Reopen only acceptance affected by a later requirement or edit.

## Contracts to preserve

- User boundary: `exec-plans` must not reference `execplan-implement`; neither ExecPlan skill may reference `spec-to-tasks` or know its schema. Tasks, prerequisites and integrated acceptance live in the plan. The optional manifest bridge was removed.
- The producer owns the complete task schema, and Ralph validates every task against it before selection or completion detection. Require all schema fields, including `dependsOn`; preserve recorded IDs, pass flags, notes and evidence when reporting invalid input.
- Every dependency needs a consumed outcome/artifact or mandatory source order. Complete available authoring coverage reviews immediately; do not defer them behind implementation.
- Ralph validates intake before all-true completion, consumes explicit context/checks and prerequisite evidence, and leaves unresolved work unfinished. `commit:false` permits a read-only deliverable only with actual evidence and zero session commits; default `commit:true` still needs a real committable deliverable.
- `COMPLETE` means all validated tasks pass. `TASK_COMPLETE` means the selected task succeeded with work remaining. `BLOCKED` stops the blind loop; unchanged owner prerequisites are not retried.
- Preserve `disable-model-invocation: true` in both protected consumers and the existing `execplan-implement/agents/openai.yaml`.
- The historical installer example under `docs/agent-asset-installer/` is absent. The lifecycle fixture is self-contained; no installer content or product execution should be invented.

## Evidence and limits

Final commands run from the repository root:

- `rtk proxy python3 skills/spec-to-tasks/evals/test_grade_benchmark.py`: 34 tests pass.
- `rtk proxy python3 skills/prd-ralph-loop/evals/test_grade_benchmark.py`: 10 tests pass.
- All 16 scenario/fixture JSON files parse; temporary-cache Python compilation and whitespace checks pass.
- Skill validators pass for exec-plans, spec-to-tasks and prd-ralph. The other two still report `Unexpected key(s) in SKILL.md frontmatter: disable-model-invocation`. Preserve the required key; this is not a passing result.
- Earlier 35 ExecPlan grader and 14 runner tests apply to unchanged source.
- `rtk proxy python3 scripts/lint-okf.py`: exit 0 after the final canonical pass.

The new complete documentation manifest passes 10/10 producer CLI assertions. Lifecycle passes nine and correctly fails only readiness because runtime/commands are unresolved. Grades are retained under `/private/tmp/exec-plan-tasks-improvements/producer-validation/iteration-1/`; grader exit zero alone is not acceptance.

Six selected paired outputs pass 18/18 revised versus 17/18 baseline shared assertions. Five cases tie; the distinguishing assertion is Ralph's nonfinal completion protocol. Three fresh readers correctly identify plan/task boundaries and the intended stop on missing prerequisite decision evidence. [Provenance](/private/tmp/exec-plan-tasks-improvements/comparison/selected/iteration-1/selection-provenance.json) lists immutable source hashes and viewer-only adaptations. [Review notes](/private/tmp/exec-plan-tasks-improvements/comparison/review-notes.md) explain selection and rubric limits. There is one selected sample per case/configuration, no confirmed executed model/effort, and no time/token or efficiency claim.

The outline shows two tasks under one milestone, multiple Progress entries for T1, and a separate integration check. Both ExecPlan skills use task terminology. The planning skill owns shared task, dependency, reconciliation, and acceptance rules; the consumer references them while retaining dispatch and Git integration procedures. The earlier full-workflow comparisons predate these clarifications. A subsequent consumer-only comparison passed 9/9 existing assertions for both the pre-deduplication and revised versions. Its [review notes](/private/tmp/execplan-implement-dedupe.k2Z4FY/review-notes.md) retain the coverage map, sampling limits, and validator limitation; its [review viewer](/private/tmp/execplan-implement-dedupe.k2Z4FY/review.html) contains the three paired answers. This does not establish live orchestration behavior or a performance improvement.

The producer and Ralph now use one complete task contract. The obsolete compatibility scenario and fixture were removed, and loop completion wording no longer distinguishes input versions. Source review, both skill validators, all 44 existing grader tests, and 16 JSON parses passed after this cleanup. Earlier paired comparisons predate this change; no new regression tests were added for the deletion.

Read-only interpretations do not establish execution of the disposable Ralph sandbox scenarios, actual product behavior or owner-host acceptance. No product commands, personal installation, Git commit or push occurred.

## Review lessons and recovery

The first revised lifecycle output delayed a coverage audit behind implementation; semantic review rejected it and the affected rerun passed after a focused producer clarification. The first revised loop output read the worker skill; both loop versions were rerun with only their own skill. Earlier outputs remain unchanged. JSON shape and fixture keywords never replace semantic review.

Public grader repairs cover complete original/enriched fields, invalid verification values, malformed references, actual prerequisite wording, restored domain checks, valid backend vocabulary, NUL paths, non-object timing data, and contradictory loop decision fields. Earlier synthetic artifacts missing required fields remain invalid evidence, even where their original grade said pass. [Repair history](/private/tmp/exec-plan-tasks-improvements/grader-repair-checkpoint.md), `grader-reproducer/`, `grader-final-repair/` and `loop-final-repair/` retain the diagnostics under the same temporary root.

Tool Guardian rejected shell writes over its 256-token command limit; file patches and short commands worked. RTK works, while its optional gain database reported error 14; no user configuration was changed. Account-wide installation was not needed for source-copy evaluation.

The [earlier audit](/private/tmp/exec-plan-tasks-improvements/dispatch-audit.json) and [resumed audit](/private/tmp/exec-plan-tasks-improvements/dispatch-audit-resumed.json) retain explicit routes, unconfirmed execution settings, rejected/excluded outputs, the corrected implicit dispatch and missed warning checkpoints. The final grader repair's warning compliance is recorded as unverified/noncompliant, not hidden.

The final canonical pass updated skills instructions/testing, grader API guidance and the retained-effort map; earlier repository/index/runner-test routing updates remain synchronized. OKF profile only; no canonical additions, moves, splits or remaining quality TODOs. Temporary evidence is disposable, so preserve it elsewhere if later work needs long-term artifact retention.
