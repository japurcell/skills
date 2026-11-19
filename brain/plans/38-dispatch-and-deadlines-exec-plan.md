# Verify worker dispatch and deadline enforcement

## Purpose / Big Picture

A parent running delegate-to-subagents or execplan-implement can wait quietly for a healthy worker, handle early completion, and enforce a deadline on a silent worker. Both Copilot CLI and Codex must demonstrate this. In the dispatch instructions, find the shortest tested wording that avoids known-invalid model calls and still attempts an allowed model missing from descriptive help. Preserve the router's policy and the user's choices. User-only skill invocation is outside this work.

Prove It Works and Boundary Discipline govern what a host trace establishes. Model the Domain and Separate Before Serializing Shared State put each assignment under one owner. Guard the Context Window, Subtract Before You Add and Explain the Number govern the wording comparison. Sequence Verifiable Units keeps baseline capture independent of candidate testing.

## Next action and task graph

The operator is running the [P2 required-profile comparison](38-dispatch-and-deadlines-exec-plan/paired-dispatch.md#p2-preserve-the-worker-profile-as-well-as-the-model). The native operator owns [N2 writer shutdown](38-dispatch-and-deadlines-exec-plan/writer-shutdown.md). After these runs, the integration coordinator owns [I1](38-dispatch-and-deadlines-exec-plan/integration.md). The user authorized both caller skills, router instructions and synthetic fixtures for authenticated Codex and Copilot evaluations. The historical remote trace and credentials stay local.

## Decision Log

- The user approved one state owner, a silent-worker watchdog, one ETA-based extension, safe transfer, compact reporting and repeatable on-demand host trials. Completion notifications re-arm the remaining watch. The implementation must establish which layer owns state and which layer acts.
- Architectural review: fresh reviewer `/root/design_review38` used the codebase-design assignment to grade three shapes. **First: B** keeps lifecycle state in the existing owner for each workflow. Delegate uses the Python state file, and ExecPlan uses the parent's assignment registry. The parent arms one earliest-deadline wakeup and uses host controls to message, stop and verify writes. **Second: A**, all-native state and timers, makes silence, extension and transfer depend on two independently implemented policies. **Third: C**, a mandatory Python supervisor and per-host adapters, adds a process without gaining access to host-private notification and stop evidence. Choose B. Existing explicit periodic intervals and active v2 state keep their meaning. Ordinary new assignments should be deadline-only.
- The same reviewer ranked native traces plus small deterministic fixtures first, simulation alone second, and prose grading third. Use the first approach. Require native observations for the four host/caller verdicts. Use fixture evidence for deterministic edge cases. Label unobserved runtime settings unknown.
- Both callers keep the same short dispatch instruction. The router skill owns shared exception and reuse rules. Freeze router code/catalog, host settings, effort policy, user-model precedence and capability floor in comparisons. Keep before/after records and routing metadata outside worker prompts. An enforced worker restriction that excludes the model requires zero calls. A model absent only from descriptive help can be attempted. An initially unknown model-wide rejection permits one attempt and rules out retries at other efforts.
- Count the words read by one caller plus its shared gate. A candidate must preserve all requirements, beat or tie the longer candidate on behavior, and withstand a one-clause deletion challenge. Three matched old/new Copilot pairs per caller. Retain failures. A tied baseline supports a shorter-wording claim only. No general reliability or compaction-rate claim follows from a single trace.

- The newly supplied [scheduling research](scheduler-research.md) separates the clock, the host stop operation and the final write. Retain the existing state owners and add a native heartbeat trial. Ordinary Copilot delegation has a documented interactive kill. When no model-callable stop or independent shutdown proof is available, leave ownership in place and report it. A host-controlled watchdog can stop work only where the host exposes that capability.

## Progress

- [x] (2026-11-18) [milestone-1] Pinned `7fc651a7702735f0b13d1f50695a8ef0ddc96477`, verified the historical archive checksum, analysis and negative tests, and reviewed architecture before renewed dispatch.
- [x] (2026-11-18) [milestone-1] Parent and S1 worker independently reproduced a status-only `progress_reminder` at 300 seconds and `deadline_expired` at 600 seconds through the old public helper. Baseline suites passed 11 scheduler and 26 router tests.
- [x] (2026-11-18) [milestone-1] All four old native pairings launched real workers and exposed lifecycle misses. See the B1 and B2 task records. Both control hosts are available.
- [x] (2026-11-18) [milestone-2] S1 at `af044126` passes 17 scheduler CLI tests. New ordinary assignments are quiet until expiry. Explicit intervals and active version 2 records retain their old behavior.
- [x] (2026-11-18) [milestone-2] E1 at `b1a63dd2` passes six controlled tests, including rejection of a quiet-time lookup and transfer while a separate writer is active.
- [x] (2026-11-18) [milestone-2] Integrated R1 at `5f2892ab`. Both caller hashes match the tested sources. The combined checkout passed 17 scheduler tests, six controlled tests and skill-source validation. Native acceptance belongs to milestone 4.
- [x] (2026-11-18) [milestone-2] Integrated 9ac6517c, nine controlled checks and 17 scheduler checks. [E2, fail missing evidence](38-dispatch-and-deadlines-exec-plan/missing-evidence.md), after three empty-input false positives reproduced in the public grader.
- [x] (2026-11-18) [milestone-3] W1 observed 23/23 for each baseline, short and challenger caller after hardening the trace grader. Deleting the original effort condition failed the reuse case in both callers (22/23 each).
- [x] (2026-11-18) [milestone-3] P1 ran six native pairs. Both arms avoided the excluded model on all six attempts. Old callers selected the required worker profile 6/6, the shorter callers 4/6.
- [ ] [milestone-3] P2 tests a shared Copilot profile-field example before publication.
- [x] (2026-11-18) [milestone-4] First Copilot N1 trials exposed a delayed native notification and a late checkpoint. Both original traces retained.
- [x] (2026-11-18) [milestone-4] R2 wait guidance integrated at c66ae7a8. Both Codex replays produced the expected bytes.
- [x] (2026-11-18) [milestone-4] All four caller/host combinations demonstrated quiet waiting, early closure and real silent-worker enforcement. R3 Copilot had a 2.909-second wait delivery lag and acted within grace.
- [ ] [milestone-4] N2 active-writer measurements and I1 integrated verification, review and backlog reconciliation.

## Milestone contracts and integration evidence

| Milestone | Status | Acceptance |
| --- | --- | --- |
| [1. Historical and native baselines](38-dispatch-and-deadlines-exec-plan/baselines.md) | done | met |
| [2. Lifecycle, continuity and reporting](38-dispatch-and-deadlines-exec-plan/lifecycle.md) | done | met |
| [3. Controlled and live dispatch comparison](38-dispatch-and-deadlines-exec-plan/dispatch.md) | in progress | not met |
| [4. Integrated native acceptance and review](38-dispatch-and-deadlines-exec-plan/native-and-close.md) | in progress | not met |

## Concrete steps, validation and recovery

Next, finish P2 and N2 using their frozen inputs and update the native evidence. At integration, from the repository root run `rtk proxy python3 skills/default/delegate-to-subagents/scripts/test_scheduler.py`, `rtk proxy python3 skills/default/subagent-model-router/scripts/test_route.py`, `rtk proxy python3 -m unittest discover -s scripts/tests/orchestration`, `rtk proxy python3 scripts/validate-skill-sources.py skills` and `rtk git diff --check`. The new controlled suite must execute actual tests. A zero-test run means evidence is missing. Expected verdicts, native setup steps and stopping conditions are in the linked assignments. Record exact native invocations after the first valid run.

Use fresh run directories, identify old and new sources by Git revision or content hash and preserve previous partial runs on retry. No global installation or policy change is required. If the sandbox restricts legitimate vendor connections, request approval for the scoped native action. If the provider then requires owner authentication, record that prerequisite and proceed with offline work. Earlier startup artifacts are under `/private/tmp/todo38-1795057091956/{copilot,codex}`.

## Surprises & Discoveries

The supplied metadata trace has 25 prompts from a recurring five-minute Copilot host schedule. In 17 windows the only parent tool start was an assignment lookup. The delegate helper ran earlier in the session. Seven of ten compactions occurred in workers and one parent compaction was manual. The private stream and historical skill bodies are unavailable. The first local attempts saw Copilot CLI 1.0.114 and Codex CLI 0.170.0. A disposable Copilot home started a new OAuth flow and hit a loopback permission error. Codex stopped first at a non-repository fixture and later at an invalid features subcommand. Neither attempt produced worker evidence.

## Outcomes & Retrospective

The historical trace, four native scheduling baselines and four post-change lifecycle demonstrations are verified. The deterministic lifecycle and routing controls pass. P1 found two wrong-profile dispatches despite the correct model. P2 and N2 investigate native profile selection and writer shutdown. The calibrated project hook reproduces a known exclusion, while the original remote account's picker configuration is unknown.
