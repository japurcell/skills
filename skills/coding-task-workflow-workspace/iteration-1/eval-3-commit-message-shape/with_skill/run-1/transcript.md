## Eval Prompt

Phase 11 is ready for work item `2026-04-23-add-retry-mechanism` on parent issue `#42`. Show the required commit message shape that coding-task-workflow expects, including any trailer formatting rules.

Write these artifacts:
1. transcript.md with sections: `## Eval Prompt`, `## Files Read`, `## Steps`, `## Final Answer`
2. outputs/final.md containing only the final user-facing answer
3. outputs/user_notes.md containing `None.` if there are no uncertainties/workarounds, otherwise brief notes
4. outputs/metrics.json with JSON object fields: tool_calls, total_tool_calls, total_steps, files_created, errors_encountered, output_chars, transcript_chars

Compute char counts from the files you wrote. Finish once the files are saved.

## Files Read

- /home/adam/dev/personal/skills/skills/coding-task-workflow/SKILL.md
- /home/adam/dev/personal/skills/skills/coding-task-workflow/references/workflow.md (lines 311-325)

## Steps

1. Read SKILL.md to confirm the non-negotiable Phase 11 commit-message rule.
2. Read the Phase 11 section in workflow.md to capture the exact subject/body/trailer requirements.
3. Composed the user-facing answer using the required commit-message shape and trailer formatting rule.
4. Wrote the required benchmark artifacts and computed character counts from the saved files.

## Final Answer

Phase 11 requires a conventional-commits subject, a body that references the work-item slug and parent issue, then a blank-line-separated trailer block. Shape:

```text
<type>(<scope>): <subject>

Work item: 2026-04-23-add-retry-mechanism
Parent issue: #42

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

If there is more than one trailer, keep all trailers together in that final trailer block.
