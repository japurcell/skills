---
name: prd-to-tasks
description: Convert an existing PRD into prd.json for the autonomous agent system. Use for requests like - convert this PRD, turn this into JSON, create prd.json from this.
---

# PRD Converter

Convert a PRD (markdown file or text) into `prd.json`.

## Inputs

- `prd_file` (required): PRD markdown file path or raw text.
- `output_directory` (optional): Directory to save `prd.json`.
  - If `prd_file` is a file path and `output_directory` is not provided, save `prd.json` next to the source file.
  - Otherwise default to `.agents/scratchpad`.

## Task

Read `prd_file` and produce `prd.json`.

## Output

```json
{
  "project": "[Project Name]",
  "branchName": "[feature-name-kebab-case]",
  "description": "[Feature description from PRD title/intro]",
  "userStories": [
    {
      "id": "US-001",
      "title": "[Story title]",
      "description": "As a [user], I want [feature] so that [benefit]",
      "acceptanceCriteria": ["Criterion 1", "Criterion 2", "Typecheck passes"],
      "filesLikelyTouched": ["src/path/to/file.ts", "tests/path/to/test.ts"],
      "priority": 1,
      "passes": false,
      "notes": ""
    }
  ]
}
```

## Core Rules

### 1) Story size

Each story must be completable in one iteration by one agent with no memory of prior work.

Split stories that are too large.

Good:

- Add a database column and migration
- Add a UI component to an existing page
- Update a server action
- Add a filter dropdown

Too big:

- Build the entire dashboard
- Add authentication
- Refactor the API

Rule of thumb: if the change cannot be described in 2–3 sentences, split it.

### 2) Story ordering

Stories run in priority order. Earlier stories must not depend on later ones.

Use this order when applicable:

1. Schema/database changes
2. Backend/server logic
3. UI components using that logic
4. Aggregated/dashboard views

### 3) Acceptance criteria

Criteria must be specific and verifiable.

Good:

- Add `status` column to tasks table with default `pending`
- Filter dropdown has options: All, Active, Completed
- Clicking delete shows confirmation dialog
- Typecheck passes
- Tests pass

Bad:

- Works correctly
- Good UX
- Handles edge cases

Always include:

- `Typecheck passes`

Also include when applicable:

- `Tests pass` for testable logic
- `Verify in browser using playwright-cli skill` for UI changes

UI stories are not complete until visually verified.

## Conversion Rules

1. Create one JSON story per implementation-sized unit of work, not necessarily one per PRD bullet.
2. Split large PRD items into multiple stories when needed.
3. Use sequential IDs: `US-001`, `US-002`, etc.
4. Set priority by dependency order, then source order.
5. Set every story to `"passes": false` and `"notes": ""`.
6. Derive `branchName` from the feature name in kebab-case.
7. Keep acceptance criteria verifiable.
8. Add `Typecheck passes` to every story.
9. Add `Tests pass` and browser verification only when applicable.

## Splitting Example

Original:

- Add user notification system

Split into:

1. Add notifications table
2. Create notification service
3. Add notification bell icon
4. Create notification dropdown
5. Add mark-as-read action
6. Add notification preferences page

## Example

Input PRD:

```markdown
# Task Status Feature

Add ability to mark tasks with different statuses.

## Requirements

- Toggle between pending/in-progress/done on task list
- Filter list by status
- Show status badge on each task
- Persist status in database
```

Output:

```json
{
  "project": "TaskApp",
  "branchName": "task-status",
  "description": "Task Status Feature - Track task progress with status indicators",
  "userStories": [
    {
      "id": "US-001",
      "title": "Add status field to tasks table",
      "description": "As a developer, I need to store task status in the database.",
      "acceptanceCriteria": [
        "Add status column: 'pending' | 'in_progress' | 'done' (default 'pending')",
        "Generate and run migration successfully",
        "Typecheck passes"
      ],
      "filesLikelyTouched": ["src/db/migrations/add-status-to-tasks.ts"],
      "priority": 1,
      "passes": false,
      "notes": ""
    },
    {
      "id": "US-002",
      "title": "Display status badge on task cards",
      "description": "As a user, I want to see task status at a glance.",
      "acceptanceCriteria": [
        "Each task card shows colored status badge",
        "Badge colors: gray=pending, blue=in_progress, green=done",
        "Typecheck passes",
        "Verify in browser using playwright-cli skill"
      ],
      "filesLikelyTouched": ["src/components/TaskCard.tsx"],
      "priority": 2,
      "passes": false,
      "notes": ""
    },
    {
      "id": "US-003",
      "title": "Add status toggle to task list rows",
      "description": "As a user, I want to change task status directly from the list.",
      "acceptanceCriteria": [
        "Each row has status dropdown or toggle",
        "Changing status saves immediately",
        "UI updates without page refresh",
        "Typecheck passes",
        "Verify in browser using playwright-cli skill"
      ],
      "filesLikelyTouched": ["src/components/TaskListRow.tsx"],
      "priority": 3,
      "passes": false,
      "notes": ""
    },
    {
      "id": "US-004",
      "title": "Filter tasks by status",
      "description": "As a user, I want to filter the list to see only certain statuses.",
      "acceptanceCriteria": [
        "Filter dropdown: All | Pending | In Progress | Done",
        "Filter persists in URL params",
        "Typecheck passes",
        "Verify in browser using playwright-cli skill"
      ],
      "filesLikelyTouched": ["src/components/TaskList.tsx"],
      "priority": 4,
      "passes": false,
      "notes": ""
    }
  ]
}
```

## Final Check

Before saving, verify:

- [ ] Each story is small enough for one iteration
- [ ] Stories are ordered by dependency
- [ ] No story depends on a later story
- [ ] Every story includes `Typecheck passes`
- [ ] UI stories include browser verification
- [ ] Acceptance criteria are concrete and testable
