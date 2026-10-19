# Commit messages

Use `<type>: <subject>` or `<type>(<scope>): <subject>`. Keep the first line at most 72 characters, with an imperative subject and no trailing period.

Choose the first applicable type: `docs` (documentation only), `test` (tests only), `fix` (bug fix), `feat` (new behavior), `refactor` (behavior-preserving restructuring), `perf` (performance), `chore` (maintenance). For mixed changes, classify the primary purpose; incidental docs or tests do not override it.

If no better subject is clear, use `update <file-basename>`, then `update <directory>`, then `update changed files`.

Use this body, with a blank line after the subject and at least one bullet in each required section:

```text
Summary:
- <what changed>

Rationale:
- <why>

Tests:
- <command or "not run (reason)">
```

Optional trailers follow the body:

- Add `Session: <note>` only with reliable session data.
- Add issue references only for actual issues. Use `Fixes #<id>` only when the user explicitly says fix, close, bug, or bugfix; otherwise use `Refs #<id>`.
- Add `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>` unless explicitly declined. Put any actual extra co-authors after it.
- Keep issue and co-author trailers contiguous, without blank lines. Example identities and issue numbers are placeholders, not attribution.
