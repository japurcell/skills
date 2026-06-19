# 🤖 Copilot CLI Session

> [!NOTE]
> - **Session ID:** `3bacc02b-b16b-432f-b83a-4238c3f6d681`  
> - **Started:** 6/18/2026, 4:50:57 PM  
> - **Duration:** 18s  
> - **Exported:** 6/18/2026, 4:51:16 PM  

---

<sub>⏱️ 0s</sub>

### ⚠️ Warning

Third-party MCP servers are disabled by your organization's Copilot policy. Only built-in servers are available.

---

<sub>⏱️ 1s</sub>

### 👤 User

Read and follow exact skill file at `/home/adam/dev/personal/skills/skills/prd-build-loop-review-workspace/skill-snapshot-pre-20260618-concise/SKILL.md`.
Ignore installed copies of `prd-build-loop-review` and any other skill with overlapping purpose; use only that file as benchmark instructions.

Benchmark constraints:
- Dry-run only.
- Do not spawn subagents.
- Do not create or modify repository files outside `/home/adam/dev/personal/skills/skills/prd-build-loop-review-workspace/iteration-9-gpt-5.4-mini/eval-4-progress-learning-handoff/old_skill/run-1/outputs`.
- Read only what current prompt requires.
- Final answer must be only exact contents for `outputs/decision.md`, with no framing, explanation, or markdown fences.

Absolute input paths for this eval:
- /home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/progress-learning-fixture/prd.json
- /home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/progress-learning-fixture/progress.txt

Current working directory already contains `outputs/` for benchmark artifacts. Write requested file there.

Task:
Use skill under test in dry-run mode for `evals/files/progress-learning-fixture/`. User says: `Finish PRD finalization and record durable guidance from progress.` Do not change files or spawn real subagents. Read only what you need, then write `outputs/decision.md` describing what the orchestrator must pass to `self-improve`, which progress-file sections it must mine, and which kinds of reusable learnings it must preserve.

---

<sub>⏱️ 8s</sub>

### ✅ `view`

**view the file at /home/adam/dev/personal/skills/skills/prd-build-loop-review-workspace/skill-snapshot-pre-20260618-concise/SKILL.md.**

/home/adam/dev/personal/skills/skills/prd-build-loop-review-workspace/skill-snapshot-pre-20260618-concise/SKILL.md

<details>
<summary>214 lines</summary>

````
1. ---
2. name: prd-build-loop-review
3. description: "Runs autonomous end-to-end PRD implementation from `prd_file`, resuming from `progress_file` and not handing control back until every remaining story is implemented, finalized, and recorded or a real stop condition applies. Use when the user says keep going until the PRD is done, resume from `progress.txt`, finish every `passes: false` story, or run the final simplify/review/verify/record loop without pausing."
4. ---
5. 
6. # PRD Build Loop Review
7. 
8. ## Overview
9. 
10. Drive every `passes: false` story in `prd_file` to completion. `prd_file` is official status; `progress_file` is append-only resume data. Orchestrator never makes code-affecting changes directly, never commits, and stops only for a real blocker or required human choice.
11. 
12. ## When to Use
13. 
14. - Implement all failing PRD stories from `prd_file`.
15. - Resume autonomous PRD work from `progress_file` or `progress.txt`.
16. - Keep going until the whole PRD is done instead of pausing after each story.
17. - Run the final combined simplify, review, verify, and record pass after implementation.
18. - Not for one-off story implementation, PRD authoring, or planning-only decomposition.
19. 
20. ## Workflow
21. 
22. 1. **Startup**
23.    - Invoke `subagent-model-router`.
24.    - Resolve `progress_file` to explicit path or `dirname(prd_file) + "/progress.txt"`.
25.    - If `progress_file` exists, read `## Codebase Patterns` plus the latest relevant entries. Otherwise create it on first append with `## Codebase Patterns` at top.
26.    - If every story already has `passes: true`, reply exactly: `<promise>COMPLETE</promise>`.
27.    - If `prd_file` is ambiguous, contradictory, invalidly ordered, missing required detail, or needs human choice, stop and ask.
28.    - In dry-run or status outputs, prefer the exact startup action shape in **Action shapes for weaker models** instead of paraphrasing.
29. 
30. 2. **Implementation loop**
31.    - Pick highest-priority story in `prd_file` with `passes: false`.
32.    - Before first `implementer` for current code-affecting unit, read only `prd_file`, `progress_file`, and nearby `AGENTS.md` needed to dispatch work.
33.    - State explicitly: `prd_file` is official source of truth; `progress_file` is supplemental resume data only.
34.    - Dispatch fresh `implementer` with `./implementer-prompt.md`, all story properties, `progress_file`, nearby `AGENTS.md`, and `mode`.
35.    - Require `Progress block`; append it to `progress_file` before interpreting or acting on it.
36.    - Apply **Status Rules** exactly.
37.    - If story is implemented but not finalized, record that state and leave `passes: false`.
38.    - Repeat until every failing story is implemented and awaiting finalization, or a **Stop Condition** applies.
39. 
40. 3. **Single finalization pass**
41.    - Restore review-fix iteration count from `progress_file`; otherwise use `0`.
42.    - Run fresh `code-simplifier` on relevant non-ignored changes in combined final state; append its `Progress block` immediately.
43.    - Run fresh `requirements-collector` for `prd_file`, relevant sibling docs, and available issue context; append its `Progress block`.
44.    - Run fresh `addy-code-reviewer` after simplification; append its `Progress block`.
45.    - If review finds issues and count is already `3`, state that the review-fix iteration limit is reached, do not fix directly, do not dispatch another review-fix implementer, record stop state, and ask.
46.    - Otherwise increment count in `progress_file`, dispatch fresh `implementer` with `mode: review_fix` and full findings, append its `Progress block`, apply **Status Rules**, then rerun simplify and review on the updated combined state.
47.    - In dry-run or status outputs, prefer the exact review-fix and iteration-limit action shapes in **Action shapes for weaker models** instead of paraphrasing.
48. 
49. 4. **Verify and record**
50.    - Only after review is clean, run required final-state checks from stories, repo guidance, nearby `AGENTS.md`, and standard project scripts for changed areas; append orchestrator verification entry immediately.
51.    - Distill durable learnings from `progress_file` first, then invoke `self-improve` with that distilled summary plus nearby `AGENTS.md` and linked docs. Pass reusable rules, not raw tracking structure.
52.    - Set `passes: true` only for stories that satisfy **Completion Gate**.
53.    - Append orchestrator final-state entry and reread `prd_file`.
54. 
55. 5. **Before any non-`<promise>COMPLETE</promise>` response**
56.    - Reread `prd_file`.
57.    - Confirm a **Stop Condition** applies.
58.    - Append latest orchestrator stop-state entry to `progress_file`.
59.    - Ask user to decide or unblock specific open issue.
60. 
61. ## Specific Techniques
62. 
63. ### Source of truth and paths
64. 
65. - `prd_file` is only official source for story completion and status.
66. - `progress_file` is append-only resume and tracking data; never treat it as official completion.
67. - Resolve relative paths from repo or provided `prd_file`, never from session state, scratchpads, home directories, or `~/.copilot/...`.
68. 
69. ### Role boundaries
70. 
71. - **Orchestrator:** selects stories, resumes from `progress_file`, dispatches subagents, applies status rules, verifies final state, updates `prd_file`, appends `progress_file`, invokes `self-improve`, and records stop/final state.
72. - **Implementer:** does story-specific discovery, code and test changes, and initial verification.
73. - **Requirements collector:** dedupes requirements before final review.
74. - **Code simplifier:** runs after all implementation and after every review-fix implementation.
75. - **Reviewer:** reviews combined final state after simplification.
76. - Any code-affecting change must be made by fresh `implementer`. Code-affecting includes code, tests, config, migrations, and implementation docs.
77. - Do not read story-specific repo files, tests, code, or behavior before first `implementer` for current code-affecting unit.
78. - Any new `implementer` change resets finalization: rerun simplify, review, and final verification on combined final state.
79. - Never simplify, review, analyze, or change `.gitignore`-ignored files; if ignore status is unclear, skip and report uncertainty.
80. 
81. ### Progress discipline
82. 
83. - Subagent output is not consumed until recorded.
84. - Every `implementer`, `requirements-collector`, `code-simplifier`, and `reviewer` must return `Progress block`.
85. - Orchestrator appends each `Progress block` immediately, including `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, and `BLOCKED`.
86. - Missing subagent progress entry is rule violation; append corrective orchestrator entry if discovered.
87. - Maintain `## Codebase Patterns` at top and store only reusable general patterns there.
88. - Subagents never write `progress_file` directly.
89. 
90. Required entry format:
91. 
92. ```text
93. ## [Date/Time] - [Story ID or FINALIZATION]
94. - Role: implementer | requirements-collector | code-simplifier | reviewer | orchestrator
95. - Summary
96. - Files changed/reviewed
97. - Verification or outcome
98. - **Learnings for future iterations:**
99.   - Patterns discovered
100.   - Gotchas encountered
101.   - Useful context
102. ---
103. ```
104. 
105. ### Self-improve handoff
106. 
107. - Before invoking `self-improve`, mine `progress_file` yourself. Read both high-level pattern sections and detailed per-entry learnings; durable guidance can hide in patterns, gotchas, or useful context.
108. - Pass `self-improve` a concise summary of reusable rules only: framework constraints, validation rules, stable fix shapes, UX-preservation rules, anti-flake testing tactics, environment/setup requirements, etc.
109. - Keep precise technical tokens from the source when they are part of the reusable rule: framework names, operators, API names, helper names, and artifact paths can stay; story IDs, timestamps, and temporary blockers should not.
110. - If the source artifact contains them, preserve at least one reusable rule for each present category: validation/safety, cache or replay behavior, UX/accessibility, testing or anti-flake tactics, and environment/setup requirements.
111. - Name the destination in the handoff: nearby `AGENTS.md` when the rule is prompt-worthy, linked docs when the detail is too long for `AGENTS.md`.
112. - Do not pass one-off filenames, temporary blockers, or story-only notes as standing guidance.
113. 
114. ### Action shapes for weaker models
115. 
116. - **Startup or resume before first implementer**
117.   1. Source of truth: `prd_file` official; `progress_file` supplemental resume data only.
118.   2. Resolved `progress_file`: explicit path or `dirname(prd_file) + "/progress.txt"`.
119.   3. Selected story: highest-priority `passes: false` story.
120.   4. Before story-specific discovery: dispatch fresh implementer; read only `prd_file`, `progress_file`, and nearby `AGENTS.md`.
121. - **After `mode: review_fix` implementer returns**
122.   1. Append implementer `Progress block` before acting on it.
123.   2. Rerun `code-simplifier` on combined final state.
124.   3. Rerun `requirements-collector`, then `addy-code-reviewer`.
125.   4. Keep `passes: true` blocked until review is clean and final checks pass.
126. - **When review-fix iteration limit is reached**
127.   1. State that the review-fix iteration limit is reached.
128.   2. Do not fix directly.
129.   3. Do not dispatch another review-fix implementer.
130.   4. Reread `prd_file`.
131.   5. Append stop-state entry to `progress_file`.
132.   6. Ask user to decide blocker.
133. - **Self-improve handoff summary**
134.   1. Destination: nearby `AGENTS.md` or linked docs.
135.   2. Reusable guidance only; no raw progress blocks, story-only notes, or transient blockers.
136.   3. Validation/safety: [reusable rules from source]
137.   4. Cache/state/replay: [reusable rules from source]
138.   5. UX/accessibility: [reusable rules from source]
139.   6. Testing/anti-flake: [reusable rules from source]
140.   7. Environment/setup: [reusable rules from source]
141. 
142. ### Completion Gate
143. 
144. Mark story complete only if all are true:
145. 
146. 1. Required implementation was completed by fresh `implementer`.
147. 2. Latest code-affecting change, including any review fix, was made by fresh `implementer`.
148. 3. Fresh `code-simplifier` ran after latest code-affecting change.
149. 4. Fresh `addy-code-reviewer` ran after latest code-affecting change.
150. 5. If review found issues, fresh `implementer` fixed them and simplify/review reran after that fix.
151. 6. Review is clean for final state.
152. 7. Required final-state quality checks passed.
153. 
154. Never treat implementer `DONE`, confidence, passing checks alone, or `progress_file` entries as sufficient.
155. 
156. ### Status Rules
157. 
158. - **DONE:** continue.
159. - **DONE_WITH_CONCERNS:** incomplete unless every concern is explicitly confirmed non-blocking.
160. - **NEEDS_CONTEXT:** if human decision is required, stop and ask; otherwise provide context and redispatch fresh subagent.
161. - **BLOCKED:** try better context, smaller slice, or stronger model; if still blocked, stop and ask.
162. 
163. ### Stop Conditions
164. 
165. Stop only if:
166. 
167. - all stories in `prd_file` have `passes: true`
168. - real blocker remains after reasonable unblocking attempts
169. - `prd_file` has contradictions, invalid ordering, or missing required details needing human correction
170. - required human decision is needed
171. - review-fix iteration limit is reached
172. - final verification failed and needs human decision
173. 
174. ## Common Rationalizations
175. 
176. | Rationalization                                                                  | Reality                                                                                                           |
177. | -------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
178. | "I already know repo; I can inspect story files before dispatching implementer." | No. Before first `implementer`, read only `prd_file`, `progress_file`, and nearby `AGENTS.md` needed to dispatch. |
179. | "Review fix is tiny; I can patch it directly."                                   | No. Any code-affecting change requires fresh `implementer`, then simplify/review/verify must rerun.               |
180. | "Tests passed, so story can be marked complete."                                 | No. Completion gate also requires fresh simplifier and reviewer after latest code change.                         |
181. | "Progress file says done, so PRD can be updated."                                | No. `prd_file` is only official completion source.                                                                |
182. | "Reviewer already ran earlier; rerunning is wasteful."                           | Any new `implementer` change resets finalization on combined final state.                                         |
183. | "One obvious note is enough; I can ignore the rest of the progress learnings."   | No. Final `self-improve` handoff must cover all durable learnings, not just the most visible one.                 |
184. 
185. ## Red Flags
186. 
187. - Returning control while any story still has `passes: false` and no **Stop Condition** applies.
188. - Resolving `progress_file` anywhere except explicit path or `dirname(prd_file) + "/progress.txt"`.
189. - Using session-state, scratchpad, home, or `~/.copilot/...` paths for `progress_file`.
190. - Treating subagent output as consumed before appending its `Progress block`.
191. - Reading story-specific files, tests, code, or behavior before first `implementer`.
192. - Making code-affecting changes directly.
193. - Skipping simplify or review.
194. - Fixing review findings without fresh `implementer`.
195. - Verifying before review is clean.
196. - Using anything except `prd_file` as official completion source.
197. - Marking `passes: true` before **Completion Gate** is satisfied.
198. - Simplifying, reviewing, analyzing, or changing `.gitignore`-ignored files.
199. - Running `self-improve` without first distilling durable learnings from `progress_file` into a reusable summary.
200. 
201. ## Verification
202. 
203. Before stopping or marking completion, confirm:
204. 
205. - [ ] `prd_file` remained official source of story status and completion.
206. - [ ] `progress_file` path was resolved from explicit path or `dirname(prd_file) + "/progress.txt"`.
207. - [ ] Every code-affecting change came from fresh `implementer`.
208. - [ ] Every subagent `Progress block` was appended before being consumed.
209. - [ ] Simplify and review ran on combined final state after latest code-affecting change.
210. - [ ] Final checks ran only after clean review.
211. - [ ] Durable learnings were distilled from `progress_file` before invoking `self-improve`.
212. - [ ] `passes: true` was set only for stories that satisfied **Completion Gate**.
213. - [ ] Any non-`<promise>COMPLETE</promise>` response followed **Stop Conditions** and recorded stop state first.
214.
````

</details>


---

<sub>⏱️ 8s</sub>

### ✅ `view`

**view the file at /home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/progress-learning-fixture/prd.json.**

/home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/progress-learning-fixture/prd.json

<details>
<summary>15 lines</summary>

```
1. {
2.   "stories": [
3.     {
4.       "id": "story-local-auth-returnurl",
5.       "title": "Local auth return-url hardening stays safe across login, validation, and startup paths",
6.       "priority": 1,
7.       "passes": false,
8.       "requirements": [
9.         "Harden local-auth return URL handling across login, validation, and startup routes",
10.         "Preserve existing UX and add stable regression coverage"
11.       ]
12.     }
13.   ]
14. }
15.
```

</details>


---

<sub>⏱️ 8s</sub>

### ✅ `view`

**view the file at /home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/progress-learning-fixture/progress.txt.**

/home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/progress-learning-fixture/progress.txt

<details>
<summary>74 lines</summary>

```
1. ## Codebase Patterns
2. - Keep auth/login guidance in one scoped location instead of scattering it across root notes.
3. - Preserve existing focus and error behavior when extending auth helpers.
4. 
5. ## 2026-06-12T10:00:00Z - story-local-auth-returnurl
6. - Role: implementer
7. - Summary: Hardened decoded prefix validation and login return-url policy reuse.
8. - Files changed/reviewed: Auth tests, login helpers, shared return-url policy
9. - Verification or outcome: Targeted auth tests passed.
10. - **Learnings for future iterations:**
11.   - Patterns discovered
12.     - Prefix safety must evaluate decoded forms, not only raw string.
13.     - Existing guard/login paths should reuse shared return-url policy coverage.
14.   - Gotchas encountered
15.     - Jasmine forbids nested `it`; keep test blocks at describe root.
16.   - Useful context
17.     - Filtered auth tests keep validation coverage fast and focused.
18. ---
19. ## 2026-06-12T10:40:00Z - story-local-auth-returnurl
20. - Role: implementer
21. - Summary: Stabilized login success flow after cache/replay regression.
22. - Files changed/reviewed: Login state stream, command path, UI tests
23. - Verification or outcome: Success-path UI regression tests passed.
24. - **Learnings for future iterations:**
25.   - Patterns discovered
26.     - Keep cached stream for reads; use fresh-fetch command path for mutations to avoid replay bugs.
27.     - Fresh-fetch command path plus cached read stream split is stable fix shape for replay bugs.
28.   - Gotchas encountered
29.     - `shareReplay(1)` stale-first behavior can cause false UI failure on success flows.
30.   - Useful context
31.     - Existing failed-login behavior already had coverage and should stay unchanged.
32. ---
33. ## 2026-06-12T11:10:00Z - story-local-auth-returnurl
34. - Role: implementer
35. - Summary: Extended helper text association without regressing error handling.
36. - Files changed/reviewed: Login field helper text, accessibility tests
37. - Verification or outcome: Accessibility checks passed.
38. - **Learnings for future iterations:**
39.   - Patterns discovered
40.     - Compose `aria-describedby` in stable order: helper first, then contextual errors.
41.     - Preserve existing error/focus UX while extending helper association through composed `aria-describedby`.
42.   - Gotchas encountered
43.     - Dev route prefix matters for browser checks.
44.   - Useful context
45.     - Browser direct `/login` may not hit the right dev route.
46. ---
47. ## 2026-06-12T11:45:00Z - story-local-auth-returnurl
48. - Role: implementer
49. - Summary: Tightened validation and startup-route coverage.
50. - Files changed/reviewed: Local login option tests, startup production-route tests
51. - Verification or outcome: Validation and startup-route checks passed.
52. - **Learnings for future iterations:**
53.   - Patterns discovered
54.     - Time-based claim assertions should use ranges to avoid flake.
55.     - Preserve single-rule targeting to avoid false negatives from unrelated validators.
56.   - Gotchas encountered
57.     - Avoid placeholder defaults to prevent unrelated validation failures.
58.   - Useful context
59.     - Startup production-route tests may need staged dist artifact to hit intended branch: `wwwroot/dist/browser/index.html`.
60. ---
61. ## 2026-06-12T12:00:00Z - FINALIZATION
62. - Role: reviewer
63. - Summary: Combined final state is clean; durable guidance capture still pending.
64. - Files changed/reviewed: auth docs, auth tests, startup route coverage
65. - Verification or outcome: Clean review. Final recording step still required.
66. - **Learnings for future iterations:**
67.   - Patterns discovered
68.     - Final recording should capture reusable auth, validation, accessibility, and startup-test rules.
69.   - Gotchas encountered
70.     - Recording only one obvious note leaves future agents under-instructed.
71.   - Useful context
72.     - Nearby auth docs should own these rules instead of bloating root guidance.
73. ---
74.
```

</details>


---

<sub>⏱️ 14s</sub>

### ✅ `apply_patch`

<details>
<summary>Arguments</summary>

```json
"*** Begin Patch\n*** Add File: /home/adam/dev/personal/skills/skills/prd-build-loop-review-workspace/iteration-9-gpt-5.4-mini/eval-4-progress-learning-handoff/old_skill/run-1/outputs/decision.md\n+Orchestrator must mine `progress_file` first, then call `self-improve` with a concise reusable-summary package: distilled rules only, plus nearby `AGENTS.md` and any linked docs when the rule is too long for `AGENTS.md`.\n+\n+Mine these progress sections:\n+- `## Codebase Patterns`\n+- every entry's `**Learnings for future iterations:**`\n+  - `Patterns discovered`\n+  - `Gotchas encountered`\n+  - `Useful context`\n+- the FINALIZATION entry, since it often records the last durable guidance\n+\n+Preserve reusable learnings of these kinds:\n+- validation/safety rules\n+- cache/replay behavior rules\n+- UX/accessibility preservation rules\n+- testing and anti-flake tactics\n+- environment/setup requirements\n+\n+Keep stable technical tokens that are part of the rule itself, like framework names, operators, API names, helper names, and artifact paths. Drop story IDs, timestamps, temporary blockers, and one-off filenames or notes.\n*** End Patch\n"
```

</details>

```
Added 1 file(s): /home/adam/dev/personal/skills/skills/prd-build-loop-review-workspace/iteration-9-gpt-5.4-mini/eval-4-progress-learning-handoff/old_skill/run-1/outputs/decision.md
```


---

<sub>⏱️ 15s</sub>

### ✅ `view`

**view the file at /home/adam/dev/personal/skills/skills/prd-build-loop-review-workspace/iteration-9-gpt-5.4-mini/eval-4-progress-learning-handoff/old_skill/run-1/outputs/decision.md.**

/home/adam/dev/personal/skills/skills/prd-build-loop-review-workspace/iteration-9-gpt-5.4-mini/eval-4-progress-learning-handoff/old_skill/run-1/outputs/decision.md

<details>
<summary>19 lines</summary>

```
1. Orchestrator must mine `progress_file` first, then call `self-improve` with a concise reusable-summary package: distilled rules only, plus nearby `AGENTS.md` and any linked docs when the rule is too long for `AGENTS.md`.
2. 
3. Mine these progress sections:
4. - `## Codebase Patterns`
5. - every entry's `**Learnings for future iterations:**`
6.   - `Patterns discovered`
7.   - `Gotchas encountered`
8.   - `Useful context`
9. - the FINALIZATION entry, since it often records the last durable guidance
10. 
11. Preserve reusable learnings of these kinds:
12. - validation/safety rules
13. - cache/replay behavior rules
14. - UX/accessibility preservation rules
15. - testing and anti-flake tactics
16. - environment/setup requirements
17. 
18. Keep stable technical tokens that are part of the rule itself, like framework names, operators, API names, helper names, and artifact paths. Drop story IDs, timestamps, temporary blockers, and one-off filenames or notes.
19.
```

</details>


---

<sub>⏱️ 17s</sub>

### 💬 Copilot

Orchestrator must mine `progress_file` first, then call `self-improve` with a concise reusable-summary package: distilled rules only, plus nearby `AGENTS.md` and any linked docs when the rule is too long for `AGENTS.md`.

Mine these progress sections:
- `## Codebase Patterns`
- every entry's `**Learnings for future iterations:**`
  - `Patterns discovered`
  - `Gotchas encountered`
  - `Useful context`
- the FINALIZATION entry, since it often records the last durable guidance

Preserve reusable learnings of these kinds:
- validation/safety rules
- cache/replay behavior rules
- UX/accessibility preservation rules
- testing and anti-flake tactics
- environment/setup requirements

Keep stable technical tokens that are part of the rule itself, like framework names, operators, API names, helper names, and artifact paths. Drop story IDs, timestamps, temporary blockers, and one-off filenames or notes.

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
