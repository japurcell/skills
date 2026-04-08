# Feature-Dev Workflow Response: Go/No-Go on Skipping Exploration

## Understanding

**Process Track: Standard**

You're new to the repo and delivering a medium-sized feature — this is textbook Standard track: multiple files touched, meaningful ambiguity from unfamiliarity, and real risk of rework if you code against the wrong conventions. Your lead's suggestion to skip exploration and figure out conventions as you go is a common time-pressure instinct. This response gives you a structured answer on whether to follow it.

---

## Relevant Findings

The feature-dev workflow is built on one non-negotiable principle:

> **"Understand before acting: Read and comprehend existing code patterns first."**

This isn't bureaucracy — it exists because convention violations in medium-sized features compound. A wrong abstraction in file 1 propagates through files 5–12. Discovering the repo uses a service-layer pattern after you've wired business logic directly into controllers means rewriting, not refactoring.

For a developer new to the codebase, the risk profile of skipping exploration is elevated compared to a team member who has internalized patterns over months. Speed gained by skipping exploration is routinely lost to:
- Mismatched naming or structural conventions caught in code review
- Duplicating existing utilities or abstractions
- Integration failures at boundaries you didn't know existed
- Test setup that doesn't match the project's testing patterns

---

## Recommendation

### **NO-GO on skipping exploration.**

Proceed to implementation only after completing the minimum pre-implementation checklist below. For a medium-sized feature, this checklist typically takes 30–90 minutes and prevents days of rework.

The feature-dev skill is explicit: exploration is Phase 2 of the workflow and is required on Standard track before design or implementation. Skipping it violates the core principle "understand before acting."

---

## Minimum Pre-Implementation Checklist

Complete every item before writing production code.

### ✅ Phase 1 — Discovery (15–20 min)

- [ ] **Define the feature clearly**: Write one paragraph — what problem does it solve, what does it do, what is explicitly out of scope?
- [ ] **Identify the process track**: Confirm this is Standard track (medium, some ambiguity, unfamiliar repo). Upgrade to Deep if the feature crosses many subsystems or has high product ambiguity.
- [ ] **Create a todo list** tracking all phases. Don't skip steps silently — mark them done.

### ✅ Phase 2 — Codebase Exploration (30–60 min)

Run **two focused exploration passes** (parallel if you have agents available, sequential if not):

- [ ] **Exploration A — Similar features**: Find 1–2 existing features similar in shape to yours. Trace their full implementation: entry point → business logic → persistence/output → tests. Note the files.
- [ ] **Exploration B — Architecture & conventions**: Map the high-level structure. Identify: directory layout, naming conventions, abstraction layers (controllers/services/repos?), error handling patterns, dependency injection approach, and test patterns.
- [ ] **Read the key files directly**: Don't rely only on agent summaries. Read the 5–10 most important files identified in exploration. Your understanding must be grounded in source.
- [ ] **Document what you found**: Note the patterns you'll follow. If conventions conflict, flag it now.

### ✅ Phase 3 — Clarifying Questions (10–15 min)

- [ ] **List only the questions that would change your design** if answered differently. Skip questions where a reasonable default exists.
- [ ] **Resolve blockers before design**: If a question is truly blocking (e.g., "should this be sync or async?"), get the answer now, not during implementation.
- [ ] **State your assumptions explicitly** for everything you're deciding without asking.

### ✅ Phase 4 — Architecture Decision (10–20 min)

- [ ] **Propose one concrete approach** (Standard track — not multiple options for their own sake).
- [ ] **Map the implementation**: List the files you'll create or modify, in the order you'll touch them.
- [ ] **Identify integration points and risks** before writing a line of code.
- [ ] If another agent or person will implement, write a handoff artifact at `.agents/scratchpad/<feature-name>/handoff-plan.md`.

### ✅ Gate Check — Ready to Implement?

Before touching production code, confirm:

- [ ] You can name the 3–5 most important files in the relevant subsystem.
- [ ] You know the repo's testing pattern and can write a failing test before implementing.
- [ ] You know the naming and structural conventions for this kind of change.
- [ ] No blocking questions remain unanswered.

If all boxes are checked: **Go.**  
If any are unchecked: **Resolve them first.**

---

## Implementation Note

Once you begin implementation, the skill requires TDD (red-green-refactor loop) — write a failing test first, then implement. This is required on every track, not optional. It's the fastest way to validate that your implementation matches the conventions you learned in exploration.

---

## Summary

| Question | Answer |
|---|---|
| Should you skip exploration? | **No.** |
| Why not? | Convention violations compound; rework costs more than 30–90 min of exploration. |
| Minimum time investment before coding? | ~1–2 hours for Standard track exploration + design. |
| What's the first thing to do? | Define the feature clearly, then run two focused exploration passes. |
| When is it safe to start coding? | When you can pass the Gate Check above. |
