---
name: prd-to-tasks
description: Convert PRDs, feature specs, planning docs, or raw requirements into dependency-ordered, parallel-ready implementation tasks in `prd.json`. Use for tickets, backlog items, agent-ready work, `/prd-build-loop` input, or splitting a feature for safe parallel implementation. Do not use to write the PRD or implement tasks.
disable-model-invocation: true
---

# /prd-to-tasks

Convert `prd_file` into agent-ready `prd.json`: small, verifiable implementation tasks with minimal dependencies and maximum safe parallelism.

## Inputs and output

- Required: `prd_file` path or raw PRD text.
- Optional: `output_directory`.
- Save to:
  - `output_directory/prd.json` if provided.
  - beside `prd_file` if `prd_file` is a path.
  - `.agents/scratchpad/prd.json` if input is raw text.
- Create the output directory if needed.

## Workflow

1. Resolve `prd_file`, output path, and create the output directory if needed.
2. Read the PRD; identify project, feature, stories, requirements, edge cases, rollout order, and shared prerequisites.
3. If repo context is needed and missing, run `/explore`; look for prefactors that make the change easier.
4. Scan relevant workspace rules when available: `AGENTS.md`, scoped docs, repo docs, package scripts, tests, and existing patterns.
5. Check and resolve PRD/workspace inconsistencies before task splitting. Prefer the most specific implementation-nearest source: rollout/migration order, acceptance criteria/Definition of Done, technical decisions, functional requirements, then narrative. Document resolutions in task descriptions or `designGuidance`; ask the user if unclear.
6. Split broad requirements into atomic tasks; pull shared prerequisites first, then fan out dependent tasks.
7. Assign direct `dependsOn`, earliest safe `parallelBatch`, and unique ascending `priority`.
8. Verify every requirement and edge case maps to at least one task or acceptance criterion.
9. Validate IDs, dependencies, batches, priorities, files, traceability, and JSON syntax.
10. Save valid JSON only to `prd.json`.
11. Final chat response: task count, output path, readiness for `/prd-build-loop`.

## Required JSON shape

```json
{
  "project": "Project Name",
  "branchName": "feature-name-kebab-case",
  "description": "Short feature description",
  "tasks": [
    {
      "id": "T001",
      "parentStoryId": "US-001",
      "title": "Small implementation task title",
      "description": "What to implement, how to verify it, relevant context, and mapped requirement IDs when available.",
      "acceptanceCriteria": ["Concrete, testable behavior", "Typecheck passes"],
      "filesLikelyTouched": ["src/path/file.ts"],
      "designGuidance": [
        {
          "source": "doc, pattern, or decision",
          "description": "Guidance",
          "rationale": "Why it matters"
        }
      ],
      "priority": 1,
      "dependsOn": [],
      "parallelBatch": 1,
      "passes": false,
      "notes": ""
    }
  ]
}
```

## PRD section handling

- For `/prd`-style PRDs, treat Functional Requirements, Technical Decisions, Definition of Done, Execution Sequence, Testing Plan, and Out of Scope as canonical.
- Do not create tasks for Out of Scope items.
- Preserve `US-*` and `FR-*` IDs in task descriptions or acceptance criteria.
- Mandatory execution order affects task array order, `dependsOn`, and `parallelBatch`; recommended order affects `priority` only when safe.
- Use relevant Definition of Done and Testing Plan items to seed acceptance criteria, commands, and test seams without copying irrelevant criteria into every task.
- Assume canonical definitions are intentional unless they conflict with workspace rules or are internally inconsistent.

## Task rules

- Each task must be narrow, complete, independently verifiable, and implementable by one agent without extra context.
- Organize by user story using `parentStoryId`; if no stories exist, synthesize stable IDs like `US-001` from coherent requirement groups.
- Good task shapes: one migration, model/type, service/query, endpoint/action, UI surface, integration point, or focused testable behavior.
- Split requirements spanning multiple features, pages, flows, roles, entities, surfaces, or unrelated verbs.
- Split backend persistence from visible UI unless they cannot be staged separately.
- Avoid horizontal tasks like “build backend,” “build frontend,” “write all tests,” or “implement feature.”
- Do not reuse PRD sections as tasks unless already implementation-sized.
- Use sequential task IDs: `T001`, `T002`, ...
- Set every task `passes` to `false` and `notes` to `""`.
- Use `designGuidance` only when useful; otherwise `[]`.
- Derive `branchName` from the feature name in kebab-case.
- Keep top-level `description` short.

## File inference rules

- Include `filesLikelyTouched` when inferable; otherwise `[]`.
- Exclude ignored/generated files.
- Include every inferable source, config, migration, fixture, script, and test file the task will create or edit.
- If acceptance criteria name a test file, script, fixture, or command target, include that path.
- If a task adds or updates tests, list the specific test files when inferable.

## Dependency and parallelism rules

- `dependsOn` lists only direct prerequisite task IDs, all earlier than the task; use `[]` when none.
- Encode causal order in `dependsOn`: schemas, migrations, parsers, shared utilities, feature flags, API contracts, and upstream behavior before downstream behavior.
- Do not move cleanup, verification, removal, or downstream tasks earlier than stated prerequisites unless explicitly independent.
- Do not add dependencies merely because of PRD document order; preserve parallelism when tasks are causally independent.
- `parallelBatch` means all tasks in that batch can start after their dependencies finish.
- Give each task the earliest safe `parallelBatch`.
- Same-batch tasks must be dependency-independent and unlikely to edit the same file, script, migration, generated artifact, shared owner file, page, form, table, endpoint, or tightly coupled surface.
- Optimize for the shortest safe critical path: common prerequisites first, then conflict-free fan-out.
- `priority` must be unique, ascending, and grouped by batch order. Within a batch, preserve dependency order, then PRD order.

## Acceptance and verification rules

- Acceptance criteria must be concrete and testable.
- Every task includes `Typecheck passes`.
- Prefer exact repo commands/scripts when inferable, especially from the PRD Testing Plan, such as `npm test`, `pnpm typecheck`, `pytest path/to/test.py`, or `./scripts/verify-hooks.test.sh`.
- Add the concrete typecheck command when known.
- Add `Tests pass` only with the specific relevant test command or suite when inferable.
- Do not invent commands, files, paths, or conventions.
- Do not use broad placeholders as the only validation for complex behavior.
- If verification commands are not inferable, say so in the task description and keep acceptance criteria behavior-focused.
- Add `Verify in browser using playwright-cli skill` for every visible UI change.
- Backend-only tasks must avoid UI/browser wording such as page, click, row, card, button, modal, or browser.

## Traceability and edge cases

- Map every explicit functional requirement, labeled requirement, edge case, fallback, and negative state to at least one task or acceptance criterion.
- If the PRD uses IDs like `FR-1`, include those IDs in task descriptions or acceptance criteria.
- Requirements involving fallback logic, missing dependencies, lock/timeouts, permissions, read-only filesystems, invalid input, retries, caching, or partial failure must include automated regression test work or explicit acceptance criteria.

## Validate before saving

Confirm:

- [ ] Tasks are implementation-sized, agent-ready, and not epic/phase/workflow-sized.
- [ ] No task has multiple unrelated verbs or unrelated UI surfaces.
- [ ] All requirements and edge cases are mapped.
- [ ] Out of Scope items were not converted into tasks.
- [ ] PRD/workspace conflicts and internal PRD inconsistencies are resolved, documented, or escalated.
- [ ] IDs are sequential and unique.
- [ ] Dependencies are direct, earlier, minimal, and acyclic.
- [ ] Mandatory order is encoded in dependencies/batches; recommended order does not create unnecessary dependencies.
- [ ] Same-batch tasks are conflict-free.
- [ ] Priorities are unique, ascending, and batch-ordered.
- [ ] Acceptance criteria are concrete, include `Typecheck passes`, and use exact commands when known.
- [ ] UI tasks include browser verification.
- [ ] Backend-only tasks avoid UI wording.
- [ ] `filesLikelyTouched` includes named tests, scripts, fixtures, configs, migrations, and command targets when inferable.
- [ ] `prd.json` is valid JSON only: no markdown, comments, or trailing commas.
