---
name: prd-build-loop-review
description: "Resume and finish a prd-to-tasks prd.json using append-only progress.txt. Use for /prd-build-loop, resume/continue/finish, dependency-ready implementation waves, final simplification, requirements collection, parallel code/security review, verification, passes updates, and self-improvement. Do not use for single-story implementation, PRD authoring, or task decomposition."
disable-model-invocation: true
---

# PRD Build Loop Review

## Purpose

Finish a `prd-to-tasks` `prd.json` safely.

Use for:

- `/prd-build-loop`
- resume / continue / keep going / finish
- review/fix, verification, `passes` updates, finalization
- self-improvement after completion

Do not use for:

- single-story implementation
- PRD authoring
- task decomposition

Final response must be exactly `<promise>COMPLETE</promise>` or a stop-state response.

## Core Rules

1. `prd_file` is source of truth.
2. `progress_file` is append-only resume/tracking data, never proof of completion.
3. Orchestrator may edit `prd_file` only for valid `passes` updates. Orchestrator must not edit code or commit.
4. Subagents never write `progress_file`; orchestrator appends each returned `Progress block` before using the result.
5. Feature work and review fixes must be done by fresh `implementer` subagents.
6. A story is complete only when `passes: true` is valid under the Completion Gate.
7. Before the first implementer in a wave, read only:
   - `prd_file`
   - `progress_file`
   - needed nearby `AGENTS.md`

   Do not read story-specific code, tests, or behavior first.

8. Ignored files:
   - Do not simplify, review, analyze, or change ignored files.
   - Exception: `requirements-collector` may read ignored requirements/source-of-truth docs read-only.
   - If unclear, skip and report uncertainty.
9. Read-only subagents: `requirements-collector`, `addy-code-reviewer`, `addy-security-auditor`.
10. `code-simplifier` may edit only non-ignored files for behavior-preserving simplification/refactor. It must not add scope or fix reviewer findings.
11. Any fresh `implementer` change resets finalization for affected stories.

## Startup

1. Invoke `subagent-model-router`.
2. Resolve paths:
   - Use explicit `progress_file` if provided.
   - Otherwise resolve `prd_file`, then set `progress_file = dirname(prd_file) + "/progress.txt"`.
   - Resolve relative paths from repo root or provided `prd_file`.
   - Never resolve from session state, scratchpads, home directories, or `~/.copilot/...`.
   - If sibling `progress.txt` is absent, create it on first append.
3. Validate `prd_file`:
   - Top-level `userStories` must exist.
   - Each unfinished story must have: `id`, `title`, `priority`, `dependsOn`, `parallelBatch`, `passes`.
   - Stop and ask on legacy `stories`, missing fields, contradictions, invalid dependency order, ambiguity, missing required detail, or required human choice.
4. Read `progress_file` if present, especially `## Codebase Patterns` and latest entries.
5. If `progress_file` is absent, create it on first append with `## Codebase Patterns` at top.
6. If all stories have `passes: true`, reply exactly `<promise>COMPLETE</promise>`.

## Main Loop

Repeat until all stories pass or a Stop Condition applies.

### A. Implementation Waves

Run all possible waves before finalization.

1. Build ready set: unfinished stories whose dependencies are either:
   - `passes: true` in `prd_file`, or
   - implemented in current/resume state with `DONE`, no blocking concerns, and no required human decision.
2. If no ready unfinished story exists, go to **Finalization**.
3. Select only the lowest ready `parallelBatch`.
4. Check parallel safety:
   - Parallel only when `filesLikelyTouched` and owner surfaces are distinct.
   - Serialize by priority if there is exact file overlap, same migration, same endpoint, same shared state owner, same page/form/table owner, or missing file hints on multiple stories.
   - For serialized stories, dispatch only the first story, then rerun wave planning after it returns.
   - Record conflict reason and dispatch order.
5. Dispatch one fresh `implementer` per parallel-safe story.
6. Implementers must return `NEEDS_CONTEXT` or `BLOCKED` if they find sibling-owned overlap or unmet prerequisites. They must not widen scope silently.
7. Wait for all current-wave implementers.
8. Append every implementer `Progress block`.
9. Apply **Status Rules**.
10. Continue to the next ready wave. Do not finalize just because one wave finished.

### B. Finalization

Run only when:

- no more implementation-ready waves can run, and
- at least one story is implemented but unfinalized.

Steps:

1. Finalize all implemented-unfinalized stories as one combined final state.
2. Run **Finalization and Review-Fix Loop**.
3. After clean code review and clean security audit, run final-state checks.
4. Append orchestrator verification entry.
5. Distill durable learnings and invoke `self-improve`.
6. Set `passes: true` only for stories satisfying the **Completion Gate**.
7. Append orchestrator final-state entry.
8. Reread `prd_file`.
9. If all stories pass, reply exactly `<promise>COMPLETE</promise>`.
10. Otherwise repeat Main Loop.

## Finalization and Review-Fix Loop

1. Restore review-fix count from `progress_file`; if absent, use `0`.
2. In parallel, dispatch fresh:
   - `code-simplifier`
   - `requirements-collector`
3. Append both `Progress block`s.
4. If simplifier edited files, treat edits as latest final state. Do not rerun only because simplifier edited code.
5. Invoke `addy-code-review-and-quality` if not already invoked.
6. In parallel, dispatch fresh:
   - `addy-code-reviewer`
   - `addy-security-auditor`
7. Append both review `Progress block`s before using either result.
8. If either reviewer finds issues:
   - If review-fix count is already `3`, stop.
   - Otherwise append incremented count to `progress_file`.
   - Dispatch fresh `implementer` with `mode: review_fix` and all reviewer findings.
   - Append its `Progress block`.
   - Apply **Status Rules**.
   - Rerun full finalization.
9. Keep `passes: true` blocked until both reviewers are clean and final checks pass.

## Status Rules

- `DONE`: implemented, not complete; needs finalization.
- `DONE_WITH_CONCERNS`: incomplete unless every concern is explicitly confirmed non-blocking.
- `NEEDS_CONTEXT`: provide context and redispatch fresh subagent unless human decision is required.
- `BLOCKED`: try better context, smaller slice, or stronger model; if still blocked, stop and ask.

## Subagent Payloads

### implementer

Use `./implementer-prompt.md`.

Include:

- `mode`: `implementation` or `review_fix`
- full story properties
- `prd_file`, `progress_file`
- current wave summary
- sibling story IDs/titles and `filesLikelyTouched`
- ownership boundaries
- for `review_fix`: all code-review and security-audit findings and required fix scope
- requirement to return a `Progress block`
- required status: `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, or `BLOCKED`

### code-simplifier

Include:

- relevant non-ignored combined final state
- changed areas and repo guidance

Require:

- preserve behavior and requirements
- edit only non-ignored files
- no feature work or reviewer fixes
- return `Progress block` with files changed/reviewed and outcome

### requirements-collector

Use a fast-tier model when available. Read-only.

Include:

- changed areas
- ignored-file rule

Require:

- construct explicit Requirements Source Set
- extract requirements, acceptance criteria, constraints, design decisions, issue context, and implementation guidance
- avoid code review
- avoid rereading changed code unless a requirements source contains code-like examples
- return `Progress block` with files/docs read, requirements found, skipped candidates with reasons, and uncertainties/conflicts

### addy-code-reviewer

Include:

- final combined state after simplifier edits
- simplifier output
- requirements output
- changed areas

Require:

- rely on requirements output unless more context is strictly necessary
- focus on correctness, maintainability, regressions, test coverage, requirement conformance, edge cases, and integration risks
- return reviewer `Progress block`

### addy-security-auditor

Include:

- final combined state after simplifier edits
- simplifier output
- requirements output
- changed areas

Require:

- rely on requirements output unless more context is strictly necessary
- focus on security, privacy, authn/authz, validation, injection, secrets, dependency/config risks, sensitive logging, and abuse cases
- return security-auditor `Progress block`

## Requirements Source Set

`requirements-collector` must inspect sibling directory candidates, then include or skip each with reasons.

Include:

1. `prd_file`
2. sibling requirements/source-of-truth docs next to `prd_file`
3. `handoff.md` if present; otherwise record absence
4. sibling docs whose filename or heading indicates requirements, handoff, PRD, spec, acceptance criteria, design constraints, issue context, or implementation guidance
5. linked issue context available to the session
6. ignored requirements/source-of-truth docs allowed by read-only exception

If a required source was missed:

1. finalization is invalid
2. have `requirements-collector` read the missed source
3. rerun both review subagents
4. if new requirements or findings require changes, dispatch fresh `implementer`, then rerun full finalization

## Completion Gate

Set `passes: true` only if all are true:

1. Required implementation was completed by fresh `implementer`.
2. Reviewer/security fixes, if any, were completed by fresh `implementer`.
3. Simplifier edits, if any, were only non-ignored simplification/refactor.
4. Fresh `code-simplifier` ran after latest implementer change.
5. Fresh `requirements-collector` ran after latest implementer change and before final review.
6. Fresh parallel `addy-code-reviewer` and `addy-security-auditor` ran after latest implementer change, requirements collection, and simplifier edits.
7. Code review and security audit are clean for final state.
8. Required final-state checks passed.

Never treat implementer `DONE`, confidence, passing checks alone, simplifier edits alone, one clean reviewer result alone, or `progress_file` entries as sufficient.

## Verification and Self-Improve

After clean code review and clean security audit:

1. Run checks required by:
   - story requirements
   - repo guidance
   - nearby `AGENTS.md`
   - standard project scripts for changed areas
2. Append orchestrator verification entry.
3. Mine `## Codebase Patterns` and all `Learnings for future iterations`.
4. Invoke `self-improve` with only concise reusable guidance.
5. Use buckets when useful:
   - Validation/safety
   - Cache/state/replay
   - UX/accessibility
   - Testing/anti-flake
   - Environment/setup
   - Other durable guidance
6. Preserve startup-test or production-artifact rules only when reusable.
7. Exclude story IDs, timestamps, temporary blockers, raw tracking, and one-off filenames.
8. State that reusable guidance belongs in nearby `AGENTS.md` or linked docs; story-specific notes do not.

## Stop Conditions

Stop only if one applies:

- Real blocker remains after reasonable unblocking attempts.
- `prd_file` contradiction, invalid dependency order, or missing required detail needs human correction.
- No unfinished story is implementation-ready and no implemented-unfinalized story exists.
- Required human decision is needed.
- Review-fix iteration limit is reached.
- Final verification failed and needs human decision.

## Stop Procedure

Before any non-`<promise>COMPLETE</promise>` response:

1. Reread `prd_file`.
2. Confirm a Stop Condition applies.
3. Append orchestrator stop-state entry to `progress_file`.
4. Ask user to decide or unblock the specific issue.

## Progress Format

Every subagent result must include a `Progress block`, including `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, and `BLOCKED`.

Append format:

```text
## [Date/Time] - [Story ID or FINALIZATION]
- Role: implementer | requirements-collector | code-simplifier | reviewer | security-auditor | orchestrator
- Summary
- Files changed/reviewed
- Issues or concerns
- Verification or outcome
- **Learnings for future iterations:**
  - Patterns discovered
  - Gotchas encountered
  - Useful context
---
```

Rules:

- Missing subagent progress is a rule violation; append corrective orchestrator entry if discovered.
- Keep `## Codebase Patterns` at the top.
- Store only reusable general patterns in `## Codebase Patterns`.

## Dry-Run / Status Mode

For dry-run/status only, report state concisely and do not perform work.

Always include:

- source of truth: `prd_file`; `progress_file` is supplemental only
- resolved `progress_file`; if absent, say it will be created at sibling path on first append
- forbidden fallback paths: session state, scratchpads, home directories, `~/.copilot/...`
- current phase: startup/resume, implementation wave, finalization, review-fix, stop, or self-improve
- next action and why

State details:

- Startup/resume: name lowest ready `parallelBatch` and ready story IDs.
- Parallel plan: dispatch fresh implementer per safe story; serialize overlaps with reason/order.
- After implementers: append progress first, record statuses, continue next ready wave.
- Finalization: run one combined final state for all implemented-unfinalized stories; unresolved stories stay `passes: false`.
- Review-fix: append fix implementer progress, rerun simplifier and requirements collector, then reviewers in parallel.
- Review-fix limit: stop; do not fix directly or dispatch another fixer.
- Before `self-improve`: pass only reusable guidance; exclude story IDs, timestamps, blockers, raw tracking, and one-off filenames.

## Final Checklist

Before stopping or marking completion, confirm:

- [ ] `prd_file` remained source of truth.
- [ ] `progress_file` path followed rules.
- [ ] Ready work used dependencies and lowest ready `parallelBatch`.
- [ ] All possible implementation waves ran before finalization unless stopped.
- [ ] Parallel dispatch used only non-overlapping stories.
- [ ] No story-specific code/tests/behavior were read before first implementer in a wave.
- [ ] Feature work and review fixes came from fresh implementers.
- [ ] Simplifier edits were non-ignored simplification/refactor only.
- [ ] Every subagent `Progress block` was appended before use.
- [ ] Requirements Source Set was explicit, including `handoff.md` presence or absence.
- [ ] Requirements collector listed files/docs read and skipped candidates with reasons.
- [ ] Ignored-file access obeyed read-only requirements-doc exception.
- [ ] Reviewers ran in parallel only after simplifier and requirements collector returned.
- [ ] Reviewer findings were handled by fresh implementer.
- [ ] Final checks ran only after clean code review and security audit.
- [ ] Durable learnings were distilled before `self-improve`.
- [ ] `passes: true` was set only after Completion Gate.
- [ ] Any non-`<promise>COMPLETE</promise>` response followed Stop Procedure.
