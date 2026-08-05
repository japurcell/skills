status: verified
---

# Summary for `cli-design-guidelines.md`

## Core Details
- **Source File**: `.agents/sources/cli-design-guidelines.md`
- **Summary File**: `.agents/memory/sources/cli-design-guidelines-md.summary.md`
- **Stale Reason**: new file

## Executive Summary
- Thoughtworks' eight CLI design guidelines emphasize familiar command structure, optional prompts with automation escape hatches, expressive flags, explicit operations, accessible help, actionable errors, visible progress, and tasteful but still machine-friendly output.

## Key Findings
- Prefer common command structure such as `[noun] [verb]`, kebab-case names, and standard short/long flags instead of custom deviations.
- Prompts can guide interactive users, but CLIs should always provide flag-based alternatives and force-style escapes for automation.
- Avoid implicit side effects; when a command performs extra work, surface it clearly or split it into separate steps.
- Helpful error output should use nonzero exit codes only for real failures, write informational output to stdout, errors to stderr, and include remediation details.
- Long-running work should report progress, and decorative output such as color, emoji, or tables should stay compatible with machine-readable automation paths.

## Integration Checklist
- [x] Read the raw source.
- [x] Update the executive summary with verified facts.
- [x] Update the key findings with verified facts.
- [x] Weave durable facts into `.agents/memory/*` or `.agents/instructions/*`.
- [x] Append an integrate record to `.agents/memory/LOG.md` after successful ingestion.
