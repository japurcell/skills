---
coverage: Rules and conventions for git and Gemini hooks under `{.copilot,.gemini}/hooks`.
---

# Git & Gemini Hooks Conventions

Guidelines for modifying and maintaining repository hook scripts under `{.copilot,.gemini}/hooks`.

## Official References

- **GitHub Copilot hooks reference:** `https://docs.github.com/en/copilot/reference/hooks-reference`
- **VS Code GitHub Copilot hooks reference:** `https://code.visualstudio.com/docs/copilot/customization/hooks`
- **Gemini CLI hooks reference:** `https://github.com/google-gemini/gemini-cli/blob/main/docs/hooks/reference.md`
- **Gemini CLI exit-code best practices:** `https://geminicli.com/docs/hooks/best-practices/#check-exit-codes`

Read official docs before non-trivial hook changes and keep implementation choices aligned with them.

## Shared Runtime Rules

- **stdout discipline:** Hook scripts must keep `stdout` JSON-only. Send logs, audit lines, and debug text to `stderr` or the audit log.
- **installed-copy rule:** Run `./scripts/install.sh` before live validation because Copilot and Gemini execute installed hooks from home-directory targets.

## Output Schemas & Exit Behavior

- **Gemini Hooks Scope:**
  - Setup errors must use: `{ "continue": false, "stopReason": ... }`
  - Validation failures must use: `{ "decision": "deny", "reason": ... }`
  - Expected hook control flow must use exit code `0`, with JSON on `stdout` driving the decision. Reserve exit code `2` for true system-block cases that should use `stderr` as the reason.
- **GitHub Hooks Scope:**
  - `agentStop` / `subagentStop` outputs must use: `{ "decision": "allow|block", "reason": ... }`
  - `postToolUse` formatting hooks should emit valid JSON only: use `{}` for no-op success, or `{ "additionalContext": ... }` when the agent should see a formatter/setup failure.
  - Expected `agentStop` and `postToolUse` control flow must exit `0` so Copilot parses `stdout` JSON. Exit code `2` is warning-only for most GitHub hook events and does not apply these decision schemas.

## Copilot and VS Code compatibility

- In `.copilot/hooks/hooks.json`, keep both `subagentStart` (CLI) and `SubagentStart` (VS Code).
- CLI responses return top-level `additionalContext`; VS Code responses return `hookSpecificOutput` plus `additionalContext`.
- Prefer `agentStop` over `subagentStop` for final-response quality validators; `subagentStop` has no matcher support in Copilot hook docs and built-in `general-purpose` agents do not emit `subagentStart` or `subagentStop`.
- Keep `SessionStart` injection path active even when `SubagentStart` exists because some VS Code `runSubagent` child sessions omit `SubagentStart`.

## Repo-specific hook gotchas

- Keep `.copilot/hooks/scripts/format.sh` in sync with `scripts/test-hooks-format.sh`; that test expects audit-backed logging, formatter command and failure logging, session-event file recovery, rollover, and lock waiting.
- Keep Copilot startup hook logic in `.copilot/hooks/scripts/load-required-skills.py` with thin shell wrappers only; keep Copilot tool-guard logic in `.copilot/hooks/scripts/tool-guard.py`; shared JSON output helpers and crash-safe audit append helpers live under `.copilot/hooks/scripts/helpers/`.
- Keep `.copilot/hooks/hooks.json` wired to the Python operational entrypoints for the retained Copilot hooks; the shell scripts stay as compatibility shims only.
- Keep Copilot RTK rewrite logic in `.copilot/hooks/scripts/rtk-hook-copilot.py`; the RTK rewrite config should point at that Python wrapper directly and `scripts/test-hooks-rtk.sh` should cover pass-through, invalid input, non-zero exit, and timeout fallbacks.
- Keep Copilot lifecycle logging hooks in `.copilot/hooks/scripts/log-agent-stop.py`, `.copilot/hooks/scripts/log-error-occurred.py`, `.copilot/hooks/scripts/log-notification.py`, `.copilot/hooks/scripts/log-tooluse-failure.py`, and `.copilot/hooks/scripts/log-subagent-stop.py` with thin shell compatibility shims; `scripts/test-hooks-format.sh` should exercise those Python entrypoints directly and keep stdout JSON-safe.
- Keep Copilot session-end hook logic in `.copilot/hooks/scripts/bell.py`, `.copilot/hooks/scripts/scan-secrets.py`, and `.copilot/hooks/scripts/log-session-end.py`; the session-end config should point at those Python entrypoints directly.
- Keep Gemini startup hook logic in `.gemini/hooks/scripts/skill-context-injector.py` and `.gemini/hooks/scripts/log-session-start.py` with thin shell wrappers only; keep Gemini passive logging hooks in `.gemini/hooks/scripts/log-after-agent.py` and `.gemini/hooks/scripts/log-notification.py` with thin shell wrappers only; shared JSON output helpers and crash-safe audit append helpers live under `.gemini/hooks/scripts/helpers/`.
- Keep Gemini RTK rewrite logic in `.gemini/hooks/scripts/rtk-hook-gemini.sh` with an inline Python implementation; the RTK rewrite config should point at that shell entrypoint and `scripts/test-gemini-hooks-rtk.sh` should cover invalid input and rewrite-failure no-op fallbacks.
- Keep Gemini session-end hook logic in `.gemini/hooks/scripts/scan-secrets.py` and `.gemini/hooks/scripts/log-session-end.py` with thin shell compatibility shims; the secrets scanner should preserve diff-only scanning, allowlists, and JSON-only stdout.
- Keep Gemini tool-guard logic in `.gemini/hooks/scripts/tool-guard.py` with a thin shell compatibility shim in `.gemini/hooks/scripts/tool-guard.sh`.
- Keep required-skill injection startup tests focused on caveman-only payloads so context loading stays consistent across Copilot CLI, VS Code, and Gemini CLI.
- Keep `scripts/test-hooks-tool-guard.sh` pointed at the Python Copilot tool-guard entrypoint while the shell wrapper remains the installed compatibility shim.
- Keep `scripts/test-hooks-rtk.sh` pointed at the Python Copilot RTK rewrite wrapper and cover payload forwarding plus no-op fallback on invalid input, non-zero exits, and timeouts.
- Keep `scripts/test-hooks-secrets-scanner.sh` pointed at the Python Copilot secrets scanner entrypoint and cover diff-header paths plus session-end hook registration.
- Keep `scripts/test-gemini-hooks-tool-guard.sh` aligned with the Gemini tool-guard shim so the installed shell wrapper can stay thin.
- Keep `scripts/test-gemini-hooks-format.sh` pointed at the Gemini passive logging Python entrypoints and cover JSON-only stdout, runtime-specific payload logging, and shadow-log behavior.
- Keep `scripts/test-gemini-hooks-secrets-scanner.sh` pointed at the Gemini secrets-scanner Python entrypoint and cover diff-only secret scanning, unchanged-secret suppression, and secret-like unified-diff header paths.
- For passive shadow logging, create shadow-log parent directory before first write and keep primary plus shadow writes inside same lock section so event ordering survives.
- When editing security-hook threat patterns or Tool Guard tests, avoid pasting raw dangerous strings directly into tool payloads; construct exact strings dynamically so active guards do not block self-edits.
- Keep simple hook input parsing in individual scripts when readability matters; do not move routine `jq` field extraction into `common.sh` only to dedupe a few lines.

## Validation route

- Run targeted checks from `.agents/memory/testing/hooks.md`.
- Distinguish repo-source proof from installed/live proof.

## Gemini-specific validator guidance

- For final-response quality validators, prefer `AfterAgent` over `AfterModel`.
- Use `prompt_response` as the text under review.
- Honor `stop_hook_active` to avoid retry loops.
