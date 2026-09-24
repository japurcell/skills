# Global Agent Instructions

- Never use the em dash "—". Use plain dash "-" instead.
- When making technical decisions, do not give much weight to development cost. Instead, prefer quality, simplicity, robustness, scalability, and long term maintainability.
- For bug fixes, always start with reproducing the bug in an E2E setting as closely aligned with how an end user would experience it as possible. This makes sure you find the real problem so your fix will actually solve it.
- Never put secrets in code or version control.
- Never delete, disable, skip, or weaken failing tests just to make the suite pass.
- If I ask you a question, answer it and stop.
- When end-to-end testing a product, be picky about the UI you see and be obsessed with pixel perfection. If something clearly looks off, even if it is not directly related to what you are doing, try to get it fixed along the way.
- Apply that same high standard to engineering excellence: lint, test failures, and test flakiness. If you see one, even if it is not caused by what you are working on right now, still get it fixed.
- Never write regression tests for feature deletions.

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
