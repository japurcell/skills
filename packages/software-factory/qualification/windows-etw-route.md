# Non-debug Windows route observation

This additive qualification command implements the representative ETW comparator boundary. It is not a product dependency. The known `windows-etw-probe*`, held-child fixture, original debugger cases, full 17 Git/3 TypeScript matrix and Windows product uncertainty remain unchanged. Final source review and actual Windows execution are pending.

Every report fixes `productAdmission:false`, `helperAdmission:"refused"`, `helperIdentity:"process-file-identity-unverified"`, `namespaceIdentity:"unverified"` and the refusals `transient-process-identity-unverified` and `namespace-identity-unverified`. A matching graph/output does not override these fields. `observation-complete` means all seven bounded observations finished; `comparison` separately reports `matched` or `refused`. `route-refused` means only part of the representative set supplied complete observations; `inconclusive` means none did. Individual `failures`, `graphMatched` and `outputVerified` distinguish the result. These names never certify a helper's process-file identity or no-child behavior for arbitrary commands.

## Fixed cases and native boundary

The cases are baseline Git and baseline fresh TypeScript emission, candidate Git and separate fresh TypeScript emission, candidate nested cmd, candidate deadline marker and candidate output-limit control. Git runs only `--no-pager --no-lazy-fetch rev-parse --show-toplevel`; TS runs only the generated successful `-p` build. The baseline uses detached:false/windowsHide:false. The candidate uses detached:true/windowsHide:true. Both use shell:false and stdio `['ignore','pipe','pipe']` through actual pinned Node spawn. The same .NET non-debug root launch context uses CreateNoWindow with redirected private root control pipes for every case.

C# starts and queries one owned file-backed PROCESS+IMAGE system session before launching a held Node root. The root writes READY, then waits for one R byte before spawning the unwrapped helper. After the actual helper exit/close and both pipe closures it persists its bounded private result, writes DONE plus its direct PID, and remains live until X. C# independently holds and checks the root handle, PID, creation/full-image/file identity and clean exit. Root End uses the measured release-to-observed-exit bracket, with actual exit inside it. No transient helper is held, suspended or delayed for identity checks. No HELD-child row exists.

The finalized ETL is parsed twice. The first pass retains bounded start/end lifecycles and suspicious console image observations across the session. The second retains images only for the reported direct PID and the complete transitive root graph. Actual TDH metadata validates property names/types, pointer widths and byte counts. Process start/end key continuity, repeated PIDs/keys, parents, lifetimes, statuses, direct PID and expected main-image path matches are checked independently of Node's declarations. All retained relevant images must fit their process lifetime and expected pin/system category; Git also requires all five exact pinned import paths. Unassigned console-host starts/loads are suspicious, including those outside the root graph. They block comparison without attribution by time or proximity.

Pins are hashed through continuously held read-sharing file handles, with FileID and exact-case DOS/NT spellings kept privately. Existing reparse components are rejected; known paths and FileIDs are rechecked. This is expected-pin-path-match evidence only. File sharing does not freeze ancestors/aliases, and pre/post checks do not exclude an intervening rename or alias swap. An image-load path is not a process-image file handle or proof that the loaded file is the process's main executable object. Namespace and transient-process identity remain unverified regardless of graph result. No event-controlled path is opened.

Bounds remain 30 seconds of native observation, ETL strictly below 64 MiB, 100,000 callbacks total across both passes, 65,536-byte schema metadata, 32,768-byte property data and 65,536-byte private receipt before persistence. Retention additionally stops before exceeding 4096 process rows, 4096 image rows or 8 MiB of retained record text. Exact mode 37748737, all-true ready/before-stop queries, zero stopped-session/final-header losses, finalized header, successful complete ProcessTrace and CloseTrace are mandatory. A cap or missing/uncertain event fails closed.

The deadline control must deliver exactly the 15-byte `deadline-ready\n` marker before Node's 500 ms stop request. The flood control is the unchanged native producer that attempts 4,194,304 bytes; Node stops after observing more than 262,144 bytes and keeps 262,144 per stream, within 10 seconds. Attempted flood size is not claimed as observed delivery. Node uses its actual ChildProcess kill API and must observe exit/close/pipe closure plus an independent nonzero stopped event. It does not claim native code 124.

C# may stop only its own created root process handle. Node may stop only its actual spawned ChildProcess. An event PID, printed PID or kernel key never authorizes external signaling. Root protocol/guard failure, unknown root completion, bridge interruption or uncertain owned-session stop prevents upload and leaves cleanup uncertainty for the disposable job operator. Resource stop/close/disposal attempts are independent; pin disposal cannot be bypassed by root cleanup failure. There is no Job Object subsystem, tracker, service, elevation, ACL/group change, taskkill or startup download.

## Commands and prerequisites

Run commands from the repository root in a disposable Windows 2025 x64 Actions job, with GITHUB_ACTIONS=true and Windows PowerShell 5.1 available. The exact Node 24.22.1 archive/bootstrap and existing startup artifact preparer must already have written `bootstrap.json` and `artifacts.json` into the same evidence directory. The latter must contain the official MinGit 2.54.0.windows.1 and TypeScript 7.0.2 archives and full extracted inventories. The new driver performs no download and hard-fails absent/mismatched prerequisites. Use a fresh evidence directory for each run.

```powershell
$env:WINDOWS_ETW_ROUTE_EVIDENCE = Join-Path $env:RUNNER_TEMP 'factory-windows-etw-route-evidence'
$env:FACTORY_EVIDENCE_DIR = $env:WINDOWS_ETW_ROUTE_EVIDENCE
# Run existing scripts/qualification-bootstrap.mjs with operational output suppressed.
# Run existing qualification/windows-startup-artifacts.mjs with WINDOWS_STARTUP_EVIDENCE
# equal to this evidence directory; its existing --offline mode may use supplied archives.
$bootstrap = Get-Content -Raw (Join-Path $env:WINDOWS_ETW_ROUTE_EVIDENCE 'bootstrap.json') | ConvertFrom-Json
$pinnedNode = Join-Path $bootstrap.directory 'node-v24.22.1-win-x64/node.exe'
& $pinnedNode --test packages/software-factory/qualification/windows-etw-route.test.mjs
& $pinnedNode packages/software-factory/qualification/windows-etw-route-run.mjs
& $pinnedNode packages/software-factory/qualification/windows-etw-route-native.qualification.mjs
& $pinnedNode packages/software-factory/qualification/windows-etw-route.mjs --prepare-artifacts
```

The explicit native qualification requires the preceding real baseline observation. It checks a forged direct PID while a separately owned same-Node process survives, and passes an incorrect held Node digest to the actual C#/PowerShell bridge, requiring native pin refusal without COMPLETE or HELD-child. It neither skips missing prerequisites nor belongs to default Node test discovery. Native actual graph/console schema, all seven cases, native controls and Windows PowerShell 5.1 compilation remain acceptance gates. Local PowerShell 7 compilation is not that evidence.

The driver returns nonzero for an incomplete set or cleanup uncertainty. A complete observation may return zero while comparison and every helper admission remain refused. Workflow acceptance must inspect both the fixed status and individual graph/output fields; do not reinterpret a zero exit as product admission. The collector's real API results establish available rights for that run only. Hosted administrator success does not prove normal nonadmin applicability; access denial is a refusal with no elevation or configuration fallback.

## Artifact contract

Parent owns workflow/CI and registry integration. Upload only the two explicit files after the public artifact guard succeeds:

- `upload/qualification.json`
- `upload/native.tsv`

All native private receipts (`cases/<fixed-case>/observation.private.tsv`), launcher results, specs, bootstrap/artifact receipts, compiler outputs, control executable and ETLs stay local. Private native receipts contain ambient PIDs and kernel keys and must never be uploaded or printed. The driver deletes each exact `cases/<fixed-case>/trace.etl` after offline parse, and retries known exact paths on finalization. An always-run workflow cleanup should also remove these seven fixed ETL paths before invoking the guard. Never upload a directory wildcard or raw operational result.

The guard first removes stale upload staging, bounds source bytes before JSON/TSV parsing, refuses any remaining known raw ETL or cleanup/guard uncertainty, and revalidates the private native/launcher evidence rather than trusting a forged public status. It reconstructs fixed case labels, booleans, bounded counts, enumerated failure codes and explicit identity refusals. It also rechecks exact Git output, native marker/flood content and TS emission privately. No raw paths, argv, environments, output content, exception text, keys, file IDs, ambient PIDs or ambient hashes enter the staged files. Each staged file remains below 65,536 bytes. Malformed/path-bearing/oversize grammar or interrupted cleanup prevents upload.

Portable public tests cover the real handshake and pre-release EOF, forged PID and graph/key/parent/lifetime/image/console failures, required Git imports, output contracts, health/caps/close/header/cleanup, noncanonical/compound grammar and private-to-fixed artifact reconstruction. Final review is deferred until all canonical implementation tasks finish. The original full alternate 17 Git/3 TS matrix, hostile/PATH/tamper controls, stronger transient identity and namespace proof, and a separate product-admission decision are still required.

Microsoft contracts: [Process events](https://learn.microsoft.com/en-us/windows/win32/etw/process-v2-typegroup1), [image events](https://learn.microsoft.com/en-us/windows/win32/etw/image-load), [ProcessTrace](https://learn.microsoft.com/en-us/windows/win32/api/evntrace/nf-evntrace-processtrace), [TDH metadata](https://learn.microsoft.com/en-us/windows/win32/api/tdh/ns-tdh-trace_event_info), [logging modes](https://learn.microsoft.com/en-us/windows/win32/etw/logging-mode-constants), [trace header](https://learn.microsoft.com/en-us/windows/win32/api/evntrace/ns-evntrace-trace_logfile_header), [file sharing](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilew), [file identity](https://learn.microsoft.com/en-us/windows/win32/api/winbase/ns-winbase-file_id_info), [namespaces/case/links](https://learn.microsoft.com/en-us/windows/win32/fileio/naming-a-file), [session creation/rights](https://learn.microsoft.com/en-us/windows/win32/api/evntrace/nf-evntrace-starttracew). These contracts do not supply transient child handle acquisition or console-client attribution.
