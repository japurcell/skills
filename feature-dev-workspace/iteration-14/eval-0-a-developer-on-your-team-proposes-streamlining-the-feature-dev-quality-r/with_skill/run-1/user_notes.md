Eval 0 — Merged review-and-simplify agent proposal

- Prompt: evaluate a proposal to merge code-simplifier and code-reviewer into a single agent
- Track applied: Light (question about the workflow itself)
- Key answer: Not acceptable. Phase 6 mandates both as separate, sequenced subagents using "always" for each
- Critical detail: code-simplifier runs BEFORE code-reviewer — merging destroys ordering guarantee
- Response cites Phase 6 Actions 1 and 2 directly; explains independence, ordering, and purpose distinction
