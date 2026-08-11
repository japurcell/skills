# Copilot Instructions

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
- Never remove failing tests.

### Questions are read-only

- If I ask you a question, just answer it and don't edit files. Feel free to offer suggestions when appropriate though.

## Coding preferences

### General

- Take advantage of typesafety when a language supports it.
- Never write regression tests for feature deletions.
- Use comments sparingly and only when necessary to explain complex logic.
- Keep comments up to date with code changes.

### TypeScript

- `any` is the enemy; inferred types are our friend.
- Write TypeScript that Matt Pocock would be proud of.
- I love Vite.

## RTK (Rust Token Killer) - Token-Optimized Commands

When running shell commands, **always prefix with `rtk`**. This reduces context
usage by 60-90% with zero behavior change. If rtk has no filter for a command,
it passes through unchanged — so it is always safe to use.

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
rtk pip list            rtk pnpm install        rtk npm run <script>
```

### Meta commands (use directly)

```bash
rtk gain              # Token savings dashboard
rtk gain --history    # Per-command savings history
rtk discover          # Find missed rtk opportunities
rtk proxy <cmd>       # Run raw (no filtering) but track usage
```

### Rules

- In command chains, prefix each segment: `rtk git add . && rtk git commit -m "msg"`
- For debugging, use raw command without rtk prefix
- `rtk proxy <cmd>` runs command without filtering but tracks usage

## Gotchas

- Structured file output: Do not create JSON, markdown, or code-containing files via shell commands (`echo`, `heredocs`, `cat <<EOF`). Use a native file-write/edit tool when available; otherwise return the file contents directly for the caller to save.
