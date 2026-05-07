# 🤖 Copilot CLI Session

> [!NOTE]
> - **Session ID:** `39f1b62f-a596-47a1-9ccd-9f66b5f32ed8`  
> - **Started:** 5/6/2026, 6:10:42 PM  
> - **Duration:** 1m 16s  
> - **Exported:** 5/6/2026, 6:11:59 PM  

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
I already have the next pending task from the plan: add pagination to `GET /api/issues`. The acceptance criteria are written, the repo's validation commands are known, and the plan already names the files likely involved. Using the build workflow, tell me what the manager should do before the implementer runs, what belongs in the handoff, and what work must stay with the implementer.


---

<sub>⏱️ 10s</sub>

### 💬 Copilot

I’m loading the required workflow context and the exact build skill, then I’ll map this task onto its manager/implementer split.

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

**view the file at /home/adam/dev/personal/skills/skills/build/SKILL.md.**

/home/adam/dev/personal/skills/skills/build/SKILL.md

<details>
<summary>105 lines</summary>

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
12. 3. If the task is ambiguous, conflicts with the plan, or the human wants tradeoff analysis first, do not dispatch yet. Resolve that first.
13. 4. Otherwise dispatch immediately with the [implementer-prompt.md](./implementer-prompt.md) template and a lean handoff:
14.    - task text and success criteria
15.    - known constraints and validation commands
16.    - only already-known file hints
17. 5. Do **not** pre-read large file sets, draft the solution, or sketch likely patches before dispatch.
18. 6. The implementer owns repo discovery, pattern lookup, first-pass design, code changes, and verification.
19. 7. After the implementer returns `DONE`, dispatch the [simplifier-prompt.md](./simplifier-prompt.md) with:
20.    - the files the implementer touched
21.    - the implementer's verification context
22.    - all uncommitted files from `git status --porcelain`, excluding deleted files and `.gitignore` files
23. 8. After the code-simplifier returns `DONE`, dispatch the [code-reviewer-prompt.md](./code-reviewer-prompt.md) with:
24.    - the touched files
25.    - the current verification context
26.    - all uncommitted files from `git status --porcelain`, excluding deleted files and `.gitignore` files
27. 9. Update tracking only after the final reviewer returns `DONE`, using <update-tracking-instructions>.
28. 
29. ## Manager Guardrails
30. 
31. - Dispatch as soon as the task is clear enough to execute.
32. - Pass through only information already known from the plan, task, or repo rules.
33. - Ordinary repo exploration, pattern lookup, and first-pass design stay with the implementer.
34. - Ordinary repo exploration is not a valid `NEEDS_CONTEXT`.
35. - If the implementer asks the manager to explore the repo or hand over a solution, push that work back to the implementer.
36. 
37. ## Verification Selection
38. 
39. - Verification ownership stays with the implementer.
40. - Infer the task's surface and stack before choosing validation.
41. - Prefer the narrowest matching checks for that stack. For shell or Python work, use shell or Python validation instead of generic frontend commands unless the task is actually frontend work.
42. 
43. <update-tracking-instructions>
44. 1. Update the plan and todo tracker immediately.
45. 2. Record the verification actually performed.
46. 3. Mark the task `done` in the tracker.
47. </update-tracking-instructions>
48. 
49. ## Shared Escalation Rules
50. 
51. - **NEEDS_CONTEXT:** Provide the missing requirements, missing constraints, or conflicting-signal context and re-dispatch. Routine discovery is not a valid `NEEDS_CONTEXT`.
52. - **BLOCKED:** Assess the blocker:
53.   1. If it's a context problem, provide more context and re-dispatch with the same model.
54.   2. If the task requires more reasoning, re-dispatch with a more capable model.
55.   3. If the task is too large, break it into smaller pieces.
56.   4. If the plan itself is wrong, escalate to the human.
57. 
58. ## Subagent Status Handling
59. 
60. ### Implementer
61. 
62. - **DONE:** Proceed to code-simplifier.
63. - **DONE_WITH_CONCERNS:** Read the concerns before any downstream step or tracking update. If they raise a correctness concern or scope concern, address them first, usually by re-dispatching an implementer. Do not update tracking yet.
64. - **NEEDS_CONTEXT:** Ordinary repo exploration and pattern lookup stay with the implementer; only missing requirements, missing constraints, or conflicting signals qualify.
65. - **BLOCKED:** Follow the shared escalation rules.
66. 
67. ### Code-Simplifier
68. 
69. - **DONE:** Proceed to code-reviewer.
70. - **DONE_WITH_CONCERNS:** Read the concerns before continuing to code-reviewer. If they raise a correctness concern or scope concern, treat them as unresolved work, address them first, usually by re-dispatching the subagent that should own the fix, and do not update tracking yet.
71. - **NEEDS_CONTEXT:** Provide the missing context and re-dispatch.
72. - **BLOCKED:** Follow the shared escalation rules.
73. 
74. ### Code-Reviewer
75. 
76. - **DONE:** Proceed to update tracking.
77. - **DONE_WITH_FINDINGS:** Address findings before updating tracking. Re-dispatch the subagent that should own the fix, then route the result back through code-simplifier and code-reviewer as needed. Only mark the task done after the final reviewer returns `DONE`.
78. - **NEEDS_CONTEXT:** Provide the missing context and re-dispatch.
79. - **BLOCKED:** Follow the shared escalation rules.
80. 
81. Never ignore an escalation or rerun the same stuck attempt without changing context, scope, or model.
82. 
83. ## Tracking Discipline
84. 
85. - Treat stale docs as incomplete work.
86. - Reflect every task status change in the tracker, plan, and todo tracker.
87. 
88. ## Commit Override Behavior
89. 
90. Never commit. The human will review the changes and commit manually later.
91. 
92. ## Red Flags
93. 
94. - Not using a subagent for implementation tasks, fixes, simplifications, or code-review findings
95. - The manager performs repo discovery, pattern lookup, first-pass design, code changes, or verification when the task is clear enough to dispatch
96. - Marking a tracking item completed when the implementer, code-simplifier, and code-reviewer did not return `DONE`
97. - Marking a task done without updating the plan and todo tracker
98. 
99. ## Verification
100. 
101. - [ ] Each increment was tested with the right checks for its stack
102. - [ ] Relevant build, test, or manual verification is clean
103. - [ ] Tracking and docs reflect the final state
104. - [ ] All changes are uncommitted
105.
```

</details>


---

<sub>⏱️ 20s</sub>

### 💬 Copilot

I’ve got the core build rules; I’m checking the implementer handoff template and required model-selection step so the manager guidance matches the exact workflow.

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

**view the file at /home/adam/dev/personal/skills/skills/build/implementer-prompt.md.**

/home/adam/dev/personal/skills/skills/build/implementer-prompt.md

<details>
<summary>40 lines</summary>

```
1. # Implement Task N: [task name]
2. 
3. You are implementing Task N: [task name]
4. 
5. ## Workflow
6. 
7. 1. Invoke the `addy-incremental-implementation`, `addy-test-driven-development`, and `addy-context-engineering` skills.
8. 2. Read the task and acceptance criteria.
9. 3. Load the minimum context yourself: code, tests, patterns, types, and commands.
10. 4. Form the first-pass approach from that context.
11. 5. Write a failing test for the expected behavior (RED).
12. 6. Implement the minimum change to pass it (GREEN).
13. 7. Infer the slice's surface and stack first, then run the matching tests, build checks, or manual verification instead of defaulting to generic frontend commands.
14. 8. Report back.
15. 
16. **NEVER** commit.
17. **If any step fails**, follow the `addy-debugging-and-error-recovery` skill.
18. 
19. ## Context Expectations
20. 
21. - Assume the manager gives you a lean handoff, not a pre-solved design.
22. - Read the relevant files and find patterns yourself.
23. - Do **not** ask for more context just because you have not explored the repo yet.
24. - Treat "run the relevant validations" as a selection task: choose the narrowest checks that match the files and stack in this slice.
25. - Use `NEEDS_CONTEXT` only for missing product decisions, missing constraints, or conflicting signals you cannot resolve from the codebase and task context.
26. 
27. ## Report Format
28. 
29. - **Status:** DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
30. - What you implemented (or what you attempted, if blocked)
31. - What you tested, the exact commands, and the results
32. - Files changed
33. - Any issues or concerns
34. 
35. **Status Determination**:
36. 
37. - Use DONE_WITH_CONCERNS if you completed the work but have doubts about correctness.
38. - Use BLOCKED if you cannot complete the task.
39. - Use NEEDS_CONTEXT if you need information that wasn't provided. Use it for genuinely missing requirements or unresolved conflicts, not routine discovery. Never silently produce work you're unsure about.
40.
```

</details>


---

<sub>⏱️ 1m 9s</sub>

### 💬 Copilot

**Because this task is already well-scoped, the manager should dispatch quickly rather than solve it first.**

1. **Before the implementer runs:** invoke `addy-context-engineering` and `subagent-model-selection`, confirm the pagination task is clear and not in conflict with the plan, then choose the narrowest capable implementer/model and dispatch. Do **not** pre-read a large file set, design the pagination approach, sketch likely patches, or run validation first.
2. **What belongs in the handoff:** only the lean execution context — the task text (`add pagination to GET /api/issues`), the written acceptance criteria, known constraints/repo rules, the exact known validation commands, and the already-known file hints from the plan. Do **not** include a pre-solved design, speculative implementation steps, or extra repo exploration.
3. **What must stay with the implementer:** repo discovery, reading the relevant code/tests/types/patterns, forming the first-pass design, doing TDD (`RED` then `GREEN`), making the code changes, choosing the narrowest matching verification for the slice, running it, and reporting back with status, files changed, and exact commands/results. Routine exploration is **not** a valid `NEEDS_CONTEXT`; if the implementer asks the manager to explore the repo or hand over a solution, the manager should push that work back.

**In short:** the manager makes the task executable and passes only known context; the implementer owns discovery, design, coding, and verification. Tracking still waits until the downstream implementer → simplifier → reviewer chain finishes with `DONE`.

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
