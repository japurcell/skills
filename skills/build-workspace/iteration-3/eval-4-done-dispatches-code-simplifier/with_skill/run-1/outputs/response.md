Next: dispatch the code-simplifier (use simplifier-prompt.md) over the four files the implementer touched and do NOT update tracking yet — wait for the code-simplifier to return DONE. Also invoke addy-context-engineering and subagent-model-selection to pick model and prune context.

Give the simplifier:
1) task text & success criteria
2) the implementer’s verification steps/results (commands, logs, pass/fail)
3) known constraints and validation commands
4) the four file paths as file-hints
5) any implementer notes/concerns

When the simplifier returns DONE, then update plan/todo: record verification performed and mark the task done.
