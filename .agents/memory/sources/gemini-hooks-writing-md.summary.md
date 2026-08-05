status: verified
---

# Summary for `gemini-hooks-writing.md`

## Core Details
- **Source File**: `.agents/sources/gemini-hooks-writing.md`
- **Summary File**: `.agents/memory/sources/gemini-hooks-writing-md.summary.md`
- **Stale Reason**: new file

## Executive Summary
- The Gemini hook writing guide walks from a minimal logging hook to a multi-event workflow assistant, showing the core stdin/stdout contract, structured denial patterns, context injection, tool filtering, and a composable end-to-end hook architecture.

## Key Findings
- Even the simplest hook reads JSON from stdin, writes logs to stderr or files, and returns JSON such as `{}` or an explicit allow/deny object on stdout.
- Exit code `0` plus structured JSON is the preferred way to deny or shape behavior, while exit code `2` is the emergency-brake path for simple hard stops or script failures.
- `BeforeAgent` hooks can inject `hookSpecificOutput.additionalContext`, and `BeforeToolSelection` hooks can narrow available tools based on the prompt.
- Multiple `BeforeToolSelection` hooks combine by unioning their allowed tool lists unless one uses `mode: "NONE"` to disable tools entirely.
- The end-to-end example assigns distinct responsibilities to `SessionStart`, `BeforeAgent`, `BeforeToolSelection`, `BeforeTool`, `AfterModel`, `AfterAgent`, and `SessionEnd`, and notes that hooks can later be packaged as extensions.

## Integration Checklist
- [x] Read the raw source.
- [x] Update the executive summary with verified facts.
- [x] Update the key findings with verified facts.
- [x] Weave durable facts into `.agents/memory/*` or `.agents/instructions/*`.
- [x] Append an integrate record to `.agents/memory/LOG.md` after successful ingestion.
