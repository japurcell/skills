# 🤖 Copilot CLI Session

> [!NOTE]
> - **Session ID:** `7be1565a-20a1-442a-a1d8-abbc5fd76c62`  
> - **Started:** 6/18/2026, 1:50:32 PM  
> - **Duration:** 50s  
> - **Exported:** 6/18/2026, 1:51:22 PM  

---

<sub>⏱️ 0s</sub>

### ⚠️ Warning

Third-party MCP servers are disabled by your organization's Copilot policy. Only built-in servers are available.

---

<sub>⏱️ 1s</sub>

### 👤 User

Ignore any installed or previously loaded copies of the `commit` skill.
Read and follow only this skill file: /home/adam/dev/personal/skills/skills/commit-workspace/skill-snapshot-current/SKILL.md

Task:
Read the fixture in evals/files/single-file-on-main/input.json and apply the commit skill as a dry run. Do not run git or mutate a repo. Save outputs/result.json and outputs/output.md. result.json must include: status, stop_reason, next_action, branch, branch_action, selected_paths, commit_type, subject, commit_message, push_requested, should_push, pr_requested, should_create_pr, pr_blocker, pr_title, pr_body. Use status=commit or status=stop. Use branch_action=create or branch_action=keep. push_requested means the user explicitly asked to push; should_push means push is actually required.

Constraints:
- Work from repo root: /home/adam/dev/personal/skills
- Input files in the prompt are relative to that repo root.
- This is a dry run. Do not run git or mutate a repo.
- Write only these deliverables under /home/adam/dev/personal/skills/skills/commit-workspace/iteration-2-gemini-3.1-pro-preview/eval-0-plans-one-feature-commit-from-an-unstaged-single/old_skill/run-1/outputs:
  - /home/adam/dev/personal/skills/skills/commit-workspace/iteration-2-gemini-3.1-pro-preview/eval-0-plans-one-feature-commit-from-an-unstaged-single/old_skill/run-1/outputs/result.json
  - /home/adam/dev/personal/skills/skills/commit-workspace/iteration-2-gemini-3.1-pro-preview/eval-0-plans-one-feature-commit-from-an-unstaged-single/old_skill/run-1/outputs/output.md
- `result.json` must be valid JSON and include every field required by the task prompt.
- `output.md` should briefly explain the branch decision, commit scope, commit message, and push/PR decision.
- Do not write anywhere else in the repository.

---

<sub>⏱️ 9s</sub>

### ✅ `bash`

**Read the skill file**

$ cat /home/adam/dev/personal/skills/skills/commit-workspace/skill-snapshot-current/SKILL.md

<details>
<summary>153 lines</summary>

````
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
<shellId: 1 completed with exit code 0>
````

</details>


---

<sub>⏱️ 9s</sub>

### ✅ `bash`

**Read the input file**

$ cat evals/files/single-file-on-main/input.json

```
cat: evals/files/single-file-on-main/input.json: No such file or directory (os error 2)
<shellId: 0 completed with exit code 1>
```


---

<sub>⏱️ 14s</sub>

### ✅ `bash`

**Find input.json**

$ rtk find . -name input.json | grep single-file-on-main

```
skills/commit/evals/files/single-file-on-main/ input.json
<shellId: 2 completed with exit code 0>
```


---

<sub>⏱️ 17s</sub>

### ✅ `bash`

**Read input JSON**

$ rtk cat skills/commit/evals/files/single-file-on-main/input.json

<details>
<summary>33 lines</summary>

```
{
  "user_request": "Please make one clean commit for the invoice CSV export work and push the branch when you're done.",
  "inputs": {
    "issue_numbers": [
      "#123"
    ],
    "base_branch": "main",
    "feature_branch": null,
    "co_author": "Copilot <223556219+Copilot@users.noreply.github.com>",
    "create_pr": false
  },
  "git_state": {
    "in_repo": true,
    "author_configured": true,
    "operation_in_progress": null,
    "conflicts": false,
    "detached_head": false,
    "current_branch": "main",
    "staged_paths": [],
    "unstaged_paths": [
      "src/invoice/export_csv.py"
    ],
    "ignored_paths": [
      ".pytest_cache/v/cache/nodeids"
    ]
  },
  "change_summary": "Adds invoice CSV export support for accountants.",
  "recent_log": [
    "8ac51ba chore: update changelog",
    "fd22aa9 test: cover invoice totals"
  ]
}
<shellId: 3 completed with exit code 0>
```

</details>


---

<sub>⏱️ 30s</sub>

### ✅ `bash`

**Create outputs directory**

$ rtk mkdir -p /home/adam/dev/personal/skills/skills/commit-workspace/iteration-2-gemini-3.1-pro-preview/eval-0-plans-one-feature-commit-from-an-unstaged-single/old_skill/run-1/outputs

```

<shellId: 4 completed with exit code 0>
```


---

<sub>⏱️ 41s</sub>

### ✅ `create`

**create a new file at /home/adam/dev/personal/skills/skills/commit-workspace/iteration-2-gemini-3.1-pro-preview/eval-0-plans-one-feature-commit-from-an-unstaged-single/old_skill/run-1/outputs/result.json.**

/home/adam/dev/personal/skills/skills/commit-workspace/iteration-2-gemini-3.1-pro-preview/eval-0-plans-one-feature-commit-from-an-unstaged-single/old_skill/run-1/outputs/result.json

```
Created file /home/adam/dev/personal/skills/skills/commit-workspace/iteration-2-gemini-3.1-pro-preview/eval-0-plans-one-feature-commit-from-an-unstaged-single/old_skill/run-1/outputs/result.json with 748 characters
```


---

<sub>⏱️ 41s</sub>

### ✅ `create`

**create a new file at /home/adam/dev/personal/skills/skills/commit-workspace/iteration-2-gemini-3.1-pro-preview/eval-0-plans-one-feature-commit-from-an-unstaged-single/old_skill/run-1/outputs/output.md.**

/home/adam/dev/personal/skills/skills/commit-workspace/iteration-2-gemini-3.1-pro-preview/eval-0-plans-one-feature-commit-from-an-unstaged-single/old_skill/run-1/outputs/output.md

```
Created file /home/adam/dev/personal/skills/skills/commit-workspace/iteration-2-gemini-3.1-pro-preview/eval-0-plans-one-feature-commit-from-an-unstaged-single/old_skill/run-1/outputs/output.md with 647 characters
```


---

<sub>⏱️ 49s</sub>

### 💬 Copilot

I've completed the dry run of the `commit` skill using the `evals/files/single-file-on-main/input.json` fixture. 

The evaluation outputs have been saved to the specified directory:
- `result.json` contains the structured output matching the dry run constraints, branching from `main` to `feat/123-invoice-csv-export`, formatting the conventional commit message referencing issue #123, and correctly determining that a push is required.
- `output.md` outlines the branch decision, commit scope, commit message strategy, and push/PR decisions.

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
