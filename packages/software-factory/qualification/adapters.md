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
