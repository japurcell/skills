Do NOT dispatch. The task conflicts with the plan (audit logging deferred to Phase 2), so resolve the conflict first. Follow Build workflow:

- Escalate / get human approval to move audit logging into Phase 1 (or keep it deferred).
- Update the plan and todo tracker to reflect the new decision.
- Clarify task text, success criteria, constraints, and validation commands.
- Invoke addy-context-engineering and subagent-model-selection.
- Only then dispatch an implementer with the lean implementer-prompt (task, success criteria, known constraints, file hints).

Do not pre-read files, draft patches, or dispatch until those steps complete.
