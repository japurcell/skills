# Eval Transcript

## Eval Prompt
For Phase 3 of coding-task-workflow, explain how the exploration outputs should be stored now. I specifically want to know where the exploration summary, `files.csv`, and open questions live in GitHub.

## Files Consulted
- `iteration-3/eval-5-exploration-artifact-subissues/eval_metadata.json`
- `skill-snapshot/SKILL.md`
- `skill-snapshot/references/workflow.md`
- `skill-snapshot/references/artifact-schema.md`
- `skill-snapshot/references/issue-hierarchy.md`
- `skill-snapshot/README.md`

## Notes
- The baseline snapshot stores Phase 3 artifacts under `.coding-workflow/work/<slug>/02-exploration/`.
- It also creates one GitHub child issue labeled `phase:exploration` and attaches it to the Phase 1 parent with `addSubIssue`.
- In the baseline docs, that GitHub sub-issue links to `02-exploration/summary.md`; `files.csv` and `open-questions.md` remain repo-local artifacts.
- The final answer was grounded in the baseline snapshot even though the eval prompt reflects a newer GitHub-artifact framing.
