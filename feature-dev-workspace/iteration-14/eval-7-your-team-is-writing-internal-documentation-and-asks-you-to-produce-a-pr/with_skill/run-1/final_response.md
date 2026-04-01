# Phase 6 Reference Card — feature-dev Workflow

**Source**: feature-dev workflow, Phase 6 specification
**Audience**: Implementation agents and engineering leads following the workflow literally
**Purpose**: Exact sequence of subagent steps Phase 6 requires

---

## Phase 6: Quality Review — Required Subagent Sequence

> **Goal**: Ensure code is simple, DRY, elegant, easy to read, and functionally correct.

---

### Step 1 — Launch `code-simplifier` subagent _(always required, runs first)_

- **Subagent**: `code-simplifier`
- **Trigger**: Immediately after implementation is complete
- **Mandate**: Identify refactoring opportunities — simplicity, DRY violations, structural clarity
- **Applies to**: Every track (Light, Standard, Deep)
- **Workflow language**: "Always launch an independent code-simplifier subagent to identify refactoring opportunities after implementation."

---

### Step 2 — Launch `code-reviewer` agent(s) _(always required, runs after Step 1)_

- **Subagent**: `code-reviewer` (one or more independent agents)
- **Mandate**: Quality review — correctness, conventions, simplicity
- **Applies to**: Every track (Light, Standard, Deep)
- **Workflow language**: "Always run independent code-reviewer agents for quality review on every track."

**Track-specific minimums**:

| Track    | Minimum                                                                                                                      |
| -------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Light    | At least one independent `code-reviewer` agent                                                                               |
| Standard | Multiple independent `code-reviewer` agents in parallel, with different focuses (e.g., simplicity, correctness, conventions) |
| Deep     | Multiple independent `code-reviewer` agents in parallel, with different focuses                                              |

---

### Step 3 — Consolidate findings and fix _(required, no subagent)_

- Consolidate findings from all agents
- Prioritize issues that matter most
- Fix obvious high-severity issues directly unless the user has asked to stop after review
- Surface remaining risks, trade-offs, and follow-up work clearly

---

## Sequence Diagram

```
Implementation complete
        │
        ▼
 [code-simplifier]        ← Step 1: always, first
        │
        ▼
 [code-reviewer(s)]       ← Step 2: always, after simplifier
  (parallel if Standard/Deep)
        │
        ▼
 Consolidate → Fix → Surface risks   ← Step 3
```

---

## Non-Negotiable Constraints

1. `code-simplifier` and `code-reviewer` are **separate, independent subagents** — they cannot be merged into a single combined pass.
2. `code-simplifier` **always runs before** `code-reviewer` — the order is not flexible.
3. Both steps are marked **"always"** in the workflow — they apply on every track and cannot be dropped.
4. On Standard and Deep tracks, multiple `code-reviewer` agents run **in parallel**, each with a distinct focus — not sequentially as a single agent rerun.

---

_This card describes only what Phase 6 of the feature-dev workflow specifies. No steps have been added from general engineering practice._
