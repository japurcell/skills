# Improve ExecPlans and task decomposition


Prepared and reconciled 2026-10-07. Status: done for the authorized skill revisions and source/read-only acceptance described below. This living ExecPlan is saved at `docs/exec-plan-tasks-improvements.md` and follows `.agents/skills/exec-plans/SKILL.md`. Changes are uncommitted. Product execution, personal installation and runtime performance are outside the observed evidence.

Keep Progress, Surprises & Discoveries, Decision Log, and Outcomes & Retrospective current. The coordinator owns contract decisions, this plan, integration, and final acceptance. Delegate independent implementation and review with explicit file ownership.

## Purpose / Big Picture


Improve two independent workflows: `exec-plans` describes design, constraints, tasks and final acceptance; `spec-to-tasks` produces structured tasks from supplied requirements. Each workflow's consumers must preserve its contract. Neither ExecPlan skill depends on the decomposition workflow.

Reduce reasoning breadth without hiding necessary technical depth. A smaller task reduces the number of unrelated facts, decisions, and failures an agent must track. It does not make a difficult recovery algorithm easy. Preserve the full correctness contract when splitting work, including negative cases and integration proof.

Success means a fresh agent can identify its prerequisites, required design context, first verification step, completion condition, and stopping boundary from a task and its explicitly required references. Judge fewer missing requirements, invented commands, unjustified completion claims, and unlisted context searches. Task count and document length are not success measures.

## Progress


- [x] (2026-10-07) [milestone-1] Reconcile this plan with the current ExecPlan skill and inspect dependent consumers; preserve baseline skill snapshots.
- [x] (2026-10-07) [milestone-1] Extend the existing ExecPlan contract and then align `execplan-implement`; remove task-schema coupling following the user's correction.
- [x] (2026-10-07) [milestone-1] Compare baseline/revised plans and integrated-acceptance responses; a fresh reader identifies A1's inputs, command and stop boundary without the owner host.
- [x] (2026-10-07) [milestone-2] Update task sizing, structured dependencies/context, task types, and applicable verification; pass source validation and complete-example JSON checks.
- [x] (2026-10-07) [milestone-2] Complete semantic review and affected reruns; clarify actual dependency inputs and perform authoring coverage review before implementation.
- [x] (2026-10-07) [milestone-3] Align both Ralph consumers with the complete task contract and retain complete-input, blocked and commit-policy scenarios.
- [x] (2026-10-07) [milestone-3] Repair graders through public-CLI reproducers. Checkpoint tests passed 29 producer/eight loop cases; final suites pass 34 producer/10 loop cases.
- [x] (2026-10-07) [milestone-3] Complete tracked/untracked grader review and README/JSON reconciliation. A new complete documentation manifest passes 10/10 CLI assertions; lifecycle correctly fails readiness only.
- [x] (2026-10-07) [milestone-4] Review six paired outputs and three fresh-reader exercises, including missing prerequisite evidence; retain earlier rejected/excluded outputs and selection provenance.
- [x] (2026-10-07) [milestone-4] Complete the checkpoint canonical documentation pass; OKF lint passed and the handoff records unfinished acceptance.
- [x] (2026-10-07) [milestone-4] Complete final source review, generate the existing review viewer, reconcile canonical docs, and pass final OKF lint.

## Context and Orientation


Run commands from this checkout's repository root, currently `/Users/adam/.codex/worktrees/3e77/skills`. Paths below are repository-relative unless stated otherwise. A skill's `SKILL.md` is its entry point; linked references hold detailed rules. A benchmark grader checks artifacts produced during a skill evaluation.

| File | Role in this change |
| --- | --- |
| [ExecPlan skill](../.agents/skills/exec-plans/SKILL.md) | Repository-local authority. Extend existing task, current-design, and integration guidance. |
| [ExecPlan consumer](../skills/execplan-implement/SKILL.md) | Apply the revised planning contract to task selection, worker context, and milestone acceptance. |
| [Task-decomposition skill](../skills/spec-to-tasks/SKILL.md) | Publishable source. Change sizing and verification requirements. |
| [Task schema](../skills/spec-to-tasks/references/task-schema.md) | Define the fields and their meanings. |
| [Task validation checklist](../skills/spec-to-tasks/references/validation.md) | Validate dependencies, coverage, context, sizing, and verification applicability. |
| [PRD handling](../skills/spec-to-tasks/references/prd-handling.md) | Preserve PRD extraction and mandatory ordering. |
| [Existing evaluations](../skills/spec-to-tasks/evals/evals.json) | Align prompts and expectations with the task contract. |
| [Existing grader](../skills/spec-to-tasks/evals/grade_benchmark.py) | Repair artifact discovery and semantic checks through public-CLI tests. |
| [Single-task consumer](../skills/prd-ralph/SKILL.md) | Consume dependencies, context, task type, and verification before changing completion state. |
| [Loop consumer](../skills/prd-ralph-loop/SKILL.md) | Forward constraints and stop on completion or actionable blockers while preserving its blind-orchestrator boundary. |
| [Skill conventions](../.agents/instructions/skills.md) and [skill testing](../.agents/instructions/testing/skills.md) | Authoring, evaluation, and validation requirements. |

Implement publishable changes in `skills/` and the explicitly authorized repository-local change in `.agents/skills/exec-plans/`. Installed copies are not the source of truth. Preserve `execplan-implement`'s `disable-model-invocation: true` and `agents/openai.yaml` policy. Its commit-message reference is unaffected.

Historical examples in this proposal describe a 30-task installer manifest: 6B became T003-T014, 6D remained T019, T012/T013 involved recovery, and T014 supplied integration proof. Neither `docs/agent-asset-installer/ExecPlan.md` nor its `tasks.json` exists in this checkout, so these counts and contracts are not current evidence. Preserve the lessons through self-contained synthetic fixtures; do not depend on or recreate unavailable installer internals.

## Surprises & Discoveries


The schema and consumer previously disagreed on whether `dependsOn` was mandatory. The producer and consumer now require the same complete contract for every task, including explicit dependencies and verification.

The pre-edit evaluation suite expected `outputs/prd.json`, `userStories`, and `parallelBatch`, contradicting the producer's `tasks.json` and `tasks`. Public CLI reproduction exposed the mismatch. Subsequent review repaired omitted original fields, invalid verification values and lost domain checks. Final review also repaired false UI rejection of database vocabulary, NUL-reference crashes, non-object timing crashes, and contradictory loop decision fields. Earlier incomplete synthetic passing artifacts remain invalid acceptance evidence; retained reproducers and new complete manifests establish the final result.

The first revised lifecycle output deferred a coverage audit behind implementation even though its inputs already existed. Supplemental semantic review rejected that dependency. The producer now requires a consumed outcome/artifact or mandatory source order for each edge and performs available coverage review during authoring. The affected rerun records its mapping immediately and retains four justified tasks. The first revised loop comparison read its worker skill; both loop versions were rerun with only their own loop skill. These earlier outputs remain unchanged as review history.

The baseline required the literal `Typecheck passes`. The revised contract uses explicit required, not-applicable, or unresolved classification while preserving real applicable checks. A known command can remain recorded when an unavailable host blocks its execution.

The current ExecPlan skill already requires self-contained plans, milestone state synchronized with Progress, actual acceptance evidence, checkpoint reconciliation, and a current contract separate from verified historical records. Its headings are `Write a self-contained plan`, `Required living sections`, `Reconcile the plan as work changes`, and `Keep the current contract separate from history`. The old proposed insertion headings no longer exist. Extend these rules instead of duplicating or weakening them.

The baseline `execplan-implement` equated checklist items with tasks and forbade tests after conflict-free rebases. The revised consumer derives tasks from the plan and requires composed-behavior proof against the integrated result. Neither ExecPlan skill depends on a task-decomposition schema.

## Decision Log


Implemented decision: retain both independent formats. An ExecPlan is self-contained design, task and acceptance authority. A task manifest supplies structured tasks and prerequisites when the separate decomposition workflow is used.

Implemented decision: preserve difficult invariants when splitting tasks. Rationale: recovery, metadata preservation, and transaction consistency may require deep reasoning even in a small task. Do not lower their acceptance bar to make a task appear easy.

Implemented decision: make dependencies, source references, required context, task type, and verification structured. Rationale: a consumer should not reconstruct these from scattered prose. Keep the task fields explicit and preserve recorded task IDs and completion evidence during updates.

Implemented decision: validate applicable checks rather than require a universal success phrase. Rationale: an unrun or inapplicable typecheck is not a pass. An existing failing check is still required and must not be relabeled inapplicable.

Implemented decision: evaluate semantic completeness and dispatch clarity, not task count or forced parallelism. Rationale: counting tasks can reward excessive fragmentation while leaving difficult reasoning hidden.

Decision, 2026-10-07, user and coordinator: keep the planning and implementation skills independent of the task-decomposition skill and its schema. `exec-plans` does not reference `execplan-implement`; neither ExecPlan skill references or knows the `spec-to-tasks` format. The ExecPlan itself records tasks, prerequisites and milestone acceptance. Never dispatch a milestone and its component tasks as duplicate work. Independent work can still share files or state and require serialization. The separate decomposition workflow may consume a plan as ordinary source material; this does not create a reverse dependency.

Decision, 2026-10-07, user and coordinator: use one complete task contract throughout the producer and consumers. Every task requires `dependsOn`, `sourceRefs`, `requiredContext`, `taskType`, and `verification` alongside the other schema fields. Validate completed tasks before any completion shortcut and report incomplete input without rewriting recorded state. A blocker leaves unfinished work unpassed and produces a bounded stop result, not another blind loop iteration.

The decisions define implementation targets. Only observed checks establish completion.

Decision, 2026-10-07, coordinator: accept source changes using public grader tests, preserved output comparisons and fresh-reader interpretation. Keep the unchanged broad rubric distinct from supplemental semantic findings. These observations do not establish live sandbox consumer execution, owner-host product acceptance, repeated-run variance or efficiency savings.

## Interfaces and Dependencies


Preserve the existing top-level `project`, `branchName`, `description`, and `tasks` fields. Preserve each task's existing ID, story mapping, title, description, acceptance criteria, likely files, design guidance, priority, `passes`, and `notes` fields. Newly generated tasks still start with `passes: false` and `notes: ""`. Reading or migrating an in-progress manifest must not reset completed work.

The following fields are implemented in `skills/spec-to-tasks/references/task-schema.md` and consumed by `skills/prd-ralph/references/intake.md`.

| Field | Shape | Meaning and validation |
| --- | --- | --- |
| `dependsOn` | Array of task ID strings | Explicit prerequisites. Empty means none. Reject unknown IDs, self-dependencies, duplicates, and cycles. Keep priorities/order consistent with prerequisite order. |
| `sourceRefs` | Array of objects with `path`, `section`, and `requirements` | Identify the originating plan and the requirements implemented or verified. Sections and requirement labels must resolve to actual source content. |
| `requiredContext` | Array of objects with `path`, `section`, and `purpose` | List the exact design or policy sections the worker must read, and why. Include inherited invariants; do not point every task at the entire plan by default. |
| `taskType` | One of `decision`, `implementation`, `verification`, `integration`, `documentation` | Identify the primary outcome. A valid task need not change product code. |
| `verification` | Array of check objects defined below | Define applicable checks and observable outcomes; these are planned checks, not claims that execution passed. |

Preserve the skill's support for inline input. When no source file exists, a `sourceRefs` or `requiredContext` entry may use `path: null` and `section: null`, with an additional `content` string containing the relevant original input or self-contained contract. Require nonempty `content` for this inline form; never invent a file path. Requirement labels must map to the captured content. The worker must receive those inline entries with the task. An empty `requiredContext` array is valid only when the task and manifest already supply all necessary design context.

A verification object contains `id`, `kind`, `applicability`, `command`, `workingDirectory`, `expected`, and `reason`. `kind` can be `test`, `typecheck`, `build`, `lint`, or `manual`. `applicability` is `required`, `not-applicable`, or `unresolved`. The working directory is repository-relative. A known command is a string. Use `null` when a check is manual, inapplicable, or its command has not yet been established. Explain that choice in `reason`.

For a required automated check, a known command and an observable expected result are necessary before execution. For a required manual check, describe the procedure and expected evidence. For an inapplicable check, give a verified reason. For an unresolved check, state what must be discovered; it cannot count as satisfied. A task may explicitly discover a verification procedure as its own deliverable, but that does not certify the product behavior awaiting that procedure.

The following is a complete illustrative task object for an inline documentation request. It demonstrates requirement/context preservation without unavailable installer paths or invented commands. The example's preceding T001 would establish the supplied current contract; a real manifest must include it. This adds fields to the current object rather than replacing the manifest format.

    {
      "id": "T002",
      "parentStoryId": "US-001",
      "title": "Document private-install refusal and preservation",
      "description": "Reconcile the supplied guide after the current-contract prerequisite, retaining metadata and no-write refusal rules.",
      "acceptanceCriteria": [
        "The guide accurately states that private installation preserves tracked files and both Git indexes.",
        "The guide describes conflict refusal before destination writes."
      ],
      "filesLikelyTouched": [],
      "designGuidance": [],
      "priority": 2,
      "passes": false,
      "notes": "",
      "dependsOn": ["T001"],
      "sourceRefs": [
        {
          "path": null,
          "section": null,
          "requirements": ["REQ-PRIVATE-INSTALL"],
          "content": "REQ-PRIVATE-INSTALL: Reconcile the supplied guide with the current private-install preservation and refusal contract."
        }
      ],
      "requiredContext": [
        {
          "path": null,
          "section": null,
          "purpose": "Preserve metadata authority and no-write refusal rules.",
          "content": "Current contract: tracked files and both Git indexes remain unchanged; conflicting destinations cause refusal before writes."
        }
      ],
      "taskType": "documentation",
      "verification": [
        {
          "id": "private-install",
          "kind": "manual",
          "applicability": "required",
          "command": null,
          "workingDirectory": ".",
          "expected": "Compare the guide with the inline contract; record the passages that preserve both indexes, tracked files, and refusal before writes.",
          "reason": "Direct document review establishes the requested outcome."
        },
        {
          "id": "typecheck",
          "kind": "typecheck",
          "applicability": "not-applicable",
          "command": null,
          "workingDirectory": ".",
          "expected": "The change remains documentation-only.",
          "reason": "The supplied scope changes prose, not executable code or declarations."
        }
      ]
    }

Do not infer safe parallel execution merely because tasks have no dependency edge. Shared files, state, or integration requirements can still require serialization. Adding a parallel scheduler or mandatory `parallelBatch` field is not part of this recommendation.

## Plan of Work


### Milestone 1: Strengthen the ExecPlan contract


Status: done

Acceptance: met

Implementation and source/read-only acceptance are complete. Comparison cases 0 and 1 pass all revised assertions; the fresh plan reader identifies the first command, full A1 acceptance, and owner-host boundary. The following specification records completed edits and must not be repeated. Existing living sections, current-contract rules and public acceptance remain intact.

The outline now shows a hypothetical milestone containing two tasks, multiple Progress entries for T1, and a separate milestone integration check. Both ExecPlan skills use task terminology. The planning skill defines a task graph through explicit prerequisites. The implementation skill references its dependency's shared rules and retains worker context, file ownership, scheduling, integration, and verification procedures. Source review and exec-plans validation passed; the implementation skill retains its known frontmatter-validator limitation. Earlier full-workflow comparisons predate the outline and terminology clarifications. A subsequent consumer-only comparison passed all nine existing assertions for both the pre-deduplication and revised versions; [review notes](/private/tmp/execplan-implement-dedupe.k2Z4FY/review-notes.md) retain the coverage map and evidence limits. This sampled read-only comparison does not establish live orchestration behavior or a performance improvement.

In `Write a self-contained plan` and `Required living sections`, add the missing task distinction:

> A milestone is a delivery and acceptance outcome, not automatically one worker task. Before dispatching a milestone, determine whether it contains independently deliverable behaviors, unrelated failure families, or unresolved design decisions. If so, decompose it into bounded tasks. Each task must state its required inputs, behavioral outcome, verification, and stopping boundary. Preserve the milestone's full acceptance and define the integration proof that remains after individual tasks pass.

In `Keep the current contract separate from history`, add stable task references while retaining the existing self-contained contract:

> Give task-referenced current requirements and active decisions stable headings or identifiers. Update affected task references when the contract changes. A worker must find the current rule without reconstructing chronological history. Keep required knowledge inline in the self-contained plan; references supplement it and never replace current requirements or permission boundaries.

Add the integration requirement to `Validation and observable acceptance` and illustrate it in `Outline`:

> For work split across tasks, identify shared invariants and the final observable proof that the tasks compose correctly. State which integration task or milestone check supplies that proof. Individual passing tasks do not establish milestone acceptance when cross-task behavior remains unverified. Preserve relevant regression and negative cases at their public boundary.

An invariant is a rule that must remain true across operations, such as preserving unrelated files or refusing conflicting edits. For the Windows example, separately passing installation and pruning does not establish recovery correctness when either operation is interrupted. T014 illustrates the required composition check. Its prerequisites should be explicit, and its acceptance should describe the combined behavior.

Use checkpoint 6B as a sizing example: keep its meaningful lifecycle outcome, but dispatch smaller tasks. Use 6D/T019 as a counterexample: a task that preserves the whole checkpoint is acceptable only when its actual work and verification justify that size. Do not force additional tasks merely to increase the count.

Verify this milestone by reading a generated plan as a fresh worker. The current contract must be identifiable, required design references must resolve, and a multi-task milestone must name its remaining integration proof. An unresolved architectural question must lead to a bounded decision/proof objective rather than silently becoming a worker's implementation responsibility.

The revised `skills/execplan-implement/SKILL.md` consumes `exec-plans` for task definitions, sizing, prerequisites, reconciliation, and acceptance. Its dispatch step forwards the full task and current plan context, prerequisite evidence, and explicit file ownership. Its execution checkpoints call the planning skill's reconciliation rules without repeating them. Preserve this one-way dependency; neither skill may depend on the separate task-decomposition workflow or its fields.

Preserve fresh workers per graph node, private branches, serial integration, repair ownership, commit guidelines, and safe cleanup. Apply TDD to source changes and use evidence appropriate to decision/documentation/verification work. After integrating related work, run required composed-behavior checks even if the rebase was conflict-free; avoid redundant checks only when evidence applies to the integrated tree. Update milestone status, acceptance, Progress, Concrete Steps, and Outcomes together. Pending owner actions or external checks remain open even when implementation commits are complete. Add create/modify/blocked consumer scenarios under `skills/execplan-implement/evals/` and keep existing ExecPlan grader cases intact.

### Milestone 2: Produce bounded tasks with explicit context and verification


Status: done

Acceptance: met

Implementation, source validation and semantic output review are complete. Final lifecycle and inline-document cases satisfy all shared assertions. The fresh task reader finds the full documentation contract; the negative reader stops on a missing prerequisite decision even when its pass flag is true. The following specification records completed edits.

After decomposition and before schema validation, the implemented sizing rule is:

> Evaluate each task by its behavioral scope, unresolved decisions, coupled state, environment uncertainty, and verification burden. A task should have one central outcome. Split independently deliverable behaviors and unrelated failure families. Do not split a vertical slice into code-only and test-only tasks, detach necessary negative cases, or reduce acceptance to make the task appear small. If correctness requires an indivisible complex task, state the reasoning risks and provide bounded entry points. Respect supplied execution limits; do not invent time/token budgets or assume a task fits one attempt because it has one ID.

Put any remaining reasoning risks and bounded entry points in `description` or `designGuidance`; another mandatory complexity-score field is unnecessary. Avoid numeric difficulty scores that have no calibration. A state-machine repair can be narrow and still difficult.

For T012/T013, retain the full recovery contract, but identify particular public interruption states as bounded starting points. Completing one starting point does not mark the entire task passed. For a task like T020, identify distinct observed failures before making a blanket task to fix generator portability. Keep prerequisite inventory separate from assuming every observed error is a product defect.

Add the structured fields defined above. Replace prose-only prerequisites with `dependsOn`. Preserve meaningful mandatory order; do not infer dependencies from ID order alone. Use `sourceRefs` for requirement coverage and `requiredContext` for the exact design the worker needs. These fields have different purposes even when they reference the same plan.

The unconditional `Typecheck passes` rule was replaced in the main skill, schema example, and validation checklist with this contract:

> Define applicable verification using existing repository commands and behavior-focused evidence. For typecheck and other relevant check categories, record a required check, a verified non-applicability reason, or an unresolved prerequisite. Never invent a command, claim an unrun check passed, or relabel a failing applicable check as inapplicable. Generated tasks describe expected results; only subsequent execution evidence establishes a pass. Documentation and decision tasks require appropriate document/evidence validation rather than fabricated product checks.

Keep applicable typechecking, building, linting, tests, and existing UI verification requirements. This is a more accurate applicability contract, not permission to suppress checks. Preserve exact failure cases and requirements while changing outdated schema wording.

Add task-type guidance. A `decision` task resolves a named uncertainty and records its approved boundary. An `implementation` task delivers behavior. A `verification` task collects specified evidence. An `integration` task proves combined behavior. A `documentation` task reconciles claims or instructions. Each type still needs a concrete outcome and verification. Task type must not become an excuse for horizontal fragments that have no independent value.

Verify this milestone with both ordinary and difficult tasks. A fresh worker should find the prerequisite IDs, relevant contract, exact first known check, full acceptance, and stop conditions. An unknown command or unavailable environment must remain visible. Generic phrases such as "run the relevant tests" are insufficient when exact applicable commands are known.

### Milestone 3: Align consumers and evaluation contracts


Status: done

Acceptance: met

Consumer edits and grader review are complete; 34 producer and 10 loop CLI tests pass. A new complete documentation artifact passes 10/10 assertions; the lifecycle artifact passes nine and correctly fails readiness because commands/environment are unresolved. Read-only Ralph and loop responses preserve context, commit constraints and result protocol. The following specification records completed work. Readiness is not execution authorization, and these interpretations do not establish execution of every disposable consumer scenario.

The single-task consumer validates the complete task contract before selection or completion detection, consumes every field and inline content, resolves references, and applies checks by task type. Preserve existing IDs, completion evidence, one-task-per-run behavior, user limits, and commit policy. Mark only the selected task passed after its full applicable checks pass; unresolved or failed checks remain unfinished.

The loop preserves its `Stay blind` boundary: it forwards manifest paths and user constraints, then consumes the worker's completion/blocked protocol rather than reading task content itself. Its explicit blocked stop branch prevents missing context, invalid prerequisites, unresolved checks, or owner-only work from causing endless dispatch. Preserve the completion marker and domain behavior. Retain completion, blocked, forwarded-input, and commit-policy scenarios.

Align `skills/spec-to-tasks/evals/evals.json` and `evals/grade_benchmark.py` with the chosen contract. Artifact paths must match `tasks.json`; the collection is `tasks`; defaults and the new fields must be checked. Adjust prompts that request incompatible output paths rather than asking a grader to guess between formats.

Preserve domain coverage in all current fixtures: status operations, member management, notifications, and token behavior still need validation. Replace obsolete exact-count or mandatory-parallelism expectations with required behaviors and justified task boundaries. Retain a count constraint only when the input explicitly requires it. Do not delete negative cases or weaken behavior checks to improve the score. Document the schema amendment and add stronger checks for omitted requirements and invalid prerequisites.

Because the grader is Python source, follow the repository's test-first rules if it is edited. Reproduce the public grading mismatch using a disposable run directory containing a valid current-format artifact. Then verify the repaired grader through the same CLI. Add invalid manifests that are parseable JSON but must fail semantic grading. A grader that writes files or exits successfully has not necessarily reported passing expectations; inspect `grading.json`.

Acceptance is a manifest that follows the complete producer/consumer contract and a grader that accepts a complete valid artifact, rejects the deliberate invalid examples, and retains the original domain requirements.

### Milestone 4: Demonstrate clearer tasks without lost requirements


Status: done

Acceptance: met

Six paired outputs and three fresh-reader interpretations are reviewed. Revised outputs satisfy 18/18 shared assertions versus 17/18 for the frozen baseline. Five cases tie under this broad rubric; the distinguishing assertion is explicit `TASK_COMPLETE` after a successful nonfinal task. Separate semantic review caught and repaired the deferred-authoring-review dependency. No timing/token or general performance claim follows from this small sample. The following procedure records how evidence was collected.

Use the existing status/member/token domain fixtures and add a self-contained lifecycle fixture under `skills/spec-to-tasks/evals/files/`. State the invariants, interruption/refusal cases, decision boundary, verification commands or unresolved prerequisites, and final integration evidence in that fixture. The unavailable installer documents are historical inspiration only. Do not implement product work, invoke native clients, or change real task completion state to evaluate these authoring skills. Baseline snapshots were captured before edits under `/private/tmp/exec-plan-tasks-improvements/<skill>-workspace/skill-snapshot/`.

Run baseline and revised skills against the same fixtures with the same available model, reasoning setting, tool access, and context boundary. Record actual settings. Follow the repository's canonical evaluation layout: one `iteration-N/eval-*/eval_metadata.json` with config-specific `run-*` directories underneath it. Keep generated results in a sibling `*-workspace/` directory. Never use an installed copy accidentally when testing a changed source skill.

Use a separate run with only the generated task, manifest constraints, prerequisite evidence, and explicitly required references. Ask the worker to explain the next authorized action, first verification step, completion condition, and stopping boundary without executing product work. Record every additional unlisted document needed. This reveals hidden context that JSON shape checks cannot detect.

The next section supplies the acceptance cases. Check semantic completeness first. Compare time, tokens, and tool calls only when actually measured. More task sessions can increase repeated setup and integration work; do not claim total reasoning savings from a larger task count.

## Concrete Steps


No implementation step remains for this request. The next review action is to inspect [the comparison viewer](/private/tmp/exec-plan-tasks-improvements/comparison/review.html) and the uncommitted source diff. [Selection provenance](/private/tmp/exec-plan-tasks-improvements/comparison/selected/iteration-1/selection-provenance.json) identifies every preserved source run, hash and viewer-only adaptation. Do not rerun completed work or install personal copies merely to resume this plan. A later changed requirement should reopen only affected acceptance.

From the repository root, these existing commands support inspection and static verification:

    rtk git status --short
    rtk proxy rg -n 'tasks.json|userStories|parallelBatch|dependsOn|Typecheck passes' skills/spec-to-tasks skills/prd-ralph skills/prd-ralph-loop
    rtk proxy env PYTHONPATH=scripts/vendor python3 skills/skill-creator/scripts/quick_validate.py skills/spec-to-tasks
    rtk proxy env PYTHONPATH=scripts/vendor python3 skills/skill-creator/scripts/quick_validate.py .agents/skills/exec-plans
    rtk proxy python3 skills/spec-to-tasks/evals/test_grade_benchmark.py
    rtk proxy python3 skills/prd-ralph-loop/evals/test_grade_benchmark.py
    rtk proxy python3 scripts/test_test_all.py
    rtk git diff --check

The validator commands use the repository's vendored YAML dependency. Do not install packages implicitly if validation cannot run. `quick_validate.py` checks skill structure/frontmatter; it does not prove task quality. Preserve any approved frontmatter keys even if a validator has a known limitation.

After changing evaluation definitions, parse `skills/spec-to-tasks/evals/evals.json` as JSON. If grader code changes, compile it with a disposable bytecode-cache location and run its targeted tests. The following compile command avoids writing cache files into the source tree:

    rtk proxy env PYTHONPYCACHEPREFIX=/private/tmp/exec-plan-tasks-pycache python3 -m py_compile skills/spec-to-tasks/evals/grade_benchmark.py

Use the equivalent disposable temporary directory on another operating system. Compilation checks syntax only and cannot establish behavioral correctness.

The final producer CLI run used this retained directory, with comparison cases mapped to the producer grader's lifecycle/document IDs:

    rtk proxy python3 skills/spec-to-tasks/evals/grade_benchmark.py /private/tmp/exec-plan-tasks-improvements/producer-validation/iteration-1

Inspect each run's `grading.json`, including failed expectations and evidence. Do not treat the grader's process exit alone as acceptance. Validate generated `tasks.json` files for JSON syntax and the semantic rules below. No general-purpose task-schema validator has been established by this guide; extend the existing grader or add a narrowly scoped validator only if needed, and document its actual invocation after it exists.

At the end of implementation, run the required documentation maintenance pass once. Update canonical instructions/memory only for implemented durable changes and new verified gotchas. Apply their formatting rules if those files change. Do not document these proposals as existing behavior before implementation.

## Validation and Acceptance


Use the following fixtures and deliberate mutations. Lifecycle, inline-document, consumer, and loop scenarios now exist under the relevant skill's `evals/` tree. The resumed check parsed all 16 JSON scenario and fixture files. Repository-local ExecPlan evaluations use the disposable external workspace with the canonical layout; the skill remains repository-local.

| Case | Required result |
| --- | --- |
| Large lifecycle milestone, based on 6B | Produce bounded behavioral tasks, preserve the full lifecycle contract, and identify the final integration proof. Do not mandate exactly 12 tasks. |
| Indivisible difficult recovery, based on T012/T013 | Retain interruption, repeated-recovery, authority, metadata, and refusal requirements. Flag high reasoning demands and bounded entry points without making each partial proof a completed task. |
| Checkpoint copied into one task, based on 6D/T019 | Explicitly assess scope and verification burden. Keep one task only when justified; do not reward renaming alone or force a split solely for count. |
| Missing dependency | Delete a real prerequisite from `dependsOn` while leaving it in prose. Semantic review must reject the mismatch. |
| Invalid dependency graph | Add an unknown ID, self-edge, duplicate edge, or cycle. Validation must fail each case with the relevant IDs. |
| Hidden context | Remove a required metadata/current-contract reference. A fresh-worker review must flag the missing authority instead of inventing it. |
| Dropped negative requirement | Remove conflict/refusal or interrupted-recovery acceptance while leaving happy paths. Coverage grading must fail. |
| Missing integration proof | Make all implementation tasks pass in a synthetic fixture but omit the shared-invariant check. Milestone acceptance must remain unmet. |
| Documentation-only task | Require actual document/evidence checks and a justified typecheck applicability decision. Reject fabricated typecheck success. |
| Applicable failing typecheck | Relabel a known required failing check as inapplicable. Validation must reject it. |
| Unknown command or unavailable host | Preserve the unresolved prerequisite. Do not invent a command, install a runtime, or count missing evidence as a pass. |
| Superseded plan decision | Put an old incompatible rule in history. The current rule and supersession link must be clear; generated tasks must use the current contract. |
| Existing domain fixtures | Preserve all explicit behaviors and negative cases while switching their output/schema expectations to the chosen contract. |
| Inline-only source input | Preserve required source/context in the inline reference form. Reject fabricated paths and missing inline content. |
| Consumer readiness | A dependent task remains ineligible until prerequisites pass. Required context/checks are read even when the task description is short. |

Structural validation must confirm required fields, allowed types, unique sequential IDs, ascending priorities, valid dependencies, source/context destinations, and fresh-task defaults. Coverage validation maps every explicit requirement, edge case, fallback, negative state, and integration gate to at least one task or acceptance check. Being parseable JSON is necessary but insufficient.

Human or model review should use a fixed rubric: identify any requirement dropped, unjustified dependency, unresolved design decision hidden inside implementation, unsafe fragmentation, broad task without a sizing explanation, invented verification, or completion claim unsupported by evidence. Record concrete examples rather than a subjective "looks good" score.

The change is accepted when valid outputs pass these checks, deliberately invalid outputs fail for the intended reasons, consumers honor the new fields, and the fresh-worker exercise exposes no missing critical context. Record remaining uncertainty honestly. Do not invent a percentage reduction in reasoning, tokens, or execution time.

## Idempotence and Recovery


Keep baseline skill snapshots and evaluation artifacts separate from maintained source. Use a fresh iteration directory for each comparison. Repeating validation must not reset task progress, mutate the live installer plan, or update personal installed skills.

If the producer and consumer disagree on the contract, keep the change unpublished until they agree. Reject incomplete task records without overwriting existing completion evidence. If an evaluation result fails, preserve its artifact and diagnostic, make a focused correction, and rerun the affected case before broadening evaluation.

## Outcomes & Retrospective


All five skill entry points and dependent references are revised and reviewed. The producer defines dependencies, current context, task types and applicable checks; Ralph intake applies the complete contract to every task and explicitly blocks incomplete input or evidence. The loop remains blind. Both ExecPlan skills preserve the user's independence boundary. The runner registers the two new public grader suites.

Final observed checks: 34 producer grader tests, 10 loop grader tests, all 16 scenario/fixture JSON files, Python compilation, supported skill validators, whitespace review and OKF lint pass. Earlier 35 ExecPlan grader and 14 runner tests apply to unchanged source. The generic validator still rejects required `disable-model-invocation` frontmatter in two consumers; those controls and `execplan-implement/agents/openai.yaml` remain intact. This is a known validation limitation, not a passing result.

The complete documentation manifest passes all ten producer CLI assertions. The valid lifecycle shape correctly fails only readiness, since its fixture has no runtime/commands. Earlier six paired outputs yield 18/18 revised versus 17/18 baseline shared assertions. All three fresh-reader exercises identify the required action/check/boundary, including the intended missing-decision stop. These comparisons predate the removal of compatibility guidance; its acceptance uses source review, the 44 existing grader tests, 16 JSON parses, and skill validation. The obsolete compatibility scenario and fixture were removed; no new regression tests were added for that deletion. The review viewer and provenance are retained. No consumer sandbox execution, product work, owner-host memory measurement, personal installation, Git commit or push was performed.

Expected benefit is less repeated interpretation during worker execution. Hard technical reasoning and cross-task integration remain explicit responsibilities. Total project effort may include additional context loading, review, and integration, so efficiency claims require measured comparisons.

## Artifacts and Notes


This guide preserves all seven original recommendation groups: three for ExecPlans (task boundaries, current design extraction, integration proof) and four for task decomposition (sizing, structured dependencies/context/type, applicable verification, semantic validation). It also includes the shared fresh-worker evaluation method and the newly verified consumer/evaluation compatibility issues.

The requested plan and [feature handoff](handoff.md) remain beside each other. The final canonical pass updated skills guidance, grader contracts/testing, and the retained-effort map; existing routing/index changes remain. Only the OKF profile branch applied, and lint exited 0. No canonical file was added, split, moved or removed; no documentation quality TODO remains.

Evidence is local and disposable under `/private/tmp/exec-plan-tasks-improvements/`: [review notes](/private/tmp/exec-plan-tasks-improvements/comparison/review-notes.md), [benchmark](/private/tmp/exec-plan-tasks-improvements/comparison/selected/iteration-1/benchmark.json), [fresh plan reader](/private/tmp/exec-plan-tasks-improvements/fresh-readers/plan/result.md), [fresh task reader](/private/tmp/exec-plan-tasks-improvements/fresh-readers/task/result.md), and [missing-context reader](/private/tmp/exec-plan-tasks-improvements/fresh-readers/missing-context/result.md). Earlier outputs, invalid fixtures and public reproductions remain unchanged.

The [earlier dispatch audit](/private/tmp/exec-plan-tasks-improvements/dispatch-audit.json) and [resumed audit](/private/tmp/exec-plan-tasks-improvements/dispatch-audit-resumed.json) distinguish selected/submitted settings from unconfirmed execution settings. They retain the corrected implicit dispatch and missed warning checkpoints, including the final grader repair's unverified threshold compliance. No delegated result is treated as runtime configuration evidence.
