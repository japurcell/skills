The manager should **push that back to the implementer and re-dispatch**, not explore the repo or pre-solve it.

A correct response is essentially:

> **This is not a valid `NEEDS_CONTEXT`.** Under the build workflow, **repo discovery, pattern lookup, first-pass design, code changes, and verification are implementer work**. I should **not** pre-read the repo, draft the solution, or hand you likely patches.  
>  
> Please **load the minimum context yourself**: relevant code, tests, patterns, types, and commands; form the first-pass approach; then implement the task.  
>  
> Come back with `NEEDS_CONTEXT` only if you hit a **real missing requirement, missing constraint, or conflicting signal** you cannot resolve from the task, plan, repo rules, and codebase.

Why: the local build skill says:
- “**Do not** pre-read a large file set, draft the solution, or sketch likely patches before the first dispatch.”
- “**The implementer owns repo discovery, pattern lookup, first-pass design, code changes, and verification.**”
- “`**NEEDS_CONTEXT**` is for missing requirements, missing constraints, or conflicting signals — **routine discovery is not a valid `NEEDS_CONTEXT`**.”
- “If the implementer asks the manager to explore the repo or hand over a solution, **push that work back to the implementer**.”
