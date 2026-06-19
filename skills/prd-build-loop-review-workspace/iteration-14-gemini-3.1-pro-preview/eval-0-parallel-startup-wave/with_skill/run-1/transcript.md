# 🤖 Copilot CLI Session

> [!NOTE]
> - **Session ID:** `a1074fb6-5300-4ef2-990f-2ee8d760a1dc`  
> - **Started:** 6/18/2026, 10:55:05 PM  
> - **Duration:** 56s  
> - **Exported:** 6/18/2026, 10:56:01 PM  

---

<sub>⏱️ 0s</sub>

### ⚠️ Warning

Third-party MCP servers are disabled by your organization's Copilot policy. Only built-in servers are available.

---

<sub>⏱️ 1s</sub>

### 👤 User

Read and follow exact skill file at `/home/adam/dev/personal/skills/skills/prd-build-loop-review/SKILL.md`.
Ignore installed copies of `prd-build-loop-review` and any other skill with overlapping purpose; use only that file as benchmark instructions.

Benchmark constraints:
- Dry-run only.
- Do not spawn subagents.
- Do not create or modify repository files outside `/home/adam/dev/personal/skills/skills/prd-build-loop-review-workspace/iteration-14-gemini-3.1-pro-preview/eval-0-parallel-startup-wave/with_skill/run-1/outputs`.
- Read only what current prompt requires.
- Final answer must be only exact contents for `outputs/decision.md`, with no framing, explanation, or markdown fences.

Absolute input paths for this eval:
- /home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/startup-fixture/prd.json
- /home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/startup-fixture/progress.txt

Current working directory already contains `outputs/` for benchmark artifacts. Write requested file there.

Task:
Use skill under test in dry-run mode for `evals/files/startup-fixture/`. User says: `Run PRD build loop on evals/files/startup-fixture/prd.json and do not stop between stories.` Do not change files or spawn real subagents. Read only what you need, then write `outputs/decision.md` with first orchestrator actions: source of truth, resolved `progress_file`, active parallel wave, and what must happen before any story-specific repo discovery.


---

<sub>⏱️ 7s</sub>

### ✅ `bash`

**Read skill file**

$ rtk cat /home/adam/dev/personal/skills/skills/prd-build-loop-review/SKILL.md

<details>
<summary>190 lines</summary>

````
---
name: prd-build-loop-review
description: "Runs dependency-aware `prd-to-tasks` execution from `prd.json` plus `progress.txt`: resume current PRD, dispatch each ready `parallelBatch` in safe implementer waves, then run parallel simplification and requirements collection before dependent final review, verification, and exact `<promise>COMPLETE</promise>` or stop-state reply. Use whenever user wants `/prd-build-loop`, resume or finish remaining PRD stories, keep going from `prd.json`/`progress.txt`, or safely fan out multi-story implementation from `prd-to-tasks`—even if they only say 'keep going' or 'finish rest of PRD'. Not for single-story implementation, PRD authoring, or task decomposition."
disable-model-invocation: true
---

# PRD Build Loop Review

## Overview

Finish current `prd-to-tasks` `prd.json` end to end. `prd_file` is official story status; `progress_file` is append-only resume data. Orchestrator never makes code-affecting changes or commits, and only returns for exact `<promise>COMPLETE</promise>` or a real **Stop Condition**.

## When to Use

- Resume or finish autonomous work from `prd.json` plus `progress.txt`.
- Execute remaining `passes: false` `userStories` without pausing between them.
- Fan out ready stories in safe parallel waves.
- Run final simplify/requirements/review/verify/record pass after implementation.
- Not for single-story implementation, PRD authoring, or task decomposition.

## Workflow

1. **Startup**
   - Invoke `subagent-model-router`.
   - Resolve `progress_file` to explicit path or `dirname(prd_file) + "/progress.txt"`.
   - Validate `prd_file` shape before planning work: expect top-level `userStories` from `prd-to-tasks`; every unfinished story needs `id`, `title`, `priority`, `dependsOn`, `parallelBatch`, and `passes`. If file is legacy `stories` format or missing parallel fields, stop and ask user to regenerate or migrate it with `prd-to-tasks`.
   - If `progress_file` exists, read `## Codebase Patterns` plus latest relevant entries. Otherwise keep that sibling path reserved and create it there on first append with `## Codebase Patterns` at top.
   - If every story already has `passes: true`, reply exactly: `<promise>COMPLETE</promise>`.
   - If `prd_file` is ambiguous, contradictory, invalidly ordered, missing required detail, or needs human choice, stop and ask.
   - In dry-run or status outputs, use **Action shapes** below.

2. **Implementation waves**
   - Build ready set from `userStories` where `passes: false` and every `dependsOn` story already has `passes: true`.
   - If no story is ready while unfinished stories remain, stop: dependency order, prerequisite state, or PRD content is invalid.
   - Take lowest ready `parallelBatch`; that batch is only active wave.
   - Before first `implementer` for current wave, read only `prd_file`, `progress_file`, and nearby `AGENTS.md` needed to dispatch work. State explicitly: `prd_file` is official source of truth; `progress_file` is supplemental resume data only.
   - Recheck safety inside current wave. Dispatch stories in parallel only when their `filesLikelyTouched` and owner surfaces are distinct. Treat exact file overlap, same migration, same endpoint, same shared state owner, same page/form/table owner, or missing file hints on multiple stories as conflict signals.
   - For each dispatched story, use fresh `implementer` with `./implementer-prompt.md`, all story properties, `progress_file`, `mode`, current wave summary, and sibling ownership boundaries.
   - If multiple stories are parallel-safe, launch one fresh `implementer` per story in parallel and wait for every current-wave result before moving on. Serialize overlap cases by priority within same wave and record why.
   - Require `Progress block`; append each returned block to `progress_file` before acting on it.
   - Apply **Status Rules** per story.
   - If story is implemented but not finalized, record that state and leave `passes: false`.
   - Do not start higher `parallelBatch` stories until current wave is resolved.
   - Repeat until every failing story is implemented and awaiting finalization, or a **Stop Condition** applies.

3. **Single finalization pass**
   - Restore review-fix iteration count from `progress_file`; otherwise use `0`.
   - Launch fresh `code-simplifier` on relevant non-ignored combined final state and fresh `requirements-collector` for `prd_file`, relevant sibling docs, and available issue context in parallel; append each `Progress block` immediately on return.
   - Run fresh `addy-code-reviewer` only after both parallel finalization helpers finish and both `Progress block`s are recorded; append its `Progress block`.
   - If review finds issues and count is already `3`, state that limit is reached, do not fix directly, do not dispatch another review-fix `implementer`, record stop state, and ask.
   - Otherwise increment count in `progress_file`, dispatch fresh `implementer` with `mode: review_fix` and full findings, append its `Progress block`, apply **Status Rules**, then rerun `code-simplifier` and `requirements-collector` in parallel before rerunning `addy-code-reviewer` on combined final state. Keep `passes: true` blocked until review is clean and final checks pass.

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

### Input contract and path rules

- `prd_file` is only official source for story completion and status.
- `progress_file` is append-only resume and tracking data; never treat it as official completion.
- Expected input is current `prd-to-tasks` output: top-level `userStories` plus per-story `dependsOn` and `parallelBatch`.
- Resolve default path in two steps: `(1)` resolve `prd_file`, `(2)` set `progress_file = dirname(resolved prd_file) + "/progress.txt"`.
- If sibling `progress.txt` does not exist yet, keep same path and create it on first append; missing file is never permission to invent another location.
- Resolve relative paths from repo or provided `prd_file`, never from session state, scratchpads, home directories, or `~/.copilot/...`.
- In dry-run/status explanations for missing sibling `progress.txt`, say all three points explicitly: exact sibling path, `if sibling progress.txt does not exist yet, create that sibling path on first append`, and forbidden fallback path families.
- `priority` stays serial tie-breaker within same ready batch; readiness comes from `passes` plus `dependsOn`.

### Safe parallel dispatch

- **Orchestrator:** selects ready wave, resumes from `progress_file`, dispatches subagents, applies status rules, verifies final state, updates `prd_file`, appends `progress_file`, invokes `self-improve`, and records stop/final state.
- **Implementer:** does story-specific discovery, code and test changes, and initial verification.
- **Requirements collector:** dedupes requirements in parallel with simplification before final review.
- **Code simplifier:** runs after all implementation and after every review-fix implementation.
- **Reviewer:** waits for both helper outputs, then reviews combined final state.
- Any code-affecting change must be made by fresh `implementer`. Code-affecting includes code, tests, config, migrations, and implementation docs.
- Do not read story-specific repo files, tests, code, or behavior before first `implementer` for current wave.
- Pass each implementer explicit wave context: current story, sibling story IDs/titles, sibling `filesLikelyTouched`, and instruction to stay inside current story scope.
- If implementer discovers required change overlaps sibling-owned surface or unmet prerequisite work, it must return `NEEDS_CONTEXT` or `BLOCKED`; do not silently widen scope.
- In dry-run/status serialization plans, say overlap stories are serialized **instead of dispatching in parallel**, then name overlap reason and dispatch order.
- Any new `implementer` change resets finalization: rerun simplify, requirements collection, review, and final verification on combined final state.
- Never simplify, review, analyze, or change `.gitignore`-ignored files; if ignore status is unclear, skip and report uncertainty.

### Progress discipline

- Do not consume subagent output until recorded.
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

- Mine both `## Codebase Patterns` and detailed per-entry learnings in `progress_file`.
- Pass `self-improve` concise reusable rules only: validation/safety, cache/state/replay, UX/accessibility, testing/anti-flake, and environment/setup guidance.
- In dry-run/status handoff output, use these exact bucket labels: `Validation/safety`, `Cache/state/replay`, `UX/accessibility`, `Testing/anti-flake`, `Environment/setup`.
- Preserve representative concrete rules when present; drop story IDs, timestamps, temporary blockers, and one-off filenames.
- State explicitly that only reusable guidance belongs in nearby `AGENTS.md` or linked docs; story-specific notes stay out.

### Action shapes

Use these exact numbered lines verbatim in dry-run/status outputs:

- Choose exactly one matching block. Do not prepend startup lines to review-fix or finalization outputs.

- **Startup or resume before first implementer wave**
  1. Source of truth: `prd_file` official; `progress_file` supplemental resume data only.
  2. Resolved `progress_file`: explicit path or `dirname(prd_file) + "/progress.txt"`; if absent, create that sibling path on first append and never substitute session-state/home path.
  3. Active wave: lowest ready `parallelBatch` and ready story IDs.
  4. Dispatch one fresh implementer per parallel-safe story before any story-specific discovery; if stories overlap, serialize instead of dispatching them in parallel, cite the shared owner surface or exact file, give dispatch order, and do not start higher-batch work.
- **After current-wave implementers return**
  1. Append every implementer `Progress block` before acting on it.
  2. Record per-story status; unresolved stories stay `passes: false`.
  3. Do not start higher `parallelBatch` work until current wave resolves.
  4. When all implementation waves are done, run `code-simplifier` and `requirements-collector` in parallel, then `addy-code-reviewer`.
- **After `mode: review_fix` implementer returns**
  1. Append implementer `Progress block` before acting on it.
  2. Rerun `code-simplifier` and `requirements-collector` in parallel on combined final state.
  3. After both return, rerun `addy-code-reviewer`.
  4. Keep `passes: true` blocked until review is clean and final checks pass.
- **When review-fix iteration limit is reached**
  1. State that review-fix iteration limit is reached.
  2. Do not fix directly.
  3. Do not dispatch another review-fix implementer.
  4. Reread `prd_file`.
  5. Append stop-state entry to `progress_file`.
  6. Human decision required: ask user to decide blocker.
- **Before invoking `self-improve`**
  1. Mine `## Codebase Patterns` and every `Learnings for future iterations` block, including patterns, gotchas, and useful context.
  2. Pass only reusable guidance into nearby `AGENTS.md` or linked docs, not story-specific notes, raw tracking data, story IDs, timestamps, temporary blockers, or one-off filenames.
  3. Preserve durable rules under exact bucket labels: `Validation/safety`, `Cache/state/replay`, `UX/accessibility`, `Testing/anti-flake`, and `Environment/setup`.
  4. Preserve staged production-artifact startup-test guidance such as `wwwroot/dist/browser/index.html` when present.

### Completion Gate

Mark story complete only if all are true:

1. Required implementation was completed by fresh `implementer`.
2. Latest code-affecting change touching that story or combined final state was made by fresh `implementer`.
3. Fresh `code-simplifier` ran after latest code-affecting change.
4. Fresh `requirements-collector` ran after latest code-affecting change and before final review.
5. Fresh `addy-code-reviewer` ran after latest code-affecting change.
6. If review found issues, fresh `implementer` fixed them and simplify/requirements/review reran after that fix.
7. Review is clean for final state.
8. Required final-state quality checks passed.

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
- `prd_file` has contradictions, invalid dependency ordering, or missing required details needing human correction
- no unfinished story is ready because prerequisite state is invalid or incomplete
- required human decision is needed
- review-fix iteration limit is reached
- final verification failed and needs human decision

## Common Rationalizations

| Rationalization | Reality |
| --- | --- |
| "Same `parallelBatch` means I can dispatch everything blindly." | No. Recheck file/owner overlap; serialize ambiguous stories before dispatch. |
| "I can start later-batch work while one story from current wave is unresolved." | No. Resolve current wave first; later batches stay blocked. |
| "Legacy `stories` format is close enough." | No. This skill expects current `prd-to-tasks` output with `userStories`, `dependsOn`, and `parallelBatch`. |
| "Parallel implementer found sibling-owned file; widening scope is faster." | No. Return `NEEDS_CONTEXT` or `BLOCKED` instead of silently stealing sibling scope. |
| "Tests passed, so story can be marked complete." | No. **Completion Gate** still requires fresh simplifier, fresh requirements collection, clean review, and final checks after latest change. |

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

## Verification

Before stopping or marking completion, confirm:

- [ ] `prd_file` remained official source of story status and completion.
- [ ] `progress_file` path was resolved from explicit path or `dirname(prd_file) + "/progress.txt"`, even when sibling `progress.txt` did not exist yet.
- [ ] Ready work was selected from `userStories` using `passes`, `dependsOn`, and lowest ready `parallelBatch`.
- [ ] Parallel dispatch was limited to non-overlapping stories; ambiguous overlaps were serialized or escalated.
- [ ] Every code-affecting change came from fresh `implementer`.
- [ ] Every subagent `Progress block` was appended before being consumed.
- [ ] `code-simplifier` and `requirements-collector` ran after latest code-affecting change, and `addy-code-reviewer` ran only after both returned.
- [ ] Final checks ran only after clean review.
- [ ] Durable learnings were distilled from `progress_file` before invoking `self-improve`.
- [ ] `passes: true` was set only for stories that satisfied **Completion Gate**.
- [ ] Any non-`<promise>COMPLETE</promise>` response followed **Stop Conditions** and recorded stop state first.
<shellId: 0 completed with exit code 0>
````

</details>


---

<sub>⏱️ 12s</sub>

### ✅ `bash`

**Read prd.json**

$ rtk read /home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/startup-fixture/prd.json

<details>
<summary>91 lines</summary>

```
{
  "project": "Auth Timeout Fanout",
  "branchName": "auth-timeout-fanout",
  "description": "Apply shared auth timeout policy across login and status surfaces.",
  "userStories": [
    {
      "id": "US-001",
      "title": "Persist shared auth timeout policy",
      "description": "As a platform owner, I want one shared auth timeout policy so dependent flows use the same rules.",
      "acceptanceCriteria": [
        "Shared auth timeout policy exists in one reusable location",
        "Typecheck passes"
      ],
      "filesLikelyTouched": [
        "src/auth/timeout_policy.ts",
        "tests/auth/timeout_policy.test.ts"
      ],
      "designGuidance": [],
      "priority": 1,
      "dependsOn": [],
      "parallelBatch": 1,
      "passes": true,
      "notes": ""
    },
    {
      "id": "US-002",
      "title": "Apply timeout policy to login flow",
      "description": "As a user, I want login timeout handling to reuse shared policy so behavior stays consistent.",
      "acceptanceCriteria": [
        "Login flow reads shared auth timeout policy",
        "Typecheck passes"
      ],
      "filesLikelyTouched": [
        "src/auth/login_flow.ts",
        "tests/auth/login_flow.test.ts"
      ],
      "designGuidance": [],
      "priority": 2,
      "dependsOn": [
        "US-001"
      ],
      "parallelBatch": 2,
      "passes": false,
      "notes": ""
    },
    {
      "id": "US-003",
      "title": "Show timeout status badge",
      "description": "As a user, I want a timeout status badge so I can see when auth policy is active.",
      "acceptanceCriteria": [
        "Status badge reflects timeout policy state",
        "Typecheck passes",
        "Verify in browser using playwright-cli skill"
      ],
      "filesLikelyTouched": [
        "src/ui/TimeoutStatusBadge.tsx",
        "tests/ui/TimeoutStatusBadge.test.tsx"
      ],
      "designGuidance": [],
      "priority": 3,
      "dependsOn": [
        "US-001"
      ],
      "parallelBatch": 2,
      "passes": false,
      "notes": ""
    },
    {
      "id": "US-004",
      "title": "Log timeout audit events",
      "description": "As an operator, I want audit events for timeout enforcement so support can trace auth failures.",
      "acceptanceCriteria": [
        "Audit event records timeout enforcement",
        "Typecheck passes"
      ],
      "filesLikelyTouched": [
        "src/audit/timeout_events.ts",
        "tests/audit/timeout_events.test.ts"
      ],
      "designGuidance": [],
      "priority": 4,
      "dependsOn": [
        "US-002"
      ],
      "parallelBatch": 3,
      "passes": false,
      "notes": ""
    }
  ]
}
<shellId: 1 completed with exit code 0>
```

</details>


---

<sub>⏱️ 12s</sub>

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

<sub>⏱️ 52s</sub>

### ✅ `create`

**create a new file at /home/adam/dev/personal/skills/skills/prd-build-loop-review-workspace/iteration-14-gemini-3.1-pro-preview/eval-0-parallel-startup-wave/with_skill/run-1/outputs/decision.md.**

/home/adam/dev/personal/skills/skills/prd-build-loop-review-workspace/iteration-14-gemini-3.1-pro-preview/eval-0-parallel-startup-wave/with_skill/run-1/outputs/decision.md

```
Created file /home/adam/dev/personal/skills/skills/prd-build-loop-review-workspace/iteration-14-gemini-3.1-pro-preview/eval-0-parallel-startup-wave/with_skill/run-1/outputs/decision.md with 667 characters
```


---

<sub>⏱️ 55s</sub>

### 💬 Copilot

1. Source of truth: `prd_file` official; `progress_file` supplemental resume data only.
2. Resolved `progress_file`: /home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/startup-fixture/progress.txt; if absent, create that sibling path on first append and never substitute session-state/home path.
3. Active wave: lowest ready `parallelBatch` 2 and ready story IDs US-002, US-003.
4. Dispatch one fresh implementer per parallel-safe story before any story-specific discovery; if stories overlap, serialize instead of dispatching them in parallel, cite the shared owner surface or exact file, give dispatch order, and do not start higher-batch work.

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
