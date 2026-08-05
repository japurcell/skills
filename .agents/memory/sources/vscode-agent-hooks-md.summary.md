status: verified
---

# Summary for `vscode-agent-hooks.md`

## Core Details
- **Source File**: `.agents/sources/vscode-agent-hooks.md`
- **Summary File**: `.agents/memory/sources/vscode-agent-hooks-md.summary.md`
- **Stale Reason**: new file

## Executive Summary
- The VS Code agent hooks preview docs define the supported hook events, workspace/user/plugin/custom-agent hook locations, shared JSON input/output contract, OS-specific command overrides, agent-scoped hooks, and compatibility caveats for Claude and Copilot hook formats.

## Key Findings
- VS Code currently supports eight hook events and loads hook files from `.github/hooks/*.json`, Claude-format settings files, user-level hook locations, plugins, and optional custom-agent frontmatter hooks.
- Hook discovery can be customized with `chat.hookFilesLocations`, and agent-frontmatter hooks require `chat.useCustomAgentHooks` to be enabled.
- Hooks share common `continue`, `stopReason`, and `systemMessage` output fields; exit code `2` blocks processing while other nonzero exits become warnings.
- VS Code ignores Claude matcher values, so Claude-format hooks still run for the event even when their matcher would have filtered elsewhere.
- Claude, Copilot, and VS Code payloads differ in tool names and field casing, so hook scripts must read the correct `tool_name` and `tool_input` shape for the runtime.
- The docs explicitly warn that hook scripts are executable code and recommend preventing agents from auto-approving edits to the scripts that the same session may later execute.

## Integration Checklist
- [x] Read the raw source.
- [x] Update the executive summary with verified facts.
- [x] Update the key findings with verified facts.
- [x] Weave durable facts into `.agents/memory/*` or `.agents/instructions/*`.
- [x] Append an integrate record to `.agents/memory/LOG.md` after successful ingestion.
