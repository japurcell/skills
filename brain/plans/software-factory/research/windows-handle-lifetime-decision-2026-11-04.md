# Windows owned-image handle-count decision

2026-11-04 UTC. Historical read-only decision, subsequently accepted by root for one bounded qualification-only implementation and native experiment. Current state is maintained in [ExecPlan](../ExecPlan.md) and [handoff](../handoff.md). Source inspected: `f3f08fb2451547f6c5d7c474017ea19a6f920155`, private worktree `/private/tmp/factory-windows-native-case-refusal`. Integration observed at `18b80448f2caf5d89dbfe200b8d45e9f7705383a`. No repository/source changes, probes, builds, tests, native execution, providers or credential inspection occurred. Only this memo was written.

## Decision

Select **(a), one bounded phase-relation diagnostic on the existing creator thread**. Preserve the original baseline, final query and strict zero-increase assertion. Collect a finite set of same-process count observations, including paired boundaries around both hash scopes and the complete target lifetime. This is the smallest justified next experiment because it changes observation points without changing the creator/debugger-thread lifetime or original API order.

It can localize an aggregate increase to a source interval and observe whether it survives existing resource releases. It cannot identify a handle, prove a leak, distinguish undocumented implementation state from a missing close, or establish that a particular API caused an increase. No concrete repair is proven. Defer (b), the owned debugger-thread lifetime candidate, until this evidence supports a specific lifetime question; do not present that candidate as a documented cure.

## Retained native fact

Run `41779606825`, job `126407912754`, at `9fdc2307`, reached profile inbox/available/ready, then first positive case refused with a valid46-state record: clear/none; cleanup=false; survival/flush/close=true; countQuery=true; countNonincrease=false; leakedZero=false; ownedZero=true; closed/closeCalls/closeQuery=true. All other reached contributors passed. Guard refused and no artifact was admitted. Retain `/tmp/factory-cleanup-contributors-41779606825-failed.log`, especially its sanitized failure at line13.

This establishes that the successful final query reported more open process handles than the original baseline, despite all tracked closes succeeding and the owned counter being zero. It does not establish the amount, type, owner or lifetime of the additional handles. The record has closeIdentity/debugClose not-reached: no manual retired-debug-handle close or identity check was reached; the accepted retired-handle query alone is not a handle inventory.

## Primary contracts and exact source

- [GetProcessHandleCount](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-getprocesshandlecount) provides an aggregate of open handles belonging to the specified process. It does not supply identities or an ownership breakdown. [Kernel Objects](https://learn.microsoft.com/en-us/windows/win32/sysinfo/kernel-objects) describes kernel handles as process-specific. An aggregate increase is therefore insufficient to name an object or assign its creator. The original before query is [probe.cpp:487](/private/tmp/factory-windows-native-case-refusal/packages/software-factory/qualification/windows-owned-image-probe.cpp:487); final query/calculation is [probe.cpp:554](/private/tmp/factory-windows-native-case-refusal/packages/software-factory/qualification/windows-owned-image-probe.cpp:554).
- [BCryptCreateHash](https://learn.microsoft.com/en-us/windows/win32/api/bcrypt/nf-bcrypt-bcryptcreatehash) requires destroying the returned hash handle and documents that its optional internally allocated hash-object memory is freed by destruction. [BCryptDestroyHash](https://learn.microsoft.com/en-us/windows/win32/api/bcrypt/nf-bcrypt-bcryptdestroyhash) destroys that object. [BCryptOpenAlgorithmProvider](https://learn.microsoft.com/en-us/windows/win32/api/bcrypt/nf-bcrypt-bcryptopenalgorithmprovider) loads/initializes a provider; [BCryptCloseAlgorithmProvider](https://learn.microsoft.com/en-us/windows/win32/api/bcrypt/nf-bcrypt-bcryptclosealgorithmprovider) closes the provider. None of these contracts promises a particular executive-handle count before/after this sequence, or equates one CNG handle to one process-count unit. The positive path opens/creates, hashes, destroys, then closes at [probe.cpp:283](/private/tmp/factory-windows-native-case-refusal/packages/software-factory/qualification/windows-owned-image-probe.cpp:283), with checked destruction/close at lines307-308. Its current reported checks passed. The provider-only warmup at [probe.cpp:482](/private/tmp/factory-windows-native-case-refusal/packages/software-factory/qualification/windows-owned-image-probe.cpp:482) does not prove a cache explanation; its comment is not a Microsoft lifetime guarantee. Preserve it unchanged and do not add warmup to hide the failed count.
- [WaitForDebugEvent](https://learn.microsoft.com/en-us/windows/win32/api/debugapi/nf-debugapi-waitfordebugevent) restricts collection to the thread that created the debuggee. It specifies automatic process/thread event-handle closure after the relevant continued exit event, and caller closure of image/DLL file handles. [Debugging Events](https://learn.microsoft.com/en-us/windows/win32/debug/debugging-events) describes those exit-event semantics. [DebugActiveProcessStop](https://learn.microsoft.com/en-us/windows/win32/api/debugapi/nf-debugapi-debugactiveprocessstop) promises stopping debugging; it does not promise restoration of the debugger process's handle count. The positive path duplicates/closes the reported image file at [probe.cpp:388](/private/tmp/factory-windows-native-case-refusal/packages/software-factory/qualification/windows-owned-image-probe.cpp:388), detaches then runs the existing retired-handle checks at [probe.cpp:411](/private/tmp/factory-windows-native-case-refusal/packages/software-factory/qualification/windows-owned-image-probe.cpp:411). Explicit creator handles, pipes, mappings and pins are released at [probe.cpp:269](/private/tmp/factory-windows-native-case-refusal/packages/software-factory/qualification/windows-owned-image-probe.cpp:269). No omitted close on this observed clear positive path is proven by these sources.
- [DebugSetProcessKillOnExit](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-debugsetprocesskillonexit) documents debugging connections associated with the calling thread and the default attached-debuggee termination on its exit. This justifies treating a fully owned creator thread as a possible future experimental lifetime boundary, not naming an internal object. [Thread termination](https://learn.microsoft.com/en-us/windows/win32/procthread/terminating-a-thread) and [ExitThread](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-exitthread) describe normal termination, signaling and thread-object lifetime; C++ should return normally for cleanup. They do not promise that exiting a thread closes every process-specific leaked handle. With this `/MT` C++ profile, [_beginthreadex](https://learn.microsoft.com/en-us/cpp/c-runtime-library/reference/beginthread-beginthreadex?view=msvc-170) supports a waitable owned handle that the caller must close and normal-return CRT cleanup. The existing special owner-loss case already has its own creator thread at [probe.cpp:449](/private/tmp/factory-windows-native-case-refusal/packages/software-factory/qualification/windows-owned-image-probe.cpp:449); it is not evidence that moving the ordinary positive path cures this failure.

## Options compared

| Route | What a result can establish | Decision |
| --- | --- | --- |
| (a) Finite phasewise count relations, original thread/profile | Exact aggregate relations at fixed boundaries; unchanged explicit-owned-handle scopes around both hash operations; whether an increase survives existing Stop/Release boundaries. No object identity or API causality. | Select next. Retains current lifetime and the strict failed assertion. |
| (b) Full original operation on an owned `_beginthreadex` creator, normal return, bounded join and caller handle close before original final query | A documented creator-thread lifetime boundary can be controlled. If the original total assertion then passes, that is an observation of a changed creator profile, not proof of a particular hidden handle or historical cause. | Defer. It changes thread/CRT/debugging lifetime together and can obscure the introduction interval. Documentation does not guarantee aggregate restoration. All debug creation, waiting, continuation and attached cleanup would have to stay on that creator, with no kill-policy change or forced thread termination. |
| (c) Close an actually omitted source-owned object | A source-proven ownership omission could justify a narrow fix with the original count assertion. | Not established on the observed clear path. Do not invent a close, close an unknown handle, or infer ownership from a count. |

## One proposed changed native experiment

After root accepts this design, implement qualification-only instrumentation. **Do not implement or run it under this read-only task.** Keep every existing native operation in its current relative order. Only add same-process `GetProcessHandleCount(GetCurrentProcess(), ...)` observations at the boundaries below. [GetCurrentProcess](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-getcurrentprocess) supplies a pseudo handle; no new real process handle, enumeration, `OpenProcess`, duplication, undocumented API or foreign-process query is required.

Capture each result once. Keep new raw counts only in bounded in-memory slots. Do not log them, print deltas, introduce comparison offsets, replace the baseline, change current close/cleanup policy, retry a failed query, wait for a count to settle, or extend any bound. Do not output the new row until after the original final measurement and failed return decision. A diagnostic query failure means unavailable evidence, never a zero count or an inferred relation.

The original baseline is slot0 and must reuse its existing query result at line487. The final slot must reuse the original query at line554, not a second sample. Add15 queries for slots1-15:

| Slot | Fixed boundary | Existing source anchor |
| --- | --- | --- |
| 1 `entry-output` | After first OWNED stdout row, before control creation; no tracked child/control handles yet. | 493 |
| 2 `control-ready` | After the existing ready/marker requirement. | 500 |
| 3 `pin-hash-enter` | In first Identify, after existing file information/size/position checks, before CNG open. | 289 |
| 4 `pin-hash-leave` | After that hash destroy/provider close, before Require/logging. | 308 |
| 5 `debug-create-enter` | Before existing target Child.Create. | 366 |
| 6 `debug-create-leave` | After Child.Create returns, before first event wait. | 366 |
| 7 `first-event` | After the created barrier, with the first event pending. | 378 |
| 8 `image-hash-enter` | Same Identify entry boundary for actual held image; explicit suspension/event state unchanged. | 289, called at392 |
| 9 `image-hash-leave` | Same Identify exit boundary for actual held image. | 308, called at392 |
| 10 `continued` | After the continued barrier, before detach. | 408 |
| 11 `detached` | After existing detach and CloseDebugHandles, before postcondition query/resume. | 413 |
| 12 `probe-return` | After existing target exit query/zero check, before returning from Probe. | 440 |
| 13 `child-stopped` | After existing child.Stop. | 530 |
| 14 `control-stopped` | After existing control.Stop. | 543 |
| 15 `child-released` | Between existing child.Release and control.Release, without moving either. | 553 |
| 16 `final` | Original final query, after both Release calls. | 554 |

No new query consumes or continues a debug event, resumes a thread, or adds a wait. Queries use the existing paused boundaries: the source keeps the target stopped at first-event, image-hash, continued and detached checkpoints; completed Stop boundaries are quiescent on the retained positive path. Keep all earlier Stop/identity/marker/deadline/cap checks authoritative. A new observation can still perturb timing or implementation state; neither the API contract nor a phase map proves otherwise.

### Exact finite wire proposal

Append one recognized row only to an existing validated cleanup-refusal observation whose original final query succeeded and reported increase:

    OWNED_IMAGE_HANDLE_PHASES<TAB>1<TAB><exact-case><TAB><16 checkpoint tokens><TAB><4 pair tokens><LF>

Fields are positional in the exact table order, with one token per checkpoint relative to slot0: `b` below, `e` equal, `a` above, `f` query failed, `n` not reached. Four further tokens compare slots3->4,8->9,2->15,1->16 directly: `b|e|a`, or `u` unavailable if either endpoint is failed/not-reached. These are comparisons, never arithmetic offsets or acceptance conditions. The two hash pairs retain the same explicit held-handle set. Slots2->15 retain the explicit control handles while the target's owned objects are created/released; the control's liveness changes, so this remains interval evidence. Slots1->16 separates the entry-output boundary observationally; **it does not replace or subtract from slot0**.

All tokens, field counts, case/context and point order are closed. The total existing refusal+cleanup+phase record remains bounded by512 bytes using single-character tokens. Public formatting expands only fixed phase names and fixed relation labels. No count, difference, object type, handle, PID, path, argv, error/message, environment or operational output is exported.

Validate atomically with the existing refusal/46-state row and native exit1/no-signal/no-cap/no-timeout context. The final token must be `a` and agree with countQuery=true/countNonincrease=false. Query-failed/not-reached states cannot carry known comparisons; pair availability and any logically forced relation must agree with endpoint states. Reject unknown versions, duplicate/extra/missing/truncated/oversized rows, raw values, accessor/forged contexts and contradictions to fixed unknown. A bare older record remains recognized with this new evidence unknown. No relation permits artifact admission or discards the actual failing result.

### Proof and stopping criteria for the later implementation

1. Preserve native34 and the original45/53 tests byte-for-byte, adding focused portable real-owned-child wire/projection/guard controls. Require deterministic RED/GREEN for the new row and inconsistent/unknown framing, with zero skipped controls. Compare original API call order after excluding only the new documented count queries; preserve both original measurement sites, final predicate, bounds, successful stdout/stderr, pins/origin/signature, Stop/Release order and success validator/artifact grammar.
2. Coordinator runs exactly one changed exact-head native experiment after clean handback. A useful reproduction retains original first-positive count increase and a complete coherent phase row. Publish only finite observations; retain every failed result and guard refusal. Any missing query/row, interruption, cap, timeout, changed failure seam or failure to reproduce is incomplete/inconclusive for origin, with no blind retry.
3. Interpret an increase across a hash pair as retention across that whole scoped sequence, not proof of a CNG object leak. Interpret a surviving increase across the target scope as untracked process state retained across that interval, not a named debugger object. Even a later return to baseline identifies an observed lifetime interval only. If instrumentation removes the failure or all34 eventually pass, do not call it a historical repair or infer why. The original zero-increase assertion remains decisive at slot16.
4. Stop after the single result. Root chooses a separately bounded follow-up: a documented owned creator-thread lifetime candidate only if the observed interval supports that question, or a source fix only after ownership/closure is actually proven. No provider, helper/product admission, namespace/closure/Node-equivalence claim, publication or policy relaxation follows.

## Unresolved facts

The additional handles' identity, number, exact creating operation and lifetime remain unknown. The primary contracts inspected do not identify them, promise aggregate restoration after CNG or detach, or justify an undocumented debug-object/type claim. No third-party Windows implementation was used as an equivalence argument. The original native failure remains the controlling evidence.


## Observed single phase experiment

The authorized run41785489720/job126426550884 at92c96edf completed06:26:56UTC with failure. The60 protocol checks and fixed inbox/available/ready profile passed. First positive case returned native1/nonempty stderr, none/clear, cleanup=false and survival/flush/close=true. The successful final count query again reported increase; explicit owned-zero and all reached close contributors passed.

The coherent phase row reports entry-output equal to baseline and every later checkpoint above baseline. Both hash enter/leave pairs are equal; target-scope and entry-output-to-final are above. These are aggregate interval relations only: no handle count/identity, API/OS cause, leak/cache explanation or historical repair is established. The original failed assertion remains decisive. Guard refused, upload skipped and artifact inventory is empty. Fixed two-line evidence: `/tmp/factory-handle-phases-41785489720-failed.log`; complete job: `/tmp/factory-handle-phases-41785489720-job.log`.

The one experiment is spent. Creator-thread lifetime changes remain a separately authorized task; there is no retry, policy adjustment,34-case acceptance, namespace/closure/Node-equivalence or helper/product admission from this result.
