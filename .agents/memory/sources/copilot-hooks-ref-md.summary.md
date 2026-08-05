status: verified
---

# Summary for `copilot-hooks-ref.md`

## Core Details
- **Source File**: `.agents/sources/copilot-hooks-ref.md`
- **Summary File**: `.agents/memory/sources/copilot-hooks-ref-md.summary.md`
- **Stale Reason**: new file

## Executive Summary
- The GitHub Copilot hooks reference defines hook locations, cloud-vs-CLI execution differences, command/HTTP/prompt hook formats, event payloads, matcher behavior, decision schemas, and exit-code semantics for Copilot CLI and Copilot cloud agent.

## Key Findings
- Copilot CLI loads hooks from policy, repository, user, inline settings, and plugins, while cloud agent only loads `.github/hooks/*.json` from the cloned repository.
- Cloud agent hook execution is Linux-only, non-interactive, network-restricted, and ephemeral; only `bash` or fallback `command` entries are honored there.
- Command hooks may emit line-delimited progress JSON objects to stdout during execution, but they still need exactly one final non-progress JSON document for the actual hook result.
- `userPromptTransformed` can rewrite only the transformed model-facing prompt, not block the turn; `notification` does not fire in cloud agent.
- Command `preToolUse` hooks fail closed on non-timeout errors, but timeouts are explicitly fail-open; PascalCase `PreToolUse` uses Claude-style matcher and tool-name compatibility rules.
- `disableAllHooks` behaves differently depending on whether it is set in a single hook file or repository settings, and policy hooks are never disabled by it.

## Integration Checklist
- [x] Read the raw source.
- [x] Update the executive summary with verified facts.
- [x] Update the key findings with verified facts.
- [x] Weave durable facts into `.agents/memory/*` or `.agents/instructions/*`.
- [x] Append an integrate record to `.agents/memory/LOG.md` after successful ingestion.
