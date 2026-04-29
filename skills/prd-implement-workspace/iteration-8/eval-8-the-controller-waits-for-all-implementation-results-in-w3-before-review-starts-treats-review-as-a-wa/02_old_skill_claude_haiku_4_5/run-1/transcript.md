# 🤖 Copilot CLI Session

> [!NOTE]
> - **Session ID:** `f029aeca-a401-4d84-bc64-7f58425085d4`  
> - **Started:** 4/28/2026, 7:19:04 PM  
> - **Duration:** 14s  
> - **Exported:** 4/28/2026, 7:19:18 PM  

---

<sub>⏱️ 2s</sub>

### 👤 User

Read and follow only this skill file as the authoritative instructions for responding to the hypothetical scenario below. Ignore any other installed skill with the same name unless it matches this exact path. 
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md

Return only the controller's user-facing response for the scenario. Do not ask questions.

Scenario:
You are executing /prd-implement for PRD #9400. Current wave W3 has AFK child issues #9401, "Backfill invoice timezone," and #9402, "Add invoice timezone admin filter." Both were launched in parallel because their likely files do not overlap. #9401 finishes first with a clean RED -\> GREEN -\> REFACTOR chain and passing targeted tests. #9402 is still running and has not returned yet. Another agent proposes starting review on #9401 now and, if it looks good, closing #9401 immediately so W4 can start sooner. Show the controller's response.


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

Let me search for content related to review, parallel execution, and waiting for dependencies:

---

<sub>⏱️ 9s</sub>

### ✅ `grep`

**review|parallel|wait|running|finished|hold|block|dependency|wave**

"review|parallel|wait|running|finished|hold|block|dependency|wave" (skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md)

<details>
<summary>90 matches</summary>

```
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:description: Execute a PRD GitHub issue that already has a task graph from `prd-to-tasks`. Use this whenever the user wants to implement, resume, or finish work from a PRD/tracker issue with child implementation issues and execution waves — for example "implement PRD #123", "work through the task graph under issue 123", "resume the AFK slices for #123", or "build the next ready task from the PRD issue". This skill reads the parent issue's managed `Task graph` block, explicitly loads the `gh-cli` skill for issue reads and child-issue writes, executes AFK child issues in dependency order, requires `tdd` subagents for implementation, and treats completion as real GitHub state changes: the child issue must actually be closed. Comments alone never count as completion. Parent task-graph checkboxes may lag behind and do not block completion. It stops before git landing work: never commit, push, or open a PR from inside this skill; use `commit` or `commit-to-pr` separately afterward. Do not use it to create or redesign the task graph; use `prd-to-tasks` first.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:The controller owns intake, graph parsing, wave scheduling, and issue updates. It does **not** implement tasks inline. Every implementation task runs in a subagent that loads the `tdd` skill first and `gh-cli` before any GitHub reads or writes. Every review step also runs in subagents. Completed work is not fully recorded until the child issue is closed on GitHub. A completion comment, `Stage: refactor` note, or "ready to close" summary is never a substitute for that real GitHub state change. Parent `Task graph` checkbox drift does not block completion.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:1. Treat the PRD issue's managed `Task graph` block as the source of truth for wave order and intended child issues.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:3. Do not invent new tasks, waves, or dependencies during implementation. If the graph is wrong, stop and tell the user what must be fixed in GitHub first.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:4. Only execute **AFK** issues. **HITL** issues pause the workflow until the named decision, review, approval, or access step happens.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:5. Never skip a lower-numbered wave to start a later wave early.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:6. The controller schedules waves; implementation happens only in subagents.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:8. Review always happens in subagents after each completed wave. Keep review scope to the files changed in that wave.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:2. Never ask implementation, review, or verification subagents to prepare commits, push branches, draft PRs, or land code. They may inspect diffs and local state, but they must leave changes uncommitted and unpushed.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:4. If any subagent reports that it already committed, pushed, rebased, merged, or opened a PR, stop immediately and surface that as a workflow violation before review, verification, or issue closure continues. In that response, also say the child issue remains open.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:2. Parse the managed block written by `prd-to-tasks`:
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:- [ ] W1 - #123 Slice title - AFK - blocked by none
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:- [ ] W2 - #124 Another slice - HITL - blocked by #123
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:   - wave: leading `W<n>`
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:   - child issue: the first `#<number>` after the wave
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:   - blockers: the text after the final `blocked by `
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:   - title: everything between `#<number> ` and the final ` - AFK/HITL - blocked by ...`
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:6. Treat the parent managed graph as authoritative for **wave order and blockers**. Use the child issue body only as a consistency check for blocker text, not as the source of scheduling truth.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:7. If any referenced child issue is missing, unreadable, malformed enough that execution order is unclear, or disagrees with the parent graph about wave or blockers, stop with a blocking error.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:2. Find the **lowest-numbered wave** that still has open work.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:3. Within that wave:
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:   - ready tasks are open **AFK** issues whose blockers are all closed
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:   - blocked tasks stay queued for later in the same wave or a later wave
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:4. If the lowest open wave contains only HITL or blocked tasks, stop and report the exact issue numbers and what human action is required.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:5. Never advance to the next wave until the current wave's ready AFK tasks are fully handled.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:3. Some weaker models over-index on checkbox state. Make it explicit in the controller plan whenever drift exists: `child issue state controls readiness; stale parent checkbox does not block progress`.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:Treat `[same wave]` as permission for parallelism, not a command.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:Within the ready wave:
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:2. Launch tasks in parallel only when all are true:
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:   - their blockers are closed
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:   - each parallel implementation subagent has an isolated worktree or equivalent isolated checkout
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:3. Treat `Files likely touched` as a scheduling hint, not a guarantee. If overlap is uncertain, or isolated worktrees are unavailable, serialize the tasks within the wave.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:4. If one task in a parallel wave fails, let the already-running independent tasks finish, then stop before launching another wave.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:5. After every wave, wait for all implementation results, then run review, then verify, then update issue state.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:When reporting the plan for a wave, use explicit language such as:
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:- current wave name
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:- resolved blocker state
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:5. Run the child issue's targeted verification commands exactly as required for that issue, and treat missing tooling as a blocking result rather than a cue to invent substitutes.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:6. Do not finish with "ready to close", "done", or a status-only comment. Stay responsible for GitHub closeout until it is either confirmed or blocked.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:    - GitHub closeout evidence: child issue closed, or the exact blocker that prevented closure
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:Do not let the implementation subagent expand scope, edit files owned by another in-flight task, or decide wave ordering on its own.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:If it reports any git landing action already happened, treat that as a blocking workflow violation rather than progress.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:- `refactor`: re-run the post-refactor targeted tests/commands, do only the remaining cleanup or closeout work, then hand off to review.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:3. After REFACTOR, add a comment with `Stage: refactor`, the rerun command/results, and whether the task is ready for review.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:1. After review fixes are complete and every required verification command that covers the child issue passed, send the assigned implementation subagent an explicit closeout turn instead of accepting a status-only finish.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:4. If a subagent leaves comments but does not close the child issue, treat that child issue as incomplete: keep the issue open and stop before the next wave.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:6. If any closeout step fails, the subagent must return a blocking result with the exact failed GitHub command or edit step. Do not declare success.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:After each wave's implementation finishes, review the changed files in subagents before closing any child issue.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:### Required review passes
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:   - if the wave changed 5 files or fewer, use 1 subagent for the whole wave
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:2. Launch three review subagents in parallel on the reviewed wave scope:
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:   - `code-reviewer` for correctness and conventions
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:   - `security-review` for security and unsafe defaults
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:   - `code-reviewer` for simplicity, duplication, and maintainability
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:3. Fix all blocking review findings before closing the affected child issues.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:4. If review-driven fixes change code, rerun the relevant review subagents on the affected scope before closure. Do not rely on the pre-fix review result.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:5. Record deferred non-blocking findings in the relevant issue comments or as follow-up notes to the user.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:The controller must define the review file list. Review subagents must not recompute or narrow their own scope.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:Normalize blocking review findings like this:
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:- `code-reviewer`: `Critical` and `Important` block closure.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:- `security-review`: `High` and `Medium` block closure.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:- `code-simplifier`: advisory by default; only treat a finding as blocking when it exposes a correctness risk, unsafe duplication, or a cross-task scope conflict.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:## Controller checkpoint before review
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:3. If the subagent changed unexpected files, failed to produce a clean RED/GREEN/REFACTOR chain, skipped or substituted a required verification command, or left verification unclear, stop and resolve that before review.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:Do not close issues or advance waves based on subagent summaries alone.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:For each completed child issue in the wave:
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:4. If a required verification command cannot run as written because a binary, framework CLI, generated artifact, environment dependency, credential, or service is unavailable, stop and surface that exact blocker. Report the command, the missing dependency/tool, and the stderr or setup gap. Do not mark the issue ready to close, and do not invent an alternative verification path unless the child issue itself already lists it or the human updates the verification plan explicitly.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:   - wave name
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:   - notable review findings and fixes
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:11. Once review is clear and every verification command that covers the child issue passed, send the assigned implementation subagent a closeout turn with explicit instructions to load `gh-cli`, close the child issue, and re-read GitHub to confirm closure.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:12. If that closeout turn returns only a comment, "ready to close", or another status-only note without the child issue actually closing on GitHub, treat it as a failed closeout. Keep the child issue open and stop before another wave starts.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:13. If the closeout turn claims success but a fresh GitHub read still shows the child issue open, stop and report the mismatch before another wave starts.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:If a child issue has multiple verification commands and they are independent, the controller may launch them in parallel verification subagents. If they share state or resources, run them sequentially through verification subagents.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:- If the required verification command is unavailable, fail closed and report the blocker.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:- stop before the next wave unless another already-launched task is still finishing
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:Use the parent task graph for wave order and blocker parsing, but do not make checkbox edits part of task completion.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:1. Never block child-issue completion on editing the parent task-graph checkbox.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:2. Never reopen, hold, or downgrade a closed child issue just because the parent line still shows `[ ]`.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:4. Mention stale parent checkbox state only when it helps explain why the task graph display looks outdated. Do not present that drift as a blocker.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:Before declaring any child issue complete or advancing to the next wave, the controller must also confirm that:
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:2. no blocking review finding remains unresolved for that issue's scope
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:4. no required verification command was skipped, replaced with a weaker proxy, or left blocked without being reported
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:5. Continue from the lowest-numbered wave that still has open work.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:- the current lowest wave is gated by a HITL issue
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:4. If landing work is out of scope or blocked, say explicitly that no commit, push, or PR action will be performed in this run.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:6. When closeout is still pending or blocked, use these exact phrases somewhere in the response:
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:8. Never mix pending and confirmed states. If GitHub has not yet been re-read to confirm closeout, do not say the issue is closed and do not say the next wave is ready.
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:Blocked / waiting:
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:- <review deferments, assumptions, or follow-up items>
/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot-iteration-8/SKILL.md:If all AFK child issues are closed and only HITL or no work remains, say that explicitly. If the user wants the finished work landed after that, tell them `prd-implement` stops here and they must start a separate `commit` or `commit-to-pr` request. Never invoke those skills from inside `prd-implement`.
```

</details>


---

<sub>⏱️ 11s</sub>

### 💬 Copilot

Based on the skill file's authoritative instructions, here is the controller's response:

---

**Hold on review and closure. #9402 is still running in parallel.**

Per the skill rules, "After every wave, wait for all implementation results, then run review, then verify, then update issue state." We launched #9401 and #9402 together in W3 because their file scopes don't overlap. Even though #9401 finished with a clean RED → GREEN → REFACTOR chain and passing tests, we must wait for #9402 to complete before starting review on either issue.

Starting review on #9401 now and closing it would violate the requirement to handle all parallel tasks in a wave together. Review runs after all implementation in the wave is done, not mid-wave.

**Next steps:**
1. Wait for #9402 to finish
2. Collect both results
3. Run all required review passes on both #9401 and #9402 together
4. Fix any blocking findings
5. Run verification on both
6. Close both child issues
7. Then advance to W4

#9401 is not ready to close until #9402 finishes and both pass review.

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
