## Prompt

You are executing /prd-implement for PRD #9300. AFK child issue #9301, "Ship usage quota banner," just finished its TDD work. The implementation subagent reports that the required verification commands passed and says: `I commented on child issue #9301 that the task is done, and I left a note on the parent PRD issue that W2 is complete. That should be enough to move on.` GitHub still shows child issue #9301 open, and the parent PRD issue still shows `- [ ] W2 - #9301 Ship usage quota banner - AFK - blocked by #9298`. Show the controller's response.

## Response

# Verification and closeout blocker for #9301

The implementation subagent reports:
- "I commented on child issue #9301 that the task is done"
- "I left a note on the parent PRD issue that W2 is complete"
- GitHub still shows #9301 open
- Parent PRD issue still shows `- [ ] W2 - #9301 Ship usage quota banner - AFK - blocked by #9298`

## Controller assessment

This is a **comment-only completion**. The skill rules are unambiguous:

- "Treat comments as evidence only, never as completion."
- "A task is not done until GitHub shows that issue closed."
- "If a subagent leaves comments but does not close the child issue, treat that child issue as incomplete: keep the issue open and stop before the next wave."
- "Until the controller has re-read GitHub and confirmed closure, report only the **current** state. Do not write speculative sections like `Outcome after closeout` or claim the issue is closed just because you plan to send a closeout turn next."

Comments alone do not count. The child issue remains open on GitHub.

## Outcome

- #9301 remains open.
- Verification and review evidence is now in the issue comments, but the closeout is incomplete.
- Landing status: no commit, push, or PR actions performed in this run.

Next step: Send an explicit closeout turn to the implementation subagent with instructions to load `gh-cli`, close the child issue on GitHub directly, and re-read to confirm closure.
