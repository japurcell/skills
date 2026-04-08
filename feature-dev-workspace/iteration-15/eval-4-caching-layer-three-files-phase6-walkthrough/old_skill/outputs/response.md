# Phase 6 Quality Review: Caching Layer Across Three Service Files

## Track

**Standard** — a caching layer touching three service files is medium-sized, involves a non-trivial design surface (cache keys, invalidation, TTL, error handling), and spans multiple files. Standard Track is the right fit.

---

## Phase 6: Quality Review Walkthrough

### Goal
Ensure the caching implementation is simple, DRY, elegant, easy to read, and functionally correct.

---

### Step 1 — Launch `code-simplifier` (first, independent)

**Subagent**: `code-simplifier`

**Told to focus on**:
> "Review the three service files that now contain the caching layer: `<service_a.py>`, `<service_b.py>`, and `<service_c.py>`. Identify refactoring opportunities: repeated cache read/write patterns that could be extracted into a shared decorator or utility, duplicated TTL configuration, inconsistent cache key construction across services, and any over-engineered logic that could be simplified. Return a prioritized list of changes with concrete before/after suggestions."

**Why first**: The code-simplifier's job is to spot structural redundancy and refactoring opportunities before reviewers call out bugs or style issues. Running it first means its output can inform whether the reviewers are seeing a clean or cluttered implementation.

---

### Step 2 — Launch three `code-reviewer` agents **in parallel**

On Standard Track the skill requires multiple independent code-reviewer agents with different focuses. All three launch simultaneously once the code-simplifier has returned (or concurrently with it if time pressure demands).

---

#### code-reviewer #1 — Correctness

**Subagent**: `code-reviewer`

**Told to focus on**:
> "Review the caching layer implemented across `<service_a.py>`, `<service_b.py>`, and `<service_c.py>` for **correctness**. Focus on: cache invalidation logic (are stale entries evicted at the right times?), race conditions or thread-safety issues (double-check/set problems), cache key collisions between services (do keys namespace correctly?), behavior when the cache backend is unavailable (does the code degrade gracefully or crash?), and TTL edge cases (what happens at expiry boundaries?). Flag any issue that could produce incorrect data being served to callers."

---

#### code-reviewer #2 — Simplicity & DRY

**Subagent**: `code-reviewer`

**Told to focus on**:
> "Review the caching layer across `<service_a.py>`, `<service_b.py>`, and `<service_c.py>` for **simplicity and DRY**. Focus on: whether the cache read/write/invalidate pattern is implemented consistently or divergently across the three files, whether any shared abstraction (decorator, mixin, utility function) should replace copy-pasted blocks, whether cache configuration (TTL values, backend references) is centralized or scattered, and whether any logic is more complex than the problem requires. Recommend concrete consolidations."

---

#### code-reviewer #3 — Conventions & Project Patterns

**Subagent**: `code-reviewer`

**Told to focus on**:
> "Review the caching layer across `<service_a.py>`, `<service_b.py>`, and `<service_c.py>` for **adherence to project conventions**. Focus on: Python style (type hints, naming, docstrings matching the project's existing style), whether the caching integration follows the same patterns used elsewhere in the codebase (e.g., how other cross-cutting concerns like logging or metrics are applied), whether error handling around cache operations matches the project's established error-handling conventions, and whether any new public interfaces are documented consistently with the rest of the codebase."

---

### Step 3 — Consolidate Findings

After all agents return, consolidate their outputs into a single prioritized issue list:

1. **High severity** (correctness bugs, data integrity risks) — fix immediately
2. **Medium severity** (DRY violations, simplification opportunities flagged by both code-simplifier and reviewers) — fix before merge
3. **Low severity** (style, minor convention deviations) — fix if quick, otherwise note as follow-up

---

### Step 4 — Fix High-Severity Issues Directly

Per the skill: *"Fix obvious high-severity issues directly unless the user has asked to stop after review."*

Apply fixes in this order:
1. Correctness bugs (race conditions, bad invalidation, missing error handling)
2. Consolidation of duplicated cache patterns (if code-simplifier + reviewer #2 agree)
3. Convention corrections that are one-liners

---

### Step 5 — Surface Remaining Risks

Report to the user:
- Any unresolved trade-offs (e.g., "cache-aside vs. write-through was a judgment call — here's why cache-aside was chosen")
- Follow-up work that wasn't fixed in this pass
- Suggestions for load/integration testing the cache behavior under concurrency

---

## Summary of Subagents

| Order | Subagent | Focus |
|-------|----------|-------|
| 1 | `code-simplifier` | Refactoring opportunities, DRY, structural redundancy across three files |
| 2a (parallel) | `code-reviewer` | Correctness: invalidation, thread safety, key collisions, degradation, TTL |
| 2b (parallel) | `code-reviewer` | Simplicity & DRY: pattern consistency, shared abstractions, configuration centralization |
| 2c (parallel) | `code-reviewer` | Conventions: Python style, project patterns, error handling, documentation |

**Total subagents**: 4 (1 code-simplifier + 3 code-reviewers)
