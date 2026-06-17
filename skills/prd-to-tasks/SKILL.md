---
name: prd-to-tasks
description: Use when the user asks to convert, decompose, split, transform, or prepare a PRD, product requirements document, feature spec, planning doc, requirements-like markdown file, raw requirements, or feature description into atomic implementation tasks, userStories, JSON, prd.json, or input for /prd-build-loop. Trigger on requests like "convert PRD to tasks", "create prd.json", "break this into stories", "generate userStories", "decompose this feature", "requirements to stories", "tasks from requirements", "agent-ready stories", or "prepare for /prd-build-loop". Always split broad requirements into small, dependency-ordered, implementation-sized stories; never copy PRD sections unchanged unless already atomic.
---

# PRD to `prd.json`

Convert `prd_file` into an agent-ready `prd.json` with atomic implementation stories.

## Inputs

- `prd_file` required: PRD path or raw PRD text.
- `output_directory` optional:
  - If provided, save `output_directory/prd.json`.
  - Else if `prd_file` is a path, save beside it.
  - Else save `.agents/scratchpad/prd.json`.

## Workflow

1. Read `prd_file`.
2. Decompose broad requirements into atomic implementation stories.
3. Order stories by dependency, then PRD source order where possible.
4. Save valid JSON to the target `prd.json`.
5. Final response: story count, output path, and readiness for `/prd-build-loop`.

## Output schema

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

## Atomic story rules

`userStories` must be decomposed implementation stories, not copied PRD sections.

Each story must be narrow, complete, independently verifiable, and finishable by one agent in one iteration. A story usually covers exactly one:

- schema or migration change
- model or type update
- backend action, endpoint, service, or query
- UI component or surface
- user interaction
- filter, sort, search, badge, toggle, modal, or form
- integration point
- dashboard or aggregate view
- focused testable behavior

Never create stories that mean:

- implement the whole PRD, feature, system, epic, page, or full workflow
- combine multiple stageable behaviors
- copy a multi-capability PRD story unchanged

Split smaller when unsure.

## Split rules

Split any requirement that:

- spans multiple features, pages, flows, roles, entities, or UI surfaces
- has multiple unrelated verbs, such as create, edit, delete, filter, export, or notify
- combines schema, backend, and UI work that can be staged
- cannot be explained in 2–3 sentences
- would touch many unrelated files
- is not independently demoable after prerequisites
- uses “and” to join separate capabilities

Avoid horizontal stories like “build backend,” “build frontend,” or “write all tests” unless the PRD only asks for that layer.

## Decomposition algorithm

For each requirement:

1. Identify the smallest user-visible or system-visible capability.
2. Create prerequisite stories first:
   - database/schema
   - models/types
   - server actions/API/service/query
3. Split UI surfaces:
   - list view
   - detail view
   - form
   - modal
   - navigation
   - dashboard
4. Split user actions:
   - create
   - update
   - delete
   - filter
   - sort
   - search
   - export
   - notify
5. Split cross-cutting requirements only when independently implementable.
6. Re-split any generated story that still contains multiple capabilities.

## Ordering rules

Stories run in ascending `priority`; no story may depend on a later story.

Dependency order:

1. schema/database
2. shared types/models
3. backend/server logic
4. UI using that logic
5. aggregate/dashboard views
6. polish, validation, and follow-up enhancements

Preserve PRD source order where dependencies allow.

## Acceptance criteria rules

Criteria must be concrete and testable.

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

Bad criteria:

- `Works correctly`
- `Good UX`
- `Handles edge cases`
- `Implement the feature`

UI stories are incomplete without visual/browser verification.

## Field rules

- Use sequential IDs: `US-001`, `US-002`, etc.
- Derive `branchName` from the feature name in kebab-case.
- Keep top-level `description` short and based on the PRD title or intro.
- Set every story `passes` to `false`.
- Set every story `notes` to `""`.
- Include `filesLikelyTouched` when inferable.
- Exclude files ignored by repository `.gitignore`.
- Use `designGuidance` only when useful; otherwise set `[]`.
- The saved `prd.json` must contain valid JSON only: no markdown, comments, or trailing commas.

## Minimal example

Input:

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

Verify:

- [ ] PRD is decomposed into small implementation stories.
- [ ] No story is merely copied from the PRD.
- [ ] Each story is narrow, independently verifiable, and implementation-sized.
- [ ] No story depends on a later-priority story.
- [ ] Every story has concrete acceptance criteria.
- [ ] Every story includes `Typecheck passes`.
- [ ] Every UI story includes `Verify in browser using playwright-cli skill`.
- [ ] `filesLikelyTouched` excludes ignored files.
- [ ] `prd.json` is valid and saved to the correct path.

If any story fails, split or revise it before saving.
