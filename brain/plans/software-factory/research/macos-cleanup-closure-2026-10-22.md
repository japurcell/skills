# Targeted macOS cleanup closure

This scoped execution plan covers only `scripts/verify-security-fixture-patch.py`,
`scripts/test-verify-security-fixture-patch.py`, and this note. It follows
`.agents/skills/exec-plans/SKILL.md`. The parent owns the factory plan, CI,
and canonical documentation.

## Purpose / Big Picture

Cancellation of a real scanner must stop every observed descendant and
metadata observer within the existing two-second absolute cleanup deadline,
including a child that moves to a separate session. Success is observable as
the public `--check --json` CLI returning `interrupted`/130 with no surviving
owned process. An incomplete or denied query must return a safe failure, not
claim successful cancellation. Ordinary process observations retain their
one-second cap. The owned-process finalization reserve remains 50 ms.

## Progress

- [x] (2026-10-22) [milestone-1] Inspect the actual hosted Mac and Linux
  failures, current verifier, fixture, and official native API contracts.
- [x] (2026-10-22) [milestone-1] Run the unchanged original public Mac CLI
  cancellation case locally and retain its timing.
- [x] (2026-10-22) [milestone-1] Obtain parent approval of the bounded
  Mac-only closure design before changing production behavior.
- [x] (2026-10-22) [milestone-2] Correct the Linux ESRCH public fixture
  acknowledgment race without removing its fault-exercised assertion.
- [x] (2026-10-22) [milestone-2] Add the public Mac CLI scheduling case,
  observe red against original source, implement targeted closure, then
  observe green with the resistant child and observers stopped.
- [x] (2026-10-22) [milestone-3] Run focused public cases and all 42 existing
  cases plus two new cases on the native host: 44 passed in 111.536 seconds.
- [x] (2026-10-22) [milestone-3] Prepare the three owned files for a clean
  commit and parent handoff; independent review and hosted qualification are
  parent-owned follow-up gates.

## Surprises & Discoveries

- Hosted Mac full run `39788049247` failed the original 0.3-second capture plus
  0.55-second return-delay case. The first delayed observer took 1.084 seconds;
  the second had allowance 0.835 seconds and timed out at 0.836. Its 42-case
  run took 219.925 seconds. The same public case passed locally in 1.861065
  seconds with 28 recorded processes stopped, leaving little schedule slack.
- Hosted Linux `39788049229` returned `interrupted`/130 in its ESRCH case but
  failed the retained assertion that the injected descriptor read happened.
  The fixture's `sampled` marker is written before that observer delivers its
  output; `reaped` can become visible before the verifier consumes the
  snapshot. This is a fixture synchronization hypothesis to prove by a
  controlled public probe, not a reason to remove the assertion.
- The new public CLI case keeps the original requested 0.3/0.55-second
  delays and adds 0.12 seconds of bounded return scheduling cost. Against the
  unchanged verifier, it failed as intended: exit 2,
  `process_observation_timeout`, second cleanup scan allowance 0.863 seconds,
  measured 0.865. The first cleanup observer delivered at 1.072608 seconds.
  This is a deterministic local E2E reproduction of the hosted two-scan
  failure shape.
- After Mac direct-child closure, the new case returned 130 in 0.041626
  seconds with the resistant separate-session child and all three recorded
  observers stopped. The unchanged original 0.3/0.55 case returned 130 in
  0.035347 seconds in the final full run.
- The original three-generation fixture released later children only during
  successive cleanup `/bin/ps` scans. Its release markers now attach to real
  `proc_listchildpids` calls. Cancellation starts with generation 1 only;
  generations 2 and 3 are born after SIGINT at successive targeted queries.
  All three true PID markers and exit checks remain. Its 0.2-second observer
  settlement remains.
- The simulated Linux fixture's parent verifier initially sent the new Mac
  child protocol to its Linux-emulating helper. Setting `sys.platform` to
  Linux in both test processes restores a coherent Linux public scenario.
  ESRCH, denial, I/O error, and empty-read modes pass with injected-read and
  process-stop assertions intact.
- Final native Mac run: 44 cases passed in 111.536 seconds. A prior integrated
  run failed only the simulated Linux protocol mismatch, which was corrected.
- Apple SDK `libproc.h` declares `proc_listchildpids`. Apple XNU implements it
  with `PROC_PPID_ONLY`; its return value counts PIDs copied, and a full
  supplied buffer can mean truncation. The Linux `proc_tid_children(5)` manual
  warns that concurrent child exits may cause omission of other living children
  unless all children are stopped or frozen. Therefore the proposed first
  production slice is Mac-only.

## Decision Log

- Approved by parent 2026-10-22: During Mac cleanup, query direct children only for
  stopped, birth-identity-verified known ancestors using the existing bounded
  native helper. Use a 257-slot result for the existing 256-process limit and
  fail closed at saturation, denial, invalid records, drift, or timeout. Freeze
  and acknowledge newly found children, repeat until no new child exists,
  revalidate all birth identities and current groups, then kill and prove exit.
  Keep ordinary global `/bin/ps` observation and the Linux cleanup graph.
  No native error may fall back to a weaker cleanup path.

## Outcomes & Retrospective

The Mac-only targeted child query is implemented, and the local public suite
passes all 44 cases. The original 42 assertions and delays remain, with two
new cases for hosted-shape scheduling and direct-child protocol boundaries.
Independent review and fresh hosted Mac/Linux qualification remain owned by
the parent. This local result does not establish hosted qualification.

## Context and Orientation

`scripts/verify-security-fixture-patch.py` runs real scanners, observes their
process tree with `/bin/ps`, and queries native PID birth/parent/group/state
through a bounded helper. `stop_process` first stops known descendants,
rediscovers children, revalidates identities, kills, and confirms exit.
`scripts/test-verify-security-fixture-patch.py` exercises the public CLI with
real scanner and observer processes. The known host issue is two sequential
delayed global metadata snapshots after SIGINT. A child that was never sampled
and detaches beyond a stopped known ancestor is outside the current boundary;
this plan does not expand ownership to arbitrary processes.

## Plan of Work

### Milestone 1: Establish a safe design
Status: done
Acceptance: met

Inspect the host evidence and official API. Confirm the proposed Mac-only
targeted query design with the parent before production edits. Task T1 has no
prerequisite. Its stopping boundary is design approval.

### Milestone 2: Repair and exercise public behavior
Status: done
Acceptance: met

Task T2 strengthened the Linux fixture so SIGINT waits for a subsequent
ordinary observer launch that proves the child-containing snapshot was
consumed. The fault-exercised and leak assertions pass. Task T3 added an
adversarial public Mac CLI case at the existing seam. It failed before the
source change at 0.863/0.865 seconds and passed afterward with exit 130 in
0.041626 seconds. `process_query_helper`, `ProcessInspector`, and
`stop_process` now use bounded numeric direct-child requests only on Mac
cleanup. They revalidate parent and child birth identity before signaling and
fail closed on denial, saturation, invalid data, drift, or timeout. Existing
limits, assertions, and injected delays remain.

### Milestone 3: Integrated native proof and handoff
Status: done
Acceptance: met

Task T4 required T2 and T3. Focused red/green and the full 44-case public
suite ran under real native Mac processes with narrow escalation and passed
in 111.536 seconds. The suite checks unchanged file fingerprints, safe JSON,
no secret/traceback, stopped descendants and observers, and two-second
cancellation. The three owned files are ready for one clean commit and parent
handoff. The parent owns independent review and hosted Mac/Linux qualification;
local green alone does not establish those gates.

## Validation and Acceptance

From `/Users/adam/.codex/worktrees/factory-cleanup-closure/skills`, use the
public seam `python3 scripts/test-verify-security-fixture-patch.py
PreflightTests.<case>` for focused native cases and
`python3 scripts/test-verify-security-fixture-patch.py` for integration. The
original Mac case returned 130 in 1.861065 seconds before this change, while
hosted Mac returned 2 with `process_observation_timeout`. The new hosted-shape
case failed before the production edit and passed after. The Linux fixture
showed its injected-read marker before accepting each result. Final native
Mac suite: 44 tests, 111.536 seconds, exit 0. Hosted results remain pending.

## Recovery

All fixtures use disposable directories. On test failure, retain logs and
identify any survivor before emergency fixture cleanup, then verify exit.
Never signal a persisted PID after restart or treat a submitted signal as exit
proof. If the new API is unavailable or returns incomplete information, keep
the verifier's fail-closed result and report that limitation to the parent.

## Reflection

The durable lesson is encoded in the public fixtures and this scoped note:
simulated native platforms must agree between verifier and helper, and a
fixture marker written before metadata delivery needs a later-launch
acknowledgment to prove consumption. No brain or skill file changed; the
parent owns those shared files outside this scoped branch.

## Sources

- Apple SDK `/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/include/libproc.h`
- [Apple XNU libproc wrapper](https://github.com/apple-oss-distributions/xnu/blob/main/libsyscall/wrappers/libproc/libproc.c)
- [Apple XNU process-list kernel implementation](https://github.com/apple-oss-distributions/xnu/blob/main/bsd/kern/proc_info.c)
- [Linux proc_tid_children manual](https://man7.org/linux/man-pages/man5/proc_tid_children.5.html)
