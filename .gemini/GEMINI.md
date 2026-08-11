# Gemini Instructions

## Universal Rules

### Keep it simple

- Follow you-aint-gonna-need-it (YAGNI) principles to keep things as simple as possible.
- My teammates and I will be reviewing the code you write, so please make it easy to read and understand.

### Verify

- There should NEVER be secrets in code or version control.

### Boundaries

- Never install or add new dependencies without approval.
- Never modify database schemas without approval.
- Never commit secrets.
- Never delete, disable, skip, or weaken failing tests just to make the suite pass.

### Questions are read-only

- If I ask you a question, just answer it and don't edit files. Feel free to offer suggestions when appropriate though.

## Coding preferences

### General

- Take advantage of type safety when a language supports it.
- Never write regression tests for feature deletions.
- Use comments sparingly and only when necessary to explain complex logic.
- Keep comments up to date with code changes.

### TypeScript

- `any` is the enemy; inferred types are our friend.
- Write idiomatic, type-safe TypeScript that Matt Pocock would be proud of.
- I love Vite; prefer it for applicable frontend projects.

## RTK (Rust Token Killer) - Token-Optimized Commands

### Default rule

- Prefix shell commands with `rtk` by default.
- This is mandatory unless one of the exceptions below applies.
- `rtk` reduces context usage by keeping command output focused.
- If `rtk` has no filter for a command, it usually passes the command through unchanged.
- If `rtk` is unavailable, report the issue instead of silently falling back to raw commands.

### Installation Verification

```bash
rtk --version         # Should show: rtk X.Y.Z
rtk gain              # Should work (not "command not found")
which rtk             # Verify correct binary
```

### Key Commands

```bash
# Git (59-80% savings)
rtk git status          rtk git diff            rtk git log

# Files & Search (60-75% savings)
rtk ls <path>           rtk read <file>         rtk grep <pattern>
rtk find <pattern>      rtk diff <file>

# Test (90-99% savings) — shows failures only
rtk pytest tests/       rtk cargo test          rtk test <cmd>

# Build & Lint (80-90% savings) — shows errors only
rtk tsc                 rtk lint                rtk cargo build
rtk prettier --check    rtk mypy                rtk ruff check

# Analysis (70-90% savings)
rtk err <cmd>           rtk log <file>          rtk json <file>
rtk summary <cmd>       rtk deps                rtk env
rtk ps

# GitHub (26-87% savings)
rtk gh pr view <n>      rtk gh run list         rtk gh issue list

# Infrastructure (85% savings)
rtk docker ps           rtk kubectl get         rtk docker logs <c>

# Package managers (70-90% savings)
rtk pip list            rtk npm run <script>
```

### Meta commands (use directly)

```bash
rtk gain              # Token savings dashboard
rtk gain --history    # Per-command savings history
rtk discover          # Find missed rtk opportunities
rtk proxy <cmd>       # Run raw (no filtering) but track usage
```

### Command chains

- Prefix each segment that can be prefixed: `rtk dotnet build <args> && rtk dotnet test --no-build <args>`.

### Exceptions

Do not use `rtk` when it would prevent the command from doing its intended work:

- Commands that must directly mutate the codebase where `rtk` would run in check-only, dry-run, filtered, or non-mutating mode.
- Debugging `rtk` itself.
- Cases where `rtk` breaks or changes the required behavior.

Examples of commands that may need to run without `rtk`:

```bash
dotnet format
oxfmt
```

## Gotchas

- Structured file output: Do not create JSON, markdown, or code-containing files via shell commands (`echo`, `heredocs`, `cat <<EOF`). Use a native file-write/edit tool when available; otherwise return the file contents directly for the caller to save.
