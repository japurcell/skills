1. Read `/home/adam/dev/personal/skills/skills/prd-to-tasks-workspace/skill-snapshot/SKILL.md` and treated it as authoritative for the run.
2. Relied on **Workflow → 1. Gather context**, which says to fetch an existing GitHub issue with comments using `gh issue view <issue-number-or-url> --repo <owner/repo> --comments`.
3. Created the assigned run output directory and ran `gh issue view 311 --repo acme/platform --comments`.
4. The command failed with `GraphQL: Could not resolve to a Repository with the name 'acme/platform'. (repository)`.
5. Per **Workflow → 1. Gather context**, stopped immediately and reported the exact `gh` failure plus the next action needed instead of drafting slices, issue bodies, or commands.
