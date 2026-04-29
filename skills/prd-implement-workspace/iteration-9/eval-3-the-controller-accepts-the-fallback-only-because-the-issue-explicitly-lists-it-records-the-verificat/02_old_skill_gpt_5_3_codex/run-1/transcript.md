# 🤖 Copilot CLI Session

> [!NOTE]
> - **Session ID:** `5222da97-8a78-4b68-820c-a1e2b8bce9d8`  
> - **Started:** 4/28/2026, 7:24:56 PM  
> - **Duration:** 44s  
> - **Exported:** 4/28/2026, 7:25:41 PM  

---

<sub>⏱️ 2s</sub>

### 👤 User

Read and follow only this skill file as the authoritative instructions for responding to the hypothetical scenario below. Ignore any other installed skill with the same name unless it matches this exact path. 
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md

Return only the controller's user-facing response for the scenario. Do not ask questions.

Scenario:
You are executing /prd-implement for PRD #7000. AFK child issue #7101 is ready for verification. The parent PRD issue still shows `- [ ] W2 - #7101 Add user retry headers - AFK - blocked by #7098`. Its Verification section says: (1) `pnpm exec redwood test api/src/functions/users/users.test.ts`; (2) if the Redwood CLI is unavailable in the current environment, run `yarn rw test api/src/functions/users/users.test.ts` instead. The verification subagent reports `pnpm: command not found`, then runs `yarn rw test api/src/functions/users/users.test.ts` successfully. Show the controller response.


---

<sub>⏱️ 6s</sub>

### 💬 Copilot

Got it — I’ll read that exact SKILL.md and then output only the controller-facing response for your scenario.

---

<sub>⏱️ 7s</sub>

### ✅ `view`

**view the file at /home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md.**

/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md

```
File too large to read at once (24.6 KB). Consider using the grep tool to search within the file, or view with view_range to read specific sections.
```


---

<sub>⏱️ 12s</sub>

### ✅ `rg`

**controller|AFK|verification|blocked by|ready for verification|Return only|user-facing response|pnpm|yarn rw|fallback|PRD**

"controller|AFK|verification|blocked by|ready for verification|Return only|user-facing response|pnpm|yarn rw|fallback|PRD" (skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md)

<details>
<summary>61 matches</summary>

```
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:3:description: Execute a PRD GitHub issue that already has a task graph from `prd-to-tasks`. Use this whenever the user wants to implement, resume, or finish work from a PRD/tracker issue with child implementation issues and execution waves — for example "implement PRD #123", "work through the task graph under issue 123", "resume the AFK slices for #123", or "build the next ready task from the PRD issue". This skill reads the parent issue's managed `Task graph` block, explicitly loads the `gh-cli` skill for issue reads and child-issue writes, executes AFK child issues in dependency order, requires `tdd` subagents for implementation, and treats completion as real GitHub state changes: the child issue must actually be closed. Comments alone never count as completion. Parent task-graph checkboxes may lag behind and do not block completion. It stops before git landing work: never commit, push, or open a PR from inside this skill; use `commit` or `commit-to-pr` separately afterward. Do not use it to create or redesign the task graph; use `prd-to-tasks` first.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:6:# PRD Implement
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:8:Use this skill to turn a PRD issue graph into implemented code without letting the controller context balloon.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:10:The controller owns intake, graph parsing, wave scheduling, and issue updates. It does **not** implement tasks inline. Every implementation task runs in a subagent that loads the `tdd` skill first and `gh-cli` before any GitHub reads or writes. Every review step also runs in subagents. Completed work is not fully recorded until the child issue is closed on GitHub. A completion comment, `Stage: refactor` note, or "ready to close" summary is never a substitute for that real GitHub state change. Parent `Task graph` checkbox drift does not block completion.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:21:1. Treat the PRD issue's managed `Task graph` block as the source of truth for wave order and intended child issues.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:22:2. Treat each child issue body as the source of truth for that task's scope, acceptance criteria, verification steps, likely files, and HITL/AFK type.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:24:4. Only execute **AFK** issues. **HITL** issues pause the workflow until the named decision, review, approval, or access step happens.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:26:6. The controller schedules waves; implementation happens only in subagents.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:29:9. Treat completion as a GitHub closeout: close the child issue. A task is not done until GitHub shows that issue closed. Leave the parent PRD issue open.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:31:11. This skill never commits, pushes, rebases, merges, or opens PRs. Landing work always happens in a separate request after PRD execution stops.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:38:2. Never ask implementation, review, or verification subagents to prepare commits, push branches, draft PRs, or land code. They may inspect diffs and local state, but they must leave changes uncommitted and unpushed.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:39:3. If the user asks for "implement PRD #123 and open a PR" in one request, execute only the PRD implementation workflow. In the final response, say that landing work remains out of scope for this run and requires a separate `commit` or `commit-to-pr` request after this skill finishes.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:40:4. If any subagent reports that it already committed, pushed, rebased, merged, or opened a PR, stop immediately and surface that as a workflow violation before review, verification, or issue closure continues. In that response, also say the child issue remains open.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:41:5. Some weaker models equate "verified" with "ready to land." Counter that drift by restating the boundary in the controller plan whenever the user mentions commits, pushes, branches, or PRs: `Landing work remains out of scope for this run.`
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:53:- [ ] W1 - #123 Slice title - AFK - blocked by none
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:54:- [ ] W2 - #124 Another slice - HITL - blocked by #123
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:63:   - type: the final `- AFK -` or `- HITL -` segment
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:64:   - blockers: the text after the final `blocked by `
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:65:   - title: everything between `#<number> ` and the final ` - AFK/HITL - blocked by ...`
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:81:   - ready tasks are open **AFK** issues whose blockers are all closed
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:85:5. Never advance to the next wave until the current wave's ready AFK tasks are fully handled.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:89:Before launching new implementation or verification work:
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:93:3. Some weaker models over-index on checkbox state. Make it explicit in the controller plan whenever drift exists: `child issue state controls readiness; stale parent checkbox does not block progress`.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:104:   - their `Files likely touched` hints do not overlap **and** the controller's code reading does not reveal a shared file or module boundary
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:134:- acceptance criteria and verification commands
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:135:- any directly relevant source files the controller already read
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:143:5. Run the child issue's targeted verification commands exactly as required for that issue, and treat missing tooling as a blocking result rather than a cue to invent substitutes.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:151:8. Never commit, push, rebase, merge, open a PR, or invoke landing skills. Leave the worktree uncommitted for the controller.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:154:If it must touch a file that was not listed in `Files likely touched`, it should stop and escalate that need back to the controller instead of silently broadening scope.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:181:Review and verification still gate completion, but the implementation subagent owns the final GitHub closeout for its child issue.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:183:1. After review fixes are complete and every required verification command that covers the child issue passed, send the assigned implementation subagent an explicit closeout turn instead of accepting a status-only finish.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:189:5. Until the controller has re-read GitHub and confirmed closure, report only the **current** state. Do not write speculative sections like `Outcome after closeout` or claim the issue is closed just because you plan to send a closeout turn next.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:209:The controller must define the review file list. Review subagents must not recompute or narrow their own scope.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:220:After each implementation subagent finishes, the controller must inspect the actual diff and the task's test output before moving on.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:224:3. If the subagent changed unexpected files, failed to produce a clean RED/GREEN/REFACTOR chain, skipped or substituted a required verification command, or left verification unclear, stop and resolve that before review.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:230:Verification also runs in subagents. Keep the controller focused on orchestration and acceptance, then hand final GitHub closeout back to the implementation subagent rather than treating a comment or summary as enough.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:234:1. Build a controller-authored verification plan before launching verification subagents:
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:235:   - default: one verification subagent per child issue using that issue's `Verification` steps
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:237:2. Assert that every child issue being considered for closure is covered by at least one verification command or command group. If any issue has no verification coverage, do not close it.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:238:3. Treat each listed verification step as the required command contract for that issue. If the issue says to use a framework or project CLI, run that CLI; do not silently swap in static analysis, code reading, lint-only checks, type-check-only checks, or some other weaker proxy just because the intended verification tool is missing or inconvenient.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:239:4. If a required verification command cannot run as written because a binary, framework CLI, generated artifact, environment dependency, credential, or service is unavailable, stop and surface that exact blocker. Report the command, the missing dependency/tool, and the stderr or setup gap. Do not mark the issue ready to close, and do not invent an alternative verification path unless the child issue itself already lists it or the human updates the verification plan explicitly.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:240:5. Launch verification subagents from that plan.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:241:6. Have each verification subagent run its assigned commands and return command, exit code, covered issue numbers, and evidence.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:242:7. Do not treat passing verification as completion. Verification subagents provide evidence only; they do not close child issues or edit the parent task graph.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:249:   - verification evidence
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:251:11. Once review is clear and every verification command that covers the child issue passed, send the assigned implementation subagent a closeout turn with explicit instructions to load `gh-cli`, close the child issue, and re-read GitHub to confirm closure.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:255:If a child issue has multiple verification commands and they are independent, the controller may launch them in parallel verification subagents. If they share state or resources, run them sequentially through verification subagents.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:257:Verification subagents must preserve verification strength:
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:259:- If the required verification command is unavailable, fail closed and report the blocker.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:260:- Do not replace framework-native verification with static analysis, source inspection, or generic "looks correct" reasoning.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:262:- Never commit, push, or open a PR after verification passes. Verification proves readiness for issue-state updates only.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:264:If verification is missing, ambiguous, or failing:
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:281:Before declaring any child issue complete or advancing to the next wave, the controller must also confirm that:
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:285:3. the latest issue comments make the TDD stage history and verification outcome visible from GitHub alone
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:286:4. no required verification command was skipped, replaced with a weaker proxy, or left blocked without being reported
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:315:- a required verification command or framework CLI is unavailable and no human-approved replacement path exists
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:316:- an implementation or verification failure remains unresolved
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:326:3. If the parent PRD issue stays open, say that explicitly.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:331:   - `parent PRD issue remains open.`
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:341:PRD execution status for #<parent>
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:366:If all AFK child issues are closed and only HITL or no work remains, say that explicitly. If the user wants the finished work landed after that, tell them `prd-implement` stops here and they must start a separate `commit` or `commit-to-pr` request. Never invoke those skills from inside `prd-implement`.
```

</details>


---

<sub>⏱️ 20s</sub>

### ✅ `view`

**view the file at /home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md.**

/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md (lines 228-380)

<details>
<summary>140 lines</summary>

````
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
367.
````

</details>


---

<sub>⏱️ 20s</sub>

### ✅ `view`

**view the file at /home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md.**

/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md (lines 84-110)

<details>
<summary>27 lines</summary>

```
84. 4. If the lowest open wave contains only HITL or blocked tasks, stop and report the exact issue numbers and what human action is required.
85. 5. Never advance to the next wave until the current wave's ready AFK tasks are fully handled.
86. 
87. ### Prefer child issue state over checkbox drift
88. 
89. Before launching new implementation or verification work:
90. 
91. 1. If a child issue is already closed but its parent task-graph line is still `[ ]`, treat the child issue state as authoritative and continue scheduling from the child issue state.
92. 2. If a parent task-graph line is `[x]` but the child issue is still open, treat the task as still open. Do not trust the checkbox alone as proof of completion.
93. 3. Some weaker models over-index on checkbox state. Make it explicit in the controller plan whenever drift exists: `child issue state controls readiness; stale parent checkbox does not block progress`.
94. 
95. ## Wave scheduling
96. 
97. Treat `[same wave]` as permission for parallelism, not a command.
98. 
99. Within the ready wave:
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
```

</details>


---

<sub>⏱️ 20s</sub>

### ✅ `view`

**view the file at /home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md.**

/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md (lines 136-170)

<details>
<summary>35 lines</summary>

```
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
```

</details>


---

<sub>⏱️ 20s</sub>

### ✅ `view`

**view the file at /home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md.**

/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md (lines 312-340)

<details>
<summary>29 lines</summary>

````
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
````

</details>


---

<sub>⏱️ 41s</sub>

### 💬 Copilot

PRD execution status for #7000

Completed this run:

1. #7101 Add user retry headers — verification executed per issue instructions: `pnpm exec redwood test api/src/functions/users/users.test.ts` failed with `pnpm: command not found`, then the issue-defined fallback `yarn rw test api/src/functions/users/users.test.ts` passed.

Blocked / waiting:

1. #7101 Add user retry headers - verification is complete, but GitHub closeout is still pending and must be confirmed before completion.

Next ready work:

- W2: #7101 Add user retry headers (implementation-subagent closeout and GitHub re-read)

Landing status:

- Local changes only; no commit, push, or PR actions performed in this run.

Notes:

- Parent task-graph checkbox drift is informational only; child issue state controls readiness, so the stale `- [ ] W2 ... blocked by #7098` line does not block progress.
- #7101 remains open.
- parent PRD issue remains open.

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
