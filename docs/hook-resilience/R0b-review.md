# R0b: acquisition and stream boundary review

Independent read-only review completed on 2026-10-14 with no actionable security or correctness finding in `33b5bee2..1b44f4db`. Reviewer `/root/stream_boundary_review` used the clean isolated checkout at `0563bff6479a36e81d82da978323e61868c25405`. No source files changed. The coordinator retained this report; a read-only review did not require an empty implementation commit.

## Scope

The reviewer inspected completed private Git captures, bounded output, descendants, range validation and cleanup; descriptor traversal, FIFO resistance, growth handling, protected spool replay and classification; pinned singleton/batch OIDs, logical-byte charging and batch lifetime. Streaming review covered full-text splitlines versus byte-first diff splitting, replacement/surrogateescape decoding, fixed nonoverlap and greedy completion, exact normalized allowlisting, bounded redaction, line/pattern ordering, finding caps and late error draining. Changed capture/merge tests and retained design/evidence were included. No new dependency or hardcoded credential was found in this scoped change.

## Observed verification

All probes used fake credentials, disposable repositories/logs, bytecode disabled and `OBSERVABILITY_TESTING=1`. Shell invocations used `rtk proxy`.

- `python3 -B scripts/test-scan-secrets-stream-component.py -v`: 12 tests passed in 0.147 seconds.
- 10,000 additional independently chunked full-text regex/splitlines comparisons passed.
- 5,000 additional independently chunked diff-line/surrogateescape comparisons passed.
- `python3 -B scripts/test-scan-secrets-capture.py codex`: capture failures and no-HEAD success passed.
- `python3 -B scripts/test-scan-secrets-merge.py MergeScannerTests.test_singleton_index_edit_keeps_pinned_secret -v`: all-provider test passed in 2.442 seconds.
- Four additional all-provider merge tests covered binary/empty ranges, exact aggregate allowance with framing overhead, and parent/child directory-file ordering; passed in 7.603 seconds.

The additional oracle probes compared whole-string regex/splitlines results and decoded diff lines against independently chosen chunk boundaries. Their pass counts are reviewer observations, not new maintained suites.

## Limits

T4a remains intentionally inactive until T4b; this review does not establish public larger-file acceptance. Full merge-suite reruns, whole-process performance/RSS, native Windows, live installation and authenticated provider dispatch were not performed. Atomic repository snapshots, concurrent same-inode consistency and hard bounds on blocking filesystem operations remain outside the design guarantees. This supplements the final biaxis review and release verification; it does not replace them.
