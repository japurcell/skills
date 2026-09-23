# RTK Setup Warning

**Type:** grilling
**Status:** closed
**Blocked By:** none
**Research Dir:** none

## Question

How should agent-issued, explicit `rtk` commands suppress the misleading `No hook installed` notice across providers and platforms using an available RTK build, while preserving other RTK diagnostics and command behavior?

---

## Resolution

Suppress RTK's missing-hook notice on explicit `rtk` commands issued inside Copilot, Gemini, and Codex agent sessions, on every supported platform where the notice is misleading. Keep RTK's user-global configuration and normal terminal command unchanged. Stable [v0.49.0](https://github.com/rtk-ai/rtk/releases/tag/v0.49.0) lacks the setting, but the already-published [dev-0.50.0-rc.451 release](https://github.com/rtk-ai/rtk/releases/tag/dev-0.50.0-rc.451) contains the `RTK_SUPPRESS_HOOK_WARNING=1` feature from [PR #776](https://github.com/rtk-ai/rtk/pull/776). Pin the release tag and verify each platform asset against its published checksum. No future release is required.

Install the pinned build alongside stable RTK. Provider pre-tool hooks should rewrite explicit `rtk` commands in agent sessions to invoke that build with `RTK_SUPPRESS_HOOK_WARNING=1` scoped to the command; Codex needs RTK pre-tool registration. Preserve shell quoting, command chains, arguments, stdout, stderr, and exit codes. If a provider path cannot safely rewrite a command, agent instructions should use the pinned build with a command-scoped environment variable on that path. Leave unrelated commands and quoted text untouched. Do not set a global environment variable, edit global RTK config, fake a Claude hook installation, or filter stderr. The suppression flag targets the missing-hook notice; other diagnostics must remain visible.

The notice originates from the RTK CLI invocation. Repository RTK forwarders in `hooks/families/rtk.py:187-220` capture and discard RTK stderr, so they cannot directly display it. Recent Codex session logs show the notice at the start of output from explicit `rtk read` commands, including [2026-09-22 tool output](/Users/adam/.codex/sessions/2026/09/22/rollout-2026-09-22T14-30-22-01a0cb06-e92e-7253-af24-d3440bb7a214.jsonl). The same behavior was reported by the user in Copilot and Gemini. These observations establish command output as the target; they do not prove every automatic hook is installed.

An isolated, checksum-verified macOS arm64 test of `dev-0.50.0-rc.451` confirmed that default prerelease behavior still prints the notice, while `RTK_SUPPRESS_HOOK_WARNING=1` hides it. With the flag, an outdated-hook prompt remained visible, a missing-file error remained visible, and RTK kept the correct exit codes. Stable v0.49.0 still prints the notice with the flag. The prerelease archive SHA-256 matched its release checksum (`05a32507b07dc38bca835808deb8f32bd182446e8adc90b00209deda0404d321`). The prerelease binary unexpectedly reports `rtk 0.48.0` under `--version`, so use release tag, asset checksum, and functional checks to identify it; do not use the version string as proof. The verified binary was installed side by side at `/Users/adam/.local/bin/rtk-dev-0.50.0-rc.451`; default `/Users/adam/homebrew/bin/rtk` remains v0.49.0. No provider agent session was switched.

An isolated hook smoke test returned valid rewrite JSON for a Gemini `BeforeTool` payload and exit code `0` for Copilot and Codex payloads, but those two emitted no JSON; their input shapes or no-op behavior need investigation before claiming compatibility. Before switching agent sessions, the ExecPlan must test provider hook compatibility with the pinned binary and rewritten explicit commands across Copilot, Gemini, and Codex on supported shells, including native Windows PowerShell and chained commands. Quoted text containing `rtk` must remain untouched. Test exact notice suppression, other diagnostics, stdout, arguments, and exit codes. Pin and checksum-verify the Windows asset separately. The Windows live-check checklist confirms installed behavior; a live run is not an acceptance gate. Existing RTK hook tests use fake binaries, so passing them alone does not establish prerelease compatibility.
