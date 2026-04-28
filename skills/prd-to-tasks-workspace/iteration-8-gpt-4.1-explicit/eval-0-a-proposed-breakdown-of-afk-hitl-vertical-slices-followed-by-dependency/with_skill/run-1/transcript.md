Eval prompt:
The source PRD already lives in existing GitHub parent issue #4100, whose body and comments are already in context. Keep issue #4100's metadata untouched, and update #4100's body with tracking guidance instead of creating any separate tracker issue. Parent issue summary: saved searches can be created from the search page, alerts can email users when results change, and users need a way to pause alerts without deleting the saved search. Existing issue comments add two constraints: (1) shipping saved-search CRUD before alert delivery is acceptable, and (2) notification preference edits should not block initial saved-search creation. Turn this into independently-grabbable GitHub issues. Because the source is an existing GitHub issue, present the vertical-slice breakdown first, then draft the child issues and managed parent-body tracking guidance that makes clear the executable work remains in issue #4100's sibling direct sub-issues and which AFK task is next.

---

- Present vertical-slice breakdown first
- Draft full child issues using template
- Draft managed parent-body block with <!-- prd-to-tasks:start -->
- No new tracker issue; all work is direct subissues of #4100
- Use placeholders for child issue numbers
- Make next AFK task obvious
