---
name: commit
description: Create a well-formed git commit from current changes using session history for rationale and summary. Use when asked to commit, save, or push current changes.
---

# Commit

## Inputs

- `issue_numbers`: accept `#123` or `123`; dedupe and keep order.
- `co_author`: co-author attribution trailer.
- Documented repo-specific commit conventions override message-format defaults in this skill; retain scope, safety, and execution rules.

## Steps

1. Read the conversation for intent, scope, rationale, tests, and issues.

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
   - No changes exist within the selected scope
   - Conflicts or unmerged paths exist
   - `HEAD` is detached and no branch will be created
   - A required command fails unexpectedly

4. Stage intended changes, including new files (`git add -A`) after confirming scope.

5. Sanity-check newly added files. Stop and report blocker if anything looks random or likely ignored (build artifacts, logs, temp files, scratch outputs).

6. If staging is incomplete or includes unrelated files, ask the user for confirmation before proceeding.

7. Build the message using [commit message](references/message.md), then create exactly one commit using a file:

   ```bash
   git commit -F <message-file>
   ```

   Do not use escaped newlines with `-m`.

8. Verify the SHA, committed diff, and remaining staged and unstaged changes. Confirm exactly one commit was created with the selected scope. Report discrepancies and stop before pushing.

9. Push only if the user explicitly asked.

10. Report the branch, commit SHA, and subject, or the exact blocker and next action if stopped.
