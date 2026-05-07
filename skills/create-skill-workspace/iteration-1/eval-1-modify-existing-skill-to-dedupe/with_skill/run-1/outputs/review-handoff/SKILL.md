---
name: review-handoff
description: Helps agents write concise review handoffs that explain what changed, why it matters, what the reviewer should inspect, and what validation ran. Use when handing code changes to a reviewer or teammate who needs fast, decision-ready context without a full transcript.
---

# Review Handoff

## Overview

Write a short review handoff that gives the next reviewer the change summary, the key files, the main risks, the validation status, and any real follow-up.

## When to Use

- Handoffs for code review, async teammate review, or pause-and-resume review context.
- Not for full specs, implementation plans, or transcript-style session logs.

## Workflow

1. Read the diff and note scope, intent, risky areas, and validation actually run.
2. Use this heading order: `## Summary`, `## Files to Review`, `## Reviewer Focus`, `## Validation`, `## Follow-Ups`.
3. Say what still needs checking instead of repeating the same warning in multiple sections.

## Specific Techniques

- Use file bullets like `path` - why it matters.
- Put risky logic, migrations, edge cases, or missing coverage in `Reviewer Focus`.
- Replace vague "normal tests" language with the exact checks already run or still missing.

## Common Rationalizations

| Rationalization | Reality |
| --- | --- |
| "More repetition makes the handoff safer." | Repetition hides the real reviewer focus. |

## Red Flags

- The same summary, risk, or follow-up appears more than once.
- Validation says "normal tests" instead of naming real checks or gaps.
- Files are listed without saying why the reviewer should inspect them.

## Verification

- [ ] The handoff states what changed, where to review, and why it matters.
- [ ] Validation names real checks run or gaps still open.
- [ ] Risks and follow-ups appear once, clearly, without duplicate filler.
