# Make contributing-agent commit attribution automatic

This living plan is `brain/plans/todo-31-commit-attribution/ExecPlan.md`. Follow the repository `AGENTS.md`, `exec-plans`, and `brain` guidance. Keep its status and evidence current. The implementation owner must activate `tdd`, `create-skill`, and `writing-for-agents` before editing source or skill instructions. This plan author owns only this file and its plan-index entry.

## Purpose / Big Picture

Complete todo 31 in `brain/todos.md`: when Codex or Copilot produced or edited the changes during the session, an ordinary request to commit must result in exactly one verified trailer for that agent, even without a `co_author` input. Merely committing another person's work establishes no contribution. The actual Git message, validator invocation, and unchanged Git author establish success, not an agent's written assertion.

User attribution instructions, including opt-out and an explicit identity, take precedence; otherwise apply documented repository attribution rules, then the contributing agent's verified default identity. Preserve other established contributors and deduplicate matching trailers. Never use Copilot's identity for Codex or assume an unknown agent is Codex. A trailer is a final message line `Co-authored-by: Name <email>`, separate from Git author configuration.

Scope is the published bundle `skills/default/commit/` and evidence in a fresh `skills/default/commit-workspace/iteration-N/`. Preserve unrelated staging, scope, issue closing, formatting, commit-count, push, and existing evaluation behavior. Do not change installed copies, working-repository Git author settings, or existing commits. Never create evaluation commits in this working repository or push fixture commits. Fixture-only author configuration during preparation is permitted and must remain unchanged during each evaluated run. Ordinary implementation commits are permitted through the `commit` skill's validated-message workflow.

## Progress

- [ ] [milestone-1] T1: Freeze and identify the task-start bundle; capture actual baseline reproductions in disposable Codex and Copilot sessions.
- [ ] [milestone-1] T2: Record both verified identities and primary sources; resolve provider prerequisites.
- [ ] [milestone-2] T3: Prove and enforce required expected trailers, one failing check and fix at a time.
- [ ] [milestone-2] T4: Prove and implement Codex automatic attribution with observed invocation evidence.
- [ ] [milestone-2] T5: Prove and implement Copilot automatic attribution with actual Copilot CLI evidence.
- [ ] [milestone-2] T6: Prove and implement each override, exclusion, preservation, and deduplication behavior in sequence.
- [ ] [milestone-3] T7: Run integrated checks and final candidate/baseline provider comparisons; retain failures and limitations.
- [ ] [milestone-3] T8: Obtain independent review, resolve findings, reconcile todo and archive completed plan only after acceptance.

## Context and Orientation

`skills/default/commit/SKILL.md` Inputs currently describe `co_author` without a default. Step 7 currently says attribution is optional and asks for a bundled-validator invocation before exactly one commit. Independent research at `/tmp/todo31-identities.md` has now been inspected. Verified Codex CLI default: `Codex <noreply@openai.com>`, from official [OpenAI Codex source](https://github.com/openai/codex/blob/main/codex-rs/git-utils/src/baseline.rs), which emits that exact co-author line for an internal baseline commit. Verified Copilot CLI default: `Copilot <223556219+Copilot@users.noreply.github.com>`, from the implementation report in the official [Copilot CLI issue 975](https://github.com/github/copilot-cli/issues/975), supported by [GitHub configuration documentation](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-config-dir-reference) for `includeCoAuthoredBy`. These sources establish named CLI defaults, not all product/host variants; preserve explicit host identity metadata and task precedence.

Parent-reported setup: integration branch `todo31-integration`; implementation branch `todo31-implementation` in `/private/tmp/todo31-implementation`, based at `90e83b8f`. The baseline worker created `skills/default/commit-workspace/iteration-5/baseline-skill/` and `baseline.sha256`; directory existence has been observed, but this plan author has not independently audited immutability or completed provider results. Reuse this original snapshot rather than creating a later baseline. Research records Codex CLI 0.167.1 authenticated with ChatGPT and Copilot CLI 1.0.109 installed; actual Copilot authentication/provider execution remains to be demonstrated by the baseline worker.

`scripts/validate_message.py` parses repeatable `--co-author` values. `validate_trailers()` already rejects unlisted and duplicate trailers, but does not require every expected identity to appear. Its job is enforcing resolved explicit inputs, not detecting the provider or policy. With zero expected identities, no trailer is valid; unlisted trailers remain invalid.

`evals/test_validate_message.py` exercises the public validator. `evals/evals.json` has scenarios 0-3 for historical dry runs and scenario 4 for real validation/repair/commit ordering. Preserve unrelated assertions. `evals/prepare_validation_workflow.py` prepares isolated Git repositories and wraps a copied validator to record result, message, and path in `events.jsonl`; it currently does not record the option vector. A nonblocking `commit-msg` observer records commit attempts. `evals/grade_benchmark.py` reads observations and actual Git history, writing `grading.json` with `summary.failed`; exit zero alone does not mean success. `evals/test_grade_benchmark.py` tests grading using real temporary repositories. Extend these narrow interfaces for attribution rather than replacing the observation model.

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

Status: open
Acceptance: not met

#### T1: Freeze the original bundle and reproduce the user experience

Prerequisites: none. Owner: baseline worker already dispatched by the parent; integrate its evidence rather than duplicating its work. The selected fresh iteration is `skills/default/commit-workspace/iteration-5/`; its original bundle is `baseline-skill/` with manifest `baseline.sha256`. Confirm saved origin revision, source diff, tool versions, sorted file hashes, and read-only snapshot before editing the skill or validator. Do not overwrite a previous iteration or failed run.

Prepare separate disposable repositories for baseline Codex and baseline Copilot using that snapshot. Establish real contribution by asking the actual provider to make a small specified documentation edit, then request only a normal scoped commit with no push. The commit request must not mention attribution, trailers, or `co_author`. Preserve the session transcript across edit and commit. Use a fixture with known author identity and no repository attribution policy. Inspect `git log -1 --format=%B`, commit count, changed paths, author identity, and validator calls. Save observed missing-trailer behavior or the actual differing outcome honestly. Do not assert an expected failure if the baseline happens to pass.

Bound every provider subprocess with an explicit timeout and capture timeout/authentication/model errors separately from product failure. The coordinator can work on T2 and test design while a provider runs. Stop T1 when snapshots and both real provider results are recorded, or when an explicit provider blocker is recorded; a blocker leaves that provider acceptance open and does not authorize invented evidence.

#### T2: Verify identities and provider availability

Prerequisites: none; dependent implementation needs T1's snapshot and this task's verified identities. Owner: identity researcher, then coordinator integration. Inspect `/tmp/todo31-identities.md` if present. Verify exact Codex and Copilot attribution names/emails using official OpenAI/GitHub documentation or source, or explicit host attribution metadata. Retain exact source URLs or source paths/version and the decisive excerpt. Do not invent emails from product names or take the current bundle's identity claim as independent verification.

Record both identities and evidence inline in this plan before T4/T5. Record Codex and Copilot CLI versions, available models and selected model, and authentication availability. If verification or actual Copilot execution is unavailable, report the specific prerequisite and retain unmet acceptance. Stop after documenting those facts; provider setup outside authorization is not this task.

Milestone acceptance requires a verified original snapshot, both identities, and recorded actual baseline outcomes for both providers. An availability blocker does not prevent independent validator work, but prevents marking this milestone or final provider acceptance met.

### Milestone 2: Enforce attribution through bounded red/green behavior changes

Status: open
Acceptance: not met

All tasks here share one bundle owner. First inspect each task's baseline and current source. For each new behavior add the smallest meaningful failing check, run it and save failure, implement that behavior, rerun and save pass. Do not write the full implementation before observing the failures. Use the existing public CLI tests and actual provider sessions for the user-visible default behaviors. Do not alter the immutable baseline.

#### T3: Require resolved validator identities exactly once

Prerequisites: T1 snapshot exists. Inputs: `validate_trailers()` and existing validator CLI tests. Add a failing CLI test for a missing expected identity; update the function so every distinct repeatable `--co-author 'Name <email>'` identity must appear exactly once. Then exercise multiple expected identities with one absent. Retain required/present, duplicate, unlisted, and absent-by-design tests, adding focused checks where coverage is missing. Repeated identical options must not demand duplicate trailers. Update option help to describe allowed-and-required semantics. No environmental/provider guessing belongs in the Python validator.

Verification: `rtk proxy python3 skills/default/commit/evals/test_validate_message.py` from repository root must pass after recorded red results. Zero options and zero trailers passes; missing expected, duplicate, and unlisted trailers fail with exit 1; usage/read errors remain exit 2. Stop after validator semantics and their tests pass.

#### T4: Make Codex contribution attribution automatic and observable

Prerequisites: T3, verified Codex identity from T2, and original baseline snapshot. Inputs: actual baseline Codex transcript, Inputs/step 7 in `SKILL.md`, trailer rules in `references/message.md`. First add the separate Codex contribution scenario to `evals/evals.json` and attribution fixture/preparation support. Extend observation events to include the actual validator option vector, without enforcing attribution in the observer. Add failing grader tests proving missing/wrong/duplicate expected attribution and missing or malformed invocation evidence cannot pass, even when the agent claims success. Preserve scenario 4 behavior.

Run the contribution scenario on the original snapshot using Codex and record its actual outcome before the instruction fix. Then update only the Codex/contribution resolution instruction slice: session edits establish contribution; resolve identity before drafting, and pass that resolved identity to the validator. Document the verified identity/source. Candidate Codex execution must prove exactly one matching trailer and matching `--co-author`, exactly one scoped commit, and unchanged author. Stop when focused checks and that observed candidate case pass; pending Copilot/override behavior remains T5/T6.

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

Next authorized action: parent/integration coordinator consumes the baseline worker's T1 snapshot evidence and the verified T2 research above, commits this plan through the commit workflow, and synchronizes `/private/tmp/todo31-implementation` with `todo31-integration` before source edits. The parent reports the integration setup ready; record the persistent coordinator's acknowledged follow-up handle and task deadline ledger when reconciling this plan. Use routed dispatch and parent-owned deadlines per `execplan-implement`; record task/agent IDs, start/deadline, extension count and enforcement handle. The integration coordinator receives bounded merge/checkpoint assignments and stays idle between them. The implementer incorporates the integration tip before reporting; the coordinator merges verified work into the integration branch. No branches/worktrees were created by this plan author.

Record actual snapshot/run paths here before continuing. Execute T3, T4, T5, and the individual T6 cases serially under the same bundle owner; T7 integrates evidence and T8 reviews completion. Before every implementation commit, its creator activates `commit` and validates the exact message file. Evaluation commits remain confined to disposable fixtures.

From `/Users/adam/dev/skills`, required final checks are:

    rtk proxy python3 skills/default/commit/evals/test_validate_message.py
    rtk proxy python3 skills/default/commit/evals/test_grade_benchmark.py
    rtk proxy env PYTHONPATH=scripts/vendor python3 skills/default/skill-creator/scripts/quick_validate.py skills/default/commit
    rtk proxy python3 skills/default/commit/evals/grade_benchmark.py skills/default/commit-workspace/iteration-N

The existing scenario-4 preparation command is:

    rtk proxy python3 skills/default/commit/evals/prepare_validation_workflow.py <new-run-directory> <immutable-skill-snapshot>

T4 must document the exact attribution preparation/provider commands and selected scenario IDs in `evals/README.md` once its additive interface exists; no such interface exists yet. Bound shell subprocesses and provider calls explicitly. Poll long-running sessions without waits over 60 seconds and send progress updates. Provider CLI discovery must inspect installed `--help`; do not guess flags or claim an unexecuted command succeeded.

## Validation and Acceptance

All command results are pending. Expected result for focused checks is exit 0; for grading it is every relevant `summary.failed == 0`, not only exit 0. An auth error, timeout, unavailable model, or missing executable is a prerequisite failure, never a passing scenario. Keep actual baseline outcomes even if they differ from the reported bug.

Full acceptance requires real Codex and real Copilot contribution sessions with omitted `co_author` producing exactly one verified provider-correct trailer; actual validator invocation containing each resolved identity; final committed content matching validated content; exactly one scoped fixture commit; no author changes or pushes; explicit user and repository precedence; no invented attribution without contribution; preservation/deduplication; missing expected trailers failing validation; all focused checks passing; and retained baseline/candidate transcripts, messages, hashes, and observed limitations. Explicit opt-out, policy, or no-contribution cases with no resolved identities must work with no `--co-author` options.

## Idempotence and Recovery

Create-only run directories and immutable snapshots prevent accidental overwrites. On interrupted execution, inspect HEAD and events before retrying; never rerun a commit prompt in an already-committed fixture. Prepare a fresh numbered run and preserve the failed/interrupted one. Reject malformed/missing evidence rather than reconstructing events from claims. Restore only this task's edits from the initial file-scoped snapshot if a rollback is needed, preserving others' changes. Never reset the working repository, rewrite history, change global author config, or delete original failed evidence. A new candidate revision requires a new snapshot identity and rerunning affected final acceptance.

## Interfaces and Dependencies

The runtime interface remains `python3 <skill-root>/scripts/validate_message.py <message-file> [--co-author 'Name <email>']...`, plus existing issue/fixes options. Each distinct supplied identity is allowed and required exactly once. The skill resolves contribution, provider, policy, and identity; the validator enforces explicit inputs.

Requires Python 3, Git, installed authenticated Codex and Copilot CLIs, provider access, and official identity evidence. Existing fixture-local hooks and validator wrapping are observers, not enforcement. Extend event schema additively to retain invocation arguments; tests must reject absent/malformed attribution evidence for new scenarios without breaking historical scenario 4. Evidence directories are disposable repositories, but their retained results are part of acceptance.

## Outcomes & Retrospective

Planning only: no implementation or validation has been performed by this plan author. All milestone acceptance remains unmet. Identity research has been inspected and its exact defaults/sources incorporated; snapshot paths exist and integration setup is parent-reported. Baseline provider results and snapshot immutability confirmation remain T1 acceptance work. Next owner is the integration coordinator, handing serialized T3 onward to the dedicated implementation worker after the snapshot gate.
