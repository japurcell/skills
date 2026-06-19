---
name: prd-build-loop-review
description: "Autonomously finishes a PRD execution loop: resume from `progress_file`, drive every remaining `passes: false` story in `prd_file`, then run one final simplify/review/verify/record pass before returning exact completion response. Use whenever user wants agent to keep going until PRD is done, resume `progress.txt`, finish all remaining stories without pausing, or complete final PRD finalization/review work—even if they only say 'keep going' or 'finish rest of PRD'. Not for single-story implementation, PRD authoring, or task decomposition."
disable-model-invocation: true
---

# PRD Build Loop Review

## Overview

Finish `prd_file` end to end. `prd_file` is official story status; `progress_file` is append-only resume data. Orchestrator never makes code-affecting changes or commits, and returns only for `<promise>COMPLETE</promise>` or a real stop condition.

## When to Use

- Finish every remaining `passes: false` story in `prd_file`.
- Resume autonomous PRD work from `progress_file` or `progress.txt`.
- Keep going until whole PRD is done instead of pausing after each story.
- Run final simplify/review/verify/record pass after implementation.
- Not for one-off story implementation, PRD authoring, or planning/decomposition.

## Workflow

1. **Startup**
   - Invoke `subagent-model-router`.
   - Resolve `progress_file` to explicit path or `dirname(prd_file) + "/progress.txt"`.
   - Resolve `prd_file` first, then derive default `progress_file` from that exact directory. Example: `/repo/specs/prd.json` -> `/repo/specs/progress.txt`.
   - If `progress_file` exists, read `## Codebase Patterns` plus latest relevant entries. Otherwise keep that sibling path reserved and create it there on first append with `## Codebase Patterns` at top.
   - If every story already has `passes: true`, reply exactly: `<promise>COMPLETE</promise>`.
   - If `prd_file` is ambiguous, contradictory, invalidly ordered, missing required detail, or needs human choice, stop and ask.
   - In dry-run or status outputs, use **Action shapes** below.

2. **Implementation loop**
   - Pick highest-priority `passes: false` story.
   - Before first `implementer` for current code-affecting unit, read only `prd_file`, `progress_file`, and nearby `AGENTS.md` needed to dispatch work.
   - State explicitly: `prd_file` is official source of truth; `progress_file` is supplemental resume data only.
   - Dispatch fresh `implementer` with `./implementer-prompt.md`, all story properties, `progress_file`, nearby `AGENTS.md`, and `mode`.
   - Require `Progress block`; append it to `progress_file` before acting on it.
   - Apply **Status Rules** exactly.
   - If story is implemented but not finalized, record that state and leave `passes: false`.
   - Repeat until every failing story is implemented and awaiting finalization, or a **Stop Condition** applies.

3. **Single finalization pass**
   - Restore review-fix iteration count from `progress_file`; otherwise use `0`.
   - Run fresh `code-simplifier` on relevant non-ignored changes in combined final state; append its `Progress block` immediately.
   - Run fresh `requirements-collector` for `prd_file`, relevant sibling docs, and available issue context; append its `Progress block`.
   - Run fresh `addy-code-reviewer` after simplification; append its `Progress block`.
   - If review finds issues and count is already `3`, state that limit is reached, do not fix directly, do not dispatch another review-fix implementer, record stop state, and ask.
   - Otherwise increment count in `progress_file`, dispatch fresh `implementer` with `mode: review_fix` and full findings, append its `Progress block`, apply **Status Rules**, then rerun simplify, requirements collection, and review on combined final state.

4. **Verify and record**
   - Only after review is clean, run final-state checks required by story requirements, repo guidance, nearby `AGENTS.md`, and standard project scripts for changed areas; append orchestrator verification entry immediately.
   - Distill durable learnings from `progress_file`, then invoke `self-improve` with that distilled summary plus nearby `AGENTS.md` and linked docs. Pass reusable rules, not raw tracking structure.
   - Set `passes: true` only for stories that satisfy **Completion Gate**.
   - Append orchestrator final-state entry and reread `prd_file`.

5. **Before any non-`<promise>COMPLETE</promise>` response**
   - Reread `prd_file`.
   - Confirm a **Stop Condition** applies.
   - Append latest orchestrator stop-state entry to `progress_file`.
   - Ask user to decide or unblock specific open issue.

## Specific Techniques

### Source of truth, paths, and boundaries

- `prd_file` is only official source for story completion and status.
- `progress_file` is append-only resume and tracking data; never treat it as official completion.
- Resolve the default path in two steps: `(1)` resolve `prd_file`, `(2)` set `progress_file = dirname(resolved prd_file) + "/progress.txt"`.
- If that sibling `progress.txt` does not exist yet, keep the same path and create it on first append; missing file is never permission to invent a different location.
- Resolve relative paths from repo or provided `prd_file`, never from session state, scratchpads, home directories, or `~/.copilot/...`.
- Forbidden fallbacks for default `progress_file`: session-state paths, scratchpads, temp/session artifacts, or any other path not inside `dirname(prd_file)` unless user supplied an explicit `progress_file`.
- **Orchestrator:** selects stories, resumes from `progress_file`, dispatches subagents, applies status rules, verifies final state, updates `prd_file`, appends `progress_file`, invokes `self-improve`, and records stop/final state.
- **Implementer:** does story-specific discovery, code and test changes, and initial verification.
- **Requirements collector:** dedupes requirements before final review.
- **Code simplifier:** runs after all implementation and after every review-fix implementation.
- **Reviewer:** reviews combined final state after simplification.
- Any code-affecting change must be made by fresh `implementer`. Code-affecting includes code, tests, config, migrations, and implementation docs.
- Do not read story-specific repo files, tests, code, or behavior before first `implementer` for current code-affecting unit.
- Any new `implementer` change resets finalization: rerun simplify, review, and final verification on combined final state.
- Never simplify, review, analyze, or change `.gitignore`-ignored files; if ignore status is unclear, skip and report uncertainty.

### Progress discipline

- Do not consume subagent output until recorded.
- Every `implementer`, `requirements-collector`, `code-simplifier`, and `reviewer` must return `Progress block`.
- Orchestrator appends each `Progress block` immediately, including `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, and `BLOCKED`.
- Missing subagent progress entry is a rule violation; append corrective orchestrator entry if discovered.
- Maintain `## Codebase Patterns` at top and store only reusable general patterns there.
- Subagents never write `progress_file` directly.

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

### Self-improve handoff

- Before invoking `self-improve`, mine both `## Codebase Patterns` and detailed per-entry learnings in `progress_file`; durable guidance can hide in patterns, gotchas, or useful context.
- Pass `self-improve` concise reusable rules only: framework constraints, validation/safety rules, stable fix shapes, UX-preservation rules, testing/anti-flake tactics, and environment/setup requirements.
- Preserve representative concrete rules when present, not only category names: decoded return-url validation, shared return-url policy, cached reads vs fresh mutation fetches around `shareReplay(1)`, stable `aria-describedby` order, root-level Jasmine `it` with range-based time assertions, and staged startup artifact `wwwroot/dist/browser/index.html`.
- Keep precise technical tokens when they are reusable guidance; drop story IDs, timestamps, temporary blockers, and one-off filenames.
- If source contains them, preserve at least one reusable rule from each present category: validation/safety, cache/state/replay, UX/accessibility, testing/anti-flake, and environment/setup.
- Name destination in handoff: nearby `AGENTS.md` when prompt-worthy, linked docs when detail is too long for `AGENTS.md`.

### Action shapes

Use these exact numbered lines verbatim in dry-run/status outputs:

- **Startup or resume before first implementer**
  1. Source of truth: `prd_file` official; `progress_file` supplemental resume data only.
  2. Resolved `progress_file`: explicit path or `dirname(prd_file) + "/progress.txt"`; if absent, create that sibling path on first append and never substitute session-state/home path.
  3. Selected story: highest-priority `passes: false` story.
  4. Before story-specific discovery: dispatch fresh implementer; read only `prd_file`, `progress_file`, and nearby `AGENTS.md`.
- **After `mode: review_fix` implementer returns**
  1. Append implementer `Progress block` before acting on it.
  2. Rerun `code-simplifier` on combined final state.
  3. Rerun `requirements-collector`, then `addy-code-reviewer`.
  4. Keep `passes: true` blocked until review is clean and final checks pass.
- **When review-fix iteration limit is reached**
  1. State that review-fix iteration limit is reached.
  2. Do not fix directly.
  3. Do not dispatch another review-fix implementer.
  4. Reread `prd_file`.
  5. Append stop-state entry to `progress_file`.
  6. Human decision required: ask the user to decide blocker.
- **Self-improve handoff summary**
  1. Destination: nearby `AGENTS.md` or linked docs.
  2. Reusable guidance only; no raw progress blocks, story-only notes, or transient blockers.
  3. Validation/safety: [for example decoded return-url checks, shared return-url policy, single-rule targeting]
  4. Cache/state/replay: [for example cached reads vs fresh mutations, `shareReplay(1)` replay hazards]
  5. UX/accessibility: [for example stable `aria-describedby` order, preserve error/focus UX]
  6. Testing/anti-flake: [for example root-level Jasmine `it`, range-based time assertions]
  7. Environment/setup: [for example staged startup artifact `wwwroot/dist/browser/index.html`]

### Completion Gate

Mark story complete only if all are true:

1. Required implementation was completed by fresh `implementer`.
2. Latest code-affecting change, including any review fix, was made by fresh `implementer`.
3. Fresh `code-simplifier` ran after latest code-affecting change.
4. Fresh `addy-code-reviewer` ran after latest code-affecting change.
5. If review found issues, fresh `implementer` fixed them and simplify/review reran after that fix.
6. Review is clean for final state.
7. Required final-state quality checks passed.

Never treat implementer `DONE`, confidence, passing checks alone, or `progress_file` entries as sufficient.

### Status Rules

- **DONE:** continue.
- **DONE_WITH_CONCERNS:** incomplete unless every concern is explicitly confirmed non-blocking.
- **NEEDS_CONTEXT:** if human decision is required, stop and ask; otherwise provide context and redispatch fresh subagent.
- **BLOCKED:** try better context, smaller slice, or stronger model; if still blocked, stop and ask.

### Stop Conditions

Stop only if:

- all stories in `prd_file` have `passes: true`
- real blocker remains after reasonable unblocking attempts
- `prd_file` has contradictions, invalid ordering, or missing required details needing human correction
- required human decision is needed
- review-fix iteration limit is reached
- final verification failed and needs human decision

## Common Rationalizations

| Rationalization                                                                  | Reality                                                                                                           |
| -------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| "I already know repo; I can inspect story files before dispatching implementer." | No. Before first `implementer`, read only `prd_file`, `progress_file`, and nearby `AGENTS.md` needed to dispatch. |
| "Review fix is tiny; I can patch it directly."                                   | No. Any code-affecting change requires fresh `implementer`, then simplify/review/verify must rerun.               |
| "Tests passed, so story can be marked complete."                                 | No. **Completion Gate** also requires fresh simplifier and reviewer after latest code change.                     |
| "Progress file says done, so PRD can be updated."                                | No. `prd_file` is only official completion source.                                                                |
| "No sibling `progress.txt` exists yet, so I can write one in session state or scratchpad." | No. Default path stays `dirname(prd_file) + "/progress.txt"` and gets created there on first append. |
| "Reviewer already ran earlier; rerunning is wasteful."                           | Any new `implementer` change resets finalization on combined final state.                                         |
| "One obvious note is enough; I can ignore rest of progress learnings."           | No. Final `self-improve` handoff must cover all durable learnings, not only most visible one.                     |

## Red Flags

- Returning control while any story still has `passes: false` and no **Stop Condition** applies.
- Resolving `progress_file` anywhere except explicit path or `dirname(prd_file) + "/progress.txt"`.
- Creating or planning to create default `progress_file` anywhere except beside `prd_file`, including session-state, scratchpad, temp, home-artifact, or `~/.copilot/...` paths.
- Treating subagent output as consumed before appending its `Progress block`.
- Reading story-specific files, tests, code, or behavior before first `implementer`.
- Making code-affecting changes directly.
- Skipping simplify or review.
- Fixing review findings without fresh `implementer`.
- Verifying before review is clean.
- Using anything except `prd_file` as official completion source.
- Marking `passes: true` before **Completion Gate** is satisfied.
- Simplifying, reviewing, analyzing, or changing `.gitignore`-ignored files.
- Running `self-improve` without first distilling durable learnings from `progress_file`.

## Verification

Before stopping or marking completion, confirm:

- [ ] `prd_file` remained official source of story status and completion.
- [ ] `progress_file` path was resolved from explicit path or `dirname(prd_file) + "/progress.txt"`, even when sibling `progress.txt` did not exist yet.
- [ ] Every code-affecting change came from fresh `implementer`.
- [ ] Every subagent `Progress block` was appended before being consumed.
- [ ] Simplify and review ran on combined final state after latest code-affecting change.
- [ ] Final checks ran only after clean review.
- [ ] Durable learnings were distilled from `progress_file` before invoking `self-improve`.
- [ ] `passes: true` was set only for stories that satisfied **Completion Gate**.
- [ ] Any non-`<promise>COMPLETE</promise>` response followed **Stop Conditions** and recorded stop state first.
