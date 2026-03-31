## Proposed Additions to AGENTS.md

Based on today's learnings, here are the recommended updates:

### Update: ./AGENTS.md

**Why:** Document command performance discovery during codebase exploration

```diff
+ Use `rg` (ripgrep) instead of `grep` – it's faster for searching this workspace
```

### Update: ./AGENTS.md

**Why:** Establish best practice for minimal, focused edits

```diff
+ Use `apply_patch` for single-file modifications to ensure precision and reviewability
```

### Update: ./AGENTS.md

**Why:** Ensure edit quality and prevent undetected issues

```diff
+ Always run `get_errors` immediately after editing files to catch errors early
```

---

Would you like me to apply these additions to AGENTS.md? If so, I'll integrate them into the appropriate section (likely a "Tools & Commands" or "Best Practices" section if one exists, or create one if needed).
