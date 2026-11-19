---
name: accomplishment-report
description: Create or update a concise Forest Service executive accomplishment report with agency alignment and estimated AI-assisted labor savings. Use automatically at verified implementation-plan closeout, archival, or final handoff, even without a separate report request; also use when asked for an accomplishment report.
argument-hint: "[--hourly-wage <amount> <currency>]"
---

# Accomplishment Report

## Track the closeout obligation

When participating in implementation closeout, record reporting as a distinct pending item in the existing durable task tracker or authorized closeout checklist. Carry its status, destination, and missing inputs through checkpoints and handoffs. Keep reporting separate from implementation acceptance so it does not create a circular completion gate.

Before archival or a final closeout response, reconcile that item against the actual report at the plan's current location. Loading this skill, checking a box, or archiving the plan is not evidence that the report was saved. Mark reporting complete only after saving and rereading the report and performing the checks below. Otherwise, record and disclose reporting as pending with its blocker and required input or owner action; ask for missing inputs and resume when supplied. Implementation may be accepted while reporting remains pending, but do not describe the entire closeout as complete.

## Confirm scope and completion

1. Identify the exact plan from the task or repository context; ask only if multiple targets remain plausible.
2. Read the plan, repository overview, relevant changes, and acceptance evidence. Confirm every in-scope task and milestone is complete and acceptance is met. Checked boxes do not override unresolved tests, verification, or owner actions. If work remains, explain the gap and stop without generating a report or changing the plan.
3. Write to `<plan-directory>/accomplishment-report.md`. Update an existing report in place and preserve supported human edits, including owner notes, verbatim and separate from generated prose. Identify the plan. If the path belongs to another plan, ask how to resolve the collision. Do not create dated duplicates or modify implementation files.

## Resolve the hourly wage

Accept `--hourly-wage <amount> <currency>` from the invocation, for example `--hourly-wage 100 USD` means USD 100 per human hour. Read the invocation text or host-expanded arguments: `$ARGUMENTS`. The example is syntax only, never a default.

Use a finite, non-negative amount with an explicit currency. Use the invocation rate first and ask for correction if it is invalid or incomplete. When omitted, use a rate the user supplied for this task or ask “What hourly wage and currency should I use for the labor-cost estimate?” This also applies at automatic closeout. While awaiting the answer, keep the report pending and continue independent drafting and evidence gathering. Once the rate is resolved, finish the calculation and save the report in the same invocation.

## Establish the accomplishment

In plain language, summarize the evidenced outcome and why it matters, retaining meaningful supplied metrics. Attribute the user's contribution accurately and credit collaborators where supported. Distinguish delivered capability from release, deployment, adoption, and measured mission impact. Use the complete application name and its acronym when known. State accomplishments tied to agency priorities only when the causal connection is supported.

Activate the `agency-priorities` skill. Use its attributed USDA strategic goals and Forest Service priorities; retain source date and fiscal-year limits. Always connect every supplied priority that mentions AI to the AI-assisted work or report preparation: activating this skill itself uses AI. Describe the evidenced use even when savings are zero or negative. If only report preparation used AI, say so in the paragraph. Claim a contribution to service delivery only when the evidence shows how the work contributed. Treat alignment as analysis, not agency endorsement. If the skill is unavailable, leave alignment unverified rather than inventing priorities.

In the paragraph, express each referenced priority's substantive meaning and how the work supports it. Use its title or a faithful plain-language description, never an identifier alone such as "USDA strategic goal 6". Combine overlapping priorities into a short clause; retain identifiers and source details in the notes if useful. Read `assets/example-reports.md` when drafting for examples of standalone alignment and savings language; these are illustrations, not project evidence.

## Estimate labor savings

AI assistance is assumed to have contributed. Never ask whether it was used. Compare the same scope and quality bar:

- Human-only hours cover the work needed without AI. Use measured effort where available; otherwise use defensible, documented estimates. Ask for evidence when no defensible estimate can be made.
- AI-assisted human hours include prompting, oversight, review, testing, corrections, rework, and integration. Do not count agent runtime, wall time, or commit timestamps as human effort.
- Savings = (estimated equivalent human hours without AI - human hours with AI) × the hourly wage resolved above. Use its currency and show the arithmetic.
- Format monetary amounts as `$<amount> <currency>`, for example `$1,800 USD`, including in calculation notes. For negative savings use `-$160 USD`, or describe `$160 USD` in additional labor costs. Preserve the supplied currency; the dollar sign is the requested display convention, not a currency conversion.
- Give one estimate of development hours saved or added and its equivalent labor cost in the paragraph. Describe uncertainty separately in brief calculation notes. If savings are zero or negative, state that honestly with an appropriately adapted closing sentence. Mention other AI benefits only when supported.
- This is estimated labor-cost saving, not an actual budget reduction or net AI-cost saving. Exclude AI tool spend from this measure.

## Write and verify

Write one concise, copy-ready paragraph using this template, including only applicable optional parts:

`[Released on MONTH DAY, ][version number ]Full Application Name (ABBR) [accomplishments and plain-language agency alignment, including AI priorities]. AI assistance saved an estimated [hours] development hours, equivalent to approximately $[amount] [currency] in labor costs.`

Keep the opening order exact: optional release phrase using month and day only, optional known version number, then the full application name and acronym. For example: `Released on March 12, 2.4 Example Application (EA) ...`. Omit inapplicable release dates and unknown versions. Ground accomplishments and any agency-priority connection in evidence. The final AI sentence must say **development hours**. Adapt its savings claim for zero or negative savings; never imply a positive saving unsupported by the calculation.

After the paragraph, add brief supporting calculation notes in the same file: baseline human-only hours and basis, assisted human hours and basis, supplied rate and currency, arithmetic, and material assumptions. Put uncertainty, evidence limits, alignment qualifications, and scope caveats here rather than in the copy-ready paragraph. Verify that the paragraph stands alone, explains every priority connection in plain language, includes the available AI priorities, and uses the required money format. Verify the opening order and month/day-only release date, and compare retained human text verbatim with the original. Recheck units, arithmetic, claims, completion status, plan identity, and destination. Return the saved path and any material estimation limitation.
