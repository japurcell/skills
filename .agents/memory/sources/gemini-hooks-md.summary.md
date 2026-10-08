---
type: Source Summary
description: Saved-source reference for Gemini lifecycle, configuration precedence, trust, or hook management.
sources:
  - resource: ../../sources/gemini-hooks.md
---

# gemini-hooks - Source Reference

- The overview describes synchronous hook execution, JSON stdout, event-specific matchers, configuration, project trust, and hook management commands.
- Its exit table prefers exit 0 plus structured decisions, uses exit 2 for system blocks, and treats other nonzero exits as warnings. The saved precedence table orders project, user, system, then extension settings.

Evidence: [immutable raw source](../../sources/gemini-hooks.md), checked against the saved text on 2026-10-07. Recheck when the source changes or current external behavior matters. This summary routes reading; it does not create project policy.
