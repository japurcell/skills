1. Read `/home/adam/dev/personal/skills/skills/prd-to-tasks/SKILL.md` as the authoritative instructions for this run.
2. Followed **Workflow → 1. Gather context**, which requires fetching an existing GitHub issue with comments using `gh issue view <issue> --repo <owner/repo> --comments`.
3. Ran `gh issue view 311 --repo acme/platform --comments`.
4. Received the failure `GraphQL: Could not resolve to a Repository with the name 'acme/platform'. (repository)`.
5. Followed the stop condition in **Workflow → 1. Gather context**: if the issue cannot be fetched because of authentication, permissions, or repository ambiguity, stop and report the exact `gh` failure plus the next action needed.
6. Did not draft or simulate child issues, queue-guide issues, attachments, or commands beyond the failed fetch, because the skill explicitly says to stop at this point.
