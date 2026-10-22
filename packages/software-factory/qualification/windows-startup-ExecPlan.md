# Qualify exact Windows startup helpers

This ExecPlan is a living qualification spike. It follows `.agents/skills/exec-plans/SKILL.md` and is confined to `packages/software-factory/qualification/windows-startup*` plus `.github/workflows/windows-factory-startup.yml`.

## Purpose / Big Picture

Produce reviewable native evidence for four exact Git metadata invocations and direct TypeScript 7.0.2 compilation. A Windows debug launch trace must show every process creation and actual module path, including a positive child control. Source review and Mac checks are preparation, not native acceptance. Production helper admission and runtime edits are outside this spike.

## Progress

- [x] (2026-10-22) [milestone-1] Pin official artifact identities and define disposable fixtures and trace protocol in `windows-startup-artifacts.mjs` and `windows-startup-qualification.md`.
- [x] (2026-10-22) [milestone-1] Implement the debug launcher, positive child control, direct stop control, and structured failure evidence.
- [ ] [milestone-1] Observe the positive child, module paths, and direct stop on a native Windows runner at the reviewed SHA.
- [x] (2026-10-22) [milestone-2] Assemble fixed Git/compiler cases, hostile config, package tampering refusal, and bounded output control.
- [x] (2026-10-22) [milestone-2] Validate local JavaScript/PowerShell/C# syntax, Node contracts, offline archive hashes, and workflow lint.
- [ ] [milestone-2] Run the manual Windows workflow after parent review and push; retain and inspect all native evidence.

## Surprises & Discoveries

- The actual Windows foundation run 39810180199 reports `startup Git probe cleanup unknown; manual inspection required` in `/tmp/factory-foundation-39810180199-failed.log`; exit and stream closure cannot imply no descendants.

## Decision Log

- 2026-10-22: Use `DEBUG_PROCESS` on the one owned test helper. The Windows Debug API reports process creation for debugged descendants and DLL loads. This is a qualification-only instrument, not product containment. Fail closed if event handling, module resolution, or completion is uncertain.
- 2026-10-22: Bind the official MinGit archive, its native `mingw64/bin/git.exe` and all imported non-system DLLs; bind the compiler package archive, `tsc.exe`, and adjacent package libraries. Do not claim exact source-to-binary equivalence from release hashes or source audit.

## Outcomes & Retrospective

The qualification-only source and manual workflow are locally prepared. The Mac checks confirm source syntax, exact archive bytes/inventory, contract validation, and workflow structure, but cannot execute the Windows debug event loop or helpers. Native acceptance remains pending parent review/push and retained hosted evidence. No production behavior is qualified or promoted by this plan alone.

Reflection reviewed `brain/index.md` and the session. The Windows-specific facts are captured in this qualification record and enforced by the exact-mode assertions; no durable cross-cutting brain or skill edit is needed.

## Context and Orientation

The accepted research lives in `docs/software-factory/research/windows-startup-{feasibility-2026-10-22,artifacts-2026-10-21,source-audit-2026-10-21}.md`. The selected Git source commit is `2b8a3ab140826ac423c2845ef81d4c6ac4f7bf3c`; TypeScript source commit is `2bd066d87f5bafd315be9f40889d0a60b9e58e0b`. The package's existing foundation workflow supplies CI bootstrap patterns. All repositories/configuration are created under a disposable job directory.

## Plan of Work

### Milestone 1: Exact launch evidence

Status: in progress
Acceptance: not met

Create a Windows-only trace launcher under `qualification/windows-startup*` that launches an absolute executable path with fixed arguments, private environment, and cwd. It records root/descendant creation and loaded module paths through Windows debug events. A deliberately spawned child must be observed before the no-child interpretation is trusted. Unknown debug event state or timeout fails qualification.

### Milestone 2: Closed-mode matrix and CI evidence

Status: in progress
Acceptance: not met

Use the trace launcher to exercise four Git metadata modes and direct `tsc.exe -p <generated-config>`. Include linked/unborn/reftable/wrong registrations; hostile disposable config/env canaries; compiler evil source/authored config text; success/error/no-output/one-build; binary/DLL/library tampering; and cancellation/output bounds. Create a read-only, manually dispatched Windows Actions workflow with immutable action SHAs and always-retained structured artifacts. Native workflow execution requires parent review and push.

## Concrete Steps

The next action is to add a failing fixture contract for the trace record, then the smallest launcher that satisfies it. Add matrix cases after the positive control. Run syntax and local contract checks on Mac; leave native claims pending.

## Validation and Acceptance

On Windows, the positive control must produce a `CREATE_PROCESS_DEBUG_EVENT` for a child of its root. Each fixed Git/compiler case must have no child creation events, exact recorded argument/cwd identity, expected output/status, and module paths inside the pinned archive or Windows system directories. Any missing event, timeout, unrecognized module, mismatch or canary execution fails. On Mac, only schema and source checks can pass.

Observed locally on macOS with Node v24.21.0: `rtk test node --test packages/software-factory/qualification/windows-startup.test.mjs` passed 2/2; `node --check` passed for the three new JavaScript modules; PowerShell 7 parsed `windows-startup-trace.ps1` and `Add-Type -Path windows-startup-trace.cs` compiled; `windows-startup-artifacts.mjs --offline` verified the two previously downloaded exact archives and extracted every member under `/tmp/factory-windows-startup-artifacts-local`; `actionlint 1.7.12` accepted the new workflow. The Windows-only driver refused local execution and wrote an explicit `native qualification requires Windows` result. None of these observations establishes native trace behavior.

## Idempotence and Recovery

All downloads and fixtures belong to the Actions temporary directory; hash them before extraction/use. Rerunning creates fresh directories and keeps prior uploaded logs. On interruption, terminate only exact debugged processes; record uncertainty and fail. No product-state repair or global configuration change is attempted.

## Interfaces and Dependencies

Windows PowerShell's `Add-Type` compiles the C# Win32 debug P/Invoke launcher on the hosted Windows runner. The Node 24 package script assembles fixtures and checks JSON traces. Git/TypeScript archives are fetched only by explicit CI qualification steps from exact official release assets, with pinned SHA256. No runtime dependency is added to the factory product.
