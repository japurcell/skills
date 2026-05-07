Deduped `review_scope_files`:
1. `skills/build-review/SKILL.md`
2. `skills/build-review/implementer-prompt.md`
3. `notes.txt`

Run **1 code-reviewer** (the scope is 5 files or fewer, so one reviewer gets the full deduped list).

Context to pass:
- `[Files to review]`
- `skills/build-review/SKILL.md`
- `skills/build-review/implementer-prompt.md`
- `notes.txt`

Exclude `scratch.tmp` (deleted) and `.gitignore` per the build workflow.
