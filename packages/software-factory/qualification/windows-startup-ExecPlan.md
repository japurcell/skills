# Qualify exact Windows startup helpers

This ExecPlan is a living qualification spike. It follows `.agents/skills/exec-plans/SKILL.md` and is confined to `packages/software-factory/qualification/windows-startup*` plus `.github/workflows/windows-factory-startup.yml`.

## Purpose / Big Picture

Produce reviewable native evidence for four exact Git metadata invocations and direct TypeScript 7.0.2 compilation. A Windows debug launch trace must show every process creation and actual module path, including a positive child control. Source review and Mac checks are preparation, not native acceptance. Production helper admission and runtime edits are outside this spike.

## Progress

- [x] (2026-10-22) [milestone-0] Add the bounded private PowerShell baseline and per-case stage evidence to the always-uploaded directory.
- [x] (2026-10-22) [milestone-0] Confirm local missing-spec markers, `Add-Type` compilation, native-entry markers, Node contracts, and source checks.
- [ ] [milestone-0] Run the reviewed Windows workflow and inspect the retained baseline and stage file through the launcher timeout.
- [x] (2026-10-22) [milestone-1] Pin official artifact identities and define disposable fixtures and trace protocol in `windows-startup-artifacts.mjs` and `windows-startup-qualification.md`.
- [x] (2026-10-22) [milestone-1] Implement the debug launcher, positive child control, direct stop control, and structured failure evidence.
- [x] (2026-10-22) [milestone-1] Replace the PowerShell positive fixture with native `cmd.exe` and require the intended child image; prove the trace contract locally.
- [ ] [milestone-1] Confirm the exact `cmd.exe` child, module paths, and direct stop on native Windows at the reviewed SHA.
- [x] (2026-10-22) [milestone-2] Assemble fixed Git/compiler cases, hostile config, package tampering refusal, and bounded output control.
- [x] (2026-10-22) [milestone-2] Validate local JavaScript/PowerShell/C# syntax, Node contracts, offline archive hashes, and workflow lint.
- [x] (2026-10-22) [milestone-2] Add the scoped push trigger and per-case positive module validation with local contract proof.
- [ ] [milestone-2] Push reviewed scope to `codex/research-agentic-workflow-prototypes`, run the Windows workflow, and inspect retained native evidence.

## Surprises & Discoveries

- Native run 39824050563 at `3da96c9f` passed fixture preparation, then the positive control's outer `powershell.exe` hit the unchanged 75 second launcher limit. Its `spec.json` and empty launcher stdout/stderr survived, but no `debug.tsv`, `stdout.bin`, or `stderr.bin` exists. This proves only that native `Main` did not reach its first trace write; the stage before that point is unknown.
- The actual Windows foundation run 39810180199 reports `startup Git probe cleanup unknown; manual inspection required` in `/tmp/factory-foundation-39810180199-failed.log`; exit and stream closure cannot imply no descendants.
- The initial workflow used only `workflow_dispatch`, which cannot receive a manual event before the workflow is on the default branch. A path-filtered push trigger on the reviewed topic branch supplies a native run without changing the default branch.
- The first module validator accepted a complete trace with zero `DLL` rows, and the five Git imports were required only over the union of 16 cases. Each fixed-helper case now requires a resolved DLL row and every Git case requires all five imports.
- Native run 39821578705 at `c29c7765` passed archive and fixture preparation, but its PowerShell positive control timed out after 15 seconds. The retained trace has root `powershell.exe` PID 6640, incidental `conhost.exe` PID 4672, 100-plus DLL events, no `cmd.exe` event or output, followed by `STOP_REQUESTED deadline`, two `EXIT 124` events, and `DONE stopped:124`. That trace proves the intended `Start-Process` child was never observed. It does not isolate whether PowerShell startup, command discovery, or startup module loading consumed the deadline.
- The current positive validator accepts any descendant, so the incidental `conhost.exe` would satisfy it even if `cmd.exe` never launched. The repaired control must bind a child `CREATE` row to the exact intended `cmd.exe` image.

## Decision Log

- 2026-10-22: Add a diagnostic-only baseline for the same Windows PowerShell executable, private environment, and cwd, and append flushed stage timestamps from the wrapper and native entry into each case directory. Keep the existing positive child, deadline, output, and DLL assertions unchanged. The stage record is evidence, not a success condition.
- 2026-10-22: Use `DEBUG_PROCESS` on the one owned test helper. The Windows Debug API reports process creation for debugged descendants and DLL loads. This is a qualification-only instrument, not product containment. Fail closed if event handling, module resolution, or completion is uncertain.
- 2026-10-22: Bind the official MinGit archive, its native `mingw64/bin/git.exe` and all imported non-system DLLs; bind the compiler package archive, `tsc.exe`, and adjacent package libraries. Do not claim exact source-to-binary equivalence from release hashes or source audit.
- 2026-10-22: Keep the hostile include query as positive evidence for reading `core.fsmonitor`. Treat pager/filter/hook/credential/remote values and the unselected authored tsconfig as decoys until a fixture actually exercises them.
- 2026-10-22: Replace the PowerShell positive fixture with a native `cmd.exe /d /c` parent that invokes the absolute `cmd.exe /d /c exit 0` child. Keep the 15 second deadline, complete-exit checks, and output bound. Require a child event for that exact image. Microsoft's `cmd` reference defines `/d` as disabling AutoRun and `/c` as executing the command then exiting; Windows `DEBUG_PROCESS` reports descendant creation. This isolates the control from PowerShell startup while preserving genuine process creation.

## Outcomes & Retrospective

The qualification-only source and scoped push workflow are locally prepared. Native runs 39821578705 and 39824050563 both failed at the positive fixture, the latter before the first native trace write. The current diagnostic source records pretrace stages but has not run on Windows. Native acceptance remains pending parent review/push and retained hosted evidence. No production behavior is qualified or promoted by this plan alone. Detailed evidence is in `windows-startup-qualification.md`.

Reflection reviewed `brain/index.md` and the session. The new failure-stage evidence is specific to this qualification spike and is recorded here and in `windows-startup-qualification.md`; no durable cross-cutting brain or skill edit is needed.

## Context and Orientation

The accepted research lives in `docs/software-factory/research/windows-startup-{feasibility-2026-10-22,artifacts-2026-10-21,source-audit-2026-10-21}.md`. The selected Git source commit is `2b8a3ab140826ac423c2845ef81d4c6ac4f7bf3c`; TypeScript source commit is `2bd066d87f5bafd315be9f40889d0a60b9e58e0b`. The package's existing foundation workflow supplies CI bootstrap patterns. All repositories/configuration are created under a disposable job directory.

## Plan of Work

### Milestone 0: Identify the pretrace stall

Status: in progress
Acceptance: not met

Record whether the private PowerShell process can execute a minimal command, then record entry, spec read, `Add-Type` start/end, native call, native entry, and trace creation for the existing positive case. Preserve stage files and bounded error summaries after launcher timeout in the always-uploaded evidence directory. Local malformed-spec checks recorded `ps-entry` and `ps-error` before returning 4; a valid spec on macOS recorded all stages through `trace-create-end` before the expected unsupported native launch failed. The focused Node suite and JavaScript syntax checks passed. A Windows rerun is required to identify the actual stall.

### Milestone 1: Exact launch evidence

Status: in progress
Acceptance: not met

Create a Windows-only trace launcher under `qualification/windows-startup*` that launches an absolute executable path with fixed arguments, private environment, and cwd. It records root/descendant creation and loaded module paths through Windows debug events. A deliberately spawned exact `cmd.exe` child must be observed before the no-child interpretation is trusted. Unknown debug event state or timeout fails qualification.

### Milestone 2: Closed-mode matrix and CI evidence

Status: in progress
Acceptance: not met

Use the trace launcher to exercise four Git metadata modes and direct `tsc.exe -p <generated-config>`. Include linked/unborn/reftable/wrong registrations; a positively queried private config include and unexercised config decoys; compiler executable-looking source and an unselected authored-config decoy; success/error/no-output/one-build; binary/DLL/library tampering; and cancellation/output bounds. Create a read-only Windows Actions workflow with immutable action SHAs, a path-filtered topic-branch push trigger, manual dispatch for later use, and always-retained structured artifacts. Native workflow execution requires parent review and push.

## Concrete Steps

The public trace-validator test failed with a `conhost.exe` child and then passed after the exact-image check. The positive fixture still uses native `cmd.exe`. The local missing-spec check first failed because `-StagePath` was unknown, then produced `ps-entry` and `ps-error`; the valid-spec check compiled C# and recorded through `trace-create-end` before the expected non-Windows launch failure. The next owner action is independent review, then push the scoped diagnostic commit to `codex/research-agentic-workflow-prototypes`. Inspect the baseline result and `positive-child-control/launcher-stages.tsv` first, then the raw event trace, module paths, positive child, stop controls, and all helper outputs before native acceptance.

## Validation and Acceptance

On Windows, the positive control must produce a `CREATE_PROCESS_DEBUG_EVENT` for the expected absolute `cmd.exe` image with a PID distinct from its root and observed child exit. Incidental `conhost.exe` events do not satisfy this requirement. The positive control must finish with root status 0 within the original 15 second deadline and output bound. Each fixed Git/compiler case must have no child creation events, exact recorded argument/cwd identity, expected output/status, and at least one resolved module path inside the pinned archive or Windows system directories. Each Git case, including malformed registration, must observe all five pinned imported DLLs. Any missing event, timeout, unrecognized module, mismatch or canary execution fails. On Mac, only schema and source checks can pass.

The first repair test failed on macOS with `actual: true, expected: false`: the positive validator accepted a complete trace whose only child image was `conhost.exe`. After the exact-image check, `rtk test node --test packages/software-factory/qualification/windows-startup.test.mjs` passed, `node --check` passed for the three edited JavaScript modules, and `rtk git diff --check` passed, all on Node v24.21.0. Earlier macOS checks parsed `windows-startup-trace.ps1`, compiled `windows-startup-trace.cs` with PowerShell 7 `Add-Type`, verified both official archives offline, and linted the workflow. None of these observations establishes repaired native trace behavior. The actual run 39821578705 at `c29c7765` is the before-change Windows E2E failure; its trace and runner log are retained at the paths in `windows-startup-qualification.md`.

Current diagnostic checks on macOS with Node v24.21.0: `rtk proxy node --test packages/software-factory/qualification/windows-startup.test.mjs` passed 6/6 with no skips; `rtk proxy node --check` passed for the runner and test; `rtk git diff --check` passed. An actual `pwsh -File windows-startup-trace.ps1` missing-spec invocation returned 4 and left `ps-entry`/`ps-error`. A valid disposable spec compiled the C# source and left every marker through `trace-create-end`, then returned 4 on the unsupported native launch. These checks verify the diagnostic path on macOS, not Windows startup timing. The actual run 39824050563 at `3da96c9f` is the before-change native E2E failure for this diagnostic.

## Idempotence and Recovery

All downloads and fixtures belong to the Actions temporary directory; hash them before extraction/use. Rerunning creates fresh directories and keeps prior uploaded logs. On interruption, terminate only exact debugged processes; record uncertainty and fail. No product-state repair or global configuration change is attempted.

## Interfaces and Dependencies

Windows PowerShell's `Add-Type` compiles the C# Win32 debug P/Invoke launcher on the hosted Windows runner. The Node 24 package script assembles fixtures and checks JSON traces. Git/TypeScript archives are fetched only by explicit CI qualification steps from exact official release assets, with pinned SHA256. No runtime dependency is added to the factory product.
