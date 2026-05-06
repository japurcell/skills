Resolve the plan/task conflict before dispatch. Per the build workflow:

- Invoke addy-context-engineering and subagent-model-selection.
- Reconcile the disagreement (clarify whether audit logging is deferred or must run now); escalate to the human if the plan must change.
- Only when the task is clear and consistent with the plan, dispatch an implementer with implementer-prompt.md and a lean handoff (task + success criteria, known constraints & validation commands, only already-known file hints).
- Do not pre-read large file sets, draft patches, or perform repo discovery before dispatch.
