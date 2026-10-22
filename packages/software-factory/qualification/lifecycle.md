# T6 bounded lifecycle evidence

Local command-only proof: 2026-10-22, Node 24.22.1 darwin-arm64, TypeScript 7.0.2,
Git 2.54.0, qualified local APFS storage. Native foundation CI evidence is separate
from product process-control qualification. No real agent adapter was launched.

## Public controller and native scope

All stop causes use the invocation controller: saved needs-input, independent
failure, recorder failure, timeout, SIGINT/SIGTERM and `context.cancel(reason)`.
An immediate local admission barrier and durable shutting-down transition precede
new dispatch. The question capture finishes before its normal peer-interruption
request. Admission already committed before the barrier either joins live cleanup
or settles confirmed non-launch; capacity waiters consume no attempt or allowance.
Received results and independent failures retain precedence over questions;
shutdown-requested interruption alone does not invent a failed peer.

`invoke` accepts `--command-timeout-ms`, `--agent-timeout-ms`, and
`--shutdown-grace-ms`. Defaults are 1800000, 3600000 and 30000 respectively.
CommandOptions may set `timeoutMs`; execution time starts after admission, excluding
capacity waits. Positive integer execution bounds are at most 86400000 ms; grace
is at most 300000 ms. Effective defaults/configuration are saved with inputs.
Agent timeouts are a validated integration setting for future adapters, not a
claim of an implemented agent timer. `required:false` advisory results remain
supported; infrastructure/recording/cleanup failures remain terminal.

Each active command keeps its live ChildProcess reference. POSIX control covers
only members remaining in its dedicated group: SIGTERM, bounded grace, SIGKILL,
then a bounded 500 ms observation period. Signal submission never proves exit.
Inherited output pipes are bounded and closed explicitly when unsupported activity
keeps them open; those captures are partial and cleanup stays unknown. Pending
workflow scopes have a grace-plus-1000 ms drain bound. Late calls cannot write a
closed store. The CLI flushes its JSON response then exits its own foreground host,
so an unresolved authored timer cannot keep the stopped invocation alive.

`childScope:'process-group'|'unknown'` records requested scope; POSIX defaults to
its owned group and Windows remains unknown. Declaring a group does not establish
universal descendant absence. Explicit escaping/remote modes, inherited open
pipes, native inspection errors and lost ownership remain uncertain. No stdout
text is interpreted as child control evidence. There is no Job Object launcher,
universal process scanner or process recovery service. Restart tooling never
signals a stored PID. Candidate files and unresolved capacity/claims are retained.

Windows only supports conservative direct-child termination here; Node signal
names are abrupt termination rather than a graceful protocol. Descendant cleanup
stays unknown. The startup compiler is itself a managed command, so this
conservatism can prevent workflow entry even for an empty workflow. A future exact
pinned compiler-mode qualification could establish a narrower supported contract;
an arbitrary caller scope declaration cannot supply that proof. Native Windows
and Linux product cleanup acceptance remain pending.

## Owner inspection and exact clearance

`inspect-owner (--repository PATH | --common-dir PATH) [--claim ID] --json` shows exact claims, owner and
occupied scopes, and native inspection limits. Linux uses boot ID plus process
start ticks; macOS uses boot time plus available process-start metadata. macOS
start metadata has second resolution; equal metadata is conservatively treated as
live, so a rare collision can refuse clearance. Missing/unrecognized/inaccessible
metadata stays unknown. Local PID absence or differing valid boot/start identity
establishes only that saved owner is absent, not that hidden descendants stopped.
A positively identified live owner or direct scope refuses manual clearance.

`clear-owner (--repository PATH | --common-dir PATH) --claim ID --token TOKEN --operator-confirmed
--note NOTE --json` requires every explicit flag and a nonempty note. Native
inspection is computed by the controller, not supplied by the caller. One store
transaction saves the filtered note, operator basis and inspection limitations,
reconciles unresolved occupancy, and removes only the exact matching claim/token.
It never refunds an uncertain launch or rewrites prior execution outcomes.
Final summary and automatic exact-claim release also commit atomically; failed
save/release preserves blocked ownership rather than publishing successful cleanup.

## Observed verification

With qualified Node first on PATH, in `packages/software-factory`:

- `npm run typecheck`: source and qualification checks passed.
- `node scripts/build.mjs`: runtime and public declaration build passed.
- `node --test test/shutdown.test.mjs test/startup.test.mjs test/store.test.mjs test/capture.test.mjs test/recording-integration.test.mjs test/fixtures.test.mjs test/placement.test.mjs`: 78 passed, none failed/skipped.

Seventeen shutdown tests exercise real interruption, ignored SIGTERM escalation,
130/143 signal exits, preserved files, capacity cancellation, actual recorder byte
failure, late scopes, escaped inherited pipes, PID identity mismatch/unavailability,
known-live refusal, stale-token replacement protection, failed spawn-identity/summary/release
transactions, forced owner death, manual cause and exact operator cleanup.
The first needs-input reproduction waited for a three-second peer; it now stops
that peer promptly. Fault fixtures use SQLite rejection triggers and real process
boundaries, not substituted success results.

The combined proof charges an additional attempt using actual fake-harness
processes, retains an unknown scope, records explicit operator clearance, then
runs current edited workflow code with current inputs. The fresh invocation keeps
that additional allowance and preserved candidate files; no automatic restart or
executable resume occurs. One T5 fixture was reconciled with immediate shutdown:
it now receives the independent required failure before requesting the question,
retaining all original failed-summary/question/attempt assertions. The separate
T6 test proves an as-yet-unfailed peer interrupted by a question stays interruption.

Source constraints: [Node 24.22.1 process API](https://nodejs.org/docs/latest-v24.x/api/process.html),
[Node child process API](https://nodejs.org/docs/latest-v24.x/api/child_process.html),
and the repository's lifecycle platform findings. The process page was fetched;
the child-process web endpoint was unavailable during this run, so the retained
source study plus real local process proofs support that bounded integration.
No cross-platform release or real harness child-control support is inferred.

Reflection: controller/finalization boundaries and failure preconditions are
encoded in public tests. Remaining native/adaptor limitations belong to the
active plan and this evidence; no separate brain note was needed.

## Independent review repairs

Three public reproductions failed against the immutable first T6 candidate before
repair: a harmless configured API-key fixture value escaped the returned missing-
executable diagnostic; a three-second checkout smudge filter blocked SIGTERM; and
a workflow awaiting only an unresolved promise exited 0 with no final record.
All three unchanged temporary reproductions then passed against the repair and
now have maintained CLI tests.

Runtime diagnostics, recorder configuration and operator notes share the canonical
bounded filter and environment policy. Filtering applies to free-text diagnostic
boundaries, including pre-admission failures, rather than rewriting operational
claim/token JSON. Claim tokens remain usable and operator notes remain filtered.

Startup Git is asynchronous and uses live references with bounded process control.
Read-only identity/ref probes run before a repository can be identified/admitted;
if they cannot finish, report startup/cleanup uncertainty without creating a new
store. After reservation and exact worktree claim, checkout and Git registration
queries use recorded `startup/git/...` command attempts through the same runner.
Checkout filters remain within the declared group-only control limit; escaped or
unproved child activity cannot be claimed universally absent. Setup commands use
the recorded command deadline, and no automatic retry or dirty-source snapshot is
introduced. Small raw metadata reads have a 1 MiB semantic-output bound; persisted
output still uses the canonical recorder. Interrupted checkout creates no compiler,
agent or workflow phase, and retains whatever partial files Git leaves behind.

A ref'ed foreground liveness guard holds the invocation while authored code awaits
an unresolved promise. Explicit signals still route through shared shutdown. This
is not an overall workflow timeout. The guard is removed after the invocation ends.

For actionable recovery without Git, `--common-dir` opens only an existing store
through the normal canonical path, local placement, schema and repository checks.
It never bootstraps or substitutes history. Exact claim/token and inspection plus
operator confirmation are still required. Tests remove Git from PATH, verify both
owner commands work and notes are filtered, and reject wrong/incompatible/corrupt
storage without creating/replacing a database. This is the manual fallback when
Windows cannot qualify metadata Git descendant cleanup. Windows workflow entry
remains unqualified and can be blocked by metadata probes as well as the compiler;
no arbitrary caller declaration supplies the missing native proof.

The repair adds seven maintained public cases. Both pinned typechecks/declaration
build and the full 85-check combination pass. Existing startup assertions now
separate recorded setup commands from the same workflow operations: exactly one
build remains required, and startup/build failures still launch no agent or
workflow phase. No prior required/advisory outcome assertion was removed.
