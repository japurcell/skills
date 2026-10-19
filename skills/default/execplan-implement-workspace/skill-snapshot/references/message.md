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
Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
Co-authored-by: Jane <jane@example.com>
```

Rules:

- Keep one blank line after the subject.
- `Summary`, `Rationale`, and `Tests` are required.
- Each required section needs at least one bullet.
- Omit `Session:` if no reliable session data exists.
- Use `Fixes` only when the user explicitly says fix, close, bug, or bugfix.
- Otherwise use `Refs`.
- Keep issue trailers and co-author trailers contiguous.
- Do not add blank lines between trailers.
- Add default Copilot co-author unless explicitly declined.
- Add extra co-authors after the Copilot trailer.
