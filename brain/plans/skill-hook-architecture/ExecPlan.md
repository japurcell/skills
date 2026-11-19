# Implement the seven approved skill and hook changes

## Purpose / Big Picture

A maintainer should be able to change a rule once and see the same behavior in a relocated skill, a generated provider hook, or a disposable installation. Users still invoke each existing public command. The two new user-facing paths let them reindex a named project directly and request an attainable number of conversation batches after filtering. The seven milestone contracts below define the scope.

**Current assignments.** The commit-skill maintainer owns [T1b issue intent](ExecPlan/1b-intent.md). The hook maintainer owns the [T3b reader](ExecPlan/3b-input-reader.md), and the scheduler maintainer owns [T4b timer selection](ExecPlan/4b-timer.md). The integration coordinator brings tested revisions into `work/skill-hook-architecture`.

**Governing principles.** Boundary Discipline puts admission and errors at the caller's interface. Redesign From First Principles and Subtract Before You Add favor one owner for each existing rule. Separate Before Serializing Shared State gives each extraction its own directory. Make Operations Idempotent governs reinstallation and generator retries. Experience First preserves CLI output and deployed behavior. Sequence Verifiable Units and Prove It Works require evidence through each public caller and again on the combined revision.

## Context and orientation

Run commands from the checkout root with RTK, Git, Python 3.12+, Bash and PowerShell available for the relevant suite. `hooks/families/` contains build-time Python source. `scripts/generate-hooks.py` renders committed provider files that run away from the repository. `skills/default/brain-install/assets/` ships the portable project installation. Its six skill directories have repository-local peers in `.agents/skills/`. `scripts/install.sh` and `scripts/install.ps1` also install the published skills. Addy has its own replacement behavior. A “candidate” below is an implementation commit on a separate local branch.

The approved design baseline is `069b3f22`. The original plan is `66e3a80e`, the rewritten plan is `ea7abf10`, and the individual assignments are in `1eaf63dc`. Integrated revisions and evidence are recorded below.

## Progress

- [x] (2026-11-19) Seven outcomes approved, original adversarial design review closed, concrete alternatives re-ranked for this rewrite.
- [x] (2026-11-19) [milestone-1] Integrated T1a at `059166bf`. The CLI and grader agree on single, wrapped and empty bullets. Both suites passed (15 and 30 tests).
- [ ] [milestone-1] [Commit message validation](ExecPlan/1-commit-validation.md). Complete T1b's scenario-specific issue and author checks.
- [x] (2026-11-19) [milestone-2] Direct command and installer candidate available in `7f16d86b`. Reproduced an extra-link false success on that revision.
- [x] (2026-11-19) [milestone-2] Repaired the retained-index verifier and integrated M2 at `ebb09bb4`. Freshness and installer checks passed on macOS.
- [ ] [milestone-2] [Direct reindex](ExecPlan/2-direct-reindex.md). Native Windows qualification remains open.
- [x] (2026-11-19) [milestone-3] Frozen public-process fixture passed against reference and candidate on macOS at `886dea6a`.
- [ ] [milestone-3] [Hook event input](ExecPlan/3-hook-input.md). Migrate readers and verify identical public behavior.
- [ ] [milestone-4] [Scheduler wake and completion](ExecPlan/4-scheduler-wake.md). Offline baseline passed. Verify the timer and host adapters. Native timing remains open.
- [ ] [milestone-5] [Project brain launch registrations](ExecPlan/5-project-launchers.md). Open. Freeze the command fixture before changing the generator.
- [ ] [milestone-6] [Skill copy policy](ExecPlan/6-skill-copy.md). Open. Qualify the filesystem adapter before switching the installers.
- [x] (2026-11-19) [milestone-7] Project-mode batching and the relocated caller fixture exist in `149a2661`.
- [x] (2026-11-19) [milestone-7] Integrated batching at `ffe630df` and repeated shared bundle verification with M2 at `ebb09bb4`. The macOS suite ran 58 tests with four skips.
- [ ] [milestone-7] [Conversation batches](ExecPlan/7-conversation-batches.md). Windows workspace permissions remain open.

## Plan of work and dependencies

Each independently assignable task is linked from its milestone. Workers own their assignment files. The parent reconciles milestone and entry status at integration checkpoints.

M1, M4, the frozen M5 fixture and M6 qualification can progress independently. The generated-output integration order is M2 (integrated), M3, then M5. M5 publication also needs the independent fixture. The shared M2/M7 installation and parity runs passed on the integrated macOS tree. Serialize generator and installer fixtures that snapshot or mutate a single checkout.

## Decision Log

On 2026-11-19 the author and a fresh reviewer using `codebase-design` compared concrete interfaces against the approved contracts. Grades below are the reviewer's judgments, in rank order.

1. **Commit grammar.** Parse the message once in the validator and return its parsed header, sections and ordered trailers (A). Running the CLI for a verdict and parsing trailer text again in the grader (C) creates two grammars. The grader still owns its independent scenario expectations.
2. **Brain inventory.** Generate a standalone direct command and read-only verification from the hook inventory owner (A). A second scanner in the installer (D) can agree with a stale helper. The actual vault contents establish the expected link targets.
3. **Event input.** Render a byte collector with consumer-specific completion and admission policy (A-). A general JSON normalizer (C) loses the bytes that RTK forwards and changes whitespace acceptance.
4. **Scheduler.** Use the existing per-assignment timer selector for a locked read-only query and for due transitions (A). A separate notification service or second registry (D) duplicates state and still cannot guarantee native delivery. Keep ExecPlan's pre-launch reservation.
5. **Launch registrations.** Define the owned registration fields once and merge exact known identities under the writer lock (A-). Whole-document replacement (F) can discard unrelated handlers. Freeze an independent fixture before enabling writes.
6. **Skill copying.** One traversal with two explicit profiles and native file operations (A-) ranks above replacing all filesystem behavior with a generic Python copier (B-) and duplicating traversal per installer (D). Qualify the concrete Windows adapter on a real filesystem before switching that caller.
7. **Conversation batches.** Filter once, partition the accepted sequence and publish a private run (A). Counting twice (B-) allows the input to change between scans. Regrouping legacy manifests (D) makes publication depend on stale output. Keep the candidate's JSON keys, `accepted_count` and `manifests`.

The earlier review compared build-time sharing, consumer-local copies with parity, and a shared installed runtime. In that order its grades for M1 through M7 were A/C/D, A/D/D, A/C/D, A-/B/F, A/C/F, A-/B-/D and A/B/D. Both reviews favor standalone deployable files and independent acceptance oracles.

## Surprises & Discoveries

- A wrapped Summary passed the real validator and lost grading credit. An empty bullet failed validation and received full credit.
- On `7f16d86b`, a retained no-op helper and a current index passed. Appending a prose link to an absent note also yielded exit 0 and `Installation complete; brain/index.md verified`. The extra link survived. The trusted verifier only collected full bullet lines.
- With six matching conversations and four requested batches the legacy splitter wrote three manifests. On the M7 candidate the corresponding project invocation produced four, with sizes 2, 2, 1 and 1.

## Concrete steps, validation and recovery

Continue the current assignments above. The next independent tasks are the [M5 rollout fixture](ExecPlan/5a-launch-oracle.md) and the [M6 adapter qualification](ExecPlan/6a-adapter.md). For each integration, preserve the current plan and results and run the milestone checks on the merged tree. If a merge stops, resolve only the scoped conflicts or abort the in-flight merge and retry from the recorded revisions.

Run each milestone's listed checks. After M2/M3/M5 regeneration, run `rtk proxy python3 scripts/tests/hooks/test-generate-hooks.py` and `rtk proxy python3 scripts/generate-hooks.py --check`. Follow the repository-local `verify-skills` Doctor, default installation, selection and provider-hook journeys for affected installers using fresh disposable homes, then run `rtk proxy python3 scripts/test-all.py` with the checkout idle. Record revision, OS, command, exit, observed output and any skips. Expect current generated files, correct installed file/registration readback and passing applicable suites. On failure retain the fixture and fix its owning source, regenerate and repeat the affected checks on the combined revision.

The coordinator schedules direct-index permissions (M2), event pipes (M3), junction copying (M6) and private conversation-workspace ACL checks (M7) on native Windows. The native operator runs M4's inverted two-worker trial for each host/caller path for which prompt delivery is claimed. Until those observations exist, keep the corresponding acceptance open. M7's approved consumer proof uses recorded worker inputs from a relocated bundle and synthetic histories.

## Outcomes & Retrospective

The retained-index false success is fixed and exact conversation batching is integrated. The combined bundle passed on macOS with Windows cases skipped. T1a is integrated. The user selected local checks. Windows and authenticated host observations remain open. The implementation and local review continue on this topic branch.
