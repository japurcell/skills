# Comment-Only Completion Rejected: Real GitHub Closeout Required

**Issue #9301 is not complete.** The implementation subagent reported posting status comments, but comments do not count as task completion.

## The Problem

The subagent said: _"I commented on child issue #9301 that the task is done, and I left a note on the parent PRD issue that W2 is complete."_

Per the skill rules:

- Line 10: "A completion comment, `Stage: refactor` note, or 'ready to close' summary is never a substitute for those real GitHub state changes."
- Line 30: "Treat comments as evidence only, never as completion. A child issue with only a status comment is still open work until GitHub shows the issue closed and the parent line checked `[x]`."
- Line 191–192: "A `Stage: refactor` comment, 'done' comment, or 'task complete' comment is progress evidence only. It never counts as completion. If a subagent leaves comments but does not close the child issue and sync the parent checkbox, treat that child issue as incomplete: keep the issue open, keep the parent line `[ ]`, and stop before the next wave."

**GitHub still confirms this:** The parent PRD issue still shows `- [ ] W2 - #9301 Ship usage quota banner`, and child issue #9301 remains open.

## What Must Happen Now

Because review and verification passed, the implementation subagent must send an explicit closeout turn. In that turn, the subagent will:

1. Load `gh-cli` explicitly
2. Close child issue #9301 via `gh issue close #9301`
3. Re-fetch the parent PRD issue body
4. Locate the exact task-graph line: `- [ ] W2 - #9301 Ship usage quota banner - AFK - blocked by #9298`
5. Replace the leading checkbox to: `- [x] W2 - #9301 Ship usage quota banner - AFK - blocked by #9298`
6. Write the updated parent body back to GitHub
7. Re-read both issues and confirm both state changes succeeded

Comments are evidence of progress, but they are not completion. **Only real GitHub state changes count.**

---

## Current State

- **#9301 remains open.** Comments were posted but the issue was not closed.
- **Parent task-graph line for #9301 remains `[ ]`.** The checkbox was not updated in the parent PRD issue body.
- **Parent PRD issue remains open** because W2 is incomplete.
- **No next wave ready.** W2 work cannot advance until #9301 is actually closed and the parent line is actually checked.

Sending subagent a closeout turn now to complete the real GitHub updates.
