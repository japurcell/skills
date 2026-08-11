---
name: adversarial-review
description: Critically review code/plans via adversarial expert subagent to find bugs, edge cases, security holes, and architectural flaws before merge.
disable-model-invocation: true
---

# /adversarial-review

Activate the `subagent-model-router` skill, spawn a subagent, and instruct it to adversarially review your work. The subagent should:

- be brutal and skip praise
- output a list of issues found, and suggest fixes

Using a subagent helps ensure objectivity because they get a fresh context window.
