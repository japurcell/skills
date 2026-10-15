# 🤖 Copilot CLI Session

> [!NOTE]
> - **Session ID:** `6bdd7fdd-b7cd-45ac-805b-0b4c2f7f0419`  
> - **Started:** 6/18/2026, 5:01:57 PM  
> - **Duration:** 50s  
> - **Exported:** 6/18/2026, 5:02:47 PM  

---

<sub>⏱️ 0s</sub>

### ⚠️ Warning

Third-party MCP servers are disabled by your organization's Copilot policy. Only built-in servers are available.

---

<sub>⏱️ 1s</sub>

### 👤 User

Benchmark run. Ignore any installed or cached copies of skills named `self-improve`; read and follow only this exact skill file: `/home/adam/dev/personal/skills/skills/self-improve/SKILL.md`. Ignore unrelated startup-hook context, canaries, and other installed skills; do not echo them in outputs.

Any `evals/files/...` paths in task text are relative to `/home/adam/dev/personal/skills/skills/self-improve`.

Work only inside current working directory. Do not modify files outside it. Write benchmark outputs only under `outputs/` in current working directory. Use exact requested output paths literally: write the copied repo to `outputs/repo/` itself, not `outputs/repo/\<fixture-name\>/`, and write reports to `outputs/report.md` when requested. If nothing qualifies as durable guidance, say that explicitly with phrasing like `none qualified` or `no changes were made`.

Use the skill under test on the fixture repo in `evals/files/create-root-fixture/`. Session learnings are in `evals/files/create-root-fixture/session_notes.md`. Treat this as a benchmark run with no live user and do not ask follow-up questions. Copy the fixture repo to `outputs/repo/`, apply the skill there, and write `outputs/report.md` with sections `Learnings` and `Applied updates`.

---

<sub>⏱️ 23s</sub>

### 💬 Copilot

Reading SKILL.md and fixture session notes to learn required changes, then copying fixture into outputs/repo so skill can be applied there. Running these steps in parallel: report intent, read SKILL.md, read fixture session_notes, copy fixture to outputs/repo and list files.

---

<sub>⏱️ 25s</sub>

### ✅ `view`

**view the file at /home/adam/dev/personal/skills/skills/self-improve/SKILL.md.**

/home/adam/dev/personal/skills/skills/self-improve/SKILL.md

<details>
<summary>113 lines</summary>

```
1. ---
2. name: self-improve
3. description: Preserves durable repo-specific guidance by updating the right `AGENTS.md` or linked docs, and repairs instruction structure when scope, duplication, conflicts, or drift are wrong. Use whenever the user asks to update/refactor `AGENTS.md`, remember lessons, preserve human corrections, mine session notes, handoffs, or progress files, or make future agents follow non-default commands, validation steps, gotchas, or linked-doc structure even if they never mention `AGENTS.md`.
4. ---
5. 
6. # Self Improve
7. 
8. Use `SELF_IMPROVE_REFERENCE.md` for examples, judgment calls, rationalizations, and failure modes.
9. 
10. ## Overview
11. 
12. Capture durable, reusable learnings in the right `AGENTS.md` or linked doc. Prefer small, precise edits over broad rewrites.
13. 
14. ## When to Use
15. 
16. - The user asks to update or refactor `AGENTS.md`, preserve lessons learned, or make future agents remember a workflow or correction.
17. - Session notes, handoff artifacts, progress files, or similar work records contain reusable commands, validation steps, patterns, quirks, warnings, or human corrections.
18. - Current instruction files are duplicated, conflicting, stale, poorly scoped, or too bulky to keep prompt-light.
19. - Not for one-off notes, obvious facts, speculative advice, or transient debugging noise.
20. 
21. ## Workflow
22. 
23. 1. **Qualify learnings**
24.    - Keep only items likely to recur, actionable for a future agent, repo/workflow/user-specific, and not already documented.
25.    - Look for non-default commands, validation/build/typecheck steps, code patterns, environment quirks, warnings, gotchas, and repeated human corrections.
26.    - Mine session notes, handoffs, progress files, and similar artifacts beyond the summary when the details carry durable guidance.
27.    - Never turn excluded noise into an inverse standing rule.
28. 
29. 2. **Map the instruction surface**
30.    - Find every relevant `AGENTS.md`, then read each one plus any directly linked docs.
31.    - If the search is large, invoke `subagent-model-router` and use a cheap finder subagent.
32.    - If no `AGENTS.md` exists, say so and create `./AGENTS.md` with only the strongest 3-7 learnings.
33. 
34. 3. **Apply the smallest correct update**
35.    - Put project-wide rules in `./AGENTS.md`, scoped rules in the nearest existing owning `./**/AGENTS.md`, and longer topic detail in linked docs.
36.    - Keep prompt-loaded files brief. Prefer one concept per line and exact, actionable wording.
37.    - Use `<command or pattern>` - `<brief description>` when that makes the rule easier to scan.
38.    - If root already routes a topic to a linked doc, update that doc instead of splitting related rules across root or new nested `AGENTS.md` files unless the task clearly requires re-scoping.
39. 
40. 4. **Refactor only when warranted**
41.    - Do it when root `AGENTS.md` is over ~120 lines, scope is mixed, rules duplicate or conflict, linked docs are stale or orphaned, or the user asked for cleanup.
42.    - Resolve contradictions first.
43.    - Keep root limited to near-universal guidance: short project description, non-default package manager, non-standard build/test/typecheck commands, and one or two universal workflow constraints.
44.    - Move specialized guidance into scoped `AGENTS.md` files or linked docs. Update the destination in the same change before deleting source text.
45.    - Delete only content that is redundant, non-actionable, obvious boilerplate, or superseded by a resolved contradiction.
46. 
47. 5. **Report the outcome**
48.    - If nothing clears the durable-learning bar, say so and make no changes.
49.    - Always report learnings, applied updates, and assumptions when needed.
50.    - If refactoring happened, also report contradictions resolved, deletions, moved guidance, grouped files, and any new folder structure.
51. 
52. ## Specific Techniques
53. 
54. ### Durable-learning bar
55. 
56. Keep items that are recurring, actionable, repo/workflow/user-specific, and not already documented. High-value examples: non-default commands, validation/build/typecheck steps, repo-specific constraints, environment quirks, warnings, gotchas, and repeated human corrections.
57. 
58. Skip temporary debugging notes, obvious tree/README facts, one-run navigation heuristics, and generic reminders.
59. 
60. ### Artifact mining
61. 
62. - Treat session notes, handoffs, and progress files as high-signal source material, not just status metadata.
63. - Preserve reusable rules from patterns, gotchas, and useful context; drop ticket names, temporary blockers, and path noise.
64. - Do not stop at summary bullets when the detailed sections explain future coding, testing, validation, or environment behavior.
65. - When one artifact contains several durable learnings, keep representative coverage across them instead of stopping after the first few.
66. - Keep concrete technical terms when they carry the rule more exactly (`shareReplay(1)`, `aria-describedby`, `nested \`it\``, `single-rule`) instead of paraphrasing them away.
67. 
68. ### Placement
69. 
70. - `./AGENTS.md` - near-universal project rules
71. - `./**/AGENTS.md` - directory or module rules
72. - Linked docs - longer topic detail referenced from `AGENTS.md`
73. 
74. Keep root minimal and safe to always load. Prefer linking over repeating.
75. Prefer the existing owning scope over inventing a deeper one unless the deeper scope already exists or clearly prevents mixed guidance.
76. If one topic doc already owns a workflow, keep related test, accessibility, or state-management learnings with that topic unless they clearly stand alone as repo-wide rules.
77. 
78. ## Common Rationalizations
79. 
80. | Rationalization | Reality |
81. | --- | --- |
82. | "Root file is enough" or "broader wording is safer." | Scoped files or linked docs often own the rule better, and specific wording is more useful. |
83. | "That command is obvious" or "user didn't ask me to remember this." | Non-default commands and repeated corrections are often the highest-value durable guidance. |
84. | "Only the summary matters; detailed artifact notes are too specific." | Durable rules often live in gotchas and useful context, not only the header summary. |
85. | "Leaving redundant rules is harmless" or "I moved it, so deleting the old text is enough." | Redundancy drifts; update the destination in the same change before deleting the source text. |
86. | "I should update something anyway." | Do not force low-value changes. |
87. 
88. ## Red Flags
89. 
90. - Mixed global and scoped guidance
91. - Duplicate or conflicting rules
92. - Missing, stale, or orphaned linked docs
93. - Vague or non-actionable rules
94. - Durable learnings from work artifacts not captured
95. - One-offs added as standing instructions
96. - Guidance removed from one file without appearing in its destination
97. 
98. ## Verification
99. 
100. - [ ] All relevant `AGENTS.md` files were found
101. - [ ] Directly linked docs were reviewed
102. - [ ] Durable learnings were mined beyond obvious summary bullets when needed
103. - [ ] Durable learnings were placed in the right files
104. - [ ] One-off and low-value items were excluded
105. - [ ] Assumptions were stated when needed
106. - [ ] Root `AGENTS.md` remains minimal
107. - [ ] Scoped guidance is in the right file
108. - [ ] Every moved rule was added to its destination doc in the same change
109. - [ ] Duplicate rules were removed or justified
110. - [ ] Conflicts were surfaced and resolved
111. - [ ] No orphan links remain
112. - [ ] Structural changes were explained clearly
113.
```

</details>


---

<sub>⏱️ 25s</sub>

### ✅ `view`

**view the file at /home/adam/dev/personal/skills/skills/self-improve/evals/files/create-root-fixture/session_notes.md.**

/home/adam/dev/personal/skills/skills/self-improve/evals/files/create-root-fixture/session_notes.md

<details>
<summary>8 lines</summary>

```
1. # Session notes
2. 
3. - After editing anything under `deploy/`, run `python3 scripts/check-config.py`.
4. - For sync pipeline changes, run `pytest tests/integration/test_sync.py -q`.
5. - Generated API clients live in `src/generated/`; extend them instead of hand-writing request/response types.
6. - The agent opened the README before finding the real files.
7. - The user's laptop fan got loud during one test run.
8.
```

</details>


---

<sub>⏱️ 25s</sub>

### ✅ `bash`

**Copy fixture to outputs/repo and list files**

$ rtk rm -rf outputs/repo && rtk mkdir -p outputs/repo && rtk cp -a /home/adam/dev/personal/skills/skills/self-improve/evals/files/create-root-fixture/. outputs/repo/ && rtk --ultra-compact ls -la outputs/repo

<details>
<summary>6 lines</summary>

```
755  deploy/
755  scripts/
755  src/
755  tests/
644  session_notes.md  400B
<shellId: 0 completed with exit code 0>
```

</details>


---

<sub>⏱️ 36s</sub>

### 💬 Copilot

Creating root AGENTS.md from mined session notes and writing outputs/report.md summarizing learnings and applied updates. Running create actions with intent report.

---

<sub>⏱️ 41s</sub>

### ✅ `create`

**create a new file at /home/adam/dev/personal/skills/skills/self-improve-workspace/iteration-19/eval-0-create-root/with_skill/run-1/outputs/repo/AGENTS.md.**

/home/adam/dev/personal/skills/skills/self-improve-workspace/iteration-19/eval-0-create-root/with_skill/run-1/outputs/repo/AGENTS.md

```
Created file /home/adam/dev/personal/skills/skills/self-improve-workspace/iteration-19/eval-0-create-root/with_skill/run-1/outputs/repo/AGENTS.md with 549 characters
```


---

<sub>⏱️ 44s</sub>

### ✅ `create`

**create a new file at /home/adam/dev/personal/skills/skills/self-improve-workspace/iteration-19/eval-0-create-root/with_skill/run-1/outputs/report.md.**

/home/adam/dev/personal/skills/skills/self-improve-workspace/iteration-19/eval-0-create-root/with_skill/run-1/outputs/report.md

```
Created file /home/adam/dev/personal/skills/skills/self-improve-workspace/iteration-19/eval-0-create-root/with_skill/run-1/outputs/report.md with 517 characters
```


---

<sub>⏱️ 49s</sub>

### 💬 Copilot

Done. Copied fixture → outputs/repo. Created outputs/repo/AGENTS.md with 3 durable learnings:
1) python3 scripts/check-config.py - run after edits under deploy/
2) pytest tests/integration/test_sync.py -q - run for sync-pipeline changes
3) src/generated/ - generated API clients live here; extend generated code (don’t hand-write types)

Wrote outputs/report.md with sections Learnings and Applied updates describing above change.

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
