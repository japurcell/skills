# Feature Dev Workflow Response

## Understanding

**Request**: Implement a medium-sized feature that updates three files, then finish with review.

**Track Selected**: **Standard Track**

A feature touching three files with a request for explicit review fits Standard track — medium scope, multiple files involved, and an explicit quality gate requested. The workflow does not allow skipping review even when intent is clear.

---

## Relevant Findings

Without a real codebase to explore, the workflow would launch two focused `code-explorer` agents in parallel:

- **Agent 1**: "Map the architecture and abstractions for the feature area, tracing through the code comprehensively — return 5–10 key files to read."
- **Agent 2**: "Find features similar to this one and trace through their implementation comprehensively — return 5–10 key files to read."

After agents return, I would read every file they identify directly to ground understanding in source, not summaries.

**Patterns that typically matter for a three-file change**:
- How the three files relate (data model → service → API/controller, or similar)
- Existing conventions for error handling, naming, and testing
- Whether the files share a common abstraction layer to extend vs. patch

---

## Open Questions

For a generic three-file change, one high-leverage question remains:

1. **Which three files?** — determines whether this is model+service+route (additive extension), three sibling utilities (parallel change), or a cross-layer slice. The answer materially affects sequencing.

If the answer is "whatever you think is best," I would state my assumption (model → service → route) and get confirmation before proceeding.

---

## Recommendation

**Standard track: extend an existing pattern rather than invent a new one.**

1. Identify the correct abstraction in each of the three files.
2. Follow existing naming/error-handling conventions exactly.
3. Implement with TDD: write a failing test first, make it pass, then refactor.
4. Run quality review as a separate mandatory phase.

This avoids both over-engineering and under-testing.

---

## Implementation Map

### Phase 5: Implementation (required on every track)

**Enforcement**: The skill requires the `tdd` skill on every track with an explicit red-green-refactor loop. This cannot be bypassed.

```
File 1 (e.g., model/data layer):
  - Write failing test → implement → refactor
File 2 (e.g., service/business logic):
  - Write failing test → implement → refactor
File 3 (e.g., API/controller layer):
  - Write failing test → implement → refactor
```

Each file change follows the same TDD loop before moving to the next.

### Phase 6: Quality Review (required on every track, enforced independently)

**Exact subagent roles launched after implementation**:

| Subagent | Reference | Role | Parallelism |
|---|---|---|---|
| `code-simplifier` | `../code-simplifier/SKILL.md` | Identifies refactoring opportunities — DRY violations, unnecessary complexity, readability gaps | Always run exactly once, independently, after implementation |
| `code-reviewer` #1 | `code-reviewer` | Focus: **simplicity** — is the code as simple as it can be? | Launched in parallel with other reviewers |
| `code-reviewer` #2 | `code-reviewer` | Focus: **correctness** — are edge cases covered? Are there logic errors? | Launched in parallel |
| `code-reviewer` #3 | `code-reviewer` | Focus: **conventions** — does the code match project style, naming, and patterns? | Launched in parallel |

**Enforcement rule from the skill**:
- Standard and Deep tracks require **multiple** independent `code-reviewer` agents in parallel with different focuses — not a single combined review.
- The `code-simplifier` is always required in addition to reviewers; it is never substituted by a reviewer.
- Findings are consolidated and high-severity issues are fixed directly unless the user asked to stop after review.

### Review Consolidation

After all parallel review agents complete:
1. Merge findings, deduplicate, prioritize by severity.
2. Fix obvious high-severity issues immediately.
3. Surface remaining risks and follow-up work.

---

## Artifact Status

Because this is Standard track and implementation spans multiple phases, a handoff artifact is required at:

```
.agents/scratchpad/three-file-feature/handoff-plan.md
```

The artifact must include as **named discrete steps** in the Validation Plan (not buried in Implementation Slices):
1. TDD red-green-refactor completion
2. code-simplifier refactor pass
3. Independent code-reviewer review(s)

---

## Phase 7: Summary

**What was built**: A three-file feature implemented on the Standard track with TDD and a mandatory multi-agent quality review phase.

**Key decisions**:
- Standard track chosen because the feature touches multiple files and an explicit review phase was requested.
- TDD enforced as non-optional — required on every track per the skill.
- Three parallel `code-reviewer` agents (simplicity / correctness / conventions) plus one `code-simplifier` agent — the exact subagent roles the skill mandates for Standard/Deep tracks.

**Workflow enforcement summary**:
- Implementation: `tdd` skill, red-green-refactor, cannot be bypassed on any track.
- Review: `code-simplifier` (always, independently) + multiple parallel `code-reviewer` agents (Standard/Deep) with distinct focuses.
- Handoff: `handoff-plan.md` written for any Standard/Deep work that may continue in another turn.
