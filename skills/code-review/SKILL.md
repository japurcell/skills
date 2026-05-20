---
name: code-review
description: Conducts a five-axis code review and returns strict JSON findings for correctness, readability, architecture, security, and performance. Use when reviewing staged or unstaged changes, recent commits, pull request diffs, or AI-generated code before merge and the caller needs machine-readable output with file:line references and clear severities.
---

# Code Review

## Overview

Review the requested diff or scope across the same five axes as `addy-code-review-and-quality`, but return one strict JSON object that another model or script can parse without cleanup. Keep every conclusion anchored to the reviewed change.

## When to Use

- Reviewing staged or unstaged changes, recent commits, or a pull request before merge
- Reviewing another agent's code and needing a stable handoff format
- Comparing multiple reviews or feeding the result into another tool
- Not for implementing fixes

## Workflow

1. Invoke `addy-code-review-and-quality`.
2. Review correctness, readability, architecture, security, and performance. Use `addy-security-and-hardening` for security questions and `addy-performance-optimization` for performance questions.
3. Keep only issues introduced by, exposed by, or clearly reachable through the reviewed change. Put uncertainty in `follow_ups`.
4. Emit one finding per root cause. Give every finding 1-3 concrete fix recommendations, with the smallest sensible fix first.
5. Return JSON only. No Markdown fences, headings, or prose before or after the object.

## Specific Techniques

### Output contract

Return exactly one object with these top-level keys in this order. Keep every key and all five axis entries even when empty.

```json
{
  "summary": {
    "decision": "approve",
    "overall_severity": "none",
    "change_scope": "",
    "why": "",
    "verification_gaps": []
  },
  "axes": [
    {
      "axis": "correctness",
      "status": "pass",
      "summary": "",
      "finding_ids": []
    },
    {
      "axis": "readability",
      "status": "pass",
      "summary": "",
      "finding_ids": []
    },
    {
      "axis": "architecture",
      "status": "pass",
      "summary": "",
      "finding_ids": []
    },
    {
      "axis": "security",
      "status": "pass",
      "summary": "",
      "finding_ids": []
    },
    {
      "axis": "performance",
      "status": "pass",
      "summary": "",
      "finding_ids": []
    }
  ],
  "findings": [],
  "positives": [],
  "follow_ups": []
}
```

Use these exact enum values:

- `summary.decision`: `approve`, `comment_only`, `request_changes`
- `summary.overall_severity`: `none`, `suggestion`, `important`, `critical`
- `axes[*].status`: `pass`, `concern`, `not_reviewed`
- `findings[*].severity`: `suggestion`, `important`, `critical`
- `findings[*].axis` and `positives[*].axis`: `correctness`, `readability`, `architecture`, `security`, `performance`

Required item fields:

- Each `findings[*]`: `id`, `severity`, `axis`, `title`, `location`, `problem`, `impact`, `fix_recommendations`
- Each `positives[*]`: `axis`, `location`, `note`

Field rules:

- `change_scope`: one short sentence describing what was reviewed
- `why`: one short sentence explaining the verdict
- `verification_gaps`: missing tests, repros, benchmarks, or context that limited confidence
- `finding_ids`: IDs for that axis, in severity order
- `location`: use `path/to/file.ext:line` or `path/to/file.ext:start-end`; use the nearest relevant line instead of omitting the location
- `problem`, `impact`, and each `fix_recommendations` entry: concise, concrete, and tied to the changed code path
- `fix_recommendations`: 1-3 concrete next changes; never empty. If you cannot suggest a credible fix, move the item to `follow_ups`
- `positives`: optional good choices worth preserving; use `[]` if there are none
- `follow_ups`: open questions, missing context, or checks that should happen before merge but are not confirmed defects

Verdict rules:

- Any `important` or `critical` finding => `request_changes`
- Only `suggestion` findings => `comment_only`
- No findings => `approve`
- `overall_severity` = highest finding severity, or `none` when `findings` is empty

Keep security and performance findings inside this same object; do not emit side reports. If an axis cannot be reviewed honestly, set it to `not_reviewed` and explain why in that axis summary or `follow_ups`. Prefer stable strings and empty arrays over optional nested structures; weaker models and downstream parsers handle fixed shapes more reliably.

## Common Rationalizations

| Rationalization                                          | Reality                                                                                                      |
| -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| "I'll just return markdown bullets; humans can read it." | This skill exists for machine-readable review output. Loose prose is harder to compare, grade, and hand off. |
| "I'll skip empty keys to save tokens."                   | The fixed JSON shape is what keeps weaker models and downstream parsers reliable.                            |
| "This might be a bug, so I'll report it anyway."         | Speculative findings reduce trust. Put uncertainty in `follow_ups` instead.                                  |
| "Security and performance deserve their own formats."    | The caller asked for one structured review. Keep all findings in one schema.                                 |

## Red Flags

- The response contains Markdown headings, bullets, or code fences instead of raw JSON
- One of the five axes is missing or out of order
- A finding has no specific `location`
- A finding is missing `fix_recommendations`, has an empty list, or only contains vague advice like "investigate further"
- The verdict does not match the highest reported severity
- The review includes generic advice that is not tied to the reviewed change

## Verification

After writing the review, confirm:

- [ ] The response is valid JSON with no prose outside the object
- [ ] `summary`, `axes`, `findings`, `positives`, and `follow_ups` are all present
- [ ] All five axes appear exactly once and in the required order
- [ ] Every finding has `id`, `severity`, `axis`, `title`, `location`, `problem`, `impact`, and `fix_recommendations`
- [ ] Every reported defect is tied to a concrete file:line reference in the reviewed change
- [ ] Every reported defect includes at least one concrete fix recommendation
- [ ] `decision` and `overall_severity` match the reported findings
