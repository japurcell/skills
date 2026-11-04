# Windows full-operation creator experiment contract

Historical design provenance: read-only decision on2026-11-04, subsequently accepted by root and implemented as source3a0ac3be. Current release/results are maintained in [ExecPlan](../ExecPlan.md) and [handoff](../handoff.md). This task changes only this file. No implementation, probe, test, build, native run, GitHub, provider, authentication, review or desktop action is authorized by this packet.

## Decision

Choose one qualification-only **full operation creator** experiment. Keep the current owned CRT thread and its accounting/startup/join/checked-close protocol, but expand its work from the target branch plus `child.Stop()` to the contiguous original operation from survival `control.Create()` through `control.Release()`. This includes control readiness, target work/catches, target Stop, all original post-target checks and output, control Stop, and both Releases. Keep the original baseline, `OWNED` row and `EntryOutput` capture on the observer before the creator is created. Keep the original final query and terminal summary/FILE flush/close on the observer after proven normal creator return, actual signaled join and the checked creator-handle close.

Do not add narrower measurements in this experiment. Preserve all 15 captures, their current operation-relative positions, both authoritative query sites and the existing finite phase grammar. This is one changed lifetime profile, not a source-proven repair or a documented promise of count restoration.

Implementation remains unauthorized until root accepts this packet. Root owns the later single changed exact-head native experiment after concrete preservation and portable checks. No retry of the current failed profile is selected.

## Evidence and interpretation

Read source at root head `317f16bedb341eb38724b1fe7c51592b2ec97e2a`. Current `windows-owned-image-probe.cpp` is byte-identical to source `37fb36df92d5d34052f8ef0b8bc742a9444e98bb`; the later `b0c0ee83` fixture correction changes the portable late-producer control, not C++.

Actual run `41794618784`, job `126455664240`, exact integration `57638b107da3b9734d5a180899e5eb1822b47658`, passed protocol 63/63, origin/inbox/available/ready and MSVC compilation, then refused the first positive native case. The actual native result was exit1/nonempty stderr; phase none/reason clear; cleanup=false, survival/flush/close=true; countQuery=true, countNonincrease=false, leakedZero=false; ownedZero=true, all reached tracked closes=true. Guard refused, upload skipped, artifact inventory empty. The other 33 cases remain unproved. Evidence: `/tmp/factory-late-producer-41794618784-job.log` and `/tmp/factory-late-producer-41794618784-failed.log`, sanitized finite record at the latter line5.

The coherent phase record is entryOutput=equal, all 15 later checkpoints=above, pinHash=equal, imageHash=equal, targetScope=equal, profileRest=above. Previous original-thread profile `92c96edf` reported targetScope=above. These are observations from different profiles. The current targetScope pair is ControlReady to ChildReleased; it crosses target work, the existing creator join/close, target release and a change in the control's liveness. Equality is equality of aggregate endpoints, not evidence of unchanged handle identities or no intervening retention. Neither paired hash equality proves universal hash noninvolvement.

The minimal creator completed far enough for the downstream typed record, so this actual failed run supplies the E2E RED for the next hypothesis. It did not fix the strict final count. Source proves that the non-debug control Create/readiness and the downstream inspection/Stop/Release region still ran on the long-lived observer. No missing source-owned close is established on the observed positive path.

The next controlled question is therefore whether the same original operation, including that remaining control/release work, meets the strict assertion after its performing thread has normally ended. This is the smallest next complete lifetime profile: it expands the existing worker instead of adding another worker, another observation schema, a new resource model or a guessed close.

### Why no additional phase query first

Additional queries around control creation cannot by themselves separate expected held control handles from any untracked retained state. Queries around control release observe an interval in which explicit owned handles disappear. Existing checkpoint relations are to the original baseline; comparing two `above` labels is insufficient to recover their direct relation or amount. A new direct relation could localize an aggregate transition, but would still not establish a specific omitted close or which remaining operation needs a narrower lifetime change. Such instrumentation is a distinct optional future diagnostic, not a prerequisite for testing the already identified full-operation lifetime question.

This selection does not assign the increase to control creation, CRT state, CNG, a debug object, a cache or any particular API. Full-profile success would not distinguish those explanations. If root requires API causality rather than a bounded changed-profile observation, this experiment cannot supply it and no identity-based fix is currently justified.

## Patterns and source anchors

All anchors below refer to the inspected root source and must be relocated after implementation.

- `packages/software-factory/qualification/windows-owned-image-probe.cpp:18`: mutable process-wide handle counters, close evidence and details FILE. They require serialized access, not a broad atomic/tracker redesign.
- `windows-owned-image-probe.cpp:95`: existing `Handle` accounts real handles and closes through sticky `CheckedClose`; retain it for the creator.
- `windows-owned-image-probe.cpp:187`, `:254`, `:314`: `Child::Create`, `Child::Stop`, `Child::Release`. Preserve their implementations, inheritance list, held identity, event ownership, no-resume termination cleanup, deadlines and close order.
- `windows-owned-image-probe.cpp:328`, `:380`: `Identify` and `Probe`, including both hash pairs and original debug/suspend/continue/detach/postcondition/resume sequence. Keep these bodies intact.
- `windows-owned-image-probe.cpp:500`, `:516`: `CreatorGate` is lock-free release/acquire startup accounting with no kernel object; `PinUnjoinedCreator` never unwinds or inspects live worker state.
- `windows-owned-image-probe.cpp:523`, `:532`, `:577`: intentional nested owner-loss creator and its gated immediate-start accounting, unchanged 4000ms owner wait, 1000ms held-child wait and existing fatal guard.
- `windows-owned-image-probe.cpp:552`, `:568`, `:610`: current `TargetOutcome`, `TargetWork`, `RunTarget` and CRT entry are the local replacement seam. Extract the original branch from RunTarget into RunProfile, rather than calling its Stop-containing helper inside a broader catch. Do not create a general threading adapter or new runtime abstraction.
- `windows-owned-image-probe.cpp:635`, `:641`, `:649`: existing details/warmup prelude, authoritative baseline and pre-resource OWNED/EntryOutput. Preserve their operation order.
- `windows-owned-image-probe.cpp:653`, `:678`, `:711`: contiguous control-create/readiness, post-target checks and Release region to perform on the expanded creator.
- `windows-owned-image-probe.cpp:712`, `:715`, `:718`, `:719`, `:741`: final query, strict increase/leaked/cleanup calculation and return. Retain the original arithmetic and predicates.
- `packages/software-factory/qualification/windows-owned-image.mjs:58`, `:75`: exact receipt order/grammar, cleanup and ELAPSED<=10000 acceptance.
- `packages/software-factory/qualification/windows-owned-image-native.qualification.mjs:89`, `:110`: unchanged 12000ms transport and actual outcome/guard refusal.
- `packages/software-factory/qualification/windows-owned-image-fixture.cpp:33`: unchanged 8000ms fixture fallback, not proof of external closure.

## Stack and primary contracts

Detected stack: x64 Win32, MSVC C++17 `/W4 /WX /EHsc /MT`, `_WIN32_WINNT=0x0A00`, exact Node24.22.1 driver. Build flags are at `packages/software-factory/qualification/windows-owned-image-native-build.ps1:95`.

- [_beginthreadex](https://learn.microsoft.com/en-us/cpp/c-runtime-library/reference/beginthread-beginthreadex?view=msvc-170) supports the existing CRT entry, a caller-owned waitable handle and normal-return CRT cleanup. Null security makes that handle non-inheritable; creation failure returns0. Retain this mechanism and one caller close. It does not guarantee arbitrary aggregate process-count restoration.
- [WaitForSingleObject](https://learn.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-waitforsingleobject) distinguishes signaled, timeout and failed waits. Never close the handle during a pending wait. Actual thread termination is required in addition to completion publication. [CloseHandle](https://learn.microsoft.com/en-us/windows/win32/api/handleapi/nf-handleapi-closehandle) does not terminate its thread; a completed close is separate from a completed thread.
- [WaitForDebugEvent](https://learn.microsoft.com/en-us/windows/win32/api/debugapi/nf-debugapi-waitfordebugevent) and [ContinueDebugEvent](https://learn.microsoft.com/en-us/windows/win32/api/debugapi/nf-debugapi-continuedebugevent) constrain calls to the process-creating thread. Ordinary target debug operations and any attached Stop remain on the full creator. The existing nested owner-loss thread remains its debuggee's creator; it intentionally exits instead of performing ordinary attached Stop first.
- [C++ atomic guidance](https://learn.microsoft.com/en-us/cpp/standard-library/atomic?view=msvc-170) describes ordered atomic visibility and platform-dependent lock freedom. Retain the existing compile-time lock-free requirement and release/acquire gates; these serialize existing non-atomic state rather than make concurrent access safe.
- [GetProcessHandleCount](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-getprocesshandlecount) provides a process aggregate, without identity or ownership attribution. Keeping the strict original baseline/final predicate is the observation this experiment tests. No documented contract reviewed promises that moving this body restores that aggregate.

## Exact ownership and interface

Use one `ProfileWork` in the original `wmain` scope, replacing current `TargetWork` rather than nesting another ordinary worker. It references the original `Child child, control`, immutable selected case, and the immutable original `argv[1]` root argument. Its `CreatorGate` uses the original start timestamp. Keeping the root as a borrowed immutable argument permits the original `std::wstring root = argv[1]` construction to remain after ControlReady on the worker, instead of moving potentially allocating work into the account-before-release interval. `argv`, case string, both Child objects, context and live FILE remain in scope until join or remain pinned.

`ProfileOutcome` replaces `TargetOutcome` and holds only bounded existing values: closed-vocabulary failure/phase pointers; booleans for entered, eligibility, cleanup, survival and controlStopped; and the four existing `Check` values exitQuery, exitInactive, earlyClear and rejectedClear. Initialize to the original wmain defaults: failure none, phase survival-create, cleanup true, survival/controlStopped false, checks NotReached. No raw error, count, path, handle, PID, text buffer or copied stream content is added to the outcome. Existing Child/Stop and global evidence stays in its existing storage.

Use these local functions in the C++ anonymous namespace:

    void FinishProfile(ProfileWork& work);
    void RunProfile(ProfileWork& work);
    unsigned __stdcall OwnProfile(void* argument);

`FinishProfile` performs the original post-catch operation from `child.Stop(); CaptureCount(ChildStopped);` through `child.Release(); CaptureCount(ChildReleased); control.Release();` in exact order: child Stop/capture; `cleanup = cleanup && eligible` at the original creator-eligibility conjunction; marker/exit/OUTPUT; survival test; unconditional independent control.Stop/capture; CONTROL row; early/rejected-marker/output-prefix checks; both Releases. It executes once per path, including no-child cleanup after control preparation failed. It never performs the final count, terminal rows, FILE flush/close or new waiting policy.

`RunProfile` sets entered, then places original control Create/readiness/ControlReady, original worker-local root construction and the original target branch in their original operation order inside the fixed char-pointer/unknown catches. Extract the branch from current RunTarget rather than calling that Stop-containing helper inside this try. Preserve failurePhase survival-create/survival-ready/probe/owner-interruption/none assignments and the nested owner-loss branch. After those catches, call FinishProfile once with child.Stop **outside** the catch scope, as in the original pre-minimal body. Do not broaden the original target catches around Stop/Release, turn a new unexpected exception into successful cleanup, or overwrite an earlier cleanup failure. `OwnProfile` is the sole ordinary CRT entry; current RunTarget and OwnTarget disappear rather than become another layer.

`OwnProfile` touches only immutable context and the gate until accounting release. After gate entry it runs RunProfile. It publishes returned only after the complete operation function and automatic scopes finish, then returns normally. No exception may escape the CRT entry. A truly unexpected exception outside the original catch scopes must latch ineligible and must not publish a completed operation; normal thread exit without that publication leads to pinned refusal, never final summary or admission. Do not add a general recovery path that guesses which captures/releases already happened.

## Exact data flow and operation order

1. Observer: keep argv/allowlist/error-mode/details-open and existing provider warmup unchanged. Retain baseline query and RecordCount, then original start timestamp. This original baseline is before **every new** creator/gate resource. Existing pre-baseline details/CNG prelude is not moved or enlarged.
2. Observer: keep original Child objects, OWNED row and EntryOutput capture before `_beginthreadex`. Initialize ProfileWork and its atomics without acquiring any new OS object. No control process is created yet.
3. Observer: call `_beginthreadex(nullptr, 0, OwnProfile, &state, 0, nullptr)` and account its valid returned handle through existing Handle **before** release-publishing the gate. No throwing, allocating or evidence/output operation is permitted between successful handle accounting and release. No second ordinary worker is created.
4. Creator: after gate acquisition, run control Create, readiness loop and ControlReady; original target operation/catches; original child.Stop and ChildStopped capture; original marker/exit/OUTPUT; survival observation; original control.Stop and ControlStopped capture; CONTROL/marker/output checks; child.Release, ChildReleased capture, control.Release. Every original Win32/CNG operation retains its operation-relative order. All target debug calls and attached cleanup share this creator, except intentional nested owner-loss calls that remain exclusively on their original inner creator.
5. Observer while creator runs: compute remaining original eligibility budget and perform only the bounded wait on the held creator handle. No Child/control/FILE/stdout/counter/check/count-sample/result access, drain, close, Stop or Release occurs concurrently. Start/returned atomics and immutable timestamp are the only synchronization reads. During nested owner-loss, the outer creator also stops accessing shared globals until the inner has joined.
6. Creator: all original operation local scopes finish, completion is release-published, CRT entry returns normally. A completion flag before actual termination is insufficient.
7. Observer: require actual WAIT_OBJECT_0, elapsed within the same original 10000ms budget and acquire-published operation completion. Only then close the owned creator handle through checked existing tracking. An actual checked-close failure stays sticky in closed/closeCalls/ownedClose; it may be diagnosed after proven join, but can never qualify.
8. Observer: after the successful wait/completion checks and creator close, read the bounded outcome once to restore original failure/phase, cleanup, survival and four Check values for unchanged final diagnostics. With the original operation complete and both releases already done, perform the **original one final query**, RecordCount(Final), private Log values, unchanged increased/ownedZero/leaked and strict cleanup predicates, unchanged terminal rows, details fflush/fclose, fixed refusal rows and original final return. The final diagnostic query may still run after a proven joined creator's checked-close failure, as in the accepted minimal contract; admission always requires close success. No final query is permitted after an unproven join or incomplete operation.

This removes the old ordinary creator join between ChildStopped and marker/exit inspection and places that join after control.Release. Thread/gate/join/close scaffolding is the only allowed interposition in the original API sequence. Do not duplicate child.Stop, a capture or either Release on the successful path.

### Creation and gate failures

If `_beginthreadex` returns0, no worker exists and no child/control Create occurred. Latch creator eligibility false and the fixed host failure. The observer may execute FinishProfile once solely for the original no-child independent cleanup/output/Release behavior; it must not fall back to creating control or executing Probe. The original final query/summary may run and must refuse because eligibility is false. No wait or close of invalid creator data is fabricated.

If a real creator's gate expires without entry, the original overall eligibility budget is expired: pin and refuse, even if the creator later ends. Never route that later join into final-query fallback. Any otherwise timely actual joined, published no-entry condition must still latch eligibility false, prove that no operation touched Child/control, and close the creator before the observer may run FinishProfile on those untouched objects. Under the current monotonic deadline gate, expiration does not produce such a timely condition. Preserve entered/returned as separate facts; later time or cleanup success cannot clear a startup failure. The strict old 46-state parser may project a newly failed eligibility conjunct to unknown rather than inventing an old contributor. Do not change its grammar or coherence rules.

The ordinary no-entry path may publish normal return for safe joined fallback, while the unexpected partial-operation exception path must not publish complete operation. These two conditions must not be conflated.

### Nested owner loss

Preserve `LoseDebuggerThread`, its pending-image file close and intentional uncontinued first event on normal inner return. Keep the existing separate root-copy lifetime for OwnerLoss; after branch extraction, spell that local `ownerRoot` and initialize it from the outer immutable `root`, then pass `&ownerRoot` to OwnerLoss. This avoids introducing a shadowed/self-initialized `root` under `/W4 /WX`; the copy and its proven-join-or-pinned lifetime are preserved. Preserve account-before-release for its Handle. Preserve the existing 4000ms inner wait, exact existing fatal `ExitProcess(2)` guard, 1000ms held-child termination wait, and subsequent attached/pending/debug-handle clear order. This old isolated fatal guard is neither broadened nor reused for the full creator. No DebugSetProcessKillOnExit policy change is introduced. The original owner-interruption case still requires its original abnormal child exit and marker-free receipt; it is not converted into ordinary Stop-before-owner-exit.

## Bounds and pinned refusal

Keep receipt ELAPSED<=10000, transport12000, fixture8000, nested4000+1000 and every existing Probe/Stop/readiness/cap bound unchanged. The creator join uses the remaining original 10000ms eligibility budget, not a fresh budget. Final receipt validation still governs time used after successful join.

On expired eligibility, WAIT_TIMEOUT, WAIT_FAILED, unexpected wait result, missing completion or any unproven join: latch refusal irreversibly and enter the existing PinUnjoinedCreator inert wait. Never issue final count/COMPLETE, close the worker handle, flush/close its FILE, inspect or mutate shared Child/control/outcome/global state, unwind live context, return wmain, force thread termination or add early process exit. A later worker finish/join cannot convert this path into success. Keep all borrowed strings, both Child objects, outcome/context and live FILE pinned. The unchanged outer transport cutoff is the allowed final bound; no standalone closure guarantee is claimed.

Expected driver outcome is actual timeout/cap/signal/exit facts according to the unchanged transport, with any partial wire retained and no admitted artifact. Do not synthesize status1 or successful cleanup. The fixture fallback does not establish suspended/attached-child closure after controller termination. `processClosure` remains UNKNOWN.

## Capture and grammar preservation

Keep existing EntryOutput on observer before the new handle. Keep ControlReady, all Probe/hash/event phases, ChildStopped, ControlStopped and ChildReleased on their original operation boundaries, now on the creator. Final remains observer-only after join/close. The creator handle is legitimately held at intermediate worker captures; no subtraction, rebasing, new warmup, offset, extra count sample or settlement loop is permitted. TargetScope in this profile no longer crosses the outer join/close, unlike the minimal profile; document that difference rather than claiming its numeric equality/inequality should reproduce.

Keep `WriteCountPhases` and the strict 512-byte refusal/cleanup/phases projection unchanged. No new row, case, field, phase version, raw observation or public diagnostic is needed. Keep successful stdout/stderr grammar, validator/artifact schema and exact allowed case list unchanged. The original count-increase refusal must remain eligible for the existing coherent typed diagnostic; startup/partial-operation failures may remain unknown and still fail closed.

## Implementation map

Only after acceptance, the bounded source author modifies:

1. `packages/software-factory/qualification/windows-owned-image-probe.cpp`: replace TargetWork/TargetOutcome with ProfileWork/ProfileOutcome; extract the original target branch from RunTarget into RunProfile, with Stop outside its catches in FinishProfile; replace OwnTarget with OwnProfile; move the contiguous original operation onto that entry; keep the original observer prelude and final query/summary. Do not edit Child/Probe/Identify/tracker/CNG/debug/event/phase writers or add resources.
2. `packages/software-factory/qualification/windows-owned-image-native-case-refusal.md`: replace the active minimal-only contract with the accepted full-profile ownership/order/failure limits, actual retained RED and expected exact-head acceptance. Keep unique historical evidence clearly historical.
3. `packages/software-factory/qualification/windows-owned-image.md`: update only current qualification lifetime/acceptance statements that otherwise imply the ordinary target-only creator is current. Preserve profile/security/transport/namespace limitations.

`windows-owned-image.test.mjs` should remain byte-identical unless implementation exposes an actual missing external receipt/transport/guard behavior. The 63 existing purposes already cover the unchanged external grammar and actual timeout/late-wire/cap/exit refusal seam; adding a JavaScript model of the new Win32 lifetime would give no native proof. Any justified new test must exercise the real external seam and be scoped to an independently observed gap, with RED before source change. No new lifecycle modes or native cases are selected here.

All driver, transport, diagnostic projector, validator, artifact guard, build/authentication/host-profile sources, fixtures/shared header, origin/signature/pins, CI/workflows, product/runtime, registry, backend and canonical notes remain outside this source task. Root owns any later plan/canonical recording separately. Preserve original60 plus all three fixture controls, including the corrected direct IPC late producer, and the original native34 without skips or weakened expectations.

## Build sequence and proof gates

- [ ] Root accepts this exact design and assigns the bounded source author. No implementation before acceptance.
- [ ] Author snapshots exact source head and relevant qualification bytes. Retained native417946 first-positive count refusal is the actual E2E RED; do not claim a new local reproduction or a source-string assertion as E2E RED.
- [ ] Implement only the mapped qualification changes. Produce an operation/ownership preservation comparison against current37fb C++ plus current portable63. Compare original helper bodies and original operation statements byte-for-byte where extraction permits, and exact API/capture order after excluding only scheduling/accounting scaffolding. Explain relocation of every original statement; structural comparison is source evidence, not a runtime test.
- [ ] Prove source control flow for valid/zero creator, gate deadline/no-entry, normal completed operation, unexpected incomplete operation, WAIT_TIMEOUT/FAILED/unexpected/late join, close failure, target refusal plus independent cleanup, and nested immediate-start accounting. Show that no observer fallback can operate on an entered worker's Child/control state and no qualifying path bypasses normal join/publication/checked close. Do not construct a JS state machine that mirrors these branches.
- [ ] Run exact pinned Node24.22.1 `--test packages/software-factory/qualification/windows-owned-image.test.mjs` from the implementation worktree via `rtk proxy <qualified-node>`. Expect all63/63, zero failures/skips/cancellations/todos. Keep original60 and all three corrected real-process controls unchanged. Run relevant syntax and diff-whitespace checks. These are portable transport/grammar/guard evidence only.
- [ ] Recheck frozen source/head identity after full portable EOF and provide clean handback with exact files, source anchors, commands/results and explicitly unrun native facts. Root integrates normally and repeats the scoped concrete checks against the integrated bytes.
- [ ] Coordinator alone runs exactly one changed exact-head Windows qualification through the existing native entry/workflow after its checkpoint. Source/binary pins must naturally reflect the changed C++; no pin bypass. Observe actual MSVC `/W4 /WX` compilation, origin/signature profile, transport facts and every original native34 predicate. No local stand-in establishes Win32 scheduling, CRT teardown or count restoration.
- [ ] Stop after that one result. If the first positive still increases, retain its strict refusal and coherent phases and stop without retry. If it clears, all remaining33 original cases must pass before changed-profile native acceptance is met. A changed failure seam, missing/incoherent diagnostic, startup/join/close failure, timeout/cap or incomplete34 is failure/inconclusive; no partial artifact admission.

These proof seams are the existing externally exercised native receipt/exit/cleanup/guard and the real owned-child transport. The native34 exercise actual ordinary/negative/owner-loss behavior when reached. They do not deterministically inject every new scaffold failure. Source control-flow proof covers those branches before the native experiment; their actual Win32 fault behavior remains explicitly unverified unless later real native evidence reaches it. No invented portable concurrency claim fills that gap.

## Acceptance and unknowns

A complete pass establishes only that this exact full-operation creator profile on the exact worker met the unchanged native34 predicates, with original final zero increase, tracked close checks, successful wire and artifact guard. It does not establish historical cause or a repair to the old profile. Identity, number, type, owner, creating API and universal lifetime of the additional handles remain unknown. Source has not proven an omitted close. No documented arbitrary-handle closure guarantee follows from normal thread exit.

Namespace/DLL/code closure, equivalence to the existing Node launch, external child/process/console closure, helper/product admission, provider qualification and release remain unproved. Other C1 Windows privacy/CI tasks, C2 release, deferred reviews and desktop-last constraints are separate ownership and were not analyzed.

## Source snapshot and final read-only recheck

Initial inspected root head: `317f16bedb341eb38724b1fe7c51592b2ec97e2a`, clean git status. Relevant current Git blob IDs, ordered by path:

- `windows-owned-image-probe.cpp`: `a4607227166a9ccc17c6b333bf377788ec19a872`.
- `windows-owned-image.test.mjs`: `acd0c6e8d29e8e1d0b8555b33533ad7603f0eff8`.
- `windows-owned-image.mjs`: `ed8d5a9f3627a4b7ef1cc6223ad57caacd7129fc`.
- `windows-owned-image-native.qualification.mjs`: `0fa399ded6b4398385f509310c8ef0753f98275c`.
- `windows-owned-image-fixture.cpp`: `68ea25a56afff2068bac2df3631bb1e7b930065b`.
- `windows-owned-image-native-build.ps1`: `69b3820f73a9e9b18c56209a3b91a36fa8166453`.

Final read-only recheck at 08:16:14 UTC observed the same root head, clean git status and all six identical blob IDs. Reread current RunTarget/CRT entry and the observer baseline-to-final region at the end; source anchors and the retained operation order still agree. Only this `/tmp` decision file was written by this task. No code/probe/test/build/native/GH/provider/authentication/review/desktop action occurred.


## Integrated source proof

Full-operation creator source3a0ac3be (authored6d5389c) normally merged at clean6dd637b9. Only C++/two qualification notes differ; all three blobs and C++SHA8cd8cf3ae73041fe6f51f5696c89038b649953419a764ed6d7c78869cd84852e match handback. The accepted contract above expands the existing gated CRT creator from target-only to the original control.Create-through-control.Release operation. Observer baseline/OWNED/EntryOutput remain before thread creation; final strict query/summary stay after actual normal join/publication and checked close. Original helpers/API order/native34/15captures/bounds/parser/crypto/pins are preserved. Integrated portable63/63 passes4.911937s, zero skips at frozen6dd; syntax and head/source/runtimeSHA postflight pass09:05:53UTC. Scoped mechanical comparison uses fixed75476cd2 author baseline and verifies original branch/final block exactly, not native concurrency. Logs `/tmp/factory-full-creator-coordinator-portable.log`, postflight `/tmp/factory-full-creator-coordinator-postflight.json`, preservation `/tmp/factory-full-creator-integrated-preservation.json`. No MSVC/native/fault/count/cause/admission claim yet.

New scaffold fault behavior remains unverified natively; source preservation is not fault injection or a C++ scheduling model. One exact-head Windows experiment is authorized after this checkpoint, with no retry or product/helper admission.


## Single changed native outcome

Single full-operation creator experiment41804985008/job126489660955 at exact0b2bd1287776a8449b3cee959ee68c60f3b9462c completedFAIL09:09:13UTC. Protocol63/63/profileinbox-available-ready and actual MSVC path reach firstpositive nativeexit1/nonempty stderr. none/clear; cleanupfalse/survival+flush+closetrue; countQuerytrue/countNonincreasefalse/leakedZerofalse, ownedZerotrue/allreachedclosestrue. EntryOutputequal/alllaterpointsabove; pinHash/imageHash equal, targetScopeabove, profileRestabove. This full-profile targetScope no longer spans observer join/close. No identity/API/cause/countfix or cross-profile inference follows. Guardrefused/uploadskipped/artifacts empty; remaining33/native34 unproved. Logs `/tmp/factory-full-creator-41804985008-{job,failed}.log`. One result spent; no retry/admission.

Next Windows frontier: bounded READ-ONLY documented own-process handle-attribution feasibility decision after the finite full-creator refusal. Assess primary Win32 contracts, including Process Snapshotting only if suitable, for distinguishing untracked retained objects while preserving original baseline/final count, truthful observer perturbation, bounded sanitized output and owned observer closure. Do not assume identity, atomicity, boundedness, rights or arbitrary-handle cleanup. No undocumented API, raw handle/PID/path dump, source edit, probe, native run or another lifetime guess is authorized. Handle identity/number/type/owner/API/cause remain unknown until separately established. Root dispatches after a slot frees; any later implementation/native experiment requires a new bounded release.

Source preservation and a normal completed profile do not identify untracked objects or establish any new scaffold-fault behavior. The original strict count still governs; no admission or silent closure claim was added.
