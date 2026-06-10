---
name: commit
description: Create a well-formed git commit from the current working tree using session history for rationale and summary, and can also push the branch or open a PR when asked. Use when the user asks to commit, save, stage, push, or open a PR for current changes and wants safe file selection, branch handling, conventional commit typing, issue trailers, or PR text.
---

# Commit

## Overview

Create exactly one, well-formed commit from the current worktree using session history for rationale and summary. Push only when the user explicitly asks, and open a PR only when requested.

Honor these inputs when present: `issue_numbers`, `base_branch` (default `main`), `feature_branch`, `co_author` (default `Copilot <223556219+Copilot@users.noreply.github.com>`), and `create_pr` (default `false`).

## When to Use

- User asks to commit current changes, save staged work, or turn the worktree into one clean commit
- User also wants the branch pushed or a PR opened after the commit
- Not for splitting work into multiple commits, rewriting history, or handling merge/rebase cleanup

## Workflow

1. **Read session history to identify scope, intent, and rationale.**

2. **Inspect first and stop on blockers.**
   Run:
   - `git status --short --branch`
   - `git diff --cached`
   - `git diff`
   - `git diff --cached --name-only`
   - `git diff --name-only`
   - `git branch --show-current`
   - `git log --oneline -10`

   Stop if any of these are true: not in a git repo; git author is unset; there are no changes; merge, rebase, or cherry-pick is in progress; conflicts or unmerged paths exist; `HEAD` is detached and no branch will be created; the selected diff ends up empty; or a required git command fails.

3. **Parse issues.**
   Parse `issue_numbers` as `#123` or `123`, dedupe them, and preserve order.

   Use `Fixes` only when the user explicitly says fix, close, bug, or bugfix. Otherwise use `Refs`.

4. **Choose the branch.**
   If `feature_branch` is provided, use the local branch if it exists, else the remote tracking branch if it exists, else create it.

   Otherwise keep the current branch unless it is `base_branch`, `main`, `master`, or empty. In those cases create a branch.

5. **Choose the commit scope.**
   If staged changes exist, commit staged changes only.

   Otherwise select, in order:
   1. the only changed file;
   2. all changed files when they all live under one top-level directory;
   3. otherwise stop and ask which files to commit.

   Before staging or selecting files, verify candidates are not ignored. Never include ignored files, tool-generated artifacts, local state files, traces, videos, screenshots, storage-state files, or scratch outputs unless the user explicitly asks to version them. If staged changes include ignored-looking or generated artifacts, stop and ask before committing.

6. **Choose the type and subject.**
   Type order:
   - `docs` for docs-only
   - `test` for tests-only
   - `fix` when the user says fix, bug, or bugfix, or the diff clearly fixes an error
   - `feat` for a clear user-facing capability
   - `refactor` for structural change without a clear behavior change
   - `perf` for performance work
   - otherwise `chore`

   Optionally include a scope if available: `<type>(<scope>): <subject>`.

   Subject = a line written in imperative mood, <= 72 characters, no trailing period.

   Subject fallbacks:
   1. `update <file-basename>`
   2. `update <directory>`
   3. `update changed files`

7. **Create the branch name only when needed.**
   Format:
   - `<type>/<issue>-<slug>` when an issue exists
   - `<type>/<slug>` otherwise

   `slug` preference:
   1. short summary of the selected changes
   2. the single selected file basename without extension
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
   - first line = `<type>(<scope>): <subject>`
   - blank line after the subject
   - no blank lines between trailer lines
   - wrap body lines at 72 characters.
   - include the default Copilot trailer unless the user explicitly asks not to
   - append any extra `co_author` trailer after the Copilot trailer
   - create the commit message with a here-doc or temp file and use `git commit -F <file>` so newlines are literal (avoid -m with \n)

   Create exactly one non-interactive commit. Do not push unless the user explicitly asked for a push or a PR.

9. **Push or open a PR only when requested.**
   A PR is requested when `create_pr=true` or the user explicitly asks for one.

   If push was requested, push the working branch.

   If a PR was requested:
   - pushing becomes required even when the user did not separately ask for `push`;
   - stop if `gh` is missing, unauthenticated, or the repo cannot create GitHub PRs;
   - push the branch first if needed;
   - if a PR already exists for the branch, return its URL;
   - otherwise run `gh pr create --base <base_branch> --head <branch> --title ... --body ...`;
   - always pass both `--title` and `--body`.

## Specific Techniques

### PR body

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

- PR title = commit subject
- For dry runs, use `status=commit` when ready and `status=stop` when blocked
- For dry runs, use `branch_action=create` when making a branch and `branch_action=keep` otherwise
- For dry runs, `push_requested` means the user explicitly asked for push; `should_push` means push is actually required
- Omit `Issues:` when there are no issue lines

### Output

Return:

- branch name
- commit SHA
- commit subject
- PR URL if created
- exact blocker and next action if stopped

## Common Rationalizations

| Rationalization                                                     | Reality                                                                               |
| ------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| "I can just commit everything in the worktree."                     | The skill commits staged changes only, or stops when the unstaged scope is ambiguous. |
| "The screenshot and trace are already staged, so they must belong." | Generated-looking artifacts require confirmation before they are versioned.           |
| "I'll use `Fixes` for every issue trailer."                         | `Fixes` changes issue state; use it only when the user explicitly says fix or close.  |
| "I can open the PR later without pushing."                          | PR creation needs a usable branch state; push first when the PR flow requires it.     |

## Red Flags

- More than one commit is created
- The branch stays on `main` or `master` when a new branch was required
- Unstaged noise is included even though staged changes existed
- Generated artifacts are staged or committed without confirmation
- The commit message misses the blank line before trailers or uses the wrong trailer verb

## Verification

Before finishing, confirm:

- [ ] Exactly one commit was created, or the run stopped before committing
- [ ] The selected file scope followed the staged-then-single-file-then-one-directory order
- [ ] Ignored or generated artifacts were excluded unless the user explicitly asked to version them
- [ ] The branch decision followed `feature_branch`, current branch, and base-branch rules
- [ ] The commit message used `<type>(<scope>): <subject>`, a blank line before trailers, and the right issue verb
- [ ] The Copilot trailer was included unless the user explicitly asked not to
- [ ] Push happened only when explicitly requested or needed for a requested PR
- [ ] PR creation used explicit `--title` and `--body`, or reported the exact blocker
