## Go/No-Go Recommendation: Medium-Sized Feature in Unfamiliar Repo

**Recommendation: NO-GO on immediate implementation.**

The feature-dev workflow is unambiguous on this point: even for a medium-sized feature, Phase 2 codebase exploration is not optional. "Understand before acting" and "Read and comprehend existing code patterns first" are core principles, not suggestions. Starting to code before completing exploration in an unfamiliar codebase will produce code that fights existing patterns, misses available abstractions, and requires rework when the actual conventions surface in review.

---

### Minimum Pre-Implementation Checklist

Before writing a line of feature code, complete all three of the following:

**1. Similar-feature trace**

- Launch a code-explorer agent (or do it yourself) to find the 1–2 most comparable existing features in the repo.
- Trace through their implementation end-to-end: how is logic organized, what interfaces are used, how is the feature wired in.
- _Risk if skipped_: You duplicate abstractions that already exist, or implement against an integration pattern the codebase doesn't follow.

**2. Architecture touchpoint map**

- Identify every module, interface, or abstraction your feature will touch or extend.
- Understand the flow of control from entry point to affected code.
- _Risk if skipped_: Phase 4 decisions get made blind; the first design that "looks right" may require full rewrites when you hit actual module boundaries.

**3. Test and CI convention mapping**

- Confirm where tests live, how they are named, what mocking patterns are used, and what the CI pipeline expects.
- _Risk if skipped_: Your TDD loop (mandatory on every track) produces tests that don't match the test infrastructure — CI fails, or reviewers reject the approach entirely.

---

### Risk → Workflow Phase Mapping

| Lead's suggestion                 | What phase it skips   | What breaks                                                       |
| --------------------------------- | --------------------- | ----------------------------------------------------------------- |
| "Start coding now"                | Phase 2 (Exploration) | Implementation built against wrong patterns                       |
| "Figure out conventions as we go" | Phase 2 + Phase 3     | Conventions surface in Phase 6 review; rework required            |
| "Skip exploration for speed"      | Phase 2               | Phase 4 design is uninformed; Phase 5 code diverges from codebase |

---

### Clarifying Questions (bounded to what materially affects scope/design)

Ask these before starting exploration, not instead of it:

1. **Scope boundary**: Is there an existing module this feature should extend, or does it live in a new location?
2. **Integration point**: Does this feature need to interact with any existing service, event, or API contract?
3. **Urgency tier**: Is this being reviewed by someone who knows the codebase? That affects whether Light vs. Standard track is appropriate.

---

### Downstream gates that remain mandatory regardless of schedule

Completing exploration fast doesn't remove these:

- **TDD loop** (red-green-refactor) on every implementation track — Phase 5 is explicit that this is always required
- **Independent code-reviewer agent** in Phase 6 — at minimum one, on even the Light track

The fastest legitimate path through the workflow is the **Light track** — one focused exploration, one round of targeted questions, one recommended approach, then implement. That is the minimum the workflow allows — not skipping exploration entirely.
