# Phase 6 Quality Review — Caching Layer (3 Service Files)

## Track Selection

A caching layer across three service files is **Standard track** — it touches several files, involves real design decisions (cache key strategy, TTL policy, invalidation), and has meaningful correctness risk.

---

## Phase 6 Execution

### Step 1 — code-simplifier (runs first, before review)

**1 agent**, covering all three changed files. Because 3 files ≤ 5, a single agent handles everything. Running this before code-reviewer agents matters: the simplifier applies edits directly, so reviewers should see the cleaned-up code, not the raw first-pass implementation.

**Agent launched:**

| # | Agent | Files scoped | Focus |
|---|-------|-------------|-------|
| 1 | `code-simplifier` | `services/user_service.py`, `services/product_service.py`, `services/order_service.py` | Identify and apply refactoring opportunities: collapse duplicated cache get/set patterns across the three services into shared helpers, remove unnecessary indirection, ensure cache key construction is DRY and readable, verify no dead code was left from the implementation pass |

Wait for this agent to complete and commit its edits before proceeding.

---

### Step 2 — code-reviewer agents (launched in parallel after simplifier)

Standard track requires multiple independent reviewers with different focuses. Three agents launch simultaneously — each reads the now-simplified files but targets a distinct risk surface.

| # | Agent | Focus |
|---|-------|-------|
| 2 | `code-reviewer` — **Correctness** | Cache key collision potential (are keys namespaced per service/entity?), cache invalidation coverage (is stale data possible after writes?), behavior when the cache backend is unavailable (does it fail open or crash?), TTL values and whether they match data volatility |
| 3 | `code-reviewer` — **Simplicity & Design** | Is the caching abstraction the right layer of indirection? Are any patterns over-engineered for what the app needs? Is the cache interface consistent across all three services? Would a decorator or mixin have been cleaner than inline get/set calls? |
| 4 | `code-reviewer` — **Conventions** | Python idioms (context managers, type annotations, dataclass usage), PEP 8 compliance, naming consistency with the existing codebase, test coverage of the new cache paths, appropriate use of `__all__` or module-level constants for TTL values |

---

### Step 3 — Consolidate findings

Collect all findings from agents 2, 3, and 4. Group by severity:

- **Critical** (must fix before merge): correctness bugs, data loss risk, crash on cache failure
- **Important** (fix now if time allows): design inconsistencies, missing test coverage of error paths
- **Minor** (log as follow-up): style nitpicks, naming preferences

---

### Step 4 — Fix high-severity issues directly

Fix any critical or important issues in-place without waiting for another approval cycle. The skill is explicit: *fix obvious high-severity issues directly unless the user has asked to stop after review.*

---

### Step 5 — Surface remaining risks

Report to the user:

- Any unresolved design trade-offs (e.g., "cache-aside vs write-through was left as cache-aside — revisit if write latency becomes an issue")
- Follow-up work items (e.g., monitoring/metrics on cache hit rate, eviction policy tuning)
- Open questions that couldn't be resolved from the code alone

---

## Summary of Subagents

| Order | Agent | Parallelism | Rationale |
|-------|-------|-------------|-----------|
| 1st | `code-simplifier` (1 agent, all 3 files) | Sequential — must finish before reviewers | Applies edits directly; reviewers need to see final simplified code |
| 2nd | `code-reviewer` — Correctness | Parallel with agents 3 & 4 | Independent read-only review, different risk focus |
| 2nd | `code-reviewer` — Simplicity & Design | Parallel with agents 2 & 4 | Independent read-only review, different risk focus |
| 2nd | `code-reviewer` — Conventions | Parallel with agents 2 & 3 | Independent read-only review, different risk focus |

**Total subagents: 4** (1 sequential, then 3 parallel)
