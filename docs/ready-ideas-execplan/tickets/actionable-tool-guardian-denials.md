# Actionable Tool Guardian Denials

**Type:** grilling
**Status:** closed
**Blocked By:** security-hook-notifications.md, provider-hook-capabilities.md
**Research Dir:** none

## Question

The observed Gemini denial says `Tool Guardian blocked write_file. input_limits/critical. Adjust TOOL_GUARD_ALLOWLIST only if this action is intentional [tool-guard]`, but the agent must read hook source to learn the exact cause. Which safe, specific policy condition and remediation should a denial or warning expose so local Gemini, Copilot, and Codex agents can correct the tool call without reading source? Decide how to identify the violated field, threshold or rule, preserve the existing redacted 160-character action excerpt and secret protections, handle multiple findings and unknown causes, align the guard log, and prove provider-native delivery without excessive message noise.

---

## Resolution

Tool Guardian block and warning messages must identify the specific violated rule and why the input matched it. Preserve the safe tool/action name, blocked versus warning wording, severity, and the existing redacted `Action:` excerpt capped at 160 characters. Show up to three distinct rule reasons and an omitted count for additional findings. Do not print raw matched input, secret values, or arbitrary structured-input keys. Name a known provider field such as `write_file.content` only when the guard can identify it safely; otherwise say `tool input`.

For `input_limits`, report which limit failed, its configured threshold, and the measured count when available, using the actual unit for that limit. This includes scan-text size, command segments or tokens, and structured-input depth, nodes, strings, or bytes. A known inspection failure should state its safe cause without inventing a violated rule. Keep the existing fail-closed decision. The allowlist cannot bypass input limits, so never recommend it for those denials. Corrections are optional: reuse an existing static rule suggestion when it is accurate and cheap to surface, but do not build a new remediation engine. Never show misleading allowlist advice.

Canonical `hooks/families/tool_guard.py` currently discards the `ScanLimitExceeded` detail and rule suggestions before formatting (`build_threats`, around lines 675-691), and its formatter shows category/severity but not the exact condition (around lines 816-823). Structured traversal does not retain field paths. Capture only safe, structured rule and limit metadata needed for the message; do not log or echo exception text or arbitrary keys without review. Keep the guard log aligned with the displayed safe rule IDs, limit/count details, and the already approved identical redacted `Action:` excerpt. Keep raw tool input out of logs.

Acceptance must cover representative limit types, specific dangerous-operation rules, multiple findings and omitted counts, known and unknown fields, safe inspection failures, warning versus blocking decisions, unchanged fail-closed behavior, excerpt redaction and length, and exact safe log/message alignment. Exercise provider-specific JSON envelopes and native visible denial/warning surfaces on local Copilot, Gemini, and Codex as required by [Security Hook Notifications](security-hook-notifications.md). Preserve that ticket's supported-platform and Windows checklist gates; do not infer provider display from source-only tests.
