**Prompt:**
The source PRD already lives in existing GitHub parent issue #4200, whose body and comments are already in context. Keep issue #4200's metadata untouched, but update #4200's body with task-graph guidance so future implementation agents can figure out the next task from GitHub alone. Do not create any separate tracker issue. The issue describes billing alert policies: first add threshold schema support, then email alerts and Slack alerts can be implemented in parallel, then the alert history UI depends on both delivery paths. Turn this into grabbable GitHub issues.

**Transcript Bullets:**
- Read PRD and comments from issue #4200
- Do not alter issue metadata or create a new tracker
- Update issue body with a clear, actionable task graph
- Sequence: threshold schema → (email, Slack alerts in parallel) → alert history UI
- Specify dependencies for each sub-issue
- Instruct future agents to create sub-issues directly under #4200
- Emphasize updating only the body section for progress
- Ensure guidance is actionable for implementation agents
