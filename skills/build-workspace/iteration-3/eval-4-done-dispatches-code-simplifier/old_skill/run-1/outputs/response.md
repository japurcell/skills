Before updating tracking: read the implementer's DONE report and confirm the claimed verification — which tests were run, full-suite/build status, and that the four listed files are the ones changed and remain uncommitted. Note exactly what verification was actually performed. Then update human-readable docs (plan + todo), record the verification steps/results, and mark the task done in the tracker. Do NOT commit changes.

Context to send to the next subagent (lean handoff):
- task text + acceptance criteria
- known constraints and relevant validation/build/test commands
- explicit file hints (the four files touched)
- the implementer’s report (what changed, tests run & results, any concerns)
- note that changes are uncommitted and where to look.
