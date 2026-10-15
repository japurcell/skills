---
name: review-handoff
description: Helps agents write concise review handoffs for code changes. Use when a reviewer needs a fast summary of what changed, where to look, risks, validation, and follow-ups.
---

# Review Handoff

## Overview

Write a short markdown handoff.

## When to Use

- Review handoffs or async review context.
- Not for specs, plans, or transcript logs.

## Workflow

1. Read the diff and the validation that actually ran.
2. Write the handoff with this exact heading order: `## Summary`, `## Files to Review`, `## Reviewer Focus`, `## Validation`, `## Follow-Ups`.
3. In `Files to Review`, use `path` - why it matters.
4. Put risks, edge cases, rollouts, and missing checks in `Reviewer Focus`.
5. In `Validation`, name exact commands and missing checks. Never say "normal tests."
6. Mention each risk or follow-up once. Use `- None.` in `Follow-Ups` when nothing remains.

## Specific Techniques

- Keep `Summary` to the change and reviewer-facing outcome.
- Omit incidental files; keep risk reasoning in `Reviewer Focus` and command gaps in `Validation`.

## Common Rationalizations

| Rationalization | Reality |
| --- | --- |
| "Repeating the same warning makes the handoff safer." | Repetition hides the real reviewer focus. |

## Red Flags

- The same risk or follow-up appears more than once.
- Validation says "normal tests."

## Verification

- [ ] The handoff uses `Summary`, `Files to Review`, `Reviewer Focus`, `Validation`, and `Follow-Ups` in that order.
- [ ] `Files to Review` says why each file matters, `Validation` names exact commands or clear gaps, and risks/follow-ups appear once.
