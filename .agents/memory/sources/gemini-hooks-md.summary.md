status: verified
---

# Summary for `gemini-hooks.md`

## Core Details
- **Source File**: `.agents/sources/gemini-hooks.md`
- **Summary File**: `.agents/memory/sources/gemini-hooks-md.summary.md`
- **Stale Reason**: new file

## Executive Summary
- The Gemini hooks overview introduces synchronous hook execution, the available lifecycle events, the strict JSON stdout contract, matcher semantics, settings precedence, hook security warnings, and the built-in `/hooks` management commands.

## Key Findings
- Hooks run synchronously inside the agent loop, so every matching hook must finish before Gemini CLI continues.
- Stdout must contain only the final JSON response, while stderr is the supported path for debugging and logging.
- Exit code `0` is the preferred control path even for intentional denials, exit code `2` is a system block, and other nonzero exits warn while allowing execution to continue.
- Tool-event matchers use regular expressions, lifecycle-event matchers use exact strings, and `*` or an empty matcher applies to everything.
- Hook settings merge in precedence order of project, user, system, then extensions, and project hook identities are fingerprinted from `name` plus `command` so modified hooks are re-warned as untrusted.
- The docs surface `/hooks panel`, `/hooks enable-all`, `/hooks disable-all`, and per-hook enable/disable commands for operational management.

## Integration Checklist
- [x] Read the raw source.
- [x] Update the executive summary with verified facts.
- [x] Update the key findings with verified facts.
- [x] Weave durable facts into `.agents/memory/*` or `.agents/instructions/*`.
- [x] Append an integrate record to `.agents/memory/LOG.md` after successful ingestion.
