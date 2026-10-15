---
name: handoff
description: Capture concise continuation context for another agent. Use before compaction, context reset, handoff, handover, saving progress, ending mid-task, or when the user asks to preserve session state, resume later, or continue in a new session.
argument-hint: "Optional focus for the next agent"
---

# Handoff

Create a concise, resume-ready handoff so another agent can continue without rereading the whole conversation or repeating investigation.

## Use this skill when

- The user asks to hand off, handover, save progress, capture context, preserve session state, resume later, continue later, continue in a new session, or pass work to another agent.
- A compaction, context reset, session end, or model switch may happen.
- Work is paused mid-task and another agent, human, or async worker may continue.
- The user gives a next-session focus, task, or instruction for another agent.

## Workflow

1. **Identify scope**
   - Use any user-provided argument as the next agent’s focus.
   - Determine the active goal, current status, completed work, unfinished work, blockers, and exact next step.
   - Read only the relevant instructions, files, diffs, command outputs, errors, plans, PRDs, specs, issues, or notes needed to summarize status.
   - Do not reread the whole repository or copy the full chat.

2. **Choose output path**
   - If the user names a path, use it only if it is under `.agents/scratchpad/`.
   - If one active feature folder under `.agents/scratchpad/` clearly applies, write there.
   - Otherwise write to `.agents/scratchpad/handoff.md`.
   - If multiple feature folders are plausible, ask the user.
   - Create `.agents/scratchpad/` if needed.

3. **Write or update the handoff**
   - Save as `handoff.md`.
   - If a handoff already exists, update it in place and remove stale or duplicate information.
   - Use clear Markdown with whatever headings best preserve the important context.
   - Prefer concise bullets, but include enough detail for a weaker model to continue safely.
   - Include exact paths, commands, test results, errors, decisions, constraints, and next steps when relevant.
   - Reference existing artifacts by path or URL instead of duplicating them.
   - Redact secrets, credentials, tokens, private keys, passwords, and unnecessary personal information.
   - If writing fails, provide the handoff inline and explain why.

4. **Report result**
   - State the path written.
   - State whether it is root-scoped or feature-scoped.
   - Give the single most important next step.

## Content to include

Use a free-form structure, but capture the following when relevant:

- **Goal** — what the user is trying to accomplish.
- **Current status** — what is done, what is in progress, and what remains.
- **Next-agent focus** — the requested or likely focus for the next session.
- **Exact next step** — the first concrete action the next agent should take.
- **Suggested skills** — skills the next agent should invoke, with a brief reason for each.
- **Decisions and constraints** — user preferences, requirements, assumptions, rejected options, or non-goals.
- **Relevant files and artifacts** — paths or URLs with a short reason each matters.
- **Commands and results** — important commands run, outputs summarized, and tests passed or still needed.
- **Errors and blockers** — unresolved failures, ambiguity, missing access, or questions for the user.
- **Durable learnings** — reusable commands, repo conventions, environment quirks, gotchas, or patterns discovered.
- **Briefing** — a short plain-language summary of what changed, why, current state, and what to do first.

## Rules

- Never write outside `.agents/scratchpad/`.
- Prefer one concise page over a long transcript.
- Do not force a rigid template if it would omit important context.
- Do not include raw logs, full screenshots, large diffs, or full chat history unless essential.
- Do not duplicate content already captured in PRDs, plans, ADRs, issues, commits, or diffs; reference it instead.
- Do not claim work is complete unless it has been verified.
- Preserve important user preferences, constraints, decisions, and unresolved questions.
- Redact sensitive information.
- Make the handoff understandable to a fresh, weaker model with no hidden context.

## Validation

Before finishing, confirm:

- [ ] File path is under `.agents/scratchpad/`
- [ ] Handoff is concise but complete enough to resume
- [ ] Relevant files and artifacts include reasons
- [ ] Sensitive information is redacted
- [ ] Done, in-progress, and remaining work are distinguishable
- [ ] Suggested skills are included when useful
- [ ] The exact next step is clear
- [ ] Important context was not omitted to satisfy formatting