# Runtime qualification

## Current pin and evidence

On 2026-10-21, selected Node v24.22.1 LTS from its [official release](https://nodejs.org/en/blog/release/v24.22.1). `runtime-manifest.json` records exact platform URLs and SHA256 values from the [versioned checksum list](https://nodejs.org/download/release/v24.22.1/SHASUMS256.txt). Downloaded and hashed the darwin-arm64 archive before extraction into a private temporary directory. No global runtime was replaced. The extracted binary reports SQLite 3.53.4.

Local evidence covers darwin-arm64, Darwin 25.6.0, APFS (`statfs` type 26). Hosted run `39719540444` at commit `5464dfd8` passed pinned runtime, storage and foundation checks on Linux x64/ext, Windows x64/NTFS and macOS arm64/APFS. Windows native volume detection, WAL write-denial and cooperative qualifier cleanup ran successfully. The qualifier fails on unknown or volatile placement. These are exact foundation claims, not installed-product or release acceptance; other accepted placement types still require their own native evidence. See [hosted results](native-results-2026-10-21.md).

The [Node SQLite API](https://nodejs.org/download/release/latest-v24.x/docs/api/sqlite.html) documents synchronous database methods, busy timeout, and asynchronous page-batched backup. Its release-candidate stability classification remains a dependency limitation. [SQLite WAL](https://sqlite.org/wal.html) requires same-host storage and documents the WAL-reset race fixed before the bundled 3.53.4. No alternate backend or addon is substituted.

## Reproduction

After explicitly downloading and verifying the host's manifest-selected archive, extract it into a private temporary directory. Set `FACTORY_NODE_BIN` to that extraction's `bin` directory on POSIX. From repository root:

    rtk proxy env PATH="$FACTORY_NODE_BIN:$PATH" npm --prefix packages/software-factory run typecheck
    rtk proxy env PATH="$FACTORY_NODE_BIN:$PATH" npm --prefix packages/software-factory run build
    rtk proxy env PATH="$FACTORY_NODE_BIN:$PATH" npm --prefix packages/software-factory run test:qualification -- --area runtime
    rtk proxy "$FACTORY_NODE_BIN/node" packages/software-factory/qualification/runtime.ts

The first three commands passed on the development host. The final command prints JSON evidence and exits 0 only after its assertions pass. Wrong Node/SQLite versions, missing native prerequisites, unsupported placement, failed transactions or exceeded latency bounds exit nonzero. Runtime startup never performs these downloads.

Observed probe result: WAL, FULL synchronous (`2`), foreign keys enforced, explicit rollback, two concurrent processes committing 80 distinct rows, one 40 ms busy timeout measured at 51.465 ms, forced process loss preserving one committed row and removing the uncommitted row, and page-batched backup passing integrity and row-count checks. Across 100 small transactions, p95 commit latency was 0.075792 ms and maximum 0.159292 ms. Probe thresholds are p95 below 100 ms and maximum below one second; these small-fixture measurements do not establish recorder/SSE display latency under accepted load.

Process-loss probes terminate only child handles created by the qualifier in its disposable directory. They do not simulate machine power loss. Backup under concurrent mutation, native packaging/process control, other local filesystems and all installed behavior remain later qualification. Never infer platform support from the published hashes.

## Native CI definition and hosted evidence

The [foundation workflow](../../../.github/workflows/software-factory-qualification.yml) selects explicit Ubuntu24.04 x64, Windows2025 x64 and macOS15 arm64 runners. These labels are documented in the [GitHub runner reference](https://docs.github.com/en/actions/reference/runners/github-hosted-runners). The workflow downloads only the exact manifest URL, bounds download size/time, verifies SHA256 before extraction, and verifies the extracted Node/SQLite/platform/architecture. The official archive also integrity-pins its bundled npm. Runner images and bootstrap Node are GitHub-managed prerequisites, recorded with the evidence rather than presented as immutable images.

`assertLocalPlacement(directory)` in `src/placement.ts` resolves an existing directory and returns its canonical directory, platform and filesystem. APFS/HFS+, ext, btrfs and xfs are accepted; volatile tmpfs and unknown/network filesystem types fail closed. On Windows, an isolated fixed PowerShell script calls documented [GetVolumePathNameW](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getvolumepathnamew), [GetDriveTypeW](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getdrivetypew) and [GetVolumeInformationW](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getvolumeinformationw) APIs. It accepts only fixed NTFS/ReFS volumes. The caller path is environment data, not generated PowerShell code. No fallback database is created. This establishes an OS-reported local filesystem boundary; it cannot prove physical media or exclude administrator-configured remote block devices.

Handled cancellation remains SIGINT/SIGTERM on POSIX. On Windows, the private qualifier controller requests the same cleanup through IPC because Node's Windows kill behavior can terminate immediately. Assertions still require status130/143, stopped owned worker and removed disposable directory. The separate process-loss transaction probe uses actual native worker termination on every platform. These checks do not establish Windows console control delivery or T6 product lifecycle semantics.

See [CI evidence and remaining gates](ci.md). Hosted run `39719540444` passed all three foundation targets after the first Windows failures were repaired. Installed product, provider, descendant-control and live desktop qualification remain later gates.

## Darwin placement repair

Darwin filesystem identifiers are not treated as stable magic numbers. Hosted failure `39810180199` reported numeric25; its actual filesystem name remains unproved. The repair uses absolute `/bin/df -n -P -T apfs -- DIRECTORY`, then the fixed `hfs` filter only after exit1. [Apple's source](https://github.com/apple-oss-distributions/file_cmds/blob/f8c84000d1f02be159053846a3d730b0290f9614/df/df.c) applies the filter to the explicit operand's kernel `f_fstypename` and rejects mismatches. Native output is discarded, the environment contains only `LC_ALL=C`, and each process has a1000ms timeout. No shell or path-output parsing is used. Process errors/signals and other exit statuses refuse placement. The timeout bounds the process request, not every possible kernel/filesystem scheduling delay. The accepted filesystem policy is unchanged.

Local native APFS with literal shell metacharacters passes; HFS remains unqualified. Disposable OS-boundary fixtures prove name-based acceptance with numeric25 and refusal even when numeric26 would previously have authorized it. Strict/build and36 composed placement/store/capture/runtime checks pass in6.086s on2026-10-22. Independent review approved the repair. Changed hosted macOS foundation run `39818894909` at commit `3e9f5d28` passes every step, including placement, store and runtime; artifacts are retained under `/tmp/factory-foundation-39818894909/`. Linux and Windows storage/runtime also pass in that run, while unrelated product selectors remain failed. The original numeric25 host name remains unknown, and HFS remains unqualified.

## Browser development prerequisite

On 2026-10-22, the pinned Playwright 1.64.1 CLI downloaded Chromium revision 1248 / Chrome for Testing 156.0.8078.4, matching headless shell and FFmpeg revision 1013 into `/tmp/software-factory-playwright-browsers`. From `packages/software-factory`, setup used qualified Node with `PLAYWRIGHT_BROWSERS_PATH=/tmp/software-factory-playwright-browsers node node_modules/playwright/cli.js install chromium --no-progress --no-remove`. Restricted DNS required network escalation; no system dependency installation or user-cache replacement occurred.

A headless launch, disposable page title/heading read and browser close passed with browser version 156.0.8078.4. Set the same `PLAYWRIGHT_BROWSERS_PATH` for later browser tests. This is environment readiness only; no factory dashboard, UI, accessibility or load acceptance is established.
