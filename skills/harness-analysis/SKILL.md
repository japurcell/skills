---
name: harness-analysis
description: Use when asked to audit recent agent/harness sessions, hook logs, skills, AGENTS.md, or linked docs for read-only recommendations that reduce token use, tool churn, failures, and execution time. Use when the user requests a harness, session, process, agent-behavior, hook, skill, or agent-instruction audit. Do not use for normal coding, debugging, writing, or documentation tasks unless the user specifically asks for this audit.
---

# Harness Analysis

## Goal

Read-only audit of recent agent sessions and related guidance to recommend practical ways to reduce:

- Token use
- Tool churn
- Repeated failures
- Excessive file reads
- Slow workflows
- Confusing or conflicting agent instructions

Return evidence-backed recommendations. Do not modify files.

## Rules

- Read-only only.
- Do not create, edit, move, delete, or rewrite files.
- Do not install packages or change configuration.
- Do not execute hook scripts.
- Do not run destructive commands.
- Do not paste secrets, tokens, credentials, cookies, private keys, or personal data.
- If sensitive data appears, say only that sensitive data was observed and recommend redaction.
- Do not fabricate evidence.
- If evidence is limited, say so and mark recommendations tentative.

## Default Limits

Unless the user gives different limits:

- Time window: last 14 days
- Deeply inspect at most 10 recent session logs
- Deeply inspect at most 20 recent hook logs
- Prefer file lists, metadata, counts, `head`, `tail`, and targeted search before full reads
- Avoid reading any large file in full unless necessary
- Deduplicate findings before reporting

## What to Inspect

### Agent instructions and docs

Look for:

- `AGENTS.md`
- `.agents.md`
- `CLAUDE.md`
- `GEMINI.md`
- `.cursorrules`
- `.github/copilot-instructions.md`
- `README.md`
- `docs/`
- `.claude/`
- `.gemini/`
- `~/.agents/`
- `~/.copilot/`
- `~/.gemini/`
- Files linked from agent instructions

### Skills

Look for:

- `.claude/skills/`
- `.anthropic/skills/`
- `skills/`
- `~/.agents/skills/`
- User-provided skill paths

Check for:

- Over-broad descriptions that trigger too often
- Missing “use when” / “do not use when” boundaries
- Long always-loaded instructions
- Duplicate guidance across skills and docs
- Missing read-only or plan-mode constraints
- Guidance that encourages broad file reading
- Verbose output formats
- Ambiguous steps weaker models may misread

### Session logs

Look in likely locations:

- `~/.claude/projects/`
- `~/.claude/`
- `~/.gemini/`
- `~/.copilot/`
- Repository-local log directories

If needed, conservatively search recent files with path/name terms:

- `session`
- `transcript`
- `conversation`
- `agent`
- `claude`
- `gemini`
- `copilot`
- `chat`
- `log`
- `jsonl`

Avoid broad unbounded home-directory scans.

### Hook logs and hook files

Check if present:

- `~/.copilot/hooks/**/*.log`
- `$REPO_ROOT/.github/hooks/**/*.log`
- `~/.gemini/hooks/**/*.log`
- `$REPO_ROOT/.gemini/hooks/**/*log`
- `.github/hooks/`
- `.gemini/hooks/`
- `.claude/hooks/`
- `.husky/`
- `scripts/`
- `hooks/`

Do not run hooks.

## Procedure

1. Identify the repository root.
2. List candidate instruction, skill, doc, session-log, hook-log, and hook-script files.
3. Sort logs by modification time.
4. Inspect the most recent relevant logs first.
5. Use targeted searches for failures and churn.
6. Read only enough surrounding context to understand each issue.
7. Group duplicate or related issues.
8. Produce a concise evidence-backed report.

Useful search terms:

- `error`
- `failed`
- `failure`
- `exception`
- `traceback`
- `timeout`
- `permission denied`
- `not found`
- `rate limit`
- `retry`
- `again`
- `read_file`
- `grep`
- `glob`
- `search`
- `tool_use`
- `too many`
- `context`
- `token`
- `hook`
- `exit code`
- `stderr`
- `warning`

## Analyze For

### Failures

Look for repeated failed commands, missing dependencies, wrong paths, permission issues, hook failures, timeouts, retries without new information, and confusion from unclear instructions.

Recommend specific fixes such as preflight checks, clearer paths, better hook errors, narrower skill descriptions, stop conditions, or targeted validation.

### Excessive file reading

Look for large unnecessary reads, repeated reads, broad scans, always-read docs, and long linked docs loaded for simple tasks.

Recommend gates such as “read only when needed,” short indexes, search-before-read, moving long guidance to linked docs, and removing duplication.

### Excessive tool calls

Look for repeated `ls`, `find`, `grep`, reads, failed commands from bad assumptions, full test reruns, or planning/search loops without progress.

Recommend bounded discovery steps, preferred commands, stop conditions, and asking the user when required information is missing.

### Token waste

Look for large always-loaded instructions, duplicated content, long examples, verbose required formats, or copied logs/instructions in responses.

Recommend shortening front-loaded guidance, moving rare details to docs, splitting broad skills, concise templates, and minimal examples.

### Accuracy problems

Look for contradictory instructions, stale docs, unclear ownership, missing definitions of done, paths that do not match the repo, or hallucinated workflows.

Recommend a single source of truth, precedence rules, version notes, repo maps, and clearer task boundaries.

### Execution-time problems

Look for slow hooks, expensive checks run too often, full builds when targeted checks would work, repeated dependency installs, and timeouts.

Recommend quick-check versus full-check guidance, targeted tests, timeout expectations, cache-aware notes, and safe hook skip conditions where appropriate.

### Hook problems

Look for repeated hook failures, unavailable tools, unclear output, noisy output, blocking safe workflows, or expensive checks run too often.

Recommend dependency checks, concise errors, timeouts, less noisy output, documented behavior, and safe skip conditions where appropriate.

Do not recommend disabling security, compliance, or safety hooks unless evidence supports a safer replacement.

## Recommendation Standard

Each recommendation must be:

- Specific
- Evidence-backed
- Deduplicated
- Proportional to impact
- Safe to implement
- Easy for weaker models to follow

Avoid vague advice like “improve documentation” or “reduce tokens.”

Prefer concrete advice, for example:

- “Move the detailed testing matrix from `AGENTS.md` to `docs/testing.md` and replace it with a short decision table.”
- “Add a preflight check for `ruff` because hook logs repeatedly show `command not found: ruff`.”
- “Narrow the skill description so it triggers only for release-note generation, not all documentation tasks.”

## Report Format

Produce:

# Harness Analysis Report

## Scope

- **Repository:**
- **Time window:**
- **Session logs inspected:**
- **Hook logs inspected:**
- **Instruction files inspected:**
- **Skill files inspected:**
- **Linked docs inspected:**
- **Limits or gaps:**

## Executive Summary

3-6 bullets with the most important conclusions.

## Highest-Impact Recommendations

### 1. Recommendation Title

- **Target:** File, skill, hook, or workflow
- **Issue:** What is going wrong
- **Evidence:** Short sanitized evidence
- **Impact:** Token usage, accuracy, execution time, reliability, or tool churn
- **Recommended change:** Specific change
- **Why this helps weaker models:** How it simplifies decisions or reduces context
- **Effort:** Low, Medium, or High
- **Risk:** Low, Medium, or High
- **Validation:** How to confirm improvement

Repeat only for major deduplicated recommendations.

## Additional Findings

Use concise bullets:

- **Finding:**
  - **Target:**
  - **Recommended change:**
  - **Impact:**

## Repeated Patterns Observed

Summarize recurring patterns such as failed commands, repeated reads, broad searches, hook failures, ambiguous instructions, or token-heavy docs.

## Suggested Implementation Order

Short ordered list prioritizing:

1. High-impact, low-risk fixes
2. Frequent failures
3. Token reductions
4. Accuracy improvements
5. Longer-term cleanup

## No-Change Areas

Mention inspected areas where no clear improvement was found.

## Open Questions

List only questions that materially affect recommendations.

## Confidence

State one:

- **High:** Multiple logs or files support the findings
- **Medium:** Some evidence supports the findings
- **Low:** Limited or indirect evidence

Add one sentence explaining the confidence level.

End with:
“This analysis is read-only. No files were modified.”

## If Evidence Is Sparse

If few or no logs are available:

- Say evidence is limited.
- Inspect available instruction, skill, hook, and doc files.
- Provide tentative recommendations only.
- Ask the user to provide recent session logs for stronger analysis.
- Do not fabricate log evidence.
