# Review finding prioritization in W5: partial closure decision

Current state:
- W5 contains #9501 "Cache account lookup" and #9502 "Invalidate account cache on role change"
- All implementation subagents finished; controller ran combined W5 review
- `code-reviewer`: no blocking issues for #9501's files
- `security-review`: Medium finding in #9502's files (blocking per skill rules)
- #9501's verification commands have already passed
- Proposal: close #9501 now while #9502 gets its review fix

## Controller assessment

The skill rules define review blocking scope:

- **Blocking findings:** "`security-review`: `High` and `Medium` block closure."
- **Wave review scope:** "Do not start verification or close any child issue while the wave review phase still has unresolved blocking findings anywhere in that wave scope."
- **Fix and rerun:** "If review-driven fixes change code, rerun the relevant review subagents on the affected scope before closure."

The Medium security finding is in #9502's scope only. #9501 has no blocking findings. However, both issues are part of the same W5 review phase.

The question is whether the controller can close #9501 (which has no blocking issues and passed verification) while #9502 (which has a blocking security finding) is still being fixed.

Per the skill: "Do not close any child issue covered by a shared command group unless that shared group passes." While these have separate verification commands, they are part of one wave review. The blocking finding is in a different issue's scope, so it does not block #9501 directly.

**However**, the rule also says the wave review phase must be clear before closure. The W5 review phase is not fully clear while a blocking finding exists anywhere in W5.

## Outcome

- #9501 remains open pending full W5 review completion.
- #9502 remains open with blocking security finding to fix.
- The controller must allow #9502's review fix, rerun the affected review subagents, confirm the finding is resolved, and achieve a clear W5 review state before closing any W5 child issue.
- Landing status: no commit, push, or PR actions performed in this run.

Next step: Address the Medium security finding in #9502, rerun affected review subagents, achieve clear W5 review, then proceed with verification and closure for ready issues.