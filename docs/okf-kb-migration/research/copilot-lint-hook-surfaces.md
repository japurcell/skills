---
coverage: Current official GitHub Copilot CLI hook surfaces for validating canonical-document edits
---

# Copilot lint-hook surfaces for canonical-document edits

**Assessment date:** 2026-09-09 UTC. This note describes the current GitHub
contract; no `copilot` executable is installed here, so live-version behavior
is **UNVERIFIED**. The authoritative reference is GitHub's [Copilot hooks
reference](https://docs.github.com/en/copilot/reference/hooks-reference).

## Recommended event pairing

Use `postToolUse` as the immediate successful-edit validator and
`agentStop` as the final-response backstop. Both are supported by Copilot CLI
and cloud agent. `postToolUse` runs after a successful tool and can return
`modifiedResult` or `additionalContext`; it cannot deny or undo the edit.
`agentStop` runs after the main agent turn and can return `{"decision":"block",
"reason":"..."}` to force another turn. [Event table](https://docs.github.com/en/copilot/reference/hooks-reference#hook-events) ·
[postToolUse output](https://docs.github.com/en/copilot/reference/hooks-reference#posttooluse-output) ·
[agentStop decisions](https://docs.github.com/en/copilot/reference/hooks-reference#agentstop--subagentstop-decision-control)

For subagents, the analogous `subagentStop` can backstop their final response,
but `agentStop` is the main-turn gate. `subagentStop` additionally receives the
full final response and can return `modifiedResponse`; `agentStop` cannot rewrite
the response. [SubagentStop payload](https://docs.github.com/en/copilot/reference/hooks-reference#subagentstop--subagentstop)

## Envelopes and changed-file visibility

The camelCase `postToolUse` payload is:

```json
{"sessionId":"...","timestamp":0,"cwd":"...","toolName":"edit","toolArgs":{},"toolResult":{"resultType":"success","textResultForLlm":"..."}}
```

The PascalCase/VS Code-compatible `PostToolUse` form uses
`hook_event_name`, `session_id`, `timestamp` (ISO string), `cwd`, `tool_name`,
`tool_input`, and `tool_result.result_type` / `text_result_for_llm`.
`agentStop` similarly supplies `cwd` and `transcriptPath` (or
`transcript_path`), plus `stop_hook_active`. [PostToolUse payload](https://docs.github.com/en/copilot/reference/hooks-reference#posttooluse--posttooluse) ·
[agentStop payload](https://docs.github.com/en/copilot/reference/hooks-reference#agentstop--stop)

There is no documented `changedFiles` field, file list, edit diff, or canonical
document identifier in either envelope. A validator can inspect `toolArgs` /
`tool_input`, or derive paths/diffs from the supplied `cwd` and the workspace
(`git diff`, filesystem checks), but that is local inference and may include
unrelated concurrent/uncommitted changes. **UNVERIFIED:** whether any target
CLI build adds extra path/diff fields not in the published contract.

Matchers are optional, full-match regular expressions compiled as
`^(?:PATTERN)$`; for `postToolUse` they match `toolName`. Thus a matcher such
as `edit|create|bash` selects common mutation routes, but cannot guarantee that
all file mutations use those tools. [Matcher filtering](https://docs.github.com/en/copilot/reference/hooks-reference#matcher-filtering)

## Decision and exit semantics

Command-hook stdout must resolve to one final JSON document. A one-line JSON
`{"type":"progress",...}` message is stripped as display-only; other output
is retained, and empty/invalid/multiple final documents fall through to default
behavior. Keep diagnostics on stderr. Exit `0` parses stdout. For
`postToolUse`, `{}` preserves the result and `additionalContext` is appended
to the model-visible result (multiple additions are joined and capped at 10 KB).
[Command output parsing](https://docs.github.com/en/copilot/reference/hooks-reference#progress-messages) ·
[Exit codes](https://docs.github.com/en/copilot/reference/hooks-reference#exit-codes-for-command-hooks)

`agentStop`/`subagentStop` decisions are JSON `decision: "allow"|"block"` plus
`reason`; a block forces continuation. The CLI overrides the hook after eight
consecutive blocks, and `stop_hook_active` identifies a previously forced turn.
Therefore a final-response validator should be bounded and idempotent, and must
treat the eight-block guard as a hard reliability limit. [Runaway guard and decisions](https://docs.github.com/en/copilot/reference/hooks-reference#agentstop--subagentstop-decision-control)

## Reliability gaps and practical boundary

- `postToolUse` covers only successful tool completions. A failed edit instead
  emits `postToolUseFailure`, whose documented output is recovery
  `additionalContext`, not a blocking decision. [Failure event](https://docs.github.com/en/copilot/reference/hooks-reference#posttoolusefailure--posttoolusefailure)
- For most events, non-zero exits and timeouts are logged/skipped (fail-open).
  `postToolUse` and `agentStop` therefore cannot provide a hard filesystem
  invariant if the validator crashes or times out. `preToolUse` is the only
  command-hook denial surface, returning `permissionDecision: "deny"` and a
  required reason, but it runs before a tool—not after validating the resulting
  canonical document. Its non-timeout errors fail closed, while timeouts still
  fail open. [preToolUse control and failure behavior](https://docs.github.com/en/copilot/reference/hooks-reference#pretooluse-decision-control)
- Cloud agent is non-interactive and pre-approves tools; `permissionRequest` is
  ineffective there. Cloud hooks load only from `.github/hooks/*.json`, run in
  Linux, and have an ephemeral filesystem. [Cloud execution environment](https://docs.github.com/en/copilot/reference/hooks-reference#cloud-agent-execution-environment)
- A stop block asks the model for another turn; it does not roll back an
  already-written file. A validator must report the exact invalid paths/reason
  and rely on the continuation to repair them, then independently recheck at
  the next `agentStop`.

**Bottom line:** post-tool validation plus an `agentStop` backstop is the
documented composition for detecting and repairing canonical-document drift,
not an atomic post-write transaction or guaranteed hard block. A pre-tool hook
can reduce risk for known mutation tools, but no documented Copilot hook
envelope identifies changed files directly.
