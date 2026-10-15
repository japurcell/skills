# Copilot and Gemini permission feasibility

**Type:** research
**Status:** closed
**Blocked By:** none
**Research Dir:** ../research/native-permissions/copilot-gemini

## Question

Which native Copilot and Gemini CLI, SDK, or protocol interfaces support permission requests and responses alongside concurrent factory sessions, live output, interruption, and foreground execution? Establish versioned primary-source evidence and native platform limits. Separate documented capability from live validation. Inform Human control and publication without adopting human policy.

---

Assigned 2026-10-14. Research only; no authenticated model jobs, installation, or product implementation.

## Resolution

Completed 2026-10-14. [Findings](../research/native-permissions/copilot-gemini/findings.md) pin Copilot CLI v1.0.97, SDK v1.0.21, and Gemini CLI v0.64.0 with primary documentation and source evidence. Prefer a live protocol bridge: Copilot SDK controlling local CLI, and Gemini ACP. Ordinary JSONL prompt modes do not supply a sufficient approval-response channel; a universal native-terminal handoff is unsupported. SDK policy parity, pending-request recovery, cancellation, sandbox escape, and native-platform behavior remain validation gates. Safe local Copilot help/version probes failed during protected-cache extraction; Gemini was absent. No authenticated invocation occurred.
