# False-Positive Rubric

For each candidate issue, score whether it is real using the issue, reviewed change, relevant code, and relevant standards files.

Use this rubric verbatim:

- 0: Not confident at all. This is a false positive that doesn't stand up to light scrutiny.
- 25: Somewhat confident. This might be a real issue, but may also be a false positive. The agent wasn't able to verify that it's a real issue. If the issue is stylistic, it is one that was not explicitly called out in the relevant standards file.
- 50: Moderately confident. The agent verified this is real, but it may be minor or uncommon.
- 75: Highly confident. The agent verified it is very likely real and important, will be hit in practice, or is directly mentioned in the relevant standards file.
- 100: Absolutely certain. The agent confirmed it is definitely real and will happen frequently in practice; the evidence directly confirms this.

## Filtering rule

Only keep findings with score 80 or higher.

## Standards findings

For standards findings, the relevant standards file must explicitly support the finding. If the standards file does not explicitly support the finding, score below 80 and filter it out.

## Evidence requirements

A kept finding must include:

- concrete file reference
- explanation of why the issue is introduced by, exposed by, or clearly reachable through the reviewed change
- practical impact
- fix recommendation
