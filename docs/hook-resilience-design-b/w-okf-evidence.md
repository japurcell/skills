# W-OKF native registered-command diagnosis

Status: diagnostic candidate prepared; native source acceptance remains open.

## Retained red and prior green

Actual Windows run `38983363548`, job `117249096858`, tested snapshot
`4b52fec3f43c65801cceb6c999fd489f9019d032`. The installer, Codex
envelopes, uninstrumented native scanner capture and RTK checks passed. In
`scripts/test-repository-okf-windows.ps1`, all three direct OKF adapters
returned the expected bounded, actionable `OKF101` reason. The unchanged
project-local `.codex/hooks.json` Windows Stop command then exceeded the
test's 11-second watchdog from the fixture's nested directory.

Retained failed step: `/private/tmp/design-b-failed-38983363548.log`, SHA-256
`b85266203c468268697286fa1636fca76994c1a22c886444bd0af997687e3c96`.

Actual Windows run `38982851069`, job `117247468623`, passed the unchanged
workflow on integrated `7f9da9eb`, including this OKF suite. Retained scoped
log: `/private/tmp/design-b-integrated-windows-38982851069.log`, SHA-256
`a758203b245b4b219ab54a1e9a71d645685cacdbed98f0e0baa2baf414fca461`.
These observations establish intermittency. They do not identify the cause.

## Diagnostic candidate

Private branch `codex/design-b-w-okf` starts at
`eed8b39704f8a985c94acf74a8dab363cbfe13dd` (tree
`a18d3be98e5149dc509f29c38c20d8f5d908b01b`). Only this evidence document
and `scripts/test-repository-okf-windows.ps1` change.

The registered command, its `shell=True` invocation, fixture environment,
input, 11-second watchdog and original assertion remain intact. The three
direct adapters retain their exit, diagnostic, Windows rerun and 8 KiB
assertions. No provider, adapter, helper, installer, scanner, manifest or
generated product source changes.

The test adds parent-side elapsed timings and a read-only Windows process
observer. Its first newly created direct child is the single registered
fixture invocation. A process is retained only after its parent is the test
or a previously observed fixture process and that parent's Windows creation
time still matches. Each retained process identity contains PID, parent PID,
creation FILETIME and a sanitized executable basename. Subsequent identity
checks reject reused PIDs. No command lines, payload contents, environment
values, executable paths or unrelated host entries are retained or printed.

Observation is bounded to 48 samples with 250 ms waits, four ancestry passes
per snapshot, at most 8192 entries per pass, 12 owned identities, eight
retained topology changes and eight printed processes per change. Each
snapshot and query handle closes in `finally`. The observer is a thread,
creates no additional process, and is stopped and joined in the invocation's
`finally`. On timeout, only partial stream byte counts are printed before
the original `TimeoutExpired` is re-raised. The final observation includes
elapsed milliseconds and audit-file byte count. Sampling may miss brief
processes, and its presence may alter timing; it supplies diagnostic
evidence, not a product repair or a root-cause claim.

Win32 declarations were checked against Microsoft's current documentation:
[process snapshots](https://learn.microsoft.com/en-us/windows/win32/api/tlhelp32/nf-tlhelp32-createtoolhelp32snapshot),
[PROCESSENTRY32W](https://learn.microsoft.com/en-us/windows/win32/api/tlhelp32/ns-tlhelp32-processentry32w),
[Process32FirstW](https://learn.microsoft.com/en-us/windows/win32/api/tlhelp32/nf-tlhelp32-process32firstw),
[process creation times](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-getprocesstimes),
[query handles](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-openprocess)
and [system FILETIME](https://learn.microsoft.com/en-us/windows/win32/api/sysinfoapi/nf-sysinfoapi-getsystemtimeasfiletime).

## Verification and next action

Local parser-only checks passed for the PowerShell file and its embedded
Python. No hooks, functional tests, installers, generators or benchmarks
were executed: T1-CI2 owns the local functional execution window.

Primary reviews and transports the exact committed full tree to the
authorized Windows workflow. Inspect the native `W-OKF` timing/topology
records alongside the preserved assertion. A passing diagnostic run alone
does not identify the original stall. Product changes require an observed
cause and explicit ownership reconciliation; W2 owns the shared native
process helper and its generated closure. Final acceptance requires the
uninstrumented positive public command, native bounded red/green evidence
and affected POSIX proof after the local execution window is handed over.
Primary owns the shared ExecPlan and one final coordinated KB pass.
