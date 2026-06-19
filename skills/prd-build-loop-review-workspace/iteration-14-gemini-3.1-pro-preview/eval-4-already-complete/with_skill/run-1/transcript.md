# 🤖 Copilot CLI Session

> [!NOTE]
> - **Session ID:** `57c65e79-fe8a-438a-a093-fa2749acda1b`  
> - **Started:** 6/18/2026, 11:00:48 PM  
> - **Duration:** 22s  
> - **Exported:** 6/18/2026, 11:01:10 PM  

---

<sub>⏱️ 0s</sub>

### ⚠️ Warning

Third-party MCP servers are disabled by your organization's Copilot policy. Only built-in servers are available.

---

<sub>⏱️ 1s</sub>

### 👤 User

Read and follow exact skill file at `/home/adam/dev/personal/skills/skills/prd-build-loop-review/SKILL.md`.
Ignore installed copies of `prd-build-loop-review` and any other skill with overlapping purpose; use only that file as benchmark instructions.

Benchmark constraints:
- Dry-run only.
- Do not spawn subagents.
- Do not create or modify repository files outside `/home/adam/dev/personal/skills/skills/prd-build-loop-review-workspace/iteration-14-gemini-3.1-pro-preview/eval-4-already-complete/with_skill/run-1/outputs`.
- Read only what current prompt requires.
- Final answer must be only exact contents for `outputs/decision.md`, with no framing, explanation, or markdown fences.

Absolute input paths for this eval:
- /home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/complete-fixture/prd.json
- /home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/complete-fixture/progress.txt

Current working directory already contains `outputs/` for benchmark artifacts. Write requested file there.

Task:
Use skill under test in dry-run mode for `evals/files/complete-fixture/`. User says: `Resume PRD build loop from progress.` Do not change files or spawn real subagents. If the skill says work is already complete, write exact final response to `outputs/decision.md` and nothing else.


---

<sub>⏱️ 8s</sub>

### 💬 Copilot

I_CAN_SEE_SESSIONSTART_CONTEXT

Read files. Evaluate skill condition.



---

<sub>⏱️ 9s</sub>

### ✅ `view`

**view the file at /home/adam/dev/personal/skills/skills/prd-build-loop-review/SKILL.md.**

/home/adam/dev/personal/skills/skills/prd-build-loop-review/SKILL.md

<details>
<summary>232 lines</summary>

````
1. ---
2. name: prd-build-loop-review
3. description: "Runs dependency-aware `prd-to-tasks` execution from `prd.json` plus `progress.txt`: resume current PRD, dispatch each ready `parallelBatch` in safe implementer waves, then run parallel simplification and requirements collection before dependent final review, verification, and exact `<promise>COMPLETE</promise>` or stop-state reply. Use whenever user wants `/prd-build-loop`, resume or finish remaining PRD stories, keep going from `prd.json`/`progress.txt`, or safely fan out multi-story implementation from `prd-to-tasks`—even if they only say 'keep going' or 'finish rest of PRD'. Not for single-story implementation, PRD authoring, or task decomposition."
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
18. - Run final simplify/requirements/review/verify/record pass after implementation.
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
48.    - Launch fresh `code-simplifier` on relevant non-ignored combined final state and fresh `requirements-collector` for `prd_file`, relevant sibling docs, and available issue context in parallel; append each `Progress block` immediately on return.
49.    - Run fresh `addy-code-reviewer` only after both parallel finalization helpers finish and both `Progress block`s are recorded; append its `Progress block`.
50.    - If review finds issues and count is already `3`, state that limit is reached, do not fix directly, do not dispatch another review-fix `implementer`, record stop state, and ask.
51.    - Otherwise increment count in `progress_file`, dispatch fresh `implementer` with `mode: review_fix` and full findings, append its `Progress block`, apply **Status Rules**, then rerun `code-simplifier` and `requirements-collector` in parallel before rerunning `addy-code-reviewer` on combined final state. Keep `passes: true` blocked until review is clean and final checks pass.
52. 
53. 4. **Verify and record**
54.    - Only after review is clean, run final-state checks required by story requirements, repo guidance, nearby `AGENTS.md`, and standard project scripts for changed areas; append orchestrator verification entry immediately.
55.    - Distill durable learnings from `progress_file`, then invoke `self-improve` with that distilled summary plus nearby `AGENTS.md` and linked docs. Pass reusable rules, not raw tracking structure.
56.    - Set `passes: true` only for stories that satisfy **Completion Gate**.
57.    - Append orchestrator final-state entry and reread `prd_file`.
58. 
59. 5. **Before any non-`<promise>COMPLETE</promise>` response**
60.    - Reread `prd_file`.
61.    - Confirm a **Stop Condition** applies.
62.    - Append latest orchestrator stop-state entry to `progress_file`.
63.    - Ask user to decide or unblock specific open issue.
64. 
65. ## Specific Techniques
66. 
67. ### Input contract and path rules
68. 
69. - `prd_file` is only official source for story completion and status.
70. - `progress_file` is append-only resume and tracking data; never treat it as official completion.
71. - Expected input is current `prd-to-tasks` output: top-level `userStories` plus per-story `dependsOn` and `parallelBatch`.
72. - Resolve default path in two steps: `(1)` resolve `prd_file`, `(2)` set `progress_file = dirname(resolved prd_file) + "/progress.txt"`.
73. - If sibling `progress.txt` does not exist yet, keep same path and create it on first append; missing file is never permission to invent another location.
74. - Resolve relative paths from repo or provided `prd_file`, never from session state, scratchpads, home directories, or `~/.copilot/...`.
75. - In dry-run/status explanations for missing sibling `progress.txt`, say all three points explicitly: exact sibling path, `if sibling progress.txt does not exist yet, create that sibling path on first append`, and forbidden fallback path families.
76. - `priority` stays serial tie-breaker within same ready batch; readiness comes from `passes` plus `dependsOn`.
77. 
78. ### Safe parallel dispatch
79. 
80. - **Orchestrator:** selects ready wave, resumes from `progress_file`, dispatches subagents, applies status rules, verifies final state, updates `prd_file`, appends `progress_file`, invokes `self-improve`, and records stop/final state.
81. - **Implementer:** does story-specific discovery, code and test changes, and initial verification.
82. - **Requirements collector:** dedupes requirements in parallel with simplification before final review.
83. - **Code simplifier:** runs after all implementation and after every review-fix implementation.
84. - **Reviewer:** waits for both helper outputs, then reviews combined final state.
85. - Any code-affecting change must be made by fresh `implementer`. Code-affecting includes code, tests, config, migrations, and implementation docs.
86. - Do not read story-specific repo files, tests, code, or behavior before first `implementer` for current wave.
87. - Pass each implementer explicit wave context: current story, sibling story IDs/titles, sibling `filesLikelyTouched`, and instruction to stay inside current story scope.
88. - If implementer discovers required change overlaps sibling-owned surface or unmet prerequisite work, it must return `NEEDS_CONTEXT` or `BLOCKED`; do not silently widen scope.
89. - In dry-run/status serialization plans, say overlap stories are serialized **instead of dispatching in parallel**, then name overlap reason and dispatch order.
90. - Any new `implementer` change resets finalization: rerun simplify, requirements collection, review, and final verification on combined final state.
91. - Never simplify, review, analyze, or change `.gitignore`-ignored files; if ignore status is unclear, skip and report uncertainty.
92. 
93. ### Progress discipline
94. 
95. - Do not consume subagent output until recorded.
96. - Every `implementer`, `requirements-collector`, `code-simplifier`, and `reviewer` must return `Progress block`.
97. - Orchestrator appends each `Progress block` immediately, including `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, and `BLOCKED`.
98. - Missing subagent progress entry is rule violation; append corrective orchestrator entry if discovered.
99. - Maintain `## Codebase Patterns` at top and store only reusable general patterns there.
100. - Subagents never write `progress_file` directly.
101. 
102. Required entry format:
103. 
104. ```text
105. ## [Date/Time] - [Story ID or FINALIZATION]
106. - Role: implementer | requirements-collector | code-simplifier | reviewer | orchestrator
107. - Summary
108. - Files changed/reviewed
109. - Verification or outcome
110. - **Learnings for future iterations:**
111.   - Patterns discovered
112.   - Gotchas encountered
113.   - Useful context
114. ---
115. ```
116. 
117. ### Self-improve handoff
118. 
119. - Mine both `## Codebase Patterns` and detailed per-entry learnings in `progress_file`.
120. - Pass `self-improve` concise reusable rules only: validation/safety, cache/state/replay, UX/accessibility, testing/anti-flake, and environment/setup guidance.
121. - In dry-run/status handoff output, use these exact bucket labels: `Validation/safety`, `Cache/state/replay`, `UX/accessibility`, `Testing/anti-flake`, `Environment/setup`.
122. - Preserve representative concrete rules when present; drop story IDs, timestamps, temporary blockers, and one-off filenames.
123. - State explicitly that only reusable guidance belongs in nearby `AGENTS.md` or linked docs; story-specific notes stay out.
124. 
125. ### Action shapes
126. 
127. Use these exact numbered lines verbatim in dry-run/status outputs:
128. 
129. - Choose exactly one matching block. Do not prepend startup lines to review-fix or finalization outputs.
130. 
131. - **Startup or resume before first implementer wave**
132.   1. Source of truth: `prd_file` official; `progress_file` supplemental resume data only.
133.   2. Resolved `progress_file`: explicit path or `dirname(prd_file) + "/progress.txt"`; if absent, create that sibling path on first append and never substitute session-state/home path.
134.   3. Active wave: lowest ready `parallelBatch` and ready story IDs.
135.   4. Dispatch one fresh implementer per parallel-safe story before any story-specific discovery; if stories overlap, serialize instead of dispatching them in parallel, cite the shared owner surface or exact file, give dispatch order, and do not start higher-batch work.
136. - **After current-wave implementers return**
137.   1. Append every implementer `Progress block` before acting on it.
138.   2. Record per-story status; unresolved stories stay `passes: false`.
139.   3. Do not start higher `parallelBatch` work until current wave resolves.
140.   4. When all implementation waves are done, run `code-simplifier` and `requirements-collector` in parallel, then `addy-code-reviewer`.
141. - **After `mode: review_fix` implementer returns**
142.   1. Append implementer `Progress block` before acting on it.
143.   2. Rerun `code-simplifier` and `requirements-collector` in parallel on combined final state.
144.   3. After both return, rerun `addy-code-reviewer`.
145.   4. Keep `passes: true` blocked until review is clean and final checks pass.
146. - **When review-fix iteration limit is reached**
147.   1. State that review-fix iteration limit is reached.
148.   2. Do not fix directly.
149.   3. Do not dispatch another review-fix implementer.
150.   4. Reread `prd_file`.
151.   5. Append stop-state entry to `progress_file`.
152.   6. Human decision required: ask user to decide blocker.
153. - **Before invoking `self-improve`**
154.   1. Mine `## Codebase Patterns` and every `Learnings for future iterations` block, including patterns, gotchas, and useful context.
155.   2. Pass only reusable guidance into nearby `AGENTS.md` or linked docs, not story-specific notes, raw tracking data, story IDs, timestamps, temporary blockers, or one-off filenames.
156.   3. Preserve durable rules under exact bucket labels: `Validation/safety`, `Cache/state/replay`, `UX/accessibility`, `Testing/anti-flake`, and `Environment/setup`.
157.   4. Preserve staged production-artifact startup-test guidance such as `wwwroot/dist/browser/index.html` when present.
158. 
159. ### Completion Gate
160. 
161. Mark story complete only if all are true:
162. 
163. 1. Required implementation was completed by fresh `implementer`.
164. 2. Latest code-affecting change touching that story or combined final state was made by fresh `implementer`.
165. 3. Fresh `code-simplifier` ran after latest code-affecting change.
166. 4. Fresh `requirements-collector` ran after latest code-affecting change and before final review.
167. 5. Fresh `addy-code-reviewer` ran after latest code-affecting change.
168. 6. If review found issues, fresh `implementer` fixed them and simplify/requirements/review reran after that fix.
169. 7. Review is clean for final state.
170. 8. Required final-state quality checks passed.
171. 
172. Never treat implementer `DONE`, confidence, passing checks alone, or `progress_file` entries as sufficient.
173. 
174. ### Status Rules
175. 
176. - **DONE:** continue.
177. - **DONE_WITH_CONCERNS:** incomplete unless every concern is explicitly confirmed non-blocking.
178. - **NEEDS_CONTEXT:** if human decision is required, stop and ask; otherwise provide context and redispatch fresh subagent.
179. - **BLOCKED:** try better context, smaller slice, or stronger model; if still blocked, stop and ask.
180. 
181. ### Stop Conditions
182. 
183. Stop only if:
184. 
185. - all stories in `prd_file` have `passes: true`
186. - real blocker remains after reasonable unblocking attempts
187. - `prd_file` has contradictions, invalid dependency ordering, or missing required details needing human correction
188. - no unfinished story is ready because prerequisite state is invalid or incomplete
189. - required human decision is needed
190. - review-fix iteration limit is reached
191. - final verification failed and needs human decision
192. 
193. ## Common Rationalizations
194. 
195. | Rationalization | Reality |
196. | --- | --- |
197. | "Same `parallelBatch` means I can dispatch everything blindly." | No. Recheck file/owner overlap; serialize ambiguous stories before dispatch. |
198. | "I can start later-batch work while one story from current wave is unresolved." | No. Resolve current wave first; later batches stay blocked. |
199. | "Legacy `stories` format is close enough." | No. This skill expects current `prd-to-tasks` output with `userStories`, `dependsOn`, and `parallelBatch`. |
200. | "Parallel implementer found sibling-owned file; widening scope is faster." | No. Return `NEEDS_CONTEXT` or `BLOCKED` instead of silently stealing sibling scope. |
201. | "Tests passed, so story can be marked complete." | No. **Completion Gate** still requires fresh simplifier, fresh requirements collection, clean review, and final checks after latest change. |
202. 
203. ## Red Flags
204. 
205. - Returning control while any story still has `passes: false` and no **Stop Condition** applies.
206. - Treating `parallelBatch` as permission to ignore overlap or ownership checks.
207. - Resolving `progress_file` anywhere except explicit path or `dirname(prd_file) + "/progress.txt"`.
208. - Reading story-specific files, tests, code, or behavior before first `implementer` for current wave.
209. - Making code-affecting changes directly.
210. - Starting higher-batch work before current wave resolves.
211. - Fixing review findings without fresh `implementer`.
212. - Verifying before review is clean.
213. - Using anything except `prd_file` as official completion source.
214. - Marking `passes: true` before **Completion Gate** is satisfied.
215. - Running `self-improve` without first distilling durable learnings from `progress_file`.
216. 
217. ## Verification
218. 
219. Before stopping or marking completion, confirm:
220. 
221. - [ ] `prd_file` remained official source of story status and completion.
222. - [ ] `progress_file` path was resolved from explicit path or `dirname(prd_file) + "/progress.txt"`, even when sibling `progress.txt` did not exist yet.
223. - [ ] Ready work was selected from `userStories` using `passes`, `dependsOn`, and lowest ready `parallelBatch`.
224. - [ ] Parallel dispatch was limited to non-overlapping stories; ambiguous overlaps were serialized or escalated.
225. - [ ] Every code-affecting change came from fresh `implementer`.
226. - [ ] Every subagent `Progress block` was appended before being consumed.
227. - [ ] `code-simplifier` and `requirements-collector` ran after latest code-affecting change, and `addy-code-reviewer` ran only after both returned.
228. - [ ] Final checks ran only after clean review.
229. - [ ] Durable learnings were distilled from `progress_file` before invoking `self-improve`.
230. - [ ] `passes: true` was set only for stories that satisfied **Completion Gate**.
231. - [ ] Any non-`<promise>COMPLETE</promise>` response followed **Stop Conditions** and recorded stop state first.
232.
````

</details>


---

<sub>⏱️ 9s</sub>

### ✅ `view`

**view the file at /home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/complete-fixture/prd.json.**

/home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/complete-fixture/prd.json

<details>
<summary>49 lines</summary>

```
1. {
2.   "project": "Auth Timeout Fanout",
3.   "branchName": "auth-timeout-fanout",
4.   "description": "All auth timeout stories already completed.",
5.   "userStories": [
6.     {
7.       "id": "US-001",
8.       "title": "Persist shared auth timeout policy",
9.       "description": "As a platform owner, I want one shared auth timeout policy so dependent flows use the same rules.",
10.       "acceptanceCriteria": [
11.         "Shared auth timeout policy exists in one reusable location",
12.         "Typecheck passes"
13.       ],
14.       "filesLikelyTouched": [
15.         "src/auth/timeout_policy.ts",
16.         "tests/auth/timeout_policy.test.ts"
17.       ],
18.       "designGuidance": [],
19.       "priority": 1,
20.       "dependsOn": [],
21.       "parallelBatch": 1,
22.       "passes": true,
23.       "notes": ""
24.     },
25.     {
26.       "id": "US-002",
27.       "title": "Show timeout status badge",
28.       "description": "As a user, I want a timeout status badge so I can see when auth policy is active.",
29.       "acceptanceCriteria": [
30.         "Status badge reflects timeout policy state",
31.         "Typecheck passes",
32.         "Verify in browser using playwright-cli skill"
33.       ],
34.       "filesLikelyTouched": [
35.         "src/ui/TimeoutStatusBadge.tsx",
36.         "tests/ui/TimeoutStatusBadge.test.tsx"
37.       ],
38.       "designGuidance": [],
39.       "priority": 2,
40.       "dependsOn": [
41.         "US-001"
42.       ],
43.       "parallelBatch": 2,
44.       "passes": true,
45.       "notes": ""
46.     }
47.   ]
48. }
49.
```

</details>


---

<sub>⏱️ 9s</sub>

### ✅ `view`

**view the file at /home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/complete-fixture/progress.txt.**

/home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/complete-fixture/progress.txt

<details>
<summary>14 lines</summary>

```
1. ## Codebase Patterns
2. - Completion comes from `prd_file`, not from progress notes.
3. 
4. ## 2026-06-10T12:30:00Z - FINALIZATION
5. - Role: orchestrator
6. - Summary: Final state recorded after clean review and verification.
7. - Files changed/reviewed: prd.json, progress.txt
8. - Verification or outcome: All stories already have `passes: true`.
9. - **Learnings for future iterations:**
10.   - Completion response must be exact.
11.   - No extra prose after completion.
12.   - Resume should short-circuit immediately.
13. ---
14.
```

</details>


---

<sub>⏱️ 15s</sub>

### ✅ `bash`

**Write final exact output**

$ cat << 'EOF' > /home/adam/dev/personal/skills/skills/prd-build-loop-review-workspace/iteration-14-gemini-3.1-pro-preview/eval-4-already-complete/with_skill/run-1/outputs/decision.md
<promise>COMPLETE</promise>
EOF

```

<shellId: 0 completed with exit code 0>
```


---

<sub>⏱️ 22s</sub>

### 💬 Copilot

\<promise\>COMPLETE\</promise\>

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
