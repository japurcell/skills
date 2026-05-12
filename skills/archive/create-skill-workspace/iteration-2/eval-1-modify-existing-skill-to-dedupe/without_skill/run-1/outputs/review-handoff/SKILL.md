---
name: review-handoff
description: Helps agents write concise review handoffs that explain what changed, why it matters, what the reviewer should inspect, and what validation ran. Use when handing code changes to a reviewer or teammate who needs fast review context without a full transcript.
---

# Review Handoff

## Overview

Write a short markdown handoff that tells the next reviewer what changed, where to look, what to scrutinize, what validation ran, and whether any real follow-up remains.

## When to Use

- Handoffs for code review, async teammate review, or pause-and-resume review context.
- Not for full specs, implementation plans, or transcript-style session logs.

## Workflow

1. Read the diff and note scope, reviewer-sensitive risk, and validation actually run.
2. Write the handoff as `## Summary`, `## Files to Review`, `## Reviewer Focus`, `## Validation`, and `## Follow-Ups`.
3. Mention each risk, gap, or follow-up once in the clearest section. Use `- None.` when nothing remains.

## Specific Techniques

- In `Files to Review`, use bullets like `path/to/file` - why it matters.
- Put risky logic, migrations, edge cases, rollout concerns, or missing coverage in `Reviewer Focus`.
- In `Validation`, name exact commands or say what is still missing. Never say "normal tests."

## Common Rationalizations

| Rationalization | Reality |
| --- | --- |
| "Repeating the same warning makes the handoff safer." | Repetition hides the real reviewer focus. |

## Red Flags

- The same summary, risk, or follow-up appears more than once.
- Validation uses vague phrases like "normal tests."
- Files are listed without saying why the reviewer should inspect them.

## Verification

- [ ] The handoff uses `Summary`, `Files to Review`, `Reviewer Focus`, `Validation`, and `Follow-Ups` in that order.
- [ ] Files say why they matter, validation names real checks or gaps, and risks/follow-ups are not duplicated.
