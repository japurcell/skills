---
name: handoff
description: Writes a resume-ready handoff in `.agents/scratchpad/` so another agent can continue without rereading the session. Use whenever work may pause, compact, reset, switch models, move to another agent, or when the user asks to save progress, preserve context, resume later, continue in a new session, or leave notes for whoever picks this up next.
---

# Handoff

## Overview

Capture one concise handoff another agent can resume from immediately. Preserve state, evidence, and the first safe next action without copying the whole chat.

## When to Use

- User asks to hand off, save progress, preserve context, resume later, continue in a new session, or leave notes for another agent.
- Context compaction, reset, session end, async transfer, or model switch may happen.
- Work stops mid-task and someone else must continue.
- Not for long transcripts or notes outside `.agents/scratchpad/`.

## Workflow

1. **Gather only active context**
   - Capture goal, status, next focus, exact next step, blockers, decisions, constraints, important files, commands/results, durable learnings, and the evidence that changed the plan.
   - Preserve high-signal review findings, corrected assumptions, rejected options, and unresolved risks when they affect what the next agent should trust or avoid.
   - When a specific code location matters, record it as `path:line` or `path:start-end` instead of naming only the file.
   - Record verification state explicitly: what was run or measured, what passed or failed, and what still needs rerunning.
   - Read only artifacts needed to summarize accurately. Do not reread the whole repo or paste full chat, logs, or diffs.

2. **Choose an allowed path**
   - Use user-provided focus as next-agent focus.
   - If the user names a path, honor it only when it stays under `.agents/scratchpad/`.
   - Otherwise, if one feature folder under `.agents/scratchpad/` clearly matches, write `<that-folder>/handoff.md`.
   - Otherwise write `.agents/scratchpad/handoff.md`.
   - If the requested path is invalid or multiple folders are plausible, fall back to the root handoff and note why.

3. **Write or update `handoff.md`**
   - Create `.agents/scratchpad/` if needed.
   - Update an existing handoff in place and remove stale or duplicate content.
   - Prefer compact bullets or short sections. Default shape when it fits: Goal, Status, Next focus, Next step, Decisions/constraints, Review findings/corrections, Relevant files/artifacts, Commands/results, Verification state, Errors/blockers, Durable learnings, Suggested skills, Briefing.
   - Include exact paths, commands, errors, verification state, and measured results when relevant.
   - Include code review or QA findings when they changed the diagnosis, scope, or next step.
   - Use `path:line` anchors for source, test, config, or docs references when the next agent should inspect a specific location.
   - Reference artifacts by path or URL instead of copying them.
   - Redact secrets and unnecessary personal data.
   - If file write fails, emit the handoff inline and explain the failure.

4. **Report outcome**
   - State the written path.
   - State whether it is `root-scoped` or `feature-scoped`.
   - State the single most important next step.

## Specific Techniques

### Keep it resume-ready

- Distinguish done, in-progress, and remaining work.
- Preserve what changed the plan: review findings, failed assumptions, rejected options, and why they were rejected.
- Prefer `path:line` pointers over vague file mentions when they help the next agent jump straight to the right code.
- If verification is incomplete, say exactly what ran, what happened, and what must be rerun.
- Preserve unresolved questions and rejected options.
- Make the first action obvious for a fresh, weaker model.
- Include suggested skills only when they materially help.

### Keep it small

- Prefer one page.
- Prefer dense evidence over long prose: one benchmark delta or failing assertion beats a pasted log.
- Omit empty sections.
- Never dump raw logs, screenshots, large diffs, or full chat unless essential.

## Common Rationalizations

| Rationalization | Reality |
| --- | --- |
| "Copying chat is safest." | Fresh agent needs state, not transcript noise. Summarize and point at artifacts. |
| "User asked for `docs/handoff.md`, so path rules can bend." | Never write outside `.agents/scratchpad/`; use an allowed path and say so. |
| "Existing handoff is close enough." | Update it in place; stale next steps waste the next session. |
| "Concise means skip blockers or constraints." | Remove noise, not decision-critical context. |
| "File names are enough." | When a specific code block matters, `path:line` saves rediscovery and avoids edits in the wrong place. |
| "Review findings already live in PR comments." | If review or QA changed the diagnosis, copy the actionable finding into the handoff so the next agent inherits the corrected plan. |

## Red Flags

- Writes outside `.agents/scratchpad/`.
- Pastes logs, diffs, or chat instead of referencing them.
- Leaves stale next steps, duplicate bullets, or unverifiable completion claims.
- Omits the review finding, rejected option, or failed assumption that changed the plan.
- Lists files without telling the next agent where to look.
- Omits blockers, constraints, or the first next action.

## Verification

- [ ] Output path is under `.agents/scratchpad/`
- [ ] Handoff is concise and free of stale or duplicate context
- [ ] Done, in-progress, and remaining work are distinguishable
- [ ] Exact next step is explicit
- [ ] Review findings, rejected options, or corrected assumptions are captured when they affect next work
- [ ] Specific code references use `path:line` when a location matters
- [ ] Relevant files or artifacts include why they matter
- [ ] Verification state says what ran or was measured and what is still pending
- [ ] Sensitive information is redacted
- [ ] Suggested skills appear only when useful
