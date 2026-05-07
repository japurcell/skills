**Deduped review scope:** `skills/build-review/SKILL.md`, `skills/build-review/implementer-prompt.md`, `notes.txt`.

That comes from merging the implementer-touched files with `git status --porcelain`, then deduping and excluding deleted files and any `.gitignore` file. So `scratch.tmp` is out, `.gitignore` is out, and `notes.txt` stays in.

**How many code-reviewers:** `1`. The repo copy of `skills/build-review/SKILL.md` says **`≤5 files` => launch 1 code-reviewer covering the full list**, and reuse the same partitioning used for simplification.

**Context to send before tracking is updated:** give that reviewer the **exact file list above** plus the **current verification context**. In practice, that means the implementer’s verification details, updated with any validation the code-simplifier ran. The reviewer should review exactly that scope, not recompute it, and tracking waits until that reviewer returns `DONE`.
