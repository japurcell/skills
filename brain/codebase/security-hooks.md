# Security hooks

- Tool Guardian must conservatively handle unknown shell syntax, sinks, and payload schemas. Do not weaken unknown-input policy to pass fixtures.
- Secret scanning runs at explicit checkpoints and publication gates. A historical clean status is not permission to publish changed content.
- Expected blocking behavior uses provider-native denial JSON at exit 0; infrastructure failure and clean results remain distinct.
- Never log raw tool inputs, credential text, or complete subprocess stderr. Redact the full credential span.
- Keep bounded private capture files and platform-native descendant cleanup. Native Windows job-object behavior needs native Windows proof.
- RTK forwarding errors record status without copying unbounded subprocess diagnostics. Empty successful RTK output is a valid no-op.
- Codex uses explicit RTK commands; automatic forwarders remain Copilot/Gemini-specific.

Evidence: `hooks/families/tool_guard.py`, `hooks/runtime/`, and [[security-testing]], checked 2026-10-20. Recheck policy, process isolation, or capture changes.
