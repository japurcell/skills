# Delegation scheduler

`scripts/scheduler.py` is a portable Python 3 standard-library CLI for host-owned assignment reminders. Pass a session-specific `--state PATH` to persist JSON state. Version 3 rejects unsupported state files without migration. Each mutation takes an adjacent lock and replaces state atomically. Corrupt or unsupported state produces a diagnostic and is left untouched.

```sh
python3 scripts/scheduler.py --help
python3 scripts/scheduler.py register --help
task_now=$(date +%s)
python3 scripts/scheduler.py --state work.json register task-1 agent-1 "implement parser" --deadline "$((task_now + 600))" --checkpoint 300 --grace 120 --route coding
python3 scripts/scheduler.py --state work.json tick
python3 scripts/scheduler.py --state work.json wait --max-wait 60
```

After a deadline action, record timely status with `checkpoint task-1 --eta TIMESTAMP`. Within the decision grace period, `extend task-1 --eta TIMESTAMP` grants the one extension, or `complete task-1` closes the assignment. Prefix each command with `python3 scripts/scheduler.py --state work.json`. Use a future Unix timestamp in seconds for `TIMESTAMP`.

Register requires a future Unix timestamp deadline, positive progress interval, and optional checkpoint grace (default 60 seconds). At the initial deadline, `tick` emits a status request and starts a grace timer. A timely `checkpoint` starts a second grace timer for the host decision: complete, stop, or grant one ETA extension. A missed status or decision deadline, or an expired extension, emits a stop request. A late checkpoint or extension is rejected. Checkpoints reset reminder timing. Completed and cancelled assignments stop generating reminders. Successful operations return JSON on stdout; help writes text. Invalid arguments, transitions, and malformed files return exit 2 with a diagnostic on stderr; interruption returns 130 and a closed stdout returns 1. Commands never read stdin. State changes can already be persisted when output fails, so inspect `list` before retrying a mutation.

The `wait` command targets at most `--max-wait` and wakes for the earliest deadline, grace expiry, or progress reminder. It persists and returns due events itself, checking for concurrent changes while waiting. Each wait polls at most every 0.1 seconds; lock acquisition and operating-system scheduling can add latency. An action in JSON is a host instruction, never proof it occurred. The host performs communication and worker control.

## Ownership transfer and recovery

After verifying worker and write shutdown, run `confirm-stopped ID --confirmation worker-and-writes-stopped`, then `transfer ID`. This records `transfer_authorized: true` and `transfer_completed: false`. The parent must actually update its own ownership record before acknowledging it:

```sh
python3 scripts/scheduler.py --state work.json confirm-transfer task-1 --owner agent-2 --evidence parent-record:task-1 --confirmation parent-ownership-updated
python3 scripts/scheduler.py --state work.json list
```

Owner and evidence must be nonblank. Evidence is an opaque pointer to the actual parent record: the CLI neither reads the referenced file nor independently verifies ownership. Acknowledgment requires confirmed shutdown and prior authorization. It stores `transfer_completed: true` and `transfer_receipt` with `owner`, `evidence`, and finite `recorded_at` timestamp. The receipt is absent before completion. The parent reads back both its updated owner and the scheduler receipt before reporting reassignment complete or dispatching overlapping replacement work.

Matching owner/evidence retries return the original receipt with its original timestamp and leave state unchanged. Conflicting retries fail with exit 2 and no mutation. After a failed stdout write, inspect `list` and the parent record before retrying. A crash after the parent update requires acknowledging that existing update; a crash before it leaves authorization pending. Continue independent work while shutdown or transfer is blocked.

Transfer commands preserve assignment status. Cancel the superseded active assignment if needed, then use normal routing and fresh registration for a replacement. Cancellation without replacement remains valid; verified task completion uses `complete`.

Preserve original version 2 files and use distinct state paths. Finish with the matching version 2 CLI, or reconcile real assignments and create a fresh version 3 session. Historical `transferred: true` records authorization only and cannot manufacture a completion receipt. Reconcile pending ownership changes against the actual parent record first.

## Maintenance checks

Run focused deterministic public-CLI tests with `python3 scripts/test_scheduler.py`. They use temporary state files and synthetic time; no provider or model evaluation is involved.

Locking uses `flock` on POSIX and `msvcrt.locking` on Windows. Windows locking is implemented but has not been verified on Windows; use a local filesystem with working advisory locks and atomic replacement. The CLI does not provide a daemon or enforce host actions.
