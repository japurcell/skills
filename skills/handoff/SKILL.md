---
name: handoff
description: Maintain concise, current task handoffs. MANDATORY first action whenever a task mentions a handoff or handoff.md, or involves resume, continue, pick up, next step, checkpoint, or context transfer. Load before touching handoff files; loading the skill does not authorize file changes.
---

# Handoff

Capture one concise handoff another agent can resume from immediately. Preserve state, evidence, and the first safe next action without copying the whole chat.

## Workflow

1. **Confirm the requested action**
   - For a read-only question, review, or audit, inspect only the relevant artifacts and report findings. Do not create or update handoff or history files.
   - For authorized handoff maintenance or ongoing task work, follow the steps below. Reconcile the relevant handoff at resume, scope changes, milestone completion, and before stopping.

2. **Reconcile current state**
   - Compare the inherited snapshot with the latest user direction, current notes, changed files, and verification results. Current evidence determines scope, status, and remaining work. Read only the artifacts needed; do not reread the whole repository.
   - When asked to resume work, continue the inherited next step only if it remains current and authorized. Otherwise choose the current safe next action. Replace superseded active instructions instead of appending another status layer.
   - Keep the current goal, done/in-progress/remaining status, user-provided next focus, exact next step, blockers, decisions, constraints, authorization limits, recovery path, and verification state inline.
   - Preserve review findings, corrected assumptions, rejected options and their reasons, unresolved questions, and risks that affect what the next agent should trust or avoid.
   - Record exact runnable commands, including the working directory and necessary arguments, and concise observed error text when needed for next work. Distinguish verified causes from hypotheses.
   - State what was run or measured, what passed or failed, and what remains unverified or needs rerunning. An older pass does not prove a later change. Include the path of any retained log or report supporting a result.
   - Name important files and explain why they matter. When a specific location matters, use `path:line` or `path:start-end`, verified against line-numbered source output rather than inferred from a filtered or compressed read.

3. **Choose the destination**
   - Honor a valid user-supplied path, even when several feature folders are plausible.
   - With no supplied path, reuse the known handoff for the current task. Otherwise use `.agents/scratchpad/<feature>/handoff.md` for the single clearly matching feature folder; if none or several match, use `.agents/scratchpad/handoff.md` and explain any ambiguity.
   - A supplied path is invalid if it cannot name a file, a parent component is a file, it is outside the authorized scope, or it remains unwritable after permitted recovery. Fall back to `.agents/scratchpad/handoff.md` and state the reason. A missing parent directory alone is not invalid.

4. **Preserve lessons and history**
   - Redact secrets and unnecessary personal data before writing any handoff, history file, or inline fallback.
   - Keep lessons needed for current decisions, constraints, or prevention of repeated mistakes inline. Preserve other unique lessons and evidence in history. Move superseded run details and repeated error output behind clearly labeled historical references; archives are evidence, not current guidance.
   - Prefer an existing retained artifact that preserves the required evidence. If the old handoff is the only copy, save that evidence to a sibling history file before replacing it.
   - For a new archive, choose an unused filename such as `handoff.history-YYYY-MM-DD.md`, adding a suffix if needed. When extending an existing archive, read it first and append a dated entry without replacing earlier unique evidence.
   - Verify each reference target exists and contains the evidence before removing it from the active handoff. Never point back to the handoff being replaced. If preservation cannot be verified, keep the needed evidence inline and report the limitation. Current blockers, owner actions, recovery instructions, and pending proof stay inline regardless of related archives.

5. **Write a compact handoff**
   - Create parent directories for the selected destination if needed. Update that file in place when it exists.
   - Before editing, reread the exact section being replaced. Prefer small independent patches so stale context cannot reject unrelated updates.
   - Use compact bullets or short sections. A useful shape is Goal/status, Next focus/action, Decisions/constraints, Review findings, Relevant files, Commands/results, Blockers/recovery, Lessons, and Historical references. Omit empty sections; include suggested skills only when they materially help.
   - Prefer dense evidence: one measured benchmark delta or failing assertion beats a pasted log. Reference artifacts by path or URL. Include raw logs, screenshots, large diffs, or full chat only when essential.
   - If writing fails, emit the redacted handoff inline and explain the failure.

6. **Report the outcome**
   - On success, state the written path, whether the context is root-scoped or feature-scoped, and the single most important next step.
   - On failure, state the intended path and scope, report any partial write or uncertain file state, and provide the inline handoff and next step without claiming success.

## Verification

- [ ] Read-only requests produced findings without document changes
- [ ] Maintenance used the requested valid path or explained the fallback
- [ ] Current scope, status, next action, and verification agree with the latest evidence
- [ ] Necessary decisions, lessons, owner limits, blockers, recovery, and pending proof remain inline
- [ ] Commands, observed errors, evidence paths, and source anchors are precise where needed
- [ ] Historical references preserve unique evidence without overwriting earlier entries
- [ ] The handoff is concise, redacted, and free of stale active instructions
- [ ] The outcome accurately reports the write result and next step
