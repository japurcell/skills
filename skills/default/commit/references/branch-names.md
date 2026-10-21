# Branch names

Create a branch only when required by `SKILL.md`.

Format:

```text
<type>/<issue>-<slug>
```

or:

```text
<type>/<slug>
```

Rules:

- Lowercase kebab-case.
- Use the commit type as prefix.
- Prefer issue number when available.
- Slug preference:
  1. short summary of selected changes
  2. single selected file basename without extension
  3. `worktree-update-YYYYMMDD`

Examples:

```text
fix/123-handle-empty-config
docs/update-readme
chore/worktree-update-20260115
```
