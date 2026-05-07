Dispatch the code-simplifier next. Send the simplifier-prompt.md payload containing:
- the four deduped review_scope_files (the files the implementer touched),
- the implementer’s verification context,
- the set of all uncommitted files from git status --porcelain (exclude deleted files and .gitignore).

Scope the simplifier wave narrowly to exactly those four touched files (and any other uncommitted files discovered) — do not broaden to unrelated files or pre-draft fixes. After the simplifier returns DONE, run the code-reviewer; only update tracking after the final reviewer returns DONE.
