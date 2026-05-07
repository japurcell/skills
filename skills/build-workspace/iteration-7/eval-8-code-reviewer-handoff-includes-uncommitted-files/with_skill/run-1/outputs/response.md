The manager should dispatch **`skills/build/code-reviewer-prompt.md`** with **Context** containing:

1. **The touched files**
2. **The current verification context**
3. **All uncommitted files from `git status --porcelain`, excluding deleted files and `.gitignore` files**

From the status you gave, the extra uncommitted files to include are:

- `skills/build/SKILL.md`
- `skills/build/implementer-prompt.md`
- `notes.txt`

And the manager should **exclude**:

- `scratch.tmp` — deleted
- `.gitignore` — `.gitignore` file

So the reviewer handoff is effectively: **review the touched files + current verification context + `skills/build/SKILL.md`, `skills/build/implementer-prompt.md`, and `notes.txt`**, then wait for the reviewer to return `DONE` before updating tracking.
