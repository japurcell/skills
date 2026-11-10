---
name: reflect
description: Reflect on the conversation and update the brain. Mandatory at the end of sessions that change code. Use anytime you make a mistake and correct it, receive corrections or negative code review, discover tool quirks, or gain significant codebase learnings. Review may conclude no write is needed. Use when the user says "reflect", "remember this".
---

# Reflect

Review the conversation and persist learnings - to `brain/`, to skill files, or as structural enforcement.

## Process

Track the review in the active plan when one exists; otherwise use the available planning tools or a short checklist.

1. **Scan the conversation** for:
   - Mistakes made and corrections received
   - User preferences and workflow patterns
   - Codebase knowledge gained (architecture, gotchas, patterns)
   - Tool/library quirks discovered
   - Decisions made and their rationale
   - Friction in skill execution, orchestration, or delegation
   - Repeated manual steps that could be automated or encoded
2. **Identify lessons** that will matter in a future session. If none qualify, finish here.
3. **Route each remaining learning** to the appropriate destination below. Before a brain write, read `brain/index.md` and the relevant topic notes. Write only what those notes do not already cover.
4. **Reconcile navigation** using the brain skill after a brain write. Hooks own the root inventory.

## Routing

Not everything belongs in the brain. Route each learning to where it will have the most impact.

### Structural enforcement check

Before routing a learning to `brain/`, ask: can this be a lint rule, script, metadata flag, or runtime check? If yes, encode it structurally and skip the brain note. See `brain/principles/encode-lessons-in-structure.md`.

### Brain files (`brain/`)

Codebase knowledge, delegation principles, gotchas - anything that informs future sessions. This is the default destination. Use the `brain` skill for writing conventions.

- One topic per file. File name = topic slug.
- Group in directories with index files using standard Markdown links.
- No inlined content in index files.

### Skill improvements (`.agents/skills/<skill>/`)

If a learning is about how a specific skill works - its process, prompts, or edge cases - update the skill directly. Use the `skill-creator` skill for guidelines on effective skill content.

### Orchestration workflow improvements

If the session revealed systemic orchestration issues, route to:

- **Brain principle** (new delegation heuristic) → `brain/delegation/`
- **Skill mechanics change** (monitoring loop, review step) → relevant skill file
- **New skill opportunity** (recurring workflow that could be encoded) → note in summary for the user

### Backlog items (`brain/todos.md`)

Follow-up work that can't be done during reflection - bugs, non-trivial rewrites, tooling gaps. Use the `todo` skill to file.

## Summary

```
## Reflect Summary
- Brain: [files created/updated, one-line each]
- Skills: [skill files modified, one-line each]
- Structural: [rules/scripts/checks added]
- Todos: [follow-up items filed]
```
