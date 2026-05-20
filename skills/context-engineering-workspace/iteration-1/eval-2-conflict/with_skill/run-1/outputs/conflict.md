CONFUSION:
- Rules say: Ask before changing financial behavior without explicit approval. (AGENTS.md)
- Spec says: Round invoice totals half up to the nearest cent. (docs/spec.md)
- Code says: round_total(value: float) -> float: return round(value + 0.0000001, 2) (src/invoice_math.py)
- Missing: Explicit approval or precedence decision: user requests bankers rounding, but spec requires half-up and rules require asking before changing financial behavior.
Options:
A) Implement bankers rounding as the user requests (change code to round half to even).
B) Follow docs/spec.md and keep half-up rounding (change/keep code to half-up).
C) Ask before proceeding
Which should I follow?
