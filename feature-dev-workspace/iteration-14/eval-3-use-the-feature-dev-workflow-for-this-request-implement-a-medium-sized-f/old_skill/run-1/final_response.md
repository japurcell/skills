## Understanding

**Track: Standard** — Medium-sized feature, three files, defined scope. Standard track is appropriate.

---

## Phase 2: Codebase Exploration

Two focused code-explorer agents launched in parallel:

- Agent A: traces similar existing features to understand structural patterns, naming, and integration approach
- Agent B: maps the architecture and extension points in the area affected by this feature

After agents return, read the files they identify to ground implementation in source.

---

## Phase 5: Implementation — Workflow Enforcement

The feature-dev workflow enforces one non-negotiable implementation requirement regardless of track:

> "Always use the tdd skill to implement with an explicit red-green-refactor loop."

This means:

1. Write a failing test for the first behavior
2. Implement the minimum code to make it pass
3. Refactor for clarity while keeping tests green
4. Repeat for each behavior slice

The three-file scope does not change this. Each file's changes are driven by red-green-refactor iterations.

---

## Phase 6: Quality Review — Workflow Enforcement

After implementation, the workflow mandates independent code-reviewer subagents on every track:

> "Always run independent code-reviewer agents for quality review on every track."

For Standard track in particular:

> "Standard or Deep: launch multiple independent code-reviewer agents in parallel with different focuses such as simplicity, correctness, and conventions."

**Exact subagent roles launched for this feature:**

| Subagent                     | Focus                                                                                                               |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| `code-reviewer` (instance 1) | **Correctness** — does the implementation handle all edge cases and error paths correctly?                          |
| `code-reviewer` (instance 2) | **Simplicity and conventions** — is the code DRY, readable, and consistent with the three existing files' patterns? |

These run in parallel. Findings are consolidated and high-severity issues are fixed directly.

---

## Summary of Workflow Enforcement Points

| Phase   | Requirement                               | Mechanism                                |
| ------- | ----------------------------------------- | ---------------------------------------- |
| Phase 5 | TDD red-green-refactor                    | tdd skill, mandatory on every track      |
| Phase 6 | Independent code-reviewer agents          | At least one; multiple for Standard/Deep |
| Phase 6 | Parallel review with differentiated focus | Per Standard track specification         |
