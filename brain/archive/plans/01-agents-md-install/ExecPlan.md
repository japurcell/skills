# Replace overlapping AGENTS.md skills

This living plan is governed by the repository's exec-plans skill.

## Purpose / Big Picture

Deliver `skills/default/agents-md-install` so an explicit invocation creates or updates a project's root and appropriate nested AGENTS.md files and conditional reference documentation. Replace the two old published skills after verification. Tool-specific bridges, runtime configuration, application code, and user-global installations are outside scope.

## Progress

- [x] (2026-10-21) [milestone-1] T1: Research all seven requested sources and resolve conflicting policies with the user.
- [x] (2026-10-21) [milestone-1] T2: Author the replacement, source rationale, and evaluation scenarios; quick_validate.py reports valid.
- [x] (2026-10-21) [milestone-2] T3: Exercise creation, update, and audit-only behavior; retain original failures and corrected outputs with provenance.
- [x] (2026-10-21) [milestone-2] T4: Validate the bundle, retire both old skills, archive todo 1, and complete reflection review.
- [x] (2026-10-21) [milestone-3] T5: Reproduce the exception-preservation false pass from retained output; clarify fixture policy and split its assertions.
- [x] (2026-10-21) [milestone-3] T6: Rerun both configurations against corrected input; independent review confirms the exact exception and direct migration route, with 8/8 skill assertions and all five policy traces passing.

## Surprises & Discoveries

- The requested `~/.agents/skill/agents-md-improver/SKILL.md` does not exist. The plural `skills` path exists and matches the published workflow.
- The GitHub blog source describes custom agent personas, not the root instruction file format. Only its actionable-command, example, and boundary advice transfers.
- Old skills are discovered by directory; maintained source search found no installer or README references needing renaming.
- Iteration 1: historical grades reported 15/16 in both configurations, but the exception-preservation assertion was subsequently found too weak. Both update runs substituted a service README for the required nested AGENTS.md. The skill now explicitly distinguishes reference reuse from the mandatory scoped entry point. Creation also exposed an overly broad contributor-guide route; the skill now requires checking the content behind pointers.
- Adversarial review found that iteration 2 dropped the presentation-only condition while its grade passed preservation. The fixture's root also allowed broader web-only checks, making the input ambiguous. Iteration 3 corrects both the policy and rubric; previous update grades do not establish current acceptance.
- Independent iteration-3 grading confirms all five validation-policy traces in both runs. It also found that the skill run routed migrations through the service README. Iteration 4 clarifies the runtime requirement for direct conditional links and strengthens assertion 6 before rerunning both configurations.

## Decision Log

- 2026-10-21: User accepted minimal shared root guidance, nested scope guidance, and explicit task-triggered links. No mandatory comprehensive root template or numeric score.
- 2026-10-21: User accepted restructuring, deduplication, and evidence-backed removal of stale material while preserving valid requirements.
- 2026-10-21: User accepted install/update authorization without a redundant approval report; unresolved policy conflicts still require questions. Audit-only remains read-only.
- Preserve both predecessors' `disable-model-invocation: true`. Use prose instructions and references, not a generator that guesses project policy.

## Outcomes & Retrospective

Delivered the replacement and retired both old published bundles. Creation and audit evidence remains valid. Independent iteration-4 review confirms both follow-up P2s resolved: the skill run passes 8/8 corrected update assertions and all five validation-policy traces; the fresh no-skill baseline passes 7/8, missing the service entry point. Both configurations preserve the exact presentation-only exception. The historical 16/16 versus 15/16 totals are superseded, not recomputed as comparable results. A fresh repeated update preserved the layout and added one omitted fixture validation caveat; strict byte-for-byte idempotence is not established. No population-level performance improvement, user-global installation, or commit is claimed.

Reflection reviewed the false-pass cause and follow-up route miss. The lesson is encoded in the maintained fixture's explicit default/exception, separate assertions, positive/negative/missing-output controls, and five task traces. Direct-route verification is also explicit in the runtime skill and rubric. No duplicate brain note or unrelated authoring-skill edit is needed.

## Context and Orientation

Published bundles live under `skills/default/`; installers enumerate their directories. Predecessor bundles were `agents-md-improver` (four Markdown files with additive-only updates and a mandatory approval report) and `create-agentsmd` (one comprehensive root template and explicit-only Codex metadata). Preserve their useful discovery, command verification, actionable conventions, current links, scoped guidance, reporting, and invocation boundaries. User decisions supersede their additive-only, mandatory-template, and repeated-approval policies.

## Plan of Work

### Milestone 1: A portable replacement

Status: done
Acceptance: met

T1 has no prerequisites and is complete. T2 depends on T1. Write `SKILL.md` with discovery, evidence, scope placement, safe updating, and verification. Add a directly linked update reference, a placement reference, a maintainer README with prioritized source rationale and obligation mapping, and `evals/evals.json` plus fixture documents. Each reference has a distinct loading trigger. Existing target documents remain authoritative; compatibility bridges stay untouched.

### Milestone 2: Verified behavior and retirement

Status: done
Acceptance: met

T3 depends on T2. Run the same creation, update, and audit prompts with the exact local skill and without it in separate disposable copies. Grade actual outputs for scoped nesting, conditional routes, preserved policies, existing-document reuse, bridge preservation, and audit immutability. Retain outputs and results in the sibling `agents-md-install-workspace/` directory. Record missing timing/token metrics honestly. Generate the standard static review viewer.

T4 depends on T3. Run `rtk python3 scripts/validate-skill-sources.py skills`, the skill creator's `quick_validate.py` on the new bundle, local Markdown link checks, and `rtk git diff --check`. Retire the six predecessor files after new behavior passes, preserving the explicit-only Codex metadata in the replacement. Remove empty old directories so source validation succeeds. Archive todo 1, reconcile brain indexes, and review reflection guidance. No commit or user-global installation is requested.

### Milestone 3: Repair exception-preservation evidence

Status: done
Acceptance: met

T5 follows the adversarial review and is complete: retain the original false-pass evidence, define a full-check default with one presentation-only exception, and separate the preservation assertions. T6 depends on T5: run both configurations against the identical corrected fixture, independently assess the five task traces in `evals/README.md`, and retain per-assertion evidence. A grader must reject the broad web-only negative control and accept the exact exception. Revalidate the bundle and reconcile current claims; do not rewrite earlier outputs or grades as new measurements.

## Concrete Steps

No correction work remains. `skills/default/agents-md-install-workspace/iteration-4/review.html` presents the fresh update runs and independently reviewed grades. Its immutable input, exact skill snapshot, deterministic checks, and provenance are retained alongside outputs. Iterations 1 and 2 are historical evidence under the original weak rubric. Iteration 3 proves the corrected validation exception but does not establish direct migration reachability.

## Validation and Acceptance

Observed after correction: source/bundle validation, JSON parsing, local links, and whitespace checks pass. Independent iteration-4 grading passes all eight skill assertions and all five task traces. The focused check is sufficient only for presentation-only changes; behavior, service, shared-contract, and mixed changes retain the full check. The service guide links migration guidance directly. Byte comparisons confirm both compatibility files and non-documentation inputs are unchanged in both runs, and the input fixture remained immutable. Grader controls accept the precise policy and reject broad-web, missing-default, and missing-output cases as specified by the rubric.

Iteration 1 retains the missing-entry-point failure. Iteration 2 reruns creation/update, carries the unchanged audit and baseline evidence forward, and explicitly records the update verification reminder. The repeat run added only a source-documented fixture limitation. These are documentation fixtures with executable application code omitted: application-command execution and live host-loading behavior are unverified. Runtime did not expose measured token counts or durations; benchmark artifacts omit them instead of substituting proxies. The maintained source has no custom grader or application code changes requiring a separate source test suite.

## Idempotence and Recovery

Reinvoke against an evaluated output and expect no unnecessary file churn. Keep baseline fixtures immutable and each run isolated. Git retains deleted predecessor sources; undo only task-owned edits if recovery is needed. Do not overwrite unrelated changes. Preserve failed evaluation artifacts before rerunning a changed prompt or skill.

## Interfaces and Dependencies

Runtime requires ordinary filesystem inspection and Markdown editing tools. No external skill or local repository dependency is required by the published bundle. Maintenance uses existing skill-creator validation and viewer tools. No new installed runtime or installer behavior is needed.
