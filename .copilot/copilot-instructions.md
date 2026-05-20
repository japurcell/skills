# Copilot Instructions

## Skills

Always load:

- `cli-compression` - Optimizes shell command output for low-token usage.

**Subagent Dispatch**: When dispatching subagents, always instruct them to load the `cli-compression` skill.

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
