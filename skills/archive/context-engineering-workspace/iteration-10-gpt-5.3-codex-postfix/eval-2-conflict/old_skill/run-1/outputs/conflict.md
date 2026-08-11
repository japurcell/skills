CONFUSION:
- Rules say: Ask before changing financial behavior without explicit approval.
- Spec says: Round invoice totals half up to the nearest cent.
- Code says: `round_total` currently rounds away from zero.
- Missing: Explicit approval to change financial rounding behavior to bankers rounding.
Options:
A) Keep current behavior and do not change rounding.
B) Change to half-up behavior to match spec.
C) Ask before proceeding
Which should I follow?
