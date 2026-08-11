CONFUSION:
- Rules say: Ask before changing financial behavior without explicit approval.
- Spec says: Round invoice totals half up to nearest cent.
- Code says: `round_total` does not implement bankers rounding; current behavior differs from requested change.
- Missing: Explicit approval for financial behavior change and direction on whether spec or request should win.
Options:
A) Keep code unchanged and follow existing spec/rule set.
B) Update spec first, then change rounding after explicit approval.
C) Ask before proceeding
Which should I follow?
