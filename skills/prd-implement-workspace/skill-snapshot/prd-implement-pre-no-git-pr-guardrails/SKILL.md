---
name: prd-implement
description: Execute a PRD GitHub issue that already has a task graph from `prd-to-tasks`. Use this whenever the user wants to implement, resume, or finish work from a PRD/tracker issue with child implementation issues and execution waves — for example "implement PRD #123", "work through the task graph under issue 123", "resume the AFK slices for #123", or "build the next ready task from the PRD issue". This skill reads the parent issue's managed `Task graph` block, uses the `gh-cli` skill to retrieve and update the issue, executes AFK child issues in dependency order, keeps the parent task-graph checkboxes synchronized with closed child issues, requires `tdd` subagents for implementation, and runs review in separate subagents. Do not use it to create or redesign the task graph; use `prd-to-tasks` first.
---

# PRD Implement

Use this skill to turn a PRD issue graph into implemented code without letting the controller context balloon.

The controller owns intake, graph parsing, wave scheduling, and issue updates. It does **not** implement tasks inline. Every implementation task runs in a subagent that loads the `tdd` skill first. Every review step also runs in subagents. Completed work is not fully recorded until the child issue is closed **and** the matching parent `Task graph` line is checked off.

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
7. Every implementation subagent must load the `tdd` skill first and follow a strict RED → GREEN → REFACTOR loop.
8. Review always happens in subagents after each completed wave. Keep review scope to the files changed in that wave.
9. Treat completion as a paired GitHub update: close the child issue **and** check off the matching parent `Task graph` line. A task is not done until both are true. Leave the parent PRD issue open.
10. Do not commit, push, or open a PR unless the user explicitly asks for that after implementation is done.

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
    - record the exact parent task-graph line text for that child issue so the controller can later change only its checkbox
    - prefer the child issue state over the parent checkbox if they disagree, but treat disagreement as a state-sync problem that must be reconciled before advancing waves
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

### Reconcile task-graph state before new work

Before launching new implementation or verification work:

1. If a child issue is already closed but its parent task-graph line is still `[ ]`, synchronize the parent checkbox first. Do not treat the graph as up to date until that line becomes `[x]`.
2. If a parent task-graph line is `[x]` but the child issue is still open, stop and report the mismatch. Do not trust the checkbox alone as proof of completion.
3. Some weaker models forget this reconciliation step. Make it explicit in the controller plan whenever such a mismatch exists: `sync parent checkbox for #<issue> before starting the next wave`.

## Wave scheduling

Treat `[same wave]` as permission for parallelism, not a command.

Within the ready wave:

1. Default to **one child issue per implementation subagent**.
2. Launch tasks in parallel only when all are true:
   - their blockers are closed
   - their `Files likely touched` hints do not overlap **and** the controller's code reading does not reveal a shared file or module boundary
   - each parallel implementation subagent has an isolated worktree or equivalent isolated checkout
3. Treat `Files likely touched` as a scheduling hint, not a guarantee. If overlap is uncertain, or isolated worktrees are unavailable, serialize the tasks within the wave.
4. If one task in a parallel wave fails, let the already-running independent tasks finish, then stop before launching another wave.
5. After every wave, wait for all implementation results, then run review, then verify, then update issue state.

When reporting the plan for a wave, use explicit language such as:

```markdown
Wave W1

- Launch W1-A: #123 in a TDD subagent.
- Launch W1-B: #124 in a TDD subagent.
- Keep #125 sequential because it overlaps on `src/foo.ts`.
- Wait for W1 results before W2.
```

## Implementation subagents

Every implementation task must run in its own subagent. Before the subagent does anything else, it must load the `tdd` skill.

Pass the subagent only the context it needs:

- parent issue number and title
- assigned child issue number, title, body, and recent comments
- current wave name
- current TDD stage for that child issue: `none | red | green | refactor`
- resolved blocker state
- relevant repo/worktree/branch context
- likely file paths from `Files likely touched`, marked explicitly as hints rather than hard limits
- acceptance criteria and verification commands
- any directly relevant source files the controller already read

Tell the subagent to:

1. Implement **only** the assigned child issue.
2. Follow **RED → GREEN → REFACTOR** strictly.
3. Keep slices thin and avoid broad cleanup.
4. Run the child issue's targeted verification commands exactly as required for that issue, and treat missing tooling as a blocking result rather than a cue to invent substitutes.
5. Return:
   - RED/GREEN/REFACTOR summary
   - files changed
   - commands run and outcomes
   - remaining risks or deferments
   - whether the task is ready to close

Do not let the implementation subagent expand scope, edit files owned by another in-flight task, or decide wave ordering on its own.
If it must touch a file that was not listed in `Files likely touched`, it should stop and escalate that need back to the controller instead of silently broadening scope.

### Resume by current stage

Implementation subagents must resume from the passed `current_stage` like this:

- `none`: start with RED.
- `red`: re-run the failing test to confirm clean RED, then continue to GREEN.
- `green`: re-run the passing proof for the targeted test or command, then continue to REFACTOR.
- `refactor`: re-run the post-refactor targeted tests/commands, do only the remaining cleanup or closeout work, then hand off to review.

### Clean RED rule

A RED step counts only when the new or updated test fails for the intended missing behavior. Syntax errors in the test, broken imports caused by the test setup itself, or invalid fixtures do **not** count as a clean RED.

### Durable TDD progress

Each child issue must record TDD progress while it happens, not only at the end.

1. After clean RED, add a child-issue comment with `Stage: red`, the test command, and brief evidence of the expected failure.
2. After GREEN, add a comment with `Stage: green`, the implementation command/test result, and the files changed.
3. After REFACTOR, add a comment with `Stage: refactor`, the rerun command/results, and whether the task is ready for review.
4. On resume, the latest stage comment is the authoritative in-progress state for an open child issue.

## Review subagents

After each wave's implementation finishes, review the changed files in subagents before closing any child issue.

### Required review passes

1. Launch `code-simplifier` subagents first:
   - if the wave changed 5 files or fewer, use 1 subagent for the whole wave
   - otherwise partition files into non-overlapping groups and use one subagent per group
2. Launch three review subagents in parallel on the reviewed wave scope:
   - `code-reviewer` for correctness and conventions
   - `security-review` for security and unsafe defaults
   - `code-reviewer` for simplicity, duplication, and maintainability
3. Fix all blocking review findings before closing the affected child issues.
4. If review-driven fixes change code, rerun the relevant review subagents on the affected scope before closure. Do not rely on the pre-fix review result.
5. Record deferred non-blocking findings in the relevant issue comments or as follow-up notes to the user.

The controller must define the review file list. Review subagents must not recompute or narrow their own scope.

Normalize blocking review findings like this:

- `code-reviewer`: `Critical` and `Important` block closure.
- `security-review`: `High` and `Medium` block closure.
- `code-simplifier`: advisory by default; only treat a finding as blocking when it exposes a correctness risk, unsafe duplication, or a cross-task scope conflict.

## Controller checkpoint before review

After each implementation subagent finishes, the controller must inspect the actual diff and the task's test output before moving on.

1. Read the changed files or diff for that child issue.
2. Read the reported test/command output, or rerun the targeted command if the evidence is incomplete.
3. If the subagent changed unexpected files, failed to produce a clean RED/GREEN/REFACTOR chain, skipped or substituted a required verification command, or left verification unclear, stop and resolve that before review.

Do not close issues or advance waves based on subagent summaries alone.

## Verification subagents and issue updates

Verification also runs in subagents. Keep the controller focused on orchestration and issue state.

For each completed child issue in the wave:

1. Build a controller-authored verification plan before launching verification subagents:
   - default: one verification subagent per child issue using that issue's `Verification` steps
   - exception: if a command clearly validates multiple child issues together, create one shared command group and list the exact covered child issue numbers
2. Assert that every child issue being considered for closure is covered by at least one verification command or command group. If any issue has no verification coverage, do not close it.
3. Treat each listed verification step as the required command contract for that issue. If the issue says to use a framework or project CLI, run that CLI; do not silently swap in static analysis, code reading, lint-only checks, type-check-only checks, or some other weaker proxy just because the intended verification tool is missing or inconvenient.
4. If a required verification command cannot run as written because a binary, framework CLI, generated artifact, environment dependency, credential, or service is unavailable, stop and surface that exact blocker. Report the command, the missing dependency/tool, and the stderr or setup gap. Do not mark the issue ready to close, and do not invent an alternative verification path unless the child issue itself already lists it or the human updates the verification plan explicitly.
5. Launch verification subagents from that plan.
6. Have each verification subagent run its assigned commands and return command, exit code, covered issue numbers, and evidence.
7. Do not close any child issue covered by a shared command group unless that shared group passes.
8. Confirm the acceptance criteria are satisfied.
9. Add a concise progress comment that captures:
   - wave name
   - RED/GREEN/REFACTOR completion
   - changed files
   - verification evidence
   - notable review findings and fixes
10. Perform the completion sync only when every verification command that covers the child issue passed:
    - close the child issue
    - re-fetch the latest parent issue body immediately before editing it
    - locate the exact managed task-graph line for that child issue
    - replace only the leading checkbox on that one line from `[ ]` to `[x]`
    - preserve the rest of the line, all other task-graph lines, and all non-managed issue content verbatim
    - write the updated parent issue body back to GitHub
    - re-fetch the parent issue and verify that the line now shows `[x]`
11. If the child issue closed but the parent checkbox update failed, or the parent checkbox changed but the child issue is still open, stop and report the mismatch before another wave starts.

If a child issue has multiple verification commands and they are independent, the controller may launch them in parallel verification subagents. If they share state or resources, run them sequentially through verification subagents.

Verification subagents must preserve verification strength:

- If the required verification command is unavailable, fail closed and report the blocker.
- Do not replace framework-native verification with static analysis, source inspection, or generic "looks correct" reasoning.
- Do not downgrade `npm run verify:web`, `bin/rails test`, `cargo test`, `nx test`, framework codegen validators, or similar required commands to unrelated checks unless the issue explicitly says those checks are acceptable alternatives.

If verification is missing, ambiguous, or failing:

- do not close the child issue
- report the exact gap
- stop before the next wave unless another already-launched task is still finishing

### Parent task-graph checkbox updates

Parent task-graph edits must be surgical. The controller may update checkbox state inside the managed block, but it must not rewrite the task graph freehand.

1. Use the `gh-cli` skill explicitly for the parent issue edit as well as issue reads. Weaker models often remember the read but forget the write.
2. Match the child issue by its exact managed line from the latest parent body, not by a loose substring.
3. Only change this:

```markdown
- [ ] W2 - #124 Another slice - AFK - blocked by #123
+ [x] W2 - #124 Another slice - AFK - blocked by #123
```

4. Do **not** reorder lines, rename titles, rewrite blockers, regenerate the whole block, or touch text outside the managed section.
5. If the exact line cannot be found uniquely in the latest parent issue body, stop and report that the task graph drifted. Do not guess.
6. After the edit, re-read the parent issue and confirm the checkbox is now `[x]` before declaring the task complete.

## Acceptance confirmation

Before declaring any child issue complete or advancing to the next wave, the controller must also confirm that:

1. the acceptance criteria are satisfied
2. no blocking review finding remains unresolved for that issue's scope
3. the latest issue comments make the TDD stage history and verification outcome visible from GitHub alone
4. no required verification command was skipped, replaced with a weaker proxy, or left blocked without being reported
5. the matching parent task-graph line is checked `[x]` and still matches the same wave, title, type, and blocker text except for the checkbox change

## Resume behavior

This skill is resumable from GitHub for queue state and TDD history, but not for missing local code.

On resume:

1. Re-fetch the parent issue and all open child issues from the task graph.
2. Parse each open child issue's latest `Stage:` comment into `current_stage`.
3. Recompute ready work from current issue states and reconcile any closed-child / unchecked-parent mismatches before launching new work.
4. Ignore tasks that are already closed.
5. Continue from the lowest-numbered wave that still has open work.
6. Pass `current_stage` into the next implementation subagent instead of restarting the slice blindly.
7. Resume from `green` or `refactor` only when the corresponding local code and test state are still present in the working tree.
8. If the local state for an open issue is missing or disagrees with the latest GitHub `Stage:` history, do not trust the recorded stage. Either restart that issue from RED deliberately or stop and ask the user how to recover the lost work.

Do not rely on local scratch files for queue state.

## Stop conditions

Stop and report clearly when any of these happens:

- the parent issue has no valid `prd-to-tasks` task graph
- a child issue referenced by the graph is missing or malformed
- the current lowest wave is gated by a HITL issue
- repository or GitHub authentication is ambiguous or broken
- a required verification command or framework CLI is unavailable and no human-approved replacement path exists
- an implementation or verification failure remains unresolved
- a completed child issue cannot be synchronized back to the parent task graph safely
- unrelated local changes create a conflict with the assigned task scope

## Final response

Always end with a concise execution summary in this shape:

```markdown
PRD execution status for #<parent>

Completed this run:

1. #<issue> <title>

Blocked / waiting:

1. #<issue> <title> - <reason>

Next ready work:

- W<n>: #<issue> <title>

Notes:

- <review deferments, assumptions, or follow-up items>
```

If all AFK child issues are closed and only HITL or no work remains, say that explicitly. If the user wants the finished work landed after that, hand off to `commit` or `commit-to-pr`.
