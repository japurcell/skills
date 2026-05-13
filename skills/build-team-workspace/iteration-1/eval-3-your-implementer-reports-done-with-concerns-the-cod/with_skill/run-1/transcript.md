# 🤖 Copilot CLI Session

> [!NOTE]
> - **Session ID:** `14a68177-7540-452a-bfc9-9de08c6ac991`  
> - **Started:** 5/13/2026, 9:38:35 AM  
> - **Duration:** 13s  
> - **Exported:** 5/13/2026, 9:38:48 AM  

---

<sub>⏱️ 1s</sub>

### 👤 User

You are running a skill benchmark eval.

Read and follow this exact local skill file: /home/adam/dev/personal/skills/skills/build-team-workspace/skill-snapshot-current/SKILL.md
Ignore any installed copies of the build-team skill with the same name.
Do not edit files, create files, commit changes, or run project commands for this eval. Produce only the answer to the eval prompt.

Eval prompt:
Your implementer reports `DONE_WITH_CONCERNS`: the code landed, but the concern is about correctness for the current task, not just a cosmetic note. Explain what the build skill expects you to do before marking anything complete or moving on.


---

<sub>⏱️ 9s</sub>

### 💬 Copilot

I’ll read the requested local skill snapshot and answer from that only.

---

<sub>⏱️ 9s</sub>

### ✅ `view`

**view the file at /home/adam/dev/personal/skills/skills/build-team-workspace/skill-snapshot-current/SKILL.md.**

/home/adam/dev/personal/skills/skills/build-team-workspace/skill-snapshot-current/SKILL.md

<details>
<summary>129 lines</summary>

```
1. ---
2. name: build-team
3. description: Orchestrates an existing `$plan` through implementation, code simplification, code review, and durable lesson capture while keeping `$plan` as the source of truth. Use when the user wants you to continue an implementation plan, finish ready tasks without repeated check-ins, or run the build-team workflow from a plan file.
4. ---
5. 
6. # Build Team
7. 
8. ## Overview
9. 
10. Execute an existing `$plan` continuously. You are the orchestrator: send ready tasks to fresh implementer subagents, record completion in `$plan`, then run one simplification pass and one review pass before stopping.
11. 
12. Use a fresh implementer per task so coordination stays clean and each task gets focused context.
13. 
14. ## When to Use
15. 
16. - `$plan` already exists and has pending implementation tasks.
17. - The user wants execution of an existing plan, not planning from scratch.
18. - The work should continue through ready tasks without repeated "should I continue?" check-ins.
19. - Not for creating a plan, writing a spec, or breaking work down from scratch.
20. 
21. ## Inputs
22. 
23. - `$plan` (required): path to the implementation plan file, typically `.agents/scratchpad/<feature>/plan.md`. This file must already exist and contain pending tasks.
24. 
25. ## Workflow
26. 
27. ### Phase 1: Implementation Orchestration
28. 
29. 1. Read `$plan` and pick the next ready pending task from the file.
30. 2. Based on the task's size or scope, invoke the `subagent-model-selection` skill to determine the least powerful model and most appropriate agent type for the implementer subagent.
31. 3. Dispatch one fresh implementer subagent with the exact task text, the relevant `$plan` excerpt, and the [implementer-prompt.md](./implementer-prompt.md) template.
32. 4. Wait for the implementer to report back.
33. 5. Handle the status exactly:
34.    - **DONE:** Update the matching task in `$plan`, save it, then re-read `$plan` and verify the completion is visible before starting the next task.
35.    - **DONE_WITH_CONCERNS:** Treat this as unresolved correctness or scope risk. Read the concerns first and resolve them before marking the task complete. If the implementer only has a non-blocking observation, it should report `DONE` and include the note there instead.
36.    - **NEEDS_CONTEXT:** Provide the missing context and re-dispatch. Do not mark the task complete.
37.    - **BLOCKED:** Try to unblock with better context, a smaller slice, or a more capable model. If the blocker remains, stop and escalate to the human. Do not mark the task complete.
38. 6. Continue through ready implementation tasks without pausing for permission.
39. 7. When no ready implementation tasks remain, build one `$review_scope_files` list:
40.    - Start with every file any implementer reported changing.
41.    - Add uncommitted files from `git status --porcelain`.
42.    - Exclude deleted paths, `.gitignore`, and paths ignored by git.
43.    - Deduplicate the list and keep paths relative to the repository root.
44. 8. Proceed to the next phase. Stop early only when a real blocker remains or the plan itself is wrong.
45. 
46. ### Phase 2: Code Simplification
47. 
48. 1. Add a "Code Simplification" task to `$plan` with the full `$review_scope_files` list in the description. This makes simplification part of the execution record and ensures it doesn't get lost.
49. 2. Based on the task's size or scope, invoke the `subagent-model-selection` skill to determine the least powerful model and most appropriate agent type for the code-simplifier subagent.
50. 3. Dispatch code-simplifier subagents over `$review_scope_files` partitions with the [code-simplifier-prompt.md](./code-simplifier-prompt.md) template. Include the exact file list for each subagent. Scale based on the number of files:
51.    - **≤5 files**: launch 1 agent covering all changed files
52.    - **>5 files**: partition files into non-overlapping groups (by module, directory, or logical area) and launch one agent per group in parallel. Each file must appear in exactly one agent's scope — overlapping scopes cause conflicting writes.
53. 4. Wait for all code-simplifier subagents to report back.
54. 5. Handle the statuses exactly:
55.    - **DONE:** When all subagents report `DONE`, update the code simplification task in `$plan`, save it, then re-read `$plan` and verify the completion is visible.
56.    - **DONE_WITH_CONCERNS:** If the concern affects correctness or scope, resolve it before marking the task complete. If it's a non-blocking observation, the agent should have reported `DONE` and included the note there instead.
57.    - **NEEDS_CONTEXT:** Provide the missing context and re-dispatch. Do not mark the task complete.
58.    - **BLOCKED:** Try to unblock with better context, a smaller slice, or a more capable model. If the blocker remains, stop and escalate to the human. Do not mark the task complete.
59. 6. When the code simplification task is marked complete in `$plan`, proceed to the next phase. Stop early only when a real blocker remains.
60. 
61. ### Phase 3: Code Review
62. 
63. 1. Add a "Code Review" task to `$plan` with the full `$review_scope_files` list in the description. This makes code review part of the execution record and ensures it doesn't get lost.
64. 2. Based on the task's size or scope, invoke the `subagent-model-selection` skill to determine the least powerful model and most appropriate agent type for the code-reviewer subagent.
65. 3. Dispatch code-reviewer subagents over `$review_scope_files` with the [code-reviewer-prompt.md](./code-reviewer-prompt.md) template. Include the exact file list for each subagent. Scale based on the number of files:
66.    - **≤5 files**: launch 1 agent covering all changed files
67.    - **>5 files**: launch multiple agents in parallel with different focuses (e.g., correctness, security, performance).
68. 4. Wait for all code-reviewer subagents to report back.
69. 5. Handle the statuses exactly:
70.    - **DONE:** When all subagents report `DONE`, update the code review task in `$plan`, save it, then re-read `$plan` and verify the completion is visible.
71.    - **DONE_WITH_FINDINGS:** Re-open the affected task in `$plan` and route the fix to a fresh implementer subagent instead of patching inline. Include the finding, affected files, and original task context. After the fix lands, add any newly changed files to `$review_scope_files`, return to Phase 2 for the affected files, then repeat code review. Do not mark the code review task complete.
72.    - **NEEDS_CONTEXT:** Provide the missing context and re-dispatch. Do not mark the code review task complete.
73.    - **BLOCKED:** Try to unblock with better context, a smaller slice, or a more capable model. If the blocker remains, stop and escalate to the human. Do not mark the code review task complete.
74. 6. When the code review task is marked complete in `$plan`, proceed to the next phase. Stop early only when a real blocker remains.
75. 
76. ### Phase 4: Self-Improve
77. 
78. Before stopping, invoke the `self-improve` skill when the session produced durable, reusable learnings. Do not record one-off task trivia.
79. 
80. ## Specific Techniques
81. 
82. - Treat `$plan` as the only execution record. Internal todo trackers, memory, scratchpads, chat summaries, and subagent status messages can help coordination but never replace updating `$plan`.
83. - A task is complete only after the finished state is written to `$plan` and then verified by re-reading `$plan`.
84. - Send the implementer the exact task text plus the relevant `$plan` excerpt. Weaker models behave better when task boundaries are explicit.
85. - Keep the orchestration boundary intact: the implementer does the task work; you coordinate selection, status handling, and `$plan` updates.
86. - Reuse [implementer-prompt.md](./implementer-prompt.md) instead of re-explaining implementation details from memory. That prompt already covers incremental implementation, TDD, targeted verification, and debugging when a step fails.
87. - Reuse the simplifier and reviewer prompt templates instead of improvising status names or report formats.
88. - Leave all repository changes uncommitted.
89. 
90. ## Common Rationalizations
91. 
92. | Rationalization                                                    | Reality                                                                                                                  |
93. | ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------ |
94. | "The implementer said it's done, so I can move on."                | `DONE` is not enough by itself. The task is complete only after `$plan` is updated, saved, and re-read.                  |
95. | "Implementation tasks are done, so I can skip review."             | The workflow includes simplification and code review tasks before the final handoff.                                     |
96. | "I can track completion in my todo list or chat summary."          | Those are helpers, not execution records. `$plan` is the only source of truth.                                           |
97. | "I'll just do this task myself instead of dispatching a subagent." | This skill is for orchestration. A fresh implementer subagent per task keeps context clean and the workflow consistent.  |
98. | "I'll stop after this task and ask whether to continue."           | Keep going through ready tasks. Stop only for a real blocker, genuine ambiguity, or full completion.                     |
99. | "Review findings are faster to patch inline."                      | Re-open the affected task in `$plan` and send the fix to a fresh implementer so the orchestration record stays complete. |
100. | "The plan is done, so the skill is done."                          | Not yet. First capture durable reusable lessons with `self-improve`, if any exist.                                       |
101. 
102. ## Red Flags
103. 
104. - Code implemented by the orchestrator instead of an implementer subagent
105. - Starting the next task before `$plan` is updated and re-read
106. - Treating runtime trackers or subagent reports as equivalent to `$plan`
107. - Marking `BLOCKED` or `NEEDS_CONTEXT` work complete
108. - Stopping between ready tasks to ask for permission
109. - Skipping the simplification or code review phase after implementation tasks finish
110. - Patching review findings inline instead of reopening the affected `$plan` task
111. - Committing changes or telling the implementer to commit
112. - Finishing all plan tasks but skipping `self-improve` when durable lessons exist
113. - Recording one-off task trivia as durable lessons
114. 
115. ## Verification
116. 
117. - [ ] `$plan` existed and provided the task order.
118. - [ ] Each task was assigned to a fresh implementer subagent.
119. - [ ] Each completed task was written to `$plan` only after `DONE` or an acceptable `DONE_WITH_CONCERNS` resolution.
120. - [ ] After each `$plan` update, the file was re-read and matched the current execution state before the next task began.
121. - [ ] Ready tasks ran continuously until completion or a real blocker required escalation.
122. - [ ] `$review_scope_files` included touched files plus filtered uncommitted files, with deleted, ignored, and `.gitignore` paths excluded.
123. - [ ] A "Code Simplification" task was added to `$plan`, completed, saved, and verified by re-reading `$plan`.
124. - [ ] A "Code Review" task was added to `$plan`, completed, saved, and verified by re-reading `$plan`.
125. - [ ] Any review findings re-opened the affected `$plan` task and were routed to a fresh implementer subagent.
126. - [ ] All work remains uncommitted.
127. - [ ] Before stopping, `self-improve` was invoked if the session produced durable, reusable learnings worth preserving.
128. - [ ] Any captured lessons were durable and reusable, not one-off task trivia.
129.
```

</details>


---

<sub>⏱️ 13s</sub>

### 💬 Copilot

Treat `DONE_WITH_CONCERNS` as unresolved correctness or scope risk. Read the concern first, resolve it, and only then mark the task complete in `$plan`.

Do **not** move on while the concern remains. Completion requires updating `$plan`, saving it, then re-reading `$plan` to verify the completed state is visible. If the concern is truly non-blocking, the implementer should have reported `DONE` with a note instead.

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
