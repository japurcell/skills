# 🤖 Copilot CLI Session

> [!NOTE]
> - **Session ID:** `63aee0ae-2675-4dc8-a482-2fa20107c94c`  
> - **Started:** 5/6/2026, 4:39:22 PM  
> - **Duration:** 33s  
> - **Exported:** 5/6/2026, 4:39:56 PM  

---

<sub>⏱️ 0s</sub>

### ⚠️ Warning

Third-party MCP servers are disabled by your organization's Copilot policy. Only built-in servers are available.

---

<sub>⏱️ 1s</sub>

### 👤 User

Read and follow the build skill from this exact path: /home/adam/dev/personal/skills/skills/build-workspace/skill-snapshot-iteration-6/SKILL.md
Ignore any other installed copies of the build skill.
Answer the user's task using that workflow.

Task:
An implementer reports `DONE` on the next task, with passing verification and a list of the four files they touched. Using the build workflow, what should the manager do next before updating tracking, and what context should go to the next subagent?

---

<sub>⏱️ 19s</sub>

### 💬 Copilot

Reading the specified build-skill SKILL.md to follow its manager checklist for marking tasks done and preparing context for the next subagent. Running a parallel read of the SKILL.md and reporting intent.

---

<sub>⏱️ 21s</sub>

### ✅ `view`

**view the file at /home/adam/dev/personal/skills/skills/build-workspace/skill-snapshot-iteration-6/SKILL.md.**

/home/adam/dev/personal/skills/skills/build-workspace/skill-snapshot-iteration-6/SKILL.md

<details>
<summary>109 lines</summary>

```
1. ---
2. name: build
3. description: Coordinate the next planned implementation task incrementally — choose the next ready task, dispatch an implementer with a lean handoff, run a code-simplifier pass, run a code-reviewer pass, verify, then update tracking.
4. ---
5. 
6. # Build
7. 
8. ## Workflow
9. 
10. 1. Invoke the `addy-context-engineering` and `subagent-model-selection` skills.
11. 2. Pick the next pending task from the plan.
12. 3. If the task is ambiguous, conflicts with the plan, or the human wants tradeoff analysis first, it is not clear enough to dispatch yet. Resolve that before dispatch.
13. 4. Otherwise dispatch immediately with the [implementer-prompt.md](./implementer-prompt.md) template and a lean handoff:
14.    - task text and success criteria
15.    - known constraints and validation commands
16.    - only already-known file hints
17. 5. Do **not** pre-read a large file set, draft the solution, or sketch likely patches before the first dispatch.
18. 6. The implementer owns repo discovery, pattern lookup, first-pass design, code changes, and verification.
19. 7. After the implementer returns `DONE`, dispatch the [simplifier-prompt.md](./simplifier-prompt.md) template over the files the implementer touched.
20. 8. After the code-simplifier returns `DONE`, dispatch the [code-reviewer-prompt.md](./code-reviewer-prompt.md) template over the files the implementer touched.
21. 9. Update tracking only after the final subagent returns `DONE`, using <update-tracking-instructions>.
22. 
23. ## Implementer Dispatch Rule
24. 
25. The main agent coordinates. It does not pre-implement.
26. 
27. - Dispatch as soon as the task is clear enough to execute.
28. - Do **not** pre-read a large file set, draft the solution, or sketch likely patches before the first dispatch.
29. - Pass through only information already known from the plan, task, or repo rules.
30. - Ordinary repo exploration is implementer work, not manager work.
31. - `NEEDS_CONTEXT` is for missing requirements, missing constraints, or conflicting signals — routine discovery is not a valid `NEEDS_CONTEXT`.
32. - If the implementer asks the manager to explore the repo or hand over a solution, push that work back to the implementer.
33. 
34. <update-tracking-instructions>
35. 1. Update the plan and todo doc immediately.
36. 2. Record the verification actually performed.
37. 3. Mark the task `done` in the tracker.
38. </update-tracking-instructions>
39. 
40. ## Subagent Status Handling
41. 
42. ### Implementer
43. 
44. Implementer subagents report one of four statuses. Handle each appropriately:
45. 
46. - **DONE:** Proceed to code-simplifier.
47. - **DONE_WITH_CONCERNS:** Read the concerns before code-simplifier. If they touch correctness or scope, address them first, usually by re-dispatching another implementer. Do not update tracking yet.
48. - **NEEDS_CONTEXT:** Use this only for missing requirements, constraints, or conflicting signals, not ordinary repo exploration. Provide the missing context and re-dispatch.
49. - **BLOCKED:** The implementer cannot complete the task. Assess the blocker:
50.   1.  If it's a context problem, provide more context and re-dispatch with the same model
51.   2.  If the task requires more reasoning, re-dispatch with a more capable model
52.   3.  If the task is too large, break it into smaller pieces
53.   4.  If the plan itself is wrong, escalate to the human
54. 
55. ### Code-Simplifier
56. 
57. Code-simplifier subagents report one of four statuses. Handle each appropriately:
58. 
59. - **DONE:** Proceed to code-reviewer.
60. - **DONE_WITH_CONCERNS:** Read the concerns before code-reviewer. If they touch correctness or scope, address them before continuing with code-reviewer, usually by re-dispatching the subagent that should own the fix.
61. - **NEEDS_CONTEXT:** Provide the missing context and re-dispatch.
62. - **BLOCKED:** The code-simplifier cannot complete the task. Assess the blocker:
63.   1.  If it's a context problem, provide more context and re-dispatch with the same model
64.   2.  If the task requires more reasoning, re-dispatch with a more capable model
65.   3.  If the task is too large, break it into smaller pieces
66.   4.  If the plan itself is wrong, escalate to the human
67. 
68. ### Code-Reviewer
69. 
70. Code-reviewer subagents report one of four statuses. Handle each appropriately:
71. 
72. - **DONE:** Proceed to update tracking.
73. - **DONE_WITH_FINDINGS:** Address findings before update tracking, usually by re-dispatching the subagent that should own the fix.
74. - **NEEDS_CONTEXT:** Provide the missing context and re-dispatch.
75. - **BLOCKED:** The code-reviewer cannot complete the task. Assess the blocker:
76.   1.  If it's a context problem, provide more context and re-dispatch with the same model
77.   2.  If the task requires more reasoning, re-dispatch with a more capable model
78.   3.  If the task is too large, break it into smaller pieces
79.   4.  If the plan itself is wrong, escalate to the human
80. 
81. Never ignore an escalation or rerun the same stuck attempt without changing context, scope, or model.
82. 
83. ## Tracking Discipline
84. 
85. - Treat stale docs as incomplete work.
86. - Reflect every task status change in the tracker, plan, and todo doc.
87. 
88. ## Commit Override Behavior
89. 
90. Do NOT commit. The user will review the changes and commit manually later.
91. 
92. ## Red Flags
93. 
94. - Not using a subagent for implementation tasks, fixes, simplifications, or code-review findings
95. - Main agent performs discovery, pattern lookup, first-pass design, code changes, or verification when task is clearly defined
96. - Marking a tracking item completed when the implementer, code-simplifier, and code-reviewer did not return DONE
97. - Marking a task done without updating the plan and todo docs
98. 
99. ## Verification
100. 
101. After completing all tasks:
102. 
103. - [ ] Each increment was individually tested
104. - [ ] The full test suite passes
105. - [ ] The build is clean
106. - [ ] The feature works end-to-end as specified
107. - [ ] All relevant docs are updated to reflect the completed work
108. - [ ] All changes are uncommitted
109.
```

</details>


---

<sub>⏱️ 31s</sub>

### 💬 Copilot

Dispatch the code-simplifier next (use the simplifier-prompt.md template) over the four touched files — do this before updating tracking. Handoff context to the simplifier: task text and success criteria; known constraints and validation commands; the exact list of the four files; the implementer’s verification evidence (commands run + pass output); and any implementer notes/concerns. Do not update the tracker until the simplifier (and then code-reviewer) return DONE; finally record the verification performed and mark the task done.

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
