CONFUSION:
- Rules say: Ask before changing financial behavior without explicit approval.
- Spec says: Round invoice totals half up to the nearest cent.
- Code says: `round_total()` currently uses `round(value + 0.0000001, 2)`, which is not bankers rounding.
- Missing: Explicit approval to change invoice rounding behavior to bankers rounding.
Options:
A) Keep current behavior and do not change code.
B) Change rounding behavior only after explicit approval.
C) Ask before proceeding.
Which should I follow?
