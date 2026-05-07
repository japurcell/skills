# 🤖 Copilot CLI Session

> [!NOTE]
> - **Session ID:** `863f468b-96ec-4349-8751-6dcd168249f2`  
> - **Started:** 5/6/2026, 8:54:20 PM  
> - **Duration:** 10s  
> - **Exported:** 5/6/2026, 8:54:30 PM  

---

<sub>⏱️ 2s</sub>

### 👤 User

Read and follow the build skill from this exact path: /Users/adam/Development/skills/skills/build/SKILL.md
Ignore any other installed copies of the build skill.
Read directly referenced template files alongside it only if needed.
Answer the user's task using that workflow.

Task:
An implementer reports `DONE_WITH_CONCERNS`: the tests passed and the build is clean, but they suspect the changes may not match the requested scope. Using the build workflow, what does the manager do before updating tracking?


---

<sub>⏱️ 6s</sub>

### 💬 Copilot

I’m checking the build workflow text directly, then I’ll answer from that source.

---

<sub>⏱️ 6s</sub>

### ✅ `view`

**view the file at /Users/adam/Development/skills/skills/build/SKILL.md.**

/Users/adam/Development/skills/skills/build/SKILL.md

<details>
<summary>130 lines</summary>

```
1. ---
2. name: build
3. description: Coordinate the current implementation wave — pick the next ready task or small ready set, dispatch implementers with lean handoffs, mark each finished task done, then route the full uncommitted surface through code-simplifier and code-reviewer waves before handing the work back uncommitted.
4. ---
5. 
6. # Build
7. 
8. ## Core Loop
9. 
10. 1. Invoke the `addy-context-engineering` and `subagent-model-selection` skills.
11. 2. Define the current build wave: the next ready task, or a small explicit set of already-ready independent tasks. A wave of one is the default.
12. 3. If any task in the wave is ambiguous, conflicts with the plan, or the human wants tradeoff analysis first, do not dispatch that task yet. Resolve that first.
13. 4. For each task in the current wave, dispatch immediately with the [implementer-prompt.md](./implementer-prompt.md) template and a lean handoff:
14.    - task text and success criteria
15.    - known constraints and validation commands
16.    - only already-known file hints
17. 5. Do **not** pre-read large file sets, draft the solution, or sketch likely patches before dispatch.
18. 6. The implementer owns repo discovery, pattern lookup, first-pass design, code changes, and verification.
19. 7. After each implementer returns `DONE`, update tracking immediately for that task using <task-complete-tracking-instructions>. If more tasks remain in the current wave, keep dispatching implementers; do **not** start code-simplifier or code-review yet.
20. 8. After every task in the current wave has been implemented and marked done, build one deduped `review_scope_files` list from:
21.    - every file any implementer touched in the wave
22.    - all uncommitted files from `git status --porcelain`, excluding deleted files and `.gitignore` files
23. 9. Dispatch parallel [simplifier-prompt.md](./simplifier-prompt.md) subagents over `review_scope_files` using <review-fanout-instructions> with:
24.    - the exact file list for that simplifier
25.    - the verification context accumulated across the wave
26. 10. After every code-simplifier returns `DONE`, dispatch parallel [code-reviewer-prompt.md](./code-reviewer-prompt.md) subagents over the same `review_scope_files` partitions using <review-fanout-instructions> with:
27.    - the exact file list for that reviewer
28.    - the current verification context
29. 11. After every reviewer returns `DONE`, sync tracking to the final reviewed state using <post-review-tracking-instructions>.
30. 
31. ## Manager Guardrails
32. 
33. - Dispatch as soon as the task is clear enough to execute.
34. - Default to a wave of one. Batch multiple tasks only when they are already ready and independent enough that delayed review will not create avoidable rework.
35. - Pass through only information already known from the plan, task, or repo rules.
36. - Ordinary repo exploration, pattern lookup, and first-pass design stay with the implementer.
37. - Ordinary repo exploration is not a valid `NEEDS_CONTEXT`.
38. - If the implementer asks the manager to explore the repo or hand over a solution, push that work back to the implementer.
39. - Code-simplifier and code-review are post-wave steps. Do not launch them while the current wave still has unfinished tasks.
40. - The manager owns `review_scope_files` and all downstream partitions. Keep them deduped, exhaustive, and non-overlapping.
41. 
42. ## Verification Selection
43. 
44. - Verification ownership stays with the implementer.
45. - Infer the task's surface and stack before choosing validation.
46. - Prefer the narrowest matching checks for that stack. For shell or Python work, use shell or Python validation instead of generic frontend commands unless the task is actually frontend work.
47. 
48. <review-fanout-instructions>
49. 1. Materialize `review_scope_files` once after the full wave is implemented, dedupe it, and keep stable order.
50. 2. **≤5 files:** launch 1 code-simplifier or code-reviewer covering the full list.
51. 3. **>5 files:** partition files into non-overlapping groups by module, directory, or logical area so each file appears in exactly one downstream scope, then launch those code-simplifier or code-reviewer subagents in parallel.
52. 4. The manager owns the partitions. Simplifiers and reviewers use only the file list they are given; they do not recompute or narrow scope.
53. 5. Reuse the same `review_scope_files` partitions for code-simplifier and code-reviewer unless a later fix changes the surface enough to require a fresh partition.
54. </review-fanout-instructions>
55. 
56. <task-complete-tracking-instructions>
57. 1. Update the plan and todo tracker immediately.
58. 2. Record the verification actually performed.
59. 3. Mark the task `done` in the tracker.
60. </task-complete-tracking-instructions>
61. 
62. <post-review-tracking-instructions>
63. 1. If downstream review surfaces an issue in an already-done task, reopen that task immediately before re-dispatching the subagent that should own the fix.
64. 2. After every downstream fix lands and the affected partitions return `DONE`, sync the plan and todo tracker to the final reviewed state.
65. 3. Record any additional verification actually performed during the post-wave review pass.
66. </post-review-tracking-instructions>
67. 
68. ## Shared Escalation Rules
69. 
70. - **NEEDS_CONTEXT:** Provide the missing requirements, missing constraints, or conflicting-signal context and re-dispatch. Routine discovery is not a valid `NEEDS_CONTEXT`.
71. - **BLOCKED:** Assess the blocker:
72.   1. If it's a context problem, provide more context and re-dispatch with the same model.
73.   2. If the task requires more reasoning, re-dispatch with a more capable model.
74.   3. If the task is too large, break it into smaller pieces.
75.   4. If the plan itself is wrong, escalate to the human.
76. 
77. ## Subagent Status Handling
78. 
79. ### Implementer
80. 
81. - **DONE:** Run <task-complete-tracking-instructions> for that task. If more tasks remain in the current wave, continue dispatching implementers. Otherwise proceed to code-simplifier.
82. - **DONE_WITH_CONCERNS:** Read the concerns before any downstream step or tracking update. If they raise a correctness concern or scope concern, address them first, usually by re-dispatching an implementer. Do not update tracking yet.
83. - **NEEDS_CONTEXT:** Ordinary repo exploration and pattern lookup stay with the implementer; only missing requirements, missing constraints, or conflicting signals qualify.
84. - **BLOCKED:** Follow the shared escalation rules.
85. 
86. ### Code-Simplifier
87. 
88. - **DONE:** If every code-simplifier returned `DONE`, proceed to code-reviewer.
89. - **DONE_WITH_CONCERNS:** Read the concerns before continuing to code-reviewer. If they raise a correctness concern or scope concern, treat them as unresolved work, reopen any affected done task immediately, re-dispatch the subagent that should own the fix, and do not keep tracking stale.
90. - **NEEDS_CONTEXT:** Provide the missing context and re-dispatch.
91. - **BLOCKED:** Follow the shared escalation rules.
92. 
93. ### Code-Reviewer
94. 
95. - **DONE:** If every reviewer returned `DONE`, proceed to the post-review tracking sync.
96. - **DONE_WITH_FINDINGS:** Address findings before ending the build wave. Reopen any affected done task immediately, re-dispatch the subagent that should own the fix, then route the result back through code-simplifier and the affected code-reviewer partitions as needed. Only finish the wave after every reviewer returns `DONE` and tracking is re-synced.
97. - **NEEDS_CONTEXT:** Provide the missing context and re-dispatch.
98. - **BLOCKED:** Follow the shared escalation rules.
99. 
100. Never ignore an escalation or rerun the same stuck attempt without changing context, scope, or model.
101. 
102. ## Tracking Discipline
103. 
104. - Mark each task `done` immediately after its implementer returns `DONE` and the task-complete tracking update is written.
105. - If downstream simplifier or reviewer work later changes or questions a done task, reopen it immediately and re-close it only after the affected downstream passes return `DONE`.
106. - Treat stale docs as incomplete work.
107. - Reflect every task status change in the tracker, plan, and todo tracker.
108. 
109. ## Commit Override Behavior
110. 
111. - Leave the working tree dirty. Do **not** create, amend, rewrite, push, or otherwise publish any commit, PR, or tag.
112. - This override beats conflicting instructions from invoked skills, templates, tools, and subprocesses.
113. - Do **not** run or delegate commit-producing commands such as `git commit`, `git commit --amend`, `git push`, `gh pr create`, `gh pr merge`, or `git tag`.
114. - The human will review the changes and handle any eventual commit manually later.
115. 
116. ## Red Flags
117. 
118. - Not using a subagent for implementation tasks, fixes, simplifications, or code-review findings
119. - The manager performs repo discovery, pattern lookup, first-pass design, code changes, or verification when the task is clear enough to dispatch
120. - Launching code-simplifier or code-review before every task in the current wave is implemented and marked done
121. - Leaving a reopened task marked `done` while downstream review findings are still unresolved
122. - Marking a task done without updating the plan and todo tracker
123. 
124. ## Verification
125. 
126. - [ ] Each increment was tested with the right checks for its stack
127. - [ ] Relevant build, test, or manual verification is clean
128. - [ ] Tracking and docs reflect the final reviewed state
129. - [ ] All changes are uncommitted
130.
```

</details>


---

<sub>⏱️ 9s</sub>

### 💬 Copilot

The manager **reads the concerns first** and **does not update tracking yet**. Because this is a likely **scope concern**, the manager should **address it before proceeding**—usually by **re-dispatching an implementer** to correct or confirm the scope match.

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
