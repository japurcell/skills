# R1. Make the parent act on completion and deadlines

The runtime implementer owns the assignment, progress and runtime-enforcement text in both callers. The dispatch gate and router belong to W1/P1. Start from S1 at `af044126`. Read the E1 observations and the recorded old-case failures for the affected host. Preserve the router, the existing helper CLI, the explicit progress option, and the host's cancellation and write-shutdown checks.

Reproduce the missing behavior with the old caller in a recorded exercise. Identify the first observable decision that failed. Revise the instructions at that decision. With two workers, consume the early result, clear its alarm and arm the single nearest outstanding deadline. Quiet time alone calls for no new assignment or status lookup. At real expiry, use the existing bounded checkpoint and one-extension policy. Retain a watchdog when completion notifications are absent. Use the assignment record for the current owner, revision, completed evidence, blocker, deadline and next action. On same-task follow-up verify receipt using relevant prior setup. When transport is unavailable or a new worker is required, send the environment, pinned revision and prior evidence.

Replay the controlled cases and identify which native pairings need N1. Preserve the original failure and the changed observations. Record exact revisions, verification commands and remaining native checks here. Stop after the parent guidance and controlled behavior can be verified independently. N1 owns the native verdict.

## Replay and implementation evidence

The pre-R1 caller source is the parent-reported old runtime at `b1a63dd2`, immediately after S1/E1 and before these changes. Recorded native observations supplied by the parent show the first failed decisions:

- Codex: a silent assignment began at `03:31:30.064Z`; the parent requested status at `03:31:40.247Z`, ten seconds into a twelve-second budget, and launched multiple new worker pairs for the same task. The first failure was premature status/duplicate dispatch while the original task remained active.
- Copilot: a silent assignment began at `03:42:52.032Z`; the quick worker completed at `03:43:21.359Z`; the parent read the silent worker at `03:43:38.740Z`, before its 55-second deadline. A separate exercise supplied a past wall-clock timestamp, registered `--now 1800000000` and `--deadline 1800000055`, then used that frozen timestamp with a real `wait`. The first failures were an unnecessary pre-deadline lookup and non-live test-time values in enforcement.
- The historical Copilot trace's 17 lookup-only windows are summarized in the controlled evidence (`scripts/tests/orchestration/README.md`); they establish the recorded prompt pattern, not a due deadline event.

The R1 edits revise only each caller's `Runtime enforcement` section. Both now keep all assignments in one registry/state file while arming one nearest wake, consume completion before rearming, avoid polling other workers at idle or after a completion, detect duplicate active task assignments before dispatch, and request status only at a real expiry. They preserve bounded checkpoint and one-extension handling, require a same-worker fact check or a replacement handoff with environment/revision/evidence, and use six-field compact reports. The delegate instructions explicitly omit `--now` during live waits. Pre-dispatch and router text remains unchanged.

The pre-edit content hashes at `b1a63dd2` were:

- `skills/default/delegate-to-subagents/SKILL.md`: `8eb1f5308eabdddbe774fe4c9b0be663d8dd12d0bcbfed7f05d19a5cd3a8e044`
- `skills/default/execplan-implement/SKILL.md`: `0103ae7ec94c2cbe345a18f8adff4fca3d4bc919604cea1af34c000996e5cf70`

Replay verification from the repository root passed:

- `rtk proxy python3 -m unittest discover -s scripts/tests/orchestration` (6 tests)
- `rtk proxy python3 skills/default/delegate-to-subagents/scripts/test_scheduler.py` (17 tests)
- `rtk proxy python3 scripts/validate-skill-sources.py skills`
- `rtk git diff --check`

These deterministic tests exercise the helper and grader, not the native host's dispatch or timer wiring. N1 still needs live evidence for both Codex and Copilot caller pairings, including early completion with one remaining alarm, no idle lookup/duplicate dispatch, real-time expiry, and worker plus write shutdown before transfer. The historical trace is not a substitute for a host event at expiry.
