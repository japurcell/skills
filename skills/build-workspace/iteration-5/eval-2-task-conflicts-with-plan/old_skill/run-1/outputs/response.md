Do NOT dispatch. Follow the build workflow:

- Invoke addy-context-engineering and subagent-model-selection.
- Compare the plan vs the task; detect the conflict (audit logging deferred to Phase 2).
- Pause dispatch — mark the task NEEDS_CONTEXT or BLOCKED and escalate for human clarification (or update the plan to pull audit logging into Phase 1).
- After the decision, prepare a lean handoff (task text, acceptance criteria, constraints, named file hints) and only then dispatch the implementer.
