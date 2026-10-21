---
name: commit
description: Create exactly one well-formed git commit from the current working tree using session history for rationale and summary; can also push the branch or open a PR when asked. Use when the user asks to commit, save, stage, push, or open a PR for current changes and wants safe file selection, branch handling, conventional commit typing, issue trailers, or PR text.
---

# Commit

## Overview

Create exactly one non-interactive, well-formed commit from the current worktree using session history for scope, rationale, and summary. Push only when the user explicitly asks, except when a requested PR requires it.

Honor these inputs when present:

- `issue_numbers`
- `base_branch` (default `main`)
- `feature_branch`
- `co_author` (default `Copilot <223556219+Copilot@users.noreply.github.com>`)
- `create_pr` (default `false`)

## When to Use

- User asks to commit current changes, save staged work, or turn the worktree into one clean commit
- User also wants the branch pushed or a PR opened after the commit
- Not for splitting work into multiple commits, rewriting history, or merge/rebase/cherry-pick cleanup

## Workflow

1. **Read session history** to determine intent, scope, and rationale.

2. **Inspect first and stop on blockers.** Run:
   - `git status --short --branch`
   - `git diff --cached`
   - `git diff`
   - `git diff --cached --name-only`
   - `git diff --name-only`
   - `git branch --show-current`
   - `git log --oneline -10`

   Stop if: not in a git repo; git author is unset; no changes exist; merge, rebase, or cherry-pick is in progress; conflicts or unmerged paths exist; `HEAD` is detached and no branch will be created; the chosen commit scope is empty; or any required git command fails.

3. **Parse issues.**
   - Accept `#123` or `123`
   - Deduplicate while preserving order
   - Use `Fixes` only when the user explicitly says fix, close, bug, or bugfix
   - Otherwise use `Refs`

4. **Choose the branch.**
   - If `feature_branch` is provided: use the local branch if it exists, else the remote tracking branch if it exists, else create it
   - Otherwise keep the current branch unless it is empty, `base_branch`, `main`, or `master`; in those cases create a branch

5. **Choose commit scope.**
   - If staged changes exist, commit staged changes only
   - Otherwise select, in order:
     1. the only changed file
     2. all changed files if they are all under one top-level directory
     3. otherwise stop and ask which files to commit

   Before staging or selecting files, verify candidates are not ignored. Never include ignored files, generated artifacts, local state files, traces, videos, screenshots, storage-state files, or scratch outputs unless the user explicitly asks to version them. If staged changes contain generated-looking artifacts, stop and ask.

6. **Choose type and subject.**
   Type precedence:
   - `docs` for docs-only
   - `test` for tests-only
   - `fix` when the user says fix, bug, or bugfix, or the diff clearly fixes an error
   - `feat` for a clear user-facing capability
   - `refactor` for structural change without clear behavior change
   - `perf` for performance work
   - otherwise `chore`

   Optionally use scope: `<type>(<scope>): <subject>`

   Subject rules:
   - imperative mood
   - <= 72 characters
   - no trailing period

   Subject fallbacks:
   1. `update <file-basename>`
   2. `update <directory>`
   3. `update changed files`

7. **Create a branch name only when needed.**
   Format:
   - `<type>/<issue>-<slug>` if an issue exists
   - `<type>/<slug>` otherwise

   `slug` preference:
   1. short summary of selected changes
   2. single selected file basename without extension
   3. `worktree-update-YYYYMMDD`

   Use lowercase kebab-case.

8. **Build the commit message and commit once.**
   Format exactly:

   ```text
   <type>(<scope>): <subject>

   Summary:
   - <what changed>
   - <what changed>
   Rationale:
   - <why>
   - <why>
   Tests:
   - <command or "not run (reason)">
   Refs #123
   Refs #456
   Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
   Co-authored-by: Jane <jane@example.com>
   ```

   Rules:
   - first line is `<type>(<scope>): <subject>`
   - include the blank line after the subject
   - no blank lines between trailer lines
   - wrap body lines at 72 characters
   - include the default Copilot trailer unless the user explicitly asks not to
   - append any extra `co_author` trailer after the Copilot trailer
   - create the message with a here-doc or temp file and use `git commit -F <file>` so newlines are literal; do not use `-m` with `\n`

   Create exactly one commit. Do not push unless explicitly requested or required for a requested PR.

9. **Push or open a PR only when requested.**
   A PR is requested when `create_pr=true` or the user explicitly asks.
   - If push was requested, push the working branch
   - If a PR was requested:
     - pushing is required even if push was not separately requested
     - stop if `gh` is missing, unauthenticated, or PR creation is unavailable for the repo
     - push first if needed
     - if a PR already exists for the branch, return its URL
     - otherwise run `gh pr create --base <base_branch> --head <branch> --title ... --body ...`
     - always pass both `--title` and `--body`

## PR Body

With issues:

```text
Summary:
- <commit subject>
Issues:
Refs #123
Fixes #456
```

Without issues:

```text
Summary:
- <commit subject>
```

Rules:

- PR title = commit subject
- Omit `Issues:` when there are no issue lines

## Dry-Run Status

For dry runs:

- use `status=commit` when ready and `status=stop` when blocked
- use `branch_action=create` when creating a branch, else `branch_action=keep`
- `push_requested` means the user explicitly asked for push
- `should_push` means push is actually required

## Output

Return:

- branch name
- commit SHA
- commit subject
- PR URL if created
- exact blocker and next action if stopped

## Red Flags

- More than one commit is created
- The branch remains on `main` or `master` when a new branch was required
- Unstaged noise is included when staged changes existed
- Generated artifacts are committed without confirmation
- The commit message misses the blank line after the subject or uses the wrong issue verb

## Verification

Before finishing, confirm:

- [ ] Exactly one commit was created, or the run stopped before committing
- [ ] Scope followed staged, then single-file, then one-directory selection order
- [ ] Ignored or generated artifacts were excluded unless explicitly requested
- [ ] Branch choice followed `feature_branch`, current branch, and base-branch rules
- [ ] Commit message used `<type>(<scope>): <subject>`, included the blank line after the subject, and used the correct issue verb
- [ ] Copilot trailer was included unless explicitly declined
- [ ] Push happened only when explicitly requested or required for a requested PR
- [ ] PR creation used explicit `--title` and `--body`, or reported the exact blocker
