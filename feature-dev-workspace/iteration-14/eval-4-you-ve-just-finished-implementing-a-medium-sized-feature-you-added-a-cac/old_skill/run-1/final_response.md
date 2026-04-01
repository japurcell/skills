## Phase 6 Quality Review Walkthrough

Feature: caching layer added across three service files in a Python web app
Track: **Standard** (medium-sized, multiple files, cross-cutting concern)

---

### What Phase 6 says

The feature-dev workflow specifies for Phase 6:

> "Always run independent code-reviewer agents for quality review on every track."
> "Standard or Deep: launch multiple independent code-reviewer agents in parallel with different focuses such as simplicity, correctness, and conventions."

---

### Subagents launched, in order

**Step 1 — Launch in parallel:**

| Subagent                     | Focus instruction                                                                                                                                                                                                 |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `code-reviewer` (instance 1) | **Correctness**: Review the caching layer for cache invalidation correctness, concurrency safety, and edge cases (e.g., cache miss handling, stale data scenarios, failure modes if the cache is unavailable).    |
| `code-reviewer` (instance 2) | **Simplicity and conventions**: Does the caching implementation introduce unnecessary complexity? Does it match the existing Python patterns across the three service files? Are abstractions at the right level? |

Both agents receive the three modified service files as their review scope. They run independently and in parallel — neither sees the other's output before completing its review.

**Step 2 — Consolidate findings:**

Gather results from both agents. Group issues by severity. Identify overlapping findings (they carry more weight) and focusing-divergent findings (they reveal different risk areas).

**Step 3 — Fix high-severity issues directly:**

Address any correctness or convention issues rated high-severity without waiting for user input, unless the fix introduces a scope expansion or product decision. Surface lower-priority findings for the team.

**Step 4 — Surface remaining risks:**

Report remaining trade-offs, follow-up work, and areas of residual risk.

---

### Why two agents and not one

The workflow's "independent" constraint is intentional: an agent reviewing for correctness will look at different things than one reviewing for simplicity, and a merged review will de-prioritize at least one axis. Running them in parallel means both axes are covered fully without one influencing the other.
