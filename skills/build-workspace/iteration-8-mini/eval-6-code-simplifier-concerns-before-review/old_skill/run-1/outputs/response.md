Read the simplifier's concerns, classify them as a correctness/scope issue, and treat the work as unresolved. Re-dispatch the implementer (use the implementer-prompt + a lean handoff) with:
- the simplifier's concern text and the exact helper/function and files touched
- clear success criteria (original behavior preserved + tests)
- validation commands and the implementer's prior verification context
- only known file hints

Ask the implementer to narrow or revert the extraction (or add tests/adjust behavior) and return DONE. After that, re-run the code-simplifier, then the code-reviewer. Do not update tracking or commit until the final reviewer returns DONE.
