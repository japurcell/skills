# RTK Setup Warning

**Type:** grilling
**Status:** closed
**Blocked By:** none
**Research Dir:** none

## Question

How should agent-issued, explicit `rtk` commands suppress the misleading `No hook installed` notice across providers and platforms, while preserving other RTK diagnostics? Decide how the suppression setting reaches those commands and what evidence proves it works.

---

## Resolution

Suppress RTK's missing-hook notice on explicit `rtk` commands issued inside Copilot, Gemini, and Codex agent sessions, on every supported platform where the notice is misleading. Keep RTK's user-global configuration unchanged. The provider's pre-tool hook should add `RTK_SUPPRESS_HOOK_WARNING=1` to each explicit RTK process through its supported command rewrite, using shell-appropriate syntax. If a provider execution path cannot apply a safe rewrite, its agent instructions must supply the same per-command setting. Codex needs new RTK pre-tool registration. The user previously chose agent-scoped hook rewrites and directed work to continue after correcting the warning's origin; this resolution retains that scope and targets the actual command.

Use this setting only after verifying that a stable RTK release supports it. The [latest stable release](https://github.com/rtk-ai/rtk/releases/latest) is v0.49.0, whose [configuration documentation](https://github.com/rtk-ai/rtk/blob/v0.49.0/docs/guide/getting-started/configuration.md) does not list suppression. [Upstream development documentation](https://github.com/rtk-ai/rtk/blob/develop/docs/guide/getting-started/configuration.md) describes `RTK_SUPPRESS_HOOK_WARNING=1` as hiding only the missing-hook notice, not the outdated-hook prompt. Do not add an output-text filter or RTK 0.49 workaround. Keep real RTK errors and outdated-hook prompts visible.

The notice originates from the RTK CLI invocation. Repository RTK forwarders in `hooks/families/rtk.py:187-220` capture and discard RTK stderr, so they cannot directly display it. Recent Codex session logs show the notice at the start of output from explicit `rtk read` commands, including [2026-09-22 tool output](/Users/adam/.codex/sessions/2026/09/22/rollout-2026-09-22T14-30-22-01a0cb06-e92e-7253-af24-d3440bb7a214.jsonl). The same behavior was reported by the user in Copilot and Gemini. These observations establish command output as the target; they do not prove every automatic hook is installed.

The ExecPlan must verify the stable RTK setting, then test rewritten explicit commands across all three providers and supported shells, including native Windows PowerShell and chained commands. Tests must show that the missing-hook notice disappears, command results and exit codes remain intact, and other RTK diagnostics remain visible. The Windows live-check checklist confirms installed behavior; a live run is not an acceptance gate.
