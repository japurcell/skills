# Runtime qualification

## Current pin and evidence

On 2026-10-21, selected Node v24.22.1 LTS from its [official release](https://nodejs.org/en/blog/release/v24.22.1). `runtime-manifest.json` records exact platform URLs and SHA256 values from the [versioned checksum list](https://nodejs.org/download/release/v24.22.1/SHASUMS256.txt). Downloaded and hashed the darwin-arm64 archive before extraction into a private temporary directory. No global runtime was replaced. The extracted binary reports SQLite 3.53.4.

Native evidence covers darwin-arm64, Darwin 25.6.0, APFS (`statfs` type 26). Linux and Windows artifacts have published hashes only; neither binary nor native storage behavior is qualified. The qualifier fails on unreviewed filesystems/platforms. Windows filesystem detection remains work before Windows qualification can pass. This is a development storage probe, not installed-product or release acceptance.

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
