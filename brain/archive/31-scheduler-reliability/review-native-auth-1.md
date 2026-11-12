# Native authentication and evidence review

Reviewed base `2470dac6f5ed0fb17577bf5e9155e5a292e44a28`, target `598e706f6e85d7579ce85c896ef1efb781c1fe91`, merge base `2470dac6f5ed0fb17577bf5e9155e5a292e44a28`. This new auth/configuration/evidence scope is separate from the closed original EOF review cycle. Standards reports zero findings. Spec reports zero findings. Source is accepted; native execution qualification remains pending.

Diff SHA-256 `7bf1841233e87ac0e9596a4b72f4aa717e4fef4cec2662c2257495698fcff711`; review archive SHA-256 `976fa372de7ae29214eee7d9135c2dacf6c3d7f1482283c79e0ecc0de890c19e`. [Pinned metadata](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-native-auth-1/source.json), [diff](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-native-auth-1/diff.patch), [log](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-native-auth-1/commits.txt) and [archive](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-native-auth-1/source.tar). All 13 current package files match the reviewed target. Final three-file hashes match the retained 52-test suite, 213.254 seconds (outer 213.299), without rerunning tests. [Suite receipt](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-codex-native-b2/full-suite-overlap-final.json).

## Standards

## Verdict

APPROVE for the Standards axis. Zero Critical findings, zero Important findings and zero actionable heuristic advisories.

Reviewed the pinned `2470dac6f5ed0fb17577bf5e9155e5a292e44a28...598e706f6e85d7579ce85c896ef1efb781c1fe91` diff and commit log. Scope covers the new native authentication/configuration/evidence adapters, public fixtures and changed documentation. The closed original EOF review remains historical.

## Documented standard breaches

None confirmed against all seven standards listed in `source.json` and the supplied global rules.

- `scheduler_pilot.py:68`, `:174`, `:625` and `:778` retain allowlisted behavior/status, exclude credential-bearing values, validate native inventories and preserve bounded subprocess cleanup. These follow `brain/codebase/live-hook-testing.md`, Native authentication and adapter boundaries, and `brain/codebase/scripts-and-installers.md`, Authoring and execution.
- `scheduler_pilot.py:1072`, `:1189` and `:1366` bind retained raw rollout, current file bytes, ordered tool observations and policy audit. The independent evidence layers align with `skills/default/create-skill/references/validation.md`, Assertions and graders, and `brain/codebase/script-testing.md`, Fixtures that must remain meaningful.
- `test_scheduler_pilot.py:1301`, `:1370`, `:1402`, `:1415` and `:1476` exercise public transitions, real helper/scheduler children, complete scenarios and adversarial evidence mutations. `evals/README.md:173`, `:211` and `:221` distinguish offline proof, native metadata and pending actual execution qualification. Changed plan/readiness documentation retains pending trust/live-call prerequisites.

## Heuristic smells

Applied every supplied smell category. The substantial single-file growth warranted inspection, but the added configuration and evidence checks have concrete native consumers and preserve the existing bounded harness entry points. No consequential duplication, speculative abstraction or other actionable smell met the reporting threshold.

## Verification and limits

All three archived harness/test/README hashes match `T4-codex-native-b2/full-suite-overlap-final.json`, whose retained suite exited 0 in 213.299 seconds. The supplied run reports 52 tests. Independently exercised public `--help`, which exited 0 and documented streams/statuses. No broad suite rerun, live provider call, authentication or trust action occurred. Native execution qualification remains pending.

[Original Standards report](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-native-auth-1/standards.md).

## Spec

No substantive Spec findings in the reviewed new native-authentication, effective-configuration, context/command/patch qualification and complete-scenario scope.

Reviewed the pinned snapshot for `2470dac6f5ed0fb17577bf5e9155e5a292e44a28...598e706f6e85d7579ce85c896ef1efb781c1fe91` against the inline T4-AUTH, T4-CODEX-A/B1/B2 and current observed-run acceptance contract in `brain/plans/31-scheduler-reliability/ExecPlan.md`. Inspected the captured diff and implementation/fixtures for native auth environment separation, safe projections and drift gates, bounded metadata discovery, shell startup isolation, companion selector/context binding, ordered policy-audit reconciliation, literal patch authoring/current bytes and complete real-child scenarios.

The specification explicitly requires that "Current actual native hook input/patch-audit association remains smoke-unproven" and that "Current smokes must prove actual hook, selector and command mapping before scenarios." The source retains both-variant smoke qualification and dependent-scenario stop gates. Native execution qualification remains pending, as recorded in the plan.

This is a static source/spec review. I did not reproduce a current failure or rerun tests. The supplied exact-final-source 52-test result supports offline fixture acceptance, while actual native patch/hook association and executing selector still require the separately approved current-payload smokes. The earlier closed EOF review cycle was excluded.

[Original Spec report](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-native-auth-1/spec.md).
