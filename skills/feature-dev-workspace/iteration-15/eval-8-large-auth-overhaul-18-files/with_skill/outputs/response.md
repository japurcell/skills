# Phase 6 Quality Review — Large Auth Overhaul (18 Files)

## Process Track

This is a **Deep Track** feature: 18 files across three directories with cross-cutting changes to authentication, middleware, and tests. Phase 6 applies the large-change rules throughout.

---

## How Many code-simplifier Agents

The skill's Phase 6 rule is explicit:

> **Large (>5 changed files)**: partition the files into non-overlapping groups (by module, directory, or logical area) and launch one agent per group in parallel.

18 files > 5, so the large path applies. The natural partition is the three directories already established by the implementation:

| Agent | Scope | Files |
|-------|-------|-------|
| Agent 1 | `auth/` | 7 files |
| Agent 2 | `middleware/` | 6 files |
| Agent 3 | `tests/` | 5 files |

**Total: 3 code-simplifier agents launched in parallel.**

---

## File Partitioning

Each directory becomes one agent's exclusive scope. The skill requires the partition to follow a logical boundary — module, directory, or functional area — and the three directories here map perfectly to three coherent areas:

- **auth/** — core authentication logic (token generation, validation, session management, credential handling)
- **middleware/** — request-pipeline concerns (auth guards, rate limiting, token injection, error handling)
- **tests/** — test suite for both areas (unit tests, integration tests, fixtures, mocks)

Each agent receives the full file list for its directory and is instructed to apply simplification edits only within that set.

---

## Preventing Conflicts

The skill is explicit on the conflict rule:

> When running multiple code-simplifier agents, assign each file to exactly one agent — no file may appear in more than one agent's scope, since each agent applies edits directly and overlapping scopes would produce conflicting writes.

Concretely, I enforce this three ways:

1. **Hard boundary by directory path** — the agent prompt for Agent 1 specifies `auth/**` only; Agent 2 specifies `middleware/**` only; Agent 3 specifies `tests/**` only. No file crosses directories, so the partition is automatically non-overlapping.

2. **No shared utility files in any agent's scope** — if any utility file (e.g., `auth/utils.ts` imported by middleware) exists in one directory, it is owned exclusively by the agent for that directory. The middleware agent is instructed *not* to edit files it only imports.

3. **Sequential merge after parallel completion** — I wait for all three agents to finish before reviewing or applying any follow-up fixes. Because each agent wrote to a disjoint file set, their outputs compose cleanly without merge conflicts.

---

## Full Phase 6 Sequence

```
1. Launch 3 code-simplifier agents in parallel (one per directory)
   └─ Agent 1: auth/ (7 files) — DRY, readability, naming, dead code
   └─ Agent 2: middleware/ (6 files) — same mandate
   └─ Agent 3: tests/ (5 files) — same mandate, plus test clarity

2. Launch independent code-reviewer agents in parallel (Deep track → multiple reviewers)
   └─ Reviewer A: correctness & security focus (auth flows, token handling)
   └─ Reviewer B: conventions & simplicity focus (patterns, naming, structure)
   └─ Reviewer C: cross-cutting concerns (how auth/ and middleware/ interact)

3. Consolidate findings from all agents
   └─ Prioritize high-severity issues (security holes, logic errors, test gaps)
   └─ Fix obvious high-severity issues directly

4. Surface remaining risks and follow-up work in the handoff artifact
```

---

## Why This Partitioning

Partitioning by directory rather than by some other scheme (e.g., alphabetical split, random 6-6-6) is preferred because:

- **Logical cohesion**: files within a directory share imports, types, and abstractions, so a single agent can reason about intra-module duplication and naming consistency without stepping on the other agent's domain.
- **Zero cross-boundary edits**: directory boundaries are enforced by the filesystem, making it impossible for an agent to accidentally touch a file in a sibling directory when following its prompt.
- **Reviewable output**: when the simplifier agents finish, their diffs are naturally grouped by the same directories the original implementation was organized around, making human review straightforward.
