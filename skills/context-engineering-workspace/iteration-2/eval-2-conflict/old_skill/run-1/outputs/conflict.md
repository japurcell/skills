CONFUSION:
- Rules say: Ask before changing financial behavior without explicit approval (AGENTS.md).
- Spec says: Round invoice totals half up to the nearest cent (docs/spec.md).
- Code says: src/invoice_math.py currently adjusts the value and uses Python rounding (implemented as round(value + 0.0000001, 2)), which behaves differently from bankers rounding and has been described as rounding away from zero.
- Missing: Explicit stakeholder approval, a decision to adopt bankers rounding (round half to even), and tests specifying the desired tie-breaking behavior.
Options:
A) Change code to bankers rounding (round half to even) and update spec/docs/tests.
B) Update spec/docs to match the current implementation (round half up/away-from-zero) and keep code as-is.
C) Ask before proceeding
Which should I follow?
