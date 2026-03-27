issue: acme/platform#142
readiness: needs-clarification
notes:
- Could not access the GitHub repository/issue via gh; spec generation did not run.
- Per /issue-to-spec failure handling, execution stopped after reporting the exact command failure.

GitHub command failure:
`gh issue view 142 -R acme/platform --json number,title,body,labels,assignees,milestone,state,comments`

Error:
`GraphQL: Could not resolve to a Repository with the name 'acme/platform'. (repository)`

Because issue content and comments were not retrievable, no planning-ready spec/checklist could be generated for this run.