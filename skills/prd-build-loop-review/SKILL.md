---
name: prd-build-loop-review
description: "Runs dependency-aware `prd-to-tasks` execution from `prd.json` plus `progress.txt`: resume current PRD, dispatch each ready `parallelBatch` in safe implementer waves, then run parallel simplification and requirements collection before dependent final review, verification, and exact `COMPLETE` or stop-state reply. Use whenever user wants `/prd-build-loop`, resume or finish remaining PRD stories, keep going from `prd.json`/`progress.txt`, or safely fan out multi-story implementation from `prd-to-tasks`—even if they only say 'keep going' or 'finish rest of PRD'. Not for single-story implementation, PRD authoring, or task decomposition."
disable-model-invocation: true
---

# PRD Build Loop Review

## Purpose

Resume and finish a current `prd-to-tasks` `prd.json` using append-only `progress.txt` context. The orchestrator coordinates work, records status, verifies, updates `passes`, and never makes code-affecting changes or commits.

Final user replies during execution must be exactly `<promise>COMPLETE</promise>` or a valid stop-state response. For dry-run/status requests, use **Action Shapes**.

## Use When

Use for `/prd-build-loop`, “keep going,” “finish rest of PRD,” “resume,” remaining `passes: false` `userStories`, safe parallel execution by ready `parallelBatch`, final simplification, requirements collection, review, verification, status recording, and self-improvement handoff.

Do not use for single-story implementation, PRD authoring, or task decomposition.

## Core Rules

- `prd_file` is the only official source for story status and completion.
- `progress_file` is append-only supplemental resume/tracking data, never official completion.
- Subagents never write `progress_file`; append each subagent `Progress block` before acting on it.
- Every code-affecting change must be made by a fresh `implementer`: code, tests, config, migrations, and implementation docs.
- Orchestrator may select work, dispatch subagents, apply status rules, verify, set `passes`, append progress, invoke `self-improve`, and record stop/final state.
- Never commit.
- Never read story-specific repo files, tests, code, or behavior before the first `implementer` for the current wave.
- Never simplify, review, analyze, or change `.gitignore`-ignored files, except `requirements-collector` may read ignored requirements/source-of-truth docs read-only. If an ignored file is not clearly a requirements doc, skip it and report uncertainty. No subagent may change ignored files.
- Any new `implementer` change resets finalization: rerun `code-simplifier`, `requirements-collector`, `addy-code-reviewer`, and final verification on the combined final state before marking affected stories complete.

## Path and PRD Setup

1. Invoke `subagent-model-router`.
2. Resolve paths:
   - If `progress_file` is explicit, use it.
   - Otherwise resolve `prd_file`, then set `progress_file = dirname(resolved prd_file) + "/progress.txt"`.
   - Resolve relative paths from the repo or provided `prd_file`, never from session state, scratchpads, home directories, or `~/.copilot/...`.
   - If sibling `progress.txt` is absent, reserve that exact path and create it on first append.
3. Validate `prd_file`:
   - Must use current `prd-to-tasks` shape with top-level `userStories`.
   - Every unfinished story requires `id`, `title`, `priority`, `dependsOn`, `parallelBatch`, and `passes`.
   - If legacy `stories` format or missing parallel fields, stop and ask user to regenerate or migrate with `prd-to-tasks`.
   - If ambiguous, contradictory, invalidly ordered, missing required detail, or needing human choice, stop and ask.
4. If `progress_file` exists, read `## Codebase Patterns` and latest relevant entries. Otherwise create it on first append with `## Codebase Patterns` at top.
5. If every story has `passes: true`, reply exactly: `<promise>COMPLETE</promise>`.

## Subagent Dispatch Payloads

Dispatch subagents by role/tool name with an explicit payload.

### `implementer`

Use `./implementer-prompt.md` and include:

- `mode`: `implementation` or `review_fix`
- Full story properties
- `prd_file` and `progress_file`
- Current wave summary
- Sibling story IDs/titles
- Sibling `filesLikelyTouched`
- Ownership boundaries
- For `review_fix`: complete reviewer findings and required fix scope
- Instruction to return a `Progress block` and status: `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, or `BLOCKED`

### `code-simplifier`

Include relevant non-ignored combined final state, changed areas, repo guidance, and instruction to return a `Progress block`.

### `requirements-collector`

Include the complete **Requirements Source Set**, changed areas, ignored-file read-only constraint, and instruction to list files/docs read plus skipped candidates with reasons in the `Progress block`.

### `addy-code-reviewer`

Run only after `code-simplifier` and `requirements-collector` both return and both progress blocks are appended. Include final combined state, simplifier output, requirements output, changed areas, and instruction to return a reviewer `Progress block`.

## Implementation Waves

Repeat until all stories pass or a **Stop Condition** applies:

1. Build the ready set from `userStories` where `passes: false` and every `dependsOn` story has `passes: true`.
2. If unfinished stories remain but none are ready, stop: dependency order, prerequisite state, or PRD content is invalid.
3. Select only the lowest ready `parallelBatch` as the active wave.
4. Before first `implementer` for the wave, read only `prd_file`, `progress_file`, and nearby `AGENTS.md` needed to dispatch. State that `prd_file` is official and `progress_file` is supplemental only.
5. Recheck parallel safety inside the wave:
   - Dispatch in parallel only when `filesLikelyTouched` and owner surfaces are distinct.
   - Conflict signals: exact file overlap, same migration, same endpoint, same shared state owner, same page/form/table owner, or missing file hints on multiple stories.
   - Serialize conflicts by priority and record why.
6. Launch one fresh `implementer` per parallel-safe story.
7. If an implementer discovers required overlap with sibling-owned surface or unmet prerequisite work, it must return `NEEDS_CONTEXT` or `BLOCKED`; do not widen scope silently.
8. Wait for current-wave implementers.
9. Append every implementer `Progress block` before applying **Status Rules**.
10. Leave implemented-but-not-finalized stories as `passes: false`.
11. Do not start a higher `parallelBatch` until the current wave completes finalization, verification, and `passes` updates.

## Status Rules

- `DONE`: continue.
- `DONE_WITH_CONCERNS`: incomplete unless every concern is explicitly confirmed non-blocking.
- `NEEDS_CONTEXT`: if human decision is required, stop and ask; otherwise provide context and redispatch a fresh subagent.
- `BLOCKED`: try better context, smaller slice, or stronger model; if still blocked, stop and ask.

## Requirements Source Set

Before `requirements-collector`, construct and record an explicit source set:

1. `prd_file`.
2. Every sibling requirements/source-of-truth doc next to `prd_file`, including `handoff.md` if present. `handoff.md` is a required source-of-truth candidate, not optional.
3. Other sibling docs whose filename or heading indicates requirements, handoff, PRD, spec, acceptance criteria, design constraints, issue context, or implementation guidance.
4. Linked issue context available to the session.
5. Ignored requirements/source-of-truth docs under the read-only ignored-file exception.

Rules:

- Inspect the sibling directory for candidates before dispatching `requirements-collector`; do not rely on memory or examples.
- Pass the complete source set to `requirements-collector`.
- Require `requirements-collector` to list files/docs read and skipped candidates with reasons.
- If a required source was missed, finalization is invalid: read it, rerun `requirements-collector`, rerun `addy-code-reviewer`, and if new requirements require changes, dispatch a fresh `implementer` and rerun full finalization.

## Finalization and Review-Fix Loop

Run after each implemented wave and after every review-fix implementer.

1. Restore review-fix iteration count from `progress_file`; otherwise use `0`.
2. Construct and record the complete **Requirements Source Set**.
3. In parallel, run fresh:
   - `code-simplifier` on relevant non-ignored combined final state.
   - `requirements-collector` on the complete **Requirements Source Set**.
4. Append both `Progress block`s immediately.
5. Run fresh `addy-code-reviewer`; append reviewer `Progress block`.
6. If reviewer finds issues:
   - If review-fix count is already `3`, follow **Stop Procedure**.
   - Otherwise increment count in `progress_file`, dispatch fresh `implementer` with `mode: review_fix` and full findings, append its `Progress block`, apply **Status Rules**, then rerun full finalization.
7. Keep `passes: true` blocked until review is clean and final checks pass.

## Completion Gate

Mark a story complete only if all are true:

1. Required implementation was completed by a fresh `implementer`.
2. Latest code-affecting change touching that story or combined final state was made by a fresh `implementer`.
3. Fresh `code-simplifier` ran after latest code-affecting change.
4. Fresh `requirements-collector` ran after latest code-affecting change and before final review.
5. Fresh `addy-code-reviewer` ran after latest code-affecting change.
6. If review found issues, a fresh `implementer` fixed them and simplify/requirements/review reran after that fix.
7. Review is clean for final state.
8. Required final-state quality checks passed.

Never treat implementer `DONE`, confidence, passing checks alone, or `progress_file` entries as sufficient.

## Verify, Record, and Complete

1. Only after clean review, run final-state checks required by story requirements, repo guidance, nearby `AGENTS.md`, and standard project scripts for changed areas.
2. Append orchestrator verification entry immediately.
3. Distill durable learnings from `progress_file`, then invoke `self-improve` with reusable rules plus nearby `AGENTS.md` and linked docs. Do not pass raw tracking structure.
4. Set `passes: true` only for stories satisfying **Completion Gate**.
5. Append orchestrator final-state entry and reread `prd_file`.
6. If every story now has `passes: true`, reply exactly: `<promise>COMPLETE</promise>`.
7. Otherwise continue with the next ready implementation wave.

## Stop Conditions and Stop Procedure

Stop only if:

- A real blocker remains after reasonable unblocking attempts.
- `prd_file` has contradictions, invalid dependency ordering, or missing required details needing human correction.
- No unfinished story is ready because prerequisite state is invalid or incomplete.
- Required human decision is needed.
- Review-fix iteration limit is reached.
- Final verification failed and needs human decision.

Before any non-`<promise>COMPLETE</promise>` response:

1. Reread `prd_file`.
2. Confirm a Stop Condition applies.
3. Append latest orchestrator stop-state entry to `progress_file`.
4. Ask user to decide or unblock the specific open issue.

## Progress Discipline

Required subagent roles: `implementer`, `requirements-collector`, `code-simplifier`, `reviewer` via `addy-code-reviewer`.

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
- Missing subagent progress entry is a rule violation; append a corrective orchestrator entry if discovered.
- Keep `## Codebase Patterns` at top and store only reusable general patterns there.

## Self-Improve Handoff

- Mine both `## Codebase Patterns` and every detailed `Learnings for future iterations` block.
- Pass concise reusable rules only: validation/safety, cache/state/replay, UX/accessibility, testing/anti-flake, environment/setup, and other durable guidance.
- In dry-run/status handoff output, use exact bucket labels: `Validation/safety`, `Cache/state/replay`, `UX/accessibility`, `Testing/anti-flake`, `Environment/setup`, and `Other durable guidance`.
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

1. Exact sibling path.
2. If sibling `progress.txt` does not exist yet, create that sibling path on first append.
3. Forbidden fallback path families: session state, scratchpads, home directories, and `~/.copilot/...`.

For serialization plans, say overlap stories are serialized **instead of dispatching in parallel**, then name overlap reason and dispatch order.

## Critical Red Flags

Do not:

- Return control while any story still has `passes: false` and no Stop Condition applies.
- Treat same `parallelBatch` as permission to dispatch blindly.
- Resolve `progress_file` anywhere except explicit path or `dirname(prd_file) + "/progress.txt"`.
- Read story-specific files, tests, code, or behavior before first `implementer` for current wave.
- Make code-affecting changes directly.
- Start higher-batch work before current wave resolves.
- Treat legacy `stories` format as close enough.
- Let implementers silently widen scope into sibling-owned files/surfaces.
- Fix review findings without a fresh `implementer`.
- Verify before review is clean.
- Use anything except `prd_file` as official completion source.
- Mark `passes: true` before **Completion Gate** is satisfied.
- Run `self-improve` without first distilling durable learnings from `progress_file`.
- Apply ignored-file exception outside read-only `requirements-collector` access to requirements/source-of-truth docs.
- Miss sibling `handoff.md` or another source-of-truth requirements doc from the source set.

## Final Verification Checklist

Before stopping or marking completion, confirm:

- [ ] `prd_file` remained official source of story status and completion.
- [ ] `progress_file` path followed the path rules.
- [ ] Ready work used `passes`, `dependsOn`, and lowest ready `parallelBatch`.
- [ ] Parallel dispatch was limited to non-overlapping stories.
- [ ] Every code-affecting change came from a fresh `implementer`.
- [ ] Every subagent `Progress block` was appended before being consumed.
- [ ] Requirements Source Set was explicitly constructed; sibling `handoff.md` included if present or absence confirmed.
- [ ] `requirements-collector` listed files/docs read and skipped candidates with reasons.
- [ ] Ignored-file access obeyed the read-only requirements-doc exception.
- [ ] `code-simplifier` and `requirements-collector` ran after latest code-affecting change; `addy-code-reviewer` ran only after both returned.
- [ ] Final checks ran only after clean review.
- [ ] Durable learnings were distilled before `self-improve`.
- [ ] `passes: true` was set only after **Completion Gate**.
- [ ] Any non-`<promise>COMPLETE</promise>` response followed **Stop Procedure**.
