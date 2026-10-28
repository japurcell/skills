---
name: delegate-to-subagents
description: Pursue a long-running goal in a single session by co-ordinating subagents. Use when the user explicitly asks to delegate, spawn,dispatch, or fan out subagents.
---

# Delegate to Subagents

You co-ordinate subagents to pursue a long-running goal. This session will run for a long time.

All work should be done in subagents. Protect your context window.

Use background agents so you can stay in active dialogue with the user.

Communication to and from subagents should be sparse. Communicate primarily through **context pointers**: research notes, previous commits, knowledge base files, and others. Don't duplicate information already available via pointers.

## 1. Define assignments

Run independent work in parallel and dependent work in waves. Serialize edits to shared files.

Avoid duplicate reads and context gathering; consider one exploration subagent when several subagents need the same context.

## 2. Dispatch

Activate the `subagent-model-router` skill for each materially different subtask to determine the most cost-efficient and capable model and reasoning effort for that subtask.

Prohibit nested delegation unless intentionally authorized.

Submit the exact routed model and effort through dispatch controls when dispatching a subagent.

Give every subagent a runtime limit based on the expected effort and complexity of its task to prevent indefinite execution. Treat runtime limits as warning thresholds. When overdue, send a non-interrupting warning and request status, completed work, blockers, and an updated ETA. Keep the subagent running; lateness alone does not justify interruption, cancellation, or replacement.

Keep routing metadata out of subagent prompts. This information is only for your coordination and routing purposes.
