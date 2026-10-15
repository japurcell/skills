Branch decision: keep current branch `fix/rate-limit-backoff` because it is
already a bugfix branch and the skill only creates a new branch when the
current branch is empty or a base branch.

Commit scope: staged files only — `src/rate_limit.py` and
`tests/test_rate_limit.py`. Unstaged `README.md` stays out of the commit.

Commit message: `fix(rate-limit): correct retry backoff and add coverage`
with `Summary`, `Rationale`, `Tests`, `Fixes #456`, and the Copilot
co-author trailer.

Push/PR decision: push was not explicitly requested, but it is required
because the user requested a PR. PR title uses the subject only:
`correct retry backoff and add coverage`.
