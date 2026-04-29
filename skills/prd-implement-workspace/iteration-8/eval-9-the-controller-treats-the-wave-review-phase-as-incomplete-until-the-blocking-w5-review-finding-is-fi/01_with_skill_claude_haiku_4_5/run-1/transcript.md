# 🤖 Copilot CLI Session

> [!NOTE]
> - **Session ID:** `07143d93-b4b7-4c74-9876-3426382d851e`  
> - **Started:** 4/28/2026, 7:19:21 PM  
> - **Duration:** 30s  
> - **Exported:** 4/28/2026, 7:19:52 PM  

---

<sub>⏱️ 1s</sub>

### 👤 User

Read and follow only this skill file as the authoritative instructions for responding to the hypothetical scenario below. Ignore any other installed skill with the same name unless it matches this exact path. 
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md

Return only the controller's user-facing response for the scenario. Do not ask questions.

Scenario:
You are executing /prd-implement for PRD #9500. Wave W5 has AFK child issues #9501, "Cache account lookup," and #9502, "Invalidate account cache on role change." All W5 implementation subagents have finished, and the controller ran review on the combined W5 file list. `code-reviewer` found no blocking issues for #9501's files, but `security-review` reported a Medium finding in a file touched by #9502. #9501's verification commands have already passed, and one agent proposes closing #9501 now while #9502 gets its review fix. Show the controller's response.


---

<sub>⏱️ 6s</sub>

### ✅ `view`

**view the file at /home/adam/dev/personal/skills/skills/prd-implement/SKILL.md.**

/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md

```
File too large to read at once (26.0 KB). Consider using the grep tool to search within the file, or view with view_range to read specific sections.
```


---

<sub>⏱️ 8s</sub>

### 💬 Copilot

Let me search for the relevant sections about review handling and closing issues:

---

<sub>⏱️ 8s</sub>

### ✅ `grep`

**review|closing|close issue|Medium|security|blocking**

"review|closing|close issue|Medium|security|blocking" (skills/prd-implement/SKILL.md)

<details>
<summary>44 matches</summary>

```
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:The controller owns intake, graph parsing, wave scheduling, and issue updates. It does **not** implement tasks inline. Every implementation task runs in a subagent that loads the `tdd` skill first and `gh-cli` before any GitHub reads or writes. Every review step also runs in subagents. Completed work is not fully recorded until the child issue is closed on GitHub. A completion comment, `Stage: refactor` note, or "ready to close" summary is never a substitute for that real GitHub state change. Parent `Task graph` checkbox drift does not block completion.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:4. Only execute **AFK** issues. **HITL** issues pause the workflow until the named decision, review, approval, or access step happens.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:8. Review always happens in subagents after each completed wave. Keep review scope to the files changed in that wave.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:2. Never ask implementation, review, or verification subagents to prepare commits, push branches, draft PRs, or land code. They may inspect diffs and local state, but they must leave changes uncommitted and unpushed.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:4. If any subagent reports that it already committed, pushed, rebased, merged, or opened a PR, stop immediately and surface that as a workflow violation before review, verification, or issue closure continues. In that response, also say the child issue remains open.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:7. If any referenced child issue is missing, unreadable, malformed enough that execution order is unclear, or disagrees with the parent graph about wave or blockers, stop with a blocking error.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:5. After every wave, wait for all implementation results, inspect each result, run one wave-level review phase across the combined changed-file set, rerun review after any review-driven fixes, then verify covered child issues, then update issue state.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:2. Run the controller checkpoint, then one review phase for the whole wave.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:3. After that review phase succeeds, run verification for the covered child issues.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:4. Only after review and verification are clear may the implementation subagents perform GitHub closeout for those child issues.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:5. Run the child issue's targeted verification commands exactly as required for that issue, and treat missing tooling as a blocking result rather than a cue to invent substitutes.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:If it reports any git landing action already happened, treat that as a blocking workflow violation rather than progress.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:- `refactor`: re-run the post-refactor targeted tests/commands, do only the remaining cleanup or closeout work, then hand off to review.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:3. After REFACTOR, add a comment with `Stage: refactor`, the rerun command/results, and whether the task is ready for review.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:### GitHub closeout after wave review and verification
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:Implementation subagents still own GitHub closeout, but closeout starts only after the full wave review phase succeeds and the child issue's required verification commands pass.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:1. Do not send any closeout turn while the wave review phase is still running, still blocked on findings, or has not yet covered the full wave scope.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:2. After review fixes are complete for the whole wave and every required verification command that covers the child issue passed, send the assigned implementation subagent an explicit closeout turn instead of accepting a status-only finish.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:7. If any closeout step fails, the subagent must return a blocking result with the exact failed GitHub command or edit step. Do not declare success.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:After all implementation work in the wave finishes, run one review phase over the full changed-file set for that wave before any child issue in the wave can move to closeout.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:### Required review passes
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:2. Launch three review subagents in parallel on the reviewed wave scope:
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:   - `code-reviewer` for correctness and conventions
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:   - `security-review` for security and unsafe defaults
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:   - `code-reviewer` for simplicity, duplication, and maintainability
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:3. Do not start verification or close any child issue while the wave review phase still has unresolved blocking findings anywhere in that wave scope.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:4. Fix all blocking review findings before closing the affected child issues.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:5. If review-driven fixes change code, rerun the relevant review subagents on the affected scope before closure. Do not rely on the pre-fix review result.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:6. Record deferred non-blocking findings in the relevant issue comments or as follow-up notes to the user.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:The controller must define the review file list. Review subagents must not recompute or narrow their own scope.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:Normalize blocking review findings like this:
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:- `code-reviewer`: `Critical` and `Important` block closure.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:- `security-review`: `High` and `Medium` block closure.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:- `code-simplifier`: advisory by default; only treat a finding as blocking when it exposes a correctness risk, unsafe duplication, or a cross-task scope conflict.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:## Controller checkpoint before review
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:3. If the subagent changed unexpected files, failed to produce a clean RED/GREEN/REFACTOR chain, skipped or substituted a required verification command, or left verification unclear, stop and resolve that before review.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:Do not close issues or advance waves based on subagent summaries alone.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:After the wave review phase passes, verification also runs in subagents. Keep the controller focused on orchestration and acceptance, then hand final GitHub closeout back to the implementation subagent rather than treating a comment or summary as enough.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:For each child issue approved by the completed wave review phase:
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:    - notable review findings and fixes
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:12. Once review is clear and every verification command that covers the child issue passed, send the assigned implementation subagent a closeout turn with explicit instructions to load `gh-cli`, close the child issue, and re-read GitHub to confirm closure.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:13. If that closeout turn returns only a comment, "ready to close", or another status-only note without the child issue actually closing on GitHub, treat it as a failed closeout. Keep the child issue open and stop before another wave starts.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:2. no blocking review finding remains unresolved for that issue's scope
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:- <review deferments, assumptions, or follow-up items>
```

</details>


---

<sub>⏱️ 11s</sub>

### 💬 Copilot

Now let me look for more specific guidance on handling Medium findings and the scenario where one issue has passed verification but another has a blocking finding:

---

<sub>⏱️ 11s</sub>

### ✅ `grep`

**Medium block|separately|different issues|not block another**

"Medium block|separately|different issues|not block another" (skills/prd-implement/SKILL.md)

```
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:description: Execute a PRD GitHub issue that already has a task graph from `prd-to-tasks`. Use this whenever the user wants to implement, resume, or finish work from a PRD/tracker issue with child implementation issues and execution waves — for example "implement PRD #123", "work through the task graph under issue 123", "resume the AFK slices for #123", or "build the next ready task from the PRD issue". This skill reads the parent issue's managed `Task graph` block, explicitly loads the `gh-cli` skill for issue reads and child-issue writes, executes AFK child issues in dependency order, requires `tdd` subagents for implementation, and treats completion as real GitHub state changes: the child issue must actually be closed. Comments alone never count as completion. Parent task-graph checkboxes may lag behind and do not block completion. It stops before git landing work: never commit, push, or open a PR from inside this skill; use `commit` or `commit-to-pr` separately afterward. Do not use it to create or redesign the task graph; use `prd-to-tasks` first.
```


---

<sub>⏱️ 14s</sub>

### 💬 Copilot

Let me search for guidance on blocking findings and how they apply to individual issues:

---

<sub>⏱️ 14s</sub>

### ✅ `view`

**view the file at /home/adam/dev/personal/skills/skills/prd-implement/SKILL.md.**

/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md (lines 1-100)

<details>
<summary>100 lines</summary>

````
1. ---
2. name: prd-implement
3. description: Execute a PRD GitHub issue that already has a task graph from `prd-to-tasks`. Use this whenever the user wants to implement, resume, or finish work from a PRD/tracker issue with child implementation issues and execution waves — for example "implement PRD #123", "work through the task graph under issue 123", "resume the AFK slices for #123", or "build the next ready task from the PRD issue". This skill reads the parent issue's managed `Task graph` block, explicitly loads the `gh-cli` skill for issue reads and child-issue writes, executes AFK child issues in dependency order, requires `tdd` subagents for implementation, and treats completion as real GitHub state changes: the child issue must actually be closed. Comments alone never count as completion. Parent task-graph checkboxes may lag behind and do not block completion. It stops before git landing work: never commit, push, or open a PR from inside this skill; use `commit` or `commit-to-pr` separately afterward. Do not use it to create or redesign the task graph; use `prd-to-tasks` first.
4. ---
5. 
6. # PRD Implement
7. 
8. Use this skill to turn a PRD issue graph into implemented code without letting the controller context balloon.
9. 
10. The controller owns intake, graph parsing, wave scheduling, and issue updates. It does **not** implement tasks inline. Every implementation task runs in a subagent that loads the `tdd` skill first and `gh-cli` before any GitHub reads or writes. Every review step also runs in subagents. Completed work is not fully recorded until the child issue is closed on GitHub. A completion comment, `Stage: refactor` note, or "ready to close" summary is never a substitute for that real GitHub state change. Parent `Task graph` checkbox drift does not block completion.
11. 
12. ## Inputs
13. 
14. - `prd_issue` is required. Accept an issue number or issue URL.
15. - If the repository is ambiguous, resolve it before doing anything else.
16. 
17. If `prd_issue` is missing, ask for it. If the issue does not contain a `prd-to-tasks` task graph, stop and tell the user to run `prd-to-tasks` first.
18. 
19. ## Non-negotiable rules
20. 
21. 1. Treat the PRD issue's managed `Task graph` block as the source of truth for wave order and intended child issues.
22. 2. Treat each child issue body as the source of truth for that task's scope, acceptance criteria, verification steps, likely files, and HITL/AFK type.
23. 3. Do not invent new tasks, waves, or dependencies during implementation. If the graph is wrong, stop and tell the user what must be fixed in GitHub first.
24. 4. Only execute **AFK** issues. **HITL** issues pause the workflow until the named decision, review, approval, or access step happens.
25. 5. Never skip a lower-numbered wave to start a later wave early.
26. 6. The controller schedules waves; implementation happens only in subagents.
27. 7. Every implementation subagent must load the `tdd` skill first, then explicitly load `gh-cli` before any GitHub issue reads or writes, and follow a strict RED → GREEN → REFACTOR loop.
28. 8. Review always happens in subagents after each completed wave. Keep review scope to the files changed in that wave.
29. 9. Treat completion as a GitHub closeout: close the child issue. A task is not done until GitHub shows that issue closed. Leave the parent PRD issue open.
30. 10. Treat comments as evidence only, never as completion. A child issue with only a status comment is still open work until GitHub shows the issue closed.
31. 11. This skill never commits, pushes, rebases, merges, or opens PRs. Landing work always happens in a separate request after PRD execution stops.
32. 
33. ## Git and PR boundary
34. 
35. Treat landing work as a separate workflow. `prd-implement` ends at verified local changes plus GitHub child-issue closeout, not at branch landing.
36. 
37. 1. Never run `git commit`, `git push`, `git merge`, `git rebase`, `gh pr create`, or invoke `commit` / `commit-to-pr` from this skill.
38. 2. Never ask implementation, review, or verification subagents to prepare commits, push branches, draft PRs, or land code. They may inspect diffs and local state, but they must leave changes uncommitted and unpushed.
39. 3. If the user asks for "implement PRD #123 and open a PR" in one request, execute only the PRD implementation workflow. In the final response, say that landing work remains out of scope for this run and requires a separate `commit` or `commit-to-pr` request after this skill finishes.
40. 4. If any subagent reports that it already committed, pushed, rebased, merged, or opened a PR, stop immediately and surface that as a workflow violation before review, verification, or issue closure continues. In that response, also say the child issue remains open.
41. 5. Some weaker models equate "verified" with "ready to land." Counter that drift by restating the boundary in the controller plan whenever the user mentions commits, pushes, branches, or PRs: `Landing work remains out of scope for this run.`
42. 
43. ## Fetch and parse the graph
44. 
45. 1. Use the `gh-cli` skill to fetch the parent issue with comments. Some weaker models do not auto-load that skill, so call it explicitly before issue retrieval.
46. 2. Parse the managed block written by `prd-to-tasks`:
47. 
48. ```markdown
49. <!-- prd-to-tasks:start -->
50. 
51. ## Task graph
52. 
53. - [ ] W1 - #123 Slice title - AFK - blocked by none
54. - [ ] W2 - #124 Another slice - HITL - blocked by #123
55. <!-- prd-to-tasks:end -->
56. ```
57. 
58. 3. If the managed markers are missing, fall back to a plain `## Task graph` section only when it clearly uses the same line format.
59. 4. Parse each task-graph line with anchored fields, not naive string splitting:
60.    - checkbox: the leading `[ ]` or `[x]`
61.    - wave: leading `W<n>`
62.    - child issue: the first `#<number>` after the wave
63.    - type: the final `- AFK -` or `- HITL -` segment
64.    - blockers: the text after the final `blocked by `
65.    - title: everything between `#<number> ` and the final ` - AFK/HITL - blocked by ...`
66. 5. For every referenced child issue:
67.     - fetch its title, body, state, and recent comments
68.     - extract `Type`, `Acceptance criteria`, `Verification`, and `Files likely touched`
69.     - prefer the child issue state over the parent checkbox if they disagree
70.     - treat parent checkbox drift as informational only unless it creates ambiguity about which child issue the line refers to
71. 6. Treat the parent managed graph as authoritative for **wave order and blockers**. Use the child issue body only as a consistency check for blocker text, not as the source of scheduling truth.
72. 7. If any referenced child issue is missing, unreadable, malformed enough that execution order is unclear, or disagrees with the parent graph about wave or blockers, stop with a blocking error.
73. 
74. ## Determine what is ready
75. 
76. Build the execution queue from the current GitHub state, not assumptions from earlier in the session.
77. 
78. 1. Ignore already-closed child issues.
79. 2. Find the **lowest-numbered wave** that still has open work.
80. 3. Within that wave:
81.    - ready tasks are open **AFK** issues whose blockers are all closed
82.    - blocked tasks stay queued for later in the same wave or a later wave
83.    - **HITL** issues are never implemented by the agent
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
````

</details>


---

<sub>⏱️ 17s</sub>

### ✅ `view`

**view the file at /home/adam/dev/personal/skills/skills/prd-implement/SKILL.md.**

/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md (lines 230-330)

<details>
<summary>101 lines</summary>

```
230. 
231. After each implementation subagent finishes, the controller must inspect the actual diff and the task's test output before moving on.
232. 
233. 1. Read the changed files or diff for that child issue.
234. 2. Read the reported test/command output, or rerun the targeted command if the evidence is incomplete.
235. 3. If the subagent changed unexpected files, failed to produce a clean RED/GREEN/REFACTOR chain, skipped or substituted a required verification command, or left verification unclear, stop and resolve that before review.
236. 
237. Do not close issues or advance waves based on subagent summaries alone.
238. 
239. ## Verification subagents and implementation-owned issue closure
240. 
241. After the wave review phase passes, verification also runs in subagents. Keep the controller focused on orchestration and acceptance, then hand final GitHub closeout back to the implementation subagent rather than treating a comment or summary as enough.
242. 
243. For each child issue approved by the completed wave review phase:
244. 
245. 1. Build a controller-authored verification plan before launching verification subagents:
246.    - default: one verification subagent per child issue using that issue's `Verification` steps
247.    - exception: if a command clearly validates multiple child issues together, create one shared command group and list the exact covered child issue numbers
248. 2. Assert that every child issue being considered for closure is covered by at least one verification command or command group. If any issue has no verification coverage, do not close it.
249. 3. Treat each listed verification step as the required command contract for that issue. If the issue says to use a framework or project CLI, run that CLI; do not silently swap in static analysis, code reading, lint-only checks, type-check-only checks, or some other weaker proxy just because the intended verification tool is missing or inconvenient.
250. 4. If a required verification command cannot run as written because a binary, framework CLI, generated artifact, environment dependency, credential, or service is unavailable, stop and surface that exact blocker. Report the command, the missing dependency/tool, and the stderr or setup gap. Do not mark the issue ready to close, and do not invent an alternative verification path unless the child issue itself already lists it or the human updates the verification plan explicitly.
251. 5. Launch verification subagents from that plan.
252. 6. Have each verification subagent run its assigned commands and return command, exit code, covered issue numbers, and evidence.
253. 7. Do not treat passing verification as completion. Verification subagents provide evidence only; they do not close child issues or edit the parent task graph.
254. 8. Do not close any child issue covered by a shared command group unless that shared group passes.
255. 9. Confirm the acceptance criteria are satisfied.
256. 10. If a child issue explicitly lists a fallback verification command and that fallback passes, say that the fallback was allowed by the issue itself. Do not describe it as an improvised substitute.
257. 11. Add a concise progress comment that captures:
258.     - wave name
259.     - RED/GREEN/REFACTOR completion
260.     - changed files
261.     - verification evidence
262.     - notable review findings and fixes
263. 12. Once review is clear and every verification command that covers the child issue passed, send the assigned implementation subagent a closeout turn with explicit instructions to load `gh-cli`, close the child issue, and re-read GitHub to confirm closure.
264. 13. If that closeout turn returns only a comment, "ready to close", or another status-only note without the child issue actually closing on GitHub, treat it as a failed closeout. Keep the child issue open and stop before another wave starts.
265. 14. If the closeout turn claims success but a fresh GitHub read still shows the child issue open, stop and report the mismatch before another wave starts.
266. 
267. If a child issue has multiple verification commands and they are independent, the controller may launch them in parallel verification subagents. If they share state or resources, run them sequentially through verification subagents.
268. 
269. Verification subagents must preserve verification strength:
270. 
271. - If the required verification command is unavailable, fail closed and report the blocker.
272. - Do not replace framework-native verification with static analysis, source inspection, or generic "looks correct" reasoning.
273. - Do not downgrade `npm run verify:web`, `bin/rails test`, `cargo test`, `nx test`, framework codegen validators, or similar required commands to unrelated checks unless the issue explicitly says those checks are acceptable alternatives.
274. - Never commit, push, or open a PR after verification passes. Verification proves readiness for issue-state updates only.
275. 
276. If verification is missing, ambiguous, or failing:
277. 
278. - do not close the child issue
279. - report the exact gap
280. - stop before the next wave unless another already-launched task is still finishing
281. 
282. ### Parent task-graph checkboxes are informational only
283. 
284. Use the parent task graph for wave order and blocker parsing, but do not make checkbox edits part of task completion.
285. 
286. 1. Never block child-issue completion on editing the parent task-graph checkbox.
287. 2. Never reopen, hold, or downgrade a closed child issue just because the parent line still shows `[ ]`.
288. 3. If the parent line shows `[x]` while the child issue is still open, trust the child issue state and treat the task as still open.
289. 4. Mention stale parent checkbox state only when it helps explain why the task graph display looks outdated. Do not present that drift as a blocker.
290. 5. If the child issue is ready to close or already closed while the parent line still shows `[ ]`, say explicitly that the parent checkbox is informational only and does not delay closure.
291. 
292. ## Acceptance confirmation
293. 
294. Before declaring any child issue complete or advancing to the next wave, the controller must also confirm that:
295. 
296. 1. the acceptance criteria are satisfied
297. 2. no blocking review finding remains unresolved for that issue's scope
298. 3. the latest issue comments make the TDD stage history and verification outcome visible from GitHub alone
299. 4. no required verification command was skipped, replaced with a weaker proxy, or left blocked without being reported
300. 5. the child issue is actually closed on GitHub, not merely described as complete in a comment
301. 6. no git commit, push, merge, rebase, `commit`/`commit-to-pr` invocation, or PR creation happened during this run
302. 
303. ## Resume behavior
304. 
305. This skill is resumable from GitHub for queue state and TDD history, but not for missing local code.
306. 
307. On resume:
308. 
309. 1. Re-fetch the parent issue and all open child issues from the task graph.
310. 2. Parse each open child issue's latest `Stage:` comment into `current_stage`.
311. 3. Recompute ready work from current child-issue states and ignore stale parent checkbox drift.
312. 4. Ignore tasks that are already closed.
313. 5. Continue from the lowest-numbered wave that still has open work.
314. 6. Pass `current_stage` into the next implementation subagent instead of restarting the slice blindly.
315. 7. Resume from `green` or `refactor` only when the corresponding local code and test state are still present in the working tree.
316. 8. If the local state for an open issue is missing or disagrees with the latest GitHub `Stage:` history, do not trust the recorded stage. Either restart that issue from RED deliberately or stop and ask the user how to recover the lost work.
317. 
318. Do not rely on local scratch files for queue state.
319. 
320. ## Stop conditions
321. 
322. Stop and report clearly when any of these happens:
323. 
324. - the parent issue has no valid `prd-to-tasks` task graph
325. - a child issue referenced by the graph is missing or malformed
326. - the current lowest wave is gated by a HITL issue
327. - repository or GitHub authentication is ambiguous or broken
328. - a required verification command or framework CLI is unavailable and no human-approved replacement path exists
329. - an implementation or verification failure remains unresolved
330. - a completed child issue cannot be closed or confirmed on GitHub
```

</details>


---

<sub>⏱️ 20s</sub>

### ✅ `view`

**view the file at /home/adam/dev/personal/skills/skills/prd-implement/SKILL.md.**

/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md (lines 330-450)

<details>
<summary>51 lines</summary>

````
330. - a completed child issue cannot be closed or confirmed on GitHub
331. - unrelated local changes create a conflict with the assigned task scope
332. 
333. ## Final response visibility rules
334. 
335. Some weaker models do the right orchestration but omit state the user still needs. Make the final response spell out the safety-critical state instead of implying it.
336. 
337. 1. Keep every section from the final template, including `Landing status`, even when its content is `- none`.
338. 2. If a child issue stays open, say that explicitly with `#<issue> remains open` or `not ready to close`.
339. 3. If the parent PRD issue stays open, say that explicitly.
340. 4. If landing work is out of scope or blocked, say explicitly that no commit, push, or PR action will be performed in this run.
341. 5. If a subagent only posted a completion comment or "ready to close" note, say explicitly that comment-only status does not count and that the child issue remains open until real GitHub updates succeed.
342. 6. When closeout is still pending or blocked, use these exact phrases somewhere in the response:
343.    - `#<issue> remains open.`
344.    - `parent PRD issue remains open.`
345. 7. When closeout is confirmed, use these exact phrases somewhere in the response:
346.    - `#<issue> is closed.`
347. 8. Never mix pending and confirmed states. If GitHub has not yet been re-read to confirm closeout, do not say the issue is closed and do not say the next wave is ready.
348. 
349. ## Final response
350. 
351. Always end with a concise execution summary in this shape:
352. 
353. ```markdown
354. PRD execution status for #<parent>
355. 
356. Completed this run:
357. 
358. 1. #<issue> <title>
359. 
360. Blocked / waiting:
361. 
362. 1. #<issue> <title> - <reason>
363. 
364. Next ready work:
365. 
366. - W<n>: #<issue> <title>
367. 
368. Landing status:
369. 
370. - Local changes only; no commit, push, or PR actions performed in this run.
371. 
372. Notes:
373. 
374. - <review deferments, assumptions, or follow-up items>
375. ```
376. 
377. Keep the section order exactly as written. If a section has no items, write `- none`.
378. 
379. If all AFK child issues are closed and only HITL or no work remains, say that explicitly. If the user wants the finished work landed after that, tell them `prd-implement` stops here and they must start a separate `commit` or `commit-to-pr` request. Never invoke those skills from inside `prd-implement`.
380.
````

</details>


---

<sub>⏱️ 22s</sub>

### ✅ `view`

**view the file at /home/adam/dev/personal/skills/skills/prd-implement/SKILL.md.**

/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md (lines 155-230)

<details>
<summary>76 lines</summary>

```
155.     - RED/GREEN/REFACTOR summary
156.     - files changed
157.     - commands run and outcomes
158.     - GitHub closeout evidence: child issue closed, or the exact blocker that prevented closure
159.     - remaining risks or deferments
160. 8. Never commit, push, rebase, merge, open a PR, or invoke landing skills. Leave the worktree uncommitted for the controller.
161. 
162. Do not let the implementation subagent expand scope, edit files owned by another in-flight task, or decide wave ordering on its own.
163. If it must touch a file that was not listed in `Files likely touched`, it should stop and escalate that need back to the controller instead of silently broadening scope.
164. If it reports any git landing action already happened, treat that as a blocking workflow violation rather than progress.
165. 
166. ### Resume by current stage
167. 
168. Implementation subagents must resume from the passed `current_stage` like this:
169. 
170. - `none`: start with RED.
171. - `red`: re-run the failing test to confirm clean RED, then continue to GREEN.
172. - `green`: re-run the passing proof for the targeted test or command, then continue to REFACTOR.
173. - `refactor`: re-run the post-refactor targeted tests/commands, do only the remaining cleanup or closeout work, then hand off to review.
174. 
175. ### Clean RED rule
176. 
177. A RED step counts only when the new or updated test fails for the intended missing behavior. Syntax errors in the test, broken imports caused by the test setup itself, or invalid fixtures do **not** count as a clean RED.
178. 
179. ### Durable TDD progress
180. 
181. Each child issue must record TDD progress while it happens, not only at the end.
182. 
183. 1. After clean RED, add a child-issue comment with `Stage: red`, the test command, and brief evidence of the expected failure.
184. 2. After GREEN, add a comment with `Stage: green`, the implementation command/test result, and the files changed.
185. 3. After REFACTOR, add a comment with `Stage: refactor`, the rerun command/results, and whether the task is ready for review.
186. 4. On resume, the latest stage comment is the authoritative in-progress state for an open child issue.
187. 
188. ### GitHub closeout after wave review and verification
189. 
190. Implementation subagents still own GitHub closeout, but closeout starts only after the full wave review phase succeeds and the child issue's required verification commands pass.
191. 
192. 1. Do not send any closeout turn while the wave review phase is still running, still blocked on findings, or has not yet covered the full wave scope.
193. 2. After review fixes are complete for the whole wave and every required verification command that covers the child issue passed, send the assigned implementation subagent an explicit closeout turn instead of accepting a status-only finish.
194. 3. In that closeout turn, the subagent must explicitly load `gh-cli`, then:
195.     - close the child issue
196.     - re-read the child issue and confirm GitHub now shows it closed
197. 4. A `Stage: refactor` comment, "done" comment, or "task complete" comment is progress evidence only. It never counts as completion.
198. 5. If a subagent leaves comments but does not close the child issue, treat that child issue as incomplete: keep the issue open and stop before the next wave.
199. 6. Until the controller has re-read GitHub and confirmed closure, report only the **current** state. Do not write speculative sections like `Outcome after closeout` or claim the issue is closed just because you plan to send a closeout turn next.
200. 7. If any closeout step fails, the subagent must return a blocking result with the exact failed GitHub command or edit step. Do not declare success.
201. 
202. ## Review subagents
203. 
204. After all implementation work in the wave finishes, run one review phase over the full changed-file set for that wave before any child issue in the wave can move to closeout.
205. 
206. ### Required review passes
207. 
208. 1. Launch `code-simplifier` subagents first:
209.    - if the wave changed 5 files or fewer, use 1 subagent for the whole wave
210.    - otherwise partition files into non-overlapping groups and use one subagent per group
211. 2. Launch three review subagents in parallel on the reviewed wave scope:
212.    - `code-reviewer` for correctness and conventions
213.    - `security-review` for security and unsafe defaults
214.    - `code-reviewer` for simplicity, duplication, and maintainability
215. 3. Do not start verification or close any child issue while the wave review phase still has unresolved blocking findings anywhere in that wave scope.
216. 4. Fix all blocking review findings before closing the affected child issues.
217. 5. If review-driven fixes change code, rerun the relevant review subagents on the affected scope before closure. Do not rely on the pre-fix review result.
218. 6. Record deferred non-blocking findings in the relevant issue comments or as follow-up notes to the user.
219. 
220. The controller must define the review file list. Review subagents must not recompute or narrow their own scope.
221. Review subagents inspect code only; they must not commit, push, or prepare PR text.
222. 
223. Normalize blocking review findings like this:
224. 
225. - `code-reviewer`: `Critical` and `Important` block closure.
226. - `security-review`: `High` and `Medium` block closure.
227. - `code-simplifier`: advisory by default; only treat a finding as blocking when it exposes a correctness risk, unsafe duplication, or a cross-task scope conflict.
228. 
229. ## Controller checkpoint before review
230.
```

</details>


---

<sub>⏱️ 25s</sub>

### 💬 Copilot

Based on the SKILL.md, I now have the authoritative instructions. The key rules are:

1. **Line 226**: `security-review`: `High` and `Medium` block closure
2. **Line 216**: Fix all blocking review findings before closing the affected child issues
3. **Line 298**: No blocking review finding remains unresolved for that issue's scope

The scenario shows:
- #9501 (Cache account lookup): code-reviewer passed, verification commands passed, no blocking issues
- #9502 (Invalidate account cache on role change): security-review found a Medium finding (blocking)

Since the Medium finding is in a file touched by #9502, it only blocks #9502's closure, not #9501's. The skill requires that all blocking findings be fixed before closing affected child issues, but #9501 has no blocking findings and has passed verification.

However, there's a critical detail: "one agent proposes closing #9501 now while #9502 gets its review fix." The controller's response must address this proposal.

According to the skill:
- Line 215-216: Do not close any child issue while the wave review phase still has unresolved blocking findings **anywhere in that wave scope**
- The whole wave scope includes both #9501 and #9502
- There IS an unresolved Medium finding in the wave scope (in #9502's files)

Therefore, the controller must **block closure of both issues** until the Medium finding in #9502 is fixed and re-reviewed.

Here's the controller's user-facing response:

---

**Wave W5 review status:**

#9501 (Cache account lookup) has passed code review and verification, but **#9501 cannot close yet** because the wave-level review phase still has an unresolved blocking finding in #9502's scope. 

**security-review** reported a **Medium** finding in a file touched by #9502 (Invalidate account cache on role change). Per the review rules, all blocking findings must be fixed before any child issue in the wave can close.

**Next steps:**

1. Fix the Medium security finding in #9502's affected file(s)
2. Rerun security-review on the fixed scope
3. Once that review clears, both #9501 and #9502 will be ready for closeout in sequence

**Current state:**
- #9501 remains open — verification passed, but closeout blocked by unresolved wave-level findings
- #9502 remains open — blocked by the Medium security finding requiring fix

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
