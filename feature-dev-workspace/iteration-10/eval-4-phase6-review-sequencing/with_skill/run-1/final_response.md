# Phase 6 Quality Review — Caching Layer Across Three Service Files

## Process Track

This is a **Standard track** feature. Adding a caching layer across three service files touches enough surface area (multiple files, non-trivial logic for key generation, TTL, invalidation, and error paths) to warrant structured review, but it is not large or cross-cutting enough to be Deep.

---

## Phase 6 Sequence

Phase 6 runs in two ordered steps. You complete step 1 before launching step 2.

---

### Step 1 — code-simplifier (run first, alone)

Launch one independent **`code-simplifier`** subagent targeting the three modified service files.

**What it is told to focus on:**

> "Review the recently modified caching logic across the three service files. Focus on the implementation added in this session only. Identify unnecessary complexity, redundant abstractions, consolidation opportunities for repeated cache read/write patterns, naming clarity for cache keys and TTL constants, and anything that would make the caching layer harder to read or maintain. Preserve all functionality — only improve how the code expresses it."

You read the simplifier's output before moving to step 2, because any refactors it suggests should be applied (or evaluated) before the correctness reviewers examine the code. Reviewing already-simplified code avoids noise from issues that would have been cleaned up anyway.

---

### Step 2 — code-reviewer agents (run in parallel, after simplifier returns)

For Standard track, launch **two independent `code-reviewer` agents in parallel**, each with a distinct focus.

#### Reviewer A — Correctness & Cache Behavior

**What it is told to focus on:**

> "Review the caching layer additions in the three service files for functional correctness. Focus on: cache key generation (uniqueness, collision potential, inclusion of all discriminating inputs), TTL values and expiry handling, cache invalidation correctness (are all mutation paths invalidating the right keys?), behavior when the cache backend is unavailable (does the code degrade gracefully or fail hard?), thread safety and concurrent write scenarios, and cold-start / stale-data edge cases. Only report issues with confidence ≥ 80."

#### Reviewer B — Security & Conventions

**What it is told to focus on:**

> "Review the caching layer additions in the three service files for security issues and adherence to project conventions. Security focus: sensitive data exposure in cached values (PII, tokens, secrets), cache poisoning risk from user-controlled cache keys, and key namespace isolation between tenants or users if applicable. Conventions focus: naming patterns, import style, error handling approach, test coverage for the new caching paths, and consistency with how similar caching or I/O is done elsewhere in the codebase. Only report issues with confidence ≥ 80."

---

### Step 3 — Consolidation & Fixes

After both reviewers return:

1. Merge findings from the code-simplifier and both code-reviewers into a single ranked list.
2. Fix obvious high-severity issues (e.g., a missing cache invalidation path, sensitive data leaking into a cache key) directly without asking.
3. Surface remaining risks, lower-confidence findings, and follow-up work for the developer to evaluate.

---

## Summary

| Order | Subagent                                 | Run style                 | Focus                                                                                              |
| ----- | ---------------------------------------- | ------------------------- | -------------------------------------------------------------------------------------------------- |
| 1     | `code-simplifier`                        | Sequential (first, alone) | Simplify caching logic in 3 service files; reduce redundancy, improve naming, consolidate patterns |
| 2a    | `code-reviewer` (Correctness)            | Parallel with 2b          | Cache key uniqueness, TTL, invalidation, degraded-mode behavior, thread safety                     |
| 2b    | `code-reviewer` (Security & Conventions) | Parallel with 2a          | Sensitive data in cache, key isolation, naming, error handling, test coverage                      |

Three subagents total. The simplifier runs first because it may restructure the code; the correctness and conventions reviewers then inspect the final form in parallel to minimize latency.
