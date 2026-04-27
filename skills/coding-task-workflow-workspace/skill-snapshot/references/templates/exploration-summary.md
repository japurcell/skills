---
work_id: WORK_ID
phase: exploration
status: complete | partial
updated_at: ISO8601_TIMESTAMP
depends_on: [worktree]
track: light | standard | deep
agents_launched: 0
---

# Exploration Summary: TITLE

## Track Selected

**Track**: light | standard | deep
**Rationale**: One sentence explaining why this track was chosen (scope, ambiguity, familiarity with codebase).

## Key Findings

- **Finding 1**: Description of an important pattern, constraint, or architectural insight.
- **Finding 2**: Description.
- **Finding 3**: Description.

*Focus on findings that will influence the plan or implementation. Omit obvious or irrelevant observations.*

## Anti-patterns to Avoid

- **Anti-pattern 1**: What to avoid and why (e.g., "Do not use the legacy UserManager class — it is deprecated in favour of UserService").
- **Anti-pattern 2**: Description.

## Relevant Files

Top 5–10 files most relevant to this work item. Full list is in `files.csv`.

| File | Relevance |
|------|-----------|
| `src/example/file.ts` | Existing similar feature; follow its patterns |
| `src/example/file.test.ts` | Test pattern to follow |

## Open Questions

Questions that could not be answered from codebase exploration alone. Full details in `open-questions.md`.

- **q1**: Question text.
- **q2**: Question text.
