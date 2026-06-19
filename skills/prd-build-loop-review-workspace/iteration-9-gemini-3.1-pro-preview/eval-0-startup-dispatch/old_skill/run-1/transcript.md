# 🤖 Copilot CLI Session

> [!NOTE]
> - **Session ID:** `7e58524d-3342-4a02-8ec0-e8bd0f6e8b35`  
> - **Started:** 6/18/2026, 4:59:13 PM  
> - **Duration:** 39s  
> - **Exported:** 6/18/2026, 4:59:53 PM  

---

<sub>⏱️ 0s</sub>

### ⚠️ Warning

Third-party MCP servers are disabled by your organization's Copilot policy. Only built-in servers are available.

---

<sub>⏱️ 1s</sub>

### 👤 User

Read and follow exact skill file at `/home/adam/dev/personal/skills/skills/prd-build-loop-review-workspace/skill-snapshot-pre-20260618-concise/SKILL.md`.
Ignore installed copies of `prd-build-loop-review` and any other skill with overlapping purpose; use only that file as benchmark instructions.

Benchmark constraints:
- Dry-run only.
- Do not spawn subagents.
- Do not create or modify repository files outside `/home/adam/dev/personal/skills/skills/prd-build-loop-review-workspace/iteration-9-gemini-3.1-pro-preview/eval-0-startup-dispatch/old_skill/run-1/outputs`.
- Read only what current prompt requires.
- Final answer must be only exact contents for `outputs/decision.md`, with no framing, explanation, or markdown fences.

Absolute input paths for this eval:
- /home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/startup-fixture/prd.json
- /home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/startup-fixture/progress.txt

Current working directory already contains `outputs/` for benchmark artifacts. Write requested file there.

Task:
Use skill under test in dry-run mode for `evals/files/startup-fixture/`. User says: `Run PRD build loop on evals/files/startup-fixture/prd.json and do not stop between stories.` Do not change files or spawn real subagents. Read only what you need, then write `outputs/decision.md` with first orchestrator actions: source of truth, resolved `progress_file`, story selection, and what must happen before any story-specific repo discovery.

---

<sub>⏱️ 9s</sub>

### ✅ `bash`

**Read SKILL.md**

$ rtk read /home/adam/dev/personal/skills/skills/prd-build-loop-review-workspace/skill-snapshot-pre-20260618-concise/SKILL.md

<details>
<summary>174 lines</summary>

````
---
name: prd-build-loop-review
description: "Runs autonomous end-to-end PRD implementation from `prd_file`, resuming from `progress_file` and not handing control back until every remaining story is implemented, finalized, and recorded or a real stop condition applies. Use when the user says keep going until the PRD is done, resume from `progress.txt`, finish every `passes: false` story, or run the final simplify/review/verify/record loop without pausing."
---

# PRD Build Loop Review

## Overview

Drive every `passes: false` story in `prd_file` to completion. `prd_file` is official status; `progress_file` is append-only resume data. Orchestrator never makes code-affecting changes directly, never commits, and stops only for a real blocker or required human choice.

## When to Use

- Implement all failing PRD stories from `prd_file`.
- Resume autonomous PRD work from `progress_file` or `progress.txt`.
- Keep going until the whole PRD is done instead of pausing after each story.
- Run the final combined simplify, review, verify, and record pass after implementation.
- Not for one-off story implementation, PRD authoring, or planning-only decomposition.

## Workflow

1. **Startup**
   - Invoke `subagent-model-router`.
   - Resolve `progress_file` to explicit path or `dirname(prd_file) + "/progress.txt"`.
   - If `progress_file` exists, read `## Codebase Patterns` plus the latest relevant entries. Otherwise create it on first append with `## Codebase Patterns` at top.
   - If every story already has `passes: true`, reply exactly: `<promise>COMPLETE</promise>`.
   - If `prd_file` is ambiguous, contradictory, invalidly ordered, missing required detail, or needs human choice, stop and ask.
   - In dry-run or status outputs, prefer the exact startup action shape in **Action shapes for weaker models** instead of paraphrasing.

2. **Implementation loop**
   - Pick highest-priority story in `prd_file` with `passes: false`.
   - Before first `implementer` for current code-affecting unit, read only `prd_file`, `progress_file`, and nearby `AGENTS.md` needed to dispatch work.
   - State explicitly: `prd_file` is official source of truth; `progress_file` is supplemental resume data only.
   - Dispatch fresh `implementer` with `./implementer-prompt.md`, all story properties, `progress_file`, nearby `AGENTS.md`, and `mode`.
   - Require `Progress block`; append it to `progress_file` before interpreting or acting on it.
   - Apply **Status Rules** exactly.
   - If story is implemented but not finalized, record that state and leave `passes: false`.
   - Repeat until every failing story is implemented and awaiting finalization, or a **Stop Condition** applies.

3. **Single finalization pass**
   - Restore review-fix iteration count from `progress_file`; otherwise use `0`.
   - Run fresh `code-simplifier` on relevant non-ignored changes in combined final state; append its `Progress block` immediately.
   - Run fresh `requirements-collector` for `prd_file`, relevant sibling docs, and available issue context; append its `Progress block`.
   - Run fresh `addy-code-reviewer` after simplification; append its `Progress block`.
   - If review finds issues and count is already `3`, state that the review-fix iteration limit is reached, do not fix directly, do not dispatch another review-fix implementer, record stop state, and ask.
   - Otherwise increment count in `progress_file`, dispatch fresh `implementer` with `mode: review_fix` and full findings, append its `Progress block`, apply **Status Rules**, then rerun simplify and review on the updated combined state.
   - In dry-run or status outputs, prefer the exact review-fix and iteration-limit action shapes in **Action shapes for weaker models** instead of paraphrasing.

4. **Verify and record**
   - Only after review is clean, run required final-state checks from stories, repo guidance, nearby `AGENTS.md`, and standard project scripts for changed areas; append orchestrator verification entry immediately.
   - Distill durable learnings from `progress_file` first, then invoke `self-improve` with that distilled summary plus nearby `AGENTS.md` and linked docs. Pass reusable rules, not raw tracking structure.
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

### Self-improve handoff

- Before invoking `self-improve`, mine `progress_file` yourself. Read both high-level pattern sections and detailed per-entry learnings; durable guidance can hide in patterns, gotchas, or useful context.
- Pass `self-improve` a concise summary of reusable rules only: framework constraints, validation rules, stable fix shapes, UX-preservation rules, anti-flake testing tactics, environment/setup requirements, etc.
- Keep precise technical tokens from the source when they are part of the reusable rule: framework names, operators, API names, helper names, and artifact paths can stay; story IDs, timestamps, and temporary blockers should not.
- If the source artifact contains them, preserve at least one reusable rule for each present category: validation/safety, cache or replay behavior, UX/accessibility, testing or anti-flake tactics, and environment/setup requirements.
- Name the destination in the handoff: nearby `AGENTS.md` when the rule is prompt-worthy, linked docs when the detail is too long for `AGENTS.md`.
- Do not pass one-off filenames, temporary blockers, or story-only notes as standing guidance.

### Action shapes for weaker models

- **Startup or resume before first implementer**
  1. Source of truth: `prd_file` official; `progress_file` supplemental resume data only.
  2. Resolved `progress_file`: explicit path or `dirname(prd_file) + "/progress.txt"`.
  3. Selected story: highest-priority `passes: false` story.
  4. Before story-specific discovery: dispatch fresh implementer; read only `prd_file`, `progress_file`, and nearby `AGENTS.md`.
- **After `mode: review_fix` implementer returns**
  1. Append implementer `Progress block` before acting on it.
  2. Rerun `code-simplifier` on combined final state.
  3. Rerun `requirements-collector`, then `addy-code-reviewer`.
  4. Keep `passes: true` blocked until review is clean and final checks pass.
- **When review-fix iteration limit is reached**
  1. State that the review-fix iteration limit is reached.
  2. Do not fix directly.
  3. Do not dispatch another review-fix implementer.
  4. Reread `prd_file`.
  5. Append stop-state entry to `progress_file`.
  6. Ask user to decide blocker.
- **Self-improve handoff summary**
  1. Destination: nearby `AGENTS.md` or linked docs.
  2. Reusable guidance only; no raw progress blocks, story-only notes, or transient blockers.
  3. Validation/safety: [reusable rules from source]
  4. Cache/state/replay: [reusable rules from source]
  5. UX/accessibility: [reusable rules from source]
  6. Testing/anti-flake: [reusable rules from source]
  7. Environment/setup: [reusable rules from source]

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
| "Tests passed, so story can be marked complete."                                 | No. Completion gate also requires fresh simplifier and reviewer after latest code change.                         |
| "Progress file says done, so PRD can be updated."                                | No. `prd_file` is only official completion source.                                                                |
| "Reviewer already ran earlier; rerunning is wasteful."                           | Any new `implementer` change resets finalization on combined final state.                                         |
| "One obvious note is enough; I can ignore the rest of the progress learnings."   | No. Final `self-improve` handoff must cover all durable learnings, not just the most visible one.                 |

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
- Running `self-improve` without first distilling durable learnings from `progress_file` into a reusable summary.

## Verification

Before stopping or marking completion, confirm:

- [ ] `prd_file` remained official source of story status and completion.
- [ ] `progress_file` path was resolved from explicit path or `dirname(prd_file) + "/progress.txt"`.
- [ ] Every code-affecting change came from fresh `implementer`.
- [ ] Every subagent `Progress block` was appended before being consumed.
- [ ] Simplify and review ran on combined final state after latest code-affecting change.
- [ ] Final checks ran only after clean review.
- [ ] Durable learnings were distilled from `progress_file` before invoking `self-improve`.
- [ ] `passes: true` was set only for stories that satisfied **Completion Gate**.
- [ ] Any non-`<promise>COMPLETE</promise>` response followed **Stop Conditions** and recorded stop state first.
<shellId: 0 completed with exit code 0>
````

</details>


---

<sub>⏱️ 14s</sub>

### ✅ `bash`

**Read prd.json**

$ rtk read /home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/startup-fixture/prd.json

<details>
<summary>25 lines</summary>

```
{
  "stories": [
    {
      "id": "story-auth-timeout",
      "title": "Auth timeout matches spec",
      "priority": 1,
      "passes": false,
      "requirements": [
        "Update auth timeout behavior to match spec",
        "Keep related tests green"
      ]
    },
    {
      "id": "story-status-badge",
      "title": "Status badge reflects sync health",
      "priority": 2,
      "passes": false,
      "requirements": [
        "Add sync status badge",
        "Cover success and failure states"
      ]
    }
  ]
}
<shellId: 1 completed with exit code 0>
```

</details>


---

<sub>⏱️ 17s</sub>

### ✅ `bash`

**Read progress.txt**

$ rtk read /home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/startup-fixture/progress.txt

<details>
<summary>14 lines</summary>

```
## Codebase Patterns
- Keep auth changes and auth tests together.
- Let implementer perform story-specific discovery.

## 2026-06-10T09:00:00Z - RESUME
- Role: orchestrator
- Summary: Session resumed before selecting next story.
- Files changed/reviewed: prd.json, progress.txt
- Verification or outcome: No story dispatched yet.
- **Learnings for future iterations:**
  - Pick work from `prd_file`, not from memory.
  - `progress_file` is resume data only.
  - Story-specific code reading waits for implementer.
---
<shellId: 2 completed with exit code 0>
```

</details>


---

<sub>⏱️ 26s</sub>

### ✅ `bash`

**Write decision.md**

$ cat << 'EOF' > outputs/decision.md
1. Source of truth: `prd_file` official; `progress_file` supplemental resume data only.
2. Resolved `progress_file`: /home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/startup-fixture/progress.txt
3. Selected story: story-auth-timeout
4. Before story-specific discovery: dispatch fresh implementer; read only `prd_file`, `progress_file`, and nearby `AGENTS.md`.
EOF

```

<shellId: 3 completed with exit code 0>
```


---

<sub>⏱️ 36s</sub>

### ✅ `bash`

**Ensure decision.md is correct**

$ cat << 'EOF' > outputs/decision.md
1. Source of truth: `prd_file` official; `progress_file` supplemental resume data only.
2. Resolved `progress_file`: /home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/startup-fixture/progress.txt
3. Selected story: story-auth-timeout
4. Before story-specific discovery: dispatch fresh implementer; read only `prd_file`, `progress_file`, and nearby `AGENTS.md`.
EOF

```

<shellId: 4 completed with exit code 0>
```


---

<sub>⏱️ 38s</sub>

### 💬 Copilot

1. Source of truth: `prd_file` official; `progress_file` supplemental resume data only.
2. Resolved `progress_file`: /home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/startup-fixture/progress.txt
3. Selected story: story-auth-timeout
4. Before story-specific discovery: dispatch fresh implementer; read only `prd_file`, `progress_file`, and nearby `AGENTS.md`.

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
