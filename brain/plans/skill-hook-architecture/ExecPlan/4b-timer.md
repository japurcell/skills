# T4b, timer selection

Independently, the scheduler maintainer adds `next-wake` to the existing CLI, reading the locked snapshot and calling `next_timer(assignment, now)`. Return one JSON object with a `wake` field holding null or an object with `assignment`, `agent`, `due` and `reason`. Keep persisted version-2 state and existing mutating commands compatible. Document the same ordering on the standalone ExecPlan registry, including reservations without attached handles. Stop when scheduler CLI and delayed-launch fixtures pass.

The scheduler implementer owns scheduler.py, scheduler CLI tests and standalone registry ordering and fixture. Verify empty, tied and overdue timers, version-2 state byte stability, all due events and unattached reserved handles. Run the two test commands in the milestone. Stop before changing host delivery behavior.

Use the [milestone contract and verification commands](4-scheduler-wake.md) and the [integration plan](../ExecPlan.md). Record results and remaining evidence here.

## Result

On 2026-11-19, the CLI query used the locked snapshot and existing selector; its public tests passed (21 tests), including empty, tied, overdue, version-2 byte preservation and all-due tick cases. `python3 scripts/tests/orchestration/test_w1.py` passed 12 tests with frozen historical arms unchanged. The standalone caller guidance includes the selection order and a delayed-handle example. `python3 scripts/tests/orchestration/test_controlled.py` passed 10 tests, including a simulated delayed dispatch pinned to the current caller's rules: the reservation retains its absolute deadline before and after handle attachment. This simulation does not execute a native parent. No native model calls were made. T4c and host delivery proof remain open.

Reflection: the transient shell quoting error was corrected and tests rerun; no durable skill or brain change was identified.
