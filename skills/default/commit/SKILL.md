---
name: commit
description: Create a well-formed git commit from current changes using session history for rationale and summary. Use when asked to commit, save, or push current changes.
argument-hint: '[<issue_numbers>] [<co_author>]'
---

# Commit

## Inputs

- `issue_numbers`: accept `#123` or `123`; dedupe and keep order.
- `co_author`: explicit co-author attribution or user opt-out. User instructions take precedence over repository attribution rules and agent defaults.
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

7. Build the message using [commit message](references/message.md), write it to a UTF-8 file, and validate it with the bundled script before creating exactly one commit:

   ```bash
   python3 <skill-root>/scripts/validate_message.py <message-file> [options]
   git commit -F <message-file>
   ```

   Before drafting, decide whether the current agent contributed by producing or editing changes in this session. Running Git for changes made by someone else does not establish contribution. Resolve attribution in this order: explicit user instructions, including an identity or opt-out; documented repository policy; then the verified default identity for each contributing agent in [contributor attribution](references/message.md#contributor-attribution). Preserve other reliably established contributors and deduplicate identical identities. Never guess an unknown agent's identity or treat an unknown agent as Codex. If a contributing agent's identity cannot be verified, stop and report that blocker.

   Add one `Co-authored-by: Name <email>` trailer for each resolved contributor. Pass the same identity once through `--co-author 'Name <email>'` for each trailer. Do not pass `--co-author` when the user opts out, repository policy excludes attribution, or no agent contributed. User instructions override conflicting repository policy; repository policy overrides the defaults. Keep Git's author name and email unchanged.

   Pass `--issue <id>` for each verified issue in input order (`#123` or `123`; repeatable), and `--fixes <id>` only for each specific issue the user explicitly intends to close. Fix validation failures before committing the same file; revalidate after every edit. Exit 1 means invalid content; exit 2 means a usage or file-read error. Documented repo conventions still override default-format checks; resolve only those conflicts against the documented conventions. The checker cannot establish imperative wording, correct type, truthful content, session provenance, issue existence, closing intent, or authorship; verify those before passing options.

   Do not use escaped newlines with `-m`.

8. Verify the SHA, committed diff, and remaining staged and unstaged changes. Confirm exactly one commit was created with the selected scope. Report discrepancies and stop before pushing.

9. Push only if the user explicitly asked.

10. Report the branch, commit SHA, and subject, or the exact blocker and next action if stopped.
