# Phase 6 Quality Review — Caching Layer Across Three Service Files

## Track Selection

A caching layer touching three service files is **Standard track**: medium-sized, multi-file, with real correctness risk (cache invalidation, stale data, concurrency) and some ambiguity in conventions. Standard track Phase 6 calls for multiple independent code-reviewer agents launched in parallel.

---

## Subagents Launched

I launch **three independent `code-reviewer` agents in parallel**. All three start at the same time.

### Agent 1 — Correctness & Cache Semantics

**Focus prompt:**

> Review the caching layer added to the three service files. Focus on correctness: Are cache keys unique and collision-free across services? Is cache invalidation triggered in all write paths (creates, updates, deletes)? Are there race conditions or stale-read windows under concurrent requests? Does the TTL policy match the data's expected staleness tolerance? Flag any path where a caller could silently receive outdated data.

### Agent 2 — Simplicity & DRY

**Focus prompt:**

> Review the caching layer added to the three service files. Focus on simplicity and duplication: Is cache read/write/invalidate logic repeated across files instead of centralized? Are there unnecessary abstractions or overly complex key-building patterns? Could any of the three implementations be collapsed into a shared helper without losing clarity? Flag anything that adds cognitive overhead without a clear payoff.

### Agent 3 — Conventions & Style

**Focus prompt:**

> Review the caching layer added to the three service files. Focus on project conventions: Does the cache usage match how other parts of the codebase handle caching (if any prior patterns exist)? Are naming conventions for cache keys, TTL constants, and function signatures consistent with the rest of the service layer? Are there missing or inconsistent error-handling patterns (e.g., cache backend unavailable)? Check that type hints, docstrings, and logging follow the project's existing style.

---

## Order of Operations

| Step | Action                                                                                            |
| ---- | ------------------------------------------------------------------------------------------------- |
| 1    | Launch Agents 1, 2, and 3 **simultaneously** (parallel)                                           |
| 2    | Collect all three review reports                                                                  |
| 3    | Consolidate findings — de-duplicate overlapping issues, classify each as high/medium/low severity |
| 4    | Fix all high-severity issues directly (e.g., missing invalidation on a write path, key collision) |
| 5    | Surface remaining medium/low issues and follow-up risks to the developer                          |

The agents run in parallel — there is no sequential dependency between them. Consolidation and fixing happen only after all three have returned.
