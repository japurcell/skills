Send the **code-reviewer prompt** with the **union of the touched files and the filtered `git status --porcelain` files**, plus the **current verification context**. From the status you gave, the files to include are:

- `skills/build/SKILL.md`
- `skills/build/implementer-prompt.md`
- `notes.txt`

Exclude:

- `scratch.tmp` — deleted
- `.gitignore` — explicitly excluded by the workflow

So the manager’s handoff is effectively: **review those three files + the current verification context**, then wait for the code-reviewer to return plain `DONE` before updating tracking.
