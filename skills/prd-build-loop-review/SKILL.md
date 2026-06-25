---
name: prd-build-loop-review
description: "Resume and finish a prd-to-tasks `prd.json` using append-only `progress.txt`. Use for `/prd-build-loop`, resume/continue/keep going/finish requests, dependency-ready implementation waves by lowest `parallelBatch`, final simplification, requirements collection, parallel code/security review, verification, `passes` updates, and self-improvement. Do not use for single-story implementation, PRD authoring, or task decomposition."
disable-model-invocation: true
---

# PRD Build Loop Review

## Use When

Use this skill for `/prd-build-loop`, resume, continue, keep going, finish, review/fix, finalization, verification, `passes` updates, and self-improvement for a `prd-to-tasks` `prd.json`.

Do not use for single-story implementation, PRD authoring, or task decomposition.

## Mission

Finish a `prd-to-tasks` `prd.json` safely.

The orchestrator must:

- Treat `prd_file` as source of truth.
- Use `progress_file` only as append-only resume/tracking data.
- Run dependency-ready implementation waves by lowest `parallelBatch`.
- Dispatch subagents.
- Append every subagent `Progress block` before using its result.
- Run final simplification, requirements collection, parallel code/security review, verification, `passes` updates, and `self-improve`.

The orchestrator must not:

- Edit code directly.
- Commit changes.
- Treat `progress_file` as proof of completion.
- Mark a story complete unless `passes: true` is valid under the Completion Gate.

Final reply must be exactly `<promise>COMPLETE</promise>` or a stop-state response.

## Core Rules

1. `prd_file` is authoritative. A story is complete only when `passes: true`.
2. `progress_file` is append-only.
3. Subagents never write `progress_file`; the orchestrator appends their returned `Progress block`s.
4. Feature work and review fixes must be done by fresh `implementer` subagents.
5. Before the first implementer in a wave, read only:
   - `prd_file`
   - `progress_file`
   - needed nearby `AGENTS.md`

   Do not read story-specific code, tests, or behavior first.

6. Ignored files:
   - Do not simplify, review, analyze, or change ignored files.
   - Exception: `requirements-collector` may read ignored requirements/source-of-truth docs read-only.
   - If unclear whether an ignored file is a requirements/source-of-truth doc, skip it and report uncertainty.
7. `code-simplifier` may edit only non-ignored files for behavior-preserving simplification/refactor. It must not add scope, change requirements, or fix reviewer findings.
8. `requirements-collector`, `addy-code-reviewer`, and `addy-security-auditor` are read-only.
9. Any fresh `implementer` change resets finalization for affected stories.

## Startup

1. Invoke `subagent-model-router`.
2. Resolve paths:
   - If `progress_file` is explicit, use it.
   - Otherwise resolve `prd_file`, then set `progress_file = dirname(prd_file) + "/progress.txt"`.
   - Resolve relative paths from repo root or provided `prd_file`.
   - Never resolve from session state, scratchpads, home directories, or `~/.copilot/...`.
   - If sibling `progress.txt` is absent, create that exact path on first append.
3. Validate `prd_file`:
   - Must have top-level `userStories`.
   - Each unfinished story must have `id`, `title`, `priority`, `dependsOn`, `parallelBatch`, and `passes`.
   - Stop and ask on legacy `stories`, missing fields, contradictions, invalid dependency order, ambiguity, missing required detail, or required human choice.
4. Read `progress_file` if present, especially `## Codebase Patterns` and latest entries.
5. If `progress_file` is absent, create it on first append with `## Codebase Patterns` at top.
6. If all stories have `passes: true`, reply exactly `<promise>COMPLETE</promise>`.

## Main Loop

Repeat until all stories pass or a Stop Condition applies.

### 1. Implementation Waves

Run all possible implementation waves before finalization.

1. Build ready set: unfinished stories whose dependencies are either:
   - `passes: true` in `prd_file`, or
   - implemented in this run/resume state with acceptable status and not blocked.
2. If no ready unfinished story exists, go to Finalization.
3. Select only the lowest ready `parallelBatch`.
4. Check parallel safety:
   - Parallel only when `filesLikelyTouched` and owner surfaces are distinct.
   - Conflict signals: exact file overlap, same migration, same endpoint, same shared state owner, same page/form/table owner, or missing file hints on multiple stories.
   - Serialize conflicts by priority; record reason and dispatch order.
5. Dispatch one fresh `implementer` per parallel-safe story.
6. Implementers must return `NEEDS_CONTEXT` or `BLOCKED` if they find sibling-owned overlap or unmet prerequisites. They must not widen scope silently.
7. Wait for all current-wave implementers.
8. Append every implementer `Progress block`.
9. Apply Status Rules.
10. Continue to the next ready wave. Do not finalize only because one wave finished.

### 2. Finalization

Run only when no more implementation-ready waves can run and at least one story is implemented but unfinalized.

1. Finalize all implemented-unfinalized stories as one combined final state.
2. Run the Finalization and Review-Fix Loop.
3. After clean code review and clean security audit, run final-state checks.
4. Append orchestrator verification entry.
5. Distill durable learnings and invoke `self-improve`.
6. Set `passes: true` only for stories satisfying the Completion Gate.
7. Append orchestrator final-state entry.
8. Reread `prd_file`.
9. If all stories pass, reply exactly `<promise>COMPLETE</promise>`.
10. Otherwise repeat Main Loop.

## Status Rules

- `DONE`: implemented, not complete; needs finalization.
- `DONE_WITH_CONCERNS`: incomplete unless every concern is explicitly confirmed non-blocking.
- `NEEDS_CONTEXT`: provide context and redispatch a fresh subagent unless human decision is required.
- `BLOCKED`: try better context, smaller slice, or stronger model; if still blocked, stop and ask.

## Subagent Payloads

### `implementer`

Use `./implementer-prompt.md`.

Include:

- `mode`: `implementation` or `review_fix`
- Full story properties
- `prd_file`, `progress_file`
- Current wave summary
- Sibling story IDs/titles and `filesLikelyTouched`
- Ownership boundaries
- For `review_fix`: full code-review and security-audit findings and required fix scope
- Requirement to return a `Progress block`
- Required status: `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, or `BLOCKED`

### `code-simplifier`

Include:

- Relevant non-ignored combined final state
- Changed areas and repo guidance
- Preserve behavior and requirements
- Edit only non-ignored files
- No feature work or reviewer fixes
- Return `Progress block` with files changed/reviewed and outcome

### `requirements-collector`

Use a fast-tier model when available. Read-only.

Include:

- Changed areas
- Ignored-file rule
- Requirement to build the Requirements Source Set
- Extract requirements, acceptance criteria, constraints, design decisions, issue context, and implementation guidance
- Avoid code review
- Avoid rereading changed code unless a requirements source contains code-like examples
- Return `Progress block` with files/docs read, requirements found, skipped candidates with reasons, and uncertainties/conflicts

### Parallel Review Subagents

Run only after both `code-simplifier` and `requirements-collector` return and their `Progress block`s are appended.

Dispatch fresh read-only reviewers in parallel:

- `addy-code-reviewer`
- `addy-security-auditor`

Both reviewers must evaluate the same final combined state.

### `addy-code-reviewer`

Include:

- Final combined state after simplifier edits
- Simplifier output
- Requirements output
- Changed areas
- Rely on requirements output unless more context is strictly necessary
- Focus on correctness, maintainability, regressions, test coverage, requirement conformance, edge cases, and integration risks
- Return reviewer `Progress block`

### `addy-security-auditor`

Include:

- Final combined state after simplifier edits
- Simplifier output
- Requirements output
- Changed areas
- Rely on requirements output unless more context is strictly necessary
- Focus on security, privacy, authorization/authentication, data validation, injection risks, secret handling, dependency/configuration risks, logging sensitive data, and abuse cases
- Return security-auditor `Progress block`

## Requirements Source Set

`requirements-collector` must construct an explicit source set.

First inspect the sibling directory for candidate docs, then include or skip each with reasons.

Include:

1. `prd_file`
2. Sibling requirements/source-of-truth docs next to `prd_file`
3. `handoff.md` if present; otherwise record absence
4. Sibling docs whose filename or heading indicates requirements, handoff, PRD, spec, acceptance criteria, design constraints, issue context, or implementation guidance
5. Linked issue context available to the session
6. Ignored requirements/source-of-truth docs allowed by the read-only exception

If a required source was missed:

1. Finalization is invalid.
2. Have `requirements-collector` read the missed source.
3. Rerun both parallel review subagents.
4. If new requirements or review findings require changes, dispatch a fresh `implementer`, then rerun full finalization.

## Finalization and Review-Fix Loop

1. Restore review-fix count from `progress_file`; otherwise use `0`.
2. In parallel, dispatch fresh:
   - `code-simplifier`
   - `requirements-collector`
3. Append both `Progress block`s.
4. If simplifier edited files, treat those edits as latest final state. Do not rerun finalization only because simplifier edited code.
5. Invoke `addy-code-review-and-quality` if not already invoked.
6. Dispatch fresh parallel read-only subagents:
   - `addy-code-reviewer`
   - `addy-security-auditor`
7. Wait for both reviewers.
8. Append both review `Progress block`s before using either result.
9. If either reviewer finds issues:
   - If review-fix count is already `3`, stop.
   - Otherwise increment count in `progress_file`.
   - Dispatch fresh `implementer` with `mode: review_fix` and all findings from both reviewers.
   - Append its `Progress block`.
   - Apply Status Rules.
   - Rerun full finalization.
10. Keep `passes: true` blocked until both reviewers are clean and final checks pass.

## Completion Gate

Mark a story complete only if all are true:

1. Required implementation was completed by a fresh `implementer`.
2. Reviewer-required fixes and security-auditor-required fixes, if any, were completed by a fresh `implementer`.
3. Simplifier edits, if any, were non-ignored simplification/refactor only.
4. Fresh `code-simplifier` ran after the latest implementer change.
5. Fresh `requirements-collector` ran after the latest implementer change and before final review.
6. Fresh parallel `addy-code-reviewer` and `addy-security-auditor` ran after the latest implementer change, after requirements collection, and after simplifier edits.
7. Code review and security audit are clean for final state.
8. Required final-state checks passed.

Never treat implementer `DONE`, confidence, passing checks alone, simplifier edits alone, one clean review result alone, or `progress_file` entries as sufficient.

## Verification and Self-Improve

After clean code review and clean security audit:

1. Run checks required by:
   - Story requirements
   - Repo guidance
   - Nearby `AGENTS.md`
   - Standard project scripts for changed areas
2. Append orchestrator verification entry.
3. Mine `## Codebase Patterns` and all `Learnings for future iterations`.
4. Invoke `self-improve` with only concise reusable guidance.
5. Use buckets when useful:
   - `Validation/safety`
   - `Cache/state/replay`
   - `UX/accessibility`
   - `Testing/anti-flake`
   - `Environment/setup`
   - `Other durable guidance`
6. Preserve durable startup-test or production-artifact rules only when reusable.
7. Drop story IDs, timestamps, temporary blockers, raw tracking data, and one-off filenames.
8. State that only reusable guidance belongs in nearby `AGENTS.md` or linked docs; story-specific notes stay out.

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
4. Ask the user to decide or unblock the specific issue.

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

- Missing subagent progress is a rule violation; append a corrective orchestrator entry if discovered.
- Keep `## Codebase Patterns` at the top.
- Store only reusable general patterns in `## Codebase Patterns`.

## Dry-Run / Status Outputs

For dry-run/status only, report state concisely and do not perform work.

Always include:

- Source of truth: `prd_file`; `progress_file` is supplemental only.
- Resolved `progress_file`; if absent, say it will be created at sibling path on first append.
- Forbidden fallback paths: session state, scratchpads, home directories, `~/.copilot/...`.
- Current phase: startup/resume, implementation wave, finalization, review-fix, stop, or self-improve.
- Next action and why.

State-specific requirements:

- Startup/resume: name lowest ready `parallelBatch` and ready story IDs.
- Parallel plan: dispatch one fresh implementer per safe story; serialize overlaps with reason/order.
- After implementers: append progress first, record statuses, continue next ready wave; do not finalize just because one wave ended.
- Finalization: run one combined final state for all implemented-unfinalized stories; unresolved stories stay `passes: false`.
- Review-fix: after fix implementer returns, append progress, rerun simplifier and requirements collector, then run reviewers in parallel.
- Review-fix limit: stop; do not fix directly or dispatch another fixer; reread PRD, append stop-state, ask user.
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
- [ ] Ignored-file access obeyed the read-only requirements-doc exception.
- [ ] Reviewers ran in parallel only after simplifier and requirements collector returned.
- [ ] Code review and security audit findings were handled by fresh implementer.
- [ ] Final checks ran only after clean code review and clean security audit.
- [ ] Durable learnings were distilled before `self-improve`.
- [ ] `passes: true` was set only after Completion Gate.
- [ ] Any non-`<promise>COMPLETE</promise>` response followed Stop Procedure.
