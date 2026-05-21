---
name: cli-compression
description: Prefix every shell command with `rtk`; prefer the most compact RTK form to reduce output and token usage.
---

# CLI Compression

## Rule

Prefix **every shell command** with `rtk`:

```bash
rtk <command>
```

This includes file/search commands, Git/GitHub, build/test/lint, logs, containers, and cluster tools.

Examples:

```bash
rtk grep "pattern" .
rtk find . -name "*.js"
rtk ls -la
rtk cat file.txt
rtk git status
rtk cargo test
rtk docker logs my-container
rtk kubectl get pods
```

## Requirement

Never run raw shell commands without `rtk` unless `rtk` is unavailable or broken.

Wrong:

```bash
grep "pattern" .
find . -name "*.js"
ls -la
git status
cat file.txt
```

Correct:

```bash
rtk grep "pattern" .
rtk find . -name "*.js"
rtk ls -la
rtk git status
rtk cat file.txt
```

## Why

Use `rtk` by default because:

- if RTK supports the command, it compresses output
- if not, it passes the command through unchanged

Uncertainty is **not** a reason to skip `rtk`.

## Compactness

Prefer smaller, targeted output over full dumps:

- use focused/filtered commands
- prefer summaries before full output
- use `--ultra-compact` when helpful

Example:

```bash
rtk --ultra-compact git log -10
```

## File reading

Avoid full file dumps when a compact RTK read is enough.

Prefer:

```bash
rtk read <file>
rtk smart <file>
```

Before:

```bash
rtk cat <file>
```

Use full file output only when needed.

## Git note

Do not use `-u` to mean RTK compression. For RTK compression, use `--ultra-compact`.

Correct:

```bash
rtk --ultra-compact git status
```

`-u` keeps its normal Git meaning, for example:

```bash
rtk git push -u origin branch-name
```

## Common commands

```bash
rtk ls
rtk ls -la
rtk find . -type f
rtk grep "TODO" .
rtk diff a.txt b.txt
rtk wc -l file.txt
rtk head -50 file.txt
rtk tail -50 file.txt
rtk cat notes.txt

rtk git status
rtk git log -10
rtk git diff
rtk git show
rtk git stash list

rtk gh pr view
rtk gh pr checks
rtk gh run list
rtk gh issue view 123

rtk cargo test
rtk cargo build
rtk pytest
rtk go test ./...
rtk npm test
rtk pnpm test
rtk tsc
rtk eslint .
rtk mypy .
rtk ruff check .
rtk dotnet test

rtk docker ps
rtk docker images
rtk docker logs my-container
rtk kubectl get pods
rtk kubectl logs my-pod
```

## Meta commands

Use these to inspect RTK behavior:

```bash
rtk gain
rtk gain --history
rtk discover
```

## Exception

Only skip `rtk` if it is missing or broken in the current environment. If so:

1. state that `rtk` could not be used
2. use the raw command only if necessary

## Checklist

- [ ] Every shell command starts with `rtk`
- [ ] Prefer `rtk read` or `rtk smart` before `rtk cat` when helpful
- [ ] Prefer summaries and filtered output before large output
- [ ] Use `--ultra-compact` when extra compression helps
- [ ] Raw commands are used only if `rtk` is unavailable or broken
