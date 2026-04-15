# Phase 6: Minimum Non-Negotiable Subagent Steps

Phase 6 (Quality Review) mandates exactly **two** subagent steps. Both are required on every track; neither can be dropped.

---

## Step 1 — code-simplifier subagent(s)

**Role**: `code-simplifier`  
**Mandate** (verbatim): *"Launch independent code-simplifier subagents to identify refactoring opportunities after implementation."*

Scaling rule (changes the count, not the requirement):
- **≤5 changed files** → 1 agent covering all changed files  
- **>5 changed files** → one agent per non-overlapping partition (by module/directory/logical area), launched in parallel

No file may appear in more than one agent's scope.

---

## Step 2 — code-reviewer subagent(s)

**Role**: `code-reviewer`  
**Mandate** (verbatim): *"Always run independent code-reviewer agents for quality review on every track."*

Scaling rule (changes the count, not the requirement):
- **Light track** → at least one agent  
- **Standard or Deep track** → multiple agents in parallel with different focuses (e.g., simplicity, correctness, conventions)

---

## What Is NOT a Separate Required Subagent Step

The remaining Phase 6 actions are internal orchestrator work, not subagent launches:
- Consolidate findings and prioritize issues
- Fix obvious high-severity issues directly
- Surface remaining risks and follow-up work

---

## Summary Table

| # | Subagent Role     | Keyword in Skill       | Minimum Count |
|---|-------------------|------------------------|---------------|
| 1 | `code-simplifier` | "Launch … subagents"   | 1             |
| 2 | `code-reviewer`   | "Always run … agents"  | 1 (Light) / 2+ (Standard/Deep) |

These are the only two subagent roles Phase 6 mandates. Everything else is orchestrator-level work.
