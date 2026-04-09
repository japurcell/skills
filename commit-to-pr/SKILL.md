---
name: commit-to-pr
description: Finalize local repository work into a reviewable pull request: inspect git status, create or reuse the right branch, commit with an issue-linked conventional message, push to origin, and open a PR with `gh pr create`. Use this whenever the user asks to "commit and open a PR", "turn this into a PR", "push and make a pull request", or any equivalent wording even if they do not explicitly mention git/gh command details.
argument-hint: "spec_file: path/to/spec.yaml, issue_numbers: [123, 456], base_branch: main, feature_branch: feat/123-new-feature"
disable-model-invocation: true
---

# Commit to PR

## Inputs

You receive these parameters in your prompt:

- **spec_file** (optional): The path to the spec file that contains the linked Github issue.
- **issue_numbers** (optional): A list of issue numbers to link in the commit message and PR body. If not provided, attempt to extract from `spec_file`.
- **base_branch** (optional, default: "main"): The base branch for the pull request.
- **feature_branch** (optional): The feature branch for the pull request.

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
