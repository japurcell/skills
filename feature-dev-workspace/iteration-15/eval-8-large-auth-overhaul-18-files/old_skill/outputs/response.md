# Phase 6 Quality Review — Authentication Overhaul (18 files)

## Understanding

This is a **Deep Track** feature. Eighteen files across three directories (auth/, middleware/, tests/) constitutes large, cross-cutting work with significant security implications. Phase 6 quality review is applied at full depth.

---

## Phase 6 Actions

### Step 1: code-simplifier agent (1 agent)

The skill mandates **exactly one independent code-simplifier subagent**, launched to identify refactoring opportunities across all modified code.

**Scope**: All 18 implementation files. The simplifier is given the full set — auth/ (7 files) + middleware/ (6 files) + tests/ (5 files) — because it reasons about cross-cutting duplication and elegance that spans directory boundaries. Splitting it across multiple agents would fragment its view and miss DRY violations between, say, auth/session.ts and middleware/authGuard.ts.

**Timing**: Launched first (or concurrently with reviewers, since it is read-only analysis). Its output informs consolidation, so fixes are applied after all agents report back.

---

### Step 2: code-reviewer agents (3 agents, in parallel)

For Deep Track, the skill requires **multiple independent code-reviewer agents launched in parallel** with different focuses. For 18 files across three concerns (auth logic, middleware wiring, test coverage), three reviewers is the natural fit:

| Agent | Focus | Files Covered |
|-------|-------|---------------|
| Reviewer 1 | **Correctness & Security** — token validation, session lifecycle, privilege escalation, edge cases | auth/ (7 files) + middleware/ (6 files) |
| Reviewer 2 | **Conventions & DRY** — naming, error handling patterns, code style, abstraction boundaries | all 18 files |
| Reviewer 3 | **Test Quality & Coverage** — red-green-refactor completeness, missing scenarios, test isolation | tests/ (5 files) + auth/ + middleware/ to verify coverage |

**Why 3, not 2 or 4?** Three maps directly to the three natural concern axes of a security-critical overhaul: does it work correctly, is it written consistently, and is it verified adequately. A fourth would create redundant overlap.

---

### Step 3: Conflict Prevention

All four agents (1 simplifier + 3 reviewers) perform **read-only analysis** in parallel. There are no write conflicts during this phase — they can run simultaneously without coordination.

Conflicts are prevented during the subsequent **fix application** step:

1. **Partition by directory**: apply fixes sequentially — auth/ first, middleware/ second, tests/ third. This eliminates overlapping edits to the same file from multiple agents.
2. **Simplifier suggestions first**: apply code-simplifier refactors before reviewer fixes, since simplification may remove lines that a reviewer flagged for a different reason — avoiding fixing dead code.
3. **Consolidate before touching files**: after all agents report, merge their findings into a single prioritized list, deduplicate overlapping suggestions, then execute edits in one pass per file.
4. **High-severity reviewer fixes trump style suggestions**: correctness issues from Reviewer 1 are applied before DRY/convention fixes from Reviewer 2, ensuring security fixes are never accidentally reverted.

---

### Step 4: Consolidation and Fix Application

After agents complete:

1. Merge all findings — simplifier + 3 reviewers — into a single prioritized list
2. Fix **high-severity issues directly** (e.g., token validation gaps, missing error propagation, broken test assertions)
3. Surface remaining medium/low issues and trade-offs for the user
4. Update all todos to reflect resolved and outstanding items

---

## Summary

| Agent | Count | Scope | Parallelism |
|-------|-------|-------|-------------|
| code-simplifier | **1** | All 18 files | Parallel with reviewers |
| code-reviewer (correctness) | **1** | auth/ + middleware/ | Parallel |
| code-reviewer (conventions) | **1** | All 18 files | Parallel |
| code-reviewer (test quality) | **1** | tests/ + verification | Parallel |
| **Total** | **4** | | |

The single simplifier sees everything holistically. The three reviewers each own a non-overlapping *concern* (not necessarily non-overlapping *files*), so their read-only analysis can run in parallel without coordination. Conflicts are prevented by (a) sequencing fix application by directory and (b) applying simplifier changes before reviewer changes.
