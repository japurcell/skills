---
name: code-simplify
description: Simplify code for clarity and maintainability — reduce complexity without changing behavior
---

Activate or load the `addy-code-simplification` skill.

Simplify recently changed code (or the specified scope) while preserving exact behavior:

1. Activate or load the `subagent-model-router` skill and delegate tasks to the most suitable subagents whenever possible.
2. Read AGENTS.md and study project conventions
3. Identify the target code — recent changes unless a broader scope is specified
4. Understand the code's purpose, callers, edge cases, and test coverage before touching it
5. Scan for simplification opportunities:
   - Deep nesting → guard clauses or extracted helpers
   - Long functions → split by responsibility
   - Nested ternaries → if/else or switch
   - Generic names → descriptive names
   - Duplicated logic → shared functions
   - Dead code → remove after confirming
6. Apply each simplification incrementally — run tests after each change
7. Verify all tests pass, the build succeeds, and the diff is clean

If tests fail after a simplification, revert that change and reconsider.
