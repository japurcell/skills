# Phase 6 Quality Review — Caching Layer Feature

## Track Determination

Adding a caching layer across three service files is a **Standard track** feature. It touches several files, involves non-trivial design decisions (cache invalidation, TTL policy, error handling), and carries moderate correctness risk.

---

## Phase 6: Quality Review

The old feature-dev skill's Phase 6 instructions for Standard track are:

> Launch multiple independent `code-reviewer` agents in parallel with different focuses such as simplicity, correctness, and conventions.

### Subagents Launched

All three are launched **in parallel** (not sequentially).

---

#### Agent 1 — `code-reviewer` (Simplicity focus)

**Told to focus on:**

> "Review the caching layer changes across the three service files for simplicity and elegance. Look for unnecessary complexity, redundant logic, over-engineering, code duplication, and anything that could be expressed more clearly. Flag any patterns that are harder to read or maintain than they need to be."

---

#### Agent 2 — `code-reviewer` (Correctness focus)

**Told to focus on:**

> "Review the caching layer changes across the three service files for correctness. Look for bugs, logic errors, race conditions, incorrect cache key generation, missing or incorrect cache invalidation, silent failure modes (e.g., cache errors swallowed without fallback), and security issues such as caching data that should not be cached (PII, session tokens)."

---

#### Agent 3 — `code-reviewer` (Conventions focus)

**Told to focus on:**

> "Review the caching layer changes across the three service files for adherence to project conventions. Check import patterns, naming conventions, error handling style, logging practices, and testing coverage as defined in the project guidelines (CLAUDE.md or equivalent). Flag any deviations from how similar patterns are implemented elsewhere in this codebase."

---

### After Agents Return

1. **Consolidate findings** — merge all reported issues, deduplicate, and sort by severity (Critical → Important).
2. **Fix high-severity issues directly** — apply fixes unless the user has asked to stop after review.
3. **Surface remaining risks** — present lower-priority issues, trade-offs, and suggested follow-up work clearly.

---

## Order Summary

| Step | What happens                                                          |
| ---- | --------------------------------------------------------------------- |
| 1    | Launch all three `code-reviewer` agents **simultaneously** (parallel) |
| 2    | Receive findings from all three                                       |
| 3    | Consolidate, deduplicate, prioritize                                  |
| 4    | Fix critical/important issues                                         |
| 5    | Surface remaining risks and follow-up items                           |
