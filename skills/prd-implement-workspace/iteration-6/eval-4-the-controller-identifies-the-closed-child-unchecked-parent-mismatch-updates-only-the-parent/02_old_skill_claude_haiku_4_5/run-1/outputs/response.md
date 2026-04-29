# PRD #8200 Resume: Closed-child / Unchecked-parent Mismatch Detected

**Status:** Synchronizing parent task-graph before W2 can proceed.

## State mismatch detected

On resume:
- Child issue #8201 **is closed** (from prior execution)
- Parent task-graph line **still shows `[ ]` unchecked**

Per the prd-implement skill rules (section "Reconcile task-graph state before new work"):

> Before launching new implementation or verification work:
> 1. If a child issue is already closed but its parent task-graph line is still `[ ]`, synchronize the parent checkbox first. Do not treat the graph as up to date until that line becomes `[x]`.

This is a closed-child / unchecked-parent mismatch. It must be reconciled before W2 can start.

## Synchronization action

Using `gh-cli`, the controller fetches the latest parent issue body, locates the exact managed task-graph line:

```markdown
- [ ] W1 - #8201 Add webhook retry headers - AFK - blocked by none
```

And updates only the leading checkbox:

```markdown
- [x] W1 - #8201 Add webhook retry headers - AFK - blocked by none
```

The parent issue body is updated with this single change. The rest of the line, all other task-graph lines, and all non-managed content remain exactly as they were.

Controller re-fetches the parent issue to confirm the line now shows `[x]`.

## Wave W2 readiness

W2 contains AFK child issue #8202, "Emit webhook retry metrics," which lists #8201 as its only blocker.

**#8201 status:** ✓ Closed and synchronized in parent task-graph  
**#8202 blocker status:** ✓ Resolved

**Result:** #8202 is now unblocked and ready to proceed.

## Current state

- Child issue #8201 **closed** (from prior run)
- Parent task-graph line for #8201 **now `[x]` checked**
- Parent PRD issue #8200 **remains open**
- Wave W2 **unblocked** and ready to launch

## Next step

Proceed to launch W2 with child issue #8202 "Emit webhook retry metrics" in a TDD subagent.
