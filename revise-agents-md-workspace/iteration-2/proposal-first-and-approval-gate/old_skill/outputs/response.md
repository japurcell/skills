### Update: ./AGENTS.md

**Why:** Capture tool performance insights to guide future search strategy

```diff
+ **Search Strategy:** Use `rg` (ripgrep) for text search—it's faster than `grep` in this repo. Prefer `rg` with regex patterns when searching across files or exploring codebase patterns.
```

### Update: ./AGENTS.md

**Why:** Guide efficient single-file editing workflow

```diff
+ **Editing Single Files:** Prefer `apply_patch` for single-file edits to reduce context switching and maintain focus on localized changes.
```

### Update: ./AGENTS.md

**Why:** Ensure code quality after modifications

```diff
+ **Validation:** Run `get_errors` after any file edits to catch issues immediately and validate changes against project linting/type rules.
```
