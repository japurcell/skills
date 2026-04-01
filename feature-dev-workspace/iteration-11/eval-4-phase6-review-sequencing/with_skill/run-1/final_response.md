# Eval 4 — Phase 6 Quality Review Sequencing

## Context

**Feature completed**: A caching layer added across three service files in a Python web app.  
**Track selected**: Standard — medium-sized feature, touches multiple files, non-trivial correctness surface.

---

## Phase 6: Quality Review — Step by Step

### Step 1: Launch `code-simplifier` (sequential, first)

**Subagent**: `code-simplifier` (skill at `../code-simplifier/SKILL.md`)

**Why first**: The skill requires launching this agent independently _after_ implementation and _before_ code review, so the reviewer agents see any structural improvements the simplifier surfaces.

**What it is told**:

> "Review the three service files where the caching layer was just added. Focus only on the newly written caching code. Look for: unnecessary complexity or nesting in cache-miss/hit branches, redundant abstractions (e.g., wrapper functions that add no clarity), inconsistent naming between the three files (cache key construction, TTL constants, invalidation helpers), and any verbose patterns that can be consolidated without changing behavior. Return a list of specific simplification opportunities with file paths and line references."

**Wait for this agent to complete before proceeding.**

---

### Step 2: Launch two `code-reviewer` agents in parallel

For Standard track the skill requires multiple code-reviewer agents with different focuses. Launch both simultaneously.

---

#### Reviewer A — Correctness & Caching Semantics

**Subagent**: `code-reviewer` (agent at `agents/code-reviewer.md`)

**What it is told**:

> "Review the caching layer added across the three service files. Focus exclusively on correctness and caching semantics: Are cache keys constructed deterministically and without collision risk across callers? Is cache invalidation triggered on all relevant write paths, or are stale reads possible? Are TTL values appropriate and consistent? Are there race conditions under concurrent requests (e.g., cache stampede / thundering herd)? Is sensitive data (PII, auth tokens) accidentally being stored in the cache? Report only issues with confidence ≥ 80. Include file path, line number, and a concrete fix suggestion for each."

---

#### Reviewer B — Conventions, Simplicity & Code Quality

**Subagent**: `code-reviewer` (agent at `agents/code-reviewer.md`)

**What it is told**:

> "Review the caching layer added across the three service files. Focus on adherence to project conventions and overall code quality: Does the caching code follow the Python patterns established elsewhere in the codebase (naming conventions, error handling, import style, logging)? Is there duplicated logic across the three service files that should be extracted into a shared utility? Are cache-related concerns leaking into layers that shouldn't know about them? Is error handling correct when the cache backend is unavailable? Report only issues with confidence ≥ 80, with file path, line number, and fix suggestion."

---

### Step 3: Consolidate and Prioritize

After all three agents return:

1. Merge findings from both reviewers and the simplifier into a single ranked list.
2. Prioritize by severity: correctness bugs (stale reads, race conditions, key collisions) > conventions violations > simplification opportunities.
3. Fix all high-severity issues directly unless the user has asked to stop after review.
4. Surface any remaining risks, deferred trade-offs, or follow-up items clearly in chat or in the handoff artifact.

---

## Execution Order Summary

| Order | Agent               | Run Mode                     | Focus                                       |
| ----- | ------------------- | ---------------------------- | ------------------------------------------- |
| 1     | `code-simplifier`   | Sequential (wait for result) | Refactor opportunities in new caching code  |
| 2a    | `code-reviewer` (A) | Parallel with 2b             | Correctness, cache semantics, security      |
| 2b    | `code-reviewer` (B) | Parallel with 2a             | Conventions, duplication, code quality      |
| 3     | (main agent)        | After all complete           | Consolidate, prioritize, fix, surface risks |

---

## Key Constraints from the Skill

- `code-simplifier` is **always** launched — not optional, not skipped on any track.
- For Standard track, **multiple** code-reviewer agents are required; one is insufficient.
- The two reviewer agents run in **parallel** to save time and keep their perspectives independent.
- `code-simplifier` runs **before** the reviewers so refinements are visible to the review pass.
- High-severity issues are **fixed directly** rather than only reported, unless the user has said otherwise.
