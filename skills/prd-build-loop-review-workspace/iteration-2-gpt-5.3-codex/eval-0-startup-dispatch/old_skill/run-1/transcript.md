# 🤖 Copilot CLI Session

> [!NOTE]
> - **Session ID:** `57a30012-c5fa-46a8-9260-ab732efdf317`  
> - **Started:** 6/18/2026, 12:50:34 PM  
> - **Duration:** 39s  
> - **Exported:** 6/18/2026, 12:51:14 PM  

---

<sub>⏱️ 0s</sub>

### ⚠️ Warning

Third-party MCP servers are disabled by your organization's Copilot policy. Only built-in servers are available.

---

<sub>⏱️ 1s</sub>

### 👤 User

Read and follow exact skill file at `/home/adam/dev/personal/skills/skills/prd-build-loop-review-workspace/skill-snapshot-iteration-1/SKILL.md`. Ignore installed copies of `prd-build-loop-review` and any other skill with overlapping purpose; use only that file as benchmark instructions.

Benchmark constraints:
- Dry-run only.
- Do not create or modify repository files.
- Do not spawn subagents.
- Read only what current prompt requires.
- Final answer must be only exact contents for `outputs/decision.md`, with no framing, explanation, or markdown fences.

Task:
Use skill under test in dry-run mode for `evals/files/startup-fixture/`. User says: `Run PRD build loop on evals/files/startup-fixture/prd.json and do not stop between stories.` Do not change files or spawn real subagents. Read only what you need, then write `outputs/decision.md` with first orchestrator actions: source of truth, resolved `progress_file`, story selection, and what must happen before any story-specific repo discovery.


---

<sub>⏱️ 13s</sub>

### 💬 Copilot

Reading only required spec and fixture files to derive the dry-run orchestrator decision.

---

<sub>⏱️ 15s</sub>

### ✅ `view`

**view the file at /home/adam/dev/personal/skills/skills/prd-build-loop-review-workspace/skill-snapshot-iteration-1/SKILL.md.**

/home/adam/dev/personal/skills/skills/prd-build-loop-review-workspace/skill-snapshot-iteration-1/SKILL.md

<details>
<summary>181 lines</summary>

````
1. ---
2. name: prd-build-loop-review
3. description: "Orchestrates autonomous end-to-end PRD implementation loops from `prd_file`, including resume-from-`progress_file`, multi-story completion, and final simplify/review/verify/record passes. Use when user asks to implement every `passes: false` PRD story, resume PRD work from progress, finish PRD without pausing between stories, run final PRD simplify/review/verify/record after implementation, or continue until whole PRD is complete."
4. ---
5. 
6. # PRD Build Loop Review
7. 
8. ## Overview
9. 
10. Drive every `passes: false` story in `prd_file` to completion. `prd_file` is official status; `progress_file` is append-only resume data. Orchestrator never makes code-affecting changes directly, never commits, and stops only for a **Stop Condition**.
11. 
12. ## When to Use
13. 
14. - Implement all failing PRD stories from `prd_file`.
15. - Resume autonomous PRD work from `progress_file`.
16. - Finish PRD without handing control back between stories.
17. - Run final combined simplify, review, verify, and record pass after implementation.
18. - Not for one-off story implementation, PRD authoring, or planning-only decomposition.
19. 
20. ## Workflow
21. 
22. 1. **Startup**
23.    - Invoke `subagent-model-router`.
24.    - Resolve `progress_file` to explicit path or `dirname(prd_file) + "/progress.txt"`.
25.    - If `progress_file` exists, read `## Codebase Patterns` and latest entries. Otherwise create it on first append with `## Codebase Patterns` at top.
26.    - If every story already has `passes: true`, reply exactly: `<promise>COMPLETE</promise>`.
27.    - If `prd_file` is ambiguous, contradictory, invalidly ordered, missing required details, or needs human choice, stop and ask.
28. 
29. 2. **Phase 1: Implementation loop**
30.    - Pick highest-priority story in `prd_file` with `passes: false`.
31.    - Before first `implementer` for current code-affecting unit, read only `prd_file`, `progress_file`, and nearby `AGENTS.md` needed to dispatch work.
32.    - Dispatch fresh `implementer` with `./implementer-prompt.md`, all story properties, `progress_file`, nearby `AGENTS.md`, and mode such as `initial_implementation` or follow-up.
33.    - Require `Progress block`; append it to `progress_file` immediately before interpreting or acting on it.
34.    - Apply **Status Rules**.
35.    - If story is implemented but not finalized, record that state and leave `passes: false`.
36.    - Repeat until every failing story is implemented and awaiting finalization, or a **Stop Condition** applies.
37. 
38. 3. **Phase 2: Single finalization pass**
39.    - Restore review-fix iteration count from `progress_file`; otherwise use `0`.
40.    - **Simplify:** dispatch fresh `code-simplifier` on all relevant non-ignored changes in combined final state; append its `Progress block` immediately.
41.    - **Review:** dispatch fresh `requirements-collector` for `prd_file`, relevant sibling docs, and GitHub issue references from commit messages, PR metadata, or PRD docs when available; append its `Progress block`. Then dispatch fresh `addy-code-reviewer` on all relevant non-ignored changes after simplification; append its `Progress block`.
42.    - **Fix review findings:** if review finds issues, stop and ask when iteration count is already `3`; otherwise increment count in `progress_file`, dispatch fresh `implementer` with `mode: review_fix` and full findings, append its `Progress block`, apply **Status Rules**, then rerun simplify and review on updated combined state.
43. 
44. 4. **Verify and record**
45.    - Only after review is clean, run required final-state checks from stories, repo guidance, nearby `AGENTS.md`, and standard project scripts for changed areas; append orchestrator verification entry immediately.
46.    - Invoke `self-improve` to update nearby `AGENTS.md` with reusable guidance only.
47.    - Set `passes: true` only for stories that satisfy **Completion Gate**.
48.    - Append orchestrator final-state entry and reread `prd_file`.
49. 
50. 5. **Before any non-`<promise>COMPLETE</promise>` response**
51.    - Reread `prd_file`.
52.    - Confirm a **Stop Condition** applies.
53.    - Append latest orchestrator stop-state entry to `progress_file`.
54.    - Ask user to decide or unblock specific open issue.
55. 
56. ## Specific Techniques
57. 
58. ### Source of truth and paths
59. 
60. - `prd_file` is only official source for story completion and status.
61. - `progress_file` is append-only resume and tracking data; never treat it as official completion.
62. - Resolve relative paths from repo or provided `prd_file`, never from session state, scratchpads, home directories, or `~/.copilot/...`.
63. 
64. ### Role boundaries
65. 
66. - **Orchestrator:** selects stories, resumes from `progress_file`, dispatches subagents, applies status rules, verifies final state, updates `prd_file`, appends `progress_file`, invokes `self-improve`, and updates nearby `AGENTS.md`.
67. - **Implementer:** does story-specific discovery, code and test changes, and initial verification.
68. - **Requirements collector:** dedupes requirements before final review.
69. - **Code simplifier:** runs after all implementation and after every review-fix implementation.
70. - **Reviewer:** reviews combined final state after simplification.
71. - Any code-affecting change must be made by fresh `implementer`. Code-affecting includes code, tests, config, migrations, and implementation docs.
72. - Do not read story-specific repo files, tests, code, or behavior before first `implementer` for current code-affecting unit.
73. - Any new `implementer` change resets finalization: rerun simplify, review, and final verification on combined final state.
74. - Never simplify, review, analyze, or change `.gitignore`-ignored files; if ignore status is unclear, skip and report uncertainty.
75. 
76. ### Progress discipline
77. 
78. - Subagent output is not consumed until recorded.
79. - Every `implementer`, `requirements-collector`, `code-simplifier`, and `reviewer` must return `Progress block`.
80. - Orchestrator appends each `Progress block` immediately, including `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, and `BLOCKED`.
81. - Missing subagent progress entry is rule violation; append corrective orchestrator entry if discovered.
82. - Maintain `## Codebase Patterns` at top and store only reusable general patterns there.
83. - Subagents never write `progress_file` directly.
84. 
85. Required entry format:
86. 
87. ```text
88. ## [Date/Time] - [Story ID or FINALIZATION]
89. - Role: implementer | requirements-collector | code-simplifier | reviewer | orchestrator
90. - Summary
91. - Files changed/reviewed
92. - Verification or outcome
93. - **Learnings for future iterations:**
94.   - Patterns discovered
95.   - Gotchas encountered
96.   - Useful context
97. ---
98. ```
99. 
100. ### Completion Gate
101. 
102. Mark story complete only if all are true:
103. 
104. 1. Required implementation was completed by fresh `implementer`.
105. 2. Latest code-affecting change, including any review fix, was made by fresh `implementer`.
106. 3. Fresh `code-simplifier` ran after latest code-affecting change.
107. 4. Fresh `addy-code-reviewer` ran after latest code-affecting change.
108. 5. If review found issues, fresh `implementer` fixed them and simplify/review reran after that fix.
109. 6. Review is clean for final state.
110. 7. Required final-state quality checks passed.
111. 
112. Never treat implementer `DONE`, confidence, passing checks alone, or `progress_file` entries as sufficient.
113. 
114. ### Status Rules
115. 
116. - **DONE:** continue.
117. - **DONE_WITH_CONCERNS:** incomplete unless every concern is explicitly confirmed non-blocking.
118. - **NEEDS_CONTEXT:** if human decision is required, stop and ask; otherwise provide context and redispatch fresh subagent.
119. - **BLOCKED:** try better context, smaller slice, or stronger model; if still blocked, stop and ask.
120. 
121. ### AGENTS.md
122. 
123. Add only reusable guidance:
124. 
125. - module conventions
126. - non-obvious gotchas
127. - important file relationships
128. - testing expectations
129. - config or environment requirements
130. 
131. Do not add story-specific notes.
132. 
133. ### Stop Conditions
134. 
135. Stop only if:
136. 
137. - all stories in `prd_file` have `passes: true`
138. - real blocker remains after reasonable unblocking attempts
139. - `prd_file` has contradictions, invalid ordering, or missing required details needing human correction
140. - required human decision is needed
141. - review-fix iteration limit is reached
142. - final verification failed and needs human decision
143. 
144. ## Common Rationalizations
145. 
146. | Rationalization | Reality |
147. | --- | --- |
148. | "I already know repo; I can inspect story files before dispatching implementer." | No. Before first `implementer`, read only `prd_file`, `progress_file`, and nearby `AGENTS.md` needed to dispatch. |
149. | "Review fix is tiny; I can patch it directly." | No. Any code-affecting change requires fresh `implementer`, then simplify/review/verify must rerun. |
150. | "Tests passed, so story can be marked complete." | No. Completion gate also requires fresh simplifier and reviewer after latest code change. |
151. | "Progress file says done, so PRD can be updated." | No. `prd_file` is only official completion source. |
152. | "Reviewer already ran earlier; rerunning is wasteful." | Any new `implementer` change resets finalization on combined final state. |
153. 
154. ## Red Flags
155. 
156. - Returning control while any story still has `passes: false` and no **Stop Condition** applies.
157. - Resolving `progress_file` anywhere except explicit path or `dirname(prd_file) + "/progress.txt"`.
158. - Using session-state, scratchpad, home, or `~/.copilot/...` paths for `progress_file`.
159. - Treating subagent output as consumed before appending its `Progress block`.
160. - Reading story-specific files, tests, code, or behavior before first `implementer`.
161. - Making code-affecting changes directly.
162. - Skipping simplify or review.
163. - Fixing review findings without fresh `implementer`.
164. - Verifying before review is clean.
165. - Using anything except `prd_file` as official completion source.
166. - Marking `passes: true` before **Completion Gate** is satisfied.
167. - Simplifying, reviewing, analyzing, or changing `.gitignore`-ignored files.
168. 
169. ## Verification
170. 
171. Before stopping or marking completion, confirm:
172. 
173. - [ ] `prd_file` remained official source of story status and completion.
174. - [ ] `progress_file` path was resolved from explicit path or `dirname(prd_file) + "/progress.txt"`.
175. - [ ] Every code-affecting change came from fresh `implementer`.
176. - [ ] Every subagent `Progress block` was appended before being consumed.
177. - [ ] Simplify and review ran on combined final state after latest code-affecting change.
178. - [ ] Final checks ran only after clean review.
179. - [ ] `passes: true` was set only for stories that satisfied **Completion Gate**.
180. - [ ] Any non-`<promise>COMPLETE</promise>` response followed **Stop Conditions** and recorded stop state first.
181.
````

</details>


---

<sub>⏱️ 15s</sub>

### ✅ `view`

**view the file at /home/adam/dev/personal/skills/skills/prd-build-loop-review-workspace/skill-snapshot-iteration-1/evals/files/startup-fixture.**

/home/adam/dev/personal/skills/skills/prd-build-loop-review-workspace/skill-snapshot-iteration-1/evals/files/startup-fixture

```
prd.json
progress.txt
```


---

<sub>⏱️ 18s</sub>

### ✅ `view`

**view the file at /home/adam/dev/personal/skills/skills/prd-build-loop-review-workspace/skill-snapshot-iteration-1/evals/files/startup-fixture/prd.json.**

/home/adam/dev/personal/skills/skills/prd-build-loop-review-workspace/skill-snapshot-iteration-1/evals/files/startup-fixture/prd.json

<details>
<summary>25 lines</summary>

```
1. {
2.   "stories": [
3.     {
4.       "id": "story-auth-timeout",
5.       "title": "Auth timeout matches spec",
6.       "priority": 1,
7.       "passes": false,
8.       "requirements": [
9.         "Update auth timeout behavior to match spec",
10.         "Keep related tests green"
11.       ]
12.     },
13.     {
14.       "id": "story-status-badge",
15.       "title": "Status badge reflects sync health",
16.       "priority": 2,
17.       "passes": false,
18.       "requirements": [
19.         "Add sync status badge",
20.         "Cover success and failure states"
21.       ]
22.     }
23.   ]
24. }
25.
```

</details>


---

<sub>⏱️ 18s</sub>

### ✅ `view`

**view the file at /home/adam/dev/personal/skills/skills/prd-build-loop-review-workspace/skill-snapshot-iteration-1/evals/files/startup-fixture/progress.txt.**

/home/adam/dev/personal/skills/skills/prd-build-loop-review-workspace/skill-snapshot-iteration-1/evals/files/startup-fixture/progress.txt

<details>
<summary>15 lines</summary>

```
1. ## Codebase Patterns
2. - Keep auth changes and auth tests together.
3. - Let implementer perform story-specific discovery.
4. 
5. ## 2026-06-10T09:00:00Z - RESUME
6. - Role: orchestrator
7. - Summary: Session resumed before selecting next story.
8. - Files changed/reviewed: prd.json, progress.txt
9. - Verification or outcome: No story dispatched yet.
10. - **Learnings for future iterations:**
11.   - Pick work from `prd_file`, not from memory.
12.   - `progress_file` is resume data only.
13.   - Story-specific code reading waits for implementer.
14. ---
15.
```

</details>


---

<sub>⏱️ 37s</sub>

### 💬 Copilot

## Source of truth
`evals/files/startup-fixture/prd.json` is the only official source for story status/completion.

## Resolved progress_file
`evals/files/startup-fixture/progress.txt` (resolved via `dirname(prd_file) + "/progress.txt"`). It exists, so startup uses its `## Codebase Patterns` and latest entries for resume context.

## Story selection
`story-auth-timeout` — **Auth timeout matches spec** (highest-priority story with `passes: false`, `priority: 1`).

## Before any story-specific repo discovery
No story-specific code/test/file discovery by orchestrator yet. First, orchestration is constrained to `prd_file`, resolved `progress_file`, and nearby `AGENTS.md` needed for dispatch; then model routing and fresh `implementer` dispatch (`./implementer-prompt.md` + full story properties + `progress_file` + nearby `AGENTS.md`, mode `initial_implementation`) must occur before any story-specific repo discovery.

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
