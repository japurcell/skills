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
- [x] [milestone-2] T4: Prove and implement Codex automatic attribution with observed invocation evidence.
- [x] [milestone-2] T5: Prove and implement Copilot automatic attribution with actual Copilot CLI evidence.
- [x] [milestone-2] T6: Implement source and evaluation coverage for override, exclusion, preservation, and deduplication behaviors (full provider matrix is tracked by T7).
- [ ] [milestone-3] T7: Run integrated checks and final candidate/baseline provider comparisons; retain failures and limitations (final matrix in progress).
- [ ] [milestone-3] T8: Complete independent review cycle 1, resolve findings, then re-review the final integrated diff (cycle 2 pending).
- [x] [milestone-3] T9: Reject absent or malformed validator argv/evidence for empty-identity scenarios and add negative grader tests; implementation complete in `840b14a3`.

## Context and Orientation

The integrated `skills/default/commit/SKILL.md` now resolves contribution and identity before drafting: user instruction, repository policy, then verified defaults for contributing agents. It passes each emitted identity once to the validator. The validator requires each distinct supplied identity exactly once; the grader records actual argv and checks committed messages. Verified Codex CLI default: `Codex <noreply@openai.com>`, from official [OpenAI Codex source](https://github.com/openai/codex/blob/main/codex-rs/git-utils/src/baseline.rs), and confirmed by same-session baseline/candidate runs. Verified Copilot CLI identity: `Copilot <223556219+Copilot@users.noreply.github.com>`, supported by the [official Copilot CLI attribution discussion](https://github.com/github/copilot-cli/issues/975), [GitHub configuration documentation](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-config-dir-reference), and the actual Copilot CLI 1.0.109 baseline/candidate runs. These identities apply to the named CLIs, not all product or host variants.

Integration branch `todo31-integration` is at source commit `08e1c088e0c6ff26f9db323a0e10a205bd1a1267`, based on the separately preserved todo32 commit `49d6b2649d94b1951745134890e7e1baf2e72e62`. The baseline worker created `skills/default/commit-workspace/iteration-5/baseline-skill/` and `baseline.sha256`; all 15 entries verified, and the snapshot is read-only. Baseline and candidate records are in `skills/default/commit-workspace/iteration-5/artifacts/`. Codex CLI 0.167.1 used model `gpt-6.1-sol` for the valid same-session baseline and candidate; paired final runs must use the same model. Copilot CLI 1.0.109 used model `gpt-6-luna`, medium reasoning, for baseline and candidate.

`scripts/validate_message.py` parses repeatable `--co-author` values. After implementation commit `3863a319b54ab445ce6de592905a4d8e8d37c57b`, each distinct supplied identity is required exactly once and unexpected or duplicate trailers remain invalid. With zero expected identities, no trailer is valid. Its job is enforcing resolved explicit inputs, not detecting the provider or policy.

`evals/test_validate_message.py` exercises the public validator. Scenarios 0-3 retain historical dry runs, scenario 4 covers validation/repair/commit ordering, scenario 5 Codex attribution, scenario 6 Copilot attribution, and scenarios 7-12 precedence/exclusion/preservation. `evals/prepare_validation_workflow.py` records actual validator options. `evals/grade_benchmark.py` checks those observations and actual Git history; inspect `summary.failed`, not only process exit. The full baseline/candidate provider matrix and scenario grading remain in progress under `skills/default/commit-workspace/iteration-5/final-validation/`.

## Decision Log

- 2026-11-11: Keep a single implementation owner for the shared published bundle, tests, fixtures, and evaluation README, working in one dedicated branch/worktree outside this repository (use `/tmp` if sibling locations are unwritable). Tasks below are dependency-bounded, not parallel edits to coupled files. The parent activated `execplan-implement`: use an integration branch and persistent integration coordinator, and independent standards/spec review. Identity research and baseline execution have separate owners.
- 2026-11-11: Freeze the original runtime bundle before any skill or validator edit. Every baseline run must point to that original snapshot, never a later Git revision or candidate copy.
- 2026-11-11: Require real provider execution for the two default-attribution cases. Copilot simulations or Codex roleplay cannot satisfy Copilot acceptance. No source-only check can replace actual committed-message evidence.
- 2026-11-11: Observe one behavior failing before its implementation, then make that behavior pass before starting the next. Existing passing negative cases are retained as guards; do not manufacture failures by weakening correct behavior.

## Surprises & Discoveries

- Same-session Codex baseline omission is now verified: baseline commit `b3f52ea3c26f337fb5650953182fe826514fe2cf` has no trailer or validator identity option; the fixture author remains unchanged.
- Actual candidate Codex and Copilot commits each contain one provider-correct trailer and pass the same identity once to the validator; both fixture authors remain unchanged.
- Evaluation instrumentation now observes the validator option vector and grades it against the actual committed message.
- Historical dry-run graders have Copilot-specific expectations. Preserve those unrelated cases while making new observed scenarios explicitly provider-specific.

## Plan of Work

### Milestone 1: Establish immutable baseline and verified identities

Status: done
Acceptance: met

#### T1: Freeze the original bundle and reproduce the user experience

Prerequisites: none. Owner: baseline worker already dispatched by the parent; integrate its evidence rather than duplicating its work. The selected fresh iteration is `skills/default/commit-workspace/iteration-5/`; its original bundle is `baseline-skill/` with manifest `baseline.sha256`. Confirm saved origin revision, source diff, tool versions, sorted file hashes, and read-only snapshot before editing the skill or validator. Do not overwrite a previous iteration or failed run.

Completed. The immutable original snapshot, fixture author, and provider messages are retained in iteration 5. The valid same-session Codex baseline is `artifacts/codex-same-session-baseline.md`: Codex CLI 0.167.1, model `gpt-6.1-sol`, edited and committed in the same session, no co-author option or trailer, commit `b3f52ea3c26f337fb5650953182fe826514fe2cf`, author/committer unchanged as `Fixture <fixture@example.invalid>`. The earlier separate-session Codex run remains historical only. Copilot baseline commit `17f3814faf3f677ab0b98c206689deb28626b71d` used one resumed session and included exactly one `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>` trailer with the same identity passed to the validator. The mistaken resume from the implementation worktree was abandoned without a commit and excluded.

#### T2: Verify identities and provider availability

Completed. Codex `Codex <noreply@openai.com>` is supported by [official OpenAI Codex source](https://github.com/openai/codex/blob/main/codex-rs/git-utils/src/baseline.rs). Copilot `Copilot <223556219+Copilot@users.noreply.github.com>` is supported by [official Copilot CLI issue 975](https://github.com/github/copilot-cli/issues/975), [GitHub CLI configuration documentation](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-config-dir-reference), and the actual Copilot CLI 1.0.109 baseline trailer and validator invocation. Do not infer either identity for another host. The valid Codex baseline/candidate pair used CLI 0.167.1 and model `gpt-6.1-sol`. Copilot CLI 1.0.109 baseline/candidate used model `gpt-6-luna` and medium reasoning effort. Exact invocations and identities are retained in the baseline and candidate artifacts.

Milestone acceptance requires a verified original snapshot, both identities, and actual baseline outcomes for both providers with contribution and commit in the same session per provider. These are now recorded in the artifacts referenced above. The earlier separate-session Codex attempt is not used for acceptance. Milestone 1 is complete; this does not establish full candidate-matrix acceptance.

### Milestone 2: Enforce attribution through bounded red/green behavior changes

Status: in progress
Acceptance: not met

All tasks here share one bundle owner. First inspect each task's baseline and current source. For each new behavior add the smallest meaningful failing check, run it and save failure, implement that behavior, rerun and save pass. Do not write the full implementation before observing the failures. Use the existing public CLI tests and actual provider sessions for the user-visible default behaviors. Do not alter the immutable baseline.

#### T3: Require resolved validator identities exactly once

Completed in `3863a319b54ab445ce6de592905a4d8e8d37c57b` and merged into `todo31-integration`. The new CLI test first failed because a supplied expected identity could be omitted (retained at `/tmp/todo31-implementation-evidence/t3-red.log`). The validator now requires each distinct repeatable `--co-author 'Name <email>'` exactly once, while allowing zero trailers when no identities are supplied. Existing duplicate/unlisted checks remain. Green evidence is `/tmp/todo31-implementation-evidence/t3-green.log`; final validator suite also passed (14 tests) in `final-validator-tests.log`. No provider/policy guessing was added to Python.

#### T4: Make Codex contribution attribution automatic and observable

Prerequisites: T3, verified Codex identity from T2, and original baseline snapshot. Inputs: actual baseline Codex transcript, Inputs/step 7 in `SKILL.md`, trailer rules in `references/message.md`. Completed instrumentation in `3863a319b54ab445ce6de592905a4d8e8d37c57b`: added an attribution scenario/fixture, records the actual validator option vector, and grades expected trailer plus invocation evidence against the real commit while preserving scenario 4. Its new negative grader case first failed because expected attribution passed without the required observed validator option (retained in `/tmp/todo31-implementation-evidence/t4-red.log`); the corrected grader test passes in `t4-green.log`, and all 11 grader tests pass in `final-grader-tests.log`.

Completed in candidate commit `357f0a82b8535ad91601e22c6844cf4ba5b70735`, recorded at `artifacts/codex-t4-candidate.md`. Against an immutable candidate snapshot, Codex CLI 0.167.1/model `gpt-6.1-sol` established contribution then received only a normal commit request in the same session. It emitted one Codex trailer, passed the exact identity once to the validator, created one scoped commit, and left the fixture author/committer unchanged. The paired same-session baseline used the same model and omitted both trailer and option. T4 acceptance is met.

#### T5: Make Copilot contribution attribution automatic

Completed in candidate commit `63d9c4ae52a7a53d16085ab83ca7582478abeca8`, recorded at `artifacts/copilot-t5-candidate.md`. Copilot CLI 1.0.109/model `gpt-6-luna`, medium effort, contributed and committed in one session with a neutral commit request. It emitted one Copilot trailer, passed the same identity once to the validator, made one scoped commit, and left the fixture author/committer unchanged. The baseline on the original skill already produced the same provider-correct behavior. T5 acceptance is met for this CLI build.

#### T6: Resolve each precedence and exclusion behavior in sequence

Implemented in the integrated source/evaluation commit `08e1c088e0c6ff26f9db323a0e10a205bd1a1267`. Scenarios 7-12 and fixtures cover explicit identity override, opt-out, repository suppression/identity, user-over-repository precedence, no contribution, and preserving/deduplicating established trailers. The worker recorded a failing fixture-policy test before adding initial repository-policy state, then a passing focused suite (16 grader tests); details are in `artifacts/implementation-evidence.md`. The final actual-provider matrix for these cases remains T7 work.

Place fixtures under `evals/files/`, scenarios in `evals/evals.json`, event/actual-Git assertions in `grade_benchmark.py`, negative evidence tests in `test_grade_benchmark.py`, and setup/evidence commands in `evals/README.md`. Use expected resolved identity lists in fixture metadata for grading; observers must not inject expected arguments or trailers. No default-identity hint belongs in contribution prompts. Preserve other contributor trailers only when established by scenario provenance. Stop after all precedence/preservation cases and the focused suites pass.

Source and evaluation coverage for T3-T6 is complete. Milestone 2 remains in progress until the final frozen-candidate matrix verifies all scenarios, correct options before commit, and preserved scenario 4. Any provider blocker leaves overall acceptance unmet.

### Milestone 3: Prove integrated behavior and finish review

Status: in progress
Acceptance: not met

#### T7: Final source checks and behavioral comparison

Prerequisites: T3-T6 complete for full acceptance. Freeze/hash the integrated candidate in `snapshots/candidate/`. Run all three required focused commands below. Run paired baseline/candidate Codex cases through Codex and paired baseline/candidate Copilot cases through actual Copilot CLI using fresh sessions/repos and identical scenario prompts/settings within each provider. Preserve original failed runs; new reruns get new directories. Run the override/exclusion/preservation scenarios and scenario 4 on the final candidate. Grade the iteration and inspect every `summary.failed`, plus decisive actual messages and invocation records.

Record per run snapshot hash, provider/version/model, command, transcript, timings, initial/final HEAD, changed paths, actual commit message, Git author before/after, invocation options, actual result and limitations. Mark source checks, scenario evidence, and provider acceptance separately. Passing one run proves that observed case, not broad reliability. Stop when evidence satisfies every acceptance item or explicitly records an unmet external prerequisite.

#### T8: Independent review and completion

Cycle 1 reviewed base `90e83b8f` to integration tip `91a0b769658af69c782d1f6e6e7454ee02d6303a`. Standards report `/tmp/todo31-standards-review.md` found zero actionable issues. Spec report `/tmp/todo31-spec-review.md` found one Important grader evidence false-pass path for scenarios expecting no co-authors. T9 below implements that fix. Cycle 2 must independently re-review the updated final diff and matrix evidence, including the read-only snapshot helper and T9. Do not mark T8 done until this re-review has no unresolved actionable findings.

#### T9: Require valid observed validator evidence even when no identity is expected

Completed in `840b14a33e59ca35ae913b3299a7b9ba52a5dc03`, limited to `grade_benchmark.py` and `test_grade_benchmark.py`. Red evidence is retained under `skills/default/commit-workspace/iteration-5/artifacts/grader-review-fix/`; tests exposed false passes for absent/malformed argv and validation/message evidence in empty-identity cases. The grader now validates event fields and argv shape, requires a successful final validation before commit, and compares the validated text with the actual committed message regardless of expected identity count. The worker reports 22 grader tests pass. A source diff confirms the runtime instructions, validator, observer, README, and scenario inputs are byte-identical to commit `66b934285ff2e4dd4f2d2bd2dd1763327489371e`. Cycle-2 review is pending; do not mark T8 complete yet.

The coordinator runs `reflect`, reconciles all milestone/progress/evidence state, and marks todo 31 complete only when full acceptance is met. Use `todo` and `todo-refine` for backlog changes. Archive the completed plan with its evidence pointers under `brain/archive/plans/`, update link-only indexes, and remove the active plan entry after verifying archive links. If anything is blocked, keep the active plan with an exact next action and do not mark the todo complete. After successful integration and review, remove implementation worktree/branch only after verifying its work is integrated and evidence retained. Report the integration branch.

## Concrete Steps

Next authorized action: `/root/final_validation_v2` owns the replacement evidence matrix under `skills/default/commit-workspace/iteration-5/final-validation/`, deadline 22:41 UTC. The previous candidate `run-4` produced no commit because its prompt prohibited all `events.jsonl` writes, causing auto-review to reject the legitimate observer append. This was a fixture authorization/setup failure, not a demonstrated product defect. The replacement `run-5` scopes agent access to the disposable fixture with `--add-dir` and explicitly allows the bundled observer to append while direct evidence-file edits remain prohibited; preserve run-4 and all earlier attempts. Pair settings: Codex CLI 0.167.1/model `gpt-6.1-sol`; Copilot CLI 1.0.109/model `gpt-6-luna`/medium. Include scenario 4 and scenarios 7-12, inspect each `summary.failed`, and retain transcripts, validator argv, messages, author state, provider settings, and snapshot hashes. T9 is implemented at `840b14a3`; T8 cycle-2 review remains pending after the matrix. The review brief is `/tmp/todo31-review-brief.md`, fixed at base `90e83b8f` with a three-dot diff command; refresh its tip after final evidence changes. Do not mark acceptance or clean up worktrees before matrix and review completion.

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

At source commit `66b934285ff2e4dd4f2d2bd2dd1763327489371e`, the read-only snapshot preparation regression passed after an observed red run; the helper preserves baseline bytes/modes while preparing a writable instrumented copy. T9 grader-evidence fix `840b14a3` then added only grader and grader tests; its red/green artifacts are under `artifacts/grader-review-fix/`, and the worker reports 22 grader tests pass. The prior run-4 provider attempt did not commit because its prompt explicitly prohibited the observer's append to `events.jsonl` and auto-review rejected that write. `/root/final_validation_v2` is preparing run-5 with narrowly scoped fixture access and observer-append authorization; the full matrix remains pending. Inspect every `summary.failed` and preserve all failures before acceptance.

Full acceptance requires real Codex and real Copilot contribution sessions with omitted `co_author` producing exactly one verified provider-correct trailer; actual validator invocation containing each resolved identity; final committed content matching validated content; exactly one scoped fixture commit; no author changes or pushes; explicit user and repository precedence; no invented attribution without contribution; preservation/deduplication; missing expected trailers failing validation; all focused checks passing; and retained baseline/candidate transcripts, messages, hashes, and observed limitations. Explicit opt-out, policy, or no-contribution cases with no resolved identities must work with no `--co-author` options.

## Idempotence and Recovery

Create-only run directories and immutable snapshots prevent accidental overwrites. On interrupted execution, inspect HEAD and events before retrying; never rerun a commit prompt in an already-committed fixture. Prepare a fresh numbered run and preserve the failed/interrupted one. Reject malformed/missing evidence rather than reconstructing events from claims. Restore only this task's edits from the initial file-scoped snapshot if a rollback is needed, preserving others' changes. Never reset the working repository, rewrite history, change global author config, or delete original failed evidence. A new candidate revision requires a new snapshot identity and rerunning affected final acceptance.

## Interfaces and Dependencies

The runtime interface remains `python3 <skill-root>/scripts/validate_message.py <message-file> [--co-author 'Name <email>']...`, plus existing issue/fixes options. Each distinct supplied identity is allowed and required exactly once. The skill resolves contribution, provider, policy, and identity; the validator enforces explicit inputs.

Requires Python 3, Git, installed authenticated Codex and Copilot CLIs, provider access, and official identity evidence. Existing fixture-local hooks and validator wrapping are observers, not enforcement. Extend event schema additively to retain invocation arguments; tests must reject absent/malformed attribution evidence for new scenarios without breaking historical scenario 4. Evidence directories are disposable repositories, but their retained results are part of acceptance.

## Outcomes & Retrospective

Milestone 1 is complete: the same-session Codex baseline at commit `b3f52ea3c26f337fb5650953182fe826514fe2cf` omitted attribution, and the Copilot baseline used its runtime-supplied identity. T4/T5 candidate runs passed with correct trailers/options, one scoped commit, and unchanged fixture authors. T3-T6 and the read-only snapshot helper are integrated; T9 grader evidence enforcement is implemented in `840b14a3` with 22 grader tests reported green. Review cycle 1 had zero standards findings and one spec finding; T9 addresses it, and cycle-2 review remains pending. Overall acceptance is open while `/root/final_validation_v2` runs the replacement matrix. Earlier run-4 had no commit because its fixture prompt prohibited observer appends and auto-review rejected the write; run-5 uses scoped fixture access with explicit observer-append authorization. Preserve all attempts. Todo32 remains a separate backlog item outside Todo31 implementation scope. The integration coordinator merged T9 and updated the plan only in this checkpoint.
