# Commit rules

Use after verification passes and commit is enabled.

Commit is enabled unless `commit` is boolean `false` or string `"false"`.

## Gate

Before setting `passes: true`, create exactly one scoped commit for task changes.

Never commit:

- `prd_file`
- `progress_file`
- unrelated changes
- blocked or failing work

Do not amend, reset, rebase, squash, or otherwise rewrite commits during this skill run.

If no committable task-scoped changes exist, block.

## Steps

1. Inspect changes:

   ```bash
   git status --short
   git diff
   git diff --staged
   ```

2. Stage only task-scoped implementation/test/doc/config changes.

3. Confirm staged changes:

   ```bash
   git diff --staged
   git status --short
   ```

4. If `prd_file`, `progress_file`, or unrelated changes are staged, unstage them without discarding work.

5. Commit once using a message file:

   ```bash
   git commit -F <message-file>
   ```

   Do not use multiple commits. Do not use escaped newlines with `-m`.

6. Remove the message file.

## Message

```text
feat: [Task ID] - [Task Title]

- Added [specific changes]
- Verified with [commands/checks]
```

If browser verification was required, include the Playwright command.

## Audit

After committing, run:

```bash
git log -1 --oneline
git show --name-only --format=oneline HEAD
git log --oneline <session_start_head>..HEAD
```

For each session commit, run:

```bash
git show --name-only --format=oneline <hash>
```

Rules:

- Record every session commit in `progress_file`.
- Expected session commits: exactly one.
- Do not omit accidental, corrective, merge, hook-generated, or extra commits.
- If more or fewer than one session commit exists, block.
- If any session commit includes `prd_file`, `progress_file`, unrelated changes, or blocked/failing work, block.

## If blocked

Do not ask follow-up questions.

Record:

- blocker
- intended commit message
- current `git status --short`
- files that would have been committed
- session commits, if any

If any git command fails or times out, read `references/failures.md` and record it in `progress_file`.
