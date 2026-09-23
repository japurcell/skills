# Security Hook Notifications

**Type:** grilling
**Status:** closed
**Blocked By:** provider-hook-capabilities.md
**Research Dir:** none

## Question

How should Tool Guardian and scan-secrets show the rejected action and reason in Gemini, Copilot, and Codex without exposing secret material or excessive command content? Decide the visible banner, redaction and length rules, and behavior when a provider cannot display the same form.

---

## Resolution

### User-visible behavior

Use a common message contract for local Copilot CLI and VS Code, Gemini CLI, and Codex on supported platforms. Each provider must show the same message text and meaning through its native denial or notification surface; identical visual styling is not required. A block says `blocked`, names the safe tool or action, and gives the reason. A warning says `warning`, names the action and reason, and leaves warn-mode execution unchanged. Do not label a warning as a block. Preserve Tool Guardian's category/severity summary (at most three pairs) and allowlist guidance where applicable.

For Tool Guardian, append an `Action:` excerpt that combines the matched dangerous operation and the beginning of the tool input. Normalize it to one line, redact credentials and secret-like values, and cap the combined excerpt at 160 characters. The matched operation takes priority when space is limited. This applies even when dangerous text is found inside a non-shell tool such as `complete_task`; do not call such input a shell command. If an operation cannot be isolated or the input cannot be sanitized safely, show only the safe part or `command omitted`. Never fall back to raw tool input. Use the identical final excerpt in Tool Guardian's existing owner-only guard log; do not record raw input, and keep existing threat metadata. The user explicitly chose the log excerpt to help verify what was blocked.

For scan-secrets, show a distinct `scan-secrets blocked` or `scan-secrets warning` banner with the safe action name and a generic potential-secret finding. Do not show any matched value, partial value, or secret-bearing tool content in this banner. Keep its current detailed scan log and redaction controls; the banner does not duplicate findings. A session-end scan may name the action `session-end scan` when there is no tool invocation.

Keep denial and warning decisions in the provider's structured JSON result, with exit `0` for expected control flow. Maintain fail-closed block behavior on malformed input and unexpected scanner errors. A banner extraction or redaction failure changes the excerpt to the safe fallback; it never changes the security decision or reveals unfiltered input. Bound the complete provider response, and keep stdout JSON-only. Avoid duplicate display on surfaces where a denial reason is already shown.

### Implementation boundary

Change canonical sources under `hooks/families/` and regenerate Copilot and Gemini outputs. Tool Guardian currently discards the matched string returned by its matchers (`hooks/families/tool_guard.py:636-664`) and formats only tool name plus category/severity (`:667-674`). Its 160-character sanitizer (`:593-633`) applies to tool names now; the action excerpt needs its own safe extraction and redaction path. scan-secrets currently returns a generic potential-secret message (`hooks/families/scan_secrets.py:901-905`). Add the common banner contract without exposing the scanner's redacted match records.

Codex currently registers only the required-skills startup hook in `.codex/global-hooks.json`, so this outcome requires user-level pre-tool Tool Guardian and scan-secrets integration, not only message formatting. Register the guards through the existing Codex install/merge path, preserve unrelated user hooks, and follow Codex's trust flow. Do not import another provider's installed runtime files; share build-time policy where practical. Copilot cloud cannot load these user-level hooks and is outside this ticket's coverage. Pre-tool hooks remain limited to provider tool calls that reach the event; the banner is not an operating-system guardrail.

### Acceptance evidence for the ExecPlan

- Exercise block and warn cases through each provider's public hook stdin/stdout envelope, including a structured `complete_task` payload. Assert the same action/reason text, distinct blocked/warning wording, unchanged warn-mode execution, and provider-valid JSON.
- Test matched-operation priority, combined 160-character cap, one-line output, truncation, secret redaction, unsupported/unsafe input fallback, and identical redacted excerpt in the Tool Guardian guard log. Assert no raw command input appears in logs or provider output.
- Test scan-secrets block, warn, and session-end banners with safe action labels. Assert that no full or partial secret match appears in provider output; preserve existing scanner log redaction and bounded-failure tests.
- Verify Copilot CLI, VS Code, Gemini, and Codex registrations and installer outputs on POSIX and Windows configurations. Use automated Windows tests plus the map's live-check checklist. Include a deployed-provider smoke check for native display and distinguish source tests from installed behavior.

The provider contracts and their documented display limits are summarized in [Provider Hook Capabilities](provider-hook-capabilities.md) and its [findings](../research/provider-hook-capabilities/findings.md). Copilot command-hook timeout remains fail-open; the plan must keep pre-tool checks bounded and describe this limit rather than claiming absolute blocking.
