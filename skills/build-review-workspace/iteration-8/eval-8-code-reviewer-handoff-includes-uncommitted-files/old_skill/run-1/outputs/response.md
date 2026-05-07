**Deduped review scope:** `skills/build-review/SKILL.md`, `skills/build-review/implementer-prompt.md`, and `notes.txt`.

**How many code-reviewers:** **1.** This snapshot’s build workflow dispatches a single `code-reviewer` after the code-simplifier returns `DONE`, and tracking is updated only after that reviewer returns `DONE`.

**Context to send before any tracking update:** give that reviewer:
1. The implementer-touched files: `skills/build-review/SKILL.md`, `skills/build-review/implementer-prompt.md`
2. The **current verification context** (the latest verification details/results carried forward after implementer + simplifier)
3. All uncommitted files from `git status --porcelain`, excluding deleted files and `.gitignore` files

In this case, that uncommitted set is `skills/build-review/SKILL.md`, `skills/build-review/implementer-prompt.md`, and `notes.txt`; `scratch.tmp` is excluded because it’s deleted, and `.gitignore` is excluded explicitly.
