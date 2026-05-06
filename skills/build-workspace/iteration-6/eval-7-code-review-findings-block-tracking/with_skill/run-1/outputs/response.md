Answer per the Build workflow:

1. Invoke addy-context-engineering and subagent-model-selection, then re-dispatch the implementer (owner of code fixes) with a lean handoff containing the code-reviewer’s findings for the two correctness issues, exact success criteria, and verification commands. Do not pre-read/patch the repo yourself.

2. After that implementer returns DONE, dispatch the code-simplifier over the touched files, then re-run the code-reviewer.

3. Update tracking only after the final code-reviewer returns plain DONE — then update plan/todo, record verification performed, and mark the task done.
