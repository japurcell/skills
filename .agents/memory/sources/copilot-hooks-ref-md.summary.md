---
type: Source Summary
description: Saved-source reference for Copilot hook events, CLI/cloud differences, matchers, or exit behavior.
sources:
  - resource: ../../sources/copilot-hooks-ref.md
---

# copilot-hooks-ref - Source Reference

- The saved reference distinguishes CLI and cloud hook discovery, event payloads, matchers, decision schemas, and command/HTTP behavior.
- It documents separate progress JSON before a final command result. Command pre-tool errors fail closed, but timeouts fail open; consult the raw event and exit-code sections before relying on enforcement.

Evidence: [immutable raw source](../../sources/copilot-hooks-ref.md), checked against the saved text on 2026-10-07. Recheck when the source changes or current external behavior matters. This summary routes reading; it does not create project policy.
