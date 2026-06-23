---
name: commit
description: Creates exactly one safe non-interactive git commit from the current worktree and can push or open a PR. Use whenever the user asks to commit, save, stage, push, or open a PR for current changes—even if they only say "save this", "commit my work", or "push this branch"—and when file selection, branch choice, conventional-commit typing, issue trailers, or PR text must be handled safely.
---

# Commit

## Overview

Create exactly one clean commit from current changes using session history plus git state for scope, rationale, and summary. Push only when the user asks, except a requested PR requires it.

## When to Use

- User wants current changes committed, saved, staged into one commit, pushed, or turned into a PR
- User needs help choosing files, branch, commit type/subject, issue trailers, or PR title/body
- Not for splitting work into multiple commits, rewriting history, or merge/rebase/cherry-pick cleanup

## Workflow

1. **Read session history** for intent, scope, and rationale.

2. **Inspect first.** Run:
   - `git status --short --branch`
   - `git diff --cached`
   - `git diff`
   - `git diff --cached --name-only`
   - `git diff --name-only`
   - `git branch --show-current`
   - `git log --oneline -10`

   Stop if not in a git repo; git author is unset; no changes exist; merge, rebase, or cherry-pick is in progress; conflicts or unmerged paths exist; `HEAD` is detached and no branch will be created; the chosen scope is empty; or a required git command fails.

3. **Parse inputs and PR intent.**
   - `issue_numbers`: accept `#123` or `123`; dedupe, keep order
   - `base_branch`: default `main`
   - `feature_branch`: prefer local branch, else remote tracking, else create it
   - `co_author`: default `Copilot <223556219+Copilot@users.noreply.github.com>`
   - PR is requested when `create_pr=true` or the user explicitly asks
   - Use `Fixes` only when the user explicitly says fix, close, bug, or bugfix; otherwise use `Refs`

4. **Choose the branch.**
   - If `feature_branch` is provided, reuse or create it
   - Otherwise keep the current branch unless it is empty, `base_branch`, `main`, or `master`; then create a branch

5. **Choose commit scope.**
   - If staged changes exist, commit staged changes only
   - Otherwise auto-select, in order:
     1. the only changed file
     2. all changed files under one top-level directory
     3. otherwise stop and ask which files to commit
   - Never include ignored files, generated artifacts, local state, traces, videos, screenshots, storage-state files, or scratch outputs unless the user explicitly asks. If staged changes contain generated-looking artifacts, stop and ask.

6. **Choose type and subject.**
   - Type precedence: `docs`, `test`, `fix`, `feat`, `refactor`, `perf`, else `chore`
   - First line may be `<type>: <subject>` or `<type>(<scope>): <subject>`
   - Subject: imperative, <= 72 characters, no trailing period
   - Subject fallbacks:
     1. `update <file-basename>`
     2. `update <directory>`
     3. `update changed files`

7. **Create a branch name only when needed.**
   - Format: `<type>/<issue>-<slug>` or `<type>/<slug>`
   - `slug` preference:
     1. short summary of selected changes
     2. single selected file basename without extension
     3. `worktree-update-YYYYMMDD`
   - Use lowercase kebab-case

8. **Build the commit message and commit once.**
   - Write the message with a here-doc or temp file and use `git commit -F <file>`
   - Format:

   ```text
   <type>(<scope>): <subject>

   Summary:
   - <what changed>

   Rationale:
   - <why>

   Tests:
   - <command or "not run (reason)">

   Session: 23 min, 87K tokens, 14 files read

   Refs #123
   Refs #456
   Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
   Co-authored-by: Jane <jane@example.com>
   ```

   - Keep the blank line after the subject
   - Keep `Summary`, `Rationale`, and `Tests` in that order with at least one bullet each
   - Keep issue and co-author trailers contiguous with no blank lines between them
   - Include the default Copilot trailer unless the user explicitly declines it
   - Append any extra `co_author` trailer after the Copilot trailer
   - Create exactly one commit. Do not push yet unless required below

9. **Push or open a PR only when requested.**
   - Push only when the user explicitly asks or a PR is requested
   - For PRs, stop if `gh` is missing, unauthenticated, or unavailable for the repo
   - Push first if needed
   - If a PR already exists for the branch, return its URL
   - Otherwise run `gh pr create --base <base_branch> --head <branch> --title ... --body ...` and always pass both `--title` and `--body`

## Specific Techniques

- PR body with issues:

  ```text
  Summary:
  - <commit subject>

  Issues:
  Refs #123
  Fixes #456
  ```

- PR body without issues:

  ```text
  Summary:
  - <commit subject>
  ```

- PR title = commit subject; omit `Issues:` when there are no issue lines
- Return branch name, commit SHA, commit subject, PR URL if created, or exact blocker and next action if stopped
- For dry runs:
  - `status=commit` when ready and `status=stop` when blocked
  - `branch_action=create` when creating a branch, else `branch_action=keep`
  - `push_requested` means the user explicitly asked for push
  - `should_push` means push is actually required

## Common Rationalizations

| Rationalization | Reality |
| --- | --- |
| "Everything changed together, so I should commit it all." | Auto-scope only covers staged, single-file, or one-directory cases. Anything broader needs user confirmation. |
| "The user said push, so staying on main is fine." | Push does not waive branch rules; create a feature branch when current branch is base/main/master. |
| "Generated artifacts are already staged, so they must be intentional." | Generated or local-state files still need explicit confirmation. |
| "I can use `-m` with escaped newlines for speed." | Use `git commit -F <file>` so the exact multi-line message survives intact. |

## Red Flags

- More than one commit is created
- Base branch is reused when a new branch was required
- Unstaged noise is included when staged changes existed
- Generated artifacts are committed without confirmation
- Commit message misses the blank line after the subject, body section order, or correct issue verb

## Verification

- [ ] Exactly one commit was created, or the run stopped before committing
- [ ] Scope followed staged, then single-file, then one-directory selection order
- [ ] Ignored or generated artifacts were excluded unless explicitly requested
- [ ] Branch choice followed `feature_branch`, current-branch, and base-branch rules
- [ ] Commit message used a conventional first line, `Summary`, `Rationale`, `Tests`, and correct issue/co-author trailers
- [ ] Copilot trailer was included unless explicitly declined
- [ ] Push happened only when explicitly requested or required for a requested PR
- [ ] PR creation used explicit `--title` and `--body`, or reported the exact blocker
