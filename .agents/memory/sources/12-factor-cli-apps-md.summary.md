status: verified
---

# Summary for `12-factor-cli-apps.md`

## Core Details
- **Source File**: `.agents/sources/12-factor-cli-apps.md`
- **Summary File**: `.agents/memory/sources/12-factor-cli-apps-md.summary.md`
- **Stale Reason**: new file

## Executive Summary
- Jeff D's article lays out twelve CLI UX factors centered on discoverable help, explicit flags, reliable version reporting, strict stdout/stderr separation, informative errors, TTY-aware polish, optional prompts, parseable tables, fast startup, clear subcommands, and XDG-aligned file locations.

## Key Findings
- Help should be available from the bare command, `help`, and `-h`/`--help`, with examples and complementary web documentation.
- Prefer named flags over multiple positional argument types, support `--` passthrough for delegated commands, and expose version through a command plus `--version`/`-V`.
- Keep stdout for primary output and structured data, and use stderr for warnings, progress, and errors so redirection and piping stay reliable.
- Respect non-interactive environments by disabling colors, spinners, and progress bars when not attached to a TTY, and honor `TERM=dumb`, `NO_COLOR`, and `--no-color`.
- Prompts should only appear when stdin is interactive and should never be required; destructive actions benefit from explicit confirmation.
- Tabular output should keep one entity per row, avoid borders, and support filtering, sorting, truncation control, and alternate machine-readable formats such as JSON or CSV.

## Integration Checklist
- [x] Read the raw source.
- [x] Update the executive summary with verified facts.
- [x] Update the key findings with verified facts.
- [x] Weave durable facts into `.agents/memory/*` or `.agents/instructions/*`.
- [x] Append an integrate record to `.agents/memory/LOG.md` after successful ingestion.
