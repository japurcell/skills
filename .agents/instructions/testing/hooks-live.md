---
type: Agent Instruction
description: Use only for authorized installed-hook delivery, visible messages, timeouts, or deployment troubleshooting.
---

# Live Hook Evidence

Honor the task's installation scope and any user-reserved installation or enablement step. Follow [repository workflow](../repo.md) when installation is authorized, and refresh installed source before a live check; source tests do not prove what a provider executes.

- Use `scripts/probe-provider-hook-delivery.py --help` for the probe lifecycle. `prepare` mutates installed settings with nonce-tagged handlers; scope and back up exact destinations, retain marker/transcript paths, and always run probe `cleanup`, including after failed verification. Preserve unrelated user settings, custom instructions, and logs.
- Normal verification needs paired event/invocation entry and completion markers plus visible nonces. Handler runtime excludes provider startup-to-entry. A short runtime does not establish that a one-second provider deadline is met.
- Timeout verification needs entry, absent completion, and the expected visible timeout evidence. A harmless tool running after a timeout does not prove that the user saw a warning or that enforcement occurred.
- Copilot CLI needs a separate progress JSON line before its final decision for the probe's visible nonce. Inspect `~/.copilot/hooks/logs/observability.ndjson` or direct installed-script results as appropriate.
- VS Code diagnostics live in `GitHub Copilot Chat Hooks.log` and `GitHub Copilot Chat.log`.
- If VS Code omits `SubagentStart` for `runSubagent` child sessions, verify the direct `SubagentStart` hook is installed and use `SessionStart` as the fallback evidence.
- Require a live `AfterAgent` capability probe on the deployed Gemini version. For Gemini latency probes, set `GOOGLE_CLOUD_PROJECT` in the same child process as the CLI. Inspect each event independently.
- An empty Gemini override log does not establish missing dispatch. Check `$HOME/.gemini/hooks/logs/observability.ndjson`, then directly probe the installed emitter with the override to distinguish dispatch, environment propagation, and emitter failure.
- Keep scanner audit paths, Tool Guardian logs, and PTY transcripts outside disposable Git checkouts; untracked diagnostic files can become scanner findings. Remove only exact fake fixtures after recording evidence. On macOS, if `/usr/bin/git` fails through `xcrun` cache writes in the sandbox, use a verified native Git binary with `--no-optional-locks` for the safe-read probe.
- A force-push fixture must name a protected branch such as `main` for the configured rule; `HEAD` is not equivalent evidence.
- Existing-home installers preserve unowned and retired hook registrations. Verify a refreshed existing home separately from a fresh fixture, and leave manual removal of unrelated registrations to the user.

Run `rtk proxy python3 scripts/test-probe-provider-hook-delivery.py` when the probe contract changes. Keep native Windows and provider delivery claims separate from simulated envelope checks.
