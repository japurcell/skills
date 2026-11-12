---
name: accomplishment-report
description: Create a concise Forest Service executive accomplishment report when all work in an ExecPlan is completed, or update its existing report. Use at ExecPlan closeout and when asked to report completed work, agency alignment, and estimated AI-assisted versus human-only time and cost savings.
argument-hint: '[--hourly-wage <amount> <currency>]'
---

# Accomplishment Report

## Confirm scope and completion

1. Activate the `exec-plans` skill before reading a plan. Identify the exact ExecPlan from the task or repository context; ask only if multiple targets remain plausible.
2. Read the plan, repository overview, relevant changes, and acceptance evidence. Confirm every in-scope task and milestone is complete and acceptance is met. Checked boxes do not override unresolved tests, verification, or owner actions. If work remains, explain the gap and stop without generating a report or changing the plan. Reporting does not create a circular completion gate.
3. Write to `<plan-directory>/accomplishment-report.md`. Update an existing report in place and preserve supported human edits, including owner notes, verbatim and separate from generated prose. Identify the plan. If the path belongs to another plan, ask how to resolve the collision. Do not create dated duplicates or modify implementation files.

## Resolve the hourly wage

Accept `--hourly-wage <amount> <currency>` from the invocation, for example `--hourly-wage 100 USD` means USD 100 per human hour. Read the invocation text or host-expanded arguments: `$ARGUMENTS`. The example is syntax only, never a default.

Use a finite, non-negative amount and an explicit currency. The invocation argument takes precedence over rates in project files or earlier context. If the argument is omitted, use a rate the user already supplied for this task. Otherwise, ask directly: "What hourly wage and currency should I use for the labor-cost estimate?" Ask even when the skill was activated automatically at closeout.

The argument is optional at invocation. A missing wage is a clarification to resolve, never a reason to skip the report or mark the reporting task complete. Keep the report pending while awaiting the answer, and continue evidence gathering and drafting that do not depend on the wage. Once the user supplies it, finish and save the report without requiring another invocation. If an explicit argument is invalid or incomplete, ask for its correction rather than falling back to another rate. Finalize cost claims only after the rate and currency are resolved.

## Establish the accomplishment

In plain language, summarize the evidenced outcome and why it matters, retaining meaningful supplied metrics. Attribute the user's contribution accurately and credit collaborators where supported. Distinguish delivered capability from release, deployment, adoption, and measured mission impact. Use the complete application name and its acronym when known. State accomplishments tied to agency priorities only when the causal connection is supported.

Activate the `agency-priorities` skill. Use its attributed USDA strategic goals and Forest Service priorities; retain source date and fiscal-year limits. Treat alignment as analysis, not agency endorsement. If the skill is unavailable, leave alignment unverified rather than inventing priorities. The examples in `assets/example-reports.md` illustrate plain language and meaningful outcomes, not evidence or a required format.

## Estimate labor savings

AI assistance is assumed to have contributed. Never ask whether it was used. Compare the same scope and quality bar:

- Human-only hours cover the work needed without AI. Use measured effort where available; otherwise use defensible, documented estimates. Ask for evidence when no defensible estimate can be made.
- AI-assisted human hours include prompting, oversight, review, testing, corrections, rework, and integration. Do not count agent runtime, wall time, or commit timestamps as human effort.
- Savings = (estimated equivalent human hours without AI - human hours with AI) × the hourly wage resolved above. Use its currency and show the arithmetic.
- Report one defensible numeric estimate in the paragraph. Describe uncertainty separately in brief calculation notes. If savings are zero or negative, state that honestly with an appropriately adapted closing sentence. Mention other AI benefits only when supported.
- This is estimated labor-cost saving, not an actual budget reduction or net AI-cost saving. Exclude AI tool spend from this measure.

## Write and verify

Write one concise, copy-ready paragraph using this template, including only applicable optional parts:

`[Released on MONTH DAY, ][version number ]Full Application Name (ABBR) [accomplishments tied to agency priorities]. AI assistance saved an estimated [hours] development hours, equivalent to approximately [amount] in labor costs.`

Keep the opening order exact: optional release phrase using month and day only, optional known version number, then the full application name and acronym. For example: `Released on March 12, 2.4 Example Application (EA) ...`. Omit inapplicable release dates and unknown versions. Ground accomplishments and any agency-priority connection in evidence. The final AI sentence must say **development hours**. Adapt its savings claim for zero or negative savings; never imply a positive saving unsupported by the calculation.

After the paragraph, add brief supporting calculation notes in the same file: baseline human-only hours and basis, assisted human hours and basis, supplied rate and currency, arithmetic, and material assumptions. Put uncertainty, evidence limits, alignment qualifications, and scope caveats here rather than in the copy-ready paragraph. Verify the opening order and month/day-only release date, and compare retained human text verbatim with the original. Recheck units, arithmetic, claims, completion status, plan identity, and destination. Return the saved path and any material estimation limitation.
