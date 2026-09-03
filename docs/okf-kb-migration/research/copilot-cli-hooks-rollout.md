---
coverage: Primary-source assessment of whether current GitHub Copilot CLI hooks can safely replace the legacy KB loader with an OKF adapter
---

# Copilot CLI hook rollout: safe non-legacy OKF path assessment

## Scope, currency, and conclusion

**Assessment date:** 2026-09-03 UTC. This is an assessment of the hook contract
currently published by GitHub, not a claim about an unreleased build. GitHub's
public release page showed `v1.0.83-4` as the newest visible pre-release when
checked; it does not establish a minimum version for the hook behaviours below.
There is no `copilot` executable, globally installed Copilot package, or
user-level `~/.copilot` configuration in this execution environment, so the
locally installed CLI version cannot be established. Re-test the documented
contract and the actual target build before changing rollout state. [Official
release list](https://github.com/github/copilot-cli/releases) · [official hooks
reference](https://docs.github.com/en/copilot/reference/hooks-reference)

**Conclusion: no.** Current documented Copilot CLI hooks do **not** provide a
supported way to take this repository off the legacy loader while preserving
all of the hard requirements. In particular, there is no prompt-admission hook
that can deny a user turn before the model processes it. The two denial-capable
pre-action hooks operate only once a tool permission or tool execution has
already been proposed; stop hooks run after an agent/subagent turn. The only
per-prompt transformation event is explicitly mutation-only and is deliberately
invoked for prior messages in a batched submission, without a documented
current-message identifier. [Hook event table](https://docs.github.com/en/copilot/reference/hooks-reference#hook-events) · [prompt-transformation
payload](https://docs.github.com/en/copilot/reference/hooks-reference#userprompttransformed)

Accordingly, retain Copilot's legacy loader and withhold OKF selection/promotion
for Copilot. This is a compatibility and safety conclusion, not a claim that
an OKF projection or selector is invalid. A future Copilot path needs a
documented, tested capability that satisfies the entire gate below; a version
string alone is insufficient evidence.

## Requirement-by-requirement result

| Hard requirement | Documented capability | Result |
| --- | --- | --- |
| Deny an unsafe state *before the user turn reaches the model* | No event has a prompt-time deny/stop output. `permissionRequest` can deny before the *permission service*; `preToolUse` can deny before a *tool* executes; `agentStop`/`subagentStop` can force a later continuation. | **Not met.** All are too late for prompt admission. |
| Identify the one current prompt, rather than earlier messages supplied in a batch | `userPromptTransformed` says it runs for the primary message **and every preceding message** in a batched submission. Its published payload has only `sessionId`, `timestamp`, `cwd`, `prompt`, and `transformedPrompt`: no message ID, batch ordinal, or current/preceding flag. | **Not met.** Treating timestamp, ordering, or equal body text as a discriminator would be an undocumented inference. |
| Trust active-workspace and event-time inputs | Most camelCase payloads expose runtime-supplied `cwd` and epoch-millisecond `timestamp`; PascalCase compatibility payloads expose `cwd` and ISO-8601 `timestamp`. The reference does not define canonicalization, repository-root validation, symlink/worktree semantics, source attestation, or a cross-event ordering/correlation guarantee. | **Only ordinary host fields are available; the required trust guarantee is not documented.** An adapter may validate a supplied path locally, but cannot derive the required event-time/current-prompt guarantee from the contract. |
| Return platform-valid JSON only | Command-hook stdout is parsed as one final JSON value. Progress is allowed only as separate one-line JSON `type: "progress"` objects; any remaining empty or invalid JSON falls through to default behaviour. | **Met, if implemented conservatively.** Emit exactly one JSON object (normally `{}` or the applicable decision) and no diagnostics/body text on stdout. |
| Do not leak task prompt or content body | Prompt events deliver the body to the handler: `userPromptSubmitted` includes `prompt`, and `userPromptTransformed` includes both `prompt` and `transformedPrompt`. `subagentStop` carries the full final subagent response; some lifecycle payloads contain a transcript path. No configuration field requests a redacted/minimal payload. | **Not met for a prompt-aware adapter.** A handler can avoid echoing/logging data, but it cannot use those prompt events without receiving the body. Decision/continuation reasons are also sent back into agent context, so they must remain privacy-safe. |

The second and fifth rows are direct contract gaps. The conclusion that no
composition can satisfy all five is an inference from those gaps plus the
event timing described below.

## Every documented event and its relevant control surface

GitHub states that Copilot CLI supports all events in its event table. The
table currently lists the fourteen entries below; no documented event is a
general `beforeUserPrompt`/`beforeAgent` admission gate. [Complete event
table](https://docs.github.com/en/copilot/reference/hooks-reference#hook-events)

| Event | Timing and documented usable output | Why it cannot be the required safe switch |
| --- | --- | --- |
| `sessionStart` | Starts a new or resumed session; may add `additionalContext`. Its input has `sessionId`, `timestamp`, `cwd`, `source`, and optional `initialPrompt`. | Not per-turn; no deny/defer control. `initialPrompt` is optional and is prompt exposure if present. |
| `sessionEnd` | Session termination; no processed control output. | After all relevant turns. |
| `userPromptSubmitted` | User submits a prompt. The payload has `prompt`, but config-file command/HTTP output—including `modifiedPrompt`—is dropped; modification is SDK-programmatic only. | No supported config-hook denial or rewrite; body exposure; no documented batch correlation to transformed events. |
| `userPromptTransformed` | Immediately before model-facing content is emitted/persisted. May return `modifiedTransformedPrompt`. | Can rewrite but cannot block or handle the turn; fires for the primary and preceding batched messages; sees both prompt representations. |
| `permissionRequest` | Before rules/session approvals/auto decision/user permission prompt. `behavior: "allow"|"deny"`, optional denial `message`, and `interrupt: true` with deny can stop the agent. | A tool-permission gate, not a user-prompt gate. Some permission kinds bypass it, and it is CLI-only/not applicable to cloud agent. |
| `preToolUse` | Before each tool executes. `permissionDecision: "allow"|"deny"|"ask"`, required deny reason, and `modifiedArgs` control that tool call. | A tool gate after the prompt/model has already driven a tool request, not pre-turn admission. |
| `postToolUse` | After successful tool use; can return `modifiedResult` or `additionalContext`. | Too late; it changes the tool result/context, not turn admission. |
| `postToolUseFailure` | After failed tool use; can give recovery `additionalContext`. | Too late and no deny/transform/defer of the originating turn. |
| `preCompact` | Before context compaction; notification only. | No decision control and unrelated to user-prompt admission. Its input includes `customInstructions` and `transcriptPath`, so it is not a privacy-minimal substitute. |
| `agentStop` | Main agent has finished a turn. `decision: "block"` with `reason` forces another turn; `allow` completes it. | Post-turn only, and a runaway guard overrides eight consecutive blocks. The continuation reason becomes a prompt, so it cannot act as a silent denial channel. |
| `subagentStart` | Before an emitted subagent runs; may prepend `additionalContext` to its prompt but cannot block creation. | Only subagent scope; no parent prompt admission or denial. Built-in `general-purpose` does not emit this event. |
| `subagentStop` | A subagent has completed; shares `block`/`allow` continuation and may return `modifiedResponse`. | Post-subagent only; full response is supplied to the hook, which violates a no-body-exposure requirement. |
| `notification` | Asynchronous/fire-and-forget system notification; may inject `additionalContext`. | Never blocks and has no ordering guarantee suitable for a prompt gate. |
| `errorOccurred` | Error lifecycle notification; no processed output. | Reactive, not an admission control. |

Event timing, payload fields, and outputs above are documented in the
[event table](https://docs.github.com/en/copilot/reference/hooks-reference#hook-events),
[event payloads](https://docs.github.com/en/copilot/reference/hooks-reference#hook-event-input-payloads),
[prompt-submission output rules](https://docs.github.com/en/copilot/reference/hooks-reference#userpromptsubmitted),
[tool decision controls](https://docs.github.com/en/copilot/reference/hooks-reference#pretooluse-decision-control),
[permission controls](https://docs.github.com/en/copilot/reference/hooks-reference#permissionrequest-decision-control),
and [stop controls](https://docs.github.com/en/copilot/reference/hooks-reference#agentstop--subagentstop-decision-control).

## Important control and transport limits

- `permissionRequest` is the earliest CLI permission point and can short-circuit
  normal permission handling, but that is still a proposed tool operation.
  `read` and `hook` permission kinds short-circuit before those hooks, and a
  sandbox-bypass request cannot be pre-approved by a hook `allow`. These
  documented qualifications further rule it out as a universal state gate.
  [Permission semantics](https://docs.github.com/en/copilot/reference/hooks-reference#permissionrequest-decision-control)

- A command `preToolUse` crash or non-timeout non-zero exit denies the tool,
  but **timeouts are always fail-open**, including for policy hooks. HTTP
  `preToolUse` is fail-open on request failure. Thus even a tool-only safety
  gate must have a bounded, local command implementation and still cannot be
  promoted to a pre-turn hard stop. [Pre-tool failure
  behaviour](https://docs.github.com/en/copilot/reference/hooks-reference#pretooluse--pretooluse) · [command exit-code
  rules](https://docs.github.com/en/copilot/reference/hooks-reference#exit-codes-for-command-hooks)

- Hooks of a type execute in order, but this does not supply prompt identity or
  a transaction spanning prompt events. For `preToolUse`, any deny blocks the
  tool; for stop hooks, the host has an eight-continuation cap. Neither fact
  creates an atomic "validate current prompt, then select context or deny"
  operation. [Hook ordering and stop cap](https://docs.github.com/en/copilot/reference/hooks-reference#agentstop--subagentstop-decision-control)

- Stdout must be treated as a control protocol, not an audit channel. The host
  strips only valid single-line progress JSON and then parses the remaining
  stdout once; multiple final JSON values or plain-text diagnostics invalidate
  the control response and fall through. Send diagnostics to a protected local
  sink only after enforcing the repository's no-prompt/no-body logging rule.
  [Command output parsing](https://docs.github.com/en/copilot/reference/hooks-reference#progress-messages)

## Rollout implication and future acceptance gate

Do not infer a solution from an undocumented ordering observation, a local
transcript parse, a timestamp heuristic, or a stop-hook retry. Continue to
serve the legacy loader for Copilot. A future supported candidate must be
accepted only after both current official documentation and a behavioural test
show all of the following in the actual host build:

1. A per-submission, pre-model hard denial whose timeout/error handling cannot
   silently admit an unsafe turn.
2. A stable, documented current-message/batch discriminator carried with that
   decision event.
3. Documented provider-owned active-workspace identity and event timestamp
   semantics sufficient for adapter validation.
4. One JSON-only response protocol with a documented denial outcome.
5. A redacted/minimal event payload, or a documented host-side capability that
   lets the adapter decide without receiving, retaining, or returning task text
   or content bodies.

Until then, Copilot's supported hooks remain useful for tool-level guardrails,
startup/subagent context injection, observability, and post-turn quality
checks—not as a replacement for the legacy-loader safety boundary.
