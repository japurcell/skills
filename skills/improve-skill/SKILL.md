---
name: improve-skill
description: Mandatory at the end of a turn only when both 1 and 2 are true. 1.) a skill is activated or loaded 2.) a mistake is made, a failure occurs, a human provides steering or correction, a workaround is discovered, a code review reveals a gap in understanding, or a gap exists in a skill's instructions.
---

Identify and suggest **scoped**, minimal improvements to **targetable skills** using **durable learnings** discovered during the current session so that future agents are more accurate, efficient, and reliable.

Do not edit files. Only propose edits in the response.

## Identify Targetable Skills

A **targetable skill** is a skill that was activated or loaded in the current session.

Only target skills that were activated or loaded in the current session.

## Extract Durable Learnings

Extract only those learnings that are **likely to recur** and **actionable**. Use information already available in the current session, including conversation context, observed tool results, validation output, review comments, handoffs, progress files, or notes. Do not perform broad exploration just to find possible improvements.

**Prefer**:

- Any mistakes you made.
- Human steering and corrections.
- Review findings that reveal reusable rules.
- Execution friction only when it reveals a reusable rule: stale paths, repeated patch retries, coordination failures, validation reruns.
- Ways to avoid wasted tool calls, false failures, or timeouts.
- Non-default commands, flags, ordering, or required validation steps.
- Build, test, typecheck, lint, deploy, migration, or release rules.
- Generated-code rules.
- Known flaky-test causes and stable fixes.
- Coordination or stale-context signals that reveal a reusable workflow rule.

**Skip**:

- Obvious facts.
- One-off notes.
- Ticket/story IDs.
- Files merely opened during the session.
- Obvious README, package, or tree facts.
- Generic reminders such as “be careful”.
- Speculation.
- Broad summaries that lose the useful source detail.
- Knowledge discoverable by reading existing code.

## Formulate Scoped Edits

Suggested edits must be **scoped** to the targeted skill's instructions and purpose.

## Output

For each affected `SKILL.md` file, output a clear, actionable, **scoped**, and minimal set of edits.

Suggested output format:

```text
## SKILL.md: <skill name or path>

### Suggested edit
<minimal replacement, insertion, or deletion>

### Reason
<one-sentence explanation tied to the session learning>
```

If no durable, actionable, in-scope suggested edits are found, output:

```text
No skill improvements identified.
```

## Red Flags

- Editing any file.
- Suggesting edits that would:
  - introduce speculative rules not actually verified or encountered in the session
  - delete or weaken existing rules or exclusions
  - suppress tool errors or warning messages instead of structurally preventing them
- Targeting a skill with a learning that is outside of that skill's scope.

## Verification

- [ ] No files were edited.
- [ ] All targeted skills were activated or loaded in the current session.
- [ ] All suggested edits are minimal and surgical, with no unnecessary rewrites.
- [ ] No temporary blockers, one-time failures, or obvious facts were suggested.
- [ ] The output shows each affected `SKILL.md` file with corresponding edits that are within the scope of the skill.
