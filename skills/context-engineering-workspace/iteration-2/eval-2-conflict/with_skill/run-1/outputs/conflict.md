CONFUSION:
- Rules say: Ask before changing financial behavior without explicit approval. (AGENTS.md)
- Spec says: Round invoice totals half up to the nearest cent. (docs/spec.md)
- Code says: Current implementation uses round(value + 0.0000001, 2) — effectively rounding halves away from zero.
- Missing: Explicit approval to change financial behavior per AGENTS.md; precedence decision between the user's instruction and repo spec; tests showing the expected rounding behavior.
Options:
A) Implement bankers rounding (round half to even) now per the user's request (would diverge from the repo spec and may violate AGENTS.md).
B) Update code to match the repo spec (round half up) and request explicit approval before changing financial behavior.
C) Ask before proceeding
Which should I follow?
