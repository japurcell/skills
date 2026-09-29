# Provider Lifecycle Capabilities

**Type:** research
**Status:** closed
**Blocked By:** none
**Research Dir:** ../research/provider-lifecycle-capabilities/

## Question

What do current official Codex, Copilot, and Gemini contracts allow a context management system to observe, inject, enforce, and continue across task arrival, session startup, turns, compaction, completion, and termination?

Distinguish relevant surfaces, including Codex CLI and desktop, Copilot CLI and VS Code, and Gemini CLI. Verify event timing, available task information, hook output semantics, nested agent behavior, configuration scope, and termination limitations. Separate documented guarantees, this repository's wiring, and behavior that still needs a deployed-version test. Record version and access limits instead of guessing. Identify the facts on which automatic retrieval and maintenance can safely depend without choosing their design.

Write cited findings to the assigned research directory. Append a concise factual Resolution here before closing this ticket. Do not resolve human decision tickets or update map.md.

---

## Resolution

[Provider lifecycle findings](../research/provider-lifecycle-capabilities/findings.md) compare official Codex, Copilot CLI, VS Code Local/Agent Host, and Gemini CLI contracts with this checkout's registrations. All expose event-triggered script work and context delivery, with different timing and output schemas. Context injection alone does not execute semantic agent maintenance. Continuation hooks can require more work, but shutdown and background completion have weaker guarantees; Copilot has a documented eight-block cap.

The evidence does not certify deployed versions, first-prompt ordering, nested-agent coverage, enforcement on timeout, desktop parity, or crash recovery. Findings identify required capability probes, harness-specific canonical documentation corrections, and unresolved support/fallback/task-boundary decisions without choosing an architecture. No installed configuration or canonical agent documentation was changed.
