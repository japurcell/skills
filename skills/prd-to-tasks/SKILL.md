---
name: prd-to-tasks
description: Converts PRDs, feature specs, planning docs, or raw requirements into dependency-ordered, parallel-ready implementation stories in `prd.json`. Use whenever a user wants tickets, backlog items, agent-ready work, `/prd-build-loop` input, or asks how to split a feature so multiple agents can implement it safely in parallel—even if they do not mention `prd.json`. Not for writing the PRD itself or implementing the stories.
disable-model-invocation: true
---

# PRD to Tasks

## Overview

Convert `prd_file` into agent-ready `prd.json`. Split until each story is implementation-sized, independently verifiable, and arranged for the shortest safe dependency chain.

## When to Use

- Turn a PRD, feature spec, planning doc, or raw requirements into atomic implementation stories.
- Prepare `prd.json`, backlog items, or `/prd-build-loop` input.
- Make safe parallel work explicit for multiple agents.
- Not for PRD authoring (`prd`) or story implementation (`prd-build`).

## Workflow

1. Resolve inputs and output path.
   - `prd_file` is required: path or raw PRD text.
   - `output_directory` is optional:
     - if provided, save `output_directory/prd.json`
     - else if `prd_file` is a path, save beside it
     - else save `.agents/scratchpad/prd.json`
2. Read the PRD and extract the smallest stageable capabilities plus shared prerequisites.
3. Split into atomic stories, give each minimal `dependsOn`, then assign the earliest safe `parallelBatch`.
4. Assign unique ascending `priority` values that stay compatible with serial consumers.
5. Save valid JSON only to `prd.json`. Final response: story count, output path, readiness for `/prd-build-loop`.

## Specific Techniques

### Output schema

```json
{
  "project": "[Project Name]",
  "branchName": "[feature-name-kebab-case]",
  "description": "[Short feature description]",
  "userStories": [
    {
      "id": "US-001",
      "title": "[Small implementation story title]",
      "description": "As a [user], I want [single capability] so that [benefit].",
      "acceptanceCriteria": ["Concrete criterion", "Typecheck passes"],
      "filesLikelyTouched": ["src/path/to/file.ts"],
      "designGuidance": [
        {
          "source": "[doc link, repo pattern, design decision, etc.]",
          "description": "[Guidance]",
          "rationale": "[Why it matters]"
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

### Parallel-first split rules

- Each story must be narrow, complete, independently verifiable, and finishable by one agent in one iteration.
- Pull shared prerequisites into their own stories first, then fan out dependent work.
- Good story shapes: one schema or migration, one shared type or model, one backend action/endpoint/service/query, one UI surface, one user interaction, one integration point, one dashboard or aggregate view, one focused testable behavior.
- Split any requirement that spans multiple features, pages, flows, roles, entities, surfaces, or unrelated verbs.
- Split backend persistence from visible UI whenever the UI can wait on a completed backend story.
- Avoid horizontal stories like `build backend`, `build frontend`, `write all tests`, or `implement the feature`.
- Do not keep broad PRD sections unchanged unless they are already implementation-sized.

### Parallel safety rules

- `dependsOn` lists only direct prerequisite story IDs. Use `[]` when none.
- `parallelBatch` means the story can start in the same wave as other stories with that batch after all `dependsOn` stories finish.
- Give each story the earliest possible `parallelBatch`.
- Only place stories in the same `parallelBatch` when they are both dependency-independent and unlikely to conflict in the same files or owner surface.
- Treat the same migration, endpoint, shared state owner, form/table/page owner, or likely-touched file as a conflict signal; move one story later.
- Keep `priority` unique and ascending for current serial consumers. Earlier batches must always have lower priorities than later batches. Within a batch, preserve dependency order, then PRD source order.
- Optimize for the shortest safe critical path: extract common prerequisites once, then maximize conflict-free fan-out.

### Acceptance and field rules

- Acceptance criteria must be concrete and testable.
- Every story includes `Typecheck passes`.
- Add `Tests pass` for testable logic when applicable.
- Add `Verify in browser using playwright-cli skill` for every story that changes visible UI.
- If a draft story mixes backend work with a visible UI surface, split it unless the UI truly cannot be staged separately.
- Backend-only stories should avoid page, list, row, card, button, modal, or browser wording.
- Use sequential IDs: `US-001`, `US-002`, ...
- Derive `branchName` from the feature name in kebab-case.
- Keep top-level `description` short and based on the PRD title or intro.
- Set every story `passes` to `false` and `notes` to `""`.
- Include `filesLikelyTouched` when inferable and exclude `.gitignore`d files.
- Use `designGuidance` only when useful; otherwise `[]`.
- Save valid JSON only: no markdown, comments, or trailing commas.

### Minimal example

Input:

```markdown
Add task statuses. Users can set a task to pending, in progress, or done, see badges, and filter the task list by status.
```

Good split:

1. Add task status storage.
2. Add shared task status type or validation.
3. Add backend status update logic.
4. Show status badges.
5. Add status control.
6. Add status filter.

A strong output keeps 1-3 on the prerequisite path, then assigns 4-6 to the earliest safe `parallelBatch` values allowed by dependencies and likely file overlap.

Bad split:

1. Implement task statuses.

## Common Rationalizations

| Rationalization                                                       | Reality                                                                                                                              |
| --------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| "PRD already has sections, so I can reuse them as stories."           | Reuse wording only when the requirement is already implementation-sized. Broad sections must be split.                               |
| "One backend story and one frontend story is parallel enough."        | Horizontal layer splits hide stageable capabilities and block safe fan-out.                                                          |
| "Same batch is fine if the stories are logically independent."        | If they likely edit the same page, table, endpoint, migration, or owner file, they will still conflict.                              |
| "Priority alone is enough."                                           | Serial order hides concurrency. `dependsOn` and `parallelBatch` make safe parallel work explicit without breaking current consumers. |
| "This story is mostly backend, so UI verification can stay implicit." | Any visible UI change needs its own UI story or explicit browser verification.                                                       |

## Red Flags

- Story titles read like epics, phases, or full workflows.
- One story contains multiple unrelated verbs or multiple UI surfaces.
- `dependsOn` points to a later or missing story.
- Multiple stories share a `parallelBatch` while likely touching the same owner surface or file.
- `priority` order disagrees with dependency or batch order.
- Backend-only stories describe clicks, pages, rows, cards, or browser checks.
- Output is markdown or commented JSON instead of valid `prd.json`.

## Verification

Before saving, confirm:

- [ ] Broad requirements were split into implementation-sized stories.
- [ ] Each story is narrow, independently verifiable, and small enough for one agent loop.
- [ ] `dependsOn` is minimal and points only to earlier direct prerequisites.
- [ ] `parallelBatch` is the earliest safe batch for each story.
- [ ] Independent work shares a `parallelBatch` when the PRD allows it.
- [ ] Stories in the same `parallelBatch` are unlikely to conflict in likely-touched files or owner surfaces.
- [ ] `priority` is unique, ascending, and grouped by batch order.
- [ ] Every story has concrete acceptance criteria and includes `Typecheck passes`.
- [ ] Every UI story includes `Verify in browser using playwright-cli skill`.
- [ ] Backend-only stories avoid visible UI wording.
- [ ] `filesLikelyTouched` excludes ignored files.
- [ ] `prd.json` is valid and saved to the correct path.
