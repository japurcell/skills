# Copilot Instructions

## Skills

Always load:

- `context-engineering` - Helps load the right context at the right time.
- `karpathy-guidelines` - Guides reading, writing, and refactoring code.
- `concise-response` - Generates clear and brief answers.

**Subagent Dispatch**: When dispatching subagents, always instruct them to load the `context-engineering` skill.

## RTK — Token-Optimized CLI

**rtk** is a CLI proxy that filters and compresses command outputs, saving 60-99% tokens. When RTK is installed, supported commands are intercepted transparently; unsupported commands pass through unchanged.

### Rule

**Always** prefix shell commands with `rtk`:

```bash
# Instead of:              Use:
cat file.txt               rtk cat file.txt
grep "pattern" .           rtk grep "pattern" .
ls -la                     rtk ls -la
git status                 rtk git status
git log -10                rtk git log -10
cargo test                 rtk cargo test
docker ps                  rtk docker ps
kubectl get pods           rtk kubectl get pods
```

RTK already rewrites common tool output, including:

- Git: `git status`, `git log`, `git diff`, `git show`, `git stash list`
- GitHub CLI: `gh pr view`, `gh pr checks`, `gh run list`, `gh issue view`
- Graphite: `gt log`, `gt status`
- Rust / Cargo: `cargo test`, `cargo nextest`, `cargo build`, `cargo check`, `cargo clippy`
- JavaScript / TypeScript: `jest`, `vitest`, `tsc`, `eslint`, `pnpm list`, `pnpm outdated`, `next build`, `prisma migrate`, `playwright test`
- Python: `pytest`, `ruff check`, `mypy`, `pip install`
- Go: `go test`, `golangci-lint run`, `go build`
- Ruby: `rspec`, `rubocop`, `rake`
- .NET: `dotnet build`, `dotnet test`, `dotnet format`
- Docker / Kubernetes: `docker ps`, `docker images`, `docker logs`, `docker compose up`, `kubectl get pods`, `kubectl logs`
- Files and search: `ls`, `find`, `grep`, `diff`, `wc`, `cat`, `head`, `tail`

Prefer `rtk read <file>` and `rtk smart <file>` for compact file inspection when you need a summary instead of full contents.

### Meta commands (use directly)

```bash
rtk gain              # Token savings dashboard
rtk gain --history    # Per-command savings history
rtk discover          # Find missed rtk opportunities
rtk proxy <cmd>       # Run unsupported commands with usage tracking
```

### Global flags

- `--ultra-compact` for extra token reduction
- `-v` / `--verbose` for filtering details on stderr

Use `--ultra-compact` rather than `-u` with Git commands; Git uses `-u` for `--set-upstream`.

If a command isn't rewritten, RTK runs it through passthrough unchanged.

## Testing

- Write tests before code (TDD)
- For bugs: write a failing test first, then fix (Prove-It pattern)
- Test hierarchy: unit > integration > e2e (use the lowest level that captures the behavior)
- Run applicable test commands after every change

## Code Quality

- Review across five axes: correctness, readability, architecture, security, performance
- Every PR must pass: lint, type check, tests, build
- No secrets in code or version control

## Implementation

- Build in small, verifiable increments
- Each increment: implement → test → verify
- Never mix formatting changes with behavior changes

## Boundaries

- Always: Run tests before commits, validate user input
- Ask first: Database schema changes, new dependencies
- Never: Commit secrets, remove failing tests, skip verification
