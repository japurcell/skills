---
name: prd-build-loop-review
description: "Runs dependency-aware `prd-to-tasks` execution from `prd.json` plus append-only `progress.txt`: resume the current PRD, execute the lowest ready `parallelBatch` in safe implementer waves, then run simplification and requirements collection before dependent review, verification, and exact `COMPLETE` or stop-state reply. Use whenever the user wants `/prd-build-loop`, to resume, keep going, or finish the rest of a PRD from `prd.json`/`progress.txt`, including vague requests like 'keep going' or 'finish rest of PRD'. Do not use for single-story implementation, PRD authoring, or task decomposition."
disable-model-invocation: true
---

# PRD Build Loop Review

## Purpose

Resume and finish the current `prd-to-tasks` `prd.json` using append-only `progress.txt`.

The orchestrator only coordinates: select work, dispatch subagents, append progress, apply status rules, verify, update `passes`, invoke `self-improve`, and record stop/final state. It never changes code directly and never commits.

Final execution replies must be exactly `<promise>COMPLETE</promise>` or a valid stop-state response. For dry-run or status requests, use **Action Shapes**.

## Use When

Use for `/prd-build-loop`, “keep going,” “finish rest of PRD,” “resume,” completing remaining `passes: false` `userStories`, safe parallel execution by ready `parallelBatch`, final simplification, requirements collection, review, verification, status recording, and self-improvement handoff.

Do not use for single-story implementation, PRD authoring, or task decomposition.

## Core Rules

- `prd_file` is the only official source of story status and completion.
- `progress_file` is append-only supplemental resume/tracking data only.
- Subagents never write `progress_file`; append every subagent `Progress block` before acting on it.
- Feature implementation and review fixes must be done by a fresh `implementer`.
- `code-simplifier` may edit non-`.gitignore`-ignored files for simplification/refactor only.
- `code-simplifier` must not add scope, change requirements, fix reviewer findings, or edit ignored files.
- `requirements-collector` and `addy-code-reviewer` are read-only.
- The orchestrator never makes code-affecting changes.
- Never commit.
- Before the first `implementer` for a wave, do not read story-specific code, tests, or behavior.
- Do not simplify, review, analyze, or change `.gitignore`-ignored files, except `requirements-collector` may read ignored requirements/source-of-truth docs read-only.
- If an ignored file is not clearly a requirements/source-of-truth doc, skip it and report uncertainty.
- Any new `implementer` change or `code-simplifier` edit resets finalization for affected stories.

## Setup

1. Invoke `subagent-model-router`.
2. Resolve paths:
   - If `progress_file` is explicit, use it.
   - Otherwise resolve `prd_file`, then set `progress_file = dirname(resolved prd_file) + "/progress.txt"`.
   - Resolve relative paths from the repo or provided `prd_file`.
   - Never resolve from session state, scratchpads, home directories, or `~/.copilot/...`.
   - If sibling `progress.txt` is absent, reserve that exact path and create it on first append.
3. Validate `prd_file`:
   - Must use current `prd-to-tasks` shape with top-level `userStories`.
   - Every unfinished story must have `id`, `title`, `priority`, `dependsOn`, `parallelBatch`, and `passes`.
   - If legacy `stories` format or required parallel fields are missing, stop and ask the user to regenerate or migrate with `prd-to-tasks`.
   - If ambiguous, contradictory, invalidly ordered, missing required detail, or needing human choice, stop and ask.
4. If `progress_file` exists, read `## Codebase Patterns` and the latest relevant entries.
5. If `progress_file` does not exist, create it on first append with `## Codebase Patterns` at the top.
6. If every story has `passes: true`, reply exactly: `<promise>COMPLETE</promise>`.

## Subagent Payloads

Dispatch subagents by role/tool name with explicit payloads.

### `implementer`

Use `./implementer-prompt.md` and include:

- `mode`: `implementation` or `review_fix`
- Full story properties
- `prd_file` and `progress_file`
- Current wave summary
- Sibling story IDs/titles
- Sibling `filesLikelyTouched`
- Ownership boundaries
- For `review_fix`, complete reviewer findings and required fix scope
- Instruction to return a `Progress block`
- Required status: `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, or `BLOCKED`

### `code-simplifier`

May edit non-ignored files for simplification only. Include:

- Relevant non-ignored combined final state
- Changed areas
- Repo guidance
- Instruction to preserve behavior and requirements
- Instruction not to edit ignored files
- Instruction not to do feature work or reviewer fixes
- Instruction to return a `Progress block` listing files changed/reviewed and outcome

### `requirements-collector`

Use a fast-tier model when available. Read-only. Include:

- Complete **Requirements Source Set**
- Changed areas
- Ignored-file rule: read-only access only for clear requirements/source-of-truth docs
- Instruction to extract all relevant requirements, acceptance criteria, constraints, design decisions, issue context, and implementation guidance
- Instruction to avoid code review and avoid rereading changed code unless a requirements source contains code-like examples
- Instruction to return a `Progress block`
- Instruction to list:
  - Files/docs read
  - Requirements found
  - Skipped candidates with reasons
  - Uncertainties or conflicts

### `addy-code-reviewer`

Run only after `code-simplifier` and `requirements-collector` both return and both `Progress block`s are appended. Include:

- Final combined state after simplifier edits
- Simplifier output
- Requirements output
- Changed areas
- Instruction to rely on `requirements-collector` for requirements context unless more context is strictly necessary
- Instruction to return a reviewer `Progress block`

## Implementation Loop

Repeat until all stories pass or a **Stop Condition** applies.

1. Build the ready set from `userStories` where `passes: false` and every `dependsOn` story has `passes: true`.
2. If unfinished stories remain but none are ready, stop: dependency order, prerequisite state, or PRD content is invalid.
3. Select only the lowest ready `parallelBatch` as the active wave.
4. Before the first `implementer` for the wave, read only `prd_file`, `progress_file`, and nearby `AGENTS.md` needed to dispatch.
5. State that `prd_file` is official and `progress_file` is supplemental only.
6. Recheck parallel safety:
   - Dispatch in parallel only when `filesLikelyTouched` and owner surfaces are distinct.
   - Conflict signals include exact file overlap, same migration, same endpoint, same shared state owner, same page/form/table owner, or missing file hints on multiple stories.
   - Serialize conflicts by priority, record why, and do not start higher-batch work.
7. Launch one fresh `implementer` per parallel-safe story.
8. If an implementer discovers required overlap with a sibling-owned surface or unmet prerequisite work, it must return `NEEDS_CONTEXT` or `BLOCKED`; do not widen scope silently.
9. Wait for current-wave implementers.
10. Append every implementer `Progress block` before applying **Status Rules**.
11. Leave implemented-but-not-finalized stories as `passes: false`.
12. Run **Finalization and Review-Fix Loop** for the current wave.
13. Do not start a higher `parallelBatch` until current-wave finalization, verification, and `passes` updates are complete.

## Status Rules

- `DONE`: continue.
- `DONE_WITH_CONCERNS`: incomplete unless every concern is explicitly confirmed non-blocking.
- `NEEDS_CONTEXT`: if human decision is required, stop and ask; otherwise provide context and redispatch a fresh subagent.
- `BLOCKED`: try better context, smaller slice, or stronger model; if still blocked, stop and ask.

## Requirements Source Set

Before `requirements-collector`, construct and record an explicit source set.

Include:

1. `prd_file`
2. Every sibling requirements/source-of-truth doc next to `prd_file`, including `handoff.md` if present
3. Other sibling docs whose filename or heading indicates requirements, handoff, PRD, spec, acceptance criteria, design constraints, issue context, or implementation guidance
4. Linked issue context available to the session
5. Ignored requirements/source-of-truth docs allowed by the read-only ignored-file exception

Rules:

- Inspect the sibling directory for candidates before dispatching `requirements-collector`.
- Do not rely on memory or examples.
- `handoff.md` is a required source-of-truth candidate.
- Pass the complete source set to `requirements-collector`.
- Require `requirements-collector` to list files/docs read and skipped candidates with reasons.
- If a required source was missed, finalization is invalid:
  1. Read/add the missing source.
  2. Rerun `requirements-collector`.
  3. Rerun `addy-code-reviewer`.
  4. If new requirements require changes, dispatch a fresh `implementer` and rerun full finalization.

## Finalization and Review-Fix Loop

Run after each implemented wave, after every review-fix implementer, and after any simplifier edit.

1. Restore review-fix iteration count from `progress_file`; otherwise use `0`.
2. Construct and record the complete **Requirements Source Set**.
3. In parallel, run fresh:
   - `code-simplifier` on relevant non-ignored combined final state
   - `requirements-collector` on the complete **Requirements Source Set**
4. Append both `Progress block`s immediately.
5. If `code-simplifier` edited files, treat those edits as the latest final-state changes and use that final state for review.
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
2. Any reviewer-required fixes were completed by a fresh `implementer`.
3. Any `code-simplifier` edits were limited to non-ignored simplification/refactor only.
4. Fresh `requirements-collector` ran after the latest implementer change and before final review.
5. Fresh `code-simplifier` ran after the latest implementer change.
6. Fresh `addy-code-reviewer` ran after the latest implementer change and after any `code-simplifier` edits.
7. Review is clean for the final state.
8. Required final-state quality checks passed.

Never treat implementer `DONE`, confidence, passing checks alone, simplifier edits alone, or `progress_file` entries as sufficient.

## Verify, Record, and Complete

1. Only after clean review, run final-state checks required by story requirements, repo guidance, nearby `AGENTS.md`, and standard project scripts for changed areas.
2. Append orchestrator verification entry immediately.
3. Distill durable learnings from `progress_file`.
4. Invoke `self-improve` with reusable rules plus nearby `AGENTS.md` and linked docs.
5. Do not pass raw tracking structure to `self-improve`.
6. Set `passes: true` only for stories that satisfy **Completion Gate**.
7. Append orchestrator final-state entry.
8. Reread `prd_file`.
9. If every story now has `passes: true`, reply exactly: `<promise>COMPLETE</promise>`.
10. Otherwise continue with the next ready implementation wave.

## Stop Conditions

Stop only if one applies:

- A real blocker remains after reasonable unblocking attempts
- `prd_file` has contradictions, invalid dependency ordering, or missing required details needing human correction
- No unfinished story is ready because prerequisite state is invalid or incomplete
- Required human decision is needed
- Review-fix iteration limit is reached
- Final verification failed and needs human decision

## Stop Procedure

Before any non-`<promise>COMPLETE</promise>` response:

1. Reread `prd_file`.
2. Confirm a **Stop Condition** applies.
3. Append the latest orchestrator stop-state entry to `progress_file`.
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

- Mine both `## Codebase Patterns` and every detailed `Learnings for future iterations` block.
- Pass concise reusable rules only.
- Use these categories when applicable:
  - `Validation/safety`
  - `Cache/state/replay`
  - `UX/accessibility`
  - `Testing/anti-flake`
  - `Environment/setup`
  - `Other durable guidance`
- Preserve representative concrete durable rules.
- Preserve durable startup-test or production-artifact rules, including recurring repo-required artifact paths only when reusable guidance rather than one-off story details.
- Drop story IDs, timestamps, temporary blockers, raw tracking data, and one-off filenames.
- State explicitly that only reusable guidance belongs in nearby `AGENTS.md` or linked docs; story-specific notes stay out.

## Action Shapes

Use these exact numbered lines verbatim in dry-run/status outputs. Choose exactly one matching block. Do not prepend startup lines to review-fix or finalization outputs.

### Startup or resume before first implementer wave

1. Source of truth: `prd_file` official; `progress_file` supplemental resume data only.
2. Resolved `progress_file`: explicit path or `dirname(prd_file) + "/progress.txt"`; if absent, create that sibling path on first append and never substitute session-state/home path.
3. Active wave: lowest ready `parallelBatch` and ready story IDs.
4. Dispatch one fresh implementer per parallel-safe story before any story-specific discovery; if stories overlap, serialize instead of dispatching them in parallel, cite the shared owner surface or exact file, give dispatch order, and do not start higher-batch work.

### After current-wave implementers return

1. Append every implementer `Progress block` before acting on it.
2. Record per-story status; unresolved stories stay `passes: false`.
3. Do not start higher `parallelBatch` work until current wave resolves.
4. Construct the Requirements Source Set, run `code-simplifier` and `requirements-collector` in parallel, then `addy-code-reviewer`.

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

For missing sibling `progress.txt`, always state all three:

1. Exact sibling path
2. If sibling `progress.txt` does not exist yet, create that sibling path on first append
3. Forbidden fallback path families: session state, scratchpads, home directories, and `~/.copilot/...`

For serialization plans, say overlap stories are serialized instead of dispatching in parallel, then name the overlap reason and dispatch order.

## Final Checklist

Before stopping or marking completion, confirm:

- [ ] `prd_file` remained the official source of story status and completion.
- [ ] `progress_file` path followed the path rules.
- [ ] Ready work used `passes`, `dependsOn`, and the lowest ready `parallelBatch`.
- [ ] Parallel dispatch was limited to non-overlapping stories.
- [ ] No higher-batch work started before the current wave resolved.
- [ ] No story-specific files, tests, code, or behavior were read before the first `implementer` for the wave.
- [ ] Feature implementation and review fixes came from fresh `implementer` subagents.
- [ ] `code-simplifier` edits, if any, were non-ignored simplification/refactor only.
- [ ] Every subagent `Progress block` was appended before use.
- [ ] Requirements Source Set was explicitly constructed.
- [ ] Sibling `handoff.md` was included if present or its absence was confirmed.
- [ ] `requirements-collector` listed files/docs read and skipped candidates with reasons.
- [ ] Ignored-file access obeyed the read-only requirements-doc exception.
- [ ] `code-simplifier` and `requirements-collector` ran after the latest implementer change.
- [ ] `addy-code-reviewer` ran only after simplifier and requirements collector returned.
- [ ] Review-fix findings were handled by a fresh `implementer`, not directly.
- [ ] Final checks ran only after clean review.
- [ ] Durable learnings were distilled before `self-improve`.
- [ ] `passes: true` was set only after **Completion Gate**.
- [ ] Any non-`<promise>COMPLETE</promise>` response followed **Stop Procedure**.
