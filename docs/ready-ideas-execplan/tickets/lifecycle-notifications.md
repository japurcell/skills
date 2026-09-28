# Lifecycle Notifications

**Type:** grilling
**Status:** closed
**Blocked By:** provider-lifecycle-facts.md, repository-state-retirement.md, markdown-health-retirement.md, repository-okf-hook.md
**Research Dir:** none

## Question

Which retained hooks and key lifecycle events should emit a user-visible system or progress message on each local provider? Decide wording, security redaction, event grouping, pass/fail visibility, and rate limits so users can confirm execution without receiving a message on every ordinary tool call. Define provider-specific proof and distinguish visible output from audit-only evidence.

---

## Resolution

The user confirmed this policy on 2026-09-28:

- Cover local Copilot CLI, Gemini CLI, and Codex CLI. VS Code Local, Copilot Agent Host, and cloud agents are outside this ticket's acceptance scope. Use each CLI's native visible message surface; do not require a literal `systemMessage` field where that provider uses progress or status output. Preserve equivalent short text and meaning across providers and prove actual visibility in live CLI runs.
- Each retained operational hook independently reports a concise result when it runs at session start or turn end. Examples include required-skills loading, repository startup checks where registered, and turn-end pending-ingest, OKF lint, or secret checks where registered. Name the hook and outcome, with a safe count when useful, such as `OKF lint: passed (42 files)`. Emit one message per actual low-rate invocation, including every stop attempt after a repair; do not add a cross-hook coordinator, shared summary, or duplicate-suppression state. Telemetry-only event capture and the completion bell do not announce routine success.
- Keep routine pre/post-tool successes silent. Show actionable blocks, warnings, incomplete checks, or changes immediately through the appropriate provider surface. Keep previously approved Tool Guardian and scan-secrets redaction and wording. Ordinary success messages contain no paths, command text, document content, or secret matches. Successful `SessionEnd` handlers are audit-only; report actionable failure only when the CLI can display it.
- Use existing per-hook evidence for high-rate success: Tool Guardian logs clean outcomes in its guard log; scan-secrets logs clean outcomes in its dedicated log; RTK automatic forwarder invocations appear in observability traces but do not write an `audit.log` pass record for every successful rewrite. Do not add per-call RTK pass audit lines or claim one shared audit log proves every hook ran. Keep existing OKF turn-end audit requirements from [Repository OKF Hook](repository-okf-hook.md).
- Plan provider-native response checks and live CLI runs for startup pass, turn-end pass/fail/incomplete, repeated stop attempts, immediate block/warning, redaction, and absence of routine per-tool messages. Distinguish a visible message from model-only context, audit entries, and hook invocation markers. Verify supported platform behavior with automated Windows checks and the agreed live-check checklist. A provider field documented as visible is not proof it rendered on the installed CLI.

This replaces the initial grouped turn-end summary suggestion. The user rejected a coordinator as overkill and chose independent low-rate messages.
