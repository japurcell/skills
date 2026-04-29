# 🤖 Copilot CLI Session

> [!NOTE]
> - **Session ID:** `b1f1959e-a187-4b47-b9dc-dbd1a5dce0ed`  
> - **Started:** 4/28/2026, 7:13:19 PM  
> - **Duration:** 23s  
> - **Exported:** 4/28/2026, 7:13:43 PM  

---

<sub>⏱️ 1s</sub>

### 👤 User

Read and follow only this skill file as the authoritative instructions for responding to the hypothetical scenario below. Ignore any other installed skill with the same name unless it matches this exact path. 
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md

Return only the controller's user-facing response for the scenario. Do not ask questions.

Scenario:
You are executing /prd-implement for PRD #5000. Ready wave W3 contains only AFK child issue #5104, "Add admin settings form." The parent PRD issue still shows `- [ ] W3 - #5104 Add admin settings form - AFK - blocked by #5103`. The implementation subagent returns a clean RED -\> GREEN -\> REFACTOR summary, changed files, and these command results: `npm test -- settings-form.test.tsx` passed, `pnpm exec next typegen` could not run because `next` is unavailable in this checkout, so the subagent skipped it and instead read the generated types file plus ran `pnpm exec eslint app/settings/form.tsx`. Show how the controller handles the checkpoint before review.


---

<sub>⏱️ 6s</sub>

### ✅ `view`

**view the file at /home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md.**

/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md

```
File too large to read at once (24.6 KB). Consider using the grep tool to search within the file, or view with view_range to read specific sections.
```


---

<sub>⏱️ 8s</sub>

### 💬 Copilot

Let me get the structure first and search for checkpoint handling sections:

---

<sub>⏱️ 9s</sub>

### ✅ `bash`

**Get file size and start reading**

$ wc -l /home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md && head -100 /home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md

<details>
<summary>75 lines</summary>

````
366 /home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md
---
name: prd-implement
description: Execute a PRD GitHub issue that already has a task graph from `prd-to-tasks`. Use this whenever the user wants to implement, resume, or finish work from a PRD/tracker issue with child implementation issues and execution waves — for example "implement PRD #123", "work through the task graph under issue 123", "resume the AFK slices for #123", or "build the next ready task from the PRD issue". This skill reads the parent issue's managed `Task graph` block, explicitly loads the `gh-cli` skill for issue reads and child-issue writes, executes AFK child issues in dependency order, requires `tdd` subagents for implementation, and treats completion as real GitHub state changes: the child issue must actually be closed. Comments alone never count as completion. Parent task-graph checkboxes may lag behind and do not block completion. It stops before git landing work: never commit, push, or open a PR from inside this skill; use `commit` or `commit-to-pr` separately afterward. Do not use it to create or redesign the task graph; use `prd-to-tasks` first.
---

# PRD Implement

Use this skill to turn a PRD issue graph into implemented code without letting the controller context balloon.

The controller owns intake, graph parsing, wave scheduling, and issue updates. It does **not** implement tasks inline. Every implementation task runs in a subagent that loads the `tdd` skill first and `gh-cli` before any GitHub reads or writes. Every review step also runs in subagents. Completed work is not fully recorded until the child issue is closed on GitHub. A completion comment, `Stage: refactor` note, or "ready to close" summary is never a substitute for that real GitHub state change. Parent `Task graph` checkbox drift does not block completion.

## Inputs

- `prd_issue` is required. Accept an issue number or issue URL.
- If the repository is ambiguous, resolve it before doing anything else.

If `prd_issue` is missing, ask for it. If the issue does not contain a `prd-to-tasks` task graph, stop and tell the user to run `prd-to-tasks` first.

## Non-negotiable rules

1. Treat the PRD issue's managed `Task graph` block as the source of truth for wave order and intended child issues.
2. Treat each child issue body as the source of truth for that task's scope, acceptance criteria, verification steps, likely files, and HITL/AFK type.
3. Do not invent new tasks, waves, or dependencies during implementation. If the graph is wrong, stop and tell the user what must be fixed in GitHub first.
4. Only execute **AFK** issues. **HITL** issues pause the workflow until the named decision, review, approval, or access step happens.
5. Never skip a lower-numbered wave to start a later wave early.
6. The controller schedules waves; implementation happens only in subagents.
7. Every implementation subagent must load the `tdd` skill first, then explicitly load `gh-cli` before any GitHub issue reads or writes, and follow a strict RED → GREEN → REFACTOR loop.
8. Review always happens in subagents after each completed wave. Keep review scope to the files changed in that wave.
9. Treat completion as a GitHub closeout: close the child issue. A task is not done until GitHub shows that issue closed. Leave the parent PRD issue open.
10. Treat comments as evidence only, never as completion. A child issue with only a status comment is still open work until GitHub shows the issue closed.
11. This skill never commits, pushes, rebases, merges, or opens PRs. Landing work always happens in a separate request after PRD execution stops.

## Git and PR boundary

Treat landing work as a separate workflow. `prd-implement` ends at verified local changes plus GitHub child-issue closeout, not at branch landing.

1. Never run `git commit`, `git push`, `git merge`, `git rebase`, `gh pr create`, or invoke `commit` / `commit-to-pr` from this skill.
2. Never ask implementation, review, or verification subagents to prepare commits, push branches, draft PRs, or land code. They may inspect diffs and local state, but they must leave changes uncommitted and unpushed.
3. If the user asks for "implement PRD #123 and open a PR" in one request, execute only the PRD implementation workflow. In the final response, say that landing work remains out of scope for this run and requires a separate `commit` or `commit-to-pr` request after this skill finishes.
4. If any subagent reports that it already committed, pushed, rebased, merged, or opened a PR, stop immediately and surface that as a workflow violation before review, verification, or issue closure continues. In that response, also say the child issue remains open.
5. Some weaker models equate "verified" with "ready to land." Counter that drift by restating the boundary in the controller plan whenever the user mentions commits, pushes, branches, or PRs: `Landing work remains out of scope for this run.`

## Fetch and parse the graph

1. Use the `gh-cli` skill to fetch the parent issue with comments. Some weaker models do not auto-load that skill, so call it explicitly before issue retrieval.
2. Parse the managed block written by `prd-to-tasks`:

```markdown
<!-- prd-to-tasks:start -->

## Task graph

- [ ] W1 - #123 Slice title - AFK - blocked by none
- [ ] W2 - #124 Another slice - HITL - blocked by #123
<!-- prd-to-tasks:end -->
```

3. If the managed markers are missing, fall back to a plain `## Task graph` section only when it clearly uses the same line format.
4. Parse each task-graph line with anchored fields, not naive string splitting:
   - checkbox: the leading `[ ]` or `[x]`
   - wave: leading `W<n>`
   - child issue: the first `#<number>` after the wave
   - type: the final `- AFK -` or `- HITL -` segment
   - blockers: the text after the final `blocked by `
   - title: everything between `#<number> ` and the final ` - AFK/HITL - blocked by ...`
5. For every referenced child issue:
    - fetch its title, body, state, and recent comments
    - extract `Type`, `Acceptance criteria`, `Verification`, and `Files likely touched`
    - prefer the child issue state over the parent checkbox if they disagree
    - treat parent checkbox drift as informational only unless it creates ambiguity about which child issue the line refers to
6. Treat the parent managed graph as authoritative for **wave order and blockers**. Use the child issue body only as a consistency check for blocker text, not as the source of scheduling truth.
7. If any referenced child issue is missing, unreadable, malformed enough that execution order is unclear, or disagrees with the parent graph about wave or blockers, stop with a blocking error.

## Determine what is ready

Build the execution queue from the current GitHub state, not assumptions from earlier in the session.

1. Ignore already-closed child issues.
2. Find the **lowest-numbered wave** that still has open work.
3. Within that wave:
   - ready tasks are open **AFK** issues whose blockers are all closed
   - blocked tasks stay queued for later in the same wave or a later wave
   - **HITL** issues are never implemented by the agent
4. If the lowest open wave contains only HITL or blocked tasks, stop and report the exact issue numbers and what human action is required.
5. Never advance to the next wave until the current wave's ready AFK tasks are fully handled.

### Prefer child issue state over checkbox drift

Before launching new implementation or verification work:

1. If a child issue is already closed but its parent task-graph line is still `[ ]`, treat the child issue state as authoritative and continue scheduling from the child issue state.
2. If a parent task-graph line is `[x]` but the child issue is still open, treat the task as still open. Do not trust the checkbox alone as proof of completion.
3. Some weaker models over-index on checkbox state. Make it explicit in the controller plan whenever drift exists: `child issue state controls readiness; stale parent checkbox does not block progress`.

## Wave scheduling

Treat `[same wave]` as permission for parallelism, not a command.

Within the ready wave:
<exited with exit code 0>
````

</details>


---

<sub>⏱️ 11s</sub>

### ✅ `view`

**view the file at /home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md.**

/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md (lines 100-250)

<details>
<summary>151 lines</summary>

````
100. 
101. 1. Default to **one child issue per implementation subagent**.
102. 2. Launch tasks in parallel only when all are true:
103.    - their blockers are closed
104.    - their `Files likely touched` hints do not overlap **and** the controller's code reading does not reveal a shared file or module boundary
105.    - each parallel implementation subagent has an isolated worktree or equivalent isolated checkout
106. 3. Treat `Files likely touched` as a scheduling hint, not a guarantee. If overlap is uncertain, or isolated worktrees are unavailable, serialize the tasks within the wave.
107. 4. If one task in a parallel wave fails, let the already-running independent tasks finish, then stop before launching another wave.
108. 5. After every wave, wait for all implementation results, then run review, then verify, then update issue state.
109. 
110. When reporting the plan for a wave, use explicit language such as:
111. 
112. ```markdown
113. Wave W1
114. 
115. - Launch W1-A: #123 in a TDD subagent.
116. - Launch W1-B: #124 in a TDD subagent.
117. - Keep #125 sequential because it overlaps on `src/foo.ts`.
118. - Wait for W1 results before W2.
119. ```
120. 
121. ## Implementation subagents
122. 
123. Every implementation task must run in its own subagent. Before the subagent does anything else, it must load the `tdd` skill. Before it reads from or writes to GitHub issues, it must explicitly load `gh-cli`.
124. 
125. Pass the subagent only the context it needs:
126. 
127. - parent issue number and title
128. - assigned child issue number, title, body, and recent comments
129. - current wave name
130. - current TDD stage for that child issue: `none | red | green | refactor`
131. - resolved blocker state
132. - relevant repo/worktree/branch context
133. - likely file paths from `Files likely touched`, marked explicitly as hints rather than hard limits
134. - acceptance criteria and verification commands
135. - any directly relevant source files the controller already read
136. 
137. Tell the subagent to:
138. 
139. 1. Implement **only** the assigned child issue.
140. 2. Follow **RED → GREEN → REFACTOR** strictly.
141. 3. Keep slices thin and avoid broad cleanup.
142. 4. Use `gh-cli` explicitly for issue comments, issue closure, and parent-issue reads. Do not assume the model will remember to load it implicitly.
143. 5. Run the child issue's targeted verification commands exactly as required for that issue, and treat missing tooling as a blocking result rather than a cue to invent substitutes.
144. 6. Do not finish with "ready to close", "done", or a status-only comment. Stay responsible for GitHub closeout until it is either confirmed or blocked.
145. 7. Return:
146.     - RED/GREEN/REFACTOR summary
147.     - files changed
148.     - commands run and outcomes
149.     - GitHub closeout evidence: child issue closed, or the exact blocker that prevented closure
150.     - remaining risks or deferments
151. 8. Never commit, push, rebase, merge, open a PR, or invoke landing skills. Leave the worktree uncommitted for the controller.
152. 
153. Do not let the implementation subagent expand scope, edit files owned by another in-flight task, or decide wave ordering on its own.
154. If it must touch a file that was not listed in `Files likely touched`, it should stop and escalate that need back to the controller instead of silently broadening scope.
155. If it reports any git landing action already happened, treat that as a blocking workflow violation rather than progress.
156. 
157. ### Resume by current stage
158. 
159. Implementation subagents must resume from the passed `current_stage` like this:
160. 
161. - `none`: start with RED.
162. - `red`: re-run the failing test to confirm clean RED, then continue to GREEN.
163. - `green`: re-run the passing proof for the targeted test or command, then continue to REFACTOR.
164. - `refactor`: re-run the post-refactor targeted tests/commands, do only the remaining cleanup or closeout work, then hand off to review.
165. 
166. ### Clean RED rule
167. 
168. A RED step counts only when the new or updated test fails for the intended missing behavior. Syntax errors in the test, broken imports caused by the test setup itself, or invalid fixtures do **not** count as a clean RED.
169. 
170. ### Durable TDD progress
171. 
172. Each child issue must record TDD progress while it happens, not only at the end.
173. 
174. 1. After clean RED, add a child-issue comment with `Stage: red`, the test command, and brief evidence of the expected failure.
175. 2. After GREEN, add a comment with `Stage: green`, the implementation command/test result, and the files changed.
176. 3. After REFACTOR, add a comment with `Stage: refactor`, the rerun command/results, and whether the task is ready for review.
177. 4. On resume, the latest stage comment is the authoritative in-progress state for an open child issue.
178. 
179. ### GitHub closeout is part of implementation
180. 
181. Review and verification still gate completion, but the implementation subagent owns the final GitHub closeout for its child issue.
182. 
183. 1. After review fixes are complete and every required verification command that covers the child issue passed, send the assigned implementation subagent an explicit closeout turn instead of accepting a status-only finish.
184. 2. In that closeout turn, the subagent must explicitly load `gh-cli`, then:
185.    - close the child issue
186.    - re-read the child issue and confirm GitHub now shows it closed
187. 3. A `Stage: refactor` comment, "done" comment, or "task complete" comment is progress evidence only. It never counts as completion.
188. 4. If a subagent leaves comments but does not close the child issue, treat that child issue as incomplete: keep the issue open and stop before the next wave.
189. 5. Until the controller has re-read GitHub and confirmed closure, report only the **current** state. Do not write speculative sections like `Outcome after closeout` or claim the issue is closed just because you plan to send a closeout turn next.
190. 6. If any closeout step fails, the subagent must return a blocking result with the exact failed GitHub command or edit step. Do not declare success.
191. 
192. ## Review subagents
193. 
194. After each wave's implementation finishes, review the changed files in subagents before closing any child issue.
195. 
196. ### Required review passes
197. 
198. 1. Launch `code-simplifier` subagents first:
199.    - if the wave changed 5 files or fewer, use 1 subagent for the whole wave
200.    - otherwise partition files into non-overlapping groups and use one subagent per group
201. 2. Launch three review subagents in parallel on the reviewed wave scope:
202.    - `code-reviewer` for correctness and conventions
203.    - `security-review` for security and unsafe defaults
204.    - `code-reviewer` for simplicity, duplication, and maintainability
205. 3. Fix all blocking review findings before closing the affected child issues.
206. 4. If review-driven fixes change code, rerun the relevant review subagents on the affected scope before closure. Do not rely on the pre-fix review result.
207. 5. Record deferred non-blocking findings in the relevant issue comments or as follow-up notes to the user.
208. 
209. The controller must define the review file list. Review subagents must not recompute or narrow their own scope.
210. Review subagents inspect code only; they must not commit, push, or prepare PR text.
211. 
212. Normalize blocking review findings like this:
213. 
214. - `code-reviewer`: `Critical` and `Important` block closure.
215. - `security-review`: `High` and `Medium` block closure.
216. - `code-simplifier`: advisory by default; only treat a finding as blocking when it exposes a correctness risk, unsafe duplication, or a cross-task scope conflict.
217. 
218. ## Controller checkpoint before review
219. 
220. After each implementation subagent finishes, the controller must inspect the actual diff and the task's test output before moving on.
221. 
222. 1. Read the changed files or diff for that child issue.
223. 2. Read the reported test/command output, or rerun the targeted command if the evidence is incomplete.
224. 3. If the subagent changed unexpected files, failed to produce a clean RED/GREEN/REFACTOR chain, skipped or substituted a required verification command, or left verification unclear, stop and resolve that before review.
225. 
226. Do not close issues or advance waves based on subagent summaries alone.
227. 
228. ## Verification subagents and implementation-owned issue closure
229. 
230. Verification also runs in subagents. Keep the controller focused on orchestration and acceptance, then hand final GitHub closeout back to the implementation subagent rather than treating a comment or summary as enough.
231. 
232. For each completed child issue in the wave:
233. 
234. 1. Build a controller-authored verification plan before launching verification subagents:
235.    - default: one verification subagent per child issue using that issue's `Verification` steps
236.    - exception: if a command clearly validates multiple child issues together, create one shared command group and list the exact covered child issue numbers
237. 2. Assert that every child issue being considered for closure is covered by at least one verification command or command group. If any issue has no verification coverage, do not close it.
238. 3. Treat each listed verification step as the required command contract for that issue. If the issue says to use a framework or project CLI, run that CLI; do not silently swap in static analysis, code reading, lint-only checks, type-check-only checks, or some other weaker proxy just because the intended verification tool is missing or inconvenient.
239. 4. If a required verification command cannot run as written because a binary, framework CLI, generated artifact, environment dependency, credential, or service is unavailable, stop and surface that exact blocker. Report the command, the missing dependency/tool, and the stderr or setup gap. Do not mark the issue ready to close, and do not invent an alternative verification path unless the child issue itself already lists it or the human updates the verification plan explicitly.
240. 5. Launch verification subagents from that plan.
241. 6. Have each verification subagent run its assigned commands and return command, exit code, covered issue numbers, and evidence.
242. 7. Do not treat passing verification as completion. Verification subagents provide evidence only; they do not close child issues or edit the parent task graph.
243. 8. Do not close any child issue covered by a shared command group unless that shared group passes.
244. 9. Confirm the acceptance criteria are satisfied.
245. 10. Add a concise progress comment that captures:
246.    - wave name
247.    - RED/GREEN/REFACTOR completion
248.    - changed files
249.    - verification evidence
250.    - notable review findings and fixes
````

</details>


---

<sub>⏱️ 14s</sub>

### ✅ `view`

**view the file at /home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md.**

/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md (lines 250-366)

<details>
<summary>117 lines</summary>

````
250.    - notable review findings and fixes
251. 11. Once review is clear and every verification command that covers the child issue passed, send the assigned implementation subagent a closeout turn with explicit instructions to load `gh-cli`, close the child issue, and re-read GitHub to confirm closure.
252. 12. If that closeout turn returns only a comment, "ready to close", or another status-only note without the child issue actually closing on GitHub, treat it as a failed closeout. Keep the child issue open and stop before another wave starts.
253. 13. If the closeout turn claims success but a fresh GitHub read still shows the child issue open, stop and report the mismatch before another wave starts.
254. 
255. If a child issue has multiple verification commands and they are independent, the controller may launch them in parallel verification subagents. If they share state or resources, run them sequentially through verification subagents.
256. 
257. Verification subagents must preserve verification strength:
258. 
259. - If the required verification command is unavailable, fail closed and report the blocker.
260. - Do not replace framework-native verification with static analysis, source inspection, or generic "looks correct" reasoning.
261. - Do not downgrade `npm run verify:web`, `bin/rails test`, `cargo test`, `nx test`, framework codegen validators, or similar required commands to unrelated checks unless the issue explicitly says those checks are acceptable alternatives.
262. - Never commit, push, or open a PR after verification passes. Verification proves readiness for issue-state updates only.
263. 
264. If verification is missing, ambiguous, or failing:
265. 
266. - do not close the child issue
267. - report the exact gap
268. - stop before the next wave unless another already-launched task is still finishing
269. 
270. ### Parent task-graph checkboxes are informational only
271. 
272. Use the parent task graph for wave order and blocker parsing, but do not make checkbox edits part of task completion.
273. 
274. 1. Never block child-issue completion on editing the parent task-graph checkbox.
275. 2. Never reopen, hold, or downgrade a closed child issue just because the parent line still shows `[ ]`.
276. 3. If the parent line shows `[x]` while the child issue is still open, trust the child issue state and treat the task as still open.
277. 4. Mention stale parent checkbox state only when it helps explain why the task graph display looks outdated. Do not present that drift as a blocker.
278. 
279. ## Acceptance confirmation
280. 
281. Before declaring any child issue complete or advancing to the next wave, the controller must also confirm that:
282. 
283. 1. the acceptance criteria are satisfied
284. 2. no blocking review finding remains unresolved for that issue's scope
285. 3. the latest issue comments make the TDD stage history and verification outcome visible from GitHub alone
286. 4. no required verification command was skipped, replaced with a weaker proxy, or left blocked without being reported
287. 5. the child issue is actually closed on GitHub, not merely described as complete in a comment
288. 6. no git commit, push, merge, rebase, `commit`/`commit-to-pr` invocation, or PR creation happened during this run
289. 
290. ## Resume behavior
291. 
292. This skill is resumable from GitHub for queue state and TDD history, but not for missing local code.
293. 
294. On resume:
295. 
296. 1. Re-fetch the parent issue and all open child issues from the task graph.
297. 2. Parse each open child issue's latest `Stage:` comment into `current_stage`.
298. 3. Recompute ready work from current child-issue states and ignore stale parent checkbox drift.
299. 4. Ignore tasks that are already closed.
300. 5. Continue from the lowest-numbered wave that still has open work.
301. 6. Pass `current_stage` into the next implementation subagent instead of restarting the slice blindly.
302. 7. Resume from `green` or `refactor` only when the corresponding local code and test state are still present in the working tree.
303. 8. If the local state for an open issue is missing or disagrees with the latest GitHub `Stage:` history, do not trust the recorded stage. Either restart that issue from RED deliberately or stop and ask the user how to recover the lost work.
304. 
305. Do not rely on local scratch files for queue state.
306. 
307. ## Stop conditions
308. 
309. Stop and report clearly when any of these happens:
310. 
311. - the parent issue has no valid `prd-to-tasks` task graph
312. - a child issue referenced by the graph is missing or malformed
313. - the current lowest wave is gated by a HITL issue
314. - repository or GitHub authentication is ambiguous or broken
315. - a required verification command or framework CLI is unavailable and no human-approved replacement path exists
316. - an implementation or verification failure remains unresolved
317. - a completed child issue cannot be closed or confirmed on GitHub
318. - unrelated local changes create a conflict with the assigned task scope
319. 
320. ## Final response visibility rules
321. 
322. Some weaker models do the right orchestration but omit state the user still needs. Make the final response spell out the safety-critical state instead of implying it.
323. 
324. 1. Keep every section from the final template, including `Landing status`, even when its content is `- none`.
325. 2. If a child issue stays open, say that explicitly with `#<issue> remains open` or `not ready to close`.
326. 3. If the parent PRD issue stays open, say that explicitly.
327. 4. If landing work is out of scope or blocked, say explicitly that no commit, push, or PR action will be performed in this run.
328. 5. If a subagent only posted a completion comment or "ready to close" note, say explicitly that comment-only status does not count and that the child issue remains open until real GitHub updates succeed.
329. 6. When closeout is still pending or blocked, use these exact phrases somewhere in the response:
330.    - `#<issue> remains open.`
331.    - `parent PRD issue remains open.`
332. 7. When closeout is confirmed, use these exact phrases somewhere in the response:
333.    - `#<issue> is closed.`
334. 8. Never mix pending and confirmed states. If GitHub has not yet been re-read to confirm closeout, do not say the issue is closed and do not say the next wave is ready.
335. 
336. ## Final response
337. 
338. Always end with a concise execution summary in this shape:
339. 
340. ```markdown
341. PRD execution status for #<parent>
342. 
343. Completed this run:
344. 
345. 1. #<issue> <title>
346. 
347. Blocked / waiting:
348. 
349. 1. #<issue> <title> - <reason>
350. 
351. Next ready work:
352. 
353. - W<n>: #<issue> <title>
354. 
355. Landing status:
356. 
357. - Local changes only; no commit, push, or PR actions performed in this run.
358. 
359. Notes:
360. 
361. - <review deferments, assumptions, or follow-up items>
362. ```
363. 
364. Keep the section order exactly as written. If a section has no items, write `- none`.
365. 
366. If all AFK child issues are closed and only HITL or no work remains, say that explicitly. If the user wants the finished work landed after that, tell them `prd-implement` stops here and they must start a separate `commit` or `commit-to-pr` request. Never invoke those skills from inside `prd-implement`.
````

</details>


---

<sub>⏱️ 17s</sub>

### 💬 Copilot

Now I have the full skill file. Based on the scenario and the skill's requirements, I need to respond as the controller would handle the checkpoint before review. Key section is **"Controller checkpoint before review"** (lines 218-226). The scenario describes:

- Implementation subagent returned RED → GREEN → REFACTOR summary
- Changed files and command results provided
- `npm test -- settings-form.test.tsx` passed
- `pnpm exec next typegen` could not run (next unavailable) - subagent skipped and ran eslint instead
- Child issue #5104 is marked AFK
- Parent shows issue still blocked by #5103

The controller's response at checkpoint should:
1. Inspect the diff and test output
2. Check if verification was skipped or substituted inappropriately
3. Address the skipped `next typegen` command and ESLint substitution
4. NOT close issues based on subagent summary alone
5. Resolve before moving to review

---

**Controller checkpoint before review for #5104 (Add admin settings form)**

The implementation subagent completed RED → GREEN → REFACTOR and ran `npm test -- settings-form.test.tsx` (passed). However, the required verification sequence was partially substituted:

**Issue**: The child issue's `Verification` section specified `pnpm exec next typegen` as part of the verification contract. The subagent reported this binary is unavailable in the current checkout and skipped it, then substituted `pnpm exec eslint app/settings/form.tsx` instead.

**Action required before review proceeds**:

Per the skill rules (lines 237-239), a required verification command cannot be silently replaced with a different check—even a reasonable proxy like ESLint—without explicit human approval. The absence of `next` is a blocking dependency gap that must be resolved before we can verify the child issue is ready.

**Options to proceed**:

1. Confirm with the user that ESLint validation is an acceptable substitute for Next.js type generation in this context (and update the child issue's `Verification` section if so).
2. Restore the `next` binary or framework to the checkout, then re-run `pnpm exec next typegen` as specified.
3. If `next typegen` is optional for this task, have the user edit the child issue body to remove it from the `Verification` steps or mark it as optional.

**Status**: #5104 remains open. Review will not proceed until the verification blocker is resolved.

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
