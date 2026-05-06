Do not update tracking yet. Per the Build workflow, dispatch the code-simplifier next (use simplifier-prompt.md), then the code-reviewer, and only update tracking after code-reviewer returns DONE.

Send the code-simplifier this context:
- task text + success criteria
- known constraints and validation commands
- the four touched file paths (only those files)
- the implementer’s verification context: commands run, tests/outputs showing they passed, short summary of changes and intent, and any concerns
- model selection hint (use subagent-model-selection if needed)

After code-simplifier DONE, run code-reviewer with the same touched files + the verification context; then update tracking and record the verification performed.
