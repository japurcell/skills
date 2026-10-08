# Task manifest evaluations

Run the public CLI from the repository root:

```sh
rtk proxy python3 skills/spec-to-tasks/evals/grade_benchmark.py <iteration-dir>
rtk proxy env PYTHONPYCACHEPREFIX=/private/tmp/task-grader-pycache python3 -m unittest discover -s skills/spec-to-tasks/evals -p test_grade_benchmark.py
```

Use one `iteration-N/eval-*/eval_metadata.json` beside configuration directories,
then `<config>/run-*/outputs/tasks.json`. Eval 1 uses the explicitly requested
`outputs/generated/tasks.json`. The metadata contains `eval_id`.

Exit zero means the CLI wrote grades. Read each run's `grading.json` assertions.
The grader checks generated tasks against the complete current task schema.

Schema, fresh defaults, graph order, explicit prerequisite IDs, available
references, and fixture-scoped requirement terms are deterministic checks.
File references resolve from the repository containing this grader, not from the
run directory or the CLI's current directory. The path must stay inside that
repository and the named Markdown heading must exist. Absolute, traversing,
Windows-style and NUL-containing paths fail reference validation. Inline source
and context use null path/section values with nonempty content.

Scenario checks preserve status defaults and inline controls, required browser
verification using playwright-cli for assigned status UI, the membership branch
name, membership and notification assignment titles, backend-only token scope,
and lifecycle current authority plus an integration assignment. Backend scope
allows database tables, retained rows, collection lists, query filters and access
controls. Explicit UI/browser cues or presentation wording still fail. These are
wording heuristics, not a general UI or scope classifier.

An unresolved check can satisfy the schema while failing verification readiness.
A known command may remain in an unresolved record when host/access is missing.
The lifecycle fixture intentionally supplies no executable project tooling, so
honest output remains unresolved rather than earning a readiness pass.

Read `user_notes_summary.needs_review` and perform model or human semantic review:
map each source requirement and negative case to an assignment, inspect actual
prerequisites, required context, boundary justification, decision authority,
verification applicability and command provenance, and final integration proof.
Text heuristics cannot verify general meaning, command availability, or whether
tests passed. Source quotations alone do not count as assigned coverage.
The public CLI tests use synthetic command records, including a hypothetical
mypy check. Their passing scores establish schema and scenario-check behavior,
not command provenance, available tooling or product execution.

Eval prompts preserve the original status, membership, notifications, and token
requirements. Lifecycle and inline documentation cases add interrupted recovery,
refusal, current authority, integration, unavailable tooling, and honest
documentation verification. Review artifact quality before comparing efficiency;
missing runtime metrics are unavailable, not measured zero.
Missing, invalid JSON or nonobject timing files leave duration unavailable;
object timing retains its supplied total_duration_seconds. The grader does not
validate every timing value or check whether a supplied duration was measured.
