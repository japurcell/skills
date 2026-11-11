# Make contributing-agent commit attribution automatic

This living plan is `brain/plans/todo-31-commit-attribution/ExecPlan.md`. Follow the repository `AGENTS.md`, `exec-plans`, and `brain` guidance. Keep its status and evidence current. The implementation owner must activate `tdd`, `create-skill`, and `writing-for-agents` before editing source or skill instructions. This plan author owns only this file and its plan-index entry.

## Purpose / Big Picture

Complete todo 31 in `brain/todos.md`: when Codex or Copilot produced or edited the changes during the session, an ordinary request to commit must result in exactly one verified trailer for that agent, even without a `co_author` input. Merely committing another person's work establishes no contribution. The actual Git message, validator invocation, and unchanged Git author establish success, not an agent's written assertion.

User attribution instructions, including opt-out and an explicit identity, take precedence; otherwise apply documented repository attribution rules, then the contributing agent's verified default identity. Preserve other established contributors and deduplicate matching trailers. Never use Copilot's identity for Codex or assume an unknown agent is Codex. A trailer is a final message line `Co-authored-by: Name <email>`, separate from Git author configuration.

Scope is the published bundle `skills/default/commit/` and evidence in a fresh `skills/default/commit-workspace/iteration-N/`. Preserve unrelated staging, scope, issue closing, formatting, commit-count, push, and existing evaluation behavior. Do not change installed copies, working-repository Git author settings, or existing commits. Never create evaluation commits in this working repository or push fixture commits. Fixture-only author configuration during preparation is permitted and must remain unchanged during each evaluated run. Ordinary implementation commits are permitted through the `commit` skill's validated-message workflow.

## Progress

- [x] [milestone-1] T1: Freeze and identify the task-start bundle; capture actual baseline reproductions in disposable Codex and Copilot sessions.
- [x] [milestone-1] T2: Record both verified identities and primary sources; resolve provider prerequisites.
- [x] [milestone-2] T3: Prove and enforce required expected trailers, one failing check and fix at a time.
- [ ] [milestone-2] T4: Prove and implement Codex automatic attribution with observed invocation evidence (evaluation instrumentation is done; skill instructions and candidate runtime evidence remain).
- [ ] [milestone-2] T5: Prove and implement Copilot automatic attribution with actual Copilot CLI evidence.
- [ ] [milestone-2] T6: Prove and implement each override, exclusion, preservation, and deduplication behavior in sequence.
- [ ] [milestone-3] T7: Run integrated checks and final candidate/baseline provider comparisons; retain failures and limitations.
- [ ] [milestone-3] T8: Obtain independent review, resolve findings, reconcile todo and archive completed plan only after acceptance.

## Context and Orientation

`skills/default/commit/SKILL.md` Inputs currently describe `co_author` without a default. Step 7 currently says attribution is optional and asks for a bundled-validator invocation before exactly one commit. Independent research at `/tmp/todo31-identities.md` has been inspected and the runtime evidence is retained in `skills/default/commit-workspace/iteration-5/artifacts/`. Verified Codex CLI default: `Codex <noreply@openai.com>`, from official [OpenAI Codex source](https://github.com/openai/codex/blob/main/codex-rs/git-utils/src/baseline.rs), which emits that exact co-author line for an internal baseline commit. Verified Copilot CLI identity: `Copilot <223556219+Copilot@users.noreply.github.com>`. In addition to the implementation report in the official [Copilot CLI issue 975](https://github.com/github/copilot-cli/issues/975) and [GitHub configuration documentation](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-config-dir-reference), the actual Copilot CLI 1.0.109 baseline session supplied this exact identity in both the committed trailer and validator `--co-author` argument. This is direct host-runtime evidence for this CLI build; identity resolution must still prefer explicit metadata from the active host and obey user/repository policy. Do not generalize these defaults to other product/host variants.

Integration setup is complete: branch `todo31-integration`; implementation branch `todo31-implementation` in `/private/tmp/todo31-implementation`. Plan/index commit `1f39d36639339bad04e05576309319b348654a03` is the common starting point. The baseline worker created `skills/default/commit-workspace/iteration-5/baseline-skill/` and `baseline.sha256`; all 15 manifest entries verified with `sha256sum -c`, and the snapshot is read-only. Reuse this original snapshot rather than creating a later baseline. Codex CLI 0.167.1 ran with selected model `gpt-6-luna` and was logged in with ChatGPT. Copilot CLI 1.0.109 ran with selected model `gpt-6-luna` and medium reasoning effort, proving execution availability for this run.

`scripts/validate_message.py` parses repeatable `--co-author` values. After implementation commit `3863a319b54ab445ce6de592905a4d8e8d37c57b`, each distinct supplied identity is required exactly once and unexpected or duplicate trailers remain invalid. With zero expected identities, no trailer is valid. Its job is enforcing resolved explicit inputs, not detecting the provider or policy.

`evals/test_validate_message.py` exercises the public validator. `evals/evals.json` scenarios 0-3 retain historical dry runs and scenario 4 covers real validation/repair/commit ordering; scenario 5 now covers agent attribution. `evals/prepare_validation_workflow.py` prepares isolated Git repositories and wraps a copied validator to record result, message, path, and the actual option vector in `events.jsonl`. A nonblocking `commit-msg` observer records commit attempts. `evals/grade_benchmark.py` reads observations and actual Git history, writing `grading.json` with `summary.failed`; exit zero alone does not mean success. `evals/test_grade_benchmark.py` tests grading using real temporary repositories and now checks expected attribution evidence. Preserve unrelated assertions.

## Decision Log

- 2026-11-11: Keep a single implementation owner for the shared published bundle, tests, fixtures, and evaluation README, working in one dedicated branch/worktree outside this repository (use `/tmp` if sibling locations are unwritable). Tasks below are dependency-bounded, not parallel edits to coupled files. The parent activated `execplan-implement`: use an integration branch and persistent integration coordinator, and independent standards/spec review. Identity research and baseline execution have separate owners.
- 2026-11-11: Freeze the original runtime bundle before any skill or validator edit. Every baseline run must point to that original snapshot, never a later Git revision or candidate copy.
- 2026-11-11: Require real provider execution for the two default-attribution cases. Copilot simulations or Codex roleplay cannot satisfy Copilot acceptance. No source-only check can replace actual committed-message evidence.
- 2026-11-11: Observe one behavior failing before its implementation, then make that behavior pass before starting the next. Existing passing negative cases are retained as guards; do not manufacture failures by weakening correct behavior.

## Surprises & Discoveries

- Current `validate_trailers()` allows `--co-author` identities to be omitted from the message, so its existing allow-list is not a required-identity contract.
- Current evaluation instrumentation observes a validation result but not `--co-author` arguments. Attribution acceptance requires recording and grading the real invocation as well as the resulting commit.
- Historical dry-run graders have Copilot-specific expectations. Preserve those unrelated cases while making new observed scenarios explicitly provider-specific.

## Plan of Work

### Milestone 1: Establish immutable baseline and verified identities

Status: done
Acceptance: met

#### T1: Freeze the original bundle and reproduce the user experience

Prerequisites: none. Owner: baseline worker already dispatched by the parent; integrate its evidence rather than duplicating its work. The selected fresh iteration is `skills/default/commit-workspace/iteration-5/`; its original bundle is `baseline-skill/` with manifest `baseline.sha256`. Confirm saved origin revision, source diff, tool versions, sorted file hashes, and read-only snapshot before editing the skill or validator. Do not overwrite a previous iteration or failed run.

Completed in `skills/default/commit-workspace/iteration-5/artifacts/baseline-notes.md` and `baseline-transcripts.md`. Separate disposable Codex and Copilot repositories used the original read-only snapshot, known fixture author, and neutral edit-then-normal-commit prompts. Both produced exactly one scoped fixture commit without changing author identity or pushing. Codex commit `9b621f0139f610624f9a957b9af446d972b0a6a6` omitted attribution and its validator invocation had no `--co-author`, reproducing the reported omission. Copilot commit `17f3814faf3f677ab0b98c206689deb28626b71d` included exactly one `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>` trailer and passed that identity to the validator. The missing-trailer defect is reproduced for Codex but not for this Copilot CLI build; retain both actual outcomes as distinct baseline facts.

#### T2: Verify identities and provider availability

Completed. Codex `Codex <noreply@openai.com>` is supported by [official OpenAI Codex source](https://github.com/openai/codex/blob/main/codex-rs/git-utils/src/baseline.rs). Copilot `Copilot <223556219+Copilot@users.noreply.github.com>` is supported by [official Copilot CLI issue 975](https://github.com/github/copilot-cli/issues/975), [GitHub CLI configuration documentation](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-config-dir-reference), and, most directly for this CLI build, the actual Copilot CLI 1.0.109 baseline trailer and validator invocation. The runtime run confirms this identity metadata for Copilot CLI 1.0.109; do not infer it for another Copilot host. Codex CLI 0.167.1 ran with model `gpt-6-luna` and authenticated through ChatGPT. Copilot CLI 1.0.109 ran with model `gpt-6-luna` and medium reasoning effort. Exact invocations and observed identities are retained in the baseline artifacts.

Milestone acceptance requires a verified original snapshot, both identities, and recorded actual baseline outcomes for both providers. An availability blocker does not prevent independent validator work, but prevents marking this milestone or final provider acceptance met.

### Milestone 2: Enforce attribution through bounded red/green behavior changes

Status: open
Acceptance: not met

All tasks here share one bundle owner. First inspect each task's baseline and current source. For each new behavior add the smallest meaningful failing check, run it and save failure, implement that behavior, rerun and save pass. Do not write the full implementation before observing the failures. Use the existing public CLI tests and actual provider sessions for the user-visible default behaviors. Do not alter the immutable baseline.

#### T3: Require resolved validator identities exactly once

Completed in `3863a319b54ab445ce6de592905a4d8e8d37c57b` and merged into `todo31-integration`. The new CLI test first failed because a supplied expected identity could be omitted (retained at `/tmp/todo31-implementation-evidence/t3-red.log`). The validator now requires each distinct repeatable `--co-author 'Name <email>'` exactly once, while allowing zero trailers when no identities are supplied. Existing duplicate/unlisted checks remain. Green evidence is `/tmp/todo31-implementation-evidence/t3-green.log`; final validator suite also passed (14 tests) in `final-validator-tests.log`. No provider/policy guessing was added to Python.

#### T4: Make Codex contribution attribution automatic and observable

Prerequisites: T3, verified Codex identity from T2, and original baseline snapshot. Inputs: actual baseline Codex transcript, Inputs/step 7 in `SKILL.md`, trailer rules in `references/message.md`. Completed instrumentation in `3863a319b54ab445ce6de592905a4d8e8d37c57b`: added an attribution scenario/fixture, records the actual validator option vector, and grades expected trailer plus invocation evidence against the real commit while preserving scenario 4. Its new negative grader case first failed because expected attribution passed without the required observed validator option (retained in `/tmp/todo31-implementation-evidence/t4-red.log`); the corrected grader test passes in `t4-green.log`, and all 11 grader tests pass in `final-grader-tests.log`.

Remaining: use the baseline Codex transcript and immutable snapshot to implement the Codex/contribution resolution instruction slice in `SKILL.md` and `references/message.md`: session edits establish contribution; resolve identity before drafting; pass the resolved identity to the validator; document the verified identity/source. Run Codex against the candidate and prove exactly one matching trailer and matching `--co-author`, exactly one scoped commit, and unchanged author. T4 remains in progress until this real candidate runtime case is recorded.

#### T5: Make Copilot contribution attribution automatic

Prerequisites: T4, verified Copilot identity, actual Copilot CLI availability. Add a distinct Copilot contribution scenario/expectation using the same neutral two-stage edit then commit design. Run its original-snapshot failing check through actual Copilot CLI, preserving model/version/transcript and actual message/invocation. Implement the remaining provider selection instruction with the verified Copilot identity/source, preserving Codex behavior and refusing to assume unknown agents are Codex.

Run actual Copilot CLI against an immutable candidate snapshot and grade actual Git/message/invocation evidence. Stop when that candidate case and focused suites pass. If Copilot cannot run, record its blocker and leave T5 unmet; do not substitute another provider.

#### T6: Resolve each precedence and exclusion behavior in sequence

Prerequisites: T4; T5 may be explicitly blocked. For each following behavior, independently add the scenario/assertion and meaningful missing coverage, record its pre-fix result, implement only the missing instruction/grader behavior, then verify before proceeding: explicit identity override; explicit opt-out; documented repository policy (including suppression/different identity); no agent contribution; already-present matching trailer; preserving another established contributor while deduplicating identical trailers. Include explicit-user versus repository conflict to prove user precedence. A supplied identity takes precedence over the default; repository policy takes precedence over defaults; mere execution of Git must add no invented attribution.

Place fixtures under `evals/files/`, scenarios in `evals/evals.json`, event/actual-Git assertions in `grade_benchmark.py`, negative evidence tests in `test_grade_benchmark.py`, and setup/evidence commands in `evals/README.md`. Use expected resolved identity lists in fixture metadata for grading; observers must not inject expected arguments or trailers. No default-identity hint belongs in contribution prompts. Preserve other contributor trailers only when established by scenario provenance. Stop after all precedence/preservation cases and the focused suites pass.

Milestone integration requires all planned cases passing against the integrated candidate, correct options observed before the one commit, and preserved scenario 4. A T5 blocker keeps milestone acceptance unmet even if other tasks pass.

### Milestone 3: Prove integrated behavior and finish review

Status: open
Acceptance: not met

#### T7: Final source checks and behavioral comparison

Prerequisites: T3-T6 complete for full acceptance. Freeze/hash the integrated candidate in `snapshots/candidate/`. Run all three required focused commands below. Run paired baseline/candidate Codex cases through Codex and paired baseline/candidate Copilot cases through actual Copilot CLI using fresh sessions/repos and identical scenario prompts/settings within each provider. Preserve original failed runs; new reruns get new directories. Run the override/exclusion/preservation scenarios and scenario 4 on the final candidate. Grade the iteration and inspect every `summary.failed`, plus decisive actual messages and invocation records.

Record per run snapshot hash, provider/version/model, command, transcript, timings, initial/final HEAD, changed paths, actual commit message, Git author before/after, invocation options, actual result and limitations. Mark source checks, scenario evidence, and provider acceptance separately. Passing one run proves that observed case, not broad reliability. Stop when evidence satisfies every acceptance item or explicitly records an unmet external prerequisite.

#### T8: Independent review and completion

Prerequisites: T7 evidence is available. Invoke `code-review-biaxis` on the integration branch: independent standards and spec reviewers inspect the final bundle diff and evidence against todo 31, including false positives in the grader, precedence, unchanged author/configuration, immutable snapshots, and absence of working-repository evaluation commits. Record findings as bounded plan tasks. The bundle owner resolves findings using focused failing checks before fixes, then reruns only affected checks and final-provider cases if runtime instructions changed. Repeat the independent review/fix cycle at most three times and report unresolved findings. Do not weaken existing checks.

The coordinator runs `reflect`, reconciles all milestone/progress/evidence state, and marks todo 31 complete only when full acceptance is met. Use `todo` and `todo-refine` for backlog changes. Archive the completed plan with its evidence pointers under `brain/archive/plans/`, update link-only indexes, and remove the active plan entry after verifying archive links. If anything is blocked, keep the active plan with an exact next action and do not mark the todo complete. After successful integration and review, remove implementation worktree/branch only after verifying its work is integrated and evidence retained. Report the integration branch.

## Concrete Steps

Next authorized action: `/root/baseline` is the sole published-bundle writer in `/private/tmp/todo31-implementation` and owns the next candidate artifacts under iteration-5. Continue T4 from merged commit `3863a319b54ab445ce6de592905a4d8e8d37c57b`: update only Codex attribution instructions, then capture a candidate Codex provider run with actual validator options and committed message. T3 and T4 instrumentation are complete; T4 runtime/instruction behavior remains pending, followed by T5, the serialized T6 cases, T7, and review. The integration coordinator has acknowledged persistent follow-up readiness and has performed the plan/index commit and clean worktree sync. Parent owns dispatch/deadlines; current next-phase deadline is 21:51 UTC.

Record actual snapshot/run paths here before continuing. Execute T3, T4, T5, and the individual T6 cases serially under the same bundle owner; T7 integrates evidence and T8 reviews completion. Before every implementation commit, its creator activates `commit` and validates the exact message file. Evaluation commits remain confined to disposable fixtures.

From `/Users/adam/dev/skills`, required final checks are:

    rtk proxy python3 skills/default/commit/evals/test_validate_message.py
    rtk proxy python3 skills/default/commit/evals/test_grade_benchmark.py
    rtk proxy env PYTHONPATH=scripts/vendor python3 skills/default/skill-creator/scripts/quick_validate.py skills/default/commit
    rtk proxy python3 skills/default/commit/evals/grade_benchmark.py skills/default/commit-workspace/iteration-N

The existing scenario-4 preparation command is:

    rtk proxy python3 skills/default/commit/evals/prepare_validation_workflow.py <new-run-directory> <immutable-skill-snapshot>

The attribution fixture and scenario now exist and are documented in `evals/README.md`; the implementation owner must retain exact provider commands, selected scenario IDs, and candidate observations there as runtime runs occur. Bound shell subprocesses and provider calls explicitly. Poll long-running sessions without waits over 60 seconds and send progress updates. Provider CLI discovery must inspect installed `--help`; do not guess flags or claim an unexecuted command succeeded.

## Validation and Acceptance

Observed so far at source commit `3863a319b54ab445ce6de592905a4d8e8d37c57b`: validator tests passed (14 tests) and grader tests passed (11 tests); their preceding failing results are retained in `/tmp/todo31-implementation-evidence/`. Other command results remain pending. For grading, require every relevant `summary.failed == 0`, not only exit zero. An auth error, timeout, unavailable model, or missing executable is a prerequisite failure, never a passing scenario. Keep actual baseline outcomes even if they differ from the reported bug.

Full acceptance requires real Codex and real Copilot contribution sessions with omitted `co_author` producing exactly one verified provider-correct trailer; actual validator invocation containing each resolved identity; final committed content matching validated content; exactly one scoped fixture commit; no author changes or pushes; explicit user and repository precedence; no invented attribution without contribution; preservation/deduplication; missing expected trailers failing validation; all focused checks passing; and retained baseline/candidate transcripts, messages, hashes, and observed limitations. Explicit opt-out, policy, or no-contribution cases with no resolved identities must work with no `--co-author` options.

## Idempotence and Recovery

Create-only run directories and immutable snapshots prevent accidental overwrites. On interrupted execution, inspect HEAD and events before retrying; never rerun a commit prompt in an already-committed fixture. Prepare a fresh numbered run and preserve the failed/interrupted one. Reject malformed/missing evidence rather than reconstructing events from claims. Restore only this task's edits from the initial file-scoped snapshot if a rollback is needed, preserving others' changes. Never reset the working repository, rewrite history, change global author config, or delete original failed evidence. A new candidate revision requires a new snapshot identity and rerunning affected final acceptance.

## Interfaces and Dependencies

The runtime interface remains `python3 <skill-root>/scripts/validate_message.py <message-file> [--co-author 'Name <email>']...`, plus existing issue/fixes options. Each distinct supplied identity is allowed and required exactly once. The skill resolves contribution, provider, policy, and identity; the validator enforces explicit inputs.

Requires Python 3, Git, installed authenticated Codex and Copilot CLIs, provider access, and official identity evidence. Existing fixture-local hooks and validator wrapping are observers, not enforcement. Extend event schema additively to retain invocation arguments; tests must reject absent/malformed attribution evidence for new scenarios without breaking historical scenario 4. Evidence directories are disposable repositories, but their retained results are part of acceptance.

## Outcomes & Retrospective

Milestone 1 is complete: the original baseline snapshot manifest verified, real Codex and Copilot contribution/commit sessions ran, actual commit messages and validator invocations were inspected, and provider versions/models plus fixture author identities were retained. The reported omission reproduces for Codex; this Copilot build already auto-attributes using its runtime-supplied identity. No implementation source has been changed by the integration coordinator. Coordinator readiness and the integration/worktree setup are complete. Next owner is `/root/implementation` in `/private/tmp/todo31-implementation`, beginning with T3 validator behavior and its tests, then adding evaluation instrumentation as specified; preserve the baseline outcomes and worker-owned iteration artifacts. Current implementation deadline is 21:39 UTC with no extensions.
