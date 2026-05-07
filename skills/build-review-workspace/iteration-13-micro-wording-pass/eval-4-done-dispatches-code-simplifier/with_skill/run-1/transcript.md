# 🤖 Copilot CLI Session

> [!NOTE]
> - **Session ID:** `12a277ef-99f3-436e-8e5f-88224d5f5932`  
> - **Started:** 5/7/2026, 11:13:40 AM  
> - **Duration:** 1m 15s  
> - **Exported:** 5/7/2026, 11:14:56 AM  

---

<sub>⏱️ 0s</sub>

### ⚠️ Warning

Third-party MCP servers are disabled by your organization's Copilot policy. Only built-in servers are available.

---

<sub>⏱️ 1s</sub>

### 👤 User

Read and follow only this build-review skill file: /home/adam/dev/personal/skills/skills/build-review/SKILL.md
Ignore any other installed copies of build-review.
After reading it, answer the user's scenario concisely as the manager. Do not use any tools after reading the skill file.

User scenario:
The manager is running a build wave of two ready tasks. Task A's implementer returned `DONE` with passing verification and touched four files. Task B is still part of the current wave and has not been dispatched yet. This build is tracked in `.agents/scratchpad/issues/plan.md`, `.agents/scratchpad/issues/todo.md`, and the SQL `todos` table row `api-issues-pagination`. Using the build workflow, what should the manager sync now, and should the code-simplifier wave start yet?

---

<sub>⏱️ 31s</sub>

### 💬 Copilot

I’m reading the specified build-review skill file, then I’ll answer the scenario from that workflow only.

---

<sub>⏱️ 31s</sub>

### ✅ `skill`

**addy-using-agent-skills**

<details>
<summary>Arguments</summary>

```json
{
  "skill": "addy-using-agent-skills"
}
```

</details>

```
Skill "addy-using-agent-skills" loaded successfully. Follow the instructions in the skill context.
```


---

<sub>⏱️ 31s</sub>

### ✅ `skill`

**addy-context-engineering**

<details>
<summary>Arguments</summary>

```json
{
  "skill": "addy-context-engineering"
}
```

</details>

```
Skill "addy-context-engineering" loaded successfully. Follow the instructions in the skill context.
```


---

<sub>⏱️ 31s</sub>

### ✅ `view`

**view the file at /home/adam/dev/personal/skills/skills/build-review/SKILL.md.**

/home/adam/dev/personal/skills/skills/build-review/SKILL.md

```
File too large to read at once (11.8 KB). Consider using the grep tool to search within the file, or view with view_range to read specific sections.
```


---

<sub>⏱️ 43s</sub>

### 💬 Copilot

The first read was truncated, so I’m reading the specified skill file in chunks and then I’ll answer without any more tool use.

---

<sub>⏱️ 43s</sub>

### ✅ `view`

**view the file at /home/adam/dev/personal/skills/skills/build-review/SKILL.md.**

/home/adam/dev/personal/skills/skills/build-review/SKILL.md (lines 1-150)

<details>
<summary>118 lines</summary>

```
1. ---
2. name: build-review
3. description: Coordinate the current implementation wave. Use when the plan already has the next ready task or small ready set and you need a manager-led workflow that dispatches implementers with lean handoffs, keeps active trackers in sync, then runs code-simplifier and code-reviewer waves over the full uncommitted surface before handing the work back uncommitted.
4. ---
5. 
6. # Build Review
7. 
8. ## Overview
9. 
10. Use this skill to run a manager-led implementation wave: pick the next ready task, dispatch subagents with lean handoffs, then route the resulting surface through simplifier and reviewer waves before handing the work back uncommitted. It matters because the manager must coordinate progress and tracking without stealing repo discovery, design, implementation, or verification work from the subagents.
11. 
12. ## When to Use
13. 
14. - Use when the plan already has a next ready task or small ready set and you need to execute that wave through implementation, simplification, review, and tracking.
15. - Use when you need a manager/subagent boundary: the manager coordinates, while implementers own repo discovery, first-pass design, code changes, and validation.
16. - Use when downstream review must cover the full uncommitted surface, not just the file from one finished task.
17. - Do **not** use this skill for planning, specs, or unresolved tradeoff analysis. Resolve ambiguity first.
18. 
19. ## Workflow
20. 
21. 1. Invoke the `addy-context-engineering` and `subagent-model-selection` skills.
22. 2. Define the current build wave: the next ready task, or a small explicit set of already-ready independent tasks. A wave of one is the default.
23. 3. Identify the active trackers already in play for that wave. In this repo that usually means `plan.md`, `todo.md`, and SQL todo state. Reuse the same task names or IDs across them, and do **not** invent a new tracker mid-wave.
24. 4. If any task is ambiguous, conflicts with the plan, or the human wants tradeoff analysis first, resolve that before dispatch.
25. 5. For each task in the wave, dispatch immediately with [implementer-prompt.md](./implementer-prompt.md) and only:
26.    - task text and success criteria
27.    - known constraints and validation commands
28.    - already-known file hints
29. 6. When an implementer returns `DONE`, run one task-complete tracking sync immediately before anything else and before dispatching the next subagent: update that same task across every active tracker (`plan.md`, `todo.md`, and SQL todo state when present), record the verification actually performed, and confirm the trackers agree before you move on.
30. 7. If any task in the current wave is still unfinished, keep dispatching implementers. Do **not** start code-simplifier yet. Wait until every task in the current wave is implemented and marked done before any code-simplifier or code-review work starts. Say that exact delay plainly when work remains.
31. 8. After every task in the wave has been implemented and marked done, build one deduped `review_scope_files` list from:
32.    - every file any implementer touched in the wave
33.    - all uncommitted files from `git status --porcelain`, excluding deleted files and `.gitignore` files
34. 9. Dispatch code-simplifier subagents over manager-authored `review_scope_files` partitions using [simplifier-prompt.md](./simplifier-prompt.md).
35. 10. After every code-simplifier returns `DONE`, dispatch code-reviewer subagents over the same partitions using [code-reviewer-prompt.md](./code-reviewer-prompt.md), unless a later fix changes the surface enough to require fresh partitions.
36. 11. After every reviewer returns `DONE`, run one final reviewed tracking sync across the same active trackers, record any additional verification actually performed during review, and confirm the same final reviewed state matches everywhere. Then say the final handoff plainly: do **not** create or publish a commit, PR, or tag, and leave the changes uncommitted and local.
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
50. 1. Materialize `review_scope_files` once after the full wave is implemented, dedupe it, and keep stable order.
51. 2. **<=5 files:** launch one code-simplifier or code-reviewer over the full list.
52. 3. **>5 files:** partition files into non-overlapping groups by module, directory, or logical area so each file appears in exactly one downstream scope.
53. 4. The manager owns the partitions. Simplifiers and reviewers use only the exact file list they are given; they do not recompute or narrow scope.
54. 5. Reuse the same partitions for code-simplifier and code-review unless a later fix changes the touched surface.
55. 
56. ### Verification Selection
57. 
58. - Verification ownership stays with the implementer.
59. - Infer the task's surface and stack before choosing validation.
60. - Prefer the narrowest matching checks for that stack. Shell or Python work should use shell or Python validation instead of generic frontend commands unless the task is actually frontend work.
61. 
62. ### Tracking Sync
63. 
64. 1. Reuse the trackers that already exist for the current plan. In this repo that usually means `plan.md`, `todo.md`, and SQL todo rows.
65. 2. Apply each status change to all active trackers together. Do **not** update `todo.md` now and promise to catch up `plan.md` or SQL later.
66. 3. Keep the same task identity and status across trackers. If downstream work reopens a task, reopen it everywhere.
67. 4. If one tracker is absent for the current build, sync the trackers that do exist. Do **not** create a new tracker mid-wave just to satisfy this skill.
68. 5. Before dispatching the next subagent, confirm the active trackers agree. Say it plainly when needed: `plan.md`, `todo.md`, and SQL todo state all say the same status before moving on. Prefer the exact phrase `SQL todo state` over a vague `SQL`. Any tracker mismatch is incomplete work.
69. 
70. ### Status Handling
71. 
72. #### Implementer
73. 
74. - **DONE:** run the task-complete tracking sync immediately across every active tracker before moving on or dispatching Task B / the next subagent. If more tasks remain in the wave, keep dispatching implementers; otherwise start code-simplifier.
75. - **DONE_WITH_CONCERNS:** read the concerns before any tracking update. If they raise correctness or scope risk, address them first, usually by re-dispatching an implementer. Do **not** mark the task done yet.
76. - **NEEDS_CONTEXT:** only valid for missing requirements, missing constraints, or conflicting signals. Routine discovery stays with the implementer.
77. - **BLOCKED:** follow the escalation ladder.
78. 
79. #### Code-Simplifier
80. 
81. - **DONE:** when every simplifier is `DONE`, proceed to code-review.
82. - **DONE_WITH_CONCERNS:** begin by saying `read the code-simplifier's concerns before continuing to code-reviewer.` Treat correctness or scope concerns as unresolved work. Reopen any affected done task immediately across every active tracker, re-dispatch the subagent that should own the fix, and do **not** proceed to code-reviewer yet.
83. - **NEEDS_CONTEXT:** provide the missing context and re-dispatch.
84. - **BLOCKED:** follow the escalation ladder.
85. 
86. #### Code-Reviewer
87. 
88. - **DONE:** when every reviewer is `DONE`, run the final reviewed tracking sync across every active tracker, record any additional verification actually performed during review, and say `do not create or publish a commit, PR, or tag` plus `leave the changes uncommitted and local`.
89. - **DONE_WITH_FINDINGS:** address findings before ending the wave. Reopen any affected done task immediately across every active tracker, route the fix to the subagent that should own it, then rerun the affected code-simplifier and reviewer partitions as needed. Re-sync tracking only after every reviewer returns `DONE`.
90. - **NEEDS_CONTEXT:** provide the missing context and re-dispatch.
91. - **BLOCKED:** follow the escalation ladder.
92. 
93. ### Escalation Ladder
94. 
95. When a subagent returns `BLOCKED`:
96. 
97. 1. If it is a context problem, provide more context and re-dispatch with the same model.
98. 2. If it needs more reasoning, re-dispatch with a more capable model.
99. 3. If the task or partition is too large, split it into smaller pieces.
100. 4. If the plan itself is wrong, escalate to the human.
101. 
102. Never ignore an escalation or rerun the same stuck attempt without changing context, scope, or model.
103. 
104. ### Tracking Discipline
105. 
106. - A partial sync is not a sync. When `plan.md`, `todo.md`, and SQL todo state are active, they move together immediately, before the next dispatch.
107. - Reopen any done task immediately in every active tracker if downstream simplifier or reviewer work changes it or questions its correctness or scope.
108. - Re-close that task only after the affected downstream passes return `DONE`, and re-close it in every active tracker.
109. - Treat stale docs, stale SQL status, or tracker disagreement as incomplete work.
110. - Final handoff language should be explicit: sync the same final reviewed state, record any additional verification from review, say `do not create or publish a commit, PR, or tag`, and say `leave the changes uncommitted and local`.
111. 
112. ## Common Rationalizations
113. 
114. | Rationalization | Reality |
115. | --- | --- |
116. | "I should read the repo and sketch the patch before I dispatch." | That steals implementer work and pushes the manager out of coordination mode. Dispatch once the task is clear enough. |
117. | "The implementer has not explored the repo yet, so `NEEDS_CONTEXT` is fine." | Ordinary repo discovery, pattern lookup, and first-pass design belong to the implementer. `NEEDS_CONTEXT` is only for missing requirements, constraints, or conflicting signals. |

[Output truncated. Use view_range=[118, ...] to continue reading. In your next response, you may batch this with other view calls. File has at least 140 lines.]
```

</details>


---

<sub>⏱️ 43s</sub>

### ✅ `view`

**view the file at /home/adam/dev/personal/skills/skills/build-review/SKILL.md.**

/home/adam/dev/personal/skills/skills/build-review/SKILL.md (lines 151-300)

<details>
<summary>5 lines</summary>

```diff

diff --git a/home/adam/dev/personal/skills/skills/build-review/SKILL.md b/home/adam/dev/personal/skills/skills/build-review/SKILL.md
index 0000000..0000000 100644
--- a/home/adam/dev/personal/skills/skills/build-review/SKILL.md
+++ b/home/adam/dev/personal/skills/skills/build-review/SKILL.md
@@ -151,150 +151,150 @@
```

</details>


---

<sub>⏱️ 44s</sub>

### ✅ `view`

**view the file at /home/adam/dev/personal/skills/skills/build-review/SKILL.md.**

/home/adam/dev/personal/skills/skills/build-review/SKILL.md (lines 301-450)

<details>
<summary>5 lines</summary>

```diff

diff --git a/home/adam/dev/personal/skills/skills/build-review/SKILL.md b/home/adam/dev/personal/skills/skills/build-review/SKILL.md
index 0000000..0000000 100644
--- a/home/adam/dev/personal/skills/skills/build-review/SKILL.md
+++ b/home/adam/dev/personal/skills/skills/build-review/SKILL.md
@@ -301,150 +301,150 @@
```

</details>


---

<sub>⏱️ 50s</sub>

### ✅ `view`

**view the file at /home/adam/dev/personal/skills/skills/build-review/SKILL.md.**

/home/adam/dev/personal/skills/skills/build-review/SKILL.md (lines 118-220)

<details>
<summary>23 lines</summary>

```
118. | "One task in the wave is done, so I can start code-simplifier now." | Downstream review starts only after every task in the current wave is implemented and marked done. Say `do not start code-simplifier yet` when work remains in the wave. |
119. | "`todo.md` is already updated, so I can fix `plan.md` or SQL later." | Partial tracker sync is a workflow failure. Update every active tracker together before the next dispatch. |
120. | "Once review is done I can commit or open the PR for the human." | This skill explicitly leaves the work dirty and unpublished. The human handles any commit or PR later. |
121. 
122. ## Red Flags
123. 
124. - The manager reads large file sets, proposes a patch, or runs validation before dispatching a clear task.
125. - An implementer asks for `NEEDS_CONTEXT` just to avoid ordinary repo exploration.
126. - A simplifier or reviewer recomputes scope instead of using the exact manager-authored file list.
127. - A downstream concern or finding surfaces, but the affected task stays marked `done`.
128. - `plan.md`, `todo.md`, and SQL todo state disagree about the same task.
129. - Any step creates or publishes a commit, PR, or tag.
130. 
131. ## Verification
132. 
133. After completing the build wave, confirm:
134. 
135. - [ ] Each implementer `DONE` updated every active tracker for that task — typically `plan.md`, `todo.md`, and SQL todo state — before the next dispatch, and recorded the verification actually performed.
136. - [ ] `review_scope_files` was deduped, filtered, manager-authored, and reused across simplifier/reviewer waves unless the touched surface changed.
137. - [ ] Code-simplifier and code-review started only after the full wave was implemented and marked done.
138. - [ ] Any reopened task was reopened and re-closed across every active tracker only after the affected downstream passes returned `DONE`.
139. - [ ] The final reviewed sync leaves `plan.md`, `todo.md`, and SQL todo state aligned, and the working tree remains dirty and unpublished.
140.
```

</details>


---

<sub>⏱️ 1m 15s</sub>

### 💬 Copilot

Sync **Task A’s completion now**, not the review wave: update `.agents/scratchpad/issues/plan.md`, `.agents/scratchpad/issues/todo.md`, and the **SQL todo state** row `api-issues-pagination` to the same done status, record the verification that actually passed, and confirm all three trackers agree **before dispatching Task B**.

**Do not start code-simplifier yet.** Task B is still in the current wave, so downstream review waits until **every task in the wave** is implemented and marked done. The four touched files do **not** trigger `review_scope_files` yet.

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
