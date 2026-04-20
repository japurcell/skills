---
name: commit-to-pr
description: 'Commit local changes and open a GitHub pull request in one workflow: stage files, create or reuse the appropriate branch, write a conventional commit message with issue linkage, push to origin, and open a PR with `gh pr create`. Use this whenever the user asks to commit and open a PR, turn current work into a PR, push and make a pull request, open/raise/cut a PR, get this up for review, put this up for review, wrap this up as a PR, submit as a pull request, or any equivalent phrasing implying "take my local changes and turn them into a PR" — even if they omit git or gh details. Do not use for rebasing, cherry-picking, amending existing commits, resolving merge conflicts, or reviewing an existing PR.'
argument-hint: "spec_file: path/to/spec.yaml, issue_numbers: [123, 456], base_branch: main, feature_branch: feat/123-new-feature"
---

# Commit to PR

## Inputs

You receive these parameters in your prompt:

- **spec_file** (optional): The path to the spec file that contains the linked Github issue.
- **issue_numbers** (optional): A list of issue numbers to link in the commit message and PR body. If not provided, attempt to extract from `spec_file`.
- **base_branch** (optional, default: "main"): The base branch for the pull request.
- **feature_branch** (optional): The feature branch for the pull request.
- **co_author** (optional): One or more `Co-authored-by` trailer lines to attribute collaborators. Each line must follow the format `Co-authored-by: NAME <EMAIL>`. When multiple co-authors are needed, separate each trailer with a newline. If omitted, you (the executing agent) should add your own known co-author identity. If you don't have a known identity, ask the user to provide one.

## Context

- Current git status: !`git status`
- Current git diff (staged and unstaged changes): !`git diff HEAD`
- Current branch: !`git branch --show-current`

## Objective

Convert the current local changes into one clean pull request with minimal user back-and-forth.

## Workflow

Based on the above changes:

1. Load `issue_numbers` and extract, when available:
   - Linked issue numbers (for example `#123`)
   - Feature title or short slug candidate
   - Any acceptance criteria that should influence PR summary text
2. Validate repository readiness:
   - Confirm there are local changes to commit.
   - Confirm `gh` is available and authenticated.
   - If there are no changes, stop and clearly report that there is nothing to commit.
3. Determine branch strategy:
   - If `feature_branch` input is specified, create a new branch with that name.
   - If current branch is `main` or `master`, create a new feature branch.
   - If already on a non-main branch, reuse it unless `feature_branch` input is specified.
   - Branch names should be concise, kebab-case, and derived from the spec/issue context (for example `feat/123-add-invoice-export`).
4. Stage and commit once:
   - Stage all intended changes for this task.
   - Create exactly one atomic commit.
   - Use a conventional commit subject when possible (for example `feat: add invoice export flow`).
   - If issue numbers exist, include `Fixes #<issue>` for each issue number in the commit message body separated by newlines.
   - Always append a `Co-authored-by` trailer block at the end of the commit message. Use the `co_author` input if provided; otherwise use your own known co-author identity. Each trailer line must match the format `Co-authored-by: NAME <EMAIL>`. Separate the trailer block from the preceding body with a blank line.

   **Commit message format:**

   ```
   feat: add invoice export flow

   Fixes #123

   Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
   ```

   When there are multiple co-authors, place each on its own line with no blank lines between them:

   ```
   fix: resolve rate-limit retry logic

   Fixes #456

   Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
   Co-authored-by: Jane <jane@example.com>
   ```

   When there are no linked issues, the trailer still applies:

   ```
   chore: update audit-log schema

   Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
   ```

5. Push to origin:
   - Push the branch with upstream tracking when needed (`-u origin <branch>`).
6. Create the pull request:
   - Use `gh pr create --base <base_branch>` in non-interactive mode (`--title` and `--body`).
   - Include issue linkage in the PR body (`Fixes #<issue>`) for each issue number separated by newlines.
   - Keep PR title aligned with the commit intent; keep body brief and review-friendly.
7. Return a concise execution summary including:
   - Branch name
   - Commit SHA and subject
   - PR URL

## Guardrails

- Prefer non-interactive commands to avoid hanging.
- Do not create multiple commits for this flow.
- Do not rewrite history (no force-push) unless the user explicitly requests it.
- If a required step fails (auth, push, PR creation), stop and report the exact blocker plus next corrective action.

## Execution Mode

You have the capability to call multiple tools in a single response. Complete the full workflow in one response when possible. Avoid unrelated actions.
