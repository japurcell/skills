# T7 common adapter conformance

Local deterministic evidence, 2026-10-22 UTC, macOS arm64. This qualifies the
shared runner/adapter boundary using a real subprocess fixture. It does not
qualify a provider, native skill loading, or a new operating-system process mode.
The task starts from `caf46b425c8b19e871a496dda08edfb96d946b50` on
`codex/factory-adapters`. Independent review remains a separate integration gate.

## Public workflow contract

`WorkflowContext.agent<T>(name, AgentOptions<T>)` returns a saved succeeded or
invalid result. Required invalid output cannot be ignored when the workflow
ends. A workflow may explicitly request a permitted code/format correction with
prior-attempt lineage and findings; the existing additional/code/format budgets
still apply. Only a successful correction resolves its invalid ancestor chain.
The saved failed attempts remain failed. A valid question is saved before peers
stop, and is never silently converted into a format-correction request.
Independent failure, including unresolved invalid output, outranks a question;
the complete request remains inspectable. Cleanup uncertainty preserves the
question while retaining claims/capacity and returning a failing exit status.

Repository `.factory/agents.json` supplies defaults and named profiles. At step
start, the runner resolves defaults, selected profile, step fields, and the
explicit override targeted by the fully qualified operation key. Supplied fields
replace, omitted fields inherit, and an empty skill list clears. Workflows can
explicitly compose prompt strings or skill arrays. Prompt/skill/resource files
are read once for that step, and their effective bytes plus field provenance are
saved before adapter exposure and before launch. A later step rereads current
files. Required harness, model, reasoning, permissions, delivery mode and declared
capabilities must be honored or rejected without fallback/substitution.

The selected adapter receives the effective requested prompt, ordered skills,
resources and delivery mode as supplied inputs. Its exact launch construction
owns delivery to the harness. A successful launch is not proof that the harness
loaded or complied with those instructions. `loadedSkills` records only explicit
adapter observations; omission remains unknown. Native and instruction delivery
are explicit modes with no automatic switching. Real providers must qualify
actual native/instruction delivery in their provider task.

Structured payload contracts are named explicit workflow validators,
`{ name, validate(value): value is T }`. The common runner does not claim partial
JSON Schema validation. The adapter declares one authoritative final channel,
its decoder, event channel, question exit codes, exact argv/environment,
child-control scope and stop implementation. No inherited terminal or approval
bridge is available. Stdout/stderr are filtered and saved through the canonical
backpressured recorder before accepted event exposure. Failed protocol streams
finish as partial captures when recording remains available. Final decoding is
bounded to 1 MiB of original and saved text; oversized results retain complete
raw filtered evidence. Machine lines are bounded to 1 MiB, including the last
chunk containing a newline and the unterminated final line.

Initial work, independent review and every later invocation start fresh.
Compatible reuse is limited to an explicitly requested same-invocation
correction. Unsupported/incompatible reuse is decided before dispatch and
starts exactly one fresh attempt using the selected validated profile and
explicit saved context. A failed reuse launch never starts a fresh retry.

## Session/store interface for observation

Schema bootstrap is version 3; existing incompatible stores refuse normal open.
No automatic migration, history replacement or schema repair is introduced.

`Attempt.agent` saves `inputsCaptureId`, `resultCaptureId`, `outputCaptureId`,
`adapter`, `sessionMode: 'fresh' | 'reuse'`, the context basis,
`reusedAttemptId?`, and the validator name or null. `readHistory` capture entries
also expose their `attemptId` or null.

`saveAgentMetadata(attemptId, metadata)` requires an admitted agent and matching
capture ownership before launch. `saveSession(attemptId, SessionEvent)` returns
an exported `NativeSession`: stable id, invocation/attempt/native identities,
reported parent native identity, lifecycle, optional usage/loading evidence and
input/output/result capture references. The store rejects forged ownership keys,
invalid telemetry and original or filtered event JSON above 8192 bytes.
Omitted telemetry is `{state:'unknown'}`; genuine zero usage is possible only
with explicit `{tokens:0, scope:'self'|'includes-children'}` evidence. Parent
usage that includes children stays labelled and is never added to child totals
by the common runner. Reported children do not create managed attempts/debits.

`readSessions({invocationId, after?: number, limit?: number})` returns
`{sessions: NativeSession[], nextCursor: number, hasMore: boolean}`. Default limit
is 50, maximum 200. Serialized response size remains below 1 MiB. Row cursors
are stable across updates. `session.changed` events identify session, attempt,
invocation and lifecycle; observers refresh changed detail rather than treating
an update as a new paged row. Existing capture/event paging remains unchanged.

## Initial candidate verification before independent review

All Node checks used the qualified v24.22.1 darwin-arm64 binary, with SQLite
3.53.4, TypeScript 7.0.2 and Node types 24.19.2. The qualified binary is at
`/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/factory-qualified-node-i2fv29e3/node-v24.22.1-darwin-arm64/bin/node`.
Prepend that bin directory to PATH for these commands. The repository root is
the working directory unless stated otherwise.

- `rtk proxy npm --prefix packages/software-factory run typecheck`: strict source
  and qualification consumers pass.
- `rtk proxy npm --prefix packages/software-factory run build`: fresh runtime and
  public declaration build passes before tests.
- From `packages/software-factory`, `rtk proxy node --test test/adapters.test.mjs
  test/fixtures.test.mjs test/cli.test.mjs test/dispatch.test.mjs
  test/store.test.mjs test/capture.test.mjs test/recording-integration.test.mjs
  test/placement.test.mjs test/startup.test.mjs test/shutdown.test.mjs
  qualification/runtime.test.mjs qualification/ci.test.mjs`: 123/123 pass in
  28.025 seconds after the final source repair, zero skipped/cancelled. This
  includes 30 adapter cases and all existing 93 cases. The subsequent additional
  selected-harness/model zero-launch case also passes against that unchanged
  source/build.
- `rtk proxy node --test test/adapters.test.mjs`: final 31/31 pass in 27.359
  seconds, zero failures/skips/cancellations, against the unchanged fresh build.
- `rtk proxy npm --prefix packages/software-factory run test:all`: expected exit 1,
  `adapters: not implemented; no tests registered`. Parent owns registration;
  unfinished groups cannot pass empty. After adapter registration, the next
  unfinished group must still refuse.
- `rtk git diff --check`: passes.

Maintained public workflow/store/subprocess cases cover concurrent fresh agents,
profile precedence/current file bytes, targeted overrides, unsupported routes,
permission denial/unexpected interaction, missing/malformed/oversized final
output, explicit bounded corrections, no hidden retry, fresh review/later
invocation, early authoritative questions, independent failure precedence,
timeout/capacity waits, real recorder failure, unknown cleanup retention, child
parentage/usage scope, stream size/finalization and session row/page bounds.

Red-before-green on resume reproduced: unresolved invalid result hidden by a
later question (exit 2 instead of 1); a newline-terminated oversized event reaching
adapter decoding; a failed machine capture remaining open instead of partial;
forged session ownership fields accepted; and scalar zero telemetry accepted.
The repaired cases pass without weakened existing assertions. Raw-output checks
use public paging instead of assuming one bounded page contains the full result.

No live provider, credentials, paid call, installation, retry service, release,
learning adoption, native Windows startup, or universal descendant controller was
used. POSIX group-only and unknown-child cleanup constraints from T6 remain.
The Node v24 child-process and string-decoder documentation endpoints were not
accessible through the web tool during this run, so no new version-specific
online documentation proof is claimed beyond the pinned public runtime tests.

Reflection: failure precedence, input/observation separation, protocol completion
and ownership validation are encoded in maintained public tests and runtime
checks. Task-specific state belongs in the parent-owned active plan/handoff;
no separate durable brain or skill edit is warranted.


## Independent review repairs

Independent review requested changes on the first candidate. Its passing 31+93
cases did not establish acceptance of the uncovered behaviors. The unchanged
public probes reproduced all three findings: dropping a required-number validator
let an object succeed; recursively correcting malformed format-correction output
spent two additional attempts under the default one-format-correction policy;
and malformed machine events stopped the process group but left an unsettled
occupied attempt, despite ESRCH and a functioning partial recorder.

Corrections now retain the selected named validator and, within the same
invocation, reapply the original callable contract. Omitting or renaming a required
contract rejects before admission. A same-name always-true replacement cannot
relax it. The initial callable/name are copied before asynchronous work, so
mutating the caller's validator object also cannot weaken the saved contract.
A genuine number correction passes the preserved callable and resolves the
invalid ancestor while retaining both original attempt outcomes.

The persistent admission boundary rejects a format correction derived from any
prior format-correction ancestor. This deliberately rejects recursive format
correction instead of granting it a fresh budget. Renamed operation IDs,
intervening code corrections and a reopened store cannot erase that ancestry.
The rejected work creates no attempt/debit; existing correction and additional
limits remain in force. No schema or observation API change is needed.

After a protocol decode or session-save failure, the runner stops its live owned
scope, drains the streams and obtains actual cleanup evidence. If the recorder
still works and a started attempt remains unsettled, it records a failed terminal
outcome with that measured quiescence. Proven absent groups release occupancy
and the invocation claim; declared unknown scope retains both, even when the
local group is absent. Recorder failure and missing saved spawn identity still
retain conservative unresolved ownership. Existing terminal outcomes are never
rewritten.

Eleven maintained public regressions were added: validator omission, renaming,
same-name replacement, caller-object mutation and valid preserved-contract repair;
renamed, indirect and reopened-history recursive-format rejection; and real
subprocess decode/session-save/unknown-scope failure settlement. The review's
three scenarios, validator replacement/mutation and renamed/reopened-history
failures were observed before their corresponding source repairs. The positive
number correction and indirect-lineage case then verify permitted success and
the ancestry defense.
The working-recorder cases verify partial raw evidence, terminal failure, zero
occupied capacity, exact claim release and native group ESRCH. The unknown-scope
and unchanged recorder-failure cases verify retained ownership instead.

Final repaired-candidate proof: strict source and qualification typechecks and
fresh runtime/declaration build pass. The complete command listed above passes
135/135 cases (42 adapter plus all existing 93) in 39.285 seconds, with zero
failures/skips/cancellations. Both unchanged reviewer probe scripts then confirm:
validator removal rejects with one launch/additionalUsed 0; recursive format
correction rejects with two launches/additionalUsed 1; bad-event records failed,
quiescent true, occupiedAgents 0, cleanup complete, partial capture and ESRCH.
`test:all` still intentionally exits 1 at unregistered adapters.
Re-review remains required before integration. Parent owns active plan/handoff, adapter
registration and integrated suite proof. No live provider or installation ran.

Reflection: the review findings are enforced by public tests and runtime
invariants. No durable brain/skill edit is needed beyond these structural checks.


## T7 stream context extension

Scoped candidate evidence, 2026-10-22 UTC, starting from `04df882b` on
`codex/factory-adapter-streams`. This extends common adapter conformance through
`context.agent` with a local real Node subprocess protocol. It does not qualify
a provider or make live-provider calls. Independent review remains required.

`AdapterLaunch` may provide a per-launch
`mapEvent(line, channel: 'stdout' | 'stderr')` closure and a nonempty, unique
`eventChannels` subset. Omitted fields preserve `adapter.mapEvent` and
`adapter.eventChannel`. The selected authoritative final channel is unchanged.
Both selected streams use the existing bounded, backpressured raw recorder and
recorder barrier before decoding. The existing 1 MiB machine-frame and 8192-byte
session limits remain in force. Invalid channel arrays (including sparse arrays)
and noncallable launch mappers reject before spawn with a clean failed,
`not_started` attempt. No session/store schema or observation API changes occur.

The fixture emits a native identity once, then terminal lifecycle and usage
without identities. Two concurrent attempts now retain their distinct native
identities and explicit token totals through separate launch closures. Its mapper
opens public saved captures for the exact attempt and channel before accepting
each line, checking that decoding cannot outrun durable raw evidence.

The native subprocess can also emit valid stdout final output and exit zero
while only stderr contains a sandbox denial. That mapper exception stays an
independent terminal failure, with partial raw stderr preserved. The result case
creates no question; the authoritative question/EOF case retains its complete
question and context while the attempt and invocation remain failed. Both prove
actual native exit zero, final group absence, released occupancy and claims, and
one managed attempt without correction, retry or permission changes.

During this proof, immediate shutdown after decoding stderr sometimes probed the
already exiting macOS process group before Node delivered exit/close. The native
probe and signal returned EPERM while the child exit hook had saved code zero;
that real uncertainty correctly remained sticky. The repair leaves
`native/process.ts` unchanged. For independent stream-processing failure, the
runner stops admissions and peers immediately, then spends at most
`min(10ms, existing grace)` observing the owner's exit before its normal stop
callback. An immutable first-failure deadline charges that observation against
the existing grace; stop and failure-settlement checks receive only its remaining
budget. A cached stop promise prevents repeated callbacks from restarting this
window. The catch path retains direct live-scope cleanup if the adapter stop
callback rejects. Exit observation alone never proves quiescence: unchanged
closed-pipe and native group checks still decide it, and no observed EPERM is
cleared. No shutdown deadline or descendant-control scope is widened.

Eleven new public regressions cover concurrent contextual mapping; stdout result
and question precedence against stderr denial; empty, duplicate, unknown,
nonarray and sparse stream selections and a noncallable mapper; and live
SIGTERM-resistant owners at existing grace budgets of 1 ms and 100 ms. The live
cases require SIGKILL, group ESRCH, zero occupied capacity and no natural-exit
marker. The 1 ms case exercises an exhausted observation budget, and both remain
bounded despite a 10-second live timer. Existing unknown-scope, failed recorder,
inherited-pipe, missing identity and owner-clearance cases retain conservative
behavior.

Red evidence against the unchanged baseline runner: concurrent unkeyed events
persisted zero sessions; stderr-only denial plus valid stdout result incorrectly
succeeded with exit zero; the corresponding authoritative question incorrectly
returned needs-input/exit two; and invalid optional stream configurations reached
native spawn. Sparse-array acceptance was separately reproduced before the
validation repair. All old assertions remain intact.

Final qualified Node v24.22.1 darwin-arm64 verification:

- From `packages/software-factory`, `rtk proxy npm run typecheck` and
  `rtk proxy npm run build` pass against the final source.
- From that directory, `rtk proxy node --test test/adapters.test.mjs
  test/fixtures.test.mjs test/cli.test.mjs test/dispatch.test.mjs
  test/store.test.mjs test/capture.test.mjs test/recording-integration.test.mjs
  test/placement.test.mjs test/startup.test.mjs test/shutdown.test.mjs
  qualification/runtime.test.mjs qualification/ci.test.mjs` passes 148/148 in
  46.897 seconds: 53 adapter cases plus all 95 existing cases, with zero
  failures, skips or cancellations.
- `rtk git diff --check` passes. Generated build output and diagnostic backups
  are excluded from the commit. Registry, canonical docs, CI, providers,
  store/lifecycle/workspace sources and native process policy remain unchanged.

Reflection: per-attempt parser ownership, channel selection validation, saved
raw evidence and bounded failure cleanup are enforced in runtime checks and
maintained public subprocess tests. No separate durable brain or skill edit is
needed. The parent owns task status, integration and independent review.


## Stream stop callback review repairs

Independent review rejected `38018c85691f0973dd7477b294c0e809b397da60` despite
its passing 148 cases. SEC-001 isolated an introduced failure: the native child
closed authoritative stdout, emitted an invalid stderr event 80 ms later and
stayed alive, while `requestStop` returned a never-settling promise. The catch
awaited that promise before direct native cleanup. The invocation exhausted its
drain allowance, returned cancelled/unknown and retained an unsettled occupied
attempt with a live process group. The reviewer established that the corresponding
baseline instead failed and cleaned its owned group. SEC-002 showed the related
existing gap when stdout stayed open: `allSettled` could not reach the catch while
adapter cooperation failed to close that pipe.

The repair keeps the original immutable first-failure deadline and charged
natural-exit observation. After that observation, the runner starts its owned
native scope stop independently of adapter cooperation, using only remaining
grace. The adapter callback is awaited only against the same remaining deadline;
its timeout or rejection cannot delay native stop or leave another machine pipe
open. The catch's cached wait is now bounded, and its direct native fallback
remains. No deadline, native process policy, declared child scope, persistence
schema, or admission policy changes. Submission, callback settlement and timeout
still prove no absence; the existing native closed-pipe/group checks decide
quiescence. Recording failure and declared/observed uncertainty remain
conservative.

The first observed stream failure is retained while all streams settle. The
escaped-pipe test reproduced a later stdout `Premature close` replacing the
initiating stderr decode error under the former array-order selection. Cleanup
errors now preserve that initiating independent failure and its saved raw input.

Five additional maintained public subprocess cases cover hanging and rejecting
stop callbacks, each with stdout open and closed, plus a native owner that exits
zero while an escaped child keeps inherited pipes open. The paired hanging-stop
cases were red before repair: approximately 2.02 and 2.05 seconds, cancelled
instead of failed, with test-owned leaked groups explicitly cleaned in finalizers.
They pass after repair at approximately one second including repository/startup
work, with failed terminal attempts, actual group ESRCH, partial raw stderr,
released claims and zero occupied capacity. The rejection cases prove the same
measured cleanup. The escaped-pipe control preserves failed/unknown cleanup and
occupied capacity, proves its original owner exited zero and its original group
is absent, and verifies the escaped child remains live until explicit fixture
cleanup. This establishes that independent stop does not manufacture descendant
absence or clear genuine uncertainty.

Reflection: the review exposed a real control dependency omitted from the first
candidate's checks. Bounded adapter cooperation, independent live-scope stop and
first-failure preservation are now enforced structurally by runtime ordering and
maintained public regressions. No separate brain or skill edit is warranted.


Final repaired-candidate verification uses the same qualified Node v24.22.1
binary and full affected command documented above. Strict source/qualification
typechecks and fresh runtime/declaration build pass. The complete suite passes
153/153 in 56.488 seconds: 58 adapter cases and all 95 existing cases, with zero
failures, skips or cancellations. `rtk git diff --check` passes. These results
supersede the 148-case candidate proof for review acceptance; independent
re-review is still required. This repair changes only `src/agents.ts`, the
public adapter tests and this scoped evidence. The native process module,
provider code, store/lifecycle/workspace sources, registry, canonical docs and CI
remain unchanged.

## T8 common stdin seam candidate

The optional `AdapterLaunch.stdin` field accepts only a string whose UTF-8
encoding is at most 1048576 bytes. Invalid types and oversized text refuse
before spawn with a failed, quiescent `not_started` attempt. Omitting the field
keeps the previous ignored, closed child stdin. Supplying it selects a managed
pipe; the runner starts both saved, backpressured output readers before sending
fixed 65536-byte chunks and EOF. It waits for write and end callbacks, so an
early closed pipe is a terminal delivery failure even if the child emits a valid
result and exits zero. A stop cancels pending input without making its induced
pipe error outrank the already owned timeout or complete question. An
independent input failure stops admission and peers, while the first
independent output failure retains precedence over induced input errors.
Native closed-pipe and group evidence still determine complete versus unknown
cleanup; the existing deadline, stop grace, store schema and output limits are
unchanged.

The public `WorkflowContext.agent` real-subprocess fixture verifies exact
literal Unicode, newline and control-looking bytes on stdin and EOF, and
checks the child argv and environment for the private marker. Other cases
cover the default ignored stdin; an exact multibyte 1 MiB boundary; oversize
and nonstring prelaunch refusal; slow reading and output flooding before input
reading, with raw output saved before decode; early stdin closure on a child
programmed to return a valid result; a concurrent peer stopped by independent
input failure; blocked readers under timeout and authoritative question;
independent stderr failure with a hanging stop callback; and unknown-scope
and recorder-failure occupancy retention. The first red run showed the private fixture receiving
zero bytes through its ignored stdin. During the early-close cycle, the test
also exposed an unhandled EPIPE after the write callback reported failure;
the input stream now retains its error listener through close. All 15 new
cases passed after the repair without weakening the 166 existing checks.

Final local verification on 2026-10-22, macOS arm64, uses the pinned Node
v24.22.1 binary identified above. `rtk proxy npm run typecheck` passes strict
source and qualification consumers; `rtk proxy npm run build` passes fresh
runtime and declaration generation. From `packages/software-factory`, the
12-file command documented in the previous section passes 181/181 in 62.811
seconds: 73 adapter checks and 108 other registered checks, with zero failures,
skips or cancellations. This candidate does not change a real provider's prompt
format or qualify any provider. Independent review remains required.

UNVERIFIED: The Node v24 online child-process and writable-stream pages were
inaccessible through the available web tool. The pinned runtime subprocess
tests prove the observed pipe, callback and stop behavior used here.

## Independent stop review repair

Independent review of candidate `b3e6c03e` found that timeout and saved-question
stops still depended on `adapter.requestStop` calling the owned native stop
callback. With a blocked stdin reader and a hanging adapter callback, each
review probe returned after about 1.7 seconds with cancelled/unknown cleanup,
an unsettled attempt, an occupied slot and a live owned process group. The
reviewer's disposable fixture finalizers killed only those exact groups. The
same maintained red cases also failed when the adapter callback rejected.

The runner now uses one cached stop task and an immutable deadline for every
stop cause. It spends at most 10 ms of the existing grace observing natural
exit, then starts `scope.stop(remainingGrace())` independently of adapter
cooperation. The adapter callback is awaited only within the same remaining
grace; a hanging or rejecting callback cannot delay native cleanup. An
already-exited owner with a saved complete question needs no adapter callback,
but the owned scope still determines descendant and pipe absence. The first
independent failure remains saved, and output/input cancellation cannot replace
the timeout or saved question. Existing native process policy and grace bounds
are unchanged.

Four new maintained real-subprocess cases cover hanging and rejecting adapter
stop callbacks for both blocked-reader timeout and saved-question paths. They
assert terminal attempt outcome, complete cleanup, zero occupied capacity,
actual process-group absence, and the saved request only for the question.
The independent `/private/tmp/stdin-review-probe.test.mjs` timeout and question
reproductions both pass after the repair, in 1.881 seconds combined. Final
pinned Node v24.22.1 verification passes strict source/qualification typecheck
and fresh build; the same complete 12-file local matrix passes 185/185 in
73.204 seconds: 77 adapter cases and 108 other checks, zero failures, skips or
cancellations. `rtk git diff --check` passes. This supersedes the 181-case
candidate proof; independent re-review remains required.
