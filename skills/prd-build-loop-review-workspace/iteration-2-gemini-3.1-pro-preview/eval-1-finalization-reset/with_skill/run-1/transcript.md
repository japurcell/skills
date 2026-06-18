# 🤖 Copilot CLI Session

> [!NOTE]
> - **Session ID:** `cb99bf36-88b9-476f-b4b5-09b4660734fd`  
> - **Started:** 6/18/2026, 1:03:55 PM  
> - **Duration:** 17s  
> - **Exported:** 6/18/2026, 1:04:12 PM  

---

<sub>⏱️ 0s</sub>

### ⚠️ Warning

Third-party MCP servers are disabled by your organization's Copilot policy. Only built-in servers are available.

---

<sub>⏱️ 1s</sub>

### 👤 User

Read and follow exact skill file at `/home/adam/dev/personal/skills/skills/prd-build-loop-review/SKILL.md`. Ignore installed copies of `prd-build-loop-review` and any other skill with overlapping purpose; use only that file as benchmark instructions.

Benchmark constraints:
- Dry-run only.
- Do not create or modify repository files.
- Do not spawn subagents.
- Read only what current prompt requires.
- Final answer must be only exact contents for `outputs/decision.md`, with no framing, explanation, or markdown fences.

Task:
Use skill under test in dry-run mode for `evals/files/finalization-reset-fixture/`. User says: `Continue PRD work from progress and finish final review loop.` Do not change files or spawn real subagents. Read only what you need, then write `outputs/decision.md` with next orchestrator actions after a fresh implementer returned from `mode: review_fix`.


---

<sub>⏱️ 7s</sub>

### ✅ `bash`

**Read SKILL.md**

$ rtk cat /home/adam/dev/personal/skills/skills/prd-build-loop-review/SKILL.md

<details>
<summary>167 lines</summary>

````
---
name: prd-build-loop-review
description: "Orchestrates autonomous end-to-end PRD implementation loops from `prd_file`, including resume-from-`progress_file`, multi-story completion, and final simplify/review/verify/record passes. Use when user asks to implement every `passes: false` PRD story, resume PRD work from progress, finish PRD without pausing between stories, run final PRD simplify/review/verify/record after implementation, or continue until whole PRD is complete."
---

# PRD Build Loop Review

## Overview

Drive every `passes: false` story in `prd_file` to completion. `prd_file` is official status; `progress_file` is append-only resume data. Orchestrator never makes code-affecting changes directly, never commits, and stops only for a **Stop Condition**.

## When to Use

- Implement all failing PRD stories from `prd_file`.
- Resume autonomous PRD work from `progress_file`.
- Finish PRD without handing control back between stories.
- Run final combined simplify, review, verify, and record pass after implementation.
- Not for one-off story implementation, PRD authoring, or planning-only decomposition.

## Workflow

1. **Startup**
   - Invoke `subagent-model-router`.
   - Resolve `progress_file` to explicit path or `dirname(prd_file) + "/progress.txt"`.
   - If `progress_file` exists, read `## Codebase Patterns` and latest entries. Otherwise create it on first append with `## Codebase Patterns` at top.
   - If every story already has `passes: true`, reply exactly: `<promise>COMPLETE</promise>`.
   - If `prd_file` is ambiguous, contradictory, invalidly ordered, missing required details, or needs human choice, stop and ask.

2. **Phase 1: Implementation loop**
   - Pick highest-priority story in `prd_file` with `passes: false`.
   - Before first `implementer` for current code-affecting unit, read only `prd_file`, `progress_file`, and nearby `AGENTS.md` needed to dispatch work.
   - When describing startup or resume state, say explicitly: `prd_file` is official source of truth; `progress_file` is supplemental resume data only.
   - Dispatch fresh `implementer` with `./implementer-prompt.md`, all story properties, `progress_file`, nearby `AGENTS.md`, and mode such as `initial_implementation` or follow-up.
   - Require `Progress block`; append it to `progress_file` immediately before interpreting or acting on it.
   - Apply **Status Rules**.
   - If story is implemented but not finalized, record that state and leave `passes: false`.
   - Repeat until every failing story is implemented and awaiting finalization, or a **Stop Condition** applies.

3. **Phase 2: Single finalization pass**
   - Restore review-fix iteration count from `progress_file`; otherwise use `0`.
   - **Simplify:** dispatch fresh `code-simplifier` on all relevant non-ignored changes in combined final state; append its `Progress block` immediately.
   - **Review:** dispatch fresh `requirements-collector` for `prd_file`, relevant sibling docs, and GitHub issue references from commit messages, PR metadata, or PRD docs when available; append its `Progress block`. Then dispatch fresh `addy-code-reviewer` on all relevant non-ignored changes after simplification; append its `Progress block`.
   - **Fix review findings:** if review finds issues, stop and ask when iteration count is already `3`; otherwise increment count in `progress_file`, dispatch fresh `implementer` with `mode: review_fix` and full findings, append its `Progress block`, apply **Status Rules**, then rerun simplify and review on updated combined state.

4. **Verify and record**
   - Only after review is clean, run required final-state checks from stories, repo guidance, nearby `AGENTS.md`, and standard project scripts for changed areas; append orchestrator verification entry immediately.
   - Invoke `self-improve` to update nearby `AGENTS.md` with reusable guidance only.
   - Set `passes: true` only for stories that satisfy **Completion Gate**.
   - Append orchestrator final-state entry and reread `prd_file`.

5. **Before any non-`<promise>COMPLETE</promise>` response**
   - Reread `prd_file`.
   - Confirm a **Stop Condition** applies.
   - Append latest orchestrator stop-state entry to `progress_file`.
   - Ask user to decide or unblock specific open issue.

## Specific Techniques

### Source of truth and paths

- `prd_file` is only official source for story completion and status.
- `progress_file` is append-only resume and tracking data; never treat it as official completion.
- Resolve relative paths from repo or provided `prd_file`, never from session state, scratchpads, home directories, or `~/.copilot/...`.

### Role boundaries

- **Orchestrator:** selects stories, resumes from `progress_file`, dispatches subagents, applies status rules, verifies final state, updates `prd_file`, appends `progress_file`, invokes `self-improve`, and updates nearby `AGENTS.md`.
- **Implementer:** does story-specific discovery, code and test changes, and initial verification.
- **Requirements collector:** dedupes requirements before final review.
- **Code simplifier:** runs after all implementation and after every review-fix implementation.
- **Reviewer:** reviews combined final state after simplification.
- Any code-affecting change must be made by fresh `implementer`. Code-affecting includes code, tests, config, migrations, and implementation docs.
- Do not read story-specific repo files, tests, code, or behavior before first `implementer` for current code-affecting unit.
- Any new `implementer` change resets finalization: rerun simplify, review, and final verification on combined final state.
- Never simplify, review, analyze, or change `.gitignore`-ignored files; if ignore status is unclear, skip and report uncertainty.

### Progress discipline

- Subagent output is not consumed until recorded.
- Every `implementer`, `requirements-collector`, `code-simplifier`, and `reviewer` must return `Progress block`.
- Orchestrator appends each `Progress block` immediately, including `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, and `BLOCKED`.
- Missing subagent progress entry is rule violation; append corrective orchestrator entry if discovered.
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

### Decision templates for weaker models

Use these exact action shapes when they fit.

**Startup or resume before first implementer**

```text
Source of truth: `prd_file` official; `progress_file` supplemental resume data only.
Resolved `progress_file`: dirname(prd_file) + "/progress.txt" or explicit provided path.
Selected story: highest-priority `passes: false` story.
Before story-specific discovery: dispatch fresh implementer; read only `prd_file`, `progress_file`, and nearby `AGENTS.md`.
```

**After `mode: review_fix` implementer returns**

```text
1. Append implementer `Progress block` before acting on it.
2. Rerun `code-simplifier` on combined final state.
3. Rerun `requirements-collector`, then rerun `addy-code-reviewer` after simplification.
4. Do not set `passes: true` until review is clean and final checks pass.
```

**When review-fix iteration limit is reached**

```text
1. Stop.
2. Do not fix findings directly.
3. Do not dispatch another review-fix implementer.
4. Reread `prd_file`.
5. Append stop-state entry to `progress_file`.
6. Ask user to decide blocker.
```

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

### AGENTS.md

Add only reusable guidance:

- module conventions
- non-obvious gotchas
- important file relationships
- testing expectations
- config or environment requirements

Do not add story-specific notes.

### Stop Conditions

Stop only if:

- all stories in `prd_file` have `passes: true`
- real blocker remains after reasonable unblocking attempts
- `prd_file` has contradictions, invalid ordering, or missing required details needing human correction
- required human decision is needed
- review-fix iteration limit is reached
- final verification failed and needs human decision

## Common Rationalizations

| Rationalization | Reality |
| --- | --- |
| "I already know repo; I can inspect story files before dispatching implementer." | No. Before first `implementer`, read only `prd_file`, `progress_file`, and nearby `AGENTS.md` needed to dispatch. |
| "Review fix is tiny; I can patch it directly." | No. Any code-affecting change requires fresh `implementer`, then simplify/review/verify must rerun. |
| "Tests passed, so story can be marked complete." | No. Completion gate also requires fresh simplifier and reviewer after latest code change. |
| "Progress file says done, so PRD can be updated." | No. `prd_file` is only official completion source. |
| "Reviewer already ran earlier; rerunning is wasteful." | Any new `implementer` change resets finalization on combined final state. |

## Red Flags

- Returning control while any story still has `passes: false` and no **Stop Condition** applies.
- Resolving `progress_file` anywhere except explicit path or `dirname(prd_file) + "/progress.txt"`.
- Using session-state, scratchpad, home, or `~/.copilot/...` paths for `progress_file`.
- Treating subagent output as consumed before appending its `Progress block`.
- Reading story-specific files, tests, code, or behavior before first `implementer`.
- Making code-affecting changes directly.
- Skipping simplify or review.
- Fixing review findings without fresh `implementer`.
- Verifying before review is clean.
- Using anything except `prd_file` as official completion source.
- Marking `passes: true` before **Completion Gate** is satisfied.
- Simplifying, reviewing, analyzing, or changing `.gitignore`-ignored files.

## Verification

Before stopping or marking completion, confirm:

- [ ] `prd_file` remained official source of story status and completion.
- [ ] `progress_file` path was resolved from explicit path or `dirname(prd_file) + "/progress.txt"`.
- [ ] Every code-affecting change came from fresh `implementer`.
- [ ] Every subagent `Progress block` was appended before being consumed.
- [ ] Simplify and review ran on combined final state after latest code-affecting change.
- [ ] Final checks ran only after clean review.
- [ ] `passes: true` was set only for stories that satisfied **Completion Gate**.
- [ ] Any non-`<promise>COMPLETE</promise>` response followed **Stop Conditions** and recorded stop state first.
<shellId: 0 completed with exit code 0>
````

</details>


---

<sub>⏱️ 16s</sub>

### 💬 Copilot

1. Append implementer `Progress block` before acting on it.
2. Rerun `code-simplifier` on combined final state.
3. Rerun `requirements-collector`, then rerun `addy-code-reviewer` after simplification.
4. Do not set `passes: true` until review is clean and final checks pass.

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
