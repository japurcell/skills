# Delegation scheduler

`scripts/scheduler.py` is a portable Python 3 standard-library CLI for host-owned assignment deadlines. Pass a session-specific `--state PATH` to persist JSON state. New state uses version 3; the CLI reads version 2 assignments and preserves their configured progress intervals. Successful mutations upgrade version 2 state. Read-only `list` and timer checks with no event leave the file unchanged. Version 2 or 3 is required; other formats are rejected. Each mutation takes an adjacent lock and replaces state atomically. Corrupt or unsupported state produces a diagnostic and is left untouched. Version 2 binaries do not understand version 3 state, so use the same or newer CLI after an upgrade.

```sh
python3 scripts/scheduler.py --help
python3 scripts/scheduler.py register --help
task_now=$(date +%s)
python3 scripts/scheduler.py --state work.json register task-1 agent-1 "implement parser" --deadline "$((task_now + 600))" --grace 120 --route coding
python3 scripts/scheduler.py --state work.json tick
python3 scripts/scheduler.py --state work.json wait --max-wait 60
```

Ordinary registrations are deadline-only. Add `--checkpoint SECONDS` only when this assignment needs periodic progress reminders; existing version 2 intervals continue to run.

Register the actual worker configuration with `--model MODEL --profile PROFILE` and an optional explicit `--effort LEVEL`. Before dispatch, pass the same flags to `reusable` and use repeatable `--exclude AGENT` to omit contributors to an independent review. The JSON `agents` array contains candidates whose recorded assignments all completed normally with that configuration. Registrations with unknown configuration remain usable for deadlines. The host verifies that a candidate is available and its context is appropriate.

After a deadline action, record timely status with `checkpoint task-1 --eta TIMESTAMP`. Within the decision grace period, `extend task-1 --eta TIMESTAMP` grants the one extension, or `complete task-1` closes the assignment. Prefix each command with `python3 scripts/scheduler.py --state work.json`. Use a future Unix timestamp in seconds for `TIMESTAMP`.

Register requires a future Unix timestamp deadline. `--checkpoint`, when supplied, must be positive; checkpoint grace is optional (default 60 seconds). Without `--checkpoint`, no progress reminder is scheduled. At the initial deadline, `tick` emits a status request and starts a grace timer. A timely `checkpoint` starts a second grace timer for the host decision: complete, stop, or grant one ETA extension. A missed status or decision deadline, or an expired extension, emits a stop request. A late checkpoint or extension is rejected. Explicit legacy intervals reset when checkpointed. Completed and cancelled assignments stop generating timer events. Successful operations return JSON on stdout; help writes text. Invalid arguments, transitions, and malformed files return exit 2 with a diagnostic on stderr; interruption returns 130 and a closed stdout returns 1. Commands never read stdin. State changes can already be persisted when output fails, so inspect `list` before retrying a mutation.

The `wait` command targets at most `--max-wait` and returns the earliest deadline, grace expiry, or explicit progress reminder. It checks for concurrent state changes at most every 0.1 seconds without holding the lock while asleep. Timer checks with no event do not rewrite state. An action in JSON is a host instruction, never proof it occurred. The host performs communication and worker control. For ownership transfer after a stop, run `confirm-stopped ID --confirmation worker-and-writes-stopped` only after verifying the worker and its writes have stopped; `transfer ID` then emits a host action without performing transfer.

## Maintenance checks

Run focused deterministic public-CLI tests with `python3 scripts/test_scheduler.py`. They use temporary state files and synthetic time; no provider or model evaluation is involved.

Locking uses `flock` on POSIX and `msvcrt.locking` on Windows. Windows locking is implemented but has not been verified on Windows; use a local filesystem with working advisory locks and atomic replacement. The CLI does not provide a daemon or enforce host actions.
