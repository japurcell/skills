---
name: adversarial-review
description: Critically review code/plans via adversarial expert subagent to find bugs, edge cases, security holes, and architectural flaws before merge.
---

# Adversarial Review

## Overview

Perform critical, adversarial reviews via subagents to find flaws, assumptions, edge cases, vulnerabilities, and architectural issues before finalization.

## Workflow

1. **Load Router:** Activate `subagent-model-router` to select review agent and tier.
2. **Draft Prompt:** Prompt subagent to find bugs, edge cases, vulnerabilities, and architectural flaws. Command it to be brutal and skip praise.
3. **Spawn Subagent:** Run the subagent sequentially using `invoke_agent` with `wait_for_previous: true`.
4. **Iterate:** Apply changes, update tests, and verify. Do not dismiss findings without logical refutations.

## Specific Techniques

### Adversarial Prompt Template

```markdown
You are a highly critical, adversarial senior engineer. Find bugs, logical errors, edge cases, performance issues, and security vulnerabilities. Be brutal; do not praise.

1. Under what inputs, concurrency, or edge cases will this fail?
2. What implicit assumptions were made and what happens if violated?
3. Where are security/auth gaps or leaks?
4. What automated tests are missing?
5. How can we simplify the architecture?
```

## Common Rationalizations

| Rationalization                  | Reality                                                                   |
| -------------------------------- | ------------------------------------------------------------------------- |
| "Tests passed, so no bugs."      | Passing tests prove expected paths work, not that edge cases are handled. |
| "Too simple to need review."     | Simple code often hides assumptions or off-by-one errors.                 |
| "Subagent will give style nits." | Strong adversarial prompts force focus on correctness and security.       |

## Red Flags

- Superficial feedback (e.g. "Looks good to me") or generic praise.
- Spawning subagent without choosing tier via `subagent-model-router`.
- Accepting "no issues found" without verified full context access.

## Verification

- [ ] Loaded `subagent-model-router` for agent/model selection.
- [ ] Invoked subagent with brutal, adversarial prompt.
- [ ] Provided subagent with full code/diff context.
- [ ] Addressed valid critiques and verified.
