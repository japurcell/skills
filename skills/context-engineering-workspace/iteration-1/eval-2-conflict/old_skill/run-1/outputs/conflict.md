CONFUSION:
- Rules say: If code, spec, rules, and request conflict, ask before acting; follow repository precedence (user instruction > repo/local rules > global/user rules > this skill). AGENTS.md and the skill advise surfacing ambiguities before changing financial behavior.
- Spec says: Round invoice totals half up to the nearest cent. (docs/spec.md)
- Code says: src/invoice_math.py implements round_total(value) as `round(value + 0.0000001, 2)`, effectively rounding away from zero.
- Missing: Explicit approval from repository maintainers to change financial rounding to bankers rounding (round-half-to-even); tests and migration plan.
Options:
A) Implement bankers rounding now (change code) — requires explicit approval and tests.
B) Implement spec (round half up) — change code to match docs; requires approval and tests.
C) Ask before proceeding (recommended).
Which should I follow?
