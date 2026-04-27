## Eval Prompt
Use the coding-task-workflow skill for this handoff: Gate E already passed for work item `2026-04-23-add-rate-limit-logs`, and I want you to continue directly into Phase 8 right now in this same session. Do not tell me to resume later. Explain exactly what the workflow requires next.

## Files Read
- /home/adam/dev/personal/skills/skills/coding-task-workflow/SKILL.md
- /home/adam/dev/personal/skills/skills/coding-task-workflow/references/workflow.md
- /home/adam/dev/personal/skills/skills/coding-task-workflow/references/stop-gates.md

## Steps
1. Read the skill entrypoint and the canonical workflow and stop-gate references required for a Gate E handoff.
2. Confirmed the non-negotiable rule that Gate E is a mandatory session boundary and Phase 8 must not begin in the same session.
3. Confirmed the required handoff wording and the Phase 8 obligations after resume.
4. Wrote the final user-facing answer and eval artifacts in the run directory.

## Final Answer
Gate E already passed, so do not continue into Phase 8 in the same session. Resume from a fresh session with `coding-task-workflow RESUME=2026-04-23-add-rate-limit-logs`. Phase 8 is the next phase after the resume.

Next, Phase 8 executes `06-task-graph.yaml` in dependency order: for each slice, write a failing test, confirm the failure, write the minimal code to pass it, confirm green, then refactor. Run only tasks whose dependencies are satisfied, parallelize only tasks marked `parallelizable: true`, append each slice to `07-implementation-log.md`, and never add code for a test that has not yet been written.
