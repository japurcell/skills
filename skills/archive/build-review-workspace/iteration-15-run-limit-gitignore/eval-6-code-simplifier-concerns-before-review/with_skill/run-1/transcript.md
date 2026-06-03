# 🤖 Copilot CLI Session

> [!NOTE]
>
> - **Session ID:** `4ebf2244-80bf-4ef2-9db1-cd14fc69b4e3`
> - **Started:** 5/7/2026, 11:49:03 AM
> - **Duration:** 19s
> - **Exported:** 5/7/2026, 11:49:23 AM

---

<sub>⏱️ 2s</sub>

### 👤 User

You are running a build-review skill benchmark. Use only this exact skill file as the build-review skill: /Users/adam/Development/skills/skills/build-review/SKILL.md. Ignore any installed skill with the same name unless it is this exact file. Read the file if needed, but do not modify files, do not run repository validation, and do not create commits or artifacts. Answer the task directly and concisely.

Task:
Every task in the current build wave is already marked done in `.agents/scratchpad/auth/plan.md`, `.agents/scratchpad/auth/todo.md`, and the SQL `todos` table. Then the code-simplifier returned `DONE_WITH_CONCERNS`: the change is smaller now, but one extracted helper may have widened scope and could hide a behavior change. Using the build workflow, what should the manager do next?

---

<sub>⏱️ 13s</sub>

### 💬 Copilot

I’ll read the exact benchmark skill file and answer from that source only.

---

<sub>⏱️ 14s</sub>

### ✅ `view`

**view the file at /Users/adam/Development/skills/skills/build-review/SKILL.md.**

/Users/adam/Development/skills/skills/build-review/SKILL.md

<details>
<summary>157 lines</summary>

```
1. ---
2. name: build-review
3. description: Coordinate the current implementation wave. Use when the plan already has the next ready task or small ready set and you need a manager-led workflow that dispatches implementers with lean handoffs, keeps active trackers in sync, then runs exactly one code-simplifier wave and one code-reviewer wave over the filtered uncommitted surface before handing the work back uncommitted.
4. ---
5.
6. # Build Review
7.
8. ## Overview
9.
10. Use this skill to run a manager-led implementation wave: pick the next ready task, dispatch subagents with lean handoffs, then route the resulting surface through one simplifier wave and one reviewer wave before handing the work back uncommitted. It matters because the manager must coordinate progress, tracking, and bounded review without stealing repo discovery, design, implementation, or verification work from the subagents.
11.
12. ## When to Use
13.
14. - Use when the plan already has a next ready task or small ready set and you need to execute that wave through implementation, one simplification wave, one review wave, and tracking.
15. - Use when you need a manager/subagent boundary: the manager coordinates, while implementers own repo discovery, first-pass design, code changes, and validation.
16. - Use when downstream review must cover the full uncommitted surface, not just the file from one finished task.
17. - Do **not** use this skill for planning, specs, or unresolved tradeoff analysis. Resolve ambiguity first.
18.
19. ## Workflow
20.
21. 1. Invoke the `addy-context-engineering` and `subagent-model-router` skills.
22. 2. Define the current build wave: the next ready task, or a small explicit set of already-ready independent tasks. A wave of one is the default.
23. 3. Identify the active trackers already in play for that wave. In this repo that usually means `plan.md`, `todo.md`, and SQL todo state. Reuse the same task names or IDs across them, and do **not** invent a new tracker mid-wave.
24. 4. If any task is ambiguous, conflicts with the plan, or the human wants tradeoff analysis first, resolve that before dispatch.
25. 5. For each task in the wave, dispatch immediately with [implementer-prompt.md](./implementer-prompt.md) and only:
26.    - task text and success criteria
27.    - known constraints and validation commands
28.    - already-known file hints
29. 6. When an implementer returns `DONE`, run one task-complete tracking sync immediately before anything else and before dispatching the next subagent: update that same task across every active tracker (`plan.md`, `todo.md`, and SQL todo state when present), record the verification actually performed, and confirm the trackers agree before you move on. If another task remains in the wave, say so plainly and dispatch that remaining task next.
30. 7. If any task in the current wave is still unfinished, keep dispatching implementers. Do **not** start code-simplifier yet. Wait until every task in the current wave is implemented and marked done before any code-simplifier or code-review work starts. Say that exact delay plainly when work remains.
31. 8. After every task in the wave has been implemented and marked done, build one deduped `review_scope_files` list from:
32.     - every file any implementer touched in the wave
33.     - all uncommitted files from `git status --porcelain`, excluding deleted files, `.gitignore` itself, and any path ignored by git
34. 9. Dispatch code-simplifier subagents over manager-authored `review_scope_files` partitions using [simplifier-prompt.md](./simplifier-prompt.md).
35. 10. After the code-simplifier wave completes, dispatch exactly one code-reviewer wave over the same partitions using [code-reviewer-prompt.md](./code-reviewer-prompt.md). If simplifier concerns caused fixes before review, do **not** run another simplifier wave; continue to the single reviewer wave after the owning subagent fixes and verifies.
36. 11. If every reviewer returns `DONE`, run one final reviewed tracking sync across the same active trackers, record any additional verification actually performed during review, and confirm the same final reviewed state matches everywhere. If any reviewer returns findings and those findings cause fixes, do **not** run another simplifier or reviewer wave in this invocation; say `the final reviewed sync does not happen yet` and hand off the unreviewed post-review fixes plainly. In both cases, say the handoff plainly: do **not** create or publish a commit, PR, or tag, and leave the changes uncommitted and local.
37.
38. ## Specific Techniques
39.
40. ### Role Boundaries
41.
42. - The manager owns wave selection, dispatch, tracking, `review_scope_files`, review partitions, and the final reviewed sync.
43. - The implementer owns repo discovery, pattern lookup, first-pass design, code changes, and verification.
44. - Dispatch as soon as the task is clear enough. Do **not** pre-read large file sets, draft the solution, sketch likely patches, or run verification on the implementer's behalf.
45. - Ordinary repo exploration is never a valid `NEEDS_CONTEXT`. Only missing requirements, missing constraints, or conflicting signals qualify.
46. - Leave the working tree dirty. Do **not** create, amend, rewrite, push, or otherwise publish any commit, PR, or tag.
47.
48. ### Review Fanout
49.
50. 1. A wave is one parallel dispatch over all partitions of `review_scope_files`. A wave can contain multiple partitioned subagents; it is still one wave.
51. 2. Materialize `review_scope_files` once after the full wave is implemented, dedupe it, filter it, and keep stable order.
52. 3. Filter out any path ignored by git before partitioning. Check the union of implementer-touched files and `git status --porcelain` paths with `git check-ignore --stdin`; exit code 1 only means no ignored paths were found. Do not pass ignored paths to code-simplifier or code-reviewer, even if an implementer touched them.
53. 4. **<=5 files:** launch one code-simplifier or code-reviewer over the full list.
54. 5. **>5 files:** partition files into non-overlapping groups by module, directory, or logical area so each file appears in exactly one downstream scope.
55. 6. The manager owns the partitions. Simplifiers and reviewers use only the exact file list they are given; they do not recompute, expand, narrow, or add gitignored paths to scope.
56. 7. Reuse the same partitions for code-simplifier and code-review. Later fixes do not trigger fresh partitions or a second simplifier/reviewer wave in this invocation.
57.
58. ### Single-Pass Review Budget
59.
60. - After implementation is finished, run one code-simplifier wave and one code-reviewer wave. This bounds runtime and token use.
61. - A `BLOCKED` or `NEEDS_CONTEXT` retry is still part of completing the same wave when you change context, scope, or model. It is not permission to start a second quality gate after findings are fixed.
62. - If code-simplifier concerns lead to fixes, route the fix to the owning subagent, sync/reopen/re-close tracking as appropriate for the implementation fix, and continue to the single code-reviewer wave. Do **not** run another code-simplifier wave.
63. - If code-reviewer findings lead to fixes, route the fix to the owning subagent and record the exact verification performed. Do **not** run another code-simplifier or code-reviewer wave in the same invocation.
64. - When fixes happen after the single review wave, say `the final reviewed sync does not happen yet`, leave the affected task visibly not-final-reviewed in every active tracker, and hand off that another build-review wave can provide a fresh quality gate if desired.
65.
66. ### Verification Selection
67.
68. - Verification ownership stays with the implementer.
69. - Infer the task's surface and stack before choosing validation.
70. - Prefer the narrowest matching checks for that stack. Shell or Python work should use shell or Python validation instead of generic frontend commands unless the task is actually frontend work.
71.
72. ### Tracking Sync
73.
74. 1. Reuse the trackers that already exist for the current plan. In this repo that usually means `plan.md`, `todo.md`, and SQL todo rows.
75. 2. Apply each status change to all active trackers together. Do **not** update `todo.md` now and promise to catch up `plan.md` or SQL later.
76. 3. Keep the same task identity and status across trackers. If downstream work reopens a task, reopen it everywhere.
77. 4. If one tracker is absent for the current build, sync the trackers that do exist. Do **not** create a new tracker mid-wave just to satisfy this skill.
78. 5. Before dispatching the next subagent, confirm the active trackers agree. Say it plainly when needed: `plan.md`, `todo.md`, and SQL todo state all say the same status before moving on. Prefer the exact phrase `SQL todo state` over a vague `SQL`. Any tracker mismatch is incomplete work.
79.
80. ### Status Handling
81.
82. #### Implementer
83.
84. - **DONE:** run the task-complete tracking sync immediately across every active tracker before moving on or dispatching Task B / the next subagent. If more tasks remain in the wave, say `dispatch the remaining task next` or `continue the current wave by dispatching Task B`, then keep dispatching implementers; otherwise start code-simplifier.
85. - **DONE_WITH_CONCERNS:** read the concerns before any tracking update. If they raise correctness or scope risk, address them first, usually by re-dispatching an implementer. Do **not** mark the task done yet.
86. - **NEEDS_CONTEXT:** only valid for missing requirements, missing constraints, or conflicting signals. Routine discovery stays with the implementer.
87. - **BLOCKED:** follow the escalation ladder.
88.
89. #### Code-Simplifier
90.
91. - **DONE:** when every simplifier is `DONE`, proceed to code-review.
92. - **DONE_WITH_CONCERNS:** begin by saying `read the code-simplifier's concerns before continuing to code-reviewer.` Treat correctness or scope concerns as unresolved work. Reopen any affected done task immediately across every active tracker, re-dispatch the subagent that should own the fix, and do **not** proceed to code-reviewer yet. After the owning subagent fixes and verifies, do **not** run another code-simplifier wave; continue to the single code-reviewer wave.
93. - **NEEDS_CONTEXT:** provide the missing context and re-dispatch.
94. - **BLOCKED:** follow the escalation ladder.
95.
96. #### Code-Reviewer
97.
98. - **DONE:** when every reviewer is `DONE`, run the final reviewed tracking sync across every active tracker, record any additional verification actually performed during review, and say `do not create or publish a commit, PR, or tag` plus `leave the changes uncommitted and local`.
99. - **DONE_WITH_FINDINGS:** address findings before ending the wave. Reopen any affected done task immediately across every active tracker and route the fix to the subagent that should own it instead of patching inline. After fixes and verification, do **not** rerun code-simplifier or code-reviewer partitions in this invocation. Say `the final reviewed sync does not happen yet`, leave affected work visibly not-final-reviewed in every active tracker, and hand off the unreviewed post-review fixes.
100. - **NEEDS_CONTEXT:** provide the missing context and re-dispatch.
101. - **BLOCKED:** follow the escalation ladder.
102.
103. ### Escalation Ladder
104.
105. When a subagent returns `BLOCKED`:
106.
107. 1. If it is a context problem, provide more context and re-dispatch with the same model.
108. 2. If it needs more reasoning, re-dispatch with a more capable model.
109. 3. If the task or partition is too large, split it into smaller pieces.
110. 4. If the plan itself is wrong, escalate to the human.
111.
112. Never ignore an escalation or rerun the same stuck attempt without changing context, scope, or model.
113.
114. ### Tracking Discipline
115.
116. - A partial sync is not a sync. When `plan.md`, `todo.md`, and SQL todo state are active, they move together immediately, before the next dispatch.
117. - If `todo.md` and SQL already say `done`, `plan.md` cannot stay stale. Say that plainly instead of only saying `partial sync`.
118. - Reopen any done task immediately in every active tracker if downstream simplifier or reviewer work changes it or questions its correctness or scope.
119. - Re-close a task only when its required pass has not been spent yet. If reviewer findings caused post-review fixes, do not mark the task final-reviewed in this invocation because there is no second reviewer wave.
120. - Treat stale docs, stale SQL status, or tracker disagreement as incomplete work.
121. - Final handoff language should be explicit: sync the same final reviewed state, record any additional verification from review, say `do not create or publish a commit, PR, or tag`, and say `leave the changes uncommitted and local`.
122. - If post-review fixes exist, replace the final reviewed sync with an explicit handoff: say `the final reviewed sync does not happen yet`, list the unreviewed fixes and verification, and say another build-review wave is the fresh quality gate.
123.
124. ## Common Rationalizations
125.
126. | Rationalization | Reality |
127. | --- | --- |
128. | "I should read the repo and sketch the patch before I dispatch." | That steals implementer work and pushes the manager out of coordination mode. Dispatch once the task is clear enough. |
129. | "The implementer has not explored the repo yet, so `NEEDS_CONTEXT` is fine." | Ordinary repo discovery, pattern lookup, and first-pass design belong to the implementer. `NEEDS_CONTEXT` is only for missing requirements, constraints, or conflicting signals. |
130. | "One task in the wave is done, so I can start code-simplifier now." | Downstream review starts only after every task in the current wave is implemented and marked done. Say `do not start code-simplifier yet` when work remains in the wave. |
131. | "`todo.md` is already updated, so I can fix `plan.md` or SQL later." | Partial tracker sync is a workflow failure. Update every active tracker together before the next dispatch. |
132. | "Once review is done I can commit or open the PR for the human." | This skill explicitly leaves the work dirty and unpublished. The human handles any commit or PR later. |
133. | "A reviewer found issues, so I should rerun simplifier and reviewer after the fixes." | That creates unbounded loops. Run one simplifier wave and one reviewer wave; hand off post-review fixes as not-final-reviewed. |
134. | "The implementer touched an ignored file, so review should include it." | Gitignored files are outside the review budget. Filter them before simplifier and reviewer dispatch, even if a subagent mentioned them. |
135.
136. ## Red Flags
137.
138. - The manager reads large file sets, proposes a patch, or runs validation before dispatching a clear task.
139. - An implementer asks for `NEEDS_CONTEXT` just to avoid ordinary repo exploration.
140. - A simplifier or reviewer recomputes scope instead of using the exact manager-authored file list.
141. - A simplifier or reviewer receives a gitignored file, deleted file, or `.gitignore` itself in its scope.
142. - A reviewer finding triggers a second code-simplifier or code-reviewer wave in the same invocation.
143. - A downstream concern or finding surfaces, but the affected task stays marked `done`.
144. - `plan.md`, `todo.md`, and SQL todo state disagree about the same task.
145. - Any step creates or publishes a commit, PR, or tag.
146.
147. ## Verification
148.
149. After completing the build wave, confirm:
150.
151. - [ ] Each implementer `DONE` updated every active tracker for that task — typically `plan.md`, `todo.md`, and SQL todo state — before the next dispatch, and recorded the verification actually performed.
152. - [ ] `review_scope_files` was deduped, filtered with gitignored/deleted/`.gitignore` paths removed, manager-authored, and reused across the single simplifier and reviewer waves.
153. - [ ] Code-simplifier and code-review started only after the full wave was implemented and marked done.
154. - [ ] No second code-simplifier or code-reviewer wave ran after concerns, findings, or fixes; `BLOCKED`/`NEEDS_CONTEXT` retries only completed the original wave.
155. - [ ] Any reopened task was reopened across every active tracker, and post-review fixes were handed off as not-final-reviewed instead of silently re-closing them.
156. - [ ] The final reviewed sync leaves `plan.md`, `todo.md`, and SQL todo state aligned when every reviewer returned `DONE`; otherwise the handoff says `the final reviewed sync does not happen yet`, and the working tree remains dirty and unpublished.
157.
```

</details>

---

<sub>⏱️ 19s</sub>

### 💬 Copilot

read the code-simplifier's concerns before continuing to code-reviewer.

Because the concern is about widened scope and possible behavior change, the manager should treat it as unresolved work: immediately reopen the affected done task in `.agents/scratchpad/auth/plan.md`, `.agents/scratchpad/auth/todo.md`, and SQL todo state, then re-dispatch the owning implementer/subagent to fix and verify that helper’s scope/behavior.

Do **not** proceed to code-reviewer yet. After the owning subagent fixes and verifies it, do **not** run another code-simplifier wave; continue directly to the single code-reviewer wave over the same review partitions.

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
