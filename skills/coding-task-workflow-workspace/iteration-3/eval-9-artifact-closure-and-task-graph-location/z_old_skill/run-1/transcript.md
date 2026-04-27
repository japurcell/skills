# Eval Transcript

## Eval Prompt
I want the GitHub issue tree to end cleanly. In coding-task-workflow, when should `files.csv`, `sources.md`, and `open-questions` be closed, and where does the Phase 7 task graph YAML live?

## Files Consulted
- `iteration-3/eval-9-artifact-closure-and-task-graph-location/eval_metadata.json`
- `skill-snapshot/SKILL.md`
- `skill-snapshot/references/workflow.md`
- `skill-snapshot/references/artifact-schema.md`
- `skill-snapshot/references/issue-hierarchy.md`
- `skill-snapshot/references/stop-gates.md`

## Notes
- The baseline snapshot stores Phase 3 and Phase 4 ledgers as repo-local artifacts under `.coding-workflow/work/<slug>/...`, not as closable GitHub artifact subissues.
- `open-questions.md` is updated through research and clarification by changing per-question statuses; the baseline docs do not define a separate issue-close action for that file.
- Phase 7 writes `06-task-graph.yaml` as a local artifact, and the issue hierarchy jumps from the plan issue to implementation task sub-issues.
- The final answer follows the baseline snapshot even though the eval prompt reflects a newer issue-body/task-graph model.
