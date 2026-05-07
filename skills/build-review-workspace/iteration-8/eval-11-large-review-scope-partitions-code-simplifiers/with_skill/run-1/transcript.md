# 🤖 Copilot CLI Session

> [!NOTE]
> - **Session ID:** `fbff4092-eef2-4b48-a465-375457a3c50e`  
> - **Started:** 5/6/2026, 7:17:47 PM  
> - **Duration:** 1m 33s  
> - **Exported:** 5/6/2026, 7:19:20 PM  

---

<sub>⏱️ 0s</sub>

### ⚠️ Warning

Third-party MCP servers are disabled by your organization's Copilot policy. Only built-in servers are available.

---

<sub>⏱️ 2s</sub>

### 👤 User

Read and follow the build skill from this exact path: /home/adam/dev/personal/skills/skills/build-review/SKILL.md
Ignore any other installed copies of the build skill.
Answer the user's task using that workflow.

Task:
An implementer reports `DONE`, and the manager materialized a deduped `review_scope_files` list of 8 files across two logical areas: `src/auth/login.ts`, `src/auth/session.ts`, `src/auth/token.ts`, `tests/auth/login.test.ts`, `src/billing/invoice.ts`, `src/billing/payment.ts`, `src/billing/refund.ts`, and `tests/billing/invoice.test.ts`. Using the build workflow, how should the manager launch code-simplifiers before code-review begins?


---

<sub>⏱️ 13s</sub>

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

<sub>⏱️ 13s</sub>

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

<sub>⏱️ 21s</sub>

### ✅ `view`

**view the file at /home/adam/dev/personal/skills/skills/build-review/SKILL.md.**

/home/adam/dev/personal/skills/skills/build-review/SKILL.md

<details>
<summary>115 lines</summary>

```
1. ---
2. name: build-review
3. description: Coordinate the next implementation increment — pick the next ready task, dispatch an implementer with a lean handoff, route finished work through one or more code-simplifiers and code-reviewers, then update tracking.
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
19. 7. After the implementer returns `DONE`, build one deduped `review_scope_files` list from:
20.    - the files the implementer touched
21.    - all uncommitted files from `git status --porcelain`, excluding deleted files and `.gitignore` files
22. 8. Dispatch parallel [simplifier-prompt.md](./simplifier-prompt.md) subagents over `review_scope_files` using <review-fanout-instructions> with:
23.    - the exact file list for that simplifier
24.    - the implementer's verification context
25. 9. After every code-simplifier returns `DONE`, dispatch parallel [code-reviewer-prompt.md](./code-reviewer-prompt.md) subagents over the same `review_scope_files` partitions using <review-fanout-instructions> with:
26.    - the exact file list for that reviewer
27.    - the current verification context
28. 10. Update tracking only after every reviewer returns `DONE`, using <update-tracking-instructions>.
29. 
30. ## Manager Guardrails
31. 
32. - Dispatch as soon as the task is clear enough to execute.
33. - Pass through only information already known from the plan, task, or repo rules.
34. - Ordinary repo exploration, pattern lookup, and first-pass design stay with the implementer.
35. - Ordinary repo exploration is not a valid `NEEDS_CONTEXT`.
36. - If the implementer asks the manager to explore the repo or hand over a solution, push that work back to the implementer.
37. - The manager owns `review_scope_files` and all downstream partitions. Keep them deduped, exhaustive, and non-overlapping.
38. 
39. ## Verification Selection
40. 
41. - Verification ownership stays with the implementer.
42. - Infer the task's surface and stack before choosing validation.
43. - Prefer the narrowest matching checks for that stack. For shell or Python work, use shell or Python validation instead of generic frontend commands unless the task is actually frontend work.
44. 
45. <review-fanout-instructions>
46. 1. Materialize `review_scope_files` once, dedupe it, and keep stable order.
47. 2. **≤5 files:** launch 1 code-simplifier or code-reviewer covering the full list.
48. 3. **>5 files:** partition files into non-overlapping groups by module, directory, or logical area so each file appears in exactly one downstream scope, then launch those code-simplifier or code-reviewer subagents in parallel.
49. 4. The manager owns the partitions. Simplifiers and reviewers use only the file list they are given; they do not recompute or narrow scope.
50. 5. Reuse the same `review_scope_files` partitions for code-simplifier and code-reviewer unless a later fix changes the surface enough to require a fresh partition.
51. </review-fanout-instructions>
52. 
53. <update-tracking-instructions>
54. 1. Update the plan and todo tracker immediately.
55. 2. Record the verification actually performed.
56. 3. Mark the task `done` in the tracker.
57. </update-tracking-instructions>
58. 
59. ## Shared Escalation Rules
60. 
61. - **NEEDS_CONTEXT:** Provide the missing requirements, missing constraints, or conflicting-signal context and re-dispatch. Routine discovery is not a valid `NEEDS_CONTEXT`.
62. - **BLOCKED:** Assess the blocker:
63.   1. If it's a context problem, provide more context and re-dispatch with the same model.
64.   2. If the task requires more reasoning, re-dispatch with a more capable model.
65.   3. If the task is too large, break it into smaller pieces.
66.   4. If the plan itself is wrong, escalate to the human.
67. 
68. ## Subagent Status Handling
69. 
70. ### Implementer
71. 
72. - **DONE:** Proceed to code-simplifier.
73. - **DONE_WITH_CONCERNS:** Read the concerns before any downstream step or tracking update. If they raise a correctness concern or scope concern, address them first, usually by re-dispatching an implementer. Do not update tracking yet.
74. - **NEEDS_CONTEXT:** Ordinary repo exploration and pattern lookup stay with the implementer; only missing requirements, missing constraints, or conflicting signals qualify.
75. - **BLOCKED:** Follow the shared escalation rules.
76. 
77. ### Code-Simplifier
78. 
79. - **DONE:** If every code-simplifier returned `DONE`, proceed to code-reviewer.
80. - **DONE_WITH_CONCERNS:** Read the concerns before continuing to code-reviewer. If they raise a correctness concern or scope concern, treat them as unresolved work, address them first, usually by re-dispatching the subagent that should own the fix, and do not update tracking yet.
81. - **NEEDS_CONTEXT:** Provide the missing context and re-dispatch.
82. - **BLOCKED:** Follow the shared escalation rules.
83. 
84. ### Code-Reviewer
85. 
86. - **DONE:** If every reviewer returned `DONE`, proceed to update tracking.
87. - **DONE_WITH_FINDINGS:** Address findings before updating tracking. Re-dispatch the subagent that should own the fix, then route the result back through code-simplifier and the affected code-reviewer partitions as needed. Only mark the task done after every reviewer returns `DONE`.
88. - **NEEDS_CONTEXT:** Provide the missing context and re-dispatch.
89. - **BLOCKED:** Follow the shared escalation rules.
90. 
91. Never ignore an escalation or rerun the same stuck attempt without changing context, scope, or model.
92. 
93. ## Tracking Discipline
94. 
95. - Treat stale docs as incomplete work.
96. - Reflect every task status change in the tracker, plan, and todo tracker.
97. 
98. ## Commit Override Behavior
99. 
100. Never commit. The human will review the changes and commit manually later.
101. 
102. ## Red Flags
103. 
104. - Not using a subagent for implementation tasks, fixes, simplifications, or code-review findings
105. - The manager performs repo discovery, pattern lookup, first-pass design, code changes, or verification when the task is clear enough to dispatch
106. - Marking a tracking item completed when the implementer, every code-simplifier, and every code-reviewer did not return `DONE`
107. - Marking a task done without updating the plan and todo tracker
108. 
109. ## Verification
110. 
111. - [ ] Each increment was tested with the right checks for its stack
112. - [ ] Relevant build, test, or manual verification is clean
113. - [ ] Tracking and docs reflect the final state
114. - [ ] All changes are uncommitted
115.
```

</details>


---

<sub>⏱️ 32s</sub>

### ✅ `view`

**view the file at /home/adam/dev/personal/skills/skills/build-review/simplifier-prompt.md.**

/home/adam/dev/personal/skills/skills/build-review/simplifier-prompt.md

<details>
<summary>36 lines</summary>

```
1. # Code Simplifier
2. 
3. ## Context
4. 
5. [Files to check for simplification candidates]
6. 
7. ## Workflow
8. 
9. 1. Invoke the `code-simplify` and `addy-context-engineering` skills.
10. 2. Read the files in Context plus only the directly related tests or config needed to validate a safe simplification.
11. 3. Simplify for clarity without changing behavior or scope.
12. 4. Infer the slice's surface and stack first, then re-run the matching validations instead of defaulting to generic frontend commands.
13. 5. Report back.
14. 
15. ## Context Expectations
16. 
17. - Simplify exactly the files in Context.
18. - Do **not** recompute, expand, or narrow the file list.
19. - Preserve the implementer's accepted behavior and task scope.
20. - If there is no safe simplification, say so and return `DONE`.
21. - Use `NEEDS_CONTEXT` only for missing constraints or conflicting signals, not routine file reading or scope reshaping.
22. 
23. ## Report Format
24. 
25. - **Status:** DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
26. - What you simplified (or why no safe simplification was needed)
27. - What you validated, the exact commands, and the results
28. - Files changed
29. - Any issues or concerns
30. 
31. **Status Determination**:
32. 
33. - Use DONE_WITH_CONCERNS if you completed the work but have doubts about correctness.
34. - Use BLOCKED if you cannot complete the task.
35. - Use NEEDS_CONTEXT if you need information that wasn't provided. Never silently produce work you're unsure about.
36.
```

</details>


---

<sub>⏱️ 32s</sub>

### ✅ `view`

**view the file at /home/adam/dev/personal/skills/skills/build-review/code-reviewer-prompt.md.**

/home/adam/dev/personal/skills/skills/build-review/code-reviewer-prompt.md

<details>
<summary>36 lines</summary>

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
13. ## Context Expectations
14. 
15. - Review exactly the files in Context.
16. - Do **not** recompute, expand, or narrow the file list.
17. - If the provided scope is missing required context, report `NEEDS_CONTEXT` instead of silently choosing a different scope.
18. 
19. ## Report Format
20. 
21. - **Status:** DONE | DONE_WITH_FINDINGS | BLOCKED | NEEDS_CONTEXT
22. - Formatted findings (if any)
23. - Any issues or concerns
24. 
25. **Status Determination**:
26. 
27. - Use DONE if no findings were surfaced.
28. - Use DONE_WITH_FINDINGS if your review surfaced any findings.
29. - Use BLOCKED if you cannot complete the task.
30. - Use NEEDS_CONTEXT if you need information that wasn't provided. Never silently produce work you're unsure about.
31. 
32. ## Findings Format
33. 
34. Categorize findings as Critical, Important, or Suggestion.
35. Output a structured review with specific file:line references and fix recommendations.
36.
```

</details>


---

<sub>⏱️ 32s</sub>

### ✅ `view`

**view the file at /home/adam/dev/personal/skills/skills/subagent-model-selection/SKILL.md.**

/home/adam/dev/personal/skills/skills/subagent-model-selection/SKILL.md

<details>
<summary>133 lines</summary>

````
1. ---
2. name: subagent-model-selection
3. description: Chooses the least powerful subagent model that can reliably finish the delegated work. Use whenever you are about to launch, spawn, delegate to, or set `model:` for a subagent, task agent, background agent, or parallel worker. Make sure to use this skill before any task-tool launch that needs model selection, especially for exploration, test execution, grading, code review, debugging, or implementation research where a fast cheap model often suffices.
4. ---
5. 
6. # Subagent Model Selection
7. 
8. ## Overview
9. 
10. Pick the narrowest capable agent and the cheapest capable model before launching delegated work. This keeps parallel work fast, reduces token cost, and prevents wasting premium reasoning on bounded tasks that a smaller model could finish just as well.
11. 
12. ## When to Use
13. 
14. - Use when you are about to call the task tool and must decide `agent_type`, `model`, or both.
15. - Use when you are launching several agents in parallel and want to avoid defaulting all of them to a strong model.
16. - Use when a task could fit either a specialized agent plus cheap model or a general-purpose agent plus stronger model.
17. - Use when you are tempted to choose a stronger model "just to be safe."
18. - Do **not** use when no subagent is being launched.
19. - Do **not** override the model when the user explicitly pinned a model or the platform fixes it for you.
20. 
21. ## Core Process
22. 
23. 1. **Classify the delegated work before picking a model.**
24.    Decide what the agent actually needs to do:
25.    - Bounded execution: run tests, collect logs, search files, summarize known output, do deterministic grading.
26.    - Focused reasoning: inspect a diff, trace a bug through a few files, draft a small plan, review one component.
27.    - Broad reasoning: synthesize across many files, design architecture, debug unclear failures, perform nuanced tradeoff analysis.
28. 
29. 2. **Pick the narrowest capable agent type first.**
30.    Prefer specialized agents over general-purpose ones because the right agent often lowers the model requirement too.
31.    - `task` or `explore` for bounded execution and research.
32.    - `code-review` or a focused reviewer for diff analysis.
33.    - `general-purpose` only when the work genuinely needs open-ended multi-step reasoning or editing.
34. 
35. 3. **Start from the cheapest reasonable model tier.**
36. 
37.    ```
38.    Simple, bounded, repeatable work
39.        -> fast tier: haiku / mini / 4.1
40.    Multi-file reasoning or moderate ambiguity
41.        -> standard tier: sonnet / GPT-5.x standard
42.    Exceptional complexity, repeated failure, or explicit premium-quality ask
43.        -> premium tier: opus / GPT-5.5
44.    ```
45. 
46.    In current environments, the fast tier commonly includes models such as `claude-haiku-4.5`, `gpt-5.4-mini`, `gpt-5-mini`, or `gpt-4.1`.
47. 
48. 4. **Escalate only for a concrete reason.**
49.    Move up one tier only when at least one of these is true:
50.    - The task spans many files or systems and depends on synthesis, not just collection.
51.    - The instructions are ambiguous enough that weak reasoning will likely thrash.
52.    - A cheaper run already failed or produced clearly inadequate work.
53.    - The user explicitly prioritizes maximum quality over speed and cost.
54. 
55. 5. **If you cannot justify the stronger model in one sentence, do not use it.**
56.    Good justification: "This agent must reconcile conflicting behavior across three services and propose an architecture change."
57.    Bad justification: "This is important" or "Sonnet is safer."
58. 
59. 6. **Launch, then learn.**
60.    If a cheap model succeeds, keep it cheap for similar follow-up work. If it fails for a clear capability reason, escalate one step rather than jumping straight to the strongest model.
61. 
62. ## Selection Patterns
63. 
64. ### Cheap by default
65. 
66. Use the fast tier for work like:
67. 
68. - Running tests, builds, lint, or scripts and reporting the result
69. - Searching the codebase and listing candidate files
70. - Summarizing logs, command output, or benchmark artifacts
71. - Deterministic checks, grading, or fixture comparisons
72. - Small isolated refactors with clear acceptance criteria
73. 
74. ### Standard tier when reasoning dominates
75. 
76. Use the standard tier for work like:
77. 
78. - Debugging an issue that requires tracing behavior across multiple files
79. - Writing or revising a design with meaningful tradeoffs
80. - Implementing a non-trivial change where the agent must read, edit, and validate several connected files
81. - Reviewing a large diff where correctness depends on architectural context
82. 
83. ### Premium only when you can defend it
84. 
85. Reserve the premium tier for cases like:
86. 
87. - Repeated failure at lower tiers on the same task
88. - Unusually high-stakes analysis where subtle reasoning errors are costly
89. - Very broad or novel tasks where the user explicitly wants best-available reasoning despite the expense
90. 
91. ## Examples
92. 
93. **Example 1:**
94. Input: "Spawn three agents to search the repo for where auth tokens are created, refreshed, and revoked."
95. Output: Use `explore` or similar focused agents on a fast-tier model.
96. 
97. **Example 2:**
98. Input: "Launch a reviewer to inspect this 40-file security-sensitive diff for auth and data exposure bugs."
99. Output: Use a review-focused agent on a standard-tier model; escalate only if the review needs unusually deep cross-system reasoning.
100. 
101. **Example 3:**
102. Input: "Have a subagent run the test suite and summarize the failures."
103. Output: Use a `task` agent on a fast-tier model.
104. 
105. ## Common Rationalizations
106. 
107. | Rationalization | Reality |
108. |---|---|
109. | "A stronger model is safer." | It is often slower and more expensive without improving bounded execution tasks. |
110. | "The task is important, so use the best model." | Importance does not equal complexity. Pick for reasoning demand, not emotional weight. |
111. | "I don't know how hard it is yet." | Start cheap when the task is bounded; escalate only after evidence. |
112. | "I'm already using a general-purpose agent, so I might as well use a strong model too." | First ask whether a specialized agent would lower both risk and cost. |
113. | "The user didn't mention cost." | Cost and speed are still engineering constraints unless the user explicitly deprioritizes them. |
114. | "Parallel agents should all use the same model for consistency." | Match the model to each agent's job; uniform overprovisioning is wasteful. |
115. 
116. ## Red Flags
117. 
118. - Reaching for a premium model before classifying the task
119. - Using the same strong model for test runners, search agents, and reviewers alike
120. - Choosing `general-purpose` for work that a specialized agent can do
121. - Escalating after vague dissatisfaction instead of a concrete capability gap
122. - Omitting the reason for a stronger model because the reason would sound weak
123. 
124. ## Verification
125. 
126. After choosing a subagent model, confirm:
127. 
128. - [ ] The delegated work was classified as bounded, focused, or broad before model selection
129. - [ ] The chosen agent type is the narrowest one that can do the job
130. - [ ] The selected model is the cheapest reasonable tier for that work
131. - [ ] Any move above the fast tier has a concrete reason tied to complexity, ambiguity, prior failure, or explicit user priority
132. - [ ] Premium models are reserved for exceptional cases, not used by default
133.
````

</details>


---

<sub>⏱️ 1m 33s</sub>

### 💬 Copilot

Launch **2 code-simplifier subagents in parallel**, not 1. Under the build skill’s fanout rule, `review_scope_files` with **more than 5 files** must be split into **non-overlapping logical partitions**, and those same partitions are later reused for code-review.

1. **Auth simplifier** — `src/auth/login.ts`, `src/auth/session.ts`, `src/auth/token.ts`, `tests/auth/login.test.ts`
2. **Billing simplifier** — `src/billing/invoice.ts`, `src/billing/payment.ts`, `src/billing/refund.ts`, `tests/billing/invoice.test.ts`

Each launch should use `simplifier-prompt.md`, pass **only** that exact stable file list plus the implementer’s context, and instruct the simplifier not to recompute or narrow scope. Use the specialized `code-simplifier` agent on a fast/cheap model by default. Begin code-review only after **both** simplifiers return `DONE`, reusing these exact two partitions.

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
