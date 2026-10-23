# Prove bounded Windows ETW process observation

This ExecPlan follows `.agents/skills/exec-plans/SKILL.md` and the canonical `docs/software-factory/ExecPlan.md`. It covers only known Node/child ETW feasibility. The user requires all remaining reviews after all implementation tasks; provider qualification stays blocked and live desktop notifications stay last.

## Purpose / Big Picture

Prove that one disposable Windows session records the actual pinned Node root and known child, with independently held process/file identities, six positive events and finalized loss-free health. Remove raw ETL before publishing bounded sanitized evidence. This gate precedes a separately designed Git/TypeScript observational comparator and never admits product helper or arbitrary descendant absence.

## Progress

- [x] (2026-10-22) [milestone-1] Implement exact session/query/mode, bounded capture/offline decode and sanitized artifact protocol; repair previously reviewed privacy and cleanup findings.
- [x] (2026-10-22) [milestone-1] Reproduce actual name-only event fields and implement independently held pin/root/child identity plus safe control handshake.
- [x] (2026-10-22) [milestone-1] Reproduce redirected stdin preamble, initialized-child readiness and distinct exit/End timing; retain strict protocol and measured lifetime association.
- [x] (2026-10-22) [milestone-1] Native39881631722 at5e8d5b81 passes held positive/foreign rejection, six events and finalized zero-loss health; raw ETL removed.
- [x] (2026-10-22) [milestone-1] Parent24portable protocol/CI checks and C# compile/ownership/four cleanup fault checks pass, zero skips.
- [ ] [milestone-1] Complete final independent review after every implementation task in the canonical plan finishes; repair findings and rerun affected native proof if necessary.

## Surprises & Discoveries

Process ImageFileName is name-only on the actual runner, so it cannot prove a full file identity. Complete main-image paths match DOS/NT paths obtained from the held file. Framework redirected stdin can emit an encoding preamble before explicit release; starting with UTF8(false) and writing raw0x52 preserves the one-byte fixture contract. Child ETW End can follow exit FILETIME; distinct observations require a measured release-to-signaled-exit bracket rather than equality or an arbitrary grace interval.

## Decision Log

Keep the pinned file and both verified process handles held through offline decode. Process names supply consistency only; event keys, held lifetimes/parent and complete OS-returned image paths establish the known-fixture association. Event-controlled paths never authorize local opens. Keep exact query/mode, all six events, finalized header/zero loss and all caps. Native green remains review-required. Transient Git/TS processes need a separate feasibility decision because a delayed offline decoder cannot recover a missed live process handle.

## Outcomes & Retrospective

Known-fixture implementation and native proof pass at5e8d5b81/run39881631722. Final review remains pending by explicit user direction. No Git/TypeScript comparator, native helper, product Windows startup support or general no-child claim is accepted. Earlier failed receipts and review evidence remain in the verified historical snapshot.

## Context and Orientation

`qualification/windows-etw-probe.cs` owns C#5-compatible Windows PowerShell5.1 ABI/session/fixture/offline decode. `windows-etw-probe.ps1` is the bounded bridge. `windows-etw-child-fixture.cjs` owns K readiness and R release. `windows-etw-probe.mjs` exposes the native command, public receipt validator and upload preparation. `windows-etw-probe.test.mjs` tests public protocol/privacy/control behavior. `windows-etw-held-native.qualification.mjs` separately proves positive held identities and rejection of a foreign same-Node PID. `.github/workflows/windows-factory-etw-probe.yml` bootstraps exact Node24.22.1 and runs the two native controls on windows-2025.

## Plan of Work

### Milestone 1: Known fixture and finalized trace
Status: in progress
Acceptance: not met

Implementation/native proof is complete. Parent owns final review after all canonical implementation tasks finish. Acceptance requires no remaining review findings plus native held pin/process identity, exact keys/parents/lifetimes, all six events, exact session/query/mode, finalized loss-free header, retained caps and safe cleanup/privacy. Functional native proof is now recorded; deferred review is not silently waived.

The current native result records SESSION37748737/5/64, QUERYalltrue, MODE1/1/0/stop/0, everyAPI0, STATS0/0/0, COUNTS14174/6, positive HEADER with zero loss, six events and COMPLETE. Summary status is native-feasibility-passed-review-required. ETL3,014,656bytes was removed before the bounded two-file upload. Sanitized artifacts: `/tmp/factory-windows-etw-probe-39881631722/factory-windows-etw-probe-39881631722-1/`.

## Concrete Steps

No further review is authorized now. Continue canonical implementation tasks and the separate transient-child comparator design. At final review, evaluate current cumulative source and negative controls; do not substitute synthetic receipt passes for actual native proof. If source changes affect identity/lifetime/schema/health/cleanup, rerun the affected public checks and exact-head Windows workflow before claiming acceptance.

## Validation and Acceptance

From `packages/software-factory`, exact Node24.22.1 runs `node --test qualification/windows-etw-probe.test.mjs qualification/ci.test.mjs`: current24pass, zero skips. Public tests cover malformed/duplicate/missing positives, closed diagnostics, forged passing summaries, loss/final-header/mode/caps, byte privacy and safe failed artifact retention. Local logs `/tmp/factory-etw-exit-observation-protocol.log`, `-compile.log`, `-cleanup.log` supplement native Windows evidence. Local compilation does not establish Windows API behavior.

Native entry `node qualification/windows-etw-probe.mjs` requires pinned Windowsx64 Node24.22.1 and PowerShell5.1 after verified bootstrap. The held-only command is `node qualification/windows-etw-held-native.qualification.mjs`. Missing prerequisites fail. Workflow20minute job/12minute probe bounds do not imply trace completeness; internal observation remains30seconds, ETL64MiB and receipt65,536bytes. Every DIAG means failure. ETW End uses precise pre-release-to-signaled-exit bounds with actual exit inside; start/images stay within creation/exit. No grace interval or raw event path export is allowed.

## Idempotence and Recovery

Every run creates one new owned session and private evidence path. Never stop an unowned session or signal an unverified printed PID. Independently stop the launched root and positively parent-verified held child, retain the first error, close each resource unconditionally, then write only bounded fixed diagnostics. Always remove exact raw ETL before artifact upload; cleanup uncertainty fails and preserves available fixed evidence. A failed run never admits the route or changes product runtime behavior.

## Interfaces and Dependencies

Use documented Win32 ETW/TDH, GetProcessTimes, GetSystemTimePreciseAsFileTime, Toolhelp parent lookup, QueryFullProcessImageNameW, GetFinalPathNameByHandleW and FILE_ID_INFO. Keep exact paths and IDs in memory only. Published protocol exposes controlled PIDs, fixed labels/timestamps, closed schema/diagnostic categories, numeric API codes and health counters; no command lines, environment, raw paths or kernel pointer values. Primary references and current proof details are in `windows-etw-probe.md`.

## Historical Records

The verified [earlier ExecPlan snapshot](windows-etw-probe-ExecPlan.history-2026-10-22.md) preserves every original task, red/green log, review and failed native run before this reconciliation. The [earlier qualification note](windows-etw-probe.history-2026-10-22.md) preserves matching source contracts and failure diagnosis. Historical instructions never override current authorization, status or review timing.
