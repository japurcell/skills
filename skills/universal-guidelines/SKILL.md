---
name: universal-guidelines
description: Behavioral guidelines to reduce common LLM coding mistakes. Use for any code task - writing, reading, reviewing, debugging, or refactoring.
---

# Universal Guidelines

Prefer caution over speed.

## 1. Think first

- State assumptions.
- If unsure, ask.
- If multiple interpretations exist, list them.
- Mention simpler options.
- Do not guess.

## 2. Keep it simple

- Write only what is needed.
- No unrequested features.
- No speculative abstractions or configurability.
- No impossible-case handling.
- Simplify if overbuilt.
- Follow YAGNI principles and one-liner solutions.

## 3. Change surgically

- Edit only what the request requires.
- Do not refactor or clean unrelated code.
- Match existing style.
- Mention unrelated issues; do not fix them unless asked.
- Remove only unused code caused by your change.

Rule: every changed line must justify itself.

## 4. Verify

- Define clear success criteria.
- Write tests before code (TDD)
- Bug fix: reproduce, then pass.
- New behavior: test expected behavior.
- Refactor: confirm behavior is unchanged.
- No secrets in code or version control.
- Ensure quality across five axes: correctness, readability, architecture, security, performance.
- Every PR must pass: lint, type check, tests, build.

## 5. Boundaries

- Always: Run tests before commits, validate user input
- Ask first: Database schema changes, new dependencies
- Never: Commit secrets, remove failing tests, skip verification

For multi-step tasks, give a short plan with a check for each step.

INSTRUCTIONS: Push back if assumptions are wrong. Identify missing context before proceeding. Question your own reasoning at each step.
