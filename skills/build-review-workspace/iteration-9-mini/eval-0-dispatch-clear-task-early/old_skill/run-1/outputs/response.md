Per `skills/build-review/SKILL.md`, the manager should:

1. Invoke `addy-context-engineering` and `subagent-model-selection`.
2. Pick the next pending plan task.
3. If it’s ambiguous, conflicts with the plan, or needs tradeoff analysis, stop and resolve that first.
4. Otherwise dispatch the implementer immediately with the lean handoff template.

**Handoff should include:**
- the task text
- the success criteria / acceptance criteria
- known constraints
- known validation commands
- only already-known file hints

**Must stay with the implementer:**
- repo discovery
- pattern lookup
- first-pass design
- reading relevant code/tests/types/commands
- writing the failing test
- implementing the minimum change
- choosing and running the narrowest validations
- reporting back

Also, the manager should not pre-read large file sets, draft the solution, or sketch patches before dispatch.
