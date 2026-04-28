Eval prompt:
The source PRD already lives in existing GitHub parent issue #4200, whose body and comments are already in context. Keep issue #4200's metadata untouched, but update #4200's body with task-graph guidance so future implementation agents can figure out the next task from GitHub alone. Do not create any separate tracker issue. The issue describes billing alert policies: first add threshold schema support, then email alerts and Slack alerts can be implemented in parallel, then the alert history UI depends on both delivery paths. Turn this into grabbable GitHub issues.

- PRD already lives in #4200, so #4200 is the parent tracker.
- Do not create a new tracker issue.
- Update #4200's body with a managed task-graph block.
- Slice into thin, vertical, grabbable child issues.
- First: threshold schema support (blocker for all else).
- Then: email alerts and Slack alerts (parallel, both depend on threshold schema).
- Then: alert history UI (blocked by both delivery paths).
- Each child issue must have type, acceptance criteria, verification, blockers, queue position, likely files, and scope.
- Use canonical headings and block shapes from the skill template.
- Do not paraphrase or summarize; use literal required headings.
- Do not use slash-command shorthand for subissue attachment; use gh api graphql commands.
