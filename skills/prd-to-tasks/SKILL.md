---
name: prd-to-tasks
description: Use when the user asks to convert, decompose, split, or transform a PRD, product requirements document, feature spec, planning doc, markdown file, or raw requirements into implementation tasks, user stories, `userStories`, JSON, `prd.json`, or input for `/prd-build-loop`. Trigger on phrases such as "convert this PRD into tasks", "create prd.json", "turn this into JSON", "break this PRD into stories", "generate userStories", "split this into tasks", "decompose this feature", "make implementation stories", "prepare for /prd-build-loop", "tasks from requirements", or "convert requirements to stories". Always split broad PRD requirements into small implementation-sized stories; never copy PRD sections or stories unchanged unless they already satisfy the atomic story rules.
---

# PRD to `prd.json`

Convert `prd_file` into a decomposed `prd.json` for the autonomous agent system.

## Inputs

- `prd_file` required: PRD file path or raw PRD text.
- `output_directory` optional:
  - If set, save to `output_directory/prd.json`.
  - Else if `prd_file` is a path, save next to it.
  - Else save to `.agents/scratchpad/prd.json`.

## Required workflow

1. Read `prd_file`.
2. Decompose every broad requirement into atomic implementation stories.
3. Order stories by dependency, then PRD source order.
4. Write valid JSON to the target `prd.json` path.
5. Final response must include:
   - total story count
   - output file path
   - readiness for `/prd-build-loop`

## Output JSON schema

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

## Atomic story requirement

`userStories` must contain decomposed implementation stories, not copied PRD sections.

Each story must be a narrow, complete, verifiable change that one agent can finish in one iteration.

A story should usually cover only one of these:

- one schema or migration change
- one model or type update
- one backend action, endpoint, service, or query
- one UI component or UI surface
- one user interaction
- one filter, sort, search, badge, toggle, modal, or form
- one integration point
- one dashboard or aggregate view
- one focused testable behavior

Never create a story that means:

- implement the whole PRD
- build the whole feature
- add the whole system
- complete an epic
- implement a full page with many behaviors
- implement a full workflow end-to-end when it can be staged
- copy a PRD story unchanged when it contains multiple capabilities

Split smaller when unsure.

## Split rules

Split a requirement or story if it:

- includes multiple features, pages, flows, roles, entities, or UI surfaces
- has multiple unrelated verbs, such as create, edit, delete, filter, export, or notify
- combines schema, backend, and UI work that can be staged
- cannot be explained in 2–3 sentences
- would touch many unrelated files
- is not independently demoable after earlier prerequisites are complete
- contains “and” between separate capabilities

Avoid horizontal stories such as “build backend,” “build frontend,” or “write all tests” unless the PRD only asks for that layer.

## Decomposition algorithm

For each PRD requirement:

1. Identify the smallest user-visible or system-visible capability.
2. Split prerequisites first:
   - database/schema
   - models/types
   - server actions/API/service/query
3. Split each UI surface separately:
   - list view
   - detail view
   - form
   - modal
   - navigation
   - dashboard
4. Split each user action separately:
   - create
   - update
   - delete
   - filter
   - sort
   - search
   - export
   - notify
5. Split cross-cutting requirements only when independently implementable.
6. If a generated story still contains multiple capabilities, split it again.

## Ordering rules

Stories run in ascending `priority`. No story may depend on a later story.

Order by dependency first:

1. schema/database changes
2. shared types/models
3. backend/server logic
4. UI that uses that logic
5. aggregate/dashboard views
6. polish, validation, and follow-up enhancements

Then preserve PRD source order where dependencies allow.

## Acceptance criteria rules

Acceptance criteria must be concrete and testable.

Always include:

- `Typecheck passes`

Include when applicable:

- `Tests pass` for testable logic
- `Verify in browser using playwright-cli skill` for UI changes

Good criteria:

- `Add status column to tasks table with default 'pending'`
- `Filter dropdown options are All, Active, and Completed`
- `Changing status saves immediately`
- `Clicking delete shows a confirmation dialog`
- `Typecheck passes`

Bad criteria:

- `Works correctly`
- `Good UX`
- `Handles edge cases`
- `Implement the feature`

UI stories are incomplete unless they include visual/browser verification.

## Field rules

- Use sequential IDs: `US-001`, `US-002`, etc.
- Derive `branchName` from the feature name in kebab-case.
- Keep top-level `description` short and based on the PRD title or intro.
- Set every story to `"passes": false`.
- Set every story to `"notes": ""`.
- Include `filesLikelyTouched` when inferable.
- Do not include files excluded by repository `.gitignore`.
- Use `designGuidance` only when useful; otherwise set it to `[]`.
- Output must be valid JSON with no comments or trailing commas.

## Minimal example

Input requirement:

```markdown
Add task statuses. Users can set a task to pending, in progress, or done, see badges, and filter the task list by status.
```

Correct split:

1. Add task status schema/migration.
2. Add backend action to update task status.
3. Show status badge on task cards.
4. Add status control to task rows.
5. Add status filter to task list.

Incorrect:

1. Implement task statuses.

## Final check before saving

Verify all are true:

- [ ] The PRD is decomposed into small implementation stories.
- [ ] No story is just copied from the original PRD.
- [ ] Each story is narrow, independently verifiable, and implementation-sized.
- [ ] No story depends on a later-priority story.
- [ ] Every story has concrete acceptance criteria.
- [ ] Every story includes `Typecheck passes`.
- [ ] Every UI story includes `Verify in browser using playwright-cli skill`.
- [ ] `filesLikelyTouched` excludes ignored files.
- [ ] JSON is valid and saved to the correct `prd.json` path.

If any story fails this check, split or revise it before saving.
