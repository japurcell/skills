# Prove bounded Windows ETW process observation

This ExecPlan follows `.agents/skills/exec-plans/SKILL.md`. It covers only T17-Windows-ETW-probe at base `98587dedd35d04dd6c6f0becd6595e799e735c93`.

## Purpose / Big Picture

Run one short, ordinary pinned Node process with a known transient Node child on a disposable Windows runner. An owned ETW system-logger session must record true process starts and ends and image loads before a future independent comparator is considered. The raw ETL is parsed offline on the runner and removed before artifact upload; bounded receipts make failures inspectable. This probe makes no claim about the Git/TypeScript matrix or product admission.

## Progress

- [x] (2026-10-22) [milestone-1] Read the differential, exact plan scope, existing bootstrap/trace workflow and Microsoft ETW/TDH contracts.
- [x] (2026-10-22) [milestone-1] Public CLI/protocol checks fail before implementation and now pass for malformed health, unsupported host and valid fixture shape.
- [x] (2026-10-22) [milestone-1] Implement the bounded native ETW session, known Node child and finalized offline decode; local PowerShell 7 compilation and 64-bit managed layout check pass.
- [x] (2026-10-22) [milestone-1] Add isolated Windows workflow; initial Node syntax, protocol and actionlint checks pass locally.
- [ ] [milestone-1] Run native Windows proof at the exact candidate commit; parent owns push and native run.
- [x] (2026-10-22) [milestone-1] T1: Reproduced foreign same-basename acceptance; fixed labels now follow exact pinned path and process lifetime checks. Public negative is green.
- [x] (2026-10-22) [milestone-1] T2: Reproduced missing unsupported-host JSON; fixed stage/code reports and native numeric error rows are in place. Public CLI negative is green.
- [x] (2026-10-22) [milestone-1] T3: Reproduced oversized/path-bearing artifact exposure; producer byte cap and upload scrub are in place. Public negatives and direct C# overflow proof are green.
- [x] (2026-10-22) [milestone-1] T4: Reproduced raw bootstrap path/error exposure through public `--prepare-artifacts`; isolated operational bootstrap from staged uploads and suppressed bootstrap console output. Injected-data negative is green.
- [x] (2026-10-22) [milestone-1] Integrated local eight-case protocol, Node syntax, actionlint and PowerShell 7 ABI/producer checks passed after T1-T4.

## Milestone 1: Native feasibility

Status: in progress
Acceptance: not met

The probe starts a descriptively named, uniquely owned file-backed system logger with process and image-load flags. It queries the session before launching pinned Node, keeps the root process handle and identity, waits within a 30-second observation limit, queries and stops only its own session, and processes the finalized ETL through OpenTrace/ProcessTrace and TDH. The sequential ETL is capped at 64 MiB. Any API failure, loss counter, cap, missing final EndTime, missing known start/end/image, schema failure or uncertain cleanup reports failure or inconclusive. It never reports absence of unrelated children.

The public seam is the Node CLI/report validator. It rejects malformed or incomplete native receipts and accepts a fully specified synthetic receipt, but synthetic input is never accepted as native proof. Native acceptance requires the Windows workflow receipt and independent review of the exact runner outcome. The C# bridge uses legacy PowerShell 5.1 Add-Type with only inbox APIs and no NuGet package.

## Surprises & Discoveries

The repaired native debug run still records an extra console host for detached nested cmd. The root launch context changes observed behavior. The existing debugger is therefore not an absence oracle for this feasibility gate.

Automatic approval review rejected uploading raw ETL to GitHub because it can include ambient system process metadata; existing workflow authorization did not cover that disclosure. The safe workflow retains only bounded allowlisted receipts and removes `trace.etl` locally after parsing, with an always-run cleanup step before upload. Native evidence loses independent raw replay; the first hosted run can establish only the selected field/health positive control and should be reviewed with that limit.

An approval review also rejected a draft that would have written the pinned executable path into the uploaded `ROOT` row. The repaired producer writes a fixed label after comparing the held handle's full image with the pin in memory. It emits no TDH path or exception message, even on failure. Microsoft documents process `ImageFileName` as a path and image-load `FileName` as a file name; exact full-path verification may therefore fail on a native runner. That is an unresolved feasibility result, not permission to fall back to a basename.

Independent follow-up review found that the shared bootstrap producer writes runner paths and arbitrary errors to its local JSON and console output. A public `--prepare-artifacts` invocation initially returned success while leaving the raw bootstrap file in the upload set. The repair retains that operational file for pin verification, but stages an explicitly reconstructed qualification summary and validated native TSV in a separate `upload/` directory. Workflow upload paths name only those staged files. The bootstrap step suppresses native stdout/stderr and emits a fixed failure stage/code. Approval review rejected an attempted deletion of operational bootstrap and an attempted whole-object copy into the summary; both were replaced with the local operational receipt and explicit field construction.

## Decision Log

- 2026-10-22: Stop after the smallest native rights/schema/health and known-child positive-control probe. The full comparator is a later task.
- 2026-10-22: Treat actual Windows API/schema behavior as unverified until the parent runs the workflow. Official docs define the contracts, not runner success.
- 2026-10-22: Never publish raw ETL under current authorization. Keep its scope to an ephemeral runner file, parse it there and remove it before upload.
- 2026-10-22: Keep raw bootstrap local for exact pin verification. Suppress its untrusted console output and upload only an explicit bounded qualification summary and validated native TSV from `upload/`. Reconstruct each summary field, never copy source objects or free text.
- 2026-10-22: The independent review found that selected TDH paths and free-text errors cross the artifact boundary. The native producer must verify the exact pinned module path and known process lifetime before producing fixed event labels. Ambiguous NT paths, PID reuse and missing identity fail closed. The Node validator accepts only controlled labels. C# and Node errors use fixed stage/code values. A 65 KiB byte cap applies before native TSV persistence and again before artifact upload.
- 2026-10-22: Keep `ROOT` and event image values as fixed `pinned-node` labels. Native exact-path comparison and held root handle establish the label; the public synthetic protocol alone cannot prove native identity. Skip artifact upload unless both ETL cleanup and receipt preparation succeed.

## Context, validation and recovery

Files are under `packages/software-factory/qualification/windows-etw-probe*` plus `.github/workflows/windows-factory-etw-probe.yml`. Run `node --test packages/software-factory/qualification/windows-etw-probe.test.mjs` locally. On Windows, the separate workflow bootstraps the exact Node archive from `runtime-manifest.json`, invokes the probe, removes the raw ETL and uploads only staged `upload/qualification.json` and `upload/native.tsv` when cleanup and artifact validation succeed. The raw bootstrap receipt stays local for pin verification. It does not edit existing qualification or product paths. If native start/query/schema fails, preserve API codes in the receipt, stop only the successfully created session and halt before building the comparator. Retry only in a fresh disposable run after diagnosis. Local checks on 2026-10-22: eight public tests pass under the exact local Node v24.22.1, C# compiles under PowerShell 7 on macOS arm64, the 64-bit managed layout and producer overflow checks pass, Node syntax and actionlint pass. Windows PowerShell 5.1 compilation and every native ETW result remain unverified.

### Repair tasks and local acceptance

T1 prerequisite: the existing positive fixture and review's same-basename foreign image reproducer. Update `windows-etw-probe.test.mjs` first so foreign or missing identity fails and a fixed-label positive succeeds. Then change `windows-etw-probe.cs` event selection to retain only controlled numeric and label data in memory, verify exact pinned module path and root/child start/end lifetime before emitting any event rows, and reject ambiguous reuse. Update the Node parser to reject path-bearing event rows. Preserve the schema, known positive events, final header and loss checks.

T2 prerequisite: unsupported-host CLI repro. Extend the public test to require `qualification.json` with fixed stage/code and no untrusted strings. Make every Node catch, bridge and native `FAIL` row structured and bounded. Keep host and bootstrap pin guards before native calls. Verify cleanup failure changes status and cannot look like a successful stop.

T3 prerequisite: oversized fixture repro. Verify the Node validator refuses more than 65 KiB and the upload gate discards oversized TSV before `upload-artifact`. Add a native producer byte cap that replaces overflow with a small typed failure receipt, never with a pass. Run the three existing tests plus new negatives, Node syntax, actionlint, PowerShell 7 `Add-Type` and 64-bit `CheckAbi`. A local pass is not native Windows proof.

T4 prerequisite: invoke public `--prepare-artifacts` with a synthetic operational bootstrap containing an ambient path and arbitrary error. Assert every staged upload excludes both markers and the operational bootstrap remains available locally. Keep the bootstrap failure wrapper's console text fixed, and preserve prior byte, grammar, cleanup and native positive-event gates.

## Outcomes & Retrospective

Candidate review and follow-up privacy repairs are locally checked; native acceptance remains open. Parent owns independent review, push, and the first hosted Windows run. Reflection found no separate brain write needed within this worker's scoped ownership: the artifact boundary and exact-path feasibility risk are preserved in this qualification note, and the ABI, loss, positive-event and byte-bound lessons are encoded in runtime checks and public tests.
