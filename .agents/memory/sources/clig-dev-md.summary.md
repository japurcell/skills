status: verified
---

# Summary for `clig-dev.md`

## Core Details
- **Source File**: `.agents/sources/clig-dev.md`
- **Summary File**: `.agents/memory/sources/clig-dev-md.summary.md`
- **Stale Reason**: new file

## Executive Summary
- `clig.dev` is a broad reference for human-first but composable CLI design, covering philosophy, help and documentation, output and errors, arguments and flags, interactivity, robustness, configuration, environment variables, naming, distribution, and analytics.

## Key Findings
- Design for humans first while preserving Unix composability through clean stdout/stderr behavior, exit codes, pipes, and optional JSON output.
- CLI help should be available from bare commands and `-h`/`--help`, lead with examples, include support/documentation links, and keep concise help distinct from full help.
- Prefer flags over multiple positional argument types, provide full-length flag names, support `--no-input`, and never require prompts when stdin is non-interactive.
- Dangerous operations should confirm explicitly, file-like input/output should accept `-` for stdin/stdout, and secrets should not be accepted via flags or environment variables.
- Recommended configuration precedence is flags, shell environment, project config, user config, then system config; follow XDG base directory rules for stored files.
- Future-proofing guidance warns against catch-all subcommands and arbitrary abbreviations because they freeze namespace choices and break additive evolution.

## Integration Checklist
- [x] Read the raw source.
- [x] Update the executive summary with verified facts.
- [x] Update the key findings with verified facts.
- [x] Weave durable facts into `.agents/memory/*` or `.agents/instructions/*`.
- [x] Append an integrate record to `.agents/memory/LOG.md` after successful ingestion.
