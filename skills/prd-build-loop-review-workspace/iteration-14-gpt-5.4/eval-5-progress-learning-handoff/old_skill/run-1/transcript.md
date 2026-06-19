# 🤖 Copilot CLI Session

> [!NOTE]
> - **Session ID:** `8ee1ed05-ad3b-4c59-b646-b4b2783999c9`  
> - **Started:** 6/18/2026, 10:37:27 PM  
> - **Duration:** 26s  
> - **Exported:** 6/18/2026, 10:37:54 PM  

---

<sub>⏱️ 0s</sub>

### ⚠️ Warning

Third-party MCP servers are disabled by your organization's Copilot policy. Only built-in servers are available.

---

<sub>⏱️ 1s</sub>

### 👤 User

Read and follow exact skill file at `/home/adam/dev/personal/skills/skills/prd-build-loop-review-workspace/skill-snapshot-pre-20260618-review-deps/SKILL.md`.
Ignore installed copies of `prd-build-loop-review` and any other skill with overlapping purpose; use only that file as benchmark instructions.

Benchmark constraints:
- Dry-run only.
- Do not spawn subagents.
- Do not create or modify repository files outside `/home/adam/dev/personal/skills/skills/prd-build-loop-review-workspace/iteration-14-gpt-5.4/eval-5-progress-learning-handoff/old_skill/run-1/outputs`.
- Read only what current prompt requires.
- Final answer must be only exact contents for `outputs/decision.md`, with no framing, explanation, or markdown fences.

Absolute input paths for this eval:
- /home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/progress-learning-fixture/prd.json
- /home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/progress-learning-fixture/progress.txt

Current working directory already contains `outputs/` for benchmark artifacts. Write requested file there.

Task:
Use skill under test in dry-run mode for `evals/files/progress-learning-fixture/`. User says: `Finish PRD finalization and record durable guidance from progress.` Do not change files or spawn real subagents. Read only what you need, then write `outputs/decision.md` describing what the orchestrator must pass to `self-improve`, which progress-file sections it must mine, and which kinds of reusable learnings it must preserve.


---

<sub>⏱️ 6s</sub>

### 💬 Copilot

Loading minimal context from benchmark skill and fixture inputs, then writing dry-run decision artifact.

---

<sub>⏱️ 7s</sub>

### ✅ `view`

**view the file at /home/adam/dev/personal/skills/skills/prd-build-loop-review-workspace/skill-snapshot-pre-20260618-review-deps/SKILL.md.**

/home/adam/dev/personal/skills/skills/prd-build-loop-review-workspace/skill-snapshot-pre-20260618-review-deps/SKILL.md

<details>
<summary>222 lines</summary>

````
1. ---
2. name: prd-build-loop-review
3. description: "Orchestrates dependency-aware PRD execution for `prd-to-tasks` output: resume from `progress_file`, execute each ready `parallelBatch` with fresh implementer subagents in safe parallel waves, then run one combined simplify/review/verify/record pass before exact `<promise>COMPLETE</promise>` or stop-state reply. Use whenever user wants to resume `prd.json` or `progress.txt`, run `/prd-build-loop`, finish remaining stories without pausing, or safely fan out PRD work across multiple implementers—even if they only say 'keep going' or 'finish rest of PRD'. Not for single-story implementation, PRD authoring, or task decomposition."
4. disable-model-invocation: true
5. ---
6. 
7. # PRD Build Loop Review
8. 
9. ## Overview
10. 
11. Finish current `prd-to-tasks` `prd.json` end to end. `prd_file` is official story status; `progress_file` is append-only resume data. Orchestrator never makes code-affecting changes or commits, and only returns for exact `<promise>COMPLETE</promise>` or a real **Stop Condition**.
12. 
13. ## When to Use
14. 
15. - Resume or finish autonomous work from `prd.json` plus `progress.txt`.
16. - Execute remaining `passes: false` `userStories` without pausing between them.
17. - Fan out ready stories in safe parallel waves.
18. - Run final simplify/review/verify/record pass after implementation.
19. - Not for single-story implementation, PRD authoring, or task decomposition.
20. 
21. ## Workflow
22. 
23. 1. **Startup**
24.    - Invoke `subagent-model-router`.
25.    - Resolve `progress_file` to explicit path or `dirname(prd_file) + "/progress.txt"`.
26.    - Validate `prd_file` shape before planning work: expect top-level `userStories` from `prd-to-tasks`; every unfinished story needs `id`, `title`, `priority`, `dependsOn`, `parallelBatch`, and `passes`. If file is legacy `stories` format or missing parallel fields, stop and ask user to regenerate or migrate it with `prd-to-tasks`.
27.    - If `progress_file` exists, read `## Codebase Patterns` plus latest relevant entries. Otherwise keep that sibling path reserved and create it there on first append with `## Codebase Patterns` at top.
28.    - If every story already has `passes: true`, reply exactly: `<promise>COMPLETE</promise>`.
29.    - If `prd_file` is ambiguous, contradictory, invalidly ordered, missing required detail, or needs human choice, stop and ask.
30.    - In dry-run or status outputs, use **Action shapes** below.
31. 
32. 2. **Implementation waves**
33.    - Build ready set from `userStories` where `passes: false` and every `dependsOn` story already has `passes: true`.
34.    - If no story is ready while unfinished stories remain, stop: dependency order, prerequisite state, or PRD content is invalid.
35.    - Take lowest ready `parallelBatch`; that batch is only active wave.
36.    - Before first `implementer` for current wave, read only `prd_file`, `progress_file`, and nearby `AGENTS.md` needed to dispatch work. State explicitly: `prd_file` is official source of truth; `progress_file` is supplemental resume data only.
37.    - Recheck safety inside current wave. Dispatch stories in parallel only when their `filesLikelyTouched` and owner surfaces are distinct. Treat exact file overlap, same migration, same endpoint, same shared state owner, same page/form/table owner, or missing file hints on multiple stories as conflict signals.
38.    - For each dispatched story, use fresh `implementer` with `./implementer-prompt.md`, all story properties, `progress_file`, `mode`, current wave summary, and sibling ownership boundaries.
39.    - If multiple stories are parallel-safe, launch one fresh `implementer` per story in parallel and wait for every current-wave result before moving on. Serialize overlap cases by priority within same wave and record why.
40.    - Require `Progress block`; append each returned block to `progress_file` before acting on it.
41.    - Apply **Status Rules** per story.
42.    - If story is implemented but not finalized, record that state and leave `passes: false`.
43.    - Do not start higher `parallelBatch` stories until current wave is resolved.
44.    - Repeat until every failing story is implemented and awaiting finalization, or a **Stop Condition** applies.
45. 
46. 3. **Single finalization pass**
47.    - Restore review-fix iteration count from `progress_file`; otherwise use `0`.
48.    - Run fresh `code-simplifier` on relevant non-ignored combined final state; append its `Progress block` immediately.
49.     - Run fresh `requirements-collector` for `prd_file`, relevant sibling docs, and available issue context; append its `Progress block`.
50.    - Run fresh `addy-code-reviewer`; append its `Progress block`.
51.    - If review finds issues and count is already `3`, state that limit is reached, do not fix directly, do not dispatch another review-fix `implementer`, record stop state, and ask.
52.    - Otherwise increment count in `progress_file`, dispatch fresh `implementer` with `mode: review_fix` and full findings, append its `Progress block`, apply **Status Rules**, then rerun simplify, requirements collection, and review on combined final state.
53. 
54. 4. **Verify and record**
55.    - Only after review is clean, run final-state checks required by story requirements, repo guidance, nearby `AGENTS.md`, and standard project scripts for changed areas; append orchestrator verification entry immediately.
56.    - Distill durable learnings from `progress_file`, then invoke `self-improve` with that distilled summary plus nearby `AGENTS.md` and linked docs. Pass reusable rules, not raw tracking structure.
57.    - Set `passes: true` only for stories that satisfy **Completion Gate**.
58.    - Append orchestrator final-state entry and reread `prd_file`.
59. 
60. 5. **Before any non-`<promise>COMPLETE</promise>` response**
61.    - Reread `prd_file`.
62.    - Confirm a **Stop Condition** applies.
63.    - Append latest orchestrator stop-state entry to `progress_file`.
64.    - Ask user to decide or unblock specific open issue.
65. 
66. ## Specific Techniques
67. 
68. ### Input contract and path rules
69. 
70. - `prd_file` is only official source for story completion and status.
71. - `progress_file` is append-only resume and tracking data; never treat it as official completion.
72. - Expected input is current `prd-to-tasks` output: top-level `userStories` plus per-story `dependsOn` and `parallelBatch`.
73. - Resolve default path in two steps: `(1)` resolve `prd_file`, `(2)` set `progress_file = dirname(resolved prd_file) + "/progress.txt"`.
74. - If sibling `progress.txt` does not exist yet, keep same path and create it on first append; missing file is never permission to invent another location.
75. - Resolve relative paths from repo or provided `prd_file`, never from session state, scratchpads, home directories, or `~/.copilot/...`.
76. - `priority` stays serial tie-breaker within same ready batch; readiness comes from `passes` plus `dependsOn`.
77. 
78. ### Safe parallel dispatch
79. 
80. - **Orchestrator:** selects ready wave, resumes from `progress_file`, dispatches subagents, applies status rules, verifies final state, updates `prd_file`, appends `progress_file`, invokes `self-improve`, and records stop/final state.
81. - **Implementer:** does story-specific discovery, code and test changes, and initial verification.
82. - **Requirements collector:** dedupes requirements before final review.
83. - **Code simplifier:** runs after all implementation and after every review-fix implementation.
84. - **Reviewer:** reviews combined final state after simplification.
85. - Any code-affecting change must be made by fresh `implementer`. Code-affecting includes code, tests, config, migrations, and implementation docs.
86. - Do not read story-specific repo files, tests, code, or behavior before first `implementer` for current wave.
87. - Pass each implementer explicit wave context: current story, sibling story IDs/titles, sibling `filesLikelyTouched`, and instruction to stay inside current story scope.
88. - If implementer discovers required change overlaps sibling-owned surface or unmet prerequisite work, it must return `NEEDS_CONTEXT` or `BLOCKED`; do not silently widen scope.
89. - Any new `implementer` change resets finalization: rerun simplify, review, and final verification on combined final state.
90. - Never simplify, review, analyze, or change `.gitignore`-ignored files; if ignore status is unclear, skip and report uncertainty.
91. 
92. ### Progress discipline
93. 
94. - Do not consume subagent output until recorded.
95. - Every `implementer`, `requirements-collector`, `code-simplifier`, and `reviewer` must return `Progress block`.
96. - Orchestrator appends each `Progress block` immediately, including `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, and `BLOCKED`.
97. - Missing subagent progress entry is rule violation; append corrective orchestrator entry if discovered.
98. - Maintain `## Codebase Patterns` at top and store only reusable general patterns there.
99. - Subagents never write `progress_file` directly.
100. 
101. Required entry format:
102. 
103. ```text
104. ## [Date/Time] - [Story ID or FINALIZATION]
105. - Role: implementer | requirements-collector | code-simplifier | reviewer | orchestrator
106. - Summary
107. - Files changed/reviewed
108. - Verification or outcome
109. - **Learnings for future iterations:**
110.   - Patterns discovered
111.   - Gotchas encountered
112.   - Useful context
113. ---
114. ```
115. 
116. ### Self-improve handoff
117. 
118. - Mine both `## Codebase Patterns` and detailed per-entry learnings in `progress_file`.
119. - Pass `self-improve` concise reusable rules only: validation/safety, cache/state/replay, UX/accessibility, testing/anti-flake, and environment/setup guidance.
120. - Preserve representative concrete rules when present; drop story IDs, timestamps, temporary blockers, and one-off filenames.
121. - Name destination in handoff: nearby `AGENTS.md` when prompt-worthy, linked docs when detail is too long for `AGENTS.md`.
122. 
123. ### Action shapes
124. 
125. Use these exact numbered lines verbatim in dry-run/status outputs:
126. 
127. - **Startup or resume before first implementer wave**
128.   1. Source of truth: `prd_file` official; `progress_file` supplemental resume data only.
129.   2. Resolved `progress_file`: explicit path or `dirname(prd_file) + "/progress.txt"`; if absent, create that sibling path on first append and never substitute session-state/home path.
130.   3. Active wave: lowest ready `parallelBatch` and ready story IDs.
131.   4. Dispatch fresh implementer per parallel-safe story; serialize overlap cases before any story-specific discovery.
132. - **After current-wave implementers return**
133.   1. Append every implementer `Progress block` before acting on it.
134.   2. Record per-story status; unresolved stories stay `passes: false`.
135.   3. Do not start higher `parallelBatch` work until current wave resolves.
136.   4. When all implementation waves are done, run `code-simplifier`, `requirements-collector`, then `addy-code-reviewer`.
137. - **After `mode: review_fix` implementer returns**
138.   1. Append implementer `Progress block` before acting on it.
139.   2. Rerun `code-simplifier` on combined final state.
140.   3. Rerun `requirements-collector`, then `addy-code-reviewer`.
141.   4. Keep `passes: true` blocked until review is clean and final checks pass.
142. - **When review-fix iteration limit is reached**
143.   1. State that review-fix iteration limit is reached.
144.   2. Do not fix directly.
145.   3. Do not dispatch another review-fix implementer.
146.   4. Reread `prd_file`.
147.   5. Append stop-state entry to `progress_file`.
148.   6. Human decision required: ask user to decide blocker.
149. 
150. ### Completion Gate
151. 
152. Mark story complete only if all are true:
153. 
154. 1. Required implementation was completed by fresh `implementer`.
155. 2. Latest code-affecting change touching that story or combined final state was made by fresh `implementer`.
156. 3. Fresh `code-simplifier` ran after latest code-affecting change.
157. 4. Fresh `addy-code-reviewer` ran after latest code-affecting change.
158. 5. If review found issues, fresh `implementer` fixed them and simplify/review reran after that fix.
159. 6. Review is clean for final state.
160. 7. Required final-state quality checks passed.
161. 
162. Never treat implementer `DONE`, confidence, passing checks alone, or `progress_file` entries as sufficient.
163. 
164. ### Status Rules
165. 
166. - **DONE:** continue.
167. - **DONE_WITH_CONCERNS:** incomplete unless every concern is explicitly confirmed non-blocking.
168. - **NEEDS_CONTEXT:** if human decision is required, stop and ask; otherwise provide context and redispatch fresh subagent.
169. - **BLOCKED:** try better context, smaller slice, or stronger model; if still blocked, stop and ask.
170. 
171. ### Stop Conditions
172. 
173. Stop only if:
174. 
175. - all stories in `prd_file` have `passes: true`
176. - real blocker remains after reasonable unblocking attempts
177. - `prd_file` has contradictions, invalid dependency ordering, or missing required details needing human correction
178. - no unfinished story is ready because prerequisite state is invalid or incomplete
179. - required human decision is needed
180. - review-fix iteration limit is reached
181. - final verification failed and needs human decision
182. 
183. ## Common Rationalizations
184. 
185. | Rationalization | Reality |
186. | --- | --- |
187. | "Same `parallelBatch` means I can dispatch everything blindly." | No. Recheck file/owner overlap; serialize ambiguous stories before dispatch. |
188. | "I can start later-batch work while one story from current wave is unresolved." | No. Resolve current wave first; later batches stay blocked. |
189. | "Legacy `stories` format is close enough." | No. This skill expects current `prd-to-tasks` output with `userStories`, `dependsOn`, and `parallelBatch`. |
190. | "Parallel implementer found sibling-owned file; widening scope is faster." | No. Return `NEEDS_CONTEXT` or `BLOCKED` instead of silently stealing sibling scope. |
191. | "Tests passed, so story can be marked complete." | No. **Completion Gate** still requires fresh simplifier, clean review, and final checks after latest change. |
192. 
193. ## Red Flags
194. 
195. - Returning control while any story still has `passes: false` and no **Stop Condition** applies.
196. - Treating `parallelBatch` as permission to ignore overlap or ownership checks.
197. - Resolving `progress_file` anywhere except explicit path or `dirname(prd_file) + "/progress.txt"`.
198. - Reading story-specific files, tests, code, or behavior before first `implementer` for current wave.
199. - Making code-affecting changes directly.
200. - Starting higher-batch work before current wave resolves.
201. - Fixing review findings without fresh `implementer`.
202. - Verifying before review is clean.
203. - Using anything except `prd_file` as official completion source.
204. - Marking `passes: true` before **Completion Gate** is satisfied.
205. - Running `self-improve` without first distilling durable learnings from `progress_file`.
206. 
207. ## Verification
208. 
209. Before stopping or marking completion, confirm:
210. 
211. - [ ] `prd_file` remained official source of story status and completion.
212. - [ ] `progress_file` path was resolved from explicit path or `dirname(prd_file) + "/progress.txt"`, even when sibling `progress.txt` did not exist yet.
213. - [ ] Ready work was selected from `userStories` using `passes`, `dependsOn`, and lowest ready `parallelBatch`.
214. - [ ] Parallel dispatch was limited to non-overlapping stories; ambiguous overlaps were serialized or escalated.
215. - [ ] Every code-affecting change came from fresh `implementer`.
216. - [ ] Every subagent `Progress block` was appended before being consumed.
217. - [ ] Simplify and review ran on combined final state after latest code-affecting change.
218. - [ ] Final checks ran only after clean review.
219. - [ ] Durable learnings were distilled from `progress_file` before invoking `self-improve`.
220. - [ ] `passes: true` was set only for stories that satisfied **Completion Gate**.
221. - [ ] Any non-`<promise>COMPLETE</promise>` response followed **Stop Conditions** and recorded stop state first.
222.
````

</details>


---

<sub>⏱️ 7s</sub>

### ✅ `view`

**view the file at /home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/progress-learning-fixture/prd.json.**

/home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/progress-learning-fixture/prd.json

<details>
<summary>28 lines</summary>

```
1. {
2.   "project": "Local Auth Return URL Hardening",
3.   "branchName": "local-auth-return-url-hardening",
4.   "description": "Capture durable guidance after combined auth hardening work.",
5.   "userStories": [
6.     {
7.       "id": "US-001",
8.       "title": "Local auth return-url hardening stays safe across login, validation, and startup paths",
9.       "description": "As a user, I want return URL handling to stay safe across auth paths so redirects remain valid and predictable.",
10.       "acceptanceCriteria": [
11.         "Return URL handling is hardened across login, validation, and startup routes",
12.         "Existing UX stays intact",
13.         "Typecheck passes"
14.       ],
15.       "filesLikelyTouched": [
16.         "src/auth/local_login_options.ts",
17.         "tests/auth/local_login_options.test.ts"
18.       ],
19.       "designGuidance": [],
20.       "priority": 1,
21.       "dependsOn": [],
22.       "parallelBatch": 1,
23.       "passes": false,
24.       "notes": ""
25.     }
26.   ]
27. }
28.
```

</details>


---

<sub>⏱️ 7s</sub>

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
5. ## 2026-06-12T10:00:00Z - US-001
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
19. ## 2026-06-12T10:40:00Z - US-001
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
33. ## 2026-06-12T11:10:00Z - US-001
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
47. ## 2026-06-12T11:45:00Z - US-001
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

<sub>⏱️ 16s</sub>

### ✅ `glob`

**outputs/decision.md**

"outputs/decision.md"

```
No files matched the pattern.
```


---

<sub>⏱️ 21s</sub>

### ✅ `apply_patch`

<details>
<summary>Arguments</summary>

```json
"*** Begin Patch\n*** Add File: /home/adam/dev/personal/skills/skills/prd-build-loop-review-workspace/iteration-14-gpt-5.4/eval-5-progress-learning-handoff/old_skill/run-1/outputs/decision.md\n+# Decision\n+\n+Orchestrator must pass `self-improve` a distilled reusable-guidance summary from `progress.txt`, plus nearby auth-focused `AGENTS.md` and linked docs as destination context. Payload should preserve representative concrete rules, but strip story IDs, timestamps, temporary status text, and one-off filenames/blockers. Because progress says auth guidance should live in scoped auth docs instead of root notes, handoff should direct `self-improve` to auth-local guidance rather than broad root guidance when detail is auth-specific.\n+\n+Mine these `progress.txt` sections:\n+1. `## Codebase Patterns`\n+2. Every entry's `**Learnings for future iterations:**` subsections:\n+   - `Patterns discovered`\n+   - `Gotchas encountered`\n+   - `Useful context`\n+3. Especially the `FINALIZATION` reviewer entry, since it states which reusable rule families still need durable capture.\n+\n+Preserve these reusable learnings:\n+- **Validation/safety:** evaluate prefix safety on decoded forms, not only raw strings; reuse shared return-url policy coverage across login/guard/startup paths; preserve single-rule targeting to avoid false negatives; avoid placeholder defaults that trigger unrelated validation failures.\n+- **Cache/state/replay:** keep cached stream for reads and use fresh-fetch command path for mutations; treat `shareReplay(1)` stale-first behavior as replay-regression risk on success flows.\n+- **UX/accessibility:** preserve existing focus and error behavior when extending auth helpers; compose `aria-describedby` in stable order with helper text first and contextual errors after.\n+- **Testing/anti-flake:** keep Jasmine `it` blocks at describe root; prefer filtered/targeted auth tests for focused coverage; use time-claim ranges instead of exact instants; keep existing failed-login coverage unchanged while extending success-path behavior.\n+- **Environment/setup:** dev route prefix matters for browser checks; direct browser `/login` may miss intended dev route; startup production-route checks may require staged dist artifact.\n+- **Guidance placement/ownership:** keep auth/login guidance in one scoped auth location; do not record only one obvious note when multiple reusable auth, validation, accessibility, and startup-test rules were discovered.\n*** End Patch\n"
```

</details>

```
Added 1 file(s): /home/adam/dev/personal/skills/skills/prd-build-loop-review-workspace/iteration-14-gpt-5.4/eval-5-progress-learning-handoff/old_skill/run-1/outputs/decision.md
```


---

<sub>⏱️ 23s</sub>

### ✅ `view`

**view the file at /home/adam/dev/personal/skills/skills/prd-build-loop-review-workspace/iteration-14-gpt-5.4/eval-5-progress-learning-handoff/old_skill/run-1/outputs/decision.md.**

/home/adam/dev/personal/skills/skills/prd-build-loop-review-workspace/iteration-14-gpt-5.4/eval-5-progress-learning-handoff/old_skill/run-1/outputs/decision.md

<details>
<summary>20 lines</summary>

```
1. # Decision
2. 
3. Orchestrator must pass `self-improve` a distilled reusable-guidance summary from `progress.txt`, plus nearby auth-focused `AGENTS.md` and linked docs as destination context. Payload should preserve representative concrete rules, but strip story IDs, timestamps, temporary status text, and one-off filenames/blockers. Because progress says auth guidance should live in scoped auth docs instead of root notes, handoff should direct `self-improve` to auth-local guidance rather than broad root guidance when detail is auth-specific.
4. 
5. Mine these `progress.txt` sections:
6. 1. `## Codebase Patterns`
7. 2. Every entry's `**Learnings for future iterations:**` subsections:
8.    - `Patterns discovered`
9.    - `Gotchas encountered`
10.    - `Useful context`
11. 3. Especially the `FINALIZATION` reviewer entry, since it states which reusable rule families still need durable capture.
12. 
13. Preserve these reusable learnings:
14. - **Validation/safety:** evaluate prefix safety on decoded forms, not only raw strings; reuse shared return-url policy coverage across login/guard/startup paths; preserve single-rule targeting to avoid false negatives; avoid placeholder defaults that trigger unrelated validation failures.
15. - **Cache/state/replay:** keep cached stream for reads and use fresh-fetch command path for mutations; treat `shareReplay(1)` stale-first behavior as replay-regression risk on success flows.
16. - **UX/accessibility:** preserve existing focus and error behavior when extending auth helpers; compose `aria-describedby` in stable order with helper text first and contextual errors after.
17. - **Testing/anti-flake:** keep Jasmine `it` blocks at describe root; prefer filtered/targeted auth tests for focused coverage; use time-claim ranges instead of exact instants; keep existing failed-login coverage unchanged while extending success-path behavior.
18. - **Environment/setup:** dev route prefix matters for browser checks; direct browser `/login` may miss intended dev route; startup production-route checks may require staged dist artifact.
19. - **Guidance placement/ownership:** keep auth/login guidance in one scoped auth location; do not record only one obvious note when multiple reusable auth, validation, accessibility, and startup-test rules were discovered.
20.
```

</details>


---

<sub>⏱️ 25s</sub>

### 💬 Copilot

# Decision

Orchestrator must pass `self-improve` a distilled reusable-guidance summary from `progress.txt`, plus nearby auth-focused `AGENTS.md` and linked docs as destination context. Payload should preserve representative concrete rules, but strip story IDs, timestamps, temporary status text, and one-off filenames/blockers. Because progress says auth guidance should live in scoped auth docs instead of root notes, handoff should direct `self-improve` to auth-local guidance rather than broad root guidance when detail is auth-specific.

Mine these `progress.txt` sections:
1. `## Codebase Patterns`
2. Every entry's `**Learnings for future iterations:**` subsections:
   - `Patterns discovered`
   - `Gotchas encountered`
   - `Useful context`
3. Especially the `FINALIZATION` reviewer entry, since it states which reusable rule families still need durable capture.

Preserve these reusable learnings:
- **Validation/safety:** evaluate prefix safety on decoded forms, not only raw strings; reuse shared return-url policy coverage across login/guard/startup paths; preserve single-rule targeting to avoid false negatives; avoid placeholder defaults that trigger unrelated validation failures.
- **Cache/state/replay:** keep cached stream for reads and use fresh-fetch command path for mutations; treat `shareReplay(1)` stale-first behavior as replay-regression risk on success flows.
- **UX/accessibility:** preserve existing focus and error behavior when extending auth helpers; compose `aria-describedby` in stable order with helper text first and contextual errors after.
- **Testing/anti-flake:** keep Jasmine `it` blocks at describe root; prefer filtered/targeted auth tests for focused coverage; use time-claim ranges instead of exact instants; keep existing failed-login coverage unchanged while extending success-path behavior.
- **Environment/setup:** dev route prefix matters for browser checks; direct browser `/login` may miss intended dev route; startup production-route checks may require staged dist artifact.
- **Guidance placement/ownership:** keep auth/login guidance in one scoped auth location; do not record only one obvious note when multiple reusable auth, validation, accessibility, and startup-test rules were discovered.

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
