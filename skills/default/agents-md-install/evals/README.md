# Evaluation grading

Use the assertions in [evals.json](evals.json). Grade the effective instructions reached through root, applicable nested files, and referenced policy docs, not isolated keywords. Missing artifacts cannot establish a passing assertion.

## Update case: preserve the validation exception

The default is `npm run verify:all` before completing any change. The sole exception permits `npm run verify:web` instead for changes confined to web presentation. Evaluate these concrete tasks:

| Task | Required completion check |
| --- | --- |
| CSS spacing or color changes only | `npm run verify:web` is sufficient |
| Web form submission or validation behavior only | `npm run verify:all` |
| Service implementation changes | `npm run verify:all`, plus the existing service validation |
| Public API consumer behavior changed only under apps/web | `npm run verify:all` |
| Mixed presentation and behavioral changes | `npm run verify:all` |

The first three update assertions separately check the default, the exact exception condition, and the excluded cases. Fail preservation if any applicable instruction permits a weaker result for these tasks, even if another file retains the correct command. A specific condition may be preserved through a clear link; its exact wording need not be copied.

### Grader controls

Judge each control as a standalone complete policy, without importing rules from the input fixture or another control. In these examples, both commands run from the repository root.

| Control | Default | Presentation-only exception | Excluded cases |
| --- | --- | --- | --- |
| "Run `npm run verify:all` before completing changes. Only web presentation-only changes may use `npm run verify:web` instead; web behavior and shared contracts still require `npm run verify:all`." | Pass | Pass | Pass |
| "For web-only changes, `npm run verify:web` is sufficient." | Fail | Fail | Fail |
| "Run `npm run verify:all` for shared API contracts; use `npm run verify:web` for presentation." | Fail | Pass | Fail |
| Missing output | Fail | Fail | Fail |

For unresolved conflicting rules, fail each assertion whose effective policy is contradictory. Do not infer preservation from the response's claims. Even with a correct shared-contract rule elsewhere, permission to use only the focused check for all web-only work fails the presentation-condition and excluded-case assertions.

Keep input fixtures immutable during a run. When the fixture or rubric changes, rerun both skill and baseline against the same corrected input. Preserve earlier outputs and grades as historical evidence, label their rubric version, and do not carry old scores forward as results under the corrected assertions.

## Update case: direct migration route

Assertion 6 requires the service AGENTS.md itself to name schema or migration work as the trigger and link directly to the existing database document. A service README can remain the owner of the general workflow, but an AGENTS.md -> README -> database-doc chain fails this assertion. Resolve the actual relative link from the service guide; a filename mentioned in prose without a usable link does not establish the route.
