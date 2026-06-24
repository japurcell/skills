---
name: universal-guidelines
description: Behavioral guidelines to reduce common LLM coding mistakes. Use for any code task - writing, reading, reviewing, debugging, or refactoring.
---

# Universal Guidelines

## 1. Keep it simple

- Follow YAGNI principles and one-liner solutions.

## 2. Verify

- Write tests before code (TDD)
- No secrets in code or version control.
- Ensure quality across five axes: correctness, readability, architecture, security, performance.
- Every PR must pass: lint, type check, tests, build.

## 3. Boundaries

- Always: Run tests before commits, validate user input
- Ask first: Database schema changes, new dependencies
- Never: Commit secrets, remove failing tests, skip verification

INSTRUCTIONS: Push back if assumptions are wrong. Identify missing context before proceeding. Question your own reasoning at each step.
