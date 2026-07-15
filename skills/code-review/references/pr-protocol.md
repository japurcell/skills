# PR Protocol

Use this only when reviewing a PR.

## Tool rule

Use `gh` or available PR metadata. Do not rely on the main agent reading GitHub PR/issue pages directly when CLI/API intake is available.

## Intake

Collect:

- PR state, draft status, labels, and review-needed conventions
- title/body
- base/head refs and SHAs
- changed files
- linked issues/specs
- compact summaries of linked issues
- relevant commit history
- related PRs if obvious
- code comments if available

Stop if the PR is:

- closed
- draft
- explicitly marked review-not-needed

## Before commenting

Before posting a PR comment, re-check eligibility.

If still eligible, post with `gh pr comment` using `references/output-formats.md`.
