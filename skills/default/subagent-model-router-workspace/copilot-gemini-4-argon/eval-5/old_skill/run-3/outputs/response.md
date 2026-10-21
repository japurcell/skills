Yes, `fallback: none` is valid.

`SKILL.md` states: "Use `fallback: none` only if no other exact same-tier configuration meets runtime capabilities and user constraints. Explain what excludes the alternatives." Explicit user constraints take top selection precedence. Because `model-b` at `high` violates the user's explicit model-family constraint and no other `model-a`-family configuration is available, no other exact Standard configuration meets both runtime capabilities and user constraints.

```yaml
dispatchable: true
tier: Standard
model: model-a
reasoning_effort: high
reason: Standard configuration selected from fixture data. Only model-b at high is otherwise available in Standard, and it is excluded by the user's explicit constraint permitting only model-a's family. No other model-a-family configuration is available.
escalation_trigger: Escalate if verification exposes a reasoning gap or the task becomes security-sensitive, subject to updated user constraints or dispatchable: false if the constraint blocks escalation.
fallback: none
```
