## Eval Prompt

Run only Phase 1 Intake for coding-task-workflow with `ISSUE: 42`. I also typed `WORK_ITEM: maybe clean up auth later`, but the GitHub issue body actually describes a CSV import bug that silently drops rows. Tell me what Intake should do and what it should use as the work item.

Write these artifacts:
1. transcript.md with sections: `## Eval Prompt`, `## Files Read`, `## Steps`, `## Final Answer`
2. outputs/final.md containing only the final user-facing answer
3. outputs/user_notes.md containing `None.` if there are no uncertainties/workarounds, otherwise brief notes
4. outputs/metrics.json with JSON object fields: tool_calls, total_tool_calls, total_steps, files_created, errors_encountered, output_chars, transcript_chars

Compute char counts from the files you wrote. Finish once the files are saved.

## Files Read

- /home/adam/dev/personal/skills/skills/coding-task-workflow/SKILL.md
- /home/adam/dev/personal/skills/skills/coding-task-workflow/references/workflow.md
- /home/adam/dev/personal/skills/skills/coding-task-workflow/references/artifact-schema.md
- /home/adam/dev/personal/skills/skills/coding-task-workflow/references/templates/intake.md

## Steps

1. Read SKILL.md to identify the canonical references and non-negotiable Intake authority rules.
2. Read workflow.md for Phase 1 Intake steps and issue-handling requirements.
3. Read artifact-schema.md and the intake template to confirm what Intake records in 00-intake.md.
4. Applied the Phase 1 rules to the prompt conflict between ISSUE 42 and the supplemental WORK_ITEM text.

## Final Answer

The GitHub issue title/body is the authoritative WORK_ITEM, and the supplied issue remains the Phase 1 parent issue; do not create a new parent issue. For Phase 1 Intake, it should fetch `ISSUE: 42`, infer the work item from that issue, treat `WORK_ITEM: maybe clean up auth later` as supplemental only, classify it, generate the slug, create `.coding-workflow/work/<slug>/00-intake.md`, record the issue number/node ID, and add a comment linking the intake artifact. The work item to use is the CSV import bug that silently drops rows, so Intake should classify this as a bug, not an auth cleanup task.
