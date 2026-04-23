# Phase 1 — Intake (coding-task-workflow)

> ⚠️ I don't have the `coding-task-workflow` skill documentation loaded, so the
> following is a reasonable, generic interpretation of what a "Phase 1: Intake"
> step normally does in a structured coding workflow. If your skill defines a
> stricter procedure, defer to it.

## Inputs you provided

- `ISSUE: 42` — a GitHub issue reference (authoritative source of truth).
- `WORK_ITEM: maybe clean up auth later` — a free-form note you typed.
- Out-of-band context: the body of issue #42 actually describes a **CSV import
  bug that silently drops rows**.

## What Intake should do

Intake is the "understand and frame the work" phase. It should not write code.
At minimum it should:

1. **Fetch the canonical work item.**
   Pull issue #42 from GitHub (title, body, labels, linked PRs, comments) and
   treat that as the authoritative description of the work.
2. **Reconcile inputs.** Compare the typed `WORK_ITEM` string against the
   issue body. When they conflict or diverge, the linked issue wins, because:
   - it is versioned and visible to the team,
   - it is what reviewers and downstream phases will reference,
   - the typed note is vague (`"maybe clean up auth later"`) and speculative.
3. **Flag the discrepancy back to the user** rather than silently overriding —
   so you can confirm the intent.
4. **Restate the problem in its own words** (a one-paragraph problem statement)
   based on the issue body, including:
   - observed behavior (CSV import silently drops rows),
   - expected behavior (all valid rows imported, invalid rows surfaced, not
     dropped silently),
   - impact / severity hint,
   - explicit non-goals.
5. **Classify the work**: this is a **bug fix**, not a refactor or cleanup.
6. **Identify unknowns / clarifying questions** before moving on, e.g.:
   - Which importer / code path? (filename, entry point)
   - Reproduction data or a failing example CSV?
   - Which rows get dropped — malformed, encoding issues, header mismatch,
     chunk-boundary, dedupe, validation failures swallowed in a `try/except`?
   - Desired behavior for bad rows: hard fail, skip-with-report, quarantine?
   - Acceptance criteria / how we'll know it's fixed (a regression test).
7. **Produce Intake artifacts** for the next phase (Plan/Design):
   - the canonical work-item reference (`#42`),
   - the restated problem statement,
   - classification + severity,
   - open questions,
   - a stub for a failing test that will reproduce the bug (TDD / Prove-It).
8. **Stop.** Do not proceed to design or implementation — you asked for Phase 1
   only.

## What Intake should use as the work item

**The GitHub issue #42 — the CSV import bug that silently drops rows.**

Reasoning:

- `ISSUE: 42` is an explicit, authoritative pointer; the issue body is the
  source of truth.
- `WORK_ITEM: maybe clean up auth later` is:
  - tentative ("maybe", "later"),
  - unrelated to issue #42's subject (auth vs. CSV import),
  - not a defined deliverable.
- Silently dropping rows in a data import is a correctness bug — higher
  priority than speculative auth cleanup, and it's what the referenced issue
  is actually about.

So Intake should:

- **Adopt** as the work item: *"Fix CSV importer silently dropping rows
  (issue #42)."*
- **Discard / defer** the auth cleanup note. Recommended handling: surface it
  back to you and, if you want it tracked, file it as a separate issue
  (e.g. "Investigate auth cleanup") rather than bundling it into this task.
  Mixing an unrelated refactor into a bug fix violates the
  "never mix formatting/refactor changes with behavior changes" guideline.

## Suggested Intake output (draft)

```
Work item:        GitHub issue #42
Title (restated): CSV importer silently drops rows during import
Type:             Bug (correctness / data loss)
Source of truth:  Issue #42 body + comments
Ignored input:    "WORK_ITEM: maybe clean up auth later"
                   → unrelated to #42; recommend filing separately.

Problem statement:
  The CSV import path accepts a file and reports success, but some rows
  from the input are not present in the resulting dataset, with no error
  or warning surfaced to the caller.

Open questions:
  1. Which importer module / entry point is in scope?
  2. Can you share a CSV that reproduces the drop?
  3. Desired behavior for bad rows: fail, skip+report, or quarantine?
  4. Are there existing tests around the importer we should extend?

Exit criteria for Intake:
  - Questions above answered (or assumptions explicitly recorded).
  - Failing regression test identified/drafted that demonstrates the drop.
  - Ready to enter Phase 2 (Plan/Design).
```

Phase 1 ends here — no code changes, no design, no implementation.
