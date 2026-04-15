issue: acme/mobile#233
readiness: needs-clarification
notes:
- Could not access the GitHub repository/issue via gh; spec generation did not run.
- This blocks producing a clean spec handoff from the issue + 7 comments and prevents contradiction resolution.
- High-impact unresolved ambiguity: conflict resolution policy for offline drafts cannot be determined without the issue discussion content.

GitHub command failure:
`gh issue view 233 -R acme/mobile --comments --json number,title,body,labels,assignees,milestone,state,comments,author`

Error:
`GraphQL: Could not resolve to a Repository with the name 'acme/mobile'. (repository)`

Because issue content and comments were not retrievable, no planning-ready spec/checklist could be generated for this baseline run.
