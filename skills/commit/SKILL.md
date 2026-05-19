---
name: commit
description: "Create 1 git commit from current changes, optionally open a PR."
---

# Commit

## Inputs

- `spec_file` (optional)
- `issue_numbers` (optional)
- `base_branch` (default: `main`)
- `feature_branch` (optional)
- `co_author` (optional, default: `Copilot <223556219+Copilot@users.noreply.github.com>`)
- `create_pr` (default: `false`)

## Context

- !`git status --short --branch`
- !`git diff --cached`
- !`git diff`
- !`git diff --cached --name-only`
- !`git diff --name-only`
- !`git branch --show-current`
- !`git log --oneline -10`

## Goal

- Create exactly 1 commit
- Open PR only if requested

## Stop if

- not in git repo
- git author not configured
- no changes
- merge/rebase/cherry-pick in progress
- conflicts/unmerged paths exist
- `HEAD` detached and no branch will be created
- selected diff is empty
- required git command fails

## PR requested if

- `create_pr=true`
- user explicitly asks for PR

## PR blocked if

- `gh` missing
- `gh` not authenticated
- repo cannot create GitHub PRs

## Algorithm

### 1) Issues

- Parse issues from `issue_numbers` (`#123` or `123`)
- If missing, and `spec_file` is readable, also parse:
  - `#123`
  - `GH-123`
  - GitHub issue URLs
- Deduplicate, preserve order
- Trailer verb:
  - `Fixes` only if user explicitly says fix/close
  - else `Refs`

### 2) Branch

If `feature_branch` provided:

- use local branch if it exists
- else use remote tracking branch if it exists
- else create it

Else:

- if current branch is `base_branch`, `main`, `master`, or empty: create branch
- else use current branch

### 3) Files

If staged changes exist:

- commit staged changes only

Else select, in order:

1. changed files named in `spec_file`
2. only changed file
3. all changed files if all under one top-level directory

Else:

- stop and ask which files to commit

If `spec_file` unreadable/unparseable:

- ignore it

Before selecting files to commit:

- exclude ignored files and paths matched by `.gitignore`

### 4) Type

Choose one:

- `docs`: docs-only
- `test`: tests-only
- `fix`: user says fix/bug/bugfix, or diff clearly fixes error
- `feat`: clearly adds user-facing capability
- `refactor`: restructure without clear behavior change
- `perf`: performance improvement
- else `chore`

### 5) New branch name

Only if creating branch.

- prefix = commit type, else `chore`
- issue = first issue number if any
- slug = first available:
  1. `spec_file` basename without extension
  2. short summary of selected changes
  3. single selected file basename without extension
  4. `worktree-update-YYYYMMDD`
- slug must be lowercase kebab-case

Format:

- `<type>/<issue>-<slug>` if issue exists
- `<type>/<slug>` otherwise

### 6) Subject

Use short action summary.

Fallbacks:

1. `update <file-basename>`
2. `update <directory>`
3. `update changed files`

### 7) Commit message

Format exactly:

```text
<type>: <subject>

Refs #123
Refs #456
Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
Co-authored-by: Jane <jane@example.com>
```

Rules:

- first line = `<type>: <subject>`
- blank line after subject
- blank line before trailers
- no blank lines between trailer lines

### 8) Commit

- create exactly 1 commit
- prefer non-interactive commands
- do not push unless user explicitly asks

### 9) PR

Only if PR requested.

- if PR already exists for branch: return its URL
- else run `gh pr create --base <base_branch> --head <branch> --title ... --body ...`
- always pass both `--title` and `--body`
- title = commit subject
- include issue lines in body if any
- omit `Issues:` if no issues
- if PR creation fails: report failure and next action

PR body with issues:

```text
Summary:
- <commit subject>

Issues:
Refs #123
Fixes #456
```

PR body without issues:

```text
Summary:
- <commit subject>
```

## Output

Return:

- branch name
- commit SHA
- commit subject
- PR URL if created
- next action if stopped

## Guardrails

- never create more than 1 commit
- stop on blocker
- report exact blocker and next action
- never stage or commit ignored files, tool-generated artifacts, local state files, traces, videos, screenshots, storage-state files, or scratch outputs unless the user explicitly asks for them to be versioned
- before staging, verify candidate files are not ignored via git
- if staged changes include ignored-looking or generated artifacts, stop and ask before committing
