# RTK Setup Warning

**Type:** grilling
**Status:** open
**Blocked By:** none
**Research Dir:** none

## Question

How should agent-issued, explicit `rtk` commands suppress the misleading `No hook installed` notice across providers and platforms, while preserving other RTK diagnostics? Decide how the suppression setting reaches those commands and what evidence proves it works.

---

## Pending discussion

The user confirmed that the warning appears in output of explicit `rtk` commands, wants only the misleading missing-hook notice hidden, and wants the same remedy on any platform where it occurs. The user chose a stable upstream RTK suppression feature over a workaround for RTK 0.49. The earlier choice of agent-scoped hook rewrites over global RTK configuration needs revalidation: it was made before the user corrected the assumption that hook execution created the visible warning. Final confirmation of the corrected decision is pending.

Repository RTK forwarders capture and discard RTK stderr, so they cannot directly display this warning. Recent Codex session logs show the notice at the start of output from explicit `rtk read` commands, including [2026-09-22 tool output](/Users/adam/.codex/sessions/2026/09/22/rollout-2026-09-22T14-30-22-01a0cb06-e92e-7253-af24-d3440bb7a214.jsonl). The local RTK 0.49 binary lacks the suppression setting; [upstream development documentation](https://github.com/rtk-ai/rtk/blob/develop/docs/guide/getting-started/configuration.md) describes `RTK_SUPPRESS_HOOK_WARNING=1`, which suppresses the missing-hook notice while preserving the outdated-hook prompt. The eventual ExecPlan must verify that a stable release supports the setting before relying on it. Codex currently lacks RTK pre-tool wiring, so hook-based delivery there requires new registration.
