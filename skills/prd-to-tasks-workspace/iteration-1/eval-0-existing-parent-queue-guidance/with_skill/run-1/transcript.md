1. Read `/home/adam/dev/personal/skills/skills/prd-to-tasks/SKILL.md` and used it as the authoritative procedure for this dry run.
2. Relied on **Workflow → 1. Gather context**, which says that when the user provides an existing GitHub issue, I must fetch it with comments using `gh issue view <issue> --repo <owner/repo> --comments`.
3. Ran `gh issue view 142 --repo acme/platform --comments`.
4. The command failed with `GraphQL: Could not resolve to a Repository with the name 'acme/platform'. (repository)`.
5. Relied on **Workflow → 1. Gather context** again, which says to stop and report the exact `gh` failure plus the next action needed if the issue cannot be fetched because of authentication, permissions, or repository ambiguity.
6. Wrote a stop-state user-facing response instead of drafting slices or issue bodies.
