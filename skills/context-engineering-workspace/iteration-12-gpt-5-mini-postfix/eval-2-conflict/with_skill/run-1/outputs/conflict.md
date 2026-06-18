CONFUSION:
- Rules say: Ask before changing financial behavior without explicit approval. (AGENTS.md)
- Spec says: Round invoice totals half up to the nearest cent. (docs/spec.md)
- Code says: round_total currently rounds away from zero: `return round(value + 0.0000001, 2)`. (src/invoice_math.py)
- Missing: explicit approval to change rounding to bankers (round-half-to-even) and instruction which source to follow (user request vs repo spec).
Options:
A) Implement bankers rounding in code (change to round-half-to-even).
B) Keep spec's half-up behavior (no change).
C) Ask before proceeding.
Which should I follow?
