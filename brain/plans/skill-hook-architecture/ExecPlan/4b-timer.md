# T4b, timer selection

Independently, the scheduler maintainer adds `next-wake` to the existing CLI, reading the locked snapshot and calling `next_timer(assignment, now)`. Return one JSON object with a `wake` field holding null or an object with `assignment`, `agent`, `due` and `reason`. Keep persisted version-2 state and existing mutating commands compatible. Document the same ordering on the standalone ExecPlan registry, including reservations without attached handles. Stop when scheduler CLI and delayed-launch fixtures pass.

The scheduler implementer owns scheduler.py, scheduler CLI tests and standalone registry ordering and fixture. Verify empty, tied and overdue timers, version-2 state byte stability, all due events and unattached reserved handles. Run the two test commands in the milestone. Stop before changing host delivery behavior.

Use the [milestone contract and verification commands](4-scheduler-wake.md) and the [integration plan](../ExecPlan.md). Record results and remaining evidence here.
