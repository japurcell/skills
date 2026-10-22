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
