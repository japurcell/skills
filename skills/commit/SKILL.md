---
name: commit
description: Create exactly one safe non-interactive git commit from the current worktree. Use when the user asks to commit, save, stage, push, or open a PR for current changes.
---

# Commit

Create **exactly one** clean commit. Push only when explicitly requested, except a requested PR requires a push.

## Use for

- Commit/save/stage current changes
- Push current branch
- Create a PR for current changes
- Choose files, branch, commit message, issue trailers, or PR text

Do **not** use for multi-commit work, history rewriting, merge/rebase/cherry-pick cleanup, or conflict resolution.

## Workflow

1. Read the conversation for intent, scope, rationale, tests, issues, branch, push, and PR requests.

2. Inspect git state before changing anything:

   ```bash
   git status --short --branch
   git diff --cached
   git diff
   git diff --cached --name-only
   git diff --name-only
   git ls-files --others --exclude-standard
   git branch --show-current
   git log --oneline -10
   git config user.name
   git config user.email
   ```

3. Stop and report the blocker if:
   - Not in a git repo
   - Git author name or email is unset
   - No tracked, staged, or untracked non-ignored changes exist
   - Merge, rebase, or cherry-pick is in progress
   - Conflicts or unmerged paths exist
   - `HEAD` is detached and no branch will be created
   - Chosen scope is empty
   - A required command fails unexpectedly

4. Choose branch:
   - If `feature_branch` is provided, reuse a local branch, track a remote branch, or create it.
   - Otherwise keep the current branch unless the branch name is blank, `main`, `master`, or `base_branch`.
   - If a new branch is needed, use `references/branch-names.md`.

5. Choose commit scope:
   - If anything is staged, commit **only staged changes**.
   - Else auto-stage only when there is:
     1. one changed file, or
     2. changed files under one top-level directory.
   - Otherwise stop and ask which files to commit.
   - Never include ignored files, generated artifacts, local state, traces, videos, screenshots, storage-state files, or scratch outputs unless explicitly requested.
   - If such files are already staged, stop and ask.

6. Build the commit message using `references/message.md`.

7. Commit once using a file:

   ```bash
   git commit -F <message-file>
   ```

   Do not use multiple commits. Do not use escaped newlines with `-m`.

8. Push, create PR, or dry run:
   - Push only if the user explicitly asked, or PR creation requires it.
   - For PRs, follow `references/pr.md`.
   - For dry runs, follow `references/dry-run.md`.

9. Final response must include:
   - Branch name
   - Commit SHA
   - Commit subject
   - PR URL, if created
   - Or exact blocker and next action, if stopped

## Inputs

- `issue_numbers`: accept `#123` or `123`; dedupe and keep order.
- `base_branch`: default `main`.
- `feature_branch`: requested branch name.
- `co_author`: extra co-author trailer.
- Default co-author: `Copilot <223556219+Copilot@users.noreply.github.com>`.
- Include default Copilot trailer unless the user explicitly declines it.
- PR requested if user asks for a PR or sets `create_pr=true`.

## Verification

Before final response, verify:

- Exactly one commit was created, or no commit was created.
- Scope followed staged → single file → one directory → ask.
- Generated/local files were excluded unless explicitly requested.
- Branch rules were followed.
- Message has subject, blank line, `Summary`, `Rationale`, `Tests`, applicable issue trailers, and co-author trailers.
- Push happened only when explicitly requested or required for PR.
- PR used explicit title and body.
