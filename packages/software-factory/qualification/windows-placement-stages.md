# Windows placement stage diagnostic candidate, 2026-10-22

## Retained native evidence

[Foundation run 39791273442](https://github.com/japurcell/skills/actions/runs/39791273442) tested `a53c154b`. Both Windows fixture URL fix cases passed (9/9). The Windows store group passed 27/30 cases; three native placement probes timed out after approximately 10.1-10.5 seconds. Their safe refusal facts were `error=ETIMEDOUT`, `status=none`, `signal=SIGTERM`, and `elapsedMs` around 10015. The same run's later isolated placement case passed in 311 ms. Runtime qualification independently failed its unchanged 100 ms small-transaction p95 target at 118.4797 ms. These observations establish the 10-second placement subprocess deadline expired, but identify neither the stage that stalled nor its root cause. The runtime failure has no established connection to the placement timeouts. Compiler or first-use contention remains a hypothesis.

Retained temporary evidence: `/tmp/factory-foundation-39791273442-failed.log` and `/tmp/factory-native-39791273442/software-factory-foundation-win32-x64-39791273442-1/`, especially `store.log`, `placement.log`, and `runtime.log`. Preserve the run URL and artifact before its retention expires.

## Candidate behavior and interpretation

The PowerShell probe now emits these fixed stage markers to standard error, flushing each one before proceeding. On refusal, `assertLocalPlacement` reads at most 8192 characters of captured standard error and reports only the last exact allowlisted marker, or `none`. It never includes native output, exception text, paths, or environment values in the thrown error. Unknown and malformed markers are ignored. Existing allowlisted error, status, signal, and elapsed-time facts remain in the message.

| Reported stage | Last completed point |
| --- | --- |
| `none` | No recognized marker was captured. Launch failure, early termination, missing output, and other causes remain possible. |
| `entered` | PowerShell started the probe and set its error preference; `Add-Type` has not been confirmed complete. |
| `interop_ready` | The existing C# P/Invoke type compiled. |
| `volume_path` | `GetVolumePathNameW` returned successfully. |
| `volume_information` | `GetVolumeInformationW` returned successfully. |
| `complete` | The fixed drive/filesystem JSON was constructed, before writing it to standard output and process exit. |

A stage marks progress, not the cause of a later stall. A timeout with `stage=entered`, for example, does not by itself prove that `Add-Type` compilation was responsible. The existing Windows API declarations, placement acceptance/refusal rules, 10-second timeout, 8192-byte output cap, subprocess concurrency, and benchmark target are unchanged. This is an intentional native diagnostic experiment, not a repair claim.

## Local verification and remaining native proof

On macOS arm64 with pinned Node 24.22.1, the public placement test failed before the parser change and passed afterward. The disposable child test checks last-known stage, CRLF markers, no marker, forged unknown markers, a marker beyond the 8192-character inspection cap, and no private-path or native-output leakage. Focused placement passed 3/3; the affected store/capture/placement group passed 30/30. Source and qualification strict TypeScript checks and the package build passed. PowerShell 7 parsed the extracted probe without syntax errors, and its `Add-Type` compiled the unchanged extracted C# interop declaration. Those local checks do not establish Windows PowerShell 5.1 execution or native stage delivery.

After independent review and integration, run the existing `software-factory-qualification.yml` foundation workflow at the integrated SHA with its pinned Windows runtime. Preserve its current test order, concurrency, assertions, 10-second probe deadline, and runtime p95 threshold. Retain the run URL, SHA, runner image, OS, full store and placement logs, foundation JSON, and runtime evidence whether the run passes or fails. For each placement refusal, record only the safe `error/status/signal/stage/elapsedMs` tuple. Compare stage values across the three affected public store cases and the later standalone placement case. A fresh passing run qualifies only that execution; it does not erase the retained timeout. Investigate the runtime p95 failure on its own evidence.

API references: [Node 24 `spawnSync` result and timeout](https://r2.nodejs.org/docs/latest-v24.x/api/child_process.html#child_processspawnsynccommand-args-options), [Windows PowerShell 5.1 `Add-Type`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/add-type?view=powershell-5.1), and [.NET Framework `Console.Error`](https://learn.microsoft.com/en-us/dotnet/api/system.console.error?view=netframework-4.8.1).
