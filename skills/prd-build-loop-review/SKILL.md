---
name: prd-build-loop-review
description: "Runs dependency-aware `prd-to-tasks` execution from `prd.json` plus `progress.txt`: resume current PRD, dispatch each ready `parallelBatch` in safe implementer waves, then run parallel simplification and requirements collection before dependent final review, verification, and exact `<promise>COMPLETE</promise>` or stop-state reply. Use whenever user wants `/prd-build-loop`, resume or finish remaining PRD stories, keep going from `prd.json`/`progress.txt`, or safely fan out multi-story implementation from `prd-to-tasks`—even if they only say 'keep going' or 'finish rest of PRD'. Not for single-story implementation, PRD authoring, or task decomposition."
disable-model-invocation: true
---

# PRD Build Loop Review

## Purpose

Finish the current `prd-to-tasks` `prd.json` using append-only `progress.txt` resume context. The orchestrator never makes code-affecting changes or commits. It returns only exact `<promise>COMPLETE</promise>` or a valid stop-state response.

## When to Use

Use for `/prd-build-loop`, “keep going,” “finish rest of PRD,” resume, remaining `passes: false` `userStories`, safe parallel execution by ready `parallelBatch`, final simplification, requirements collection, review, verification, status recording, and self-improvement handoff.

Do not use for single-story implementation, PRD authoring, or task decomposition.

## Invariants

- `prd_file` is the only official source for story status and completion.
- `progress_file` is append-only supplemental resume/tracking data, never official completion.
- Subagents never write `progress_file`; append each subagent `Progress block` before acting on it.
- Every code-affecting change must be made by a fresh `implementer`: code, tests, config, migrations, and implementation docs.
- Orchestrator may select work, dispatch subagents, apply status rules, verify, set `passes`, append progress, invoke `self-improve`, and record stop/final state.
- Never commit.
- Never read story-specific repo files, tests, code, or behavior before the first `implementer` for the current wave.
- Never simplify, review, analyze, or change `.gitignore`-ignored files, except that `requirements-collector` may read ignored requirements/source-of-truth docs read-only. If an ignored file is not clearly a requirements doc, skip it and report uncertainty. No subagent may change ignored files.
- Any new `implementer` change resets finalization: rerun `code-simplifier`, `requirements-collector`, `addy-code-reviewer`, and final verification on combined final state.

## Workflow

### 1. Startup

1. Invoke `subagent-model-router`.
2. Resolve paths:
   - If `progress_file` is explicit, use it.
   - Otherwise resolve `prd_file`, then set `progress_file = dirname(resolved prd_file) + "/progress.txt"`.
   - Resolve relative paths from repo or provided `prd_file`, never from session state, scratchpads, home directories, or `~/.copilot/...`.
   - If sibling `progress.txt` is absent, reserve that exact path and create it on first append.
3. Validate `prd_file`:
   - Must use current `prd-to-tasks` shape: top-level `userStories`.
   - Every unfinished story requires `id`, `title`, `priority`, `dependsOn`, `parallelBatch`, and `passes`.
   - If legacy `stories` format or missing parallel fields, stop and ask user to regenerate or migrate with `prd-to-tasks`.
   - If ambiguous, contradictory, invalidly ordered, missing required detail, or needing human choice, stop and ask.
4. If `progress_file` exists, read `## Codebase Patterns` and latest relevant entries. Otherwise create it on first append with `## Codebase Patterns` at top.
5. If every story has `passes: true`, reply exactly: `<promise>COMPLETE</promise>`.
6. In dry-run/status outputs, use **Action Shapes**.

### 2. Implementation Waves

1. Build ready set from `userStories` where `passes: false` and every `dependsOn` story has `passes: true`.
2. If unfinished stories remain but none are ready, stop: dependency order, prerequisite state, or PRD content is invalid.
3. Select only the lowest ready `parallelBatch` as the active wave.
4. Before first `implementer` for the wave, read only `prd_file`, `progress_file`, and nearby `AGENTS.md` needed to dispatch. State that `prd_file` is official and `progress_file` is supplemental only.
5. Recheck parallel safety inside the wave:
   - Dispatch in parallel only when `filesLikelyTouched` and owner surfaces are distinct.
   - Conflict signals: exact file overlap, same migration, same endpoint, same shared state owner, same page/form/table owner, or missing file hints on multiple stories.
   - Serialize conflicts by priority and record why.
6. For each dispatched story, launch one fresh `implementer` with `./implementer-prompt.md`, all story properties, `progress_file`, `mode`, current wave summary, sibling story IDs/titles, sibling `filesLikelyTouched`, and ownership boundaries.
7. If an implementer discovers required overlap with sibling-owned surface or unmet prerequisite work, it must return `NEEDS_CONTEXT` or `BLOCKED`; do not widen scope silently.
8. Wait for all current-wave implementers.
9. Append each implementer `Progress block` before applying **Status Rules**.
10. Leave implemented-but-not-finalized stories as `passes: false`.
11. Do not start higher `parallelBatch` work until current wave resolves.
12. Repeat until all unfinished stories are implemented and awaiting finalization, or a **Stop Condition** applies.

### 3. Finalization and Review-Fix Loop

1. Restore review-fix iteration count from `progress_file`; otherwise use `0`.
2. In parallel, run fresh:
   - `code-simplifier` on relevant non-ignored combined final state.
   - `requirements-collector` for `prd_file`, all identifiable requirements/source-of-truth docs including sibling docs such as `prd.md` or `handoff.md`, linked issue context, and ignored requirements docs under the read-only exception.
3. Append both `Progress block`s immediately on return.
4. Run fresh `addy-code-reviewer` only after both helpers finish and both progress blocks are recorded. Append reviewer `Progress block`.
5. If reviewer finds issues:
   - If review-fix count is already `3`, record stop state, do not fix directly, do not dispatch another review-fix implementer, and ask user.
   - Otherwise increment count in `progress_file`, dispatch fresh `implementer` with `mode: review_fix` and full findings, append its `Progress block`, apply **Status Rules**, then rerun simplifier, requirements collector, and reviewer.
6. Keep `passes: true` blocked until review is clean and final checks pass.

### 4. Verify, Record, and Complete

1. Only after clean review, run final-state checks required by story requirements, repo guidance, nearby `AGENTS.md`, and standard project scripts for changed areas.
2. Append orchestrator verification entry immediately.
3. Distill durable learnings from `progress_file`, then invoke `self-improve` with reusable rules plus nearby `AGENTS.md` and linked docs. Do not pass raw tracking structure.
4. Set `passes: true` only for stories satisfying **Completion Gate**.
5. Append orchestrator final-state entry and reread `prd_file`.
6. If every story now has `passes: true`, reply exactly: `<promise>COMPLETE</promise>`.

### 5. Before Any Non-`<promise>COMPLETE</promise>` Response

1. Reread `prd_file`.
2. Confirm a **Stop Condition** applies.
3. Append latest orchestrator stop-state entry to `progress_file`.
4. Ask user to decide or unblock the specific open issue.

## Status Rules

- `DONE`: continue.
- `DONE_WITH_CONCERNS`: incomplete unless every concern is explicitly confirmed non-blocking.
- `NEEDS_CONTEXT`: if human decision is required, stop and ask; otherwise provide context and redispatch fresh subagent.
- `BLOCKED`: try better context, smaller slice, or stronger model; if still blocked, stop and ask.

## Completion Gate

Mark a story complete only if all are true:

1. Required implementation was completed by fresh `implementer`.
2. Latest code-affecting change touching that story or combined final state was made by fresh `implementer`.
3. Fresh `code-simplifier` ran after latest code-affecting change.
4. Fresh `requirements-collector` ran after latest code-affecting change and before final review.
5. Fresh `addy-code-reviewer` ran after latest code-affecting change.
6. If review found issues, fresh `implementer` fixed them and simplify/requirements/review reran after that fix.
7. Review is clean for final state.
8. Required final-state quality checks passed.

Never treat implementer `DONE`, confidence, passing checks alone, or `progress_file` entries as sufficient.

## Stop Conditions

Stop only if:

- Real blocker remains after reasonable unblocking attempts.
- `prd_file` has contradictions, invalid dependency ordering, or missing required details needing human correction.
- No unfinished story is ready because prerequisite state is invalid or incomplete.
- Required human decision is needed.
- Review-fix iteration limit is reached.
- Final verification failed and needs human decision.

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
- Missing subagent progress entry is a rule violation; append corrective orchestrator entry if discovered.
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
4. When all implementation waves are done, run `code-simplifier` and `requirements-collector` in parallel, then `addy-code-reviewer`.

### After `mode: review_fix` implementer returns

1. Append implementer `Progress block` before acting on it.
2. Rerun `code-simplifier` and `requirements-collector` in parallel on combined final state.
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

## Dry-Run/Status Path Output

For missing sibling `progress.txt`, always state all three:

1. Exact sibling path.
2. If sibling `progress.txt` does not exist yet, create that sibling path on first append.
3. Forbidden fallback path families: session state, scratchpads, home directories, and `~/.copilot/...`.

For serialization plans, say overlap stories are serialized **instead of dispatching in parallel**, then name overlap reason and dispatch order.

## Common Rationalizations

| Rationalization                                                                 | Reality                                                                                                                                 |
| ------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| “Same `parallelBatch` means I can dispatch everything blindly.”                 | No. Recheck file/owner overlap; serialize ambiguous stories before dispatch.                                                            |
| “I can start later-batch work while one story from current wave is unresolved.” | No. Resolve current wave first; later batches stay blocked.                                                                             |
| “Legacy `stories` format is close enough.”                                      | No. This skill expects current `prd-to-tasks` output with `userStories`, `dependsOn`, and `parallelBatch`.                              |
| “Parallel implementer found sibling-owned file; widening scope is faster.”      | No. Return `NEEDS_CONTEXT` or `BLOCKED` instead of silently stealing sibling scope.                                                     |
| “Tests passed, so story can be marked complete.”                                | No. Completion Gate still requires fresh simplifier, fresh requirements collection, clean review, and final checks after latest change. |

## Red Flags

- Returning control while any story still has `passes: false` and no **Stop Condition** applies.
- Treating `parallelBatch` as permission to ignore overlap or ownership checks.
- Resolving `progress_file` anywhere except explicit path or `dirname(prd_file) + "/progress.txt"`.
- Reading story-specific files, tests, code, or behavior before first `implementer` for current wave.
- Making code-affecting changes directly.
- Starting higher-batch work before current wave resolves.
- Fixing review findings without fresh `implementer`.
- Verifying before review is clean.
- Using anything except `prd_file` as official completion source.
- Marking `passes: true` before **Completion Gate** is satisfied.
- Running `self-improve` without first distilling durable learnings from `progress_file`.
- Applying the ignored-file exception to anything except read-only `requirements-collector` access to requirements/source-of-truth docs.

## Verification Checklist

Before stopping or marking completion, confirm:

- [ ] `prd_file` remained official source of story status and completion.
- [ ] `progress_file` path was explicit or `dirname(prd_file) + "/progress.txt"`, even when sibling `progress.txt` did not exist yet.
- [ ] Ready work was selected from `userStories` using `passes`, `dependsOn`, and lowest ready `parallelBatch`.
- [ ] Parallel dispatch was limited to non-overlapping stories; ambiguous overlaps were serialized or escalated.
- [ ] Every code-affecting change came from fresh `implementer`.
- [ ] Every subagent `Progress block` was appended before being consumed.
- [ ] Ignored-file access was limited to read-only `requirements-collector` access to requirements/source-of-truth docs.
- [ ] `code-simplifier` and `requirements-collector` ran after latest code-affecting change, and `addy-code-reviewer` ran only after both returned.
- [ ] Final checks ran only after clean review.
- [ ] Durable learnings were distilled from `progress_file` before invoking `self-improve`.
- [ ] `passes: true` was set only for stories satisfying **Completion Gate**.
- [ ] Any non-`<promise>COMPLETE</promise>` response followed **Stop Conditions** and recorded stop state first.
