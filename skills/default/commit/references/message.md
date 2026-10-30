# Commit message

## First line

Use Conventional Commit format:

```text
<type>: <subject>
```

or:

```text
<type>(<scope>): <subject>
```

Rules:

- Subject is imperative.
- Max 72 characters.
- No trailing period.

## Type

Choose the first matching type:

1. `docs`
2. `test`
3. `fix`
4. `feat`
5. `refactor`
6. `perf`
7. `chore`

Use `fix` only for bug fixes.

## Subject fallback

If no better subject is clear:

1. `update <file-basename>`
2. `update <directory>`
3. `update changed files`

## Body format

```text
<type>(<scope>): <subject>

Summary:
- <what changed>

Rationale:
- <why>

Tests:
- <command or "not run (reason)">

Session: <optional session note>
Refs #123
Fixes #456
Co-authored-by: <name> <email>
```

Rules:

- Keep one blank line after the subject.
- `Summary`, `Rationale`, and `Tests` are required.
- Each required section needs at least one bullet.
- Omit `Session:` if no reliable session data exists.
- Use `Fixes` only when the user explicitly intends this commit to close that specific issue; otherwise use `Refs`.
- Keep issue and co-author trailers contiguous, without blank lines between them.
- Add `Co-authored-by` trailers only for contributors explicitly identified by the user or reliably established by session context.
