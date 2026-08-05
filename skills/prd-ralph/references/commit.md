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

If no committable task-scoped changes exist, committing is blocked.

After a successful commit, `prd_file` and `progress_file` may remain modified and uncommitted.

## Steps

Inspect changes:

```bash
git status --short
git diff
git diff --staged
```

Stage only task-scoped implementation/test/doc/config changes.

Confirm staged changes:

```bash
git diff --staged
git status --short
```

If `prd_file`, `progress_file`, or unrelated changes are staged, unstage them before committing.

If any git command fails or times out, read `references/failures.md` and record it in `progress_file`.

## Message

Use this format:

```text
feat: [Task ID] - [Task Title]

- Added [specific changes]
- Verified with [tests, commands, or manual checks]
```

If browser verification was required, include the Playwright command in the verification line.

Commit once using a message file:

```bash
git commit -F <message-file>
```

Do not use multiple commits. Do not use escaped newlines with `-m`.

## Confirm

After committing, run:

```bash
git log -1 --oneline
git show --name-only --format=oneline HEAD
```

Confirm committed files are scoped and exclude `prd_file` and `progress_file`.

Record the commit hash.

Remove the commit message file.

## If blocked

Do not ask follow-up questions. Report:

- blocker
- intended commit message
- current `git status --short`
- files that would have been committed

Record the blocker and any command/tool failure or timeout in `progress_file`.
