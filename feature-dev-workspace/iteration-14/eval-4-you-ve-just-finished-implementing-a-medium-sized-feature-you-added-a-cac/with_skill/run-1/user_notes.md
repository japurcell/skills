Eval 4 — Phase 6 walkthrough for caching layer (Python web app, 3 service files)

- Prompt: walk through Phase 6, name exact subagents, focus, order
- Track: Standard (3-service file change)
- Step 1: code-simplifier — focus on duplication between cache integration points, key construction, flattenable logic
- Step 2: 3 code-reviewer agents in parallel — correctness (invalidation, thread safety, error handling), conventions (naming, abstraction match), simplicity (minimal implementation)
- Ordering: code-simplifier BEFORE code-reviewer — explicitly stated and reason given
- Key fact from skill: code-simplifier listed as Action 1, code-reviewer as Action 2 in Phase 6
