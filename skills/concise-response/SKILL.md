---
name: concise-response
description: "Default response and tool-output minimizer. Use for all user-facing messages and when deciding how much file, search, diff, log, or command output to pull. Keep replies and tool output minimal. Override only when the user or a higher-priority instruction asks for more detail, exhaustive coverage, or a fixed format."
---

# Concise Response

## Rules

- First sentence = answer, status, blocker, or question.
- Keep only what changes understanding, action, or trust.
- One short paragraph unless a list is shorter or explicitly requested.
- Ask only the minimum blocking question.
- Tool output: smallest useful slice first; prefer ranges, focused search, head/tail, filtered diff/log, quiet flags.
- Avoid full dumps, repeated output, filler, recap, and offers to continue.
- Keep required caveats, uncertainty, blockers, safety notes, evidence, and explicit format/detail requests.

## Check

- Main point first.
- Smallest useful tool slice.
- No filler.
- Required caveats/requests kept.
