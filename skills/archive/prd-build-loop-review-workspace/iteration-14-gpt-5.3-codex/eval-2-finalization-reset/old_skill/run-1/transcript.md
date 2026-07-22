# 🤖 Copilot CLI Session

> [!NOTE]
> - **Session ID:** `d87eb0d5-e31e-4196-8a87-d85b6c0402c3`  
> - **Started:** 6/18/2026, 10:48:26 PM  
> - **Duration:** 43s  
> - **Exported:** 6/18/2026, 10:49:10 PM  

---

<sub>⏱️ 0s</sub>

### ⚠️ Warning

Third-party MCP servers are disabled by your organization's Copilot policy. Only built-in servers are available.

---

<sub>⏱️ 2s</sub>

### 👤 User

Read and follow exact skill file at `/home/adam/dev/personal/skills/skills/prd-build-loop-review-workspace/skill-snapshot-pre-20260618-review-deps/SKILL.md`.
Ignore installed copies of `prd-build-loop-review` and any other skill with overlapping purpose; use only that file as benchmark instructions.

Benchmark constraints:
- Dry-run only.
- Do not spawn subagents.
- Do not create or modify repository files outside `/home/adam/dev/personal/skills/skills/prd-build-loop-review-workspace/iteration-14-gpt-5.3-codex/eval-2-finalization-reset/old_skill/run-1/outputs`.
- Read only what current prompt requires.
- Final answer must be only exact contents for `outputs/decision.md`, with no framing, explanation, or markdown fences.

Absolute input paths for this eval:
- /home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/finalization-reset-fixture/prd.json
- /home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/finalization-reset-fixture/progress.txt

Current working directory already contains `outputs/` for benchmark artifacts. Write requested file there.

Task:
Use skill under test in dry-run mode for `evals/files/finalization-reset-fixture/`. User says: `Continue PRD work from progress and finish final review loop.` Do not change files or spawn real subagents. Read only what you need, then write `outputs/decision.md` with next orchestrator actions after a fresh implementer returned from `mode: review_fix`, including which helpers may run in parallel and which review step must wait on them.


---

<sub>⏱️ 11s</sub>

### 💬 Copilot

Got it — I’ll load the exact benchmark skill file and the two fixture inputs, then produce `outputs/decision.md` only.

---

<sub>⏱️ 14s</sub>

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

<sub>⏱️ 14s</sub>

### ✅ `view`

**view the file at /home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/finalization-reset-fixture/prd.json.**

/home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/finalization-reset-fixture/prd.json

<details>
<summary>28 lines</summary>

```
1. {
2.   "project": "Billing Retry Guard",
3.   "branchName": "billing-retry-guard",
4.   "description": "Finish billing retry hardening after review-fix work.",
5.   "userStories": [
6.     {
7.       "id": "US-001",
8.       "title": "Billing retry covers duplicate charge edge case",
9.       "description": "As a billing operator, I want duplicate charge retries handled safely so users are not charged twice.",
10.       "acceptanceCriteria": [
11.         "Duplicate charge retries are guarded",
12.         "Tests cover duplicate charge retry path",
13.         "Typecheck passes"
14.       ],
15.       "filesLikelyTouched": [
16.         "src/billing_retry.py",
17.         "tests/test_billing_retry.py"
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

<sub>⏱️ 14s</sub>

### ✅ `view`

**view the file at /home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/finalization-reset-fixture/progress.txt.**

/home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/finalization-reset-fixture/progress.txt

<details>
<summary>44 lines</summary>

```
1. ## Codebase Patterns
2. - Review findings usually require new tests plus rerun of finalization.
3. 
4. ## 2026-06-10T11:00:00Z - US-001
5. - Role: implementer
6. - Summary: Implemented duplicate charge retry guard.
7. - Files changed/reviewed: src/billing_retry.py, tests/test_billing_retry.py
8. - Verification or outcome: Targeted retry tests passed.
9. - **Learnings for future iterations:**
10.   - Retry logic lives in src/billing_retry.py.
11.   - Negative tests matter for duplicate charges.
12.   - Finalization still pending.
13. ---
14. ## 2026-06-10T11:20:00Z - FINALIZATION
15. - Role: code-simplifier
16. - Summary: Simplified retry helper names.
17. - Files changed/reviewed: src/billing_retry.py
18. - Verification or outcome: No functional change claimed.
19. - **Learnings for future iterations:**
20.   - Small naming cleanups still count as final-state change.
21.   - Combined final state matters.
22.   - Review still required.
23. ---
24. ## 2026-06-10T11:35:00Z - FINALIZATION
25. - Role: reviewer
26. - Summary: Found missing negative test for duplicate charge after retry.
27. - Files changed/reviewed: src/billing_retry.py, tests/test_billing_retry.py
28. - Verification or outcome: Review fix required. review-fix iteration count = 1
29. - **Learnings for future iterations:**
30.   - Review is not clean.
31.   - Story cannot be marked complete yet.
32.   - Review fix must come from fresh implementer.
33. ---
34. ## 2026-06-10T11:50:00Z - US-001
35. - Role: implementer
36. - Summary: Returned from `mode: review_fix` after adding missing negative test.
37. - Files changed/reviewed: tests/test_billing_retry.py
38. - Verification or outcome: Status = DONE
39. - **Learnings for future iterations:**
40.   - Latest code-affecting change is review fix.
41.   - Finalization must rerun after this change.
42.   - `passes: true` still pending.
43. ---
44.
```

</details>


---

<sub>⏱️ 32s</sub>

### ✅ `view`

**view the file at /home/adam/dev/personal/skills/skills/prd-build-loop-review-workspace/iteration-14-gpt-5.3-codex/eval-2-finalization-reset/old_skill/run-1/outputs.**

/home/adam/dev/personal/skills/skills/prd-build-loop-review-workspace/iteration-14-gpt-5.3-codex/eval-2-finalization-reset/old_skill/run-1/outputs

<details>
<summary>6 lines</summary>

```diff

diff --git a/home/adam/dev/personal/skills/skills/prd-build-loop-review-workspace/iteration-14-gpt-5.3-codex/eval-2-finalization-reset/old_skill/run-1/outputs b/home/adam/dev/personal/skills/skills/prd-build-loop-review-workspace/iteration-14-gpt-5.3-codex/eval-2-finalization-reset/old_skill/run-1/outputs
create file mode 100644
index 0000000..0000000
--- a/dev/null
+++ b/home/adam/dev/personal/skills/skills/prd-build-loop-review-workspace/iteration-14-gpt-5.3-codex/eval-2-finalization-reset/old_skill/run-1/outputs
@@ -1,0 +1,0 @@
```

</details>


---

<sub>⏱️ 36s</sub>

### ✅ `apply_patch`

<details>
<summary>Arguments</summary>

```json
"*** Begin Patch\n*** Add File: outputs/decision.md\n+1. Append implementer `Progress block` before acting on it.\n+2. Rerun `code-simplifier` on combined final state.\n+3. Rerun `requirements-collector`, then `addy-code-reviewer`.\n+4. Keep `passes: true` blocked until review is clean and final checks pass.\n+5. Parallel helpers in this stage: none; do not run `code-simplifier` and `requirements-collector` concurrently.\n+6. Required wait point: `addy-code-reviewer` must wait until both reruns finish and their `Progress block`s are appended.\n*** End Patch\n"
```

</details>

```
Added 1 file(s): /home/adam/dev/personal/skills/skills/prd-build-loop-review-workspace/iteration-14-gpt-5.3-codex/eval-2-finalization-reset/old_skill/run-1/outputs/decision.md
```


---

<sub>⏱️ 39s</sub>

### ✅ `view`

**view the file at /home/adam/dev/personal/skills/skills/prd-build-loop-review-workspace/iteration-14-gpt-5.3-codex/eval-2-finalization-reset/old_skill/run-1/outputs/decision.md.**

/home/adam/dev/personal/skills/skills/prd-build-loop-review-workspace/iteration-14-gpt-5.3-codex/eval-2-finalization-reset/old_skill/run-1/outputs/decision.md

<details>
<summary>7 lines</summary>

```
1. 1. Append implementer `Progress block` before acting on it.
2. 2. Rerun `code-simplifier` on combined final state.
3. 3. Rerun `requirements-collector`, then `addy-code-reviewer`.
4. 4. Keep `passes: true` blocked until review is clean and final checks pass.
5. 5. Parallel helpers in this stage: none; do not run `code-simplifier` and `requirements-collector` concurrently.
6. 6. Required wait point: `addy-code-reviewer` must wait until both reruns finish and their `Progress block`s are appended.
7.
```

</details>


---

<sub>⏱️ 41s</sub>

### 💬 Copilot

1. Append implementer `Progress block` before acting on it.
2. Rerun `code-simplifier` on combined final state.
3. Rerun `requirements-collector`, then `addy-code-reviewer`.
4. Keep `passes: true` blocked until review is clean and final checks pass.
5. Parallel helpers in this stage: none; do not run `code-simplifier` and `requirements-collector` concurrently.
6. Required wait point: `addy-code-reviewer` must wait until both reruns finish and their `Progress block`s are appended.

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
