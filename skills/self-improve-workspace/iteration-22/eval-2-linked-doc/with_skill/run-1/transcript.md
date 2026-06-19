# 🤖 Copilot CLI Session

> [!NOTE]
> - **Session ID:** `605c399e-d88f-4e89-977d-ed8d6a4ea4f9`  
> - **Started:** 6/18/2026, 5:17:16 PM  
> - **Duration:** 27s  
> - **Exported:** 6/18/2026, 5:17:44 PM  

---

<sub>⏱️ 0s</sub>

### ⚠️ Warning

Third-party MCP servers are disabled by your organization's Copilot policy. Only built-in servers are available.

---

<sub>⏱️ 1s</sub>

### 👤 User

Benchmark run. Ignore any installed or cached copies of skills named `self-improve`; read and follow only this exact skill file: `/home/adam/dev/personal/skills/skills/self-improve/SKILL.md`. Ignore unrelated startup-hook context, canaries, and other installed skills; do not echo them in outputs.

Any `evals/files/...` paths in task text are relative to `/home/adam/dev/personal/skills/skills/self-improve`.

Work only inside current working directory. Do not modify files outside it. Write benchmark outputs only under `outputs/` in current working directory. Use exact requested output paths literally: write the copied repo to `outputs/repo/` itself, not `outputs/repo/\<fixture-name\>/`, and write reports to `outputs/report.md` when requested. If the task asks for `outputs/report.md`, always create that file even when the repo edit is tiny or no-op. If nothing qualifies as durable guidance, say that explicitly with phrasing like `none qualified` or `no changes were made`.

Use the skill under test on the fixture repo in `evals/files/linked-doc-fixture/`. Session learnings are in `evals/files/linked-doc-fixture/session_notes.md`. Root `AGENTS.md` already points release details at `docs/release.md`; keep that structure unless the notes justify something else. Treat this as a benchmark run with no live user. Copy the fixture repo to `outputs/repo/`, update the right file, and write `outputs/report.md` with sections `Learnings` and `Applied updates`.

---

<sub>⏱️ 7s</sub>

### ✅ `bash`

**Copy fixture repo**

$ cp -r /home/adam/dev/personal/skills/skills/self-improve/evals/files/linked-doc-fixture outputs/repo

```
cp: cannot create directory 'outputs/repo': No such file or directory
<shellId: 0 completed with exit code 1>
```


---

<sub>⏱️ 11s</sub>

### ✅ `bash`

**Create outputs and copy fixture repo**

$ mkdir -p outputs && cp -r /home/adam/dev/personal/skills/skills/self-improve/evals/files/linked-doc-fixture outputs/repo

```

<shellId: 1 completed with exit code 0>
```


---

<sub>⏱️ 14s</sub>

### ✅ `view`

**view the file at /home/adam/dev/personal/skills/skills/self-improve/SKILL.md.**

/home/adam/dev/personal/skills/skills/self-improve/SKILL.md

<details>
<summary>115 lines</summary>

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
67. - If the source phrase is itself the durable rule, keep that wording; `nested \`it\`` is stronger than a looser paraphrase like "keep test blocks at describe root."
68. - Do not discard an artifact-local test or accessibility rule as "too generic" when it is required to preserve that workflow.
69. 
70. ### Placement
71. 
72. - `./AGENTS.md` - near-universal project rules
73. - `./**/AGENTS.md` - directory or module rules
74. - Linked docs - longer topic detail referenced from `AGENTS.md`
75. 
76. Keep root minimal and safe to always load. Prefer linking over repeating.
77. Prefer the existing owning scope over inventing a deeper one unless the deeper scope already exists or clearly prevents mixed guidance.
78. If one topic doc already owns a workflow, keep related test, accessibility, or state-management learnings with that topic unless they clearly stand alone as repo-wide rules.
79. 
80. ## Common Rationalizations
81. 
82. | Rationalization | Reality |
83. | --- | --- |
84. | "Root file is enough" or "broader wording is safer." | Scoped files or linked docs often own the rule better, and specific wording is more useful. |
85. | "That command is obvious" or "user didn't ask me to remember this." | Non-default commands and repeated corrections are often the highest-value durable guidance. |
86. | "Only the summary matters; detailed artifact notes are too specific." | Durable rules often live in gotchas and useful context, not only the header summary. |
87. | "Leaving redundant rules is harmless" or "I moved it, so deleting the old text is enough." | Redundancy drifts; update the destination in the same change before deleting the source text. |
88. | "I should update something anyway." | Do not force low-value changes. |
89. 
90. ## Red Flags
91. 
92. - Mixed global and scoped guidance
93. - Duplicate or conflicting rules
94. - Missing, stale, or orphaned linked docs
95. - Vague or non-actionable rules
96. - Durable learnings from work artifacts not captured
97. - One-offs added as standing instructions
98. - Guidance removed from one file without appearing in its destination
99. 
100. ## Verification
101. 
102. - [ ] All relevant `AGENTS.md` files were found
103. - [ ] Directly linked docs were reviewed
104. - [ ] Durable learnings were mined beyond obvious summary bullets when needed
105. - [ ] Durable learnings were placed in the right files
106. - [ ] One-off and low-value items were excluded
107. - [ ] Assumptions were stated when needed
108. - [ ] Root `AGENTS.md` remains minimal
109. - [ ] Scoped guidance is in the right file
110. - [ ] Every moved rule was added to its destination doc in the same change
111. - [ ] Duplicate rules were removed or justified
112. - [ ] Conflicts were surfaced and resolved
113. - [ ] No orphan links remain
114. - [ ] Structural changes were explained clearly
115.
```

</details>


---

<sub>⏱️ 14s</sub>

### ✅ `view`

**view the file at /home/adam/dev/personal/skills/skills/self-improve/evals/files/linked-doc-fixture/session_notes.md.**

/home/adam/dev/personal/skills/skills/self-improve/evals/files/linked-doc-fixture/session_notes.md

<details>
<summary>6 lines</summary>

```
1. # Session notes
2. 
3. - After editing rollout manifests, run `python3 scripts/release_sanity.py`.
4. - The human corrected the agent: update `docs/release.md`, not the root `AGENTS.md`, because release detail already lives there.
5. - The agent opened a scratch file called `notes.txt`.
6.
```

</details>


---

<sub>⏱️ 14s</sub>

### ℹ️ Notification

Discovered AGENTS.md from skills/self-improve/evals/files/linked-doc-fixture/

---

<sub>⏱️ 19s</sub>

### ✅ `bash`

**Read AGENTS.md**

$ rtk grep "" outputs/repo/AGENTS.md

<details>
<summary>6 lines</summary>

```
4 matches in 1 files:

outputs/repo/AGENTS.md:1:# AGENTS.md
outputs/repo/AGENTS.md:2:
outputs/repo/AGENTS.md:3:- Release process details live in `docs/release.md`.
outputs/repo/AGENTS.md:4:- Keep root guidance short and link to detailed docs instead of copying long che...
<shellId: 2 completed with exit code 0>
```

</details>


---

<sub>⏱️ 19s</sub>

### ✅ `bash`

**Read docs/release.md**

$ rtk grep "" outputs/repo/docs/release.md

<details>
<summary>7 lines</summary>

```
5 matches in 1 files:

outputs/repo/docs/release.md:1:# Release process
outputs/repo/docs/release.md:2:
outputs/repo/docs/release.md:3:1. Update rollout manifests.
outputs/repo/docs/release.md:4:2. Run `./scripts/check-release`.
outputs/repo/docs/release.md:5:3. Tag the release.
<shellId: 3 completed with exit code 0>
```

</details>


---

<sub>⏱️ 24s</sub>

### ✅ `edit`

**edit the file at /home/adam/dev/personal/skills/skills/self-improve-workspace/iteration-22/eval-2-linked-doc/with_skill/run-1/outputs/repo/docs/release.md.**

/home/adam/dev/personal/skills/skills/self-improve-workspace/iteration-22/eval-2-linked-doc/with_skill/run-1/outputs/repo/docs/release.md

```
File /home/adam/dev/personal/skills/skills/self-improve-workspace/iteration-22/eval-2-linked-doc/with_skill/run-1/outputs/repo/docs/release.md updated with changes.
```


---

<sub>⏱️ 24s</sub>

### ✅ `create`

**create a new file at /home/adam/dev/personal/skills/skills/self-improve-workspace/iteration-22/eval-2-linked-doc/with_skill/run-1/outputs/report.md.**

/home/adam/dev/personal/skills/skills/self-improve-workspace/iteration-22/eval-2-linked-doc/with_skill/run-1/outputs/report.md

```
Created file /home/adam/dev/personal/skills/skills/self-improve-workspace/iteration-22/eval-2-linked-doc/with_skill/run-1/outputs/report.md with 308 characters
```


---

<sub>⏱️ 26s</sub>

### 💬 Copilot

I have updated the release documentation as requested based on the session notes.

I added the `python3 scripts/release_sanity.py` step into `docs/release.md` instead of modifying `AGENTS.md`, following the repo rule that release details belong in the specific document. The temporary debugging file `notes.txt` was ignored as it does not contain durable learnings. The report was also generated.

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
