# Pull requests

Create a PR only when explicitly requested.

## Preconditions

Stop if:

- `gh` is missing
- `gh` is unauthenticated
- `gh` cannot access the repo
- Branch cannot be pushed

## Steps

1. Push the branch if needed.
2. Check whether a PR already exists for the branch.
3. If it exists, return its URL.
4. Otherwise create one:

   ```bash
   gh pr create --base <base_branch> --head <branch> --title "<title>" --body "<body>"
   ```

Always pass both `--title` and `--body`.

## Title

Use the first line of the commit message described in `references/message.md` as the PR title.

## Body

Same as the commit message body described in `references/message.md` as the PR body.

Omit `Issues:` when there are no issue trailers.
