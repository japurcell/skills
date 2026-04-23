The GitHub issue title/body is the authoritative `WORK_ITEM`, and the supplied issue remains the Phase 1 parent issue; do not create a new parent issue.

Intake should:

1. Fetch issue #42 first: `gh issue view 42 --json number,title,body,url,id`.
2. Infer `WORK_ITEM` from that issue's title/body — the CSV import bug that silently drops rows. Your typed `WORK_ITEM: maybe clean up auth later` is supplemental only and is discarded where it conflicts.
3. Classify (here: `bug`), assign slug `YYYY-MM-DD-<kebab-title>`, create `.coding-workflow/work/<slug>/`, and write `00-intake.md`.
4. Keep #42 as the Phase 1 parent issue and record its number and node ID. Do not open a new parent issue.
