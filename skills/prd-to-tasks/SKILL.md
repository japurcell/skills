---
name: prd-to-tasks
description: Converts a PRD, feature spec, planning doc, or raw requirements into dependency-ordered atomic implementation stories in `prd.json`. Use when the user wants to split a feature into implementable tasks, user stories, `prd.json`, or `/prd-build-loop` input—even if they say "break this down," "make this implementable," "turn this spec into tickets," or "prepare agent-ready stories." Not for writing the PRD itself or implementing the feature.
---

# PRD to Tasks

## Overview

Convert `prd_file` into agent-ready `prd.json`. Split until each story is narrow, independently verifiable, dependency-ordered, and small enough for one implementation loop.

## When to Use

- Turn a PRD, spec, planning doc, or raw requirements into atomic implementation stories.
- Prepare `prd.json`, user stories, or agent-ready work items for `/prd-build-loop`.
- Decompose broad requirements into stageable backend, UI, data, and integration work.
- Not for PRD authoring (`prd`) or story implementation (`prd-build`, `prd-build-loop-review`).

## Workflow

1. Resolve inputs and output path.
   - `prd_file` is required: file path or raw PRD text.
   - `output_directory` is optional:
     - if provided, save `output_directory/prd.json`
     - else if `prd_file` is a path, save beside it
     - else save `.agents/scratchpad/prd.json`
2. Read the PRD and identify the smallest stageable capabilities.
3. Split broad requirements into atomic stories, then order by dependency and source order.
4. Write valid JSON only to `prd.json`.
5. Final response: story count, output path, and readiness for `/prd-build-loop`.

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
      "passes": false,
      "notes": ""
    }
  ]
}
```

### Atomic story rules

- Each story must be narrow, complete, independently verifiable, and finishable by one agent in one iteration.
- A story usually covers one stageable capability, such as:
  - schema or migration
  - shared model or type
  - backend action, endpoint, service, or query
  - one UI surface
  - one user interaction
  - one integration point
  - one dashboard or aggregate view
  - one focused testable behavior
- If a source requirement is already atomic and implementation-sized, keep it as one story. Otherwise split it. Never copy broad PRD sections unchanged.
- Never create stories that mean:
  - implement whole feature, page, epic, or workflow
  - combine unrelated stageable behaviors
  - split only by technical layer when user-visible capabilities can be staged

### Split rules

Split any requirement that:

- spans multiple features, pages, flows, roles, entities, or surfaces
- uses multiple unrelated verbs like create, edit, delete, filter, export, or notify
- combines schema, backend, and UI work that can be staged
- cannot be explained in 2-3 sentences
- would touch many unrelated files
- is not demoable after its prerequisites
- joins separate capabilities with `and`

Avoid horizontal stories like `build backend`, `build frontend`, or `write all tests` unless the PRD only asks for that layer.

### Decomposition sequence

For each requirement:

1. Find smallest user-visible or system-visible capability.
2. Create prerequisite stories first: schema/database, then shared types/models, then backend logic.
3. Split UI by surface when needed: list, detail, form, modal, navigation, dashboard.
4. Split user actions when needed: create, update, delete, filter, sort, search, export, notify.
5. Re-split any draft story that still bundles multiple capabilities.

For weaker models, apply this exact rule:

- If one requirement includes both backend persistence and a visible UI surface, split them into separate stories.
- Backend-only stories should describe storage, types, actions, endpoints, validation, or persistence; do not describe visible cards, rows, lists, controls, filters, or other UI surfaces there.
- Backend-only stories also must not describe where a user clicks, which page triggers the action, or task-list/card/row behavior. Leave those details to separate UI stories.
- Any story that describes a visible UI surface must include browser verification.

### Ordering rules

- `priority` ascends; no story may depend on a later story.
- Preferred order:
  1. schema/database
  2. shared types/models
  3. backend/server logic
  4. UI using that logic
  5. aggregate/dashboard views
  6. polish, validation, follow-up enhancements
- Preserve PRD source order when dependencies allow.

### Acceptance criteria rules

- Criteria must be concrete and testable.
- Every story includes `Typecheck passes`.
- Add `Tests pass` for testable logic when applicable.
- Add `Verify in browser using playwright-cli skill` for every story that changes visible UI.
- Treat badges, cards, rows, lists, filters, forms, dropdowns, modals, pages, and controls as UI even when the same story also wires backend behavior.
- If a draft story mentions both backend work and any visible UI surface, split it before saving instead of keeping one mixed story.
- UI stories are incomplete without browser verification.

Good:

- `Add status column to tasks table with default 'pending'`
- `Filter dropdown options are All, Active, and Completed`
- `Changing status saves immediately`
- `Clicking delete shows a confirmation dialog`

Bad:

- `Works correctly`
- `Good UX`
- `Handles edge cases`
- `Implement the feature`

### Field rules

- Use sequential IDs: `US-001`, `US-002`, ...
- Derive `branchName` from the feature name in kebab-case.
- Keep top-level `description` short and based on the PRD title or intro.
- Set every story `passes` to `false`.
- Set every story `notes` to `""`.
- Include `filesLikelyTouched` when inferable.
- Exclude files ignored by repository `.gitignore`.
- Use `designGuidance` only when useful; otherwise `[]`.
- Save valid JSON only: no markdown, comments, or trailing commas.

### Minimal example

Input:

```markdown
Add task statuses. Users can set a task to pending, in progress, or done, see badges, and filter the task list by status.
```

Correct split:

1. Add task status schema or migration.
2. Add backend action to update task status.
3. Show status badge on task cards.
4. Add status control to task rows.
5. Add status filter to task list.

Incorrect:

1. Implement task statuses.

## Common Rationalizations

| Rationalization | Reality |
| --- | --- |
| "PRD already has sections, so I can reuse them as stories." | Only reuse wording when a requirement is already atomic and implementation-sized. Broad sections must be split. |
| "One story for backend and one for frontend is enough." | Horizontal layer splits hide stageable capabilities and block dependency ordering. |
| "Acceptance criteria can stay vague because implementer will figure it out." | Criteria must be concrete so stories are independently verifiable. |
| "This story is mostly backend, so inline UI control does not need browser verification." | If the story changes any visible control or other UI surface, include `Verify in browser using playwright-cli skill`. |
| "I can keep backend update logic in one story that also describes task-list behavior." | No. Split backend persistence/action work from visible list, row, card, filter, or control work before saving. |
| "Backend story can still say users change status from the list as long as UI is separate." | No. Pure backend stories should avoid UI entry-point wording entirely; keep list, row, card, page, and control language in UI stories only. |

## Red Flags

- Story titles read like epics, phases, or full workflows.
- One story contains multiple unrelated verbs or multiple UI surfaces.
- A later-priority story is prerequisite for an earlier one.
- Acceptance criteria use vague language.
- UI stories omit browser verification.
- Output is markdown or commented JSON instead of valid `prd.json`.

## Verification

Before saving, confirm:

- [ ] Broad requirements were split into implementation-sized stories.
- [ ] Any unchanged source requirement was already atomic.
- [ ] Each story is narrow, independently verifiable, and dependency-ordered.
- [ ] No story depends on a later-priority story.
- [ ] Every story has concrete acceptance criteria.
- [ ] Every story includes `Typecheck passes`.
- [ ] Every UI story includes `Verify in browser using playwright-cli skill`.
- [ ] Mixed UI/backend stories still include browser verification when they change visible UI.
- [ ] Backend-only stories do not describe visible UI surfaces.
- [ ] Backend-only stories do not describe UI entry points like list, row, card, page, or control interactions.
- [ ] `filesLikelyTouched` excludes ignored files.
- [ ] `prd.json` is valid and saved to the correct path.
