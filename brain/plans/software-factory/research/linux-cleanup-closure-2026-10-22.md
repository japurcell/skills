# Targeted Linux cleanup closure

This scoped ExecPlan covers `scripts/verify-security-fixture-patch.py`,
`scripts/test-verify-security-fixture-patch.py`, and this note. The parent owns
the factory plan, CI, and canonical documentation. Keep Progress, discoveries,
decisions, and outcomes current under `.agents/skills/exec-plans/SKILL.md`.

## Purpose / Big Picture

On SIGINT, a real scanner whose children change sessions must return the public
`--check --json` result `interrupted`/130 within the existing two-second
absolute cleanup deadline, with no observed descendant or metadata helper left
running. Denial, incomplete native observations, and missed deadlines must
fail closed. Ordinary process observation retains its one-second limit; the
finalization reserve remains 50 ms and the known-process cap remains 256.

## Progress

- [x] (2026-10-22) [milestone-1] Read hosted Linux failure log, current source,
  fixture, relevant brain, and Linux native API documentation.
- [x] (2026-10-22) [milestone-1] Record both red public E2E failures from the
  actual hosted Linux 44-case run before changing production code.
- [x] (2026-10-22) [milestone-2] Make the Linux direct-child query bounded, identity-checked,
  and thread-complete through the existing native helper.
- [x] (2026-10-22) [milestone-2] Route three-generation fixture release through actual Linux
  native discovery while retaining all three post-SIGINT assertions.
- [x] (2026-10-22) [milestone-3] Run both public Linux simulations, focused
  protocol/failure cases, and all 47 native Mac cases; record native limits.
- [x] (2026-10-22) [milestone-3] Inspect the three-file diff, confirm only
  owned paths changed, and prepare one clean scoped commit.

## Surprises & Discoveries

- Hosted Linux run `39797767406`, 44 tests in 108.432 seconds, failed two cases.
  The delayed case returned `process_observation_timeout`/2 with `limit: 0.915`
  and `measured: 0.915` during cleanup. The generation case did not create its
  second child because its release injection intercepts only Mac libproc.
- Linux kernel documentation says `/proc/<pid>/task/<tid>/children` lists direct
  children of a particular thread. Every thread must be covered. The interface
  is imprecise while children exit; it is intended for stopped or frozen trees.
- The simulated Linux ESRCH public case initially returned 2 because the
  child-request validator still applied Mac's microsecond bound to Linux
  start ticks. Raising that field's bound to the existing 63-bit tick range
  restored 130; denial, I/O error, and empty record remained safe 2 results.
- The existing three-generation fixture intercepted Mac `proc_listchildpids`
  only. Linux now releases each successor after a real per-thread procfs
  `children` read, retaining the 0.2-second wait and requiring second and third
  PID markers created after SIGINT.
- The two hosted-shaped public cases with both verifier and helper forced to
  Linux passed on Mac: delayed 0.3/0.55/0.12 cleanup returned 130 in 0.121393
  seconds; cascade returned 130 in 0.335837 seconds with all three generations
  stopped. These are simulated procfs results, not native Linux qualification.
- Full native Mac suite passed 47 tests in 113.995 seconds. The original 44
  remain active. Targeted Linux helper protocol checks include a child born
  from a nonleader thread, parent birth drift/disappearance, changing thread
  lists, an unfrozen thread, denial, missing children, and saturation.

## Decision Log

- Decision: Use the existing bounded native helper for Linux `children` queries
  of newly birth-verified, stopped known parents; cover every thread, validate
  child PPID and identity, then freeze and acknowledge discoveries before the
  next generation. Fail closed on malformed, missing, denied, saturated, or
  timed-out results. Do not add a global tracker or signal saved PIDs.
  Rationale: This removes serial global `/bin/ps` cleanup scans while keeping
  the existing ownership and deadline checks. Date/author: 2026-10-22, Codex.
- Decision: Require every enumerated thread to report stopped state before
  reading any child list, require the same thread set and stopped state after,
  and revalidate the parent's native birth token before and after the query.
  Treat disappearance, denial, drift, more than 256 threads or children, and
  malformed records as incomplete. Rationale: a leader's stopped state alone
  does not prove every thread is frozen; an incomplete procfs read must not
  authorize a 130 success. Date/author: 2026-10-22, Codex.

## Outcomes & Retrospective

Implementation and local checks are complete. The three owned files are
prepared for one scoped commit; Git records the resulting commit. The parent
owns independent review and fresh hosted Linux qualification; a Mac
simulation cannot establish native Linux correctness. An exiting child can make procfs omit a different, still-live child, even
when all parent threads are stopped. Unknown children cannot be frozen before
discovery, so this method establishes closure of known/discovered processes,
not a universal whole-tree proof. Never-observed descendants, including a live
sibling omitted during another child's exit or an escaped/re-parented child,
remain outside that bounded claim. This Linux-specific caveat is stronger
than merely saying the omitted child itself exited.

## Context and Orientation

`scripts/verify-security-fixture-patch.py` runs real scanners, uses `/bin/ps`
for ordinary process-graph observation, and uses a separate native IPC helper
for PID birth, parent, group, and state. On cancellation, `stop_process` freezes
known processes, rediscovers descendants, kills only identity-verified members,
and confirms exit. Both Mac and Linux cleanup now use targeted native child
queries; ordinary observation still uses global `ps`. The public tests in
`scripts/test-verify-security-fixture-patch.py` create real scanner trees and
inspect exit status, elapsed time, surviving processes, and safe JSON.

## Plan of Work

### Milestone 1: Establish red public evidence
Status: done
Acceptance: met

Task T1 had no prerequisite. Actual hosted Linux run `39797767406` supplies
public E2E red: the delayed case exited 2 with a cleanup observation allowance
and measurement both 0.915 seconds; the generation case lacked its second
marker. These failures were recorded before the production edit. The original
0.3/0.55/0.12 requested delays and three post-SIGINT generations remain.

### Milestone 2: Implement bounded Linux closure
Status: done
Acceptance: met

Task T2 required T1. `process_query_helper` enumerates each thread of an
identity-verified stopped Linux parent and each thread's direct children,
within per-read byte, 256-thread/child, IPC, and parent deadline bounds. It
verifies all thread stop states before and after, stable thread membership,
child PPID, and parent birth before and after returning numeric IPC records.
`stop_process` uses the existing targeted `query_children` and
`remember_native_children` for Linux too, retaining freeze, identity, kill,
and exit proof. The fixture releases each next generation after an actual
Linux child-query read. Public simulated Linux cases return 130 and stop all
observed processes; original assertions and delays remain.

### Milestone 3: Integrated native proof and handoff
Status: done
Acceptance: met

Task T3 required T2. All 47 public cases passed on native Mac in 113.995
seconds. Focused Linux simulations and protocol cases passed, Python AST
parsing passed, and `git diff --check` passed. The scoped diff contains only
the two scripts and this note. One clean commit is prepared on
`codex/factory-linux-closure`. Mac native proof remains separate from the
parent's hosted Linux qualification gate.

## Concrete Steps

The prepared three-file commit is made from
`/Users/adam/.codex/worktrees/factory-linux-closure/skills`. Next, the parent
performs independent review and one fresh hosted Linux qualification. On a
hosted failure, retain the log and classify the exact case and phase before
any further code change.

## Validation and Acceptance

The two original public cases are
`test_cancellation_closes_two_delayed_snapshots_with_host_scheduling_cost`
and `test_cancellation_discovers_descendants_created_during_successive_scans`.
The first must return 130 within two seconds and stop all owned descendants;
the second must create all three true generations after SIGINT, then stop them
and every observer. Failures may safely return 2, but cannot report 130 while a
known descendant remains alive. Their simulated Linux variants passed with
the verifier and helper both forced to Linux. The Linux helper protocol
rejected denial, disappearing child, parent birth drift, incomplete thread
scan, live thread, and saturation. Final native Mac run: 47 tests,
113.995 seconds, exit 0. Native Linux acceptance still needs the parent's
fresh hosted action after independent review.

## Idempotence and Recovery

Tests use disposable directories. On a failed process fixture, inspect its
identity-guarded emergency cleanup and confirm no survivor before retrying.
Do not signal a persisted PID after restart. If procfs children are unavailable
or incomplete, preserve an incomplete result and report it to the parent.

## Reflection

The reusable lesson is encoded in the fixture and this scoped note: Linux
child discovery is per thread, and a simulated native platform must agree in
both verifier and helper. A leader's `T` state alone is insufficient as a
proof that every thread is frozen. No shared brain or skill file changed;
those files are outside this scoped branch's ownership.

## Sources

- [Linux kernel procfs documentation](https://www.kernel.org/doc/html/v6.14/filesystems/proc.html)
- [Linux proc_tid_children manual](https://man7.org/linux/man-pages/man5/proc_tid_children.5.html)
- [Linux proc_pid_task manual](https://man7.org/linux/man-pages/man5/proc_tid.5.html)

## Independent review and normal-path assertion

Independent complete review passes all47 cases in113.019 seconds and finds no blocking production-code issue, while identifying the new simulated-Linux cascade assertion as too permissive: it accepted safe refusal2 as well as normal interruption130. The simulated Linux normal-path case now requires exactly130; the existing Mac assertion and separate safe-refusal fixtures remain unchanged. Parent runs the focused strengthened public case before integration and all47 composed cases afterward. Native Linux remains pending Actions.
