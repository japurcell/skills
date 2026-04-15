# Phase 6 Quality Review: code-simplifier Scaling — Scenario A (3 files) vs Scenario B (12 files)

## Skill Context

The feature-dev skill's Phase 6 Quality Review specifies a **file-count threshold** that governs how many code-simplifier agents to launch:

> - **Small (≤5 changed files)**: launch 1 agent covering all changed files  
> - **Large (>5 changed files)**: partition the files into non-overlapping groups (by module, directory, or logical area) and launch one agent per group **in parallel**

A key invariant applies in both cases: **no file may appear in more than one agent's scope**, because each agent applies edits directly and overlapping scopes would produce conflicting writes.

---

## Scenario A — 3 files changed

**Classification**: Small (3 ≤ 5)

**code-simplifier step**:  
Launch **1 code-simplifier agent** with all three changed files in its scope.

- The single agent sees the full change surface and can reason about cross-file consistency holistically.
- There is no need to partition or coordinate between agents.
- The agent applies its edits directly; since there is only one agent, write conflicts cannot arise.

**Why this is correct**: With only 3 files the change is bounded. A single agent provides sufficient coverage without the overhead of partitioning or parallelism coordination.

---

## Scenario B — 12 files changed across two packages

**Classification**: Large (12 > 5)

**code-simplifier step**:  
**Partition** the 12 files into non-overlapping groups — at minimum two groups aligned with the two packages — and launch **one agent per group in parallel**.

For example, if the packages are `pkg/auth` (6 files) and `pkg/api` (6 files):

| Agent | Scope |
|-------|-------|
| code-simplifier-1 | `pkg/auth` — all 6 files in that package |
| code-simplifier-2 | `pkg/api` — all 6 files in that package |

Both agents run in parallel. Each file is assigned to exactly one agent.

**Why this is correct**: 12 files is beyond the threshold where a single agent can efficiently review and refactor in one pass. Partitioning by package (or logical area / directory) is the natural boundary because changes within a package are more tightly coupled to each other than to the other package. Parallelism reduces wall-clock time. The no-overlap rule ensures agents never edit the same file concurrently, preventing conflicting writes.

---

## Key Difference Summary

| Dimension | Scenario A (3 files) | Scenario B (12 files, 2 packages) |
|---|---|---|
| Threshold classification | Small (≤5) | Large (>5) |
| Number of code-simplifier agents | 1 | 2 (one per package group) |
| Execution mode | Single sequential agent | Parallel agents |
| Partitioning required | No | Yes — by package/logical area |
| No-overlap rule | Trivially satisfied | Must be enforced explicitly |

---

## Why the Threshold Exists

The ≤5/> 5 boundary reflects a pragmatic judgment:

1. **Context window and focus**: A single agent given too many files either misses cross-cutting patterns or exhausts its focus on lower-priority files. Keeping any one agent's scope to a coherent, bounded set produces higher-quality simplifications.
2. **Write safety**: Multiple agents editing the same file concurrently produce conflicting patches. Strict partitioning eliminates this risk entirely.
3. **Speed**: For large changes, parallel agents reduce total wall-clock time versus a single sequential agent working through 12 files.
4. **Natural boundaries**: Packages and directories already encode logical cohesion, making them the default partitioning criterion.
