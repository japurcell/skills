issue: acme/platform#88
readiness: needs-clarification
notes:
- attempted gh command: gh issue view 88 -R acme/platform --json number,title,body,labels,assignees,milestone,state,comments
- exact gh error: GraphQL: Could not resolve to a Repository with the name 'acme/platform'. (repository)
- next action required: verify repository access/auth (or correct owner/repo) so issue retrieval can proceed.
