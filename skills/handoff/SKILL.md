---
name: handoff
description: MANDATORY first action whenever user, task, spec, PRD, or workflow mentions, reads, touches, or updates 'handoff', 'handoff.md', or any path ending in 'handoff.md'. Also trigger immediately on resume, continue, pick up, next step, checkpoint, or transfer context. Load before any tool call touching handoff files; update handoff whenever scope, status, blockers, or next step changes, and before stopping.
---

# Handoff

## Overview

Capture one concise handoff another agent can resume from immediately. Preserve state, evidence, and the first safe next action without copying the whole chat.

## Workflow

1. **Gather only active context**
   - Reconcile the inherited handoff with the latest user direction, current notes, changed files, and verification results. Treat an existing handoff as a prior snapshot; current evidence determines scope, status, and what remains.
   - At resume, scope change, milestone completion, and before stopping, replace stale active status and next steps. Continue an inherited next step only when it is still current and authorized; otherwise record the current safe next action.
   - Keep the current goal, status, next focus, exact next step, blockers, constraints, authorization limits, recovery path, important files, and verification state inline.
   - Keep a durable lesson inline when it changes the current decision or prevents a repeated mistake. Before removing unique history, reuse a retained artifact when it preserves the evidence. If the old handoff is the only copy, save the unique evidence to a clearly labeled sibling history file first, then verify the file exists and contains it. Point to the retained artifact, never back to the handoff being replaced. If preservation fails, keep the needed evidence inline and report the limitation.
   - Do not keep a superseded step inline merely to say it is obsolete. Preserve its evidence behind a historical reference when needed; retain an inline lesson only when it explains a current constraint or decision.
   - Put superseded run details and repeated error output behind a clearly labeled history reference. Archives are historical evidence, not current guidance.
   - Preserve review findings, corrected assumptions, rejected options, and unresolved risks when they still affect what the next agent should trust or avoid.
   - When a specific code location matters, record it as `path:line` or `path:start-end` instead of naming only the file.
   - Verify each line anchor against line-numbered source output. Do not infer line numbers from a filtered or compressed read.
   - Record current verification explicitly: what was run or measured, what passed or failed, and what remains unverified or needs rerunning. Do not use an older result as proof for later changes.
   - When a verification result comes from a retained log or report, include its path alongside the result so the next agent can inspect the evidence.
   - Read only artifacts needed to summarize accurately. Do not reread the whole repo or paste full chat, logs, or diffs.

2. **Choose an allowed path**
   - Use user-provided focus as next-agent focus.
   - If the user names a path, honor it.
   - Otherwise, if one feature folder under `.agents/scratchpad/` clearly matches, write `<that-folder>/handoff.md`.
   - Otherwise write `.agents/scratchpad/handoff.md`.
   - If the requested path is invalid or multiple folders are plausible, fall back to the root handoff and note why.

3. **Write or update `handoff.md`**
   - Create `.agents/scratchpad/` if needed.
   - Update an existing handoff in place and remove stale or duplicate content.
   - When resuming from an existing handoff, compare its stated `Next step` with current scope and evidence before acting. Continue it only if it remains current and authorized. If it is complete or superseded, replace the stale active state and set the next step from current facts.
   - Before editing an existing handoff, reread the exact section being replaced; prefer small independent patches when changing multiple files or sections so stale context cannot reject unrelated updates.
   - Prefer compact bullets or short sections. Default shape when it fits: Goal, Status, Next focus, Next step, Decisions/constraints, Review findings/corrections, Relevant files/artifacts, Commands/results, Verification state, Blockers/recovery, Durable lesson, Historical references, Suggested skills, Briefing. Omit empty sections.
   - Include exact paths, relevant commands, current error causes, verification state, and measured results when they affect next work.
   - Include code review or QA findings when they changed the diagnosis, scope, or next step.
   - Use `path:line` anchors for source, test, config, or docs references when the next agent should inspect a specific location.
   - Reference artifacts by path or URL instead of copying them.
   - Keep historical material clearly labeled as evidence, not current instructions. Preserve current blockers, authorization limits, recovery, and unverified proof in the active handoff even when related logs move to history.
   - Redact secrets and unnecessary personal data.
   - If file write fails, emit the handoff inline and explain the failure.

4. **Report outcome**
   - State the written path.
   - State whether it is `root-scoped` or `feature-scoped`.
   - State the single most important next step.

## Specific Techniques

### Keep it resume-ready

- Distinguish done, in-progress, and remaining work.
- Recheck the inherited scope, status, and next step against the latest direction and current artifacts. Replace superseded active state instead of appending another status layer.
- Preserve what changed the plan: review findings, failed assumptions, rejected options, and why they were rejected.
- Prefer `path:line` pointers over vague file mentions when they help the next agent jump straight to the right code.
- Keep active constraints, owner actions, blockers, recovery, and unverified proof explicit. Say what actually ran and what still must be rerun; a prior pass does not prove a later change.
- Preserve unresolved questions and rejected options.
- Make the first action obvious for a fresh, weaker model.
- Include suggested skills only when they materially help.

### Keep it small

- Prefer dense evidence over long prose: one benchmark delta or failing assertion beats a pasted log.
- Omit empty sections.
- Never dump raw logs, screenshots, large diffs, or full chat unless essential.
- Keep a decision-relevant lesson inline and point to labeled historical evidence for superseded or repeated run details. Archives are historical evidence, not current guidance.
- Before replacing inline history, confirm its reference target exists and preserves any unique evidence. Keep the evidence inline when preservation cannot be confirmed.

## Common Rationalizations

| Rationalization                                            | Reality                                                                                                                                                               |
| ---------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Copying chat is safest."                                  | Fresh agent needs state, not transcript noise. Summarize and point at artifacts.                                                                                      |
| "Existing handoff is close enough."                        | Update it in place; stale next steps waste the next session.                                                                                                          |
| "Concise means skip blockers or constraints."              | Remove noise, not decision-critical context.                                                                                                                          |
| "File names are enough."                                   | When a specific code block matters, `path:line` saves rediscovery and avoids edits in the wrong place.                                                                |
| "Review findings already live in PR comments."             | If review or QA changed the diagnosis, copy the actionable finding into the handoff so the next agent inherits the corrected plan.                                    |
| "A complete incident history is safest." | Keep the lesson that changes current work, then link the original run history. Repeating every old error obscures current status and next action. |
| "The existing next step must still be right." | Check it against current scope and evidence; continue it only while it remains current and authorized. |
| "An earlier passing test proves the current change." | State which behavior was verified and keep later or unrun checks explicitly unverified. |

## Red Flags

- Creates a new handoff.md instead of updating the existing one.
- Completes the inherited `Next step` but stops without updating the existing handoff.
- Pastes logs, diffs, or chat instead of referencing them.
- Leaves stale next steps, duplicate bullets, or unverifiable completion claims.
- Keeps a superseded next step or appends a new status without replacing stale active state.
- Copies repeated historical errors into active status or presents an archive as current guidance.
- Omits the review finding, rejected option, or failed assumption that changed the plan.
- Lists files without telling the next agent where to look.
- Omits current blockers, authorization limits, recovery, unverified proof, or the first safe action.

## Verification

- [ ] Handoff is concise and free of stale or duplicate context
- [ ] Done, in-progress, and remaining work are distinguishable
- [ ] Exact next step is explicit
- [ ] Scope, status, and next step match the latest direction and current artifacts
- [ ] Review findings, rejected options, or corrected assumptions are captured when they affect next work
- [ ] Current blockers, authorization limits, recovery, and unverified proof remain inline
- [ ] Superseded run details are labeled historical references, with unique durable lessons preserved inline
- [ ] Each historical reference points to an existing retained artifact and does not point to the handoff being replaced
- [ ] Specific code references use `path:line` when a location matters
- [ ] Relevant files or artifacts include why they matter
- [ ] Verification state says what ran or was measured and what is still pending
- [ ] Sensitive information is redacted
- [ ] Suggested skills appear only when useful
