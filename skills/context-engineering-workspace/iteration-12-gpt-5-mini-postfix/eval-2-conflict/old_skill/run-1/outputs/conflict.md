CONFUSION:
- Rules say: AGENTS.md requires asking for approval before changing financial behavior.
- Spec says: docs/spec.md requires "round half up" (round halves up).
- Code says: src/invoice_math.py currently implements rounding away from zero (not bankers rounding).
- Missing: explicit stakeholder approval to change invoice rounding to bankers rounding (round-half-to-even) and explicit precedence decision.
Options:
A) Update code to bankers rounding (round half to even) — requires explicit approval per AGENTS.md.
B) Keep current implementation (away-from-zero) — preserves code but conflicts with spec.
C) Ask before proceeding (follows AGENTS.md; recommended).
Which should I follow?
