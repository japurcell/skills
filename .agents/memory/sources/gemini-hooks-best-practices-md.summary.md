status: verified
---

# Summary for `gemini-hooks-best-practices.md`

## Core Details
- **Source File**: `.agents/sources/gemini-hooks-best-practices.md`
- **Summary File**: `.agents/memory/sources/gemini-hooks-best-practices-md.summary.md`
- **Stale Reason**: new file

## Executive Summary
- Gemini's hook best-practices guide focuses on fast synchronous hooks, clean debugging discipline, targeted matcher/event use, hook threat modeling, explicit input validation, strict timeouts and permissions, and privacy controls around telemetry and sensitive data.

## Key Findings
- Hooks should stay fast by choosing the narrowest relevant event, filtering with matchers, caching expensive work, and preferring `AfterAgent` over `AfterModel` when only the final turn output matters.
- Stdout must remain JSON-only; logs belong on stderr or dedicated files, and hooks should be tested independently with sample JSON payloads before wiring them into the CLI.
- The guide distinguishes trust levels across system, user, extension, and project hooks, and calls out arbitrary code execution, exfiltration, and prompt injection as primary risks.
- Environment-variable redaction exists but is disabled by default; enabling it requires allowlisting any variables a hook still needs.
- Secure hooks should validate JSON structure and tool names, run with tight timeouts and minimal permissions, avoid root, and minimize logging or output of sensitive data.
- `suppressOutput` only suppresses background telemetry/logging; user-visible `systemMessage` or `reason` text still appears in the terminal.

## Integration Checklist
- [x] Read the raw source.
- [x] Update the executive summary with verified facts.
- [x] Update the key findings with verified facts.
- [x] Weave durable facts into `.agents/memory/*` or `.agents/instructions/*`.
- [x] Append an integrate record to `.agents/memory/LOG.md` after successful ingestion.
