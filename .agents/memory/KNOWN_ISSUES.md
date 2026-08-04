---
coverage: Repo-wide / cross-cutting quirks and workarounds; layer-specific issues live in known-issues/<area>.md
---

# Known Issues

Repo-wide and cross-cutting issues only. Layer-specific gotchas live in dedicated per-layer files (load only the one for your area):

- hooks (`.copilot/hooks`, `.gemini/hooks`) → `.agents/memory/known-issues/hooks.md`
- skills (`skills/`) → `.agents/memory/known-issues/skills.md`

## Blank lines with whitespace fail linting

**Affected area:** all
**Description:** Blank lines containing any space or tab fail lint/format; trailing whitespace also fails.
**Workaround:** Keep blank lines completely empty.
