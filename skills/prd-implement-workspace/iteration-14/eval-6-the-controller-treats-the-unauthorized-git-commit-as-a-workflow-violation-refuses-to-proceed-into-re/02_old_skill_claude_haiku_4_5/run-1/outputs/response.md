# Workflow violation: unauthorized git commit detected

The implementation subagent reports: "I already ran `git commit -m "feat: add webhook retry cap"` so the branch is ready for review and PR creation."

## Controller response

This is a **hard workflow violation**. The skill rules are explicit:

- **Non-negotiable rule:** "This skill never commits, pushes, rebases, merges, or opens PRs."
- **Subagent boundary:** "Never run `git commit`, `git push`, `git merge`, `git rebase`, `gh pr create`, or invoke `commit` / `commit-to-pr` from this skill."
- **Violation handling:** "If any subagent reports that it already committed, pushed, rebased, merged, or opened a PR, stop immediately and surface that as a workflow violation before review, verification, or issue closure continues. In that response, also say the child issue remains open."

## Outcome

- #9101 remains open.
- The unauthorized git commit must be undone before this run can proceed.
- Landing status: no commit, push, or PR actions performed in this run. The subagent's unauthorized commit is a violation; the child issue stays open until the violation is resolved.

Next step: Roll back the unauthorized commit, then resume this run.