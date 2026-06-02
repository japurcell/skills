# Copilot Instructions

## Skills

Immediately load the `cli-compression`, `context-engineering`, `karpathy-guidelines`, and `caveman` skills if not already loaded.

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
