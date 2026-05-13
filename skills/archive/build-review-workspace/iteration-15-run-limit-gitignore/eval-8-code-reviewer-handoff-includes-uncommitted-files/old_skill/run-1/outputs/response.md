I’ll read the specified snapshot skill file and answer from that source only.

Build one stable, deduped `review_scope_files` list:

```text
skills/build-review/SKILL.md
skills/build-review/implementer-prompt.md
dist/generated-report.json
notes.txt
```

Include `dist/generated-report.json` because an implementer touched it, even though `dist/` is ignored. Include `notes.txt` because it is uncommitted. Exclude `scratch.tmp` because it is deleted, and exclude `.gitignore` because `.gitignore` files are filtered out by the workflow.

Because the scope has **4 files**, run **one code-reviewer** over the full list. Give that reviewer the exact manager-authored file list, tell them code-simplifier has already returned `DONE`, and instruct them not to recompute or narrow scope. Only after the reviewer returns `DONE` should the manager run the final reviewed tracking sync across the active trackers, record any review verification actually performed, and leave the changes uncommitted and local.
