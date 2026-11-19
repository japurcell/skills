# T1b, intent and attribution

After T1a gives the grader real trailer entries, update `eval_one` or the applicable scenario handler, `skills/default/commit/evals/evals.json`, fixture input and public grader tests together. Compare trailer entries with the scenario's independently specified issues and authors. Test unauthorized PR closure even when the PR also contains a neutral reference. Stop after the two intent cases and existing live Git workflow checks pass together.

The commit-skill implementer starts from the integrated T1a parser. Own the grader, intent fixtures, eval specification and related tests. Verify using the two CLI suites in the milestone. Stop with a paired neutral-reference and explicit-close scenario and passing existing workflow assertions.

Use the [milestone contract and verification commands](1-commit-validation.md) and the [integration plan](../ExecPlan.md). Record results and remaining evidence here.

## Result

On 2026-11-19 the implementer merged integration `059166bf` before starting. Through the public grader CLI, a valid neutral-reference result initially failed two assertions because both required `Fixes #456`. The revised paired scenario inputs independently specify issue 456, authorized `fixes` and the expected contributor. The grader compares parsed issue and co-author trailers in order, checks the reported subject, and checks PR references and closing directives separately. Neutral and explicit-close positive outputs pass; negative cases include unauthorized closure alongside a neutral reference, closure in prose without a trailer, missing, wrong or extra contributors, subject mismatch and extra closure. The existing live Git workflow tests remain independent.

Verification on the candidate tree: `python3 skills/default/commit/evals/test_validate_message.py` exited 0 (15 tests); `python3 skills/default/commit/evals/test_grade_benchmark.py` exited 0 (34 tests), including disposable Git workflow tests. The candidate commit identifies the tested revision.

Separately, eval 0's pre-existing skill anatomy assertion fails against the current `SKILL.md`: the assertion on `059166bf` requires headings absent from the file on that revision. It is unchanged and outside T1b; the eval 0 trailer-specific assertion passes and the negative prose-only case fails as intended. No live provider benchmark was run.

Reflection: independently specified fixture expectations and public negative cases now structurally capture the intent distinction. No further durable brain note or skill improvement was identified.
