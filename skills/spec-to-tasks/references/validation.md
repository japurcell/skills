# Validation checklist

Validate both coverage and dispatch clarity. Parseable JSON alone does not establish a usable task manifest.

## Source coverage and task sizing

- [ ] Every explicit requirement, edge case, fallback, negative state, partial failure, and out-of-scope boundary is mapped to a task or acceptance check.
- [ ] Stable source headings or IDs resolve to the current source. Every `sourceRefs` entry identifies real source content; inline entries have `path: null`, `section: null`, and nonempty `content`.
- [ ] Each task has one central outcome and is sized by behavioral scope, unresolved decisions, coupled state, environment uncertainty, and verification burden.
- [ ] Implementation tasks remain end-to-end vertical slices. No necessary negative case or test is detached into a valueless horizontal task.
- [ ] An indivisible difficult invariant retains its full acceptance contract. Remaining reasoning risks and bounded entry points are described without implying that a partial proof passes the task.
- [ ] An unresolved architectural choice within the task's authority is a bounded decision/proof task. A choice requiring user approval is not silently assigned to implementation.
- [ ] Shared invariants have an explicit integration task or check that proves the combined behavior. Component passes alone do not satisfy the integration gate.
- [ ] Out-of-scope items are excluded, and conflicting requirements are resolved or escalated before the manifest is written.

## Manifest shape and dependency graph

- [ ] Top-level `project`, `branchName`, `description`, and `tasks` are present; output is valid JSON only.
- [ ] Every task includes the existing fields: `id`, `parentStoryId`, `title`, `description`, `acceptanceCriteria`, `filesLikelyTouched`, `designGuidance`, `priority`, `passes`, and `notes`.
- [ ] `filesLikelyTouched` includes confidently inferable source, test, script, config, migration, fixture, and command-target files; use `[]` when paths cannot be inferred confidently.
- [ ] Every task includes `dependsOn`, nonempty `sourceRefs`, `requiredContext`, `taskType`, and `verification`.
- [ ] Fresh tasks have `passes: false` and `notes: ""`. Existing IDs, notes and historical evidence are preserved; completion is reconciled using [Updating existing tasks](task-schema.md#updating-existing-tasks), including affected downstream guarantees and reasons for reopening.
- [ ] An empty `requiredContext` is used only when the task and manifest already contain all context needed to finish the task.
- [ ] A file reference has a nonempty repository-relative string `path` and nonempty string `section`. Inline source or context uses both `path: null` and `section: null`, plus nonempty `content`; one null without the other, absolute paths, and invented paths are invalid.
- [ ] New task IDs are unique and sequential. Priorities are unique and ascending, with mandatory source order represented in the task order and dependency graph.
- [ ] Every dependency ID exists. There are no self-dependencies, duplicate edges, or cycles. A dependent task remains ineligible until each prerequisite passes. No dependency or priority claim implies safe parallel execution.
- [ ] Each edge has a concrete consumed outcome/artifact or mandatory source-order reason. Existing task definitions can be reviewed now; their implementation is not a prerequisite for reviewing the manifest. Authoring-time coverage/schema review is complete rather than deferred into execution tasks.
- [ ] Recommended order affects priority only when safe; priority never authorizes bypassing a prerequisite.
- [ ] Each `taskType` is one of `decision`, `implementation`, `verification`, `integration`, or `documentation`, and the task has an independent outcome appropriate to that type.

## Verification and readiness

- [ ] Every task has at least one required check that directly establishes its outcome, plus an explicit `typecheck` check classified as `required`, `not-applicable`, or `unresolved`.
- [ ] Every verification object contains exactly `id`, `kind`, `applicability`, `command`, `workingDirectory`, `expected`, and `reason`. `kind` and `applicability` use the allowed values in [task-schema.md](task-schema.md).
- [ ] Verification check IDs are unique within each task.
- [ ] Required automated checks use known commands, repository-relative working directories, and observable expected results. No command has been invented.
- [ ] Each relevant test, typecheck, build, lint, and UI behavior is covered by a required check or a verified non-applicability reason. A known failing applicable check remains required.
- [ ] A required manual check has `command: null` and a concrete procedure plus expected evidence in `expected`.
- [ ] A not-applicable check has `command: null` and a verified reason. An unresolved check names what must be discovered; use `command: null` only when the command is unknown, and retain any known command when host or access availability blocks execution.
- [ ] Decision, verification, integration, and documentation tasks use evidence appropriate to their outcome rather than fabricated product checks.
- [ ] Planned checks are not described as passed. Only execution evidence can establish a pass. Never erase a known command or relabel an applicable failing check as inapplicable.
- [ ] An unresolved required check or unavailable required environment remains visible and cannot count as satisfied. Report the manifest as `needs follow-up`, not ready.
- [ ] A missing required context reference or invalid graph is corrected before save. If it cannot be resolved safely, do not write the manifest or report it ready.
- [ ] UI-visible tasks specify a concrete browser scenario and include the instruction “activate the `playwright-cli` skill”. Backend-only tasks avoid browser and UI wording.

## Output

- [ ] The output path follows the precedence in the main skill, and the final response reports task count, path, and honest readiness.
