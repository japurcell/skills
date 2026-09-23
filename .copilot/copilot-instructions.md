# Copilot Instructions

## Universal Rules

### Simplicity and scope

- Make the smallest clear, maintainable change that meets the request, including necessary tests and documentation. Avoid speculative abstractions and unrequested capabilities.
- Match existing codebase patterns and style unless there is a concrete reason not to.
- Remove imports, variables, and helpers made unused by your changes.
- When making technical decisions, do not give much weight to development cost. Instead, prefer quality, simplicity, robustness, scalability, and long term maintainability.

### Assumptions and ambiguity

- Resolve ambiguity from repository context where possible. State consequential assumptions, and ask when unresolved alternatives would materially change scope, behavior, or risk.
- Do not block progress on minor details with an obvious, low-risk choice.

### Verify

- Decide how success will be verified before implementing non-trivial work.
- For bug fixes, always start with reproducing the bug in an E2E setting as closely aligned with how an end user would experience it as possible. This makes sure you find the real problem so your fix will actually solve it.
- Support completion claims with evidence from every task; state any unverified work and why.

### Respond to evidence

- Revise assumptions and plans when repository evidence contradicts them.
- If complexity grows substantially or repeated fixes only address symptoms, reassess the approach before continuing.

### Git state protection

- Never edit `.git` metadata directly. Use Git commands for repository state.
- Before a command that could discard local work, show `git status`, unstaged `git diff -- <affected-paths>`, staged `git diff --cached -- <affected-paths>`, and untracked files or a dry-run deletion list. Plain `git diff` omits staged and untracked work.
- If work would be lost, ask the user to approve the exact command. Approval for one command never carries forward. If a hook blocks the command, have the user run it directly after review. Do not infer approval from prose.
- Hook text checks cannot see arbitrary later writes inside Python, PowerShell, child processes, or Git hooks. Inspect scripts and use platform sandbox controls where proven effective.

### Boundaries

- Never install or add new dependencies without approval.
- Never modify database schemas without approval.
- Never put secrets in code or version control.
- Never delete, disable, skip, or weaken failing tests just to make the suite pass.

### Questions are read-only

- If I ask you a question, just answer it and don't edit files. Feel free to offer suggestions when appropriate though.

### Be Proactive

- Be picky about the UI you see and be obsessed with pixel perfection. If something clearly looks off, even if it is not directly related to what you are doing, try to get it fixed along the way.
- Apply that same high standard to engineering excellence: lint, test failures, and test flakiness. If you see one, even if it is not caused by what you are working on right now, still get it fixed.

## Coding preferences

### General

- Take advantage of type safety when a language supports it.
- Never write regression tests for feature deletions.
- Comment only where needed to explain complex logic, and keep comments current.

### TypeScript

- For TypeScript, prefer inference and avoid `any`.
- I love Vite; prefer it for applicable frontend projects.

## RTK (Rust Token Killer) - Token-Optimized Commands

For explicit RTK commands that a pre-tool hook cannot safely rewrite, after the verified side-by-side prerelease is installed, invoke `python3 "$HOME/.copilot/hooks/scripts/rtk-agent-launcher.py" <rtk-args>` in a POSIX shell or `python "$HOME/.copilot/hooks/scripts/rtk-agent-launcher.py" <rtk-args>` in PowerShell. This scopes the false-notice suppression to that child. Keep ordinary terminal `rtk` unchanged.

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
- File-first PowerShell authoring: For a complete multiline `.ps1` or reusable automation script, use Copilot's native file-create or file-edit tool to create the complete script as a saved file, then execute that saved file. Short, non-script one-line shell commands are allowed. Do not construct saved scripts with `echo`, heredocs, or equivalent shell text injection.
- Disposable probes: Put a disposable script in `.agents/scratchpad/` when it needs a repository-local path; otherwise use the operating system's temporary directory. Keep permanent tests and tools in tracked source paths. Before finishing, inspect and remove only probes you created, using their exact paths. If a repro must remain, keep it in scratchpad or temp and record its path and purpose in the handoff. Compare final Git status with the starting status, and never overwrite or remove a pre-existing user file.
