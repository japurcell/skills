---
name: cli-compression
description: Enforce low-token shell workflows by routing shell commands through `rtk` and using compact RTK modes for files, logs, git, GitHub CLI, and test/build output. Use when running shell commands.
---

# CLI Compression

## Overview

Use **`rtk`** for shell work. `rtk` filters and compresses command output, often saving 60-99% tokens. If a command is supported, RTK rewrites the output. If not, RTK passes it through unchanged.

## When to Use

Use `rtk` before running shell commands in `bash`, a terminal, or an interactive CLI.

## Rules

- Prefix shell commands with `rtk`.
- Do not run plain shell commands when `rtk <command>` would work.
- Prefer compact RTK output over raw output.
- Prefer summaries before full file contents.
- For extra compression, use `--ultra-compact`.
- Do not use `-u` for RTK compression with Git commands; in Git, `-u` means `--set-upstream`.

## Examples

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

## Preferred Patterns

- Use `rtk read <file>` or `rtk smart <file>` before dumping full files.
- Use `rtk` for git inspection, logs, test output, and build output.
- Use `--ultra-compact` when you need more compression.
- Use targeted commands instead of broad raw output.

## Command Inventory

RTK rewrites output for many common tools, including:

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

### Meta commands

```bash
rtk gain              # Token savings dashboard
rtk gain --history    # Per-command savings history
rtk discover          # Find missed RTK opportunities
```

### Global flags

- `--ultra-compact` for extra compression
- `-v` or `--verbose` for filtering details on stderr

## Notes

If RTK does not support a command, it passes the command through unchanged. This means using the `rtk` prefix is safe even when rewrite support is unknown.

## Anti-Patterns

- Running shell commands without `rtk`
- Dumping full files when `rtk read` or `rtk smart` would suffice
- Dumping full `git diff`, logs, or test/build output when a compact form would suffice
- Using `-u` with Git when the goal is RTK compression

## Verification

Before finishing, confirm:

- [ ] Shell commands are prefixed with `rtk`.
- [ ] File inspection uses `rtk read`, `rtk smart`, or another compact RTK form when possible.
- [ ] Git, log, test, and build inspection uses compact RTK output when possible.
- [ ] `--ultra-compact` is used instead of `-u` when extra compression is needed with Git commands.
- [ ] `rtk gain`, `rtk gain --history`, or `rtk discover` are used when measuring or improving compression.
