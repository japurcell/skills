# False-Positive Rubric

Score each candidate finding using the reviewed change, code, specs, and standards. Intermediate scores are allowed.

- 0: False positive; does not survive light scrutiny.
- 25: Possible issue, but not verified. Stylistic issues score here unless explicitly required by standards.
- 50: Verified issue, but minor, uncommon, or low impact.
- 75: Very likely real and important, likely hit in practice, or directly supported by standards.
- 100: Definitely real, frequent, and directly confirmed by evidence.

## Keep rule

Keep only findings scored 80+.

## Standards rule

A standards finding must cite an explicit rule in a relevant standards file. Otherwise score below 80.

## Required evidence

Every kept finding must include:

- concrete file reference
- change linkage
- practical impact
- fix recommendation
