# Verify worker dispatch and deadline enforcement

## Purpose / Big Picture

A parent running delegate-to-subagents or execplan-implement can wait quietly for a healthy worker, handle early completion, and enforce a deadline on a silent worker. Both Copilot CLI and Codex must demonstrate this. In the dispatch instructions, find the shortest tested wording that avoids known-invalid model calls and still attempts an allowed model missing from descriptive help. Preserve the router's policy and the user's choices. User-only skill invocation is outside this work.

Prove It Works and Boundary Discipline govern what a host trace establishes. Model the Domain and Separate Before Serializing Shared State put each assignment under one owner. Guard the Context Window, Subtract Before You Add and Explain the Number govern the wording comparison. Sequence Verifiable Units keeps baseline capture independent of candidate testing.

## Next action and task graph

The scheduler implementer completed [S1, helper baseline and repair](38-dispatch-and-deadlines-exec-plan/scheduler.md). The native operators are running [B1, Copilot baseline](38-dispatch-and-deadlines-exec-plan/copilot-baseline.md) and [B2, Codex baseline](38-dispatch-and-deadlines-exec-plan/codex-baseline.md). Each native assignment stops at its own baseline. The integration branch is `feat/todo-38-dispatch-deadlines`. The verified coordinator follow-up handle is `/root/codex`.

[E1, controlled behavior](38-dispatch-and-deadlines-exec-plan/controlled.md) and [W1, candidate screening](38-dispatch-and-deadlines-exec-plan/wording.md) also depend on the design review. E1 owns the orchestration fixtures, W1 owns distinct wording fixtures in the same test directory. P1 requires W1, E1 and the Copilot baseline. N1 runs only for a host/caller needing new proof. I1 verifies and reconciles the combined result. See [P1, N1 and I1 assignments](38-dispatch-and-deadlines-exec-plan/native-and-close.md). Each receives a separate assignment when its prerequisites have evidence. The parent updates this entry after verifying results.

[R1, caller lifecycle instructions](38-dispatch-and-deadlines-exec-plan/runtime.md) owns the caller-side changes exposed by S1, E1 and the old native cases. W1 and P1 own the dispatch wording. N1 uses the integrated lifecycle changes. These assignments can test the two behaviors independently.

## Decision Log

- The user approved one state owner, a silent-worker watchdog, one ETA-based extension, safe transfer, compact reporting and repeatable on-demand host trials. Completion notifications re-arm the remaining watch. The implementation must establish which layer owns state and which layer acts.
- Architectural review: fresh reviewer `/root/design_review38` used the codebase-design assignment to grade three shapes. **First: B** keeps lifecycle state in the existing owner for each workflow. Delegate uses the Python state file, and ExecPlan uses the parent's assignment registry. The parent arms one earliest-deadline wakeup and uses host controls to message, stop and verify writes. **Second: A**, all-native state and timers, makes silence, extension and transfer depend on two independently implemented policies. **Third: C**, a mandatory Python supervisor and per-host adapters, adds a process without gaining access to host-private notification and stop evidence. Choose B. Existing explicit periodic intervals and active v2 state keep their meaning. Ordinary new assignments should be deadline-only.
- The same reviewer ranked native traces plus small deterministic fixtures first, simulation alone second, and prose grading third. Use the first approach. Require native observations for the four host/caller verdicts. Use fixture evidence for deterministic edge cases. Label unobserved runtime settings unknown.
- Both callers keep the same short dispatch instruction. The router skill owns shared exception and reuse rules. Freeze router code/catalog, host settings, effort policy, user-model precedence and capability floor in comparisons. Keep before/after records and routing metadata outside worker prompts. An enforced worker restriction that excludes the model requires zero calls. A model absent only from descriptive help can be attempted. An initially unknown model-wide rejection permits one attempt and rules out retries at other efforts.
- Count the words read by one caller plus its shared gate. A candidate must preserve all requirements, beat or tie the longer candidate on behavior, and withstand a one-clause deletion challenge. Three matched old/new Copilot pairs per caller. Retain failures. A tied baseline supports a shorter-wording claim only. No general reliability or compaction-rate claim follows from a single trace.

## Progress

- [x] (2026-11-18) [milestone-1] Pinned `7fc651a7702735f0b13d1f50695a8ef0ddc96477`, verified the historical archive checksum, analysis and negative tests, and reviewed architecture before renewed dispatch.
- [x] (2026-11-18) [milestone-1] Parent and S1 worker independently reproduced a status-only `progress_reminder` at 300 seconds and `deadline_expired` at 600 seconds through the old public helper. Baseline suites passed 11 scheduler and 26 router tests.
- [ ] [milestone-1] Complete B1 and B2 native baseline evidence.
- [x] (2026-11-18) [milestone-2] S1 at `af044126` passes 17 scheduler CLI tests. New ordinary assignments are quiet until expiry. Explicit intervals and active version 2 records retain their old behavior.
- [ ] [milestone-2] E1 continuity/reporting/transfer cases and negative controls. R1 caller instructions and verification.
- [ ] [milestone-3] W1 shorter candidate and challenger, P1 six matched Copilot pairs.
- [ ] [milestone-4] N1 and I1 integrated verdict, review and backlog reconciliation.

## Milestone 1. Establish comparable baselines

Status: in progress
Acceptance: not met

From the repo root verify `rtk git rev-parse HEAD` and the old revision above. Commit `b7874592` changed the planning skill only. Git showed no difference in the three target skills. Each operator records the active CLI version, source identities, normal provider-managed session and evidence directory. Missing auth, rejected sandbox access and missing host events remain distinct from semantic failures. Store no credentials or private application data. B1 and B2 end with a recorded host verdict or blocker. A blocker leaves the affected live acceptance open.

## Milestone 2. Verify lifecycle, continuity and status

Status: in progress
Acceptance: not met

The delegate source is `skills/default/delegate-to-subagents/scripts/scheduler.py`. Test via its CLI and `scripts/test_scheduler.py` in the same skill. The ExecPlan caller's runtime-enforcement section owns its registry policy. Demonstrate early completion, quiet time, deadline expiry, bounded grace, one extension and separate worker/write shutdown checks before transfer. Exercise both same-task delivery of a setup fact and fresh-worker recovery with the environment, pinned revision and prior evidence. Compare two status reports for owner, revision, completed evidence, blocker, deadline and next action. The second uses stable references instead of reconstructing history. Use the same grader on an unnecessary five-minute status lookup and a legitimate expiry.

## Milestone 3. Compare gates

Status: open
Acceptance: not met

Run W1 against the frozen gate, short shared rule and shorter challenger. P1 uses actual Copilot router and dispatch events for both callers. A model name in the worker prompt, a worker ID alone, or a recreated JSON event does not establish the effective settings. Publish winning text only on applicable passing evidence. Full scope and [earlier research](../../docs/subagent-dispatch-research.md) supplement the assignment.

## Milestone 4. Validate the combined revision

Status: open
Acceptance: not met

Each of four skill/host pairings must show real early completion, quiet waiting, and action at the remaining deadline. A passing baseline counts. Repeat affected cases after a fix, retain every failure and classify it. Run the focused suites and independent standards and spec reviews. Keep todo 38 open until the controlled cases, live runs and wording verdict meet the agreed bar.

## Concrete steps, validation and recovery

From the repository root run `rtk proxy python3 skills/default/delegate-to-subagents/scripts/test_scheduler.py`, `rtk proxy python3 skills/default/subagent-model-router/scripts/test_route.py`, `rtk proxy python3 -m unittest discover -s scripts/tests/orchestration`, `rtk proxy python3 scripts/validate-skill-sources.py skills` and `rtk git diff --check`. The new controlled suite must execute actual tests. A zero-test run means evidence is missing. Expected verdicts, native setup steps and stopping conditions are in the linked assignments. Record exact native invocations after the first valid run.

Use fresh run directories, identify old and new sources by Git revision or content hash and preserve previous partial runs on retry. No global installation or policy change is required. If the sandbox restricts legitimate vendor connections, request approval for the scoped native action. If the provider then requires owner authentication, record that prerequisite and proceed with offline work. Earlier startup artifacts are under `/private/tmp/todo38-1795057091956/{copilot,codex}`.

## Surprises & Discoveries

The supplied metadata trace has 25 prompts from a recurring five-minute Copilot host schedule. In 17 windows the only parent tool start was an assignment lookup. The delegate helper ran earlier in the session. Seven of ten compactions occurred in workers and one parent compaction was manual. The private stream and historical skill bodies are unavailable. The first local attempts saw Copilot CLI 1.0.114 and Codex CLI 0.170.0. A disposable Copilot home started a new OAuth flow and hit a loopback permission error. Codex stopped first at a non-repository fixture and later at an invalid features subcommand. Neither attempt produced worker evidence.

## Outcomes & Retrospective

The design review and historical baseline are complete. Current-host acceptance, the controlled suite, and candidate selection remain open. The earlier plan bundled baseline and candidate trials in one assignment; the new task graph stops each worker at the first independently verifiable outcome.
