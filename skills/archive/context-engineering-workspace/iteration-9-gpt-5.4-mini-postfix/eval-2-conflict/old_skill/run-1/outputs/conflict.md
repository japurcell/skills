CONFUSION:
- Rules say: AGENTS says ask before changing financial behavior without explicit approval.
- Spec says: docs/spec.md says invoice rounding should round half up.
- Code says: src/invoice_math.py rounds away from zero.
- Missing: explicit approval to change financial behavior; user request for bankers rounding conflicts with spec and current code.
Options:
A) Keep half-up to match docs/spec.
B) Keep away-from-zero to match current code.
C) Ask before proceeding
Which should I follow?
