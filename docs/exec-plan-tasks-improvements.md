# Improve ExecPlans and task decomposition


Prepared 2026-10-07. Status: recommendations saved for future implementation. Saving this document does not apply the proposed skill or schema changes. Its destination, `.agents/scratchpad/exec-plan-tasks-improvements.md`, is Git-ignored in this repository.

This guide uses the ExecPlan structure to make the recommendations implementable by a novice. Its improvement milestones are separate from the agent-asset installer's milestones. Keep Progress, decisions, findings, and outcomes current if this guide is later implemented.

## Purpose / Big Picture


Improve the connection between two skills: `exec-plans` describes the design, constraints, and final acceptance; `spec-to-tasks` produces bounded assignments that workers can execute without reconstructing the entire plan.

Reduce reasoning breadth without hiding necessary technical depth. A smaller assignment reduces the number of unrelated facts, decisions, and failures an agent must track. It does not make a difficult recovery algorithm easy. Preserve the full correctness contract when splitting work, including negative cases and integration proof.

Success means a fresh agent can identify its prerequisites, required design context, first verification step, completion condition, and stopping boundary from a task and its explicitly required references. Judge fewer missing requirements, invented commands, unjustified completion claims, and unlisted context searches. Task count and document length are not success measures.

## Progress


- [x] (2026-10-07) [preparation] Record all recommendations, current evidence, proposed edits, compatibility considerations, and verification procedures in this guide.
- [ ] [improvement-1] Update the ExecPlan contract for assignment boundaries, extractable current decisions, and integration proof.
- [ ] [improvement-2] Update task sizing, structured dependencies/context, task types, and applicable verification.
- [ ] [improvement-3] Align affected consumers and evaluation contracts, preserving behavioral coverage.
- [ ] [improvement-4] Verify structural rules and compare baseline versus revised skill behavior using controlled fixtures.

## Context and Orientation


Run repository commands from `/Users/adam/.codex/worktrees/2af1/skills`, or the corresponding repository root in a later checkout. Paths below are repository-relative unless stated otherwise. A skill's `SKILL.md` is its entry point; linked reference files provide detailed rules. A benchmark grader checks the artifacts produced during a skill evaluation.

| File | Role in this change |
| --- | --- |
| [ExecPlan skill](../.agents/skills/exec-plans/SKILL.md) | Repository-local authoritative skill. Change its milestone, current-design, and integration guidance. |
| [Task-decomposition skill](../skills/spec-to-tasks/SKILL.md) | Publishable source. Change sizing and verification requirements and route readers to its references. |
| [Task schema](../skills/spec-to-tasks/references/task-schema.md) | Define the proposed fields and their meanings. |
| [Task validation checklist](../skills/spec-to-tasks/references/validation.md) | Validate dependencies, coverage, context, sizing, and verification applicability. |
| [PRD handling](../skills/spec-to-tasks/references/prd-handling.md) | Inspect for conflicting task/output rules when changing the main contract. |
| [Existing evaluations](../skills/spec-to-tasks/evals/evals.json) | Update prompts and expectations to match the task contract; add the cases described below. |
| [Existing grader](../skills/spec-to-tasks/evals/grade_benchmark.py) | Align artifact discovery and semantic checks with the revised schema. |
| [Single-task consumer](../skills/prd-ralph/SKILL.md) | Already reads `dependsOn`; inspect and update its explicit task-reading list when adding fields. |
| [Loop consumer](../skills/prd-ralph-loop/SKILL.md) | Inspect forwarding, selection, and completion behavior for compatibility. Change only demonstrated incompatibilities. |
| Historical installer ExecPlan, recorded as `docs/agent-asset-installer/ExecPlan.md` | Unavailable in this checkout. Recover the original example before using it as evidence or fixture input; it is not an implementation target. |
| Historical installer task file, recorded as `docs/agent-asset-installer/tasks.json` | Unavailable in this checkout. The discussion below preserves the recorded example, not a verified current decomposition. |
| [Skill conventions](../.agents/instructions/skills.md) and [skill testing](../.agents/instructions/testing/skills.md) | Repository requirements for authoring, snapshots, evaluation layout, and validation. |

The earlier discussion read the installed `spec-to-tasks` copy under `/Users/adam/.agents/skills/`. Its main skill, schema, and validation reference currently match the repository source byte for byte. Implement changes in `skills/spec-to-tasks/`, not the installed personal copy. A source edit does not refresh installed skills. The repository-local ExecPlan skill lives under `.agents/skills/`; implementation requires an instruction that actually authorizes editing that protected skill, rather than treating this saved proposal as such authorization.

The historical task-file example was recorded as 30 tasks covering the remaining portions of installer milestones 6 and 7. In that example, checkpoint 6B became T003-T014, checkpoint 6D remained essentially T019, T012/T013 required deep interruption/recovery reasoning, and T014 collected integration reasoning. The source artifacts are absent from this checkout, so these details need rechecking before constructing fixtures. They illustrate why a task label or a high task count does not guarantee a small assignment.

## Surprises & Discoveries


The task schema currently has no `dependsOn` field, although task descriptions encode dependencies in prose. The single-task consumer already uses `dependsOn` to determine eligibility and treats a missing field as no dependencies. This mismatch can make an unfinished prerequisite invisible to selection. Structured dependencies are therefore functional data, not merely nicer documentation.

The current evaluation suite expects `outputs/prd.json`, `userStories`, and `parallelBatch`, while the main skill and schema specify `tasks.json` and `tasks`. Several expectations also enforce an exact task count, a minimum count, or parallel batches. Inspect `evals/evals.json` and the grader's `all_story_defaults` and dependency/batch checks. Align the contract before using benchmark results to judge the improvement.

The main skill, schema example, validation checklist, and grader currently require the literal criterion `Typecheck passes`. That is not a meaningful completion condition for every decision, evidence, or documentation task. Replace the blanket phrase with applicability-aware verification while preserving every real applicable check.

The ExecPlan already contains substantial design and test guidance. The proposed improvement is extracting reliable execution boundaries and required context, not compensating for an absence of design.

## Decision Log


Proposed decision: keep both formats. The ExecPlan remains the design and acceptance authority; `tasks.json` remains the assignment and prerequisite manifest. Rationale: neither milestone-level coordination nor narrow worker execution replaces the other.

Proposed decision: preserve difficult invariants when splitting tasks. Rationale: recovery, metadata preservation, and transaction consistency may require deep reasoning even in a small assignment. Do not lower their acceptance bar to make a task appear easy.

Proposed decision: make dependencies, source references, required context, task type, and verification structured. Rationale: a consumer should not reconstruct these from scattered prose. Preserve existing fields unless a compatibility review establishes a reason to migrate them.

Proposed decision: validate applicable checks rather than require a universal success phrase. Rationale: an unrun or inapplicable typecheck is not a pass. An existing failing check is still required and must not be relabeled inapplicable.

Proposed decision: evaluate semantic completeness and dispatch clarity, not task count or forced parallelism. Rationale: counting tasks can reward excessive fragmentation while leaving difficult reasoning hidden.

These are recommendations recorded on 2026-10-07, not evidence that the changes have been implemented or validated.

## Interfaces and Dependencies


Preserve the existing top-level `project`, `branchName`, `description`, and `tasks` fields. Preserve each task's existing ID, story mapping, title, description, acceptance criteria, likely files, design guidance, priority, `passes`, and `notes` fields. Newly generated tasks still start with `passes: false` and `notes: ""`. Reading or migrating an in-progress manifest must not reset completed work.

Add the following task fields to `references/task-schema.md`. Their definitions must also be understood by task consumers before readiness is advertised.

| Proposed field | Shape | Meaning and validation |
| --- | --- | --- |
| `dependsOn` | Array of task ID strings | Explicit prerequisites. Empty means none. Reject unknown IDs, self-dependencies, duplicates, and cycles. Keep priorities/order consistent with prerequisite order. |
| `sourceRefs` | Array of objects with `path`, `section`, and `requirements` | Identify the originating plan and the requirements implemented or verified. Sections and requirement labels must resolve to actual source content. |
| `requiredContext` | Array of objects with `path`, `section`, and `purpose` | List the exact design or policy sections the worker must read, and why. Include inherited invariants; do not point every task at the entire plan by default. |
| `taskType` | One of `decision`, `implementation`, `verification`, `integration`, `documentation` | Identify the primary outcome. A valid task need not change product code. |
| `verification` | Array of check objects defined below | Define applicable checks and observable outcomes; these are planned checks, not claims that execution passed. |

Preserve the skill's support for inline input. When no source file exists, a `sourceRefs` or `requiredContext` entry may use `path: null` and `section: null`, with an additional `content` string containing the relevant original input or self-contained contract. Require nonempty `content` for this inline form; never invent a file path. Requirement labels must map to the captured content. The worker must receive those inline entries with the task. An empty `requiredContext` array is valid only when the task and manifest already supply all necessary design context.

A verification object contains `id`, `kind`, `applicability`, `command`, `workingDirectory`, `expected`, and `reason`. `kind` can be `test`, `typecheck`, `build`, `lint`, or `manual`. `applicability` is `required`, `not-applicable`, or `unresolved`. The working directory is repository-relative. A known command is a string. Use `null` when a check is manual, inapplicable, or its command has not yet been established. Explain that choice in `reason`.

For a required automated check, a known command and an observable expected result are necessary before execution. For a required manual check, describe the procedure and expected evidence. For an inapplicable check, give a verified reason. For an unresolved check, state what must be discovered; it cannot count as satisfied. A task may explicitly discover a verification procedure as its own deliverable, but that does not certify the product behavior awaiting that procedure.

The following is a complete proposed task object for a hypothetical fixture. `fixture-plan.md`, `Current contract`, and `REQ-PRIVATE-INSTALL` are fixture labels that must be created before validating this example; they are not claimed repository files or requirements. The command shown is an existing public test selector. This example adds fields to the current object rather than replacing the manifest format.

    {
      "id": "T002",
      "parentStoryId": "US-001",
      "title": "Preserve Git state during private installation",
      "description": "Deliver private installation after the team-install prerequisite, retaining the fixture's metadata and no-write refusal rules.",
      "acceptanceCriteria": [
        "Private installation preserves tracked files and both Git indexes.",
        "Conflicting existing state causes refusal without destination writes."
      ],
      "filesLikelyTouched": [
        "scripts/agent_assets/transaction.py",
        "scripts/test-agent-assets.py"
      ],
      "designGuidance": [],
      "priority": 2,
      "passes": false,
      "notes": "",
      "dependsOn": ["T001"],
      "sourceRefs": [
        {
          "path": "fixture-plan.md",
          "section": "Private installation",
          "requirements": ["REQ-PRIVATE-INSTALL"]
        }
      ],
      "requiredContext": [
        {
          "path": "fixture-plan.md",
          "section": "Current contract",
          "purpose": "Preserve metadata authority and no-write refusal rules."
        }
      ],
      "taskType": "implementation",
      "verification": [
        {
          "id": "private-install",
          "kind": "test",
          "applicability": "required",
          "command": "rtk proxy python3 scripts/test-agent-assets.py --group scopes -k test_local_install_is_private_and_preserves_git_metadata_and_indexes",
          "workingDirectory": ".",
          "expected": "The named public case passes on the authorized target host with its file/index/privacy assertions intact.",
          "reason": "Existing public behavior and verification entry point."
        },
        {
          "id": "typecheck",
          "kind": "typecheck",
          "applicability": "unresolved",
          "command": null,
          "workingDirectory": ".",
          "expected": "Identify an applicable existing check or establish non-applicability before claiming task completion.",
          "reason": "No dedicated typecheck command was established by the source plan."
        }
      ]
    }

Do not infer safe parallel execution merely because tasks have no dependency edge. Shared files, state, or integration requirements can still require serialization. Adding a parallel scheduler or mandatory `parallelBatch` field is not part of this recommendation.

## Plan of Work


### Milestone 1: Strengthen the ExecPlan contract


Status: open

Acceptance: not met

Edit `.agents/skills/exec-plans/SKILL.md`. Preserve its existing self-contained-plan requirement, living sections, public acceptance, explicit milestone state, and synchronized progress rules. Add focused guidance to the existing sections instead of creating a second planning workflow.

Under `Milestones`, insert this proposed rule:

> A milestone is a delivery and acceptance outcome, not automatically one worker assignment. Before dispatching a milestone, determine whether it contains independently deliverable behaviors, unrelated failure families, or unresolved design decisions. If so, decompose it into bounded tasks. Each assignment must state its required inputs, behavioral outcome, verification, and stopping boundary. Preserve the milestone's full acceptance and define the integration proof that remains after individual tasks pass.

Under `Living plans and design decisions`, insert this proposed rule:

> Keep the current contract and active decisions easy to identify through stable section headings or explicit identifiers. Separate active requirements, unresolved questions, and superseded historical decisions. Record what superseded a decision. A worker must be able to read the exact referenced design sections without reconstructing current rules from chronological history. Keep all necessary knowledge within the self-contained plan or its already-supported checked-in references.

Add an integration requirement to `Milestones` and show it in the skeleton:

> For work split across tasks, identify shared invariants and the final observable proof that the tasks compose correctly. State which integration task or milestone check supplies that proof. Individual passing tasks do not establish milestone acceptance when cross-task behavior remains unverified. Preserve relevant regression and negative cases at their public boundary.

An invariant is a rule that must remain true across operations, such as preserving unrelated files or refusing conflicting edits. For the Windows example, separately passing installation and pruning does not establish recovery correctness when either operation is interrupted. T014 illustrates the required composition check. Its prerequisites should be explicit, and its acceptance should describe the combined behavior.

Use checkpoint 6B as a sizing example: keep its meaningful lifecycle outcome, but dispatch smaller tasks. Use 6D/T019 as a counterexample: a task that preserves the whole checkpoint is acceptable only when its actual work and verification justify that size. Do not force additional tasks merely to increase the count.

Verify this milestone by reading a generated plan as a fresh worker. The current contract must be identifiable, required design references must resolve, and a multi-task milestone must name its remaining integration proof. An unresolved architectural question must lead to a bounded decision/proof objective rather than silently becoming a worker's implementation responsibility.

### Milestone 2: Produce bounded tasks with explicit context and verification


Status: open

Acceptance: not met

Edit `skills/spec-to-tasks/SKILL.md`, `references/task-schema.md`, and `references/validation.md` together. Keep the main entry point concise; put field definitions and detailed validation in the existing references.

After decomposition and before schema validation, require a sizing pass with this proposed text:

> Evaluate each task by its behavioral scope, unresolved decisions, coupled state, environment uncertainty, and verification burden. A task should have one central outcome. Split independently deliverable behaviors and unrelated failure families. Do not split a vertical slice into code-only and test-only tasks, detach necessary negative cases, or reduce acceptance to make the task appear small. If correctness requires an indivisible complex task, state the reasoning risks and provide bounded entry points. Respect supplied execution limits; do not invent time/token budgets or assume a task fits one attempt because it has one ID.

Put any remaining reasoning risks and bounded entry points in `description` or `designGuidance`; another mandatory complexity-score field is unnecessary. Avoid numeric difficulty scores that have no calibration. A state-machine repair can be narrow and still difficult.

For T012/T013, retain the full recovery contract, but identify particular public interruption states as bounded starting points. Completing one starting point does not mark the entire task passed. For a task like T020, identify distinct observed failures before making a blanket assignment to fix generator portability. Keep prerequisite inventory separate from assuming every observed error is a product defect.

Add the structured fields defined above. Replace prose-only prerequisites with `dependsOn`. Preserve meaningful mandatory order; do not infer dependencies from ID order alone. Use `sourceRefs` for requirement coverage and `requiredContext` for the exact design the worker needs. These fields have different purposes even when they reference the same plan.

Replace the unconditional `Typecheck passes` rule in the main skill, schema example, and validation checklist with this proposed text:

> Define applicable verification using existing repository commands and behavior-focused evidence. For typecheck and other relevant check categories, record a required check, a verified non-applicability reason, or an unresolved prerequisite. Never invent a command, claim an unrun check passed, or relabel a failing applicable check as inapplicable. Generated tasks describe expected results; only subsequent execution evidence establishes a pass. Documentation and decision tasks require appropriate document/evidence validation rather than fabricated product checks.

Keep applicable typechecking, building, linting, tests, and existing UI verification requirements. This is a more accurate applicability contract, not permission to suppress checks. Preserve exact failure cases and requirements while changing outdated schema wording.

Add task-type guidance. A `decision` task resolves a named uncertainty and records its approved boundary. An `implementation` task delivers behavior. A `verification` task collects specified evidence. An `integration` task proves combined behavior. A `documentation` task reconciles claims or instructions. Each type still needs a concrete outcome and verification. Task type must not become an excuse for horizontal fragments that have no independent value.

Verify this milestone with both ordinary and difficult tasks. A fresh worker should find the prerequisite IDs, relevant contract, exact first known check, full acceptance, and stop conditions. An unknown command or unavailable environment must remain visible. Generic phrases such as "run the relevant tests" are insufficient when exact applicable commands are known.

### Milestone 3: Align consumers and evaluation contracts


Status: open

Acceptance: not met

Inspect consumers before publishing a schema change. `skills/prd-ralph/SKILL.md` already checks `dependsOn`, but its explicit implementation reading list names only existing fields. Update the applicable reading/verification guidance so workers consume the manifest's global constraints, selected task, `taskType`, `sourceRefs`, `requiredContext`, and `verification`, plus prerequisite completion evidence. Readiness is not execution authorization. Preserve existing user-imposed limits and permissions.

Check `skills/prd-ralph-loop/SKILL.md` and related references for assumptions about field names, selection, pass flags, and forwarding. Limit changes to demonstrated compatibility needs. Do not rewrite the orchestration system or introduce a scheduler. Do not claim that the new manifest is ready for a consumer that ignores its required context or verification fields.

Preserve old manifests as legacy input if the consumer currently supports them. Missing new fields in a legacy file must not be advertised as satisfying the new quality contract. For a migration, reconstruct dependencies and required context from the source plan, preserve IDs/completion evidence, and validate before use. Do not silently migrate the live installer task file as part of evaluating these skill edits.

Align `skills/spec-to-tasks/evals/evals.json` and `evals/grade_benchmark.py` with the chosen contract. Artifact paths must match `tasks.json`; the collection is `tasks`; defaults and the new fields must be checked. Adjust prompts that request incompatible output paths rather than asking a grader to guess between formats.

Preserve domain coverage in all current fixtures: status operations, member management, notifications, and token behavior still need validation. Replace obsolete exact-count or mandatory-parallelism expectations with required behaviors and justified task boundaries. Retain a count constraint only when the input explicitly requires it. Do not delete negative cases or weaken behavior checks to improve the score. Document the schema amendment and add stronger checks for omitted requirements and invalid prerequisites.

Because the grader is Python source, follow the repository's test-first rules if it is edited. Reproduce the public grading mismatch using a disposable run directory containing a valid current-format artifact. Then verify the repaired grader through the same CLI. Add invalid manifests that are parseable JSON but must fail semantic grading. A grader that writes files or exits successfully has not necessarily reported passing expectations; inspect `grading.json`.

Acceptance is a consumer-compatible manifest and a grader that accepts a complete valid artifact, rejects the deliberate invalid examples, and retains the original domain requirements. Existing legacy compatibility must either remain verified or have an explicit migration path.

### Milestone 4: Demonstrate clearer assignments without lost requirements


Status: open

Acceptance: not met

Use the existing installer closeout documents as read-only source material for controlled fixtures. Do not implement the Windows tasks, invoke native clients, or change real task completion state to evaluate these authoring skills. Capture fixture input and baseline skill versions so comparisons do not drift as the live plan changes.

Run baseline and revised skills against the same fixtures with the same available model, reasoning setting, tool access, and context boundary. Record actual settings. Follow the repository's canonical evaluation layout: one `iteration-N/eval-*/eval_metadata.json` with config-specific `run-*` directories underneath it. Keep generated results in a sibling `*-workspace/` directory. Never use an installed copy accidentally when testing a changed source skill.

Use a separate run with only the generated task, manifest constraints, prerequisite evidence, and explicitly required references. Ask the worker to explain the next authorized action, first verification step, completion condition, and stopping boundary without executing product work. Record every additional unlisted document needed. This reveals hidden context that JSON shape checks cannot detect.

The next section supplies the acceptance cases. Check semantic completeness first. Compare time, tokens, and tool calls only when actually measured. More task sessions can increase repeated setup and integration work; do not claim total reasoning savings from a larger task count.

## Concrete Steps


Before future implementation, read the repository's current instructions and applicable skill-authoring guidance. Confirm the intended source paths above still exist, inspect current changes, and preserve a baseline snapshot using the repository's skill benchmark convention. Do not overwrite unrelated work.

From the repository root, these existing commands support inspection and static verification:

    rtk git status --short
    rtk proxy rg -n 'tasks.json|userStories|parallelBatch|dependsOn|Typecheck passes' skills/spec-to-tasks skills/prd-ralph skills/prd-ralph-loop
    rtk proxy env PYTHONPATH=scripts/vendor python3 skills/skill-creator/scripts/quick_validate.py skills/spec-to-tasks
    rtk proxy env PYTHONPATH=scripts/vendor python3 skills/skill-creator/scripts/quick_validate.py .agents/skills/exec-plans
    rtk git diff --check

The validator commands use the repository's vendored YAML dependency. Do not install packages implicitly if validation cannot run. `quick_validate.py` checks skill structure/frontmatter; it does not prove task quality. Preserve any approved frontmatter keys even if a validator has a known limitation.

After changing evaluation definitions, parse `skills/spec-to-tasks/evals/evals.json` as JSON. If grader code changes, compile it with a disposable bytecode-cache location and run its targeted tests. The following compile command avoids writing cache files into the source tree:

    rtk proxy env PYTHONPYCACHEPREFIX=/private/tmp/exec-plan-tasks-pycache python3 -m py_compile skills/spec-to-tasks/evals/grade_benchmark.py

Use the equivalent disposable temporary directory on another operating system. Compilation checks syntax only and cannot establish behavioral correctness.

After real evaluation artifacts exist, run the existing grader with the actual new iteration directory. `iteration-N` below is a placeholder to replace, not an existing result:

    rtk proxy python3 skills/spec-to-tasks/evals/grade_benchmark.py skills/spec-to-tasks-workspace/iteration-N

Inspect each run's `grading.json`, including failed expectations and evidence. Do not treat the grader's process exit alone as acceptance. Validate generated `tasks.json` files for JSON syntax and the semantic rules below. No general-purpose task-schema validator has been established by this guide; extend the existing grader or add a narrowly scoped validator only if needed, and document its actual invocation after it exists.

At the end of implementation, run the required documentation maintenance pass once. Update canonical instructions/memory only for implemented durable changes and new verified gotchas. Apply their formatting rules if those files change. Do not document these proposals as existing behavior before implementation.

## Validation and Acceptance


Use the following fixtures and deliberate mutations. New fixture files are proposed additions under the relevant skill's `evals/` tree; no such new files are claimed to exist yet. If the repository-local ExecPlan skill needs a separate eval workspace, follow the repository-local skill boundary and existing benchmark conventions rather than moving the skill into publishable `skills/`.

| Case | Required result |
| --- | --- |
| Large lifecycle milestone, based on 6B | Produce bounded behavioral assignments, preserve the full lifecycle contract, and identify the final integration proof. Do not mandate exactly 12 tasks. |
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

If schema/consumer compatibility fails, keep the change unpublished until the producer and consumer agree. Do not discard new required fields silently or migrate active task records by overwriting completion evidence. If an evaluation result fails, preserve its artifact and diagnostic, make a focused correction, and rerun the affected case before broadening evaluation.

## Outcomes & Retrospective


The recommendations and verification design are captured. No skill, consumer, grader, installer source, live task record, or installed personal skill was changed by preparing this document. Future implementers should replace this paragraph with measured outcomes as improvement milestones complete.

Expected benefit is less repeated interpretation during worker execution. Hard technical reasoning and cross-task integration remain explicit responsibilities. Total project effort may include additional context loading, review, and integration, so efficiency claims require measured comparisons.

## Artifacts and Notes


This guide preserves all seven original recommendation groups: three for ExecPlans (assignment boundaries, current design extraction, integration proof) and four for task decomposition (sizing, structured dependencies/context/type, applicable verification, semantic validation). It also includes the shared fresh-worker evaluation method and the newly verified consumer/evaluation compatibility issues.

Current maintenance classification: this is a transient recommendation document, not a changed repository workflow or public API. Canonical documentation pass: Added: None; Changed: None; Split or moved: None; Deduplicated: None; Index updates: None; Remaining doc quality TODOs: None. Proposed skill/evaluation repairs remain tracked above rather than being represented as completed canonical changes.

Revision note, 2026-10-07: created at the user's requested scratchpad path with novice-oriented edit locations, proposed rule text, a schema example, compatibility work, commands, and observable acceptance. This records recommendations without starting their implementation.
