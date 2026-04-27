Phase 3 writes the exploration artifacts into `.coding-workflow/work/<slug>/02-exploration/`, then creates a `phase:exploration` GitHub child issue and attaches it to the Phase 1 parent with `gh api graphql ... addSubIssue`.

- Exploration summary: `.coding-workflow/work/<slug>/02-exploration/summary.md`; the GitHub `phase:exploration` sub-issue links to this artifact.
- `files.csv`: `.coding-workflow/work/<slug>/02-exploration/files.csv`.
- Open questions: `.coding-workflow/work/<slug>/02-exploration/open-questions.md`.

So in this baseline, GitHub gets one exploration sub-issue; the files themselves stay in the repo artifact directory rather than separate GitHub artifact issues.
