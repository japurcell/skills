# Implement the seven approved skill and hook changes

## Purpose / Big Picture

A maintainer should be able to change a rule once and see the same behavior in a relocated skill, a generated provider hook, or a disposable installation. Users still invoke each existing public command. The two new user-facing paths let them reindex a named project directly and request an attainable number of conversation batches after filtering. The seven milestone contracts below define the scope.

**Current assignments.** A single implementer owns the [two review findings](ExecPlan/review-fixes.md). The coordinator owns integration, combined checks, fresh independent standards and specification reviews, and cleanup.

**Governing principles.** Boundary Discipline puts admission and errors at the caller's interface. Redesign From First Principles and Subtract Before You Add favor one owner for each existing rule. Separate Before Serializing Shared State gives each extraction its own directory. Make Operations Idempotent governs reinstallation and generator retries. Experience First preserves CLI output and deployed behavior. Sequence Verifiable Units and Prove It Works require evidence through each public caller and again on the combined revision.

## Context and orientation

Run commands from the checkout root with RTK, Git, Python 3.12+, Bash and PowerShell available for the relevant suite. `hooks/families/` contains build-time Python source. `scripts/generate-hooks.py` renders committed provider files that run away from the repository. `skills/default/brain-install/assets/` ships the portable project installation. Its six skill directories have repository-local peers in `.agents/skills/`. `scripts/install.sh` and `scripts/install.ps1` also install the published skills. Addy has its own replacement behavior. A “candidate” below is an implementation commit on a separate local branch.

The approved design baseline is `069b3f22`. The original plan is `66e3a80e`, the rewritten plan is `ea7abf10`, and the individual assignments are in `1eaf63dc`. Integrated revisions and evidence are recorded below.

## Progress

- [x] (2026-11-19) Seven outcomes approved, original adversarial design review closed, concrete alternatives re-ranked for this rewrite.
- [x] (2026-11-19) [milestone-1] Integrated T1a at `059166bf`. The CLI and grader agree on single, wrapped and empty bullets. Both suites passed (15 and 30 tests).
- [x] (2026-11-19) [milestone-1] [Commit message validation](ExecPlan/1-commit-validation.md). Integrated independent intent and attribution checks. Both suites passed at `92a8c0a0`.
- [x] (2026-11-19) [milestone-2] Direct command and installer candidate available in `7f16d86b`. Reproduced an extra-link false success on that revision.
- [x] (2026-11-19) [milestone-2] Repaired the retained-index verifier and integrated M2 at `ebb09bb4`. Freshness and installer checks passed on macOS.
- [x] (2026-11-19) [milestone-2] [Direct reindex](ExecPlan/2-direct-reindex.md). Native directory permissions and the retained-helper target inventory passed. Both original files survived failed verification.
- [x] (2026-11-19) [milestone-3] Frozen public-process fixture passed against reference and candidate on macOS at `886dea6a`.
- [x] (2026-11-19) [milestone-3] [Hook event input](ExecPlan/3-hook-input.md). The shipped pipe test passed on macOS and Windows, including exact forwarded bytes.
- [x] (2026-11-19) [milestone-4] Query and standalone timer ordering integrated at `b386efe`.
- [x] (2026-11-19) [milestone-4] [Scheduler wake and completion](ExecPlan/4-scheduler-wake.md). Integrated measured native timing and the limitations of each caller at `c406fc2d`.
- [x] (2026-11-19) [milestone-5] Froze the original 20 commands and owned metadata at `eb949e2`.
- [x] (2026-11-19) [milestone-5] [Project brain launch registrations](ExecPlan/5-project-launchers.md). Publication, concurrent-edit recovery, frozen commands and installed readback passed at `615111b3`.
- [x] (2026-11-19) [milestone-6] [Skill copy policy](ExecPlan/6-skill-copy.md). The shipped installer passed the native Windows junction fixture and the local copy and readback checks.
- [x] (2026-11-19) [milestone-7] Project-mode batching and the relocated caller fixture exist in `149a2661`.
- [x] (2026-11-19) [milestone-7] Integrated batching at `ffe630df` and repeated shared bundle verification with M2 at `ebb09bb4`. The macOS suite ran 58 tests with four skips.
- [x] (2026-11-19) [milestone-7] [Conversation batches](ExecPlan/7-conversation-batches.md). The relocated workflow and all four Windows ACL cases passed. The Windows matrix passed on Python 3.12 and 3.14.

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

Run the combined local and native checks for the integrated revision. If a merge stops, resolve only the scoped conflicts or abort the in-flight merge and retry from the recorded revisions.

Run each milestone's listed checks. After M2/M3/M5 regeneration, run `rtk proxy python3 scripts/tests/hooks/test-generate-hooks.py` and `rtk proxy python3 scripts/generate-hooks.py --check`. Follow the repository-local `verify-skills` Doctor, default installation, selection and provider-hook journeys for affected installers using fresh disposable homes, then run `rtk proxy python3 scripts/test-all.py` with the checkout idle. Record revision, OS, command, exit, observed output and any skips. Expect current generated files, correct installed file/registration readback and passing applicable suites. On failure retain the fixture and fix its owning source, regenerate and repeat the affected checks on the combined revision.

The coordinator schedules direct-index permissions (M2), event pipes (M3), junction copying (M6) and private conversation-workspace ACL checks (M7) on native Windows. The native operator runs M4's inverted two-worker trial for each host/caller path for which prompt delivery is claimed. Until those observations exist, keep the corresponding acceptance open. M7's approved consumer proof uses recorded worker inputs from a relocated bundle and synthetic histories.

## Outcomes & Retrospective

All seven milestone results are recorded above. The final integration includes the corrected Windows test user, both new suites in the repository runner, and measured Codex and Copilot delivery limits. The independent final review and task cleanup remain.
