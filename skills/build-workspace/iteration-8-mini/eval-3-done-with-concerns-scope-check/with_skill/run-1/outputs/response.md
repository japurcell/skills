Read the implementer’s concerns first. If they indicate a correctness or scope mismatch: do NOT update tracking. Instead:
- Assess the concerns and decide whether they require clarification, a fix, or more context.
- Usually re-dispatch an implementer with a lean re-handoff (clear scope, missing constraints, concrete success criteria, verification commands).
- If context is missing, escalate as NEEDS_CONTEXT per rules; if it’s larger reasoning, use a stronger model.
- Only after the concerns are resolved and downstream reviewers return DONE should the manager update the tracker and record verification performed.
