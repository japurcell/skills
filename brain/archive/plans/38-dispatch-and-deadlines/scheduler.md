# S1. Reproduce and fix helper deadlines

Owner: scheduler implementer. Input: the published helper at 7fc651a7 in skills/default/delegate-to-subagents/scripts and its existing public CLI tests. Prerequisites: reviewed ownership and migration choice in Decision Log. Use a disposable state file. Run register with --deadline 600 --checkpoint 300 --now 0, then tick --now 300. Record the observed status-only event. Test a new ordinary registration without a periodic interval and run tick at 300 and 600. The first result should be empty, the second a deadline_expired event. Demonstrate the failure before editing.

Change scheduler.py at argument parsing, registration, state validation, event calculation, wait timing and checkpoint transitions as needed. Preserve public opt-in progress intervals and existing v2 state semantics. Test two outstanding deadlines, completion of one before expiry, no status wake before the other deadline, last completion, grace, exactly one extension, stop and transfer gates. Respect active concurrent registrations and complete/cancel retries according to existing CLI semantics. Update its README and the delegate skill's runtime-enforcement instructions where the reproduction warrants it. Preserve separate pre-dispatch text until P1. Run `rtk proxy python3 skills/default/delegate-to-subagents/scripts/test_scheduler.py`. Stop after helper-facing checks and record evidence, tested revision and remaining host-owned checks.

## S1 results

Tested on branch `work/todo38-scheduler`, based on `be7ae87c052f09ddff0311efa4cfdefc48dece8b`.

- Before editing, the required CLI reproduction registered with `--deadline 600 --checkpoint 300 --now 0`; `tick --now 300` emitted `progress_reminder`, then `tick --now 600` emitted `deadline_expired`.
- New registrations omit periodic progress timing by default. `--checkpoint SECONDS` remains an explicit opt-in. New records use schema v3; the reader accepts v2 records with their old intervals and behavior. Read-only `list`, and `tick` or `wait` with no due event, do not rewrite a v2 file. A successful mutation upgrades it to v3; a v2 binary cannot read v3 files.
- Added CLI cases for no reminder before the deadline, early completion among two deadlines, completion of the last assignment, concurrent deadline waits, and a frozen v2 fixture covering interval reminders, extension expiry, and the stop/transfer gate. Existing grace and extension cases remain in the suite.
- `rtk proxy python3 skills/default/delegate-to-subagents/scripts/test_scheduler.py`: 17 tests passed. The suite includes bounded wait duration, concurrent registration detection within the existing 0.1-second poll, malformed state and numeric input, no early progress wake, deadline-only grace/extension, and v2/v3 transitions.
- `rtk proxy python3 scripts/validate-skill-sources.py skills` and `rtk git diff --check` passed.

Host delivery, completion notification re-arming, worker cancellation, and verification that worker writes have stopped are outside this helper-only task. They remain for the controlled/native tasks in the parent plan.
