---
name: prd-to-tasks
description: Convert a PRD into `prd.json` for the autonomous agent system. Use for requests like - convert this PRD, turn this into JSON, create prd.json from this.
---

# PRD to `prd.json`

Convert a PRD (file path or raw markdown/text) into `prd.json`.

## Inputs

- `prd_file` (required): PRD file path or raw text.
- `output_directory` (optional): Directory for `prd.json`.
  - If provided, save to `output_directory/prd.json`.
  - Else if `prd_file` is a file path, save next to it.
  - Else save to `.agents/scratchpad/prd.json`.

## Workflow

1. Read `prd_file`.
2. Create `prd.json`.
3. Save it.
4. In the final response, report:
   - total story count
   - output file path
   - readiness for `/prd-build-loop`

## Output format

```json
{
  "project": "[Project Name]",
  "branchName": "[feature-name-kebab-case]",
  "description": "[Short feature description]",
  "userStories": [
    {
      "id": "US-001",
      "title": "[Story title]",
      "description": "As a [user], I want [feature] so that [benefit]",
      "acceptanceCriteria": ["Criterion 1", "Criterion 2", "Typecheck passes"],
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

## Rules

### 1) Make stories implementation-sized

Create one story per unit of work that one agent can finish in one iteration without depending on unfinished prior work. Split anything too large.

Good:

- Add a database column and migration
- Add a UI component to an existing page
- Update a server action
- Add a filter dropdown

Too large:

- Build the entire dashboard
- Add authentication
- Refactor the API

Rule of thumb: if a change cannot be described in 2-3 sentences, split it.

### 2) Order by dependency

Stories run in ascending `priority`. No story may depend on a later story.

Use this order when relevant:

1. Schema/database changes
2. Backend/server logic
3. UI using that logic
4. Aggregated/dashboard views

Set priority by dependency first, then PRD source order.

### 3) Make acceptance criteria testable

Acceptance criteria must be concrete and verifiable.

Good:

- Add `status` column to tasks table with default `pending`
- Filter dropdown has options: All, Active, Completed
- Clicking delete shows a confirmation dialog
- Typecheck passes
- Tests pass

Bad:

- Works correctly
- Good UX
- Handles edge cases

Always include:

- `Typecheck passes`

Include when applicable:

- `Tests pass` for testable logic
- `Verify in browser using playwright-cli skill` for UI changes

UI stories are not complete until visually verified.

### 4) Field rules

- Use sequential IDs: `US-001`, `US-002`, etc.
- Derive `branchName` from the feature name in kebab-case.
- Keep `description` short and based on the PRD title or intro.
- Set every story to `"passes": false` and `"notes": ""`.
- Include `filesLikelyTouched` when inferable. Exclude files matched by repository `.gitignore`.
- Use `designGuidance` only when useful; otherwise set it to `[]`.

## Splitting example

Original:

- Add user notification system

Split:

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
      "designGuidance": [
        {
          "source": "https://www.prisma.io/docs/concepts/components/prisma-schema/data-model#enum-types",
          "description": "Use an enum type for the status column.",
          "rationale": "Enforces valid values."
        }
      ],
      "priority": 1,
      "passes": false,
      "notes": ""
    },
    {
      "id": "US-002",
      "title": "Display status badge on task cards",
      "description": "As a user, I want to see task status at a glance.",
      "acceptanceCriteria": [
        "Each task card shows a status badge",
        "Badge colors: gray=pending, blue=in_progress, green=done",
        "Typecheck passes",
        "Verify in browser using playwright-cli skill"
      ],
      "filesLikelyTouched": ["src/components/TaskCard.tsx"],
      "designGuidance": [
        {
          "source": "https://web.dev/articles/color-and-contrast-accessibility",
          "description": "Ensure badge colors meet accessibility contrast standards.",
          "rationale": "Maintaining sufficient color contrast is essential for users with visual impairments to distinguish between different statuses effectively."
        },
        {
          "source": "design-system/components/StatusBadge",
          "description": "Use the existing status badge component.",
          "rationale": "Keeps UI consistent."
        }
      ],
      "priority": 2,
      "passes": false,
      "notes": ""
    },
    {
      "id": "US-003",
      "title": "Add status toggle to task list rows",
      "description": "As a user, I want to change task status from the list.",
      "acceptanceCriteria": [
        "Each row has a status dropdown or toggle",
        "Changing status saves immediately",
        "UI updates without page refresh",
        "Typecheck passes",
        "Verify in browser using playwright-cli skill"
      ],
      "filesLikelyTouched": ["src/components/TaskListRow.tsx"],
      "designGuidance": [
        {
          "source": "design-system/components/StatusToggle",
          "description": "Use the existing status toggle component.",
          "rationale": "Keeps UI consistent."
        }
      ],
      "priority": 3,
      "passes": false,
      "notes": ""
    },
    {
      "id": "US-004",
      "title": "Filter tasks by status",
      "description": "As a user, I want to filter tasks by status.",
      "acceptanceCriteria": [
        "Filter dropdown options: All | Pending | In Progress | Done",
        "Filter persists in URL params",
        "Typecheck passes",
        "Verify in browser using playwright-cli skill"
      ],
      "filesLikelyTouched": ["src/components/TaskList.tsx"],
      "designGuidance": [
        {
          "source": "design-system/components/StatusFilter",
          "description": "Use the existing status filter component.",
          "rationale": "Keeps UI consistent."
        }
      ],
      "priority": 4,
      "passes": false,
      "notes": ""
    }
  ]
}
```

## Final check

Before saving, verify:

- [ ] Each story is small enough for one iteration
- [ ] Stories are ordered by dependency
- [ ] No story depends on a later story
- [ ] Every story includes `Typecheck passes`
- [ ] UI stories include `Verify in browser using playwright-cli skill`
- [ ] `filesLikelyTouched` excludes files matched by repository `.gitignore`
- [ ] Acceptance criteria are concrete and testable
