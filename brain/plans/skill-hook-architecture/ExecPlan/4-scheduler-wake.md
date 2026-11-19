# M4. Scheduler wake and native completion

Status: open
Acceptance: not met

## Assignment

T4 belongs to the milestone implementer. Work from the repository root on a branch based on the committed plan. The committed plan is the only prerequisite. Reproduce any defect through the caller before editing. Stop when the behavior below is delivered, checks are recorded and any native evidence gap is named.

## Source and interfaces

- `skills/default/delegate-to-subagents/scripts/scheduler.py`
- `skills/default/execplan-implement/SKILL.md`
- `scripts/tests/orchestration/native-lifecycle.md`

## Scheduling decision

Expose a read-only query over the delegate scheduler’s locked snapshot. Return the assignment ID, native worker ID, absolute due time and timer reason, or an explicit empty result. Apply the same per-assignment phase and reminder rules as tick, including precedence when a phase is already overdue. Across assignments, select earliest due time, then expiry before reminder, then assignment ID. A due timestamp in the past means attend immediately. Querying never advances a phase or changes persisted assignment data. Tick continues to advance every due assignment once per call.

## Host delivery

Use a host wait that wakes on any eligible completion and cap it at the chosen due time. A one-shot host timer paired with a notification yield also qualifies. Refresh after completion, a registry mutation, a deadline or an interruption. Drain delivered completions before expiring assignments. A host that only waits on one worker and lacks independent notifications may consume other completions late. Describe that latency explicitly and use only verified capabilities in its instructions. The registry owner re-arms when it changes a deadline. Do not assume an external state-file write wakes a native wait.

## ExecPlan compatibility

Keep ExecPlan’s standalone pre-launch registry. It reserves the assignment and absolute deadline before dispatch, attaches the actual worker handle on return and can re-anchor once at launch. Apply the same selection ordering to that registry. ExecPlan does not require the optional delegate scheduler executable or registration of a made-up worker. A reserved assignment still has a live timer while the host obtains a worker handle. No second persisted registry or state-format migration is required.

## Acceptance

Test tied timers, overdue phases, version-2 state without mutation, no active worker, concurrent completion, and all due events on tick. Exercise delayed dispatch in the standalone ExecPlan fixture. In the native two-worker trial, invert the existing positive control: SILENT owns the earlier deadline and QUICK finishes first. Record when the parent consumes QUICK and how the SILENT deadline is enforced. Repeat for each host path that claims prompt delivery. Until demonstrated, that claim stays unverified.

## Verification

Run from the checkout root. Each command must exit zero. Inspect the files or output specified above.

- `rtk proxy python3 skills/default/delegate-to-subagents/scripts/test_scheduler.py`
- `rtk proxy python3 scripts/tests/orchestration/test_w1.py`

Follow `scripts/tests/orchestration/native-lifecycle.md` with the inverted deadline order in an isolated authenticated host profile. Record the host version, both deadlines and actual parent consumption times.

## Progress

- [ ] [milestone-4] Implement T4 and exercise the public entry points.
- [ ] [milestone-4] Verify integrated behavior and record platform evidence.
