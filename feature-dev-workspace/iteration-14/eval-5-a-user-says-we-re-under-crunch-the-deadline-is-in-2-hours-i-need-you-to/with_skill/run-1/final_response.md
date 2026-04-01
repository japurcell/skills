# Feature Dev Workflow: Rate-Limiting Under Deadline Pressure

## Understanding

A two-file rate-limiting change under a 2-hour deadline. The user is asking to skip the TDD loop. Using the feature-dev workflow to respond.

**Track chosen**: Light — two-file change, well-bounded, relatively small scope.

---

## Response

Understood — two hours is tight, and rate-limiting logic across two files is genuinely bounded. Let's move fast. But no, we cannot skip the TDD loop.

### TDD Is Required on Every Track

The feature-dev workflow states:

> **Always use the tdd skill to implement with an explicit red-green-refactor loop. Treat this as required for Implementation on every track; do not bypass it.**

This is not a guideline or preference — it is a workflow-level constraint that applies on the Light track too. The reason it exists is that rate-limiting logic is exactly the kind of code where "I'll write tests later" becomes "tests were never written" and edge cases (off-by-one on the rate window, clock skew, concurrent request handling) only surface in production.

Writing the implementation first and the tests later is also slower than TDD for a bounded change — you end up manually testing behavior you could have been running automatically from the start.

---

## Concrete Path Forward That Fits the Deadline

Here is how to implement this within two hours while keeping TDD:

### 1. Scope the TDD loop to the minimum

For a two-file rate-limiting change:

- Write **2–3 focused tests** that cover the core contract: request allowed when under limit, request rejected when at limit, counter resets after the window expires. Skip edge cases for now and note them as follow-up.
- Write only enough production code to make those tests pass.
- Refactor for clarity (should be 5–10 minutes for two files).

This is a 30–45 minute investment, not a full TDD ceremony.

### 2. Light track exploration (15 minutes)

Do a quick targeted read of the two API handler files to understand the existing rate-limiting integration point (or lack thereof) and the request/response pattern used. Launching even one focused code-explorer subagent would help avoid a naming or pattern mismatch.

### 3. Skip optional phases

Under time pressure on a Light track:

- Skip Phase 3 (Clarifying Questions) if the requirement is clear
- Skip Phase 4 (Architecture Design) beyond one concrete approach
- Limit Phase 6 to one `code-simplifier` pass and one `code-reviewer` agent — both still run, but quickly

### 4. What stays non-negotiable

Even at two hours:

- TDD loop runs (scoped down, but not skipped)
- `code-simplifier` runs after implementation (brief pass)
- At least one `code-reviewer` agent runs (can be a quick focused review)

---

## Summary

**No on skipping TDD.** The workflow requires it on every track, and the urgency framing does not override that. The right move is to scope the TDD loop down — 2–3 tests covering the core contract — rather than removing it. A scoped TDD loop takes 30–45 minutes and still gives you confidence that the rate-limiting boundary conditions are checked before you ship.

Ready to start. Share the two API handler files and the specific rate-limiting behavior expected (requests-per-minute, per-IP, per-token?) and we'll begin with the failing tests.
