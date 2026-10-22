# Hosted foundation evidence, 2026-10-21

User explicitly authorized the branch push and native qualification. [Run 39718601088](https://github.com/japurcell/skills/actions/runs/39718601088) tested commit `6f94f4b5e9ab1c37866738d34d584ed4428d4034`. Runtime archives passed their reviewed integrity checks. All targets used Node v24.22.1 and SQLite 3.53.4. This is foundation evidence only; product, provider and live desktop acceptance remain unfinished.

| Target | Runner image | OS release / filesystem | Foundation result |
| --- | --- | --- | --- |
| linux-x64 | ubuntu24 20261018.339.1 | 7.0.0-1017-azure / ext | passed |
| darwin-arm64 | macos15 20260907.0337.1 | 24.6.0 / apfs | passed |
| win32-x64 | win25-vs2026 20261018.275.1 | 10.0.26100 / NTFS | failed |

All three direct storage probes observed WAL, synchronous=FULL, foreign keys, rollback, a busy writer, 80 concurrent rows, one committed row after process loss, zero uncommitted rows after process loss, and backup integrity=ok. Small-transaction p95 commit times were Linux 0.307 ms, macOS 0.212 ms and Windows 5.968 ms. These bounded fixture measurements are not production latency guarantees.

Windows foundation failed before most recorder/store cases because Git rejects the Node Windows device path supplied as GIT_CONFIG_GLOBAL. Its cancellation qualifier also encountered SQLITE_BUSY in the concurrent writer after the short individual wait; unlike production store transactions, the probe writer lacked a bounded pre-BEGIN retry. Both failures remain required repairs. The native WAL-write-lock test did not run successfully, so its behavior remains unqualified.

Each job uploaded bootstrap JSON, every step log, foundation JSON and direct runtime JSON, including Windows failures. Artifacts are retained by Actions for 14 days; the concise version, result and mechanism evidence above is retained here. Local downloaded evidence resides under `/tmp/factory-native-{linux,macos,windows}-39718601088/` and is temporary. A subsequent passing rerun must be linked separately; do not rewrite this failed-run evidence as success.

## Reviewed repair and passing native rerun

Commit `7ae5f2da` isolates fixture Git config/hooks as regular owned paths and retries only confirmed pre-BEGIN SQLite busy contention for up to five seconds. Independent review approved the repair. On the integrated local pinned-runtime tree, strict typechecks/build, 29 store/capture/placement/composed tests, six fixture/CLI checks and six runtime/CI checks pass. The two real-lock regressions prove all 40 rows survive released contention and an unreleased lock fails within its deadline without inserting rows. The separate 40 ms busy probe remains intact. Native rerun results must be recorded separately.

[Run 39719540444](https://github.com/japurcell/skills/actions/runs/39719540444) tested commit `5464dfd80b9c60f2d8565de1b00600288d70ffaf` and passed all three foundation jobs. Every target passed the exact archive/bootstrap checks, strict typechecks/build, six fixtures, 29 store/capture/placement/composed checks, two additional placement checks, two CI contracts, four runtime checks and direct SQLite proof. Windows executed the native WAL byte-lock failure case successfully; this proves that I/O-failure fixture, not disk-full parity or product descendant cleanup.

| Target | Runner image | OS / filesystem | Small-commit p95 |
| --- | --- | --- | --- |
| darwin-arm64 | macos15 20260907.0337.1 | 24.6.0 / apfs | 0.154 ms |
| linux-x64 | ubuntu24 20261012.334.1 | 6.17.0-1022-azure / ext | 0.346 ms |
| win32-x64 | win25-vs2026 20261007.264.1 | 10.0.26100 / NTFS | 7.187 ms |

All direct transaction, rollback, 80-row contention, process-loss and backup-integrity assertions passed again. POSIX signal cleanup and Windows cooperative qualifier cleanup passed their distinct assertions. No Windows console-signal, installed runtime, real provider or desktop-delivery claim follows. Passing artifacts were downloaded under `/tmp/factory-native-pass-39719540444/`; their retained Actions copies expire after 14 days.

## Reviewed T6 source, retained latency rejection and fresh-host rerun

[Run 39726180450](https://github.com/japurcell/skills/actions/runs/39726180450) tests `8053272b55ea4e8024cd075a45bfed8b890db7fe`, including reviewed T6 source. macOS and Windows passed attempt 1. Linux passed all earlier foundation steps but its direct storage probe rejected small-commit p95 **121.044151 ms** against the unchanged **100 ms** threshold. The qualifier, placement source and foundation driver are identical to earlier passing `6435ec41`; no source repair or threshold change was made. The exact cause of the different measured latency was not established.

After retaining attempt 1 evidence, the operator reran only the failed job on another hosted runner. Linux attempt 2 passed. This is explicit qualification on that runner, not proof that every runner with the same image meets latency requirements, a flakiness repair, or a factory-managed infrastructure retry. The workflow has no automatic retry.

| Target / passing attempt | Runner image | OS / filesystem | Small-commit p95 |
| --- | --- | --- | --- |
| darwin-arm64 / 1 | macos15 20260907.0337.1 | 24.6.0 / apfs | 0.132 ms |
| linux-x64 / 2 | ubuntu24 20261018.339.1 | 7.0.0-1017-azure / ext | 0.553 ms |
| win32-x64 / 1 | win25-vs2026 20261018.275.1 | 10.0.26100 / NTFS | 4.802 ms |

All passing targets again verified WAL/FULL/foreign keys, rollback, 80 concurrent rows, one committed and zero uncommitted rows after process loss, and backup integrity. Failure artifacts are downloaded under `/tmp/factory-foundation-linux-39726180450-attempt1`; passing artifacts under `/tmp/factory-foundation-39726180450/`. Actions retention is 14 days. These remain foundation-only checks; the hosted workflow does not run T6 startup/shutdown, real providers or desktop delivery.


## Reviewed diagnostics and three-platform pass

[Run39736090737](https://github.com/japurcell/skills/actions/runs/39736090737) tests `ca450bc9f7e99f97a857578007ffa1115a8c67e2` and passes all three foundation jobs on attempt1. Reviewed placement diagnostics preserve the original ten-second probe limit and concurrency. The prior Windows placement failure in run39729936207 remains unexplained; this pass does not establish its cause or a cure.

| Target | Runner image | OS / filesystem | Small-commit p95 |
| --- | --- | --- | --- |
| darwin-arm64 | macos15 20260907.0337.1 |24.6.0 / apfs |0.343125ms |
| linux-x64 | ubuntu24 20261012.334.1 |6.17.0-1022-azure / ext |0.506312ms |
| win32-x64 | win25-vs2026 20261018.275.1 |10.0.26100 / NTFS |3.493800ms |

Pinned Node24.22.1/SQLite3.53.4, bootstrap integrity, strict build/typechecks, registered fixture/store groups, explicit placement/CI/runtime checks, WAL/FULL/foreign keys, rollback,80 concurrent rows, one committed and zero uncommitted rows after process loss, and backup integrity all pass. Evidence is downloaded under `/tmp/factory-native-39736090737/`; hosted artifacts expire after14days. This remains foundation-only, excluding lifecycle/provider/UI/desktop qualification.

Separate [fresh-host Windows capture run39736090516](https://github.com/japurcell/skills/actions/runs/39736090516) passes the exact previously failing copilot/warn/partial public-hook scenario with disposable home/audit/observability isolation. The unchanged full-suite workflow runs on a different host. This single focused pass does not establish the original watchdog cause or prove a general timeout cure. Its artifact is `/tmp/factory-windows-diagnostic-39736090516/windows-capture-diagnostic-39736090516-1/partial.log`.

The separate unchanged full-suite [Windows run39736090551](https://github.com/japurcell/skills/actions/runs/39736090551) also passes on its own host, including scanner envelopes/capture, stable RTK configuration and lifecycle messages. The public capture suite completed with original matrix and watchdogs. Full log is `/tmp/factory-windows-hooks-39736090551.log`. This provides native regression evidence while the original timeout stage remains unproved.


[POSIX run39736090738](https://github.com/japurcell/skills/actions/runs/39736090738) passes Linux verifier41 checks in93.451seconds, including actual ESRCH and conservative denied/EIO/empty controls. The macOS job fails1 and errors1 of41 in304.336seconds. Maintained stage evidence shows a requested0.3-second delay consumed0.433962seconds; the final observer reached return-delay start at0.505989seconds, then timed out at1.005043seconds before its requested0.55-second return delay completed. Structured rejection is2/process_observation_timeout, limit1.0, measured1.002. A separate broken-output-pipe public invocation exceeded its unchanged15-second test wait; its blocked phase is not known. The log is `/tmp/factory-hook-39736090738-failed.log`. This establishes scheduling delay in the tested observer, not a safe reason to widen budgets or shorten injected delays. A fresh macOS verifier host with bounded timing/load metadata can distinguish host scheduling from preceding full-suite effects while preserving the existing full-suite job and assertions.


## Later diagnostic and fixture publication failure

[Fresh macOS run39738670569](https://github.com/japurcell/skills/actions/runs/39738670569) at4af7c204 fails only delayed metadata return:41tests in267.751seconds, limit1.0/measured1.002. The fresh host is Darwin25.6/arm64 with3CPUs and recorded load averages10.67/31.27/17.82. Requested0.3-second sleeps measured0.317-0.377seconds;0.55-second sleeps measured0.564-0.615seconds. The final observer began its return delay at0.454921seconds and exited at1.003012seconds before completing it. Artifacts are in `/tmp/factory-fresh-macos-39738670569/`. Earlier pipeline work is not necessary for this failure; load is observed, not established sole cause. No deadline or original assertion is waived.

[Foundation run39738670567](https://github.com/japurcell/skills/actions/runs/39738670567) passes Linux and Windows, but macOS sees an empty launch report in the test-only fixture before its write finishes. The deterministic public regression pauses the actual filesystem write after creation and reproduces visibility before complete JSON. The reviewed fix creates an exclusive0600sibling, writes/closes its owned descriptor, then renames atomically. A second red/green case proves collision refusal preserves an unowned existing temp file and requires actual EEXIST exit1, not timeout. Nine fixture/CLI/dispatch checks and two affected lifecycle cases pass; native qualification of this exact repair remains pending. Failure artifacts are retained under `/tmp/factory-native-39738670567/` and log `/tmp/factory-foundation-39738670567-failed.log`.


## Reviewed shared cleanup budget candidate

Independent review approves `587a0e9c`, rebased source-identically to `e028cd24` and `10d0e852`. Cleanup-only observation uses the remaining original two-second absolute deadline with a 50 ms finalization reserve; ordinary observation remains capped at one second. The additional public case fails on the original source at limit 1.0/measured 1.002 and passes on the candidate. Review caught and repaired a fixture acknowledgement race, then independently passed its forced scheduling probe and all 42 native cases in 143.347 seconds. The original 41 methods, injected delays and leak/identity assertions remain. Detailed evidence is in `docs/software-factory/research/macos-cleanup-2026-10-22.md`. Integrated at `d39e8058`; all 42 native base cases pass in 138.325 seconds (`/tmp/factory-cleanup-base42.log`). Hosted Python 3.13 qualification of this exact source remains pending. This repair removes the redundant observation subcap; it does not promise completion on an arbitrarily stalled host.


## Qualification batch at cdb9bc57

[Foundation 39788049151](https://github.com/japurcell/skills/actions/runs/39788049151) passes Linux x64 and macOS arm64, including the atomic launch report repair. Windows x64 passes storage/runtime/placement but fails the two new fixture preload tests: Node treats drive-absolute `--import C:...` as an unsupported URL scheme. The parent converts both preload paths with `pathToFileURL(...).href`, without changing assertions or deadlines. The native run is the public red; all nine fixture/CLI/dispatch cases pass locally after repair. Exact pinned [Node URL API source](https://github.com/nodejs/node/blob/v24.22.1/doc/api/url.md#urlpathtofileurlpath-options) confirms the portable conversion. Native proof of this narrow Windows test fix remains pending. Artifacts: `/tmp/factory-native-39788049151/`; log `/tmp/factory-foundation-39788049151-failed.log`. Commit p95: Linux 0.461577 ms, macOS 0.245458 ms, Windows 16.658 ms; all native SQLite mechanisms pass.

[Windows hooks 39788049296](https://github.com/japurcell/skills/actions/runs/39788049296) passes again on its independent native host. [POSIX 39788049229](https://github.com/japurcell/skills/actions/runs/39788049229) fails Linux because the ESRCH fixture never exercises its injected descriptor result (42 cases, 87.022 seconds), and macOS because the second delayed graph receives only 0.925 seconds (42 cases, 265.462 seconds). [Fresh macOS 39788049247](https://github.com/japurcell/skills/actions/runs/39788049247) independently fails the same original 0.3/0.55 case, limit 0.835/measured 0.836, with 42 cases in 219.925 seconds. Its first fresh graph took 1.084 seconds; the added known-closure 0.3/0.7 case passes in 1.187 seconds. Darwin 25.6 arm64/three-CPU host load 96.68 is measured, not proved sole cause. Exact artifacts: `/tmp/factory-posix-39788049229/`, `/tmp/factory-fresh-macos-39788049247/`; failed logs retain those run IDs.

A new bounded repair is active in factory-cleanup-closure: Darwin-only direct child enumeration for freshly verified stopped known parents through the existing owned native helper. Linux retains its current graph algorithm and gets a stricter consumed-snapshot fixture acknowledgement. The original two-second deadline, 50 ms reserve, ordinary one-second observation, 256-process bound and all 42 assertions/delays remain. No new hosted pass is claimed.


## Portable preloads pass; placement timeout is confirmed

[Foundation 39791273442](https://github.com/japurcell/skills/actions/runs/39791273442) at `a53c154b` passes Linux and macOS. Windows passes all nine fixtures, including both repaired file-URL preloads. It fails three concurrent store-group cases because the native PowerShell placement probe reaches its unchanged ten-second timeout (ETIMEDOUT/status none/SIGTERM, observed elapsed 10015 ms). A later standalone native placement case passes in 311 ms. The runtime benchmark separately fails its unchanged 100 ms small-transaction p95 target at 118.4797 ms. This establishes the bounded probe timeout, not its internal stage/root cause or a cause for the latency rejection. Artifacts: `/tmp/factory-native-39791273442/`; failed log `/tmp/factory-foundation-39791273442-failed.log`. Fixed-enum stage instrumentation is an active intentional diagnostic task; no cache, serialization, larger timeout or benchmark weakening is authorized.

Independent complete review approves the new Darwin targeted-child repair `9690e057`, rebased source-identically to `5f34d83a`. All 44 native macOS cases pass independently in 113.072 seconds; this includes original late children, three actual post-SIGINT generations, denied shutdown, truncation/duplicate/wrong-parent/absent-child/parent disappearance protocols and simulated Linux ESRCH controls. Integrated at `9fdd9ee1`; fresh base proof passes all 44 cases in 113.376 seconds (`/tmp/factory-closure-base44.log`). Clean integrated tree was archived and branch deleted. Hosted Linux/macOS proof remains pending.
