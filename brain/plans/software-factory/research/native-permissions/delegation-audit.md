# Native permission research delegation audit

Research date: 2026-10-14. All three independent research tasks completed before the ten-minute warning threshold. Parent checked progress and wall-clock time during execution. A later Copilot/Gemini follow-up only returned existing source paths for verification; no new research or edits were requested.

The runtime did not report executed model settings. Submitted values matched printed routes. Premium was selected for security-sensitive permission semantics using provisional catalog capability guidance. Available Premium sol configurations had comparable listed rates; latest gpt-6.1-sol was chosen, with gpt-6-sol/high as fallback. These are routing assumptions, not a measured benchmark or actual API cost claim.

```json
{
  "dispatches": [
    {
      "subtask_id": "codex_permissions",
      "selected": {
        "model": "gpt-6.1-sol",
        "reasoning_effort": "high"
      },
      "submitted": {
        "model": "gpt-6.1-sol",
        "reasoning_effort": "high"
      },
      "executed": {
        "model": "unconfirmed",
        "reasoning_effort": "unconfirmed"
      },
      "runtime_limit": {
        "value": "10-minute warning threshold",
        "mechanism": "Parent wall-clock/status checks; non-interrupting overrun message"
      },
      "routing_compliant": true,
      "status": "completed",
      "output_verified": true
    },
    {
      "subtask_id": "copilot_gemini_permissions",
      "selected": {
        "model": "gpt-6.1-sol",
        "reasoning_effort": "high"
      },
      "submitted": {
        "model": "gpt-6.1-sol",
        "reasoning_effort": "high"
      },
      "executed": {
        "model": "unconfirmed",
        "reasoning_effort": "unconfirmed"
      },
      "runtime_limit": {
        "value": "10-minute warning threshold",
        "mechanism": "Parent wall-clock/status checks; non-interrupting overrun message"
      },
      "routing_compliant": true,
      "status": "completed",
      "output_verified": true
    },
    {
      "subtask_id": "opencode_pi_permissions",
      "selected": {
        "model": "gpt-6.1-sol",
        "reasoning_effort": "high"
      },
      "submitted": {
        "model": "gpt-6.1-sol",
        "reasoning_effort": "high"
      },
      "executed": {
        "model": "unconfirmed",
        "reasoning_effort": "unconfirmed"
      },
      "runtime_limit": {
        "value": "10-minute warning threshold",
        "mechanism": "Parent wall-clock/status checks; non-interrupting overrun message"
      },
      "routing_compliant": true,
      "status": "completed",
      "output_verified": true
    }
  ]
}
```

Parent verification: read all reports and ticket resolutions; spot-checked OpenCode permission/run source and Pi security documentation through the web tool, Codex app-server documentation and retained local schema evidence, and Copilot/Gemini primary-source files fetched by the researcher through GitHub Contents API. Pinned GitHub/raw URLs for Copilot/Gemini returned parent web cache misses; the existing fetched source was used instead. Added the Copilot no-handler documentation/source conflict to the report. Product behavior remains untested. Link/status/cycle/whitespace checks are recorded in the feature handoff.

