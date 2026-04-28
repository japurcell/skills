Stopped during context gathering.

Attempted command:
`gh issue view 311 --repo acme/platform --comments`

Exact failure:
`GraphQL: Could not resolve to a Repository with the name 'acme/platform'. (repository)`

Next action needed:
- Verify that `acme/platform` is the correct repository slug.
- Ensure GitHub authentication has access to that repository.
- Rerun once the source issue can be fetched, because this skill requires reading the existing parent issue before drafting child issues.
