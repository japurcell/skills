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

## Integrated base proof

Independent review approved the repaired source at `449c9d69`; source/tests stayed
identical after rebase to `c794db5c`. Base fast-forwarded through `a27e3f2b`.
After registering shutdown coverage, both strict typechecks/build and all 93
registered checks passed: lifecycle 52, store/capture/placement 29, fixture/CLI 6,
runtime/CI 6. Lifecycle completed in 26.626 seconds with zero failures or skips.
The registered composed case records operator clearance, current edited entry
and new inputs, preserved files and retained additional allowance. Independent
review also verified prompt-only and live-interval SIGTERM exits, filtered secret
diagnostics, cancellable checkout and Git-free exact-token recovery. Native
Windows/Linux product qualification remains pending as documented above.


## Preserved preparation recovery

Local T6 preparation-recovery proof, 2026-10-22 UTC, from integrated base
`a58a1c392298acece1427638d28c6ac833eacd40`. Runtime is qualified Node 24.22.1
with SQLite 3.53.4, TypeScript 7.0.2, Node types 24.19.2, and Git 2.54.0
(Apple Git-157) on macOS arm64/local APFS. This is not Windows startup or
universal descendant-cleanup qualification.

The original public reproducer was inspected and rerun against unchanged source
in the new private worktree. A real smudge filter starts a detached child with
inherited stderr while completing checkout. The factory honestly returns failed,
cleanup unknown, preserves the Git-registered checkout and saves registration
`reserved`. After fresh fixture-child start/command verification, termination,
observed absence and exact public operator clearance, reuse by ID/path both
refused with exit 3. The new maintained success assertions reproduced those
failures before source changes.

The repair records minimal original preparation evidence during bounded failure
finalization under the still-current exact claim, only after a working recorder
barrier. It saves worktree-directory and regular `.git` marker device/inode
identity plus an opaque SHA-256 of at most 16 KiB marker bytes. The descriptor
uses no-follow/nonblocking open where available and fstat checks before reading;
the path/descriptor/root identities are rechecked. It never parses the marker,
`commondir`, or another Git format, and never starts post-stop metadata work.
The marker retains the original registration pointer as opaque evidence. No
original git-dir inode or atomic filesystem immutability is claimed. Local
filesystem identity must be available; native Windows evidence is still pending.

The optional preparation object in existing Worktree JSON retains the exact
original invocation/claim and identity. Schema version 3 and settled T7 session
interfaces are unchanged. An original anchor cannot be overwritten. Legacy
unanchored reserved rows, including old crash states where no anchor could commit,
remain refused with `reserved worktree lacks original preparation identity
evidence; explicit recovery required`. No migration or guessed salvage occurs.
Anchor-write failure follows that same honest missing-evidence path.

Explicit reuse locates the same worktree by ID or canonical path, acquires a fresh
exclusive claim, then obtains authoritative current root/common-dir/worktree
registration/git-dir identity through managed Git probes. Git remains the source
of registration semantics: an unchanged marker hash cannot authorize a foreign
current common directory. Recovery requires the original retained run, safe
original final cleanup or recorded clearance of its exact historical claim,
and no occupied activity for that worktree. A new run cannot discard previously
paid additional allowance. Ordinary registered-worktree checks stay in force.

`reconcileWorktreePreparation` checks the current exact token, current starting
invocation, reserved-only state, retained-run/clearance basis and fresh filesystem
identity in one transaction before changing registration. Stale or competing
reconciliation cannot overwrite a replacement claim or commit twice. Identity is
checked adjacent to reconciliation, before build and again before workflow entry.
A filesystem actor with independent write authority is not made immutable by a
claim; no universal atomic filesystem transaction is asserted.

The next invocation builds and enters current workflow code with current inputs.
It never repeats checkout, resets files, copies candidate content, kills a saved
PID or rewrites the old failed/unknown outcome/captures. Public success cases
preserve candidate/payload files, marker bytes, old attempt/capture facts and a
real paid fake-agent correction debit (`additionalUsed:1`). Before explicit
clearance, an inactive original owner remains blocked just like live ownership.

Thirteen maintained public/store cases cover both selectors, root/marker
replacement, marker/path symlinks, foreign current Git identity, missing legacy
evidence, original-run retention, failed anchor storage, stale/competing tokens,
transaction interruption and SIGTERM during claimed Git metadata. The real signal
case saves interruption, starts no compiler/workflow, keeps registration reserved
and permits a later explicit fresh recovery. A real SQLite rejection trigger
proves registration/event transaction rollback; removing that fixture trigger
permits a new invocation without replay or reset. Existing process-loss and
recording-failure cases retain their conservative ownership assertions unchanged.

Commands use the pinned Node bin first on PATH and `login:false`, from repository
root unless stated otherwise. The new worktree initially lacked dependencies;
explicit `rtk proxy npm --prefix packages/software-factory ci --ignore-scripts
--offline --cache /tmp/software-factory-npm-cache` installed seven locked packages,
with zero audit findings. No startup installation or global install occurred.

- `rtk proxy npm --prefix packages/software-factory run typecheck`: source and
  qualification consumer checks pass.
- `rtk proxy npm --prefix packages/software-factory run build`: fresh runtime and
  declaration build passes before proof.
- From `packages/software-factory`, `rtk proxy node --test test/adapters.test.mjs
  test/fixtures.test.mjs test/cli.test.mjs test/dispatch.test.mjs
  test/store.test.mjs test/capture.test.mjs test/recording-integration.test.mjs
  test/placement.test.mjs test/startup.test.mjs test/shutdown.test.mjs
  qualification/runtime.test.mjs qualification/ci.test.mjs`: 149/149 pass in
  50.173 seconds (136 registered baseline plus 13 recovery cases), with zero
  failures/skips/cancellations, against the final fresh build.
- `rtk git diff --check`: passes.

Separate scratch evidence preserves the original scenario with only its target
build location adjusted: `/tmp/factory-preparation-recovery-repro.mjs`, results
`/tmp/factory-preparation-recovery-repro-results.json`, full histories under
`/private/tmp/factory-startup-e2e-hfKM1z/`. The same public scenario with success
assertions passes on fresh anchored evidence:
`/tmp/factory-preparation-recovery-green.mjs`, results
`/tmp/factory-preparation-recovery-green-results.json`, histories under
`/private/tmp/factory-startup-e2e-fsfPnp/`. Both fixture-child cleanups used fresh
identity checks; no live fixture child remains. Maintained tests carry the proof
when scratch evidence is no longer available.

Current Git registration is checked with Git's documented root/common/git-dir
queries and NUL-delimited worktree porcelain output. See the official
[git-worktree manual](https://git-scm.com/docs/git-worktree) and
[git-rev-parse manual](https://git-scm.com/docs/git-rev-parse). No hook/filter
configuration behavior, provider, dashboard, Windows helper, installed package,
release, or learning-adoption implementation changes were made.

Reflection: unavailable original identity cannot be reconstructed safely by fresh
path shape checks alone. The anchor, exact-origin/run guard and explicit legacy
refusal are structural enforcement with maintained public tests, so no separate
brain/skill edit is needed. Independent review is still required before integration.
