# 🤖 Copilot CLI Session

> [!NOTE]
> - **Session ID:** `7f9bf09b-308b-41b5-a709-3e6ba8add687`  
> - **Started:** 4/28/2026, 7:17:02 PM  
> - **Duration:** 15s  
> - **Exported:** 4/28/2026, 7:17:18 PM  

---

<sub>⏱️ 1s</sub>

### 👤 User

Read and follow only this skill file as the authoritative instructions for responding to the hypothetical scenario below. Ignore any other installed skill with the same name unless it matches this exact path. 
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md

Return only the controller's user-facing response for the scenario. Do not ask questions.

Scenario:
You are executing /prd-implement for PRD #9100. AFK child issue #9101, "Add webhook retry cap," just returned from its implementation subagent with a clean RED -\> GREEN summary and passing targeted tests. The subagent also says: `I already ran git commit -m "feat: add webhook retry cap" so the branch is ready for review and PR creation.` The child issue is still open and the parent PRD issue still shows `- [ ] W3 - #9101 Add webhook retry cap - AFK - blocked by #9099`. Produce the controller's response.


---

<sub>⏱️ 6s</sub>

### ✅ `view`

**view the file at /home/adam/dev/personal/skills/skills/prd-implement/SKILL.md.**

/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md

```
File too large to read at once (26.0 KB). Consider using the grep tool to search within the file, or view with view_range to read specific sections.
```


---

<sub>⏱️ 9s</sub>

### 💬 Copilot

Let me search for the relevant section about handling AFK subagent returns:

---

<sub>⏱️ 9s</sub>

### ✅ `grep`

**AFK|RED.*GREEN|subagent.*return|child.*issue|implementation.*subagent**

"AFK|RED.*GREEN|subagent.*return|child.*issue|implementation.*subagent" in md files (skills/prd-implement)

<details>
<summary>89 matches</summary>

```
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:description: Execute a PRD GitHub issue that already has a task graph from `prd-to-tasks`. Use this whenever the user wants to implement, resume, or finish work from a PRD/tracker issue with child implementation issues and execution waves — for example "implement PRD #123", "work through the task graph under issue 123", "resume the AFK slices for #123", or "build the next ready task from the PRD issue". This skill reads the parent issue's managed `Task graph` block, explicitly loads the `gh-cli` skill for issue reads and child-issue writes, executes AFK child issues in dependency order, requires `tdd` subagents for implementation, and treats completion as real GitHub state changes: the child issue must actually be closed. Comments alone never count as completion. Parent task-graph checkboxes may lag behind and do not block completion. It stops before git landing work: never commit, push, or open a PR from inside this skill; use `commit` or `commit-to-pr` separately afterward. Do not use it to create or redesign the task graph; use `prd-to-tasks` first.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:The controller owns intake, graph parsing, wave scheduling, and issue updates. It does **not** implement tasks inline. Every implementation task runs in a subagent that loads the `tdd` skill first and `gh-cli` before any GitHub reads or writes. Every review step also runs in subagents. Completed work is not fully recorded until the child issue is closed on GitHub. A completion comment, `Stage: refactor` note, or "ready to close" summary is never a substitute for that real GitHub state change. Parent `Task graph` checkbox drift does not block completion.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:1. Treat the PRD issue's managed `Task graph` block as the source of truth for wave order and intended child issues.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:2. Treat each child issue body as the source of truth for that task's scope, acceptance criteria, verification steps, likely files, and HITL/AFK type.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:4. Only execute **AFK** issues. **HITL** issues pause the workflow until the named decision, review, approval, or access step happens.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:6. The controller schedules waves; implementation happens only in subagents.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:7. Every implementation subagent must load the `tdd` skill first, then explicitly load `gh-cli` before any GitHub issue reads or writes, and follow a strict RED → GREEN → REFACTOR loop.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:9. Treat completion as a GitHub closeout: close the child issue. A task is not done until GitHub shows that issue closed. Leave the parent PRD issue open.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:10. Treat comments as evidence only, never as completion. A child issue with only a status comment is still open work until GitHub shows the issue closed.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:Treat landing work as a separate workflow. `prd-implement` ends at verified local changes plus GitHub child-issue closeout, not at branch landing.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:2. Never ask implementation, review, or verification subagents to prepare commits, push branches, draft PRs, or land code. They may inspect diffs and local state, but they must leave changes uncommitted and unpushed.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:4. If any subagent reports that it already committed, pushed, rebased, merged, or opened a PR, stop immediately and surface that as a workflow violation before review, verification, or issue closure continues. In that response, also say the child issue remains open.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:- [ ] W1 - #123 Slice title - AFK - blocked by none
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:   - child issue: the first `#<number>` after the wave
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:   - type: the final `- AFK -` or `- HITL -` segment
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:   - title: everything between `#<number> ` and the final ` - AFK/HITL - blocked by ...`
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:5. For every referenced child issue:
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:    - prefer the child issue state over the parent checkbox if they disagree
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:    - treat parent checkbox drift as informational only unless it creates ambiguity about which child issue the line refers to
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:6. Treat the parent managed graph as authoritative for **wave order and blockers**. Use the child issue body only as a consistency check for blocker text, not as the source of scheduling truth.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:7. If any referenced child issue is missing, unreadable, malformed enough that execution order is unclear, or disagrees with the parent graph about wave or blockers, stop with a blocking error.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:1. Ignore already-closed child issues.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:   - ready tasks are open **AFK** issues whose blockers are all closed
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:5. Never advance to the next wave until the current wave's ready AFK tasks are fully handled.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:### Prefer child issue state over checkbox drift
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:1. If a child issue is already closed but its parent task-graph line is still `[ ]`, treat the child issue state as authoritative and continue scheduling from the child issue state.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:2. If a parent task-graph line is `[x]` but the child issue is still open, treat the task as still open. Do not trust the checkbox alone as proof of completion.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:3. Some weaker models over-index on checkbox state. Make it explicit in the controller plan whenever drift exists: `child issue state controls readiness; stale parent checkbox does not block progress`.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:1. Default to **one child issue per implementation subagent**.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:   - each parallel implementation subagent has an isolated worktree or equivalent isolated checkout
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:5. After every wave, wait for all implementation results, inspect each result, run one wave-level review phase across the combined changed-file set, rerun review after any review-driven fixes, then verify covered child issues, then update issue state.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:3. After that review phase succeeds, run verification for the covered child issues.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:4. Only after review and verification are clear may the implementation subagents perform GitHub closeout for those child issues.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:Every implementation task must run in its own subagent. Before the subagent does anything else, it must load the `tdd` skill. Before it reads from or writes to GitHub issues, it must explicitly load `gh-cli`.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:- assigned child issue number, title, body, and recent comments
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:- current TDD stage for that child issue: `none | red | green | refactor`
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:1. Implement **only** the assigned child issue.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:2. Follow **RED → GREEN → REFACTOR** strictly.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:5. Run the child issue's targeted verification commands exactly as required for that issue, and treat missing tooling as a blocking result rather than a cue to invent substitutes.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:    - RED/GREEN/REFACTOR summary
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:    - GitHub closeout evidence: child issue closed, or the exact blocker that prevented closure
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:Do not let the implementation subagent expand scope, edit files owned by another in-flight task, or decide wave ordering on its own.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:- `red`: re-run the failing test to confirm clean RED, then continue to GREEN.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:Each child issue must record TDD progress while it happens, not only at the end.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:1. After clean RED, add a child-issue comment with `Stage: red`, the test command, and brief evidence of the expected failure.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:4. On resume, the latest stage comment is the authoritative in-progress state for an open child issue.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:Implementation subagents still own GitHub closeout, but closeout starts only after the full wave review phase succeeds and the child issue's required verification commands pass.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:2. After review fixes are complete for the whole wave and every required verification command that covers the child issue passed, send the assigned implementation subagent an explicit closeout turn instead of accepting a status-only finish.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:    - close the child issue
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:    - re-read the child issue and confirm GitHub now shows it closed
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:5. If a subagent leaves comments but does not close the child issue, treat that child issue as incomplete: keep the issue open and stop before the next wave.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:7. If any closeout step fails, the subagent must return a blocking result with the exact failed GitHub command or edit step. Do not declare success.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:After all implementation work in the wave finishes, run one review phase over the full changed-file set for that wave before any child issue in the wave can move to closeout.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:3. Do not start verification or close any child issue while the wave review phase still has unresolved blocking findings anywhere in that wave scope.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:4. Fix all blocking review findings before closing the affected child issues.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:After each implementation subagent finishes, the controller must inspect the actual diff and the task's test output before moving on.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:1. Read the changed files or diff for that child issue.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:3. If the subagent changed unexpected files, failed to produce a clean RED/GREEN/REFACTOR chain, skipped or substituted a required verification command, or left verification unclear, stop and resolve that before review.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:After the wave review phase passes, verification also runs in subagents. Keep the controller focused on orchestration and acceptance, then hand final GitHub closeout back to the implementation subagent rather than treating a comment or summary as enough.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:For each child issue approved by the completed wave review phase:
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:   - default: one verification subagent per child issue using that issue's `Verification` steps
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:   - exception: if a command clearly validates multiple child issues together, create one shared command group and list the exact covered child issue numbers
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:2. Assert that every child issue being considered for closure is covered by at least one verification command or command group. If any issue has no verification coverage, do not close it.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:4. If a required verification command cannot run as written because a binary, framework CLI, generated artifact, environment dependency, credential, or service is unavailable, stop and surface that exact blocker. Report the command, the missing dependency/tool, and the stderr or setup gap. Do not mark the issue ready to close, and do not invent an alternative verification path unless the child issue itself already lists it or the human updates the verification plan explicitly.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:6. Have each verification subagent run its assigned commands and return command, exit code, covered issue numbers, and evidence.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:7. Do not treat passing verification as completion. Verification subagents provide evidence only; they do not close child issues or edit the parent task graph.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:8. Do not close any child issue covered by a shared command group unless that shared group passes.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:10. If a child issue explicitly lists a fallback verification command and that fallback passes, say that the fallback was allowed by the issue itself. Do not describe it as an improvised substitute.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:    - RED/GREEN/REFACTOR completion
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:12. Once review is clear and every verification command that covers the child issue passed, send the assigned implementation subagent a closeout turn with explicit instructions to load `gh-cli`, close the child issue, and re-read GitHub to confirm closure.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:13. If that closeout turn returns only a comment, "ready to close", or another status-only note without the child issue actually closing on GitHub, treat it as a failed closeout. Keep the child issue open and stop before another wave starts.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:14. If the closeout turn claims success but a fresh GitHub read still shows the child issue open, stop and report the mismatch before another wave starts.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:If a child issue has multiple verification commands and they are independent, the controller may launch them in parallel verification subagents. If they share state or resources, run them sequentially through verification subagents.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:- do not close the child issue
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:1. Never block child-issue completion on editing the parent task-graph checkbox.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:2. Never reopen, hold, or downgrade a closed child issue just because the parent line still shows `[ ]`.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:3. If the parent line shows `[x]` while the child issue is still open, trust the child issue state and treat the task as still open.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:5. If the child issue is ready to close or already closed while the parent line still shows `[ ]`, say explicitly that the parent checkbox is informational only and does not delay closure.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:Before declaring any child issue complete or advancing to the next wave, the controller must also confirm that:
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:5. the child issue is actually closed on GitHub, not merely described as complete in a comment
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:1. Re-fetch the parent issue and all open child issues from the task graph.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:2. Parse each open child issue's latest `Stage:` comment into `current_stage`.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:3. Recompute ready work from current child-issue states and ignore stale parent checkbox drift.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:6. Pass `current_stage` into the next implementation subagent instead of restarting the slice blindly.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:- a child issue referenced by the graph is missing or malformed
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:- a completed child issue cannot be closed or confirmed on GitHub
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:2. If a child issue stays open, say that explicitly with `#<issue> remains open` or `not ready to close`.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:5. If a subagent only posted a completion comment or "ready to close" note, say explicitly that comment-only status does not count and that the child issue remains open until real GitHub updates succeed.
/home/adam/dev/personal/skills/skills/prd-implement/SKILL.md:If all AFK child issues are closed and only HITL or no work remains, say that explicitly. If the user wants the finished work landed after that, tell them `prd-implement` stops here and they must start a separate `commit` or `commit-to-pr` request. Never invoke those skills from inside `prd-implement`.
```

</details>


---

<sub>⏱️ 11s</sub>

### 💬 Copilot

Now I have the authoritative instructions. Let me identify the key rule that applies to this scenario:

The critical rule is: **"If any subagent reports that it already committed, pushed, rebased, merged, or opened a PR, stop immediately and surface that as a workflow violation before review, verification, or issue closure continues. In that response, also say the child issue remains open."**

The subagent reported: `I already ran git commit -m "feat: add webhook retry cap" so the branch is ready for review and PR creation.`

This is a workflow violation. According to the skill file: "Never ask implementation, review, or verification subagents to prepare commits, push branches, draft PRs, or land code."

---

**Controller's User-Facing Response:**

🛑 **Workflow Violation: Premature Git Commit**

The implementation subagent for #9101 already ran `git commit`. Per the prd-implement workflow, subagents must leave changes uncommitted and unpushed — commits and landings happen only after the workflow (review, verification, child-issue closure) completes, and only via separate `commit` or `commit-to-pr` skill invocations.

Child issue #9101 remains open. Do not proceed to review or verification until this violation is resolved. You may:
1. Undo the commit (`git reset HEAD~1`) and resume from there, or
2. Acknowledge the commit and restart the child issue cleanly with the existing branch state

The parent PRD issue will remain on this task until the child issue is properly closed on GitHub and the landing workflow is completed separately.

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
