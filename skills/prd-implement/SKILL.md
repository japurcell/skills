---
name: prd-implement
description: Execute a PRD GitHub issue that already has a task graph from `prd-to-tasks`. Use this whenever the user wants to implement, resume, or finish work from a PRD/tracker issue with child implementation issues and execution waves — for example "implement PRD #123", "work through the task graph under issue 123", "resume the AFK slices for #123", or "build the next ready task from the PRD issue". This skill reads the parent issue's managed `Task graph` block, explicitly loads the `gh-cli` skill for issue reads and child-issue writes, executes AFK child issues in dependency order, requires `tdd` subagents for implementation, and treats completion as real GitHub state changes: the child issue must actually be closed. Comments alone never count as completion. Parent task-graph checkboxes may lag behind and do not block completion. It stops before git landing work: never commit, push, or open a PR from inside this skill; use `commit` or `commit-to-pr` separately afterward. Do not use it to create or redesign the task graph; use `prd-to-tasks` first.
disable-model-invocation: true
---

# PRD Implement

Use this skill as the controller for a PRD issue graph. The controller reads GitHub state, schedules waves, delegates implementation/review/verification, and updates child issues. It does not implement slices inline and it never lands code.

If the user gives a complete hypothetical state and asks for the controller's response or issue-handling outcome, apply these rules directly to the supplied facts and produce the final response. Do not invent GitHub reads for a dry-run prompt.

For dry-run/controller-response prompts, answer in the final response template from this skill, not with analysis sections like "Scenario", "Policy violation", or quoted rule text. The user is testing the controller outcome, so the useful output is the issue state, blocker, next ready work, landing status, and notes in the required section order.

Before sending any dry-run or final response, run this quick phrase checklist and include the applicable exact phrases:

- Required verification unavailable with no issue-defined fallback: name the command/tool, say the proposed substitute is insufficient, say `#<issue> remains open.`, and stop before the next wave.
- Explicit fallback passed: say the original command could not run, the fallback command passed, the fallback was allowed by the issue itself, parent task-graph checkbox updates are not required, and the child needs explicit GitHub closeout before it is complete.
- Closed child with stale parent checkbox: say `#<issue> is closed.`, child issue state is authoritative, checkbox sync is not required, the next wave/issue is ready, and `parent PRD issue remains open.`
- User asks for commit/push/PR: say landing work remains out of scope, no commit, push, or PR action will be performed in this run, changes remain local-only/uncommitted, and `commit` or `commit-to-pr` requires a separate follow-up request.
- Unauthorized landing action already happened: call it an unauthorized/out-of-scope landing action or workflow violation, stop before review/verification/closeout/PR creation, say `#<issue> remains open.`, and say you will not push, open a PR, or treat the commit as permission to continue.
- Comment-only completion: say comments or status notes do not count as task completion, require `gh-cli`-driven closeout or equivalent real GitHub state change, say `#<issue> remains open.`, and stop before the next wave.
- In-flight same-wave task: say review cannot start until all implementation subagents in that wave finish or the named pending issue returns, closeout must wait for wave-level review, the current child remains open, and the next wave remains blocked.
- Blocking wave review finding: say the wave review phase is incomplete, fix the blocking finding and rerun review on the affected scope before closing any child in the wave, keep all affected child issues open, and stop before additional closeout or another wave.

## Controller loop

1. **Resolve input.** Get the parent PRD issue number or URL and repository. If either is ambiguous, ask before doing anything else.
2. **Load GitHub context.** Explicitly invoke `gh-cli`, then read the parent issue and relevant comments.
3. **Parse the task graph.** Use the parent issue's managed `Task graph` block for wave order and blockers. If no valid `prd-to-tasks` graph exists, stop and tell the user to run `prd-to-tasks` first.
4. **Read child issues.** For each referenced child issue, fetch title, body, state, recent comments, type, acceptance criteria, verification steps, and likely files.
5. **Compute readiness from GitHub state.** Child issue state controls completion. Stale parent checkbox state is informational only.
6. **Select the lowest open wave.** Execute only ready AFK issues whose blockers are closed. HITL issues pause the workflow for human action.
7. **Launch implementation subagents.** One child issue per implementation subagent. Each implementation subagent loads `tdd` first and `gh-cli` before any issue read/write.
8. **Wait for the wave.** Wait for all implementation subagents launched for the current wave before review starts.
9. **Run the controller checkpoint.** Inspect each diff and verification evidence. Stop before review if any required command was skipped, substituted, or unclear.
10. **Review the whole wave.** Run one wave-level review phase over the combined changed-file set. Resolve blocking findings and rerun affected review before verification or closeout.
11. **Verify exactly.** Run the child issue's required verification commands, or shared command groups that explicitly cover listed issues. Missing tools block closure unless the child issue itself listed a fallback.
12. **Close child issues for real.** Verification is evidence, not completion. Send the implementation subagent a closeout turn that loads `gh-cli`, closes the child issue, and re-reads GitHub to confirm it is closed.
13. **Report and stop or continue.** Never advance past a blocked lowest wave. Leave the parent PRD issue open. Never commit, push, or open a PR from this skill.

## Non-negotiable invariants

- The parent managed graph is authoritative for wave order and blockers.
- The child issue body is authoritative for scope, acceptance criteria, verification, likely files, and AFK/HITL intent.
- Do not invent tasks, waves, or dependencies. If the graph is wrong, stop and say what must change in GitHub.
- Only AFK child issues are implemented by agents. HITL issues remain waiting for the named human decision, approval, access, or review.
- Never skip a lower-numbered open wave to start a later wave.
- Implementation happens only in subagents; the controller orchestrates and checks.
- Comments or status notes do not count as task completion. A child issue is complete only when GitHub shows it closed.
- Parent task-graph checkbox updates are not required for task completion. A closed child issue is complete even if the parent line still shows `[ ]`.
- Landing work remains out of scope. Do not commit, push, merge, rebase, open PRs, or invoke `commit` / `commit-to-pr`.

## Git and PR boundary

`prd-implement` ends at verified local changes plus GitHub child-issue closeout. Landing work is a separate workflow.

1. Never run `git commit`, `git push`, `git merge`, `git rebase`, `gh pr create`, or invoke landing skills.
2. Never ask implementation, review, or verification subagents to prepare commits, push branches, draft PRs, or land code.
3. If the user's request combines implementation with PR creation, do only PRD implementation. In the final response, say no commit, push, or PR will be performed in this run and that the user must make a separate `commit` or `commit-to-pr` request after this skill finishes.
4. If any subagent already committed, pushed, rebased, merged, opened a PR, or invoked a landing skill, stop immediately. Treat it as an unauthorized, out-of-scope landing action; do not proceed to review, verification, issue closure, or PR creation. Say the child issue remains open.
5. When the user mentions commits, branches, pushes, or PRs, restate: `Landing work remains out of scope for this run.`

## Graph parsing and readiness

Read the managed block written by `prd-to-tasks`:

```markdown
<!-- prd-to-tasks:start -->

## Task graph

- [ ] W1 - #123 Slice title - AFK - blocked by none
- [ ] W2 - #124 Another slice - HITL - blocked by #123
<!-- prd-to-tasks:end -->
```

If the markers are missing, fall back to a plain `## Task graph` section only when it clearly uses the same line format. Parse each line by anchored fields:

- checkbox: leading `[ ]` or `[x]`
- wave: `W<n>`
- child issue: first `#<number>` after the wave
- title: text between the child issue number and final type segment
- type: final `- AFK -` or `- HITL -`
- blockers: text after final `blocked by `

For every child issue:

1. Fetch title, body, state, and recent comments.
2. Extract `Type`, `Acceptance criteria`, `Verification`, and `Files likely touched`.
3. Prefer child issue state over parent checkbox drift:
   - child closed + parent `[ ]`: treat the child as complete; stale parent checkbox does not block readiness.
   - parent `[x]` + child open: treat the child as open; checkbox sync is not required and the checkbox alone is not proof.
4. Use child issue bodies as consistency checks, but use the parent graph for wave order and blockers.
5. Stop if a referenced child issue is missing, unreadable, malformed enough to make ordering unclear, or conflicts with the graph about wave or blockers.

To choose work, ignore already-closed children, find the lowest-numbered wave with open work, then run only open AFK issues whose blockers are closed. If the lowest open wave contains only HITL or blocked tasks, report the issue numbers and required human action.

## Wave scheduling

Treat same-wave placement as permission for parallelism, not a command.

- Default to one child issue per implementation subagent.
- Launch same-wave tasks in parallel only when blockers are closed, likely files do not overlap, controller code reading does not reveal a shared module boundary, and isolated worktrees or equivalent checkouts are available.
- If overlap or isolation is uncertain, serialize within the wave.
- If one parallel task fails, let already-running independent tasks finish, then stop before another wave.
- Review, verification, and closeout are wave-level gates: do not close one child or start the next wave while another child in the current wave is still implementing or blocked by review.

Lifecycle for each wave:

1. Finish all implementation work launched for the current wave.
2. Run the controller checkpoint.
3. Run one wave-level review phase across the combined changed-file set.
4. Fix and rerun review for blocking findings.
5. Verify covered child issues.
6. Send explicit closeout turns for child issues whose review and verification are clear.

## Implementation subagent contract

Each implementation task runs in its own subagent. The subagent must load `tdd` before anything else and load `gh-cli` before issue reads, comments, or closure.

Pass only the needed context:

- parent issue number/title
- assigned child issue number/title/body/recent comments
- current wave
- current TDD stage: `none | red | green | refactor`
- resolved blocker state
- repo/worktree/branch context
- likely file paths, explicitly as hints
- acceptance criteria and verification commands
- relevant source files already read by the controller

Tell the subagent to:

1. Implement only the assigned child issue.
2. Follow RED -> GREEN -> REFACTOR. A clean RED means the new or changed test fails for the intended missing behavior, not for syntax/import/fixture mistakes.
3. Keep the slice thin; avoid broad cleanup.
4. Treat required verification commands as contracts. Missing tooling is a blocking result, not a reason to invent substitutes.
5. Record durable TDD progress while it happens:
   - `Stage: red` comment after clean RED
   - `Stage: green` comment after implementation passes targeted proof
   - `Stage: refactor` comment after cleanup and rerun proof
6. Return the RED/GREEN/REFACTOR summary, files changed, commands and outcomes, GitHub closeout evidence or blocker, and remaining risks.
7. Never commit, push, rebase, merge, open a PR, invoke landing skills, or broaden scope without controller approval.

On resume, pass the current stage from the latest `Stage:` comment:

- `none`: start with RED.
- `red`: re-run the failing test to confirm clean RED, then continue.
- `green`: re-run the passing proof, then refactor.
- `refactor`: re-run post-refactor targeted tests/commands, then hand off for review/closeout.

Resume from `green` or `refactor` only when matching local code and test state still exist. If local state is missing or disagrees with GitHub stage history, restart from RED deliberately or stop and ask how to recover.

## Controller checkpoint before review

Before review, inspect the real output of every implementation subagent:

1. Read the changed files or diff.
2. Read the reported test/command output, or rerun targeted commands when evidence is incomplete.
3. Stop before review if the subagent changed unexpected files, lacked a clean RED/GREEN/REFACTOR chain, skipped or substituted a required verification command, left verification unclear, or performed any landing action.

Do not close issues or advance waves based on summaries alone.

## Review phase

After all implementation work in the wave finishes, review the full wave scope before any child issue moves to verification or closeout.

1. Run `code-simplifier` first:
   - 5 files or fewer: one subagent for the whole wave
   - more than 5 files: partition into non-overlapping groups
2. Run review subagents in parallel on the controller-defined file list:
   - `code-reviewer` for correctness and conventions
   - `security-review` for security and unsafe defaults
   - `code-reviewer` for simplicity, duplication, and maintainability
3. Blocking findings:
   - `code-reviewer`: Critical and Important
   - `security-review`: High and Medium
   - `code-simplifier`: advisory unless it exposes correctness risk, unsafe duplication, or cross-task scope conflict
4. If any blocking finding remains, the wave review phase is incomplete. Fix it, then rerun review on the affected scope before verifying or closing any child in that wave.
5. Review subagents inspect code only; they do not commit, push, or prepare PR text.

## Verification and closeout

Verification protects the user's acceptance criteria. Preserve its strength.

1. Build a controller-authored verification plan after wave review passes:
   - default: one verification subagent per child issue using that issue's `Verification` steps
   - shared command group: allowed only when a command clearly validates multiple child issues; list the exact covered issue numbers
2. Every child considered for closure must be covered by at least one required command or command group.
3. Run the listed command contract. If the issue says to use a framework/project CLI, run that CLI.
4. Do not replace framework-native verification with static analysis, source inspection, lint-only checks, type-check-only checks, diff inspection, or "looks correct" reasoning.
5. If a required command cannot run because a binary, framework CLI, artifact, dependency, credential, or service is unavailable, fail closed. Report the exact command, missing tool/dependency, and stderr/setup gap. Do not close the child issue.
6. If the child issue explicitly lists a fallback command and that fallback passes, say the fallback was allowed by the issue itself. Do not describe it as an improvised substitute.
7. Do not close any child issue covered by a shared command group unless that shared group passes. If it fails, every covered child remains open.
8. Verification subagents return command, exit code, covered issues, and evidence. They do not close issues or edit the parent task graph.
9. Once review and verification are clear, add a concise progress comment with wave, TDD stages, changed files, verification evidence, and review findings/fixes.
10. Send the assigned implementation subagent an explicit `gh-cli`-driven closeout turn: close the child issue and re-read it to confirm GitHub shows it closed.
11. If closeout returns only a comment, "done", "ready to close", or another status note, reject comment-only completion. The child issue remains open until real GitHub state changes succeed.
12. Until a fresh GitHub read confirms closure, report only the current state. Do not claim the issue is closed or the next wave is ready.

## Acceptance gate

Before declaring any child issue complete or advancing waves, confirm:

- acceptance criteria are satisfied
- no blocking review finding remains
- TDD stage history and verification outcome are visible from GitHub comments
- no required verification command was skipped, replaced by a weaker proxy, or left blocked without being reported
- the child issue is actually closed on GitHub
- no commit, push, merge, rebase, landing skill, or PR creation happened during this run

## Resume behavior

Queue state and progress come from GitHub, not local scratch files.

1. Re-fetch the parent issue and all task-graph child issues.
2. Ignore closed child issues even when parent checkboxes are stale.
3. Parse open child issue comments for latest `Stage:` history.
4. Recompute readiness from current child issue states.
5. Continue from the lowest-numbered wave with open work.
6. Pass `current_stage` into implementation subagents instead of restarting blindly.
7. If local code is missing for a staged open issue, restart deliberately from RED or stop and ask how to recover.

## Stop conditions

Stop and report clearly when:

- the parent issue lacks a valid `prd-to-tasks` graph
- a graph child issue is missing or malformed
- the lowest open wave is gated by HITL or unresolved blockers
- repository or GitHub authentication is ambiguous or broken
- a required verification command or framework CLI is unavailable and no issue-defined or human-approved fallback exists
- implementation, review, verification, or closeout remains blocked
- a completed child issue cannot be closed or confirmed on GitHub
- unrelated local changes conflict with the assigned scope
- any landing action happened during this run

## Final response rules

Some weaker models do the right work but omit state the user still needs. Make safety-critical state explicit:

- If a child issue stays open, say `#<issue> remains open.` or `not ready to close`.
- If a child issue is confirmed closed, say `#<issue> is closed.`
- If the parent PRD issue stays open, say `parent PRD issue remains open.`
- If parent checkbox drift is relevant, say `parent task-graph checkbox state is informational only` or `parent task-graph checkbox updates are not required`.
- If comments/status notes were the only completion action, say comments do not count as task completion and real GitHub updates are still required.
- If closeout is pending, blocked, or unconfirmed, do not say the issue is closed and do not say the next wave is ready.
- If landing work is requested or mentioned, say no commit, push, or PR action will be performed in this run.

End with this section order:

```markdown
PRD execution status for #<parent>

Completed this run:

1. #<issue> <title>

Blocked / waiting:

1. #<issue> <title> - <reason>

Next ready work:

- W<n>: #<issue> <title>

Landing status:

- Local changes only; no commit, push, or PR actions performed in this run.

Notes:

- <review deferments, assumptions, or follow-up items>
```

If a section has no items, write `- none`. If all AFK child issues are closed and only HITL or no work remains, say so explicitly. If the user wants the finished work landed after that, tell them `prd-implement` stops here and they must start a separate `commit` or `commit-to-pr` request.
