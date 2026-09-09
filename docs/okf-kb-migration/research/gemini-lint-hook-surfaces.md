---
coverage: Current official Gemini CLI hook surfaces for blocking invalid canonical-document edits
---

# Gemini CLI lint-hook surfaces for canonical-document edits

**Assessment date:** 2026-09-09 UTC. Sources below track Gemini CLI `main`,
which is a moving target; verify the deployed CLI version before relying on
behavior.

## Short conclusion

Use `AfterTool` as the immediate post-edit validator, filtered to the edit
tools (for example `write_file|replace`), and `AfterAgent` as a final-response
backstop. `AfterTool` is the only one of these two events that exposes the
tool arguments and therefore the likely target path/content. It runs after
the tool has executed: the documented `deny` behavior hides/replaces the
result sent to the model; it is **not documented as undoing or rolling back the
filesystem edit**. This last consequence is an inference from the published
output contract, so a true pre-write block still requires `BeforeTool`.

## Envelopes and changed-file detection

All hooks receive this common envelope: `session_id`, `transcript_path`,
`cwd`, `hook_event_name`, and ISO-8601 `timestamp`.

`AfterTool` adds:

```json
{
  "tool_name": "write_file",
  "tool_input": {},
  "tool_response": {"llmContent": [], "returnDisplay": "", "error": null},
  "mcp_context": {},
  "original_request_name": "..."
}
```

`mcp_context` and `original_request_name` are optional in the upstream
TypeScript interface; `tool_response` is a record whose documented contents
include `llmContent`, `returnDisplay`, and optional `error`. The contract does
not provide a `changedFiles`, diff, or post-write file list. A hook must inspect
the tool-specific arguments (often a path plus content/new string) and/or
derive changed paths from `cwd` and the local filesystem/Git state. The latter
is an inference and can include unrelated pre-existing or concurrent changes.

`AfterAgent` adds only `prompt`, `prompt_response`, and `stop_hook_active`.
It has no changed-file or tool-call history field. A final gate can scan the
workspace from `cwd` (or maintain state from earlier `AfterTool` invocations),
but that state/correlation scheme is hook-owned and is not a Gemini guarantee.

## Matchers

For `BeforeTool` and `AfterTool`, `matcher` is evaluated against the tool name.
The upstream planner treats `*` and an empty matcher as match-all; otherwise it
constructs JavaScript `RegExp(matcher)` and calls `.test(toolName)`. Invalid
regex falls back to literal equality. Thus `write_file|replace` is a useful
edit-tool filter, but it is not a file-path filter. Lifecycle matchers (such as
`AfterAgent`) are exact trigger/source comparisons; `*` remains the explicit
match-all special case.

## Decisions and exit semantics

For normal structured control, emit JSON on stdout and exit `0`:

- `AfterTool`: `{ "decision": "deny", "reason": "..." }` hides the real
  tool result and sends `reason` instead; `continue: false` terminates the
  entire agent loop. `{ "decision": "allow" }` is the normal allow result.
- `AfterAgent`: `decision: "deny"` rejects the final response and forces an
  automatic retry, with `reason` supplied as the correction prompt;
  `continue: false` stops the session without retrying. `stop_hook_active`
  identifies that the hook is already in a retry sequence and should be used
  to prevent an unbounded retry policy.

Exit `2` is the emergency/system-block path: stderr supplies the reason. For
`AfterTool` it blocks/hides the result while the turn continues; for
`AfterAgent` it rejects the response and triggers an automatic retry. Other
nonzero exits are warnings and the CLI continues. Stdout must contain only
JSON (no diagnostics).

## Reliability and design gaps

- **Post-write limitation:** `AfterTool` is auditing/context/result-hiding,
  not a documented transaction/rollback boundary. Pair it with `BeforeTool`
  for deterministic pre-write validation, or have the post-hook explicitly
  repair/revert with carefully scoped, hook-owned logic.
- **No canonical-document identity:** neither envelope names canonical docs or
  supplies a diff. Path/content extraction and Git comparison are local
  policy, not portable hook fields.
- **Final gate availability:** an official open Gemini CLI issue reports that
  `AfterAgent` configured in `settings.json` was never executed in a reported
  build. Treat `AfterAgent` as a required capability probe in the target
  version, not an assumed guarantee. **UNVERIFIED:** whether that issue is
  fixed in the deployed build.
- **No live CLI here:** this note did not execute Gemini CLI; actual event
  firing, tool argument shapes for every edit tool, retries, and timeout
  behavior remain **UNVERIFIED** for the installed/deployed version.

## Primary sources

- [Hooks reference](https://github.com/google-gemini/gemini-cli/blob/main/docs/hooks/reference.md)
- [Hook writing and exit-code guidance](https://github.com/google-gemini/gemini-cli/blob/main/docs/hooks/writing-hooks.md)
- [Hook planner source (`main`)](https://github.com/google-gemini/gemini-cli/blob/main/packages/core/src/hooks/hookPlanner.ts)
- [Hook input/output TypeScript interfaces (`main`)](https://github.com/google-gemini/gemini-cli/blob/main/packages/core/src/hooks/types.ts)
- [Official open `AfterAgent` issue](https://github.com/google-gemini/gemini-cli/issues/27712)

