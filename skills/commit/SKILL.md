---
name: commit
description: "Create one clean git commit from current local changes, push the branch to origin, and optionally open a PR. Use for commit, save, or push requests. Also use for commit+PR requests when create_pr=true or the user explicitly asks for a PR."
---

# Commit

## Inputs

- **spec_file** (optional): Path to a spec file that may contain issue references and target file paths.
- **issue_numbers** (optional): Issue numbers to include; if omitted, try to extract them from `spec_file`.
- **base_branch** (optional, default: `main`): Protected base branch name.
- **feature_branch** (optional): Branch to create or use.
- **co_author** (optional, default: `Copilot <223556219+Copilot@users.noreply.github.com>`): One or more `NAME <EMAIL>` entries separated by newlines; render each as `Co-authored-by: NAME <EMAIL>`.
- **create_pr** (optional, default: `false`): If `true`, open a PR after successful commit and push.

## Context

- Git status: !`git status --short --branch`
- Staged diff: !`git diff --cached`
- Unstaged diff: !`git diff`
- Staged files: !`git diff --cached --name-only`
- Unstaged files: !`git diff --name-only`
- Current branch: !`git branch --show-current`
- Recent commits: !`git log --oneline -10`

## Goal

Create exactly one atomic commit, push its branch to `origin`, optionally open a PR, and return branch, commit, push, and PR details.

## Stop the workflow if

- not inside a Git repository
- Git author identity is not configured
- there are no staged or unstaged changes
- merge, rebase, or cherry-pick is in progress
- there are unmerged paths or index conflicts
- `HEAD` is detached and no new branch will be created
- the selected staged diff is empty
- a required Git command for branching, staging, committing, or pushing fails

## PR creation is requested when

- `create_pr=true`, or
- the user explicitly asks for a PR

## Skip PR creation and report the blocker if PR creation was requested and

- `gh` is not installed
- GitHub CLI is not authenticated
- the repository does not support GitHub PR creation

## Workflow

### 1) Extract issues

- Accept `#123` or bare integers from `issue_numbers`.
- If `issue_numbers` is missing and `spec_file` is readable, extract from:
  - `#123`
  - `GH-123`
  - full GitHub issue URLs
- Deduplicate while preserving first appearance.
- Use `Fixes #N` only if the user explicitly says to fix or close the issue; otherwise use `Refs #N`.

### 2) Choose branch

- If `feature_branch` is provided:
  - switch to it if it exists locally and checkout succeeds cleanly
  - else create a local tracking branch if it exists remotely
  - else create it
- Otherwise:
  - if current branch is `base_branch`, `main`, `master`, or empty, create a new branch
  - else reuse current branch

### 3) Select files

- If staged changes exist, commit staged changes only.
- Otherwise select files in this order:
  1. files explicitly named in `spec_file` and present in current changes
  2. the only changed file, if exactly one file changed
  3. all changed files, if all are under one top-level directory
- Otherwise stop and ask which files to commit.
- If `spec_file` cannot be read or parsed, ignore it; if that makes selection ambiguous, stop and ask.

### 4) Choose commit type

Use:

- `docs` for docs-only changes
- `test` for tests-only changes
- `fix` if the user explicitly says `fix`, `bug`, or `bugfix`, or the diff clearly resolves an error or failing condition
- `feat` if the diff clearly adds a user-facing capability
- `refactor` if the diff restructures code without clear behavior change
- `perf` if the diff clearly improves performance
- otherwise `chore`

### 5) Name branch

When creating a branch:

- prefix: selected commit type when reasonable, else `chore`
- issue: first extracted issue number, if any
- slug, in order:
  1. `spec_file` basename without extension
  2. concise summary of selected changes
  3. single selected file basename without extension
  4. `worktree-update-YYYYMMDD`
- normalize slug to lowercase kebab-case
- format:
  - `<type>/<issue>-<slug>` if an issue exists
  - `<type>/<slug>` otherwise

### 6) Build commit subject

Use a concise conventional subject:

- prefer a short action-oriented summary of selected changes
- if unclear and exactly one file is selected: `update <file-basename>`
- if unclear and all selected files are under one top-level directory: `update <directory>`
- otherwise: `update changed files`

### 7) Create commit message

Rules:

- blank line after subject
- blank line before trailers
- no blank lines between trailer lines

Format exactly:

```text
<type>: <subject>

Refs #123
Refs #456

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
Co-authored-by: Jane <jane@example.com>
```

### 8) Commit and push

- Create exactly one commit.
- Prefer non-interactive commands.
- If `origin` does not exist, create the local commit, skip push and PR creation, and report that no `origin` remote is configured.
- Otherwise push to `origin`.
- Do not force-push unless explicitly requested.

### 9) Open PR

If PR creation was requested and push succeeded:

- if a PR already exists for the branch, return the existing PR URL and do not create a duplicate
- otherwise run `gh pr create --base <base_branch> --head <branch> --title ... --body ...`
- always pass both `--title` and `--body`
- use the commit subject as the PR title
- include issue linkage in the PR body using `Fixes #N` or `Refs #N`
- if there are no issues, omit the `Issues:` section
- if PR creation fails after commit and push succeed, report PR failure and next action

PR body format:

```text
Summary:
- <commit subject>

Issues:
Refs #123
Fixes #456
```

If there are no issues:

```text
Summary:
- <commit subject>
```

## Output

Return:

- branch name
- commit SHA
- commit subject
- push result or exact push error
- PR URL if created
- next action if stopped

## Guardrails

- do not create multiple commits
- stop and report the exact blocker and next action
