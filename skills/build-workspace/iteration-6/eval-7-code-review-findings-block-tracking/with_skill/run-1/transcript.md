# 🤖 Copilot CLI Session

> [!NOTE]
> - **Session ID:** `9cb6c7af-2690-4150-8f0e-f2fd0e18b177`  
> - **Started:** 5/6/2026, 4:44:27 PM  
> - **Duration:** 28s  
> - **Exported:** 5/6/2026, 4:44:56 PM  

---

<sub>⏱️ 0s</sub>

### ⚠️ Warning

Third-party MCP servers are disabled by your organization's Copilot policy. Only built-in servers are available.

---

<sub>⏱️ 1s</sub>

### 👤 User

Read and follow the build skill from this exact path: /home/adam/dev/personal/skills/skills/build/SKILL.md
Ignore any other installed copies of the build skill.
Answer the user's task using that workflow.

Task:
The implementer and code-simplifier both returned `DONE`, but the code-reviewer returned `DONE_WITH_FINDINGS`: two correctness issues remain in files already touched. Using the build workflow, what should the manager do next, and when can tracking be updated?

---

<sub>⏱️ 9s</sub>

### 💬 Copilot

Reading the build skill file at the path provided to follow its workflow and determine the manager's next actions and tracking updates. Running a parallel tool call: report_intent + view file.

---

<sub>⏱️ 11s</sub>

### ✅ `view`

**view the file at /home/adam/dev/personal/skills/skills/build/SKILL.md.**

/home/adam/dev/personal/skills/skills/build/SKILL.md

<details>
<summary>115 lines</summary>

```
1. ---
2. name: build
3. description: Coordinate the next implementation increment — pick the next ready task, dispatch an implementer with a lean handoff, route finished work through code-simplifier and code-reviewer, then update tracking.
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
19. 7. After the implementer returns `DONE`, dispatch the [simplifier-prompt.md](./simplifier-prompt.md) template over the files the implementer touched and the verification context they produced.
20. 8. After the code-simplifier returns `DONE`, dispatch the [code-reviewer-prompt.md](./code-reviewer-prompt.md) template over the touched files plus the current verification context.
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
34. ## Verification Selection
35. 
36. - Verification ownership stays with the implementer.
37. - Infer the task's surface and stack before choosing validation.
38. - Prefer the narrowest matching checks for that stack. For shell or Python work, use shell or Python validation rather than generic frontend commands unless the task is actually frontend work.
39. 
40. <update-tracking-instructions>
41. 1. Update the plan and todo doc immediately.
42. 2. Record the verification actually performed.
43. 3. Mark the task `done` in the tracker.
44. </update-tracking-instructions>
45. 
46. ## Subagent Status Handling
47. 
48. ### Implementer
49. 
50. Implementer subagents report one of four statuses. Handle each appropriately:
51. 
52. - **DONE:** Proceed to code-simplifier.
53. - **DONE_WITH_CONCERNS:** Read the concerns before code-simplifier. If they touch correctness or scope, address them first, usually by re-dispatching another implementer. Do not update tracking yet.
54. - **NEEDS_CONTEXT:** Use this only for missing requirements, constraints, or conflicting signals, not ordinary repo exploration. Provide the missing context and re-dispatch.
55. - **BLOCKED:** The implementer cannot complete the task. Assess the blocker:
56.   1.  If it's a context problem, provide more context and re-dispatch with the same model
57.   2.  If the task requires more reasoning, re-dispatch with a more capable model
58.   3.  If the task is too large, break it into smaller pieces
59.   4.  If the plan itself is wrong, escalate to the human
60. 
61. ### Code-Simplifier
62. 
63. Code-simplifier subagents report one of four statuses. Handle each appropriately:
64. 
65. - **DONE:** Proceed to code-reviewer.
66. - **DONE_WITH_CONCERNS:** Read the concerns before code-reviewer. If they touch correctness or scope, address them before continuing with code-reviewer, usually by re-dispatching the subagent that should own the fix.
67. - **NEEDS_CONTEXT:** Provide the missing context and re-dispatch.
68. - **BLOCKED:** The code-simplifier cannot complete the task. Assess the blocker:
69.   1.  If it's a context problem, provide more context and re-dispatch with the same model
70.   2.  If the task requires more reasoning, re-dispatch with a more capable model
71.   3.  If the task is too large, break it into smaller pieces
72.   4.  If the plan itself is wrong, escalate to the human
73. 
74. ### Code-Reviewer
75. 
76. Code-reviewer subagents report one of four statuses. Handle each appropriately:
77. 
78. - **DONE:** Proceed to update tracking.
79. - **DONE_WITH_FINDINGS:** Address findings before update tracking, usually by re-dispatching the subagent that should own the fix.
80. - **NEEDS_CONTEXT:** Provide the missing context and re-dispatch.
81. - **BLOCKED:** The code-reviewer cannot complete the task. Assess the blocker:
82.   1.  If it's a context problem, provide more context and re-dispatch with the same model
83.   2.  If the task requires more reasoning, re-dispatch with a more capable model
84.   3.  If the task is too large, break it into smaller pieces
85.   4.  If the plan itself is wrong, escalate to the human
86. 
87. Never ignore an escalation or rerun the same stuck attempt without changing context, scope, or model.
88. 
89. ## Tracking Discipline
90. 
91. - Treat stale docs as incomplete work.
92. - Reflect every task status change in the tracker, plan, and todo doc.
93. 
94. ## Commit Override Behavior
95. 
96. Do NOT commit. The user will review the changes and commit manually later.
97. 
98. ## Red Flags
99. 
100. - Not using a subagent for implementation tasks, fixes, simplifications, or code-review findings
101. - Main agent performs discovery, pattern lookup, first-pass design, code changes, or verification when task is clearly defined
102. - Marking a tracking item completed when the implementer, code-simplifier, and code-reviewer did not return DONE
103. - Marking a task done without updating the plan and todo docs
104. 
105. ## Verification
106. 
107. After completing all tasks:
108. 
109. - [ ] Each increment was individually tested
110. - [ ] The full test suite passes
111. - [ ] The build is clean
112. - [ ] The feature works end-to-end as specified
113. - [ ] All relevant docs are updated to reflect the completed work
114. - [ ] All changes are uncommitted
115.
```

</details>


---

<sub>⏱️ 24s</sub>

### 💬 Copilot

Answer per the Build workflow:

1. Invoke addy-context-engineering and subagent-model-selection, then re-dispatch the implementer (owner of code fixes) with a lean handoff containing the code-reviewer’s findings for the two correctness issues, exact success criteria, and verification commands. Do not pre-read/patch the repo yourself.

2. After that implementer returns DONE, dispatch the code-simplifier over the touched files, then re-run the code-reviewer.

3. Update tracking only after the final code-reviewer returns plain DONE — then update plan/todo, record verification performed, and mark the task done.

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
