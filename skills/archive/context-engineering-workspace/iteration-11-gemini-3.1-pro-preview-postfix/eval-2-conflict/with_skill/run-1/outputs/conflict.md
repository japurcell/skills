CONFUSION:
- Rules say: Ask before changing financial behavior without explicit approval.
- Spec says: Round invoice totals half up to the nearest cent.
- Code says: `return round(value + 0.0000001, 2)` (rounds away from zero)
- Missing: Explicit approval to change financial behavior to bankers rounding

Options:
A) Change rounding to bankers rounding (user request)
B) Change rounding to half up (spec)
C) Ask before proceeding

Which should I follow?
