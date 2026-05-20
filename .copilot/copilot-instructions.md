# Copilot Instructions

## Skills

Always load:

- `context-engineering` - Helps load the right context at the right time.
- `karpathy-guidelines` - Guides reading, writing, and refactoring code.
- `concise-response` - Generates clear and brief answers.

**Subagent Dispatch**: When dispatching subagents, always instruct them to load the `context-engineering` skill.

## RTK — Token-Optimized CLI

**rtk** is a CLI proxy that filters and compresses command outputs, saving 60-90% tokens.

### Rule

Always prefix shell commands with `rtk`:

```bash
# Instead of:              Use:
cat file.txt               rtk cat file.txt
grep "pattern" .           rtk grep "pattern" .
ls -la                     rtk ls -la
git status                 rtk git status
git log -10                rtk git log -10
cargo test                 rtk cargo test
docker ps                  rtk docker ps
kubectl get pods           rtk kubectl pods
```

### Meta commands (use directly)

```bash
rtk gain              # Token savings dashboard
rtk gain --history    # Per-command savings history
rtk discover          # Find missed rtk opportunities
rtk proxy <cmd>       # Run raw (no filtering) but track usage
```

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
