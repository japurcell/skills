# Implement the seven approved skill and hook changes

## Purpose / Big Picture

A maintainer should be able to change a rule once and see the same behavior in a relocated skill, a generated provider hook, or a disposable installation. Users still invoke each existing public command. The two new user-facing paths let them reindex a named project directly and request an attainable number of conversation batches after filtering. The seven milestone contracts below define the scope.

**Next implementation action:** the M2 implementer takes [T2b, repair retained-index verification](ExecPlan/2b-retained-index.md) on the existing candidate. The coordinator owns integration on `work/skill-hook-architecture`. Preserve the candidate commits and this rewritten plan when bringing changes together.

**Governing principles.** Boundary Discipline puts admission and errors at the caller's interface. Redesign From First Principles and Subtract Before You Add favor one owner for each existing rule. Separate Before Serializing Shared State gives each extraction its own directory. Make Operations Idempotent governs reinstallation and generator retries. Experience First preserves CLI output and deployed behavior. Sequence Verifiable Units and Prove It Works require evidence through each public caller and again on the combined revision.

## Context and orientation

Run commands from the checkout root with RTK, Git, Python 3.12+, Bash and PowerShell available for the relevant suite. `hooks/families/` contains build-time Python source. `scripts/generate-hooks.py` renders committed provider files that run away from the repository. `skills/default/brain-install/assets/` ships the portable project installation. Its six skill directories have repository-local peers in `.agents/skills/`. `scripts/install.sh` and `scripts/install.ps1` also install the published skills. Addy has its own replacement behavior. A “candidate” below is an implementation commit on a separate local branch.

The approved design baseline is `069b3f22`. The original plan was committed in `66e3a80e`. At this rewrite the integration branch is at `64a92191`. M2 and M7 branch from the original plan. M6's worktree still points at that plan commit. Check `rtk proxy git worktree list` and `rtk proxy git log --oneline --all --decorate -12` for current refs before assigning work.

## Progress

- [x] (2026-11-19) Seven outcomes approved, original adversarial design review closed, concrete alternatives re-ranked for this rewrite.
- [ ] [milestone-1] [Commit message validation](ExecPlan/1-commit-validation.md). Open. Compare the public validator and dry-run grader, then verify independent issue intent.
- [x] (2026-11-19) [milestone-2] Direct command and installer candidate available in `7f16d86b`. Reproduced an extra-link false success on that revision.
- [ ] [milestone-2] [Direct reindex](ExecPlan/2-direct-reindex.md). In progress. Repair verification, integrate and exercise the installed and native paths.
- [ ] [milestone-3] [Hook event input](ExecPlan/3-hook-input.md). Open. Capture original behavior, then migrate consumers against identical streams.
- [ ] [milestone-4] [Scheduler wake and completion](ExecPlan/4-scheduler-wake.md). Open. Capture the native baseline, implement timer selection and verify delivery on each claimed host.
- [ ] [milestone-5] [Project brain launch registrations](ExecPlan/5-project-launchers.md). Open. Freeze the command fixture before changing the generator.
- [ ] [milestone-6] [Skill copy policy](ExecPlan/6-skill-copy.md). Open. Qualify the filesystem adapter before switching the installers.
- [x] (2026-11-19) [milestone-7] Project-mode batching and the relocated caller fixture exist in `149a2661`.
- [ ] [milestone-7] [Conversation batches](ExecPlan/7-conversation-batches.md). In progress. Integrate the candidate, repeat its checks alongside M2 and verify Windows workspace permissions.

## Plan of work and dependencies

The coordinator owns tasks described inside each milestone until assigning one to a worker. The first worker-ready assignment has its own file. Before dispatching any other independently owned task, copy its current inputs, prerequisite evidence, checks and stopping point into a linked assignment file. Workers update only their own assignment. The coordinator reconciles milestone and entry status together.

M1, M4's baseline and timer work, M5's frozen fixture, M6's qualification, and review of M7's candidate can proceed independently of T2b. M3 can capture the old inputs immediately. Publish generated output in order **M2, M3, M5** in the integration checkout. M3 can proceed once M2's corrected candidate is integrated and fresh. M5 publication requires M3's integrated generated files and the independently captured fixture. Native proof may proceed separately from that publication order. M2 and M7 share the portable brain bundle, so run their installation and parity checks on the same tree after both land. Serialize generator tests and installer fixtures that snapshot or mutate the checkout.

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

Start with [T2b](ExecPlan/2b-retained-index.md). After its installer check passes, inspect the candidate changes against the branch point, bring the product changes into the integration branch and preserve the current plan documents during conflict resolution. Apply the same procedure to M7. Inspect `rtk proxy git diff 66e3a80e 149a2661 --stat` before integrating it. If a cherry-pick stops on a plan file, retain the rewritten contract and reconcile verified results into it. Abort an unsuccessful in-flight pick to retry from its original revision. Keep both worker refs until integrated verification passes.

Run each milestone's listed checks. After M2/M3/M5 regeneration, run `rtk proxy python3 scripts/tests/hooks/test-generate-hooks.py` and `rtk proxy python3 scripts/generate-hooks.py --check`. Follow the repository-local `verify-skills` Doctor, default installation, selection and provider-hook journeys for affected installers using fresh disposable homes, then run `rtk proxy python3 scripts/test-all.py` with the checkout idle. Record revision, OS, command, exit, observed output and any skips. Expect current generated files, correct installed file/registration readback and passing applicable suites. On failure retain the fixture and fix its owning source, regenerate and repeat the affected checks on the combined revision.

The coordinator schedules direct-index permissions (M2), event pipes (M3), junction copying (M6) and private conversation-workspace ACL checks (M7) on native Windows. The native operator runs M4's inverted two-worker trial for each host/caller path for which prompt delivery is claimed. Until those observations exist, keep the corresponding acceptance open. M7's approved consumer proof uses recorded worker inputs from a relocated bundle and synthetic histories.

## Outcomes & Retrospective

At the 2026-11-19 rewrite, two of seven milestones have unmerged product candidates. M2 needs a correctness fix, and M7 has branch-local fixture evidence. All seven integrated acceptance decisions remain open. The generator, installer, native platform and host checks above establish when the work can be called complete.
