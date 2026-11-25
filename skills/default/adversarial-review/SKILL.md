---
name: adversarial-review
description: Use when asked for an adversarial review.
compatibility: Requires an agent environment with subagent dispatch.
---

# /adversarial-review

Dispatch a subagent, and instruct it to adversarially review your work.

Prefer using a model from a different family when available. For example, if the work was done by a OpenAI GPT model, use an Anthropic model for the review.

The subagent should:

- When `brain/principles.md` exists, read it. Follow and read every linked principle file. These inform reviewer judgment.
- be brutal and skip praise
- output a list of issues found, and suggest fixes
- only suggest fixes; not implement them

Using a subagent helps ensure objectivity because they get a fresh context window.

## Red Flags

- The subagent implements fixes or makes any other changes.
