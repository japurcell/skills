---
name: commit
description: "Create one clean git commit from current local changes and push the branch to origin. Use when the user asks to commit, save, or push current work without opening a PR. Do not use for PR creation, rebasing, cherry-picking, amending commits, resolving merge conflicts, or reviewing a PR."
---

# Commit

## Inputs

- **spec_file** (optional): Path to a spec file that may contain issue references and target file paths.
- **issue_numbers** (optional): Issue numbers to include. If omitted, try to extract them from `spec_file`.
- **base_branch** (optional, default: `main`): Protected base branch name.
- **feature_branch** (optional): Branch to create or use.
- **co_author** (optional, default: `Copilot <223556219+Copilot@users.noreply.github.com>`): One or more `NAME <EMAIL>` entries separated by newlines. Render each as `Co-authored-by: NAME <EMAIL>`.

## Context

- Git status: !`git status --short --branch`
- Staged diff: !`git diff --cached`
- Unstaged diff: !`git diff`
- Staged files: !`git diff --cached --name-only`
- Unstaged files: !`git diff --name-only`
- Current branch: !`git branch --show-current`
- Recent commits: !`git log --oneline -10`

## Goal

Create exactly one atomic commit, push its branch to `origin`, and return branch and commit details.

## Stop if

- not inside a Git repository
- Git author identity is not configured
- there are no staged or unstaged changes
- merge, rebase, or cherry-pick is in progress
- there are unmerged paths or index conflicts
- `HEAD` is detached and no new branch will be created
- the selected staged diff is empty
- a required git command fails

## Workflow

### 1) Extract issues

- Accept `#123` or bare integers from `issue_numbers`.
- If `issue_numbers` is missing and `spec_file` is readable, extract:
  - `#123`
  - `GH-123`
  - full GitHub issue URLs
- Deduplicate while preserving first appearance.
- Use `Fixes #N` only if the user explicitly says to fix or close the issue; otherwise use `Refs #N`.

### 2) Choose branch

- If `feature_branch` is provided:
  - if a local branch with that name exists, switch to it only if checkout succeeds without overwriting or conflicting with local changes; otherwise stop
  - else if a remote branch with that name exists, create a local tracking branch
  - else create it
- Otherwise:
  - if current branch is `base_branch`, `main`, `master`, or empty, create a new branch
  - else reuse current branch

### 3) Select files

- If staged changes exist, commit staged changes only.
- Otherwise select files in this order:
  1. files explicitly named in `spec_file` that are present in current changes
  2. the only changed file, if exactly one file changed
  3. all changed files, if they are all under one top-level directory
- Otherwise stop and ask which files to commit.
- If `spec_file` cannot be read or parsed, ignore it; if that makes selection ambiguous, stop and ask.

### 4) Choose commit type

Use these heuristics:

- `docs` if selected changes are docs-only
- `test` if selected changes are tests-only
- `fix` if the user explicitly says `fix`, `bug`, or `bugfix`, or the selected diff clearly resolves an error or failing condition
- `feat` if the selected diff clearly adds a user-facing capability
- `refactor` if the selected diff restructures code without clear behavior change
- `perf` if the selected diff clearly improves performance
- otherwise `chore`

### 5) Name branch

When creating a branch:

- use the selected commit type as the prefix when reasonable; otherwise use `chore`
- use the first extracted issue number, if any
- derive slug from, in order:
  1. `spec_file` basename without extension
  2. a concise summary of selected changes
  3. single selected file basename without extension
  4. `worktree-update-YYYYMMDD`
- normalize to lowercase kebab-case
- format:
  - with issue: `<type>/<issue>-<slug>`
  - without issue: `<type>/<slug>`

### 6) Build commit subject

Create a concise conventional commit subject:

- prefer a short action-oriented summary of selected changes
- if unclear and exactly one file is selected: `update <file-basename>`
- if unclear and all selected files are under one top-level directory: `update <directory>`
- otherwise: `update changed files`

### 7) Create commit message

Format exactly:

```text
<type>: <subject>

Refs #123
Refs #456

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
Co-authored-by: Jane <jane@example.com>
```
