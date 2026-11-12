---
name: adversarial-review
description: Use when asked for an adversarial review.
compatibility: Requires an agent environment with subagent dispatch.
---

# /adversarial-review

Activate the `delegate-to-subagents` skill, dispatch a subagent, and instruct it to adversarially review your work. The subagent should:

- be brutal and skip praise
- output a list of issues found, and suggest fixes
- only suggest fixes; not implement them

Using a subagent helps ensure objectivity because they get a fresh context window.

## Red Flags

- The subagent implements fixes or makes any other changes.
