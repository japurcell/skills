---
name: prd-build-loop-review
description: "Runs dependency-aware `prd-to-tasks` execution from `prd.json` with append-only `progress.txt`: resume the current PRD, execute all ready implementation waves by lowest `parallelBatch`, then run simplification, requirements collection, review, verification, update `passes`, and continue until exact `<promise>COMPLETE</promise>` or stop-state reply. Use whenever the user wants `/prd-build-loop`, to resume, keep going, continue, finish, or finish the rest of a PRD from `prd.json` and `progress.txt`, including vague requests like 'keep going', 'resume', 'continue', or 'finish rest of PRD'. Do not use for single-story implementation, PRD authoring, or task decomposition."
disable-model-invocation: true
---

# PRD Build Loop Review

## Purpose

Resume and finish a `prd-to-tasks` `prd.json` using append-only `progress.txt`.

The orchestrator coordinates only: resolve files, select dependency-ready work, dispatch subagents, append progress, finalize implemented work, verify, update `passes`, invoke `self-improve`, and record final/stop state. It never edits code directly and never commits.

Final execution reply must be exactly `<promise>COMPLETE</promise>` or a stop-state response. For dry-run/status requests, use **Action Shapes**.

## Use When

Use for `/prd-build-loop`, “keep going,” “resume,” “continue,” “finish,” “finish rest of PRD,” completing remaining `passes: false` `userStories`, safe parallel execution by lowest ready `parallelBatch`, final simplification, requirements collection, review, verification, status recording, and self-improvement handoff.

Do not use for single-story implementation, PRD authoring, or task decomposition.

## Core Rules

- `prd_file` is the official source for story completion: only `passes: true` means complete.
- `progress_file` is append-only supplemental resume/tracking data.
- Subagents never write `progress_file`; append every subagent `Progress block` before acting on it.
- Feature work and reviewer fixes must be done by fresh `implementer` subagents.
- The orchestrator never makes code-affecting changes and never commits.
- Before the first `implementer` in a wave, read only `prd_file`, `progress_file`, and needed nearby `AGENTS.md`; do not read story-specific code/tests/behavior.
- `code-simplifier` may edit only non-ignored files for simplification/refactor. It must not add scope, change requirements, fix reviewer findings, or edit ignored files.
- `requirements-collector` and `addy-code-reviewer` are read-only.
- Do not simplify, review, analyze, or change ignored files, except `requirements-collector` may read ignored requirements/source-of-truth docs read-only.
- If an ignored file is not clearly a requirements/source-of-truth doc, skip it and report uncertainty.
- Any fresh `implementer` change resets finalization for affected stories.

## Setup

1. Invoke `subagent-model-router`.
2. Resolve paths:
   - If `progress_file` is explicit, use it.
   - Otherwise resolve `prd_file`, then set `progress_file = dirname(prd_file) + "/progress.txt"`.
   - Resolve relative paths from repo root or provided `prd_file`.
   - Never resolve from session state, scratchpads, home directories, or `~/.copilot/...`.
   - If sibling `progress.txt` is absent, reserve that exact path and create it on first append.
3. Validate `prd_file`:
   - Must have top-level `userStories`.
   - Every unfinished story must have `id`, `title`, `priority`, `dependsOn`, `parallelBatch`, and `passes`.
   - Stop and ask on legacy `stories`, missing fields, contradiction, invalid dependency order, ambiguity, missing required detail, or needed human choice.
4. Read `progress_file` if present, especially `## Codebase Patterns` and latest entries. If absent, create it on first append with `## Codebase Patterns` at top.
5. If every story has `passes: true`, reply exactly `<promise>COMPLETE</promise>`.

## Main Loop

Repeat until all stories pass or a **Stop Condition** applies.

### A. Implementation Phase

Run all currently possible implementation waves before finalization.

1. Build implementation-ready set: unfinished stories where every dependency is either:
   - `passes: true` in `prd_file`, or
   - already implemented with acceptable status in this run/resume state and not blocked.
2. If no implementation-ready unfinished story exists, go to **Finalization Phase** for implemented-unfinalized stories.
3. Select only the lowest ready `parallelBatch` as the active implementation wave.
4. Recheck parallel safety:
   - Parallel only when `filesLikelyTouched` and owner surfaces are distinct.
   - Conflict signals: exact file overlap, same migration, same endpoint, same shared state owner, same page/form/table owner, or missing file hints on multiple stories.
   - Serialize conflicts by priority, record why, and do not start unsafe parallel work.
5. Dispatch one fresh `implementer` per parallel-safe story.
6. If an implementer discovers sibling-owned overlap or unmet prerequisite work, it must return `NEEDS_CONTEXT` or `BLOCKED`; do not widen scope silently.
7. Wait for all current-wave implementers.
8. Append every implementer `Progress block`.
9. Apply **Status Rules**.
10. Continue with the next implementation-ready wave. Do not run finalization merely because one wave finished.

### B. Finalization Phase

Run finalization only when no more implementation-ready waves can run, or when all remaining unfinished stories require finalization before progress can continue.

1. Finalize all implemented-unfinalized stories as one combined final state.
2. Run **Finalization and Review-Fix Loop**.
3. Mark `passes: true` only for stories satisfying **Completion Gate**.
4. Reread `prd_file`.
5. If all stories pass, reply exactly `<promise>COMPLETE</promise>`.
6. Otherwise repeat **Main Loop**.

## Status Rules

- `DONE`: story is implemented, not complete; it still needs finalization.
- `DONE_WITH_CONCERNS`: incomplete unless every concern is explicitly confirmed non-blocking.
- `NEEDS_CONTEXT`: if human decision is required, stop and ask; otherwise provide context and redispatch a fresh subagent.
- `BLOCKED`: try better context, smaller slice, or stronger model; if still blocked, stop and ask.

## Subagent Payloads

Dispatch subagents by role/tool name with explicit payloads.

### `implementer`

Use `./implementer-prompt.md`. Include:

- `mode`: `implementation` or `review_fix`
- Full story properties
- `prd_file`, `progress_file`
- Current wave summary
- Sibling story IDs/titles and `filesLikelyTouched`
- Ownership boundaries
- For `review_fix`: complete reviewer findings and required fix scope
- Instruction to return a `Progress block`
- Required status: `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, or `BLOCKED`

### `code-simplifier`

May edit non-ignored files for simplification/refactor only. Include:

- Relevant non-ignored combined final state
- Changed areas and repo guidance
- Preserve behavior and requirements
- Do not edit ignored files
- Do not do feature work or reviewer fixes
- Return a `Progress block` listing files changed/reviewed and outcome

### `requirements-collector`

Use a fast-tier model when available. Read-only. Include:

- Complete **Requirements Source Set**
- Changed areas
- Ignored-file rule: read-only access only for clear requirements/source-of-truth docs
- Extract requirements, acceptance criteria, constraints, design decisions, issue context, and implementation guidance
- Avoid code review and avoid rereading changed code unless a requirements source contains code-like examples
- Return a `Progress block` listing files/docs read, requirements found, skipped candidates with reasons, and uncertainties/conflicts

### `addy-code-reviewer`

Run only after `code-simplifier` and `requirements-collector` both return and both `Progress block`s are appended. Include:

- Final combined state after simplifier edits
- Simplifier output
- Requirements output
- Changed areas
- Rely on `requirements-collector` for requirements context unless more context is strictly necessary
- Return a reviewer `Progress block`

## Requirements Source Set

Before `requirements-collector`, construct and record an explicit source set.

Include:

1. `prd_file`
2. Every sibling requirements/source-of-truth doc next to `prd_file`
3. `handoff.md` if present, or record absence
4. Other sibling docs whose filename or heading indicates requirements, handoff, PRD, spec, acceptance criteria, design constraints, issue context, or implementation guidance
5. Linked issue context available to the session
6. Ignored requirements/source-of-truth docs allowed by the read-only ignored-file exception

Rules:

- Inspect the sibling directory for candidates before dispatch.
- Pass the complete source set to `requirements-collector`.
- Require files/docs read and skipped candidates with reasons.
- If a required source was missed, finalization is invalid: add/read it, rerun `requirements-collector`, rerun `addy-code-reviewer`, and if new requirements require changes, dispatch fresh `implementer` then rerun full finalization.

## Finalization and Review-Fix Loop

1. Restore review-fix iteration count from `progress_file`; otherwise use `0`.
2. Construct and record the complete **Requirements Source Set**.
3. In parallel, run fresh:
   - `code-simplifier` on relevant non-ignored combined final state
   - `requirements-collector` on the complete **Requirements Source Set**
4. Append both `Progress block`s.
5. If `code-simplifier` edited files, treat those edits as latest final state; do not rerun finalization only because simplifier edited code.
6. Run fresh `addy-code-reviewer`.
7. Append reviewer `Progress block`.
8. If reviewer finds issues:
   - If review-fix count is already `3`, follow **Stop Procedure**.
   - Otherwise increment count in `progress_file`.
   - Dispatch fresh `implementer` with `mode: review_fix` and full findings.
   - Append its `Progress block`.
   - Apply **Status Rules**.
   - Rerun full finalization.
9. Keep `passes: true` blocked until review is clean and final checks pass.

## Completion Gate

Mark a story complete only if all are true:

1. Required implementation was completed by a fresh `implementer`.
2. Reviewer-required fixes, if any, were completed by a fresh `implementer`.
3. `code-simplifier` edits, if any, were non-ignored simplification/refactor only.
4. Fresh `requirements-collector` ran after latest `implementer` change and before final review.
5. Fresh `code-simplifier` ran after latest `implementer` change.
6. Fresh `addy-code-reviewer` ran after latest `implementer` change and after any simplifier edits.
7. Review is clean for final state.
8. Required final-state checks passed.

Never treat implementer `DONE`, confidence, passing checks alone, simplifier edits alone, or `progress_file` entries as sufficient.

## Verify, Record, Complete

After clean review:

1. Run final-state checks required by story requirements, repo guidance, nearby `AGENTS.md`, and standard project scripts for changed areas.
2. Append orchestrator verification entry.
3. Distill durable learnings from `progress_file`.
4. Invoke `self-improve` with concise reusable rules plus nearby `AGENTS.md` and linked docs; do not pass raw tracking structure.
5. Set `passes: true` only for stories satisfying **Completion Gate**.
6. Append orchestrator final-state entry.
7. Reread `prd_file`.
8. If every story has `passes: true`, reply exactly `<promise>COMPLETE</promise>`.
9. Otherwise continue to the next ready work.

## Stop Conditions

Stop only if one applies:

- Real blocker remains after reasonable unblocking attempts
- `prd_file` contradiction, invalid dependency ordering, or missing required detail needs human correction
- No unfinished story is implementation-ready and no implemented-unfinalized story exists
- Required human decision is needed
- Review-fix iteration limit is reached
- Final verification failed and needs human decision

## Stop Procedure

Before any non-`<promise>COMPLETE</promise>` response:

1. Reread `prd_file`.
2. Confirm a **Stop Condition** applies.
3. Append latest orchestrator stop-state entry to `progress_file`.
4. Ask the user to decide or unblock the specific open issue.

## Progress Discipline

Required subagent roles:

- `implementer`
- `requirements-collector`
- `code-simplifier`
- `reviewer` via `addy-code-reviewer`

Required entry format:

```text
## [Date/Time] - [Story ID or FINALIZATION]
- Role: implementer | requirements-collector | code-simplifier | reviewer | orchestrator
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

- Every subagent result must include a `Progress block`, including `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, and `BLOCKED`.
- Missing subagent progress is a rule violation; append a corrective orchestrator entry if discovered.
- Keep `## Codebase Patterns` at the top.
- Store only reusable general patterns in `## Codebase Patterns`.

## Self-Improve Handoff

- Mine `## Codebase Patterns` and every `Learnings for future iterations` block.
- Pass only concise reusable guidance.
- Use buckets when applicable: `Validation/safety`, `Cache/state/replay`, `UX/accessibility`, `Testing/anti-flake`, `Environment/setup`, `Other durable guidance`.
- Preserve durable startup-test or production-artifact rules, including recurring repo-required artifact paths only when reusable.
- Drop story IDs, timestamps, temporary blockers, raw tracking data, and one-off filenames.
- State explicitly: only reusable guidance belongs in nearby `AGENTS.md` or linked docs; story-specific notes stay out.

## Action Shapes

Use these exact numbered lines verbatim in dry-run/status outputs. Choose exactly one matching block.

### Startup or resume before first implementer wave

1. Source of truth: `prd_file` official for completion; `progress_file` supplemental resume data only.
2. Resolved `progress_file`: explicit path or `dirname(prd_file) + "/progress.txt"`; if absent, create that sibling path on first append and never substitute session-state/home path.
3. Active implementation wave: lowest ready `parallelBatch` and ready story IDs.
4. Dispatch one fresh implementer per parallel-safe story before any story-specific discovery; if stories overlap, serialize instead of dispatching them in parallel, cite the shared owner surface or exact file, give dispatch order, and do not start unsafe parallel work.

### After current-wave implementers return

1. Append every implementer `Progress block` before acting on it.
2. Record per-story implementation status; unresolved stories stay `passes: false`.
3. Continue to the next implementation-ready wave; do not run finalization merely because one wave finished.
4. Keep `passes: true` blocked until finalization, clean review, and final checks pass.

### When no more implementation-ready waves can run

1. Append any missing current-wave `Progress block` before acting on it.
2. Run finalization and review for all implemented-unfinalized stories as one combined final state.
3. Keep unresolved stories `passes: false`.
4. Continue remaining work only after finalization updates `passes` or a stop condition is confirmed.

### After `mode: review_fix` implementer returns

1. Append implementer `Progress block` before acting on it.
2. Reconstruct the Requirements Source Set and rerun `code-simplifier` and `requirements-collector` in parallel on combined final state.
3. After both return, rerun `addy-code-reviewer`.
4. Keep `passes: true` blocked until review is clean and final checks pass.

### When review-fix iteration limit is reached

1. State that review-fix iteration limit is reached.
2. Do not fix directly.
3. Do not dispatch another review-fix implementer.
4. Reread `prd_file`.
5. Append stop-state entry to `progress_file`.
6. Human decision required: ask user to decide blocker.

### Before invoking `self-improve`

1. Mine `## Codebase Patterns` and every `Learnings for future iterations` block, including patterns, gotchas, and useful context.
2. Pass only reusable guidance into nearby `AGENTS.md` or linked docs, not story-specific notes, raw tracking data, story IDs, timestamps, temporary blockers, or one-off filenames.
3. Preserve durable rules under exact bucket labels when applicable: `Validation/safety`, `Cache/state/replay`, `UX/accessibility`, `Testing/anti-flake`, and `Environment/setup`. If reusable guidance does not fit, include it under `Other durable guidance` rather than dropping it.
4. Preserve durable startup-test or production-artifact rules when present, including recurring repo-required artifact paths only when they are reusable guidance rather than one-off story details.

## Dry-Run/Status Requirements

For missing sibling `progress.txt`, always state:

1. Exact sibling path
2. Create that sibling path on first append if it does not exist
3. Forbidden fallback path families: session state, scratchpads, home directories, and `~/.copilot/...`

For serialization plans, say overlap stories are serialized instead of dispatched in parallel, then name the overlap reason and dispatch order.

## Final Checklist

Before stopping or marking completion, confirm:

- [ ] `prd_file` remained official source of story completion.
- [ ] `progress_file` path followed path rules.
- [ ] Ready work used dependencies and lowest ready `parallelBatch`.
- [ ] All possible implementation waves ran before finalization unless a stop condition applied.
- [ ] Parallel dispatch was limited to non-overlapping stories.
- [ ] No story-specific code/tests/behavior were read before first implementer in the wave.
- [ ] Feature work and review fixes came from fresh `implementer` subagents.
- [ ] `code-simplifier` edits were non-ignored simplification/refactor only.
- [ ] Every subagent `Progress block` was appended before use.
- [ ] Requirements Source Set was explicitly constructed.
- [ ] `handoff.md` was included if present or absence was confirmed.
- [ ] `requirements-collector` listed files/docs read and skipped candidates with reasons.
- [ ] Ignored-file access obeyed read-only requirements-doc exception.
- [ ] `code-simplifier` and `requirements-collector` ran after latest implementer change.
- [ ] `addy-code-reviewer` ran only after simplifier and requirements collector returned.
- [ ] Review-fix findings were handled by fresh `implementer`, not directly.
- [ ] Final checks ran only after clean review.
- [ ] Durable learnings were distilled before `self-improve`.
- [ ] `passes: true` was set only after **Completion Gate**.
- [ ] Any non-`<promise>COMPLETE</promise>` response followed **Stop Procedure**.
