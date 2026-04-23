The GitHub issue title/body is the authoritative WORK_ITEM, and the supplied issue remains the Phase 1 parent issue; do not create a new parent issue.

So Intake should first fetch `#42` with `gh issue view 42 --json number,title,body,url,id`, infer the work item from that issue, and treat `WORK_ITEM: maybe clean up auth later` as supplemental/conflicting context only. It should use the CSV import bug that silently drops rows as the work item, classify it as a `bug`, create the slug and `00-intake.md`, and keep issue `#42` as the parent issue for later sub-issue creation.
