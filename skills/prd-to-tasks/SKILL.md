---
name: prd-to-tasks
description: Convert PRDs, feature specs, planning docs, or raw requirements into dependency-ordered, parallel-ready implementation tasks in `prd.json`. Use for tickets, backlog items, agent-ready work, `/prd-build-loop` input, or splitting a feature for safe parallel implementation, even if the user does not mention `prd.json`. Do not use to write the PRD or implement tasks.
disable-model-invocation: true
---

# /prd-to-tasks

Convert `prd_file` into agent-ready `prd.json`: small, verifiable implementation tasks with minimal dependencies and maximum safe parallelism.

## Inputs and output

- Required: `prd_file` path or raw PRD text.
- Optional: `output_directory`.
- Save to:
  - `output_directory/prd.json` if provided.
  - Beside `prd_file` if `prd_file` is a path.
  - `.agents/scratchpad/prd.json` if input is raw text.
- Create the output directory if needed.

## Workflow

1. Resolve `prd_file`, output path, and create the output directory if needed.
2. Read the PRD and identify project, feature, user stories, requirements, edge cases, and shared prerequisites.
3. If repo context is needed and missing, run `/explore` first. Look for prefactors that make the change easier.
4. Scan relevant workspace instructions and conventions when available, such as `AGENTS.md`, scoped agent docs, repo docs, package scripts, test setup, and existing patterns.
5. If the PRD conflicts with workspace rules or established architecture, resolve the conflict before task splitting. Document the resolution in task descriptions or `designGuidance`; ask the user if unclear.
6. Split broad requirements into atomic implementation tasks.
7. Pull shared prerequisites first, then fan out dependent tasks.
8. Assign only direct `dependsOn` prerequisites and the earliest safe `parallelBatch`.
9. Assign unique ascending `priority`; earlier batches must have lower priorities.
10. Verify every functional requirement and edge case maps to at least one task or acceptance criterion.
11. Validate IDs, dependencies, batches, priorities, traceability, and JSON syntax.
12. Save valid JSON only to `prd.json`.
13. Final chat response: task count, output path, readiness for `/prd-build-loop`.

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
      "description": "What to implement, how to verify it, and relevant context.",
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

## Task rules

- Each task must be narrow, complete, independently verifiable, and implementable by one agent without extra context.
- Organize tasks by user story using `parentStoryId`.
- If the PRD has no explicit user stories, synthesize stable `parentStoryId` values such as `US-001` from coherent requirement groups.
- Good task shapes: one migration, one model/type, one service/query, one endpoint/action, one UI surface, one integration point, one focused testable behavior.
- Split requirements spanning multiple features, pages, flows, roles, entities, surfaces, or unrelated verbs.
- Split backend persistence from visible UI unless they cannot be staged separately.
- Avoid horizontal tasks like “build backend,” “build frontend,” “write all tests,” or “implement feature.”
- Do not reuse PRD sections as tasks unless already implementation-sized.
- Use sequential IDs: `T001`, `T002`, ...
- Set every task `passes` to `false` and `notes` to `""`.
- Include `filesLikelyTouched` when inferable; otherwise `[]`. Exclude ignored/generated files.
- Use `designGuidance` only when useful; otherwise `[]`.
- Derive `branchName` from the feature name in kebab-case.
- Keep the top-level `description` short.

## Dependency and parallelism rules

- `dependsOn` lists only direct prerequisite task IDs, all earlier than the task.
- Use `[]` when there are no prerequisites.
- Encode PRD rollout, migration, or causal implementation order in `dependsOn`.
- Downstream behavior must depend on upstream enablers such as schemas, migrations, parsers, shared utilities, feature flags, or API contracts.
- Do not add dependencies merely because of PRD document order; preserve parallelism when tasks are causally independent.
- `parallelBatch` means all tasks in that batch can start after their dependencies finish.
- Give each task the earliest safe `parallelBatch`.
- Same-batch tasks must be dependency-independent and unlikely to edit the same file, script, migration, generated artifact, shared owner file, or tightly coupled surface.
- Treat the same endpoint, shared state owner, page, form, table, or likely file as a conflict; move one task later.
- Optimize for the shortest safe critical path: common prerequisites first, then conflict-free fan-out.
- `priority` must be unique, ascending, and grouped by batch order. Within a batch, preserve dependency order, then PRD order.

## Acceptance and verification rules

- Acceptance criteria must be concrete and testable.
- Every task includes `Typecheck passes`.
- Prefer exact repo commands or scripts when inferable, such as `npm test`, `pnpm typecheck`, `pytest path/to/test.py`, or `./scripts/verify-hooks.test.sh`.
- Add the concrete typecheck command when known.
- Add `Tests pass` only with the specific relevant test command or suite when inferable.
- Do not invent commands, files, or conventions.
- Do not use broad placeholders as the only validation for complex behavior.
- If verification commands are not inferable, say so in the task description and keep acceptance criteria behavior-focused.
- Add `Verify in browser using playwright-cli skill` for every visible UI change.
- Backend-only tasks must avoid UI/browser wording such as page, click, row, card, button, modal, or browser.

## Traceability and edge-case coverage

- Map every explicit functional requirement, labeled requirement, edge case, fallback, and negative state in the PRD to at least one task or acceptance criterion.
- If the PRD uses IDs like `FR-1`, include those IDs in task descriptions or acceptance criteria.
- Requirements involving fallback logic, missing dependencies, lock/timeouts, permissions, read-only filesystems, invalid input, retries, caching, or partial failure must include automated regression test work or explicit acceptance criteria covering those paths.
- Do not leave functional requirements or edge cases unmapped.

## Red flags to fix before saving

- Epic/phase/workflow-sized task.
- Multiple unrelated verbs or UI surfaces in one task.
- Missing, later, duplicate, or cyclic dependency.
- Same-batch tasks likely touch the same file or owner surface.
- `priority` conflicts with dependency or batch order.
- Backend-only task describes UI behavior.
- Output file is markdown, commented JSON, or invalid JSON.
- PRD/workspace conflict is unresolved.
- Requirement has no mapped task or acceptance criterion.

## Final verification

Before saving, confirm:

- [ ] Broad requirements were split into implementation-sized tasks.
- [ ] Each task is narrow, independently verifiable, and agent-ready.
- [ ] Dependencies are minimal, direct, earlier, and acyclic.
- [ ] `parallelBatch` is earliest safe for each task.
- [ ] Conflict-free independent work shares a batch.
- [ ] Priorities are unique, ascending, and batch-ordered.
- [ ] Every task has concrete acceptance criteria and `Typecheck passes`.
- [ ] UI tasks include browser verification.
- [ ] Workspace instructions and repo conventions were checked when available.
- [ ] PRD/workspace conflicts were resolved, documented, or escalated to the user before task generation.
- [ ] Every functional requirement and edge case maps to at least one task or acceptance criterion.
- [ ] Acceptance criteria use concrete commands/scripts when inferable and do not rely only on vague placeholders.
- [ ] `prd.json` is valid JSON and saved to the correct path.
