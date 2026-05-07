# 🤖 Copilot CLI Session

> [!NOTE]
> - **Session ID:** `57e9c588-81d3-4baa-88e9-c953c7edab4d`  
> - **Started:** 5/6/2026, 6:26:19 PM  
> - **Duration:** 45s  
> - **Exported:** 5/6/2026, 6:27:04 PM  

---

<sub>⏱️ 0s</sub>

### ⚠️ Warning

Third-party MCP servers are disabled by your organization's Copilot policy. Only built-in servers are available.

---

<sub>⏱️ 1s</sub>

### 👤 User

Read and follow the build skill from this exact path: /home/adam/dev/personal/skills/skills/build-workspace/skill-snapshot-iteration-7/SKILL.md
Ignore any other installed copies of the build skill.
Answer the user's task using that workflow.

Task:
The implementer returned `DONE`, the code-simplifier also returned `DONE`, and `git status --porcelain` now shows `M skills/build/SKILL.md`, ` M skills/build/implementer-prompt.md`, `?? notes.txt`, `D scratch.tmp`, and `?? .gitignore`. Using the build workflow, what should the manager send to the code-reviewer before tracking is updated?


---

<sub>⏱️ 11s</sub>

### 💬 Copilot

I’m loading the required workflow context and the exact build skill file, then I’ll derive the code-reviewer handoff from that procedure.

---

<sub>⏱️ 12s</sub>

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

<sub>⏱️ 12s</sub>

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

<sub>⏱️ 12s</sub>

### ✅ `view`

**view the file at /home/adam/dev/personal/skills/skills/build-workspace/skill-snapshot-iteration-7/SKILL.md.**

/home/adam/dev/personal/skills/skills/build-workspace/skill-snapshot-iteration-7/SKILL.md

<details>
<summary>109 lines</summary>

```
1. ---
2. name: build
3. description: Coordinate the next implementation increment — pick the next ready task, dispatch an implementer with a lean handoff, route finished work through code-simplifier and code-reviewer, then update tracking.
4. ---
5. 
6. # Build
7. 
8. ## Core Loop
9. 
10. 1. Invoke the `addy-context-engineering` and `subagent-model-selection` skills.
11. 2. Pick the next pending task from the plan.
12. 3. If the task is ambiguous, conflicts with the plan, or the human wants tradeoff analysis first, it is not clear enough to dispatch yet. Resolve that before dispatch.
13. 4. Otherwise dispatch immediately with the [implementer-prompt.md](./implementer-prompt.md) template and a lean handoff:
14.    - task text and success criteria
15.    - known constraints and validation commands
16.    - only already-known file hints
17. 5. Do **not** pre-read a large file set, draft the solution, or sketch likely patches before the first dispatch. The manager coordinates; the implementer owns repo discovery, pattern lookup, first-pass design, code changes, and verification.
18. 6. After the implementer returns `DONE`, dispatch the [simplifier-prompt.md](./simplifier-prompt.md) over the files the implementer touched plus the verification context they produced. Also include all uncomitted files (`git status --porcelain`) while excluding deleted files and `.gitignore` files.
19. 7. After the code-simplifier returns `DONE`, dispatch the [code-reviewer-prompt.md](./code-reviewer-prompt.md) over the touched files plus the current verification context. Also include all uncomitted files (`git status --porcelain`) while excluding deleted files and `.gitignore` files.
20. 8. Update tracking only after the final subagent returns plain `DONE`, using <update-tracking-instructions>.
21. 
22. ## Manager Guardrails
23. 
24. - Dispatch as soon as the task is clear enough to execute.
25. - Pass through only information already known from the plan, task, or repo rules.
26. - Ordinary repo exploration is implementer work, not manager work.
27. - `NEEDS_CONTEXT` is only for missing requirements, missing constraints, or conflicting signals. Routine discovery is not a valid `NEEDS_CONTEXT`.
28. - If the implementer asks the manager to explore the repo or hand over a solution, push that work back to the implementer.
29. 
30. ## Verification Selection
31. 
32. - Verification ownership stays with the implementer.
33. - Infer the task's surface and stack before choosing validation.
34. - Prefer the narrowest matching checks for that stack. For shell or Python work, use shell or Python validation instead of generic frontend commands unless the task is actually frontend work.
35. 
36. <update-tracking-instructions>
37. 1. Update the plan and todo tracker immediately.
38. 2. Record the verification actually performed.
39. 3. Mark the task `done` in the tracker.
40. </update-tracking-instructions>
41. 
42. ## Subagent Status Handling
43. 
44. ### Implementer
45. 
46. Implementer subagents report one of four statuses. Handle each appropriately:
47. 
48. - **DONE:** Proceed to code-simplifier.
49. - **DONE_WITH_CONCERNS:** Read the concerns before any downstream step or tracking update. If they touch correctness or scope, address them first, usually by re-dispatching an implementer. Do not update tracking yet.
50. - **NEEDS_CONTEXT:** Use this only for missing requirements, missing constraints, or conflicting signals, not ordinary repo exploration. Provide the missing context and re-dispatch.
51. - **BLOCKED:** The implementer cannot complete the task. Assess the blocker:
52.   1. If it's a context problem, provide more context and re-dispatch with the same model.
53.   2. If the task requires more reasoning, re-dispatch with a more capable model.
54.   3. If the task is too large, break it into smaller pieces.
55.   4. If the plan itself is wrong, escalate to the human.
56. 
57. ### Code-Simplifier
58. 
59. Code-simplifier subagents report one of four statuses. Handle each appropriately:
60. 
61. - **DONE:** Proceed to code-reviewer.
62. - **DONE_WITH_CONCERNS:** Read the concerns before continuing to code-reviewer. If they touch correctness or scope, address them first, usually by re-dispatching the subagent that should own the fix. Do not update tracking yet.
63. - **NEEDS_CONTEXT:** Provide the missing context and re-dispatch.
64. - **BLOCKED:** The code-simplifier cannot complete the task. Assess the blocker:
65.   1. If it's a context problem, provide more context and re-dispatch with the same model.
66.   2. If the task requires more reasoning, re-dispatch with a more capable model.
67.   3. If the task is too large, break it into smaller pieces.
68.   4. If the plan itself is wrong, escalate to the human.
69. 
70. ### Code-Reviewer
71. 
72. Code-reviewer subagents report one of four statuses. Handle each appropriately:
73. 
74. - **DONE:** Proceed to update tracking.
75. - **DONE_WITH_FINDINGS:** Address findings before updating tracking, usually by re-dispatching the subagent that should own the fix. Route the result back through simplifier and reviewer as needed, and only mark the task done after the final subagent returns `DONE`.
76. - **NEEDS_CONTEXT:** Provide the missing context and re-dispatch.
77. - **BLOCKED:** The code-reviewer cannot complete the task. Assess the blocker:
78.   1. If it's a context problem, provide more context and re-dispatch with the same model.
79.   2. If the task requires more reasoning, re-dispatch with a more capable model.
80.   3. If the task is too large, break it into smaller pieces.
81.   4. If the plan itself is wrong, escalate to the human.
82. 
83. Never ignore an escalation or rerun the same stuck attempt without changing context, scope, or model.
84. 
85. ## Tracking Discipline
86. 
87. - Treat stale docs as incomplete work.
88. - Reflect every task status change in the tracker, plan, and todo tracker.
89. 
90. ## Commit Override Behavior
91. 
92. Never commit. The human will review the changes and commit manually later.
93. 
94. ## Red Flags
95. 
96. - Not using a subagent for implementation tasks, fixes, simplifications, or code-review findings
97. - Main agent performs discovery, pattern lookup, first-pass design, code changes, or verification when task is clearly defined
98. - Marking a tracking item completed when the implementer, code-simplifier, and code-reviewer did not return DONE
99. - Marking a task done without updating the plan and todo docs
100. 
101. ## Verification
102. 
103. After completing all tasks:
104. 
105. - [ ] Each increment was tested with the right checks for its stack
106. - [ ] Relevant build, test, or manual verification is clean
107. - [ ] Tracking and docs reflect the final state
108. - [ ] All changes are uncommitted
109.
```

</details>


---

<sub>⏱️ 21s</sub>

### ✅ `skill`

**subagent-model-selection**

<details>
<summary>Arguments</summary>

```json
{
  "skill": "subagent-model-selection"
}
```

</details>

```
Skill "subagent-model-selection" loaded successfully. Follow the instructions in the skill context.
```


---

<sub>⏱️ 21s</sub>

### ✅ `view`

**view the file at /home/adam/dev/personal/skills/skills/build-workspace/skill-snapshot-iteration-7/code-reviewer-prompt.md.**

/home/adam/dev/personal/skills/skills/build-workspace/skill-snapshot-iteration-7/code-reviewer-prompt.md

<details>
<summary>30 lines</summary>

```
1. # Code Reviewer
2. 
3. ## Context
4. 
5. [Files to review]
6. 
7. ## Workflow
8. 
9. 1. Invoke the `addy-context-engineering` skill.
10. 2. Invoke the `code-review` skill on the files in Context.
11. 3. Report back.
12. 
13. ## Report Format
14. 
15. - **Status:** DONE | DONE_WITH_FINDINGS | BLOCKED | NEEDS_CONTEXT
16. - Formatted findings (if any)
17. - Any issues or concerns
18. 
19. **Status Determination**:
20. 
21. - Use DONE if no findings were surfaced.
22. - Use DONE_WITH_FINDINGS if your review surfaced any findings.
23. - Use BLOCKED if you cannot complete the task.
24. - Use NEEDS_CONTEXT if you need information that wasn't provided. Never silently produce work you're unsure about.
25. 
26. ## Findings Format
27. 
28. Categorize findings as Critical, Important, or Suggestion.
29. Output a structured review with specific file:line references and fix recommendations.
30.
```

</details>


---

<sub>⏱️ 43s</sub>

### 💬 Copilot

Send the **code-reviewer prompt** with the **union of the touched files and the filtered `git status --porcelain` files**, plus the **current verification context**. From the status you gave, the files to include are:

- `skills/build/SKILL.md`
- `skills/build/implementer-prompt.md`
- `notes.txt`

Exclude:

- `scratch.tmp` — deleted
- `.gitignore` — explicitly excluded by the workflow

So the manager’s handoff is effectively: **review those three files + the current verification context**, then wait for the code-reviewer to return plain `DONE` before updating tracking.

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
