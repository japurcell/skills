# Commit rules

Commit only when:

- all required verification passed
- selected task was marked `passes: true`
- `commit` is not `false`

## Never commit

Do not commit:

- `prd_file`
- `progress_file`
- unrelated changes
- blocked or failing work

`prd_file` and `progress_file` may remain modified locally, but must not be staged or committed.

## Before committing

Inspect changes:

```bash
git status --short
git diff
git diff --staged
```

Stage only task-scoped code/test/doc changes.

Preserve unrelated user changes.

## Commit message

Use:

```text
feat: [Task ID] - [Task Title]

- Added [specific changes]
- Verified with [tests, commands, or manual checks]
```

If browser verification was required, include the Playwright command in the verification line.

Example:

```text
feat: TASK-4 - Fix dashboard routing

- Added redirect handling and regression test
- Verified with npm test -- dashboard-routing and npx playwright-cli test tests/routing.spec.ts
```

Commit once using a file:

```bash
git commit -F <message-file>
```

Do not use multiple commits. Do not use escaped newlines with `-m`.

If committing is blocked, do not ask follow-up questions. Report:

- blocker
- intended commit message
- current status
