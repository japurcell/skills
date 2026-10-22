# Prove bounded Windows ETW process observation

This ExecPlan follows `.agents/skills/exec-plans/SKILL.md`. It covers only T17-Windows-ETW-probe at base `98587dedd35d04dd6c6f0becd6595e799e735c93`.

## Purpose / Big Picture

Run one short, ordinary pinned Node process with a known transient Node child on a disposable Windows runner. An owned ETW system-logger session must record true process starts and ends and image loads before a future independent comparator is considered. The raw ETL is parsed offline on the runner and removed before artifact upload; bounded receipts make failures inspectable. This probe makes no claim about the Git/TypeScript matrix or product admission.

## Progress

- [x] (2026-10-22) [milestone-1] Read the differential, exact plan scope, existing bootstrap/trace workflow and Microsoft ETW/TDH contracts.
- [x] (2026-10-22) [milestone-1] Public CLI/protocol checks fail before implementation and now pass for malformed health, unsupported host and valid fixture shape.
- [x] (2026-10-22) [milestone-1] Implement the bounded native ETW session, known Node child and finalized offline decode; local PowerShell 7 compilation and 64-bit managed layout check pass.
- [x] (2026-10-22) [milestone-1] Add isolated Windows workflow; Node syntax, three protocol tests and actionlint pass locally.
- [ ] [milestone-1] Run native Windows proof at the exact candidate commit; parent owns push and native run.

## Milestone 1: Native feasibility

Status: in progress
Acceptance: not met

The probe starts a descriptively named, uniquely owned file-backed system logger with process and image-load flags. It queries the session before launching pinned Node, keeps the root process handle and identity, waits within a 30-second observation limit, queries and stops only its own session, and processes the finalized ETL through OpenTrace/ProcessTrace and TDH. The sequential ETL is capped at 64 MiB. Any API failure, loss counter, cap, missing final EndTime, missing known start/end/image, schema failure or uncertain cleanup reports failure or inconclusive. It never reports absence of unrelated children.

The public seam is the Node CLI/report validator. It rejects malformed or incomplete native receipts and accepts a fully specified synthetic receipt, but synthetic input is never accepted as native proof. Native acceptance requires the Windows workflow receipt and independent review of the exact runner outcome. The C# bridge uses legacy PowerShell 5.1 Add-Type with only inbox APIs and no NuGet package.

## Surprises & Discoveries

The repaired native debug run still records an extra console host for detached nested cmd. The root launch context changes observed behavior. The existing debugger is therefore not an absence oracle for this feasibility gate.

Automatic approval review rejected uploading raw ETL to GitHub because it can include ambient system process metadata; existing workflow authorization did not cover that disclosure. The safe workflow retains only bounded allowlisted receipts and removes `trace.etl` locally after parsing, with an always-run cleanup step before upload. Native evidence loses independent raw replay; the first hosted run can establish only the selected field/health positive control and should be reviewed with that limit.

## Decision Log

- 2026-10-22: Stop after the smallest native rights/schema/health and known-child positive-control probe. The full comparator is a later task.
- 2026-10-22: Treat actual Windows API/schema behavior as unverified until the parent runs the workflow. Official docs define the contracts, not runner success.
- 2026-10-22: Never publish raw ETL under current authorization. Keep its scope to an ephemeral runner file, parse it there, remove it and upload only `bootstrap.json`, `qualification.json` and `native.tsv`.

## Context, validation and recovery

Files are under `packages/software-factory/qualification/windows-etw-probe*` plus `.github/workflows/windows-factory-etw-probe.yml`. Run `node --test packages/software-factory/qualification/windows-etw-probe.test.mjs` locally. On Windows, the separate workflow bootstraps the exact Node archive from `runtime-manifest.json`, invokes the probe, removes the raw ETL and always uploads only bounded JSON/TSV evidence. It does not edit existing qualification or product paths. If native start/query/schema fails, preserve API codes in the receipt, stop only the successfully created session and halt before building the comparator. Retry only in a fresh disposable run after diagnosis. Local checks on 2026-10-22: three public tests pass under the exact local Node v24.22.1, C# compiles under PowerShell 7 on macOS arm64, the 64-bit managed layout check passes, Node syntax and actionlint pass. Windows PowerShell 5.1 compilation and every native ETW result remain unverified.

## Outcomes & Retrospective

Candidate implementation is locally checked; native acceptance remains open. Parent owns candidate review, push, and the first hosted Windows run. Reflection found no separate brain write needed within this worker's scoped ownership: the ETW artifact disclosure decision is preserved in this qualification note, and the ABI, loss and positive-event lessons are encoded in runtime checks and public tests.
