# Feature Dev Workflow: Phase 6 Quality Review — Caching Layer Feature

## Understanding

You have just finished implementing a caching layer across three service files in a Python web app. Walking through Phase 6 quality review exactly as the feature-dev workflow specifies it.

**Track**: Standard — three-file change across service files.

---

## Phase 6: Quality Review — Exact Sequence

Phase 6 runs in the following order. The `code-simplifier` always runs first, before code review begins.

---

### Step 1: Launch `code-simplifier` subagent

**When**: Immediately after implementation is complete.

**Subagent role**: [`code-simplifier`](../code-simplifier/SKILL.md)

**What I tell it to focus on**:

> "Review the three modified service files: `service_a.py`, `service_b.py`, and `cache_layer.py`. Focus exclusively on identifying refactoring opportunities — duplication between the cache integration points, over-engineered abstraction in the cache key construction, or any logic that can be flattened without changing behavior. Return concrete suggestions with file and line references."

**Why first**: The code-simplifier cleans up structural issues so the code-reviewer assesses a simpler, cleaner implementation — not one with noise that could obscure real correctness or convention problems.

---

### Step 2: Address simplifier findings, then launch `code-reviewer` agents

**When**: After `code-simplifier` returns findings. Apply obvious improvements, then launch reviewers against the updated code.

**Subagents**: Multiple independent [`code-reviewer`](agents/code-reviewer.md) agents, run **in parallel** on the Standard track, each with a distinct focus:

#### code-reviewer-1 — Correctness

> "Review the caching layer implementation across `service_a.py`, `service_b.py`, and `cache_layer.py`. Focus on correctness: cache invalidation logic (are stale entries evicted properly?), thread safety if these services share state, error handling if the cache backend is unavailable, and boundary conditions (empty result caching, TTL edge cases)."

#### code-reviewer-2 — Conventions

> "Review the same three service files for adherence to the existing Python codebase conventions: naming patterns for cache keys, whether the cache abstraction matches how similar utilities are structured elsewhere in the codebase, import organization, and type annotation style."

#### code-reviewer-3 — Simplicity

> "Review the three modified service files purely for simplicity: is the cache integration the smallest, most direct implementation that meets the requirement? Is there any abstraction that could be removed without losing generality?"

---

### Step 3: Consolidate findings and fix

1. Collect findings from all three reviewers
2. Prioritize: correctness issues (cache invalidation bugs, thread safety) take priority over style
3. Fix obvious high-severity issues directly in the three service files
4. Surface remaining trade-offs (e.g., "cache invalidation strategy has a race window under high concurrency — flagged for follow-up") in the Phase 7 summary

---

## Key Points About the Sequence

| Constraint                                               | Source                                                                                                          |
| -------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| `code-simplifier` runs **before** `code-reviewer`        | "Always launch an independent code-simplifier subagent... after implementation" (listed as Action 1 in Phase 6) |
| Both are **always required**                             | "Always launch" and "Always run" — both use the mandatory qualifier                                             |
| They are **separate subagents**, not a single pass       | Phase 6 lists them as two distinct actions with different agent roles                                           |
| Standard track gets **multiple code-reviewer agents**    | "Standard or Deep: launch multiple independent code-reviewer agents in parallel with different focuses"         |
| Refactoring and quality review are **not the same step** | `code-simplifier` = refactoring opportunities; `code-reviewer` = quality review — distinct mandates             |
