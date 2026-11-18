# Make Operations Idempotent

**Principle:** Design operations so they converge to the correct state regardless of how many times they run or where they start from. Every state-mutating operation should answer: "What happens if this runs twice? What happens if the previous run crashed halfway?"

## Why

CLI commands, lifecycle operations, and scheduling loops run in environments where crashes, restarts, and retries are normal. If an operation leaves partial state that causes a different outcome on re-execution, every restart becomes a debugging session.

## The Pattern

- Derive each step from the state that exists. Read current state, compare it with the goal, and apply only the difference. Make leftovers such as locks, temporary files, or partial records recognizable as stale using evidence valid at every possible crash point. For file replacement, write to a temporary path and rename it into place.
- **Self-healing locks:** Merge lockfile with PID-based stale lock detection ensures orphaned locks from crashed processes are automatically recovered.

## The Test

Before shipping a state-mutating operation, ask:

1. What happens if this runs twice in a row?
2. What happens if the previous run crashed at every possible point?
3. Does re-execution converge to the same end state?

If any answer is "it depends on what state was left behind," the operation needs a reconciliation step.

## Relationship to Other Principles

- Extends [principles/fix-root-causes](fix-root-causes.md) by preventing a class of root causes (partial completion) at design time
- Complements [principles/fix-root-causes](fix-root-causes.md) by making state self-correcting rather than requiring debugging
- Distinct from [principles/encode-lessons-in-structure](encode-lessons-in-structure.md) (which is about how to encode rules, not operation design)
- Distinct from [principles/boundary-discipline](boundary-discipline.md) (which is about where validation lives, not convergence behavior)

[Upstream principle-make-operations-idempotent](https://github.com/cursor/plugins/blob/35a90942a7f02e1ebbc2443643179815f2147954/pstack/skills/principle-make-operations-idempotent/SKILL.md)
