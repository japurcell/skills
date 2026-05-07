---
name: review-handoff
description: Helps agents write concise review handoffs that explain what changed, why it matters, what the reviewer should inspect, and what validation ran. Use when handing code changes to a reviewer or teammate who needs fast review context.
---

# Review Handoff

## Overview

Write a short review handoff that tells the next reviewer what changed, where to look, what to scrutinize, what validation ran, and whether any real follow-up remains.

## When to Use

- Handoffs for code review, async teammate review, or pause-and-resume review context.
- Not for full specs, implementation plans, or transcript-style session logs.

## Workflow

1. Read the diff and note scope, intent, reviewer-sensitive risks, and validation actually run.
2. Structure the handoff as `## Summary`, `## Files to Review`, `## Reviewer Focus`, `## Validation`, and `## Follow-Ups`.
3. Mention each risk, validation gap, or follow-up once in the clearest section instead of repeating it across the handoff.

## Specific Techniques

- In `Files to Review`, use bullets like `path/to/file` - why it matters.
- In `Reviewer Focus`, call out risky logic, migrations, edge cases, missing coverage, or rollout concerns.
- In `Validation`, name the exact checks already run and any important checks still missing.

## Common Rationalizations

| Rationalization | Reality |
| --- | --- |
| "Repeating the same warning in several sections makes the handoff safer." | Repetition dilutes the reviewer focus and hides what actually needs attention. |

## Red Flags

- The same summary, risk, or follow-up appears more than once.
- Validation says "normal tests" instead of naming real checks or gaps.
- Files are listed without saying why the reviewer should inspect them.

## Verification

- [ ] The handoff states what changed, where to review, and why it matters.
- [ ] Validation names real checks run or gaps still open.
- [ ] Risks and follow-ups appear once, clearly, without duplicate filler.
