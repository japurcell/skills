---
name: code-simplify-team
description: Simplify code for clarity and maintainability — reduce complexity without changing behavior
---

Invoke the `addy-code-simplification` skill.

Simplify the target scope while preserving exact behavior.

1. Read `AGENTS.md` and follow repository conventions.

2. Define scope:
   - default to recent changes unless the user specifies otherwise
   - identify in-scope source files, related tests, and any files needed for understanding
   - do not expand scope unless required for correctness; note any expansion first

3. Understand before editing:
   - determine purpose, control flow, dependencies, callers, invariants, edge cases, and expected behavior
   - inspect tests
   - do not simplify code you do not understand

4. Use 2–4 subagents only when parallel work is likely to outweigh coordination overhead; otherwise use a single agent.

5. If using 2–4 subagents:
   - build a complete manifest of in-scope files
   - exclude generated, vendored, third-party, and build-output files unless explicitly in scope
   - partition files into 2–4 disjoint bundles covering the full in-scope set exactly once
   - group by language/file type first, then feature/module/package/directory
   - keep reusable or duplicated logic together, keep tests with corresponding production files when practical, and assign shared utilities/types/base classes/core cross-cutting files to exactly one owner
   - prefer same-language cohesion over perfect balance unless imbalance is substantial
   - balance by simplification effort, coupling, and complexity, not file count
   - output a partition plan with each subagent’s name, owned files, focus, rationale, expected themes, and cross-bundle dependencies
   - confirm every in-scope file is assigned exactly once
   - optionally invoke `subagent-model-selection` to choose the smallest sufficient model for each bundle
   - dispatch `code-simplifier` subagents that may read any in-scope file for context but modify only owned files; cross-bundle opportunities should be reported, not edited directly

6. Simplify by preferring local, behavior-preserving changes:
   - reduce nesting, clarify branching, split overly large functions, improve names, extract local duplication, and remove dead code when safe
   - improve readability and maintainability without broad architectural rewrites
   - avoid changing externally visible interfaces or other observable behavior unless verified safe

7. Verify incrementally:
   - make small changes
   - run the narrowest relevant tests after each change
   - if no relevant tests exist, use build, lint, typecheck, or other available signals and note the verification gap
   - revert any change that fails tests or introduces uncertainty
   - do not build on unverified changes

8. Synthesize and verify:
   - consolidate simplifications across bundles
   - identify reusable code candidates and follow-up extraction or coordinated refactor opportunities without performing broad cross-bundle rewrites unless explicitly requested
   - run relevant tests and broader verification appropriate to scope
   - verify the build succeeds
   - confirm the diff is minimal, coherent, and behavior-preserving
   - summarize what was simplified and why it is safe

If behavior preservation cannot be established, stop and explain the uncertainty before proceeding.
If tests fail after a simplification, revert that change and reconsider.
