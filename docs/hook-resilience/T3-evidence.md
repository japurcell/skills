# T3: verified candidate acquisition

Implemented on private branch `codex/hook-resilience-t3`, based on `5dd8af43`, on 2026-10-14. This task implements the approved acquisition contract in [streaming-design.md](streaming-design.md). The coordinator owns the active ExecPlan and the single coordinated knowledge-maintenance pass.

## Public reproduction and result

The new `MergeScannerTests.test_singleton_index_edit_keeps_pinned_secret` runs generated hooks against a real temporary Git repository. A Git wrapper replaces the single selected index entry with an equally sized safe blob after returning its original metadata. Before T3, Codex block and warn both recorded `clean` instead of the required `findings`:

```text
rtk proxy python3 scripts/test-scan-secrets-merge.py --provider codex \
  MergeScannerTests.test_singleton_index_edit_keeps_pinned_secret -v
Ran 1 test in 0.876s
FAILED (failures=2): 'clean' != 'findings'
```

After immutable OID acquisition, the same command passed, including both modes (`Ran 1 test in 0.803s; OK`). The complete final merge suite exercises the case across Copilot, Gemini, and Codex.

## Implemented acquisition behavior

`capture_git` retains the existing private regular temporary-file stdout, five-second Git deadline bounded by the shared eight-second work deadline, discarded stderr, prompt disabling, bounded input/output, accepted empty nonzero HEAD/ref cases, descendant checks, process-tree cleanup and native Windows descendant handling. It lends a `VerifiedCapture` only after completion and final type/mode/owner/size verification. Reader chunks are at most 65,536 bytes and check deadlines and exact capture/range sizes. Candidate and index metadata use incremental NUL/newline records; decimal blob sizes accept at most 20 digits. Candidate records remain capped at 256 and argv batches at the existing 8,192-byte estimate.

All stage-zero and unresolved index snapshots, including a singleton, now resolve literal index paths to pinned OIDs. Metadata and grouped bodies use only those IDs. Every metadata size is reserved once before requesting bodies. Framing is validated for the complete batch before any snapshot is lent; snapshots retain protected offsets/lengths instead of copied blob dictionaries. One capture persists across interleaved worktree candidates and closes after its last index range. The raw `cat-file blob OID` fallback supports an exact capture-cap body when framing would exceed the cap; that larger-body route becomes reachable under T4's policy.

Worktree acquisition uses descriptor-relative/no-follow traversal where available, adds nonblocking open against FIFO swaps, immediately verifies regular/reparse status, and reads once from the descriptor into one owner-only private spool. It prechecks size and remaining aggregate allowance, charges actual bytes once, and rejects the first extra byte during growth. Full protected-snapshot classification uses bounded strict incremental UTF-8 validation, EOF flush, and NUL precedence before matching; replay never reopens the pathname. Missing unresolved worktree files remain permitted. Snapshot contexts invalidate and close their state, and source exit closes any remaining batch.

The legacy 1 MiB snapshot ceiling remains. The existing matcher receives a temporary one-snapshot materialization, cleared before the next acquisition. Diff output remains on its old materialized compatibility path for T4. Aggregate worktree overflow now reports `total_bytes_limit/candidate_read`, with the original measured/limit values, because it fails before scanning the excess candidate; the maintained capture assertion was updated accordingly without removing its denial/audit checks.

## Validation

- `rtk proxy python3 scripts/test-scan-secrets-capture.py codex`, `copilot`, and `gemini`: all passed, including block/warn negatives, no-HEAD success, race cases and classification cases.
- `rtk proxy bash scripts/test-codex-hooks-secrets-scanner.sh` and `scripts/test-gemini-hooks-secrets-scanner.sh`: final serial reruns passed (exit 0), including their expanded capture suites.
- `rtk proxy python3 scripts/generate-hooks.py --check`: passed, 35 generated files current. AST parsing of the canonical renderer, all three outputs and both Python suites passed. `rtk git diff --check` passed.
- `rtk proxy python3 scripts/test-scan-secrets-merge.py -v`: final frozen-source serial run passed all 33 tests in 212.008 seconds.
- `rtk proxy bash scripts/test-hooks-secrets-scanner.sh`: final serial repaired suite passed (exit 0), including native `cat-file` failure denials/warnings and the expanded capture cases.

Retained failed validation and repairs: the original Copilot Bash suite expected injected `git show` failures after T3 retired that command. The coordinator authorized changing the injection to actual `cat-file` acquisition; all exact native denial, warn, exit and incomplete assertions remain. The final serial Copilot suite passed with the repaired injection.

An earlier all-provider merge run before the final incremental-enumeration/lifecycle changes passed all 33 tests in 220.956 seconds. A concurrent final-tree run finished 33 tests in 242.028 seconds with one Codex block/diff long-path case reporting `incomplete` instead of `clean`. The old assertion did not include the diagnostic and the temporary fixture was already cleaned, so its exact cause was unavailable. The assertion now retains the sanitized record when status differs. A first targeted repeat passed in 29.541 seconds while the remainder of the full suite was still running. A strictly serial targeted Codex repeat then passed (`Ran 1 test in 29.471s; OK`). A complete serial run then reproduced a Gemini block/diff final-secret failure: 33 tests in 223.546 seconds; `scan_timeout/git_diff`, eight seconds, expected `findings` but got `incomplete`.

An invocation/wait-cycle probe compared frozen `5dd8af43` and T3 through the same public fixture. Completed 256-path scans both used one `cat-file --batch-check`, one `cat-file --batch`, 14 bounded literal `ls-files` batches, 258 diffs (256 legacy per-path plus two enumeration calls), two other `ls-files` calls and three `rev-parse` calls. There was no per-object content fallback. Local `subprocess.Popen._wait` source and integer wait-cycle instrumentation identified exponential sleeps up to eight milliseconds under the existing 20 ms wait slice, repeated hundreds of times. Baseline complete probes recorded 279-285 such eight-millisecond sleeps. The unmodified T3 probe also retained one timeout after 225 diff calls.

T3 changes only the bounded completion wait slice to five milliseconds, reducing stdlib completion sleeps to one/two milliseconds while preserving the five/eight-second deadlines, output checks, parent/descendant validation and cleanup. The instrumented repaired probe retained a Copilot timeout after 253 diff calls; Gemini/Codex completed. That probe imports JSON/logs each Git call and counts wait cycles, so it is diagnostic evidence rather than latency acceptance. The actual uninstrumented `MergeScannerTests.test_batch_long_paths_fit_bounded_git_command_lines` then passed across all three providers, both modes/scopes and clean/final-secret cases (`Ran 1 test in 70.289s; OK`). The complete final frozen-source serial merge run passed all 33 tests in 212.008 seconds. All failed observations remain retained.

The extended capture suite checks FIFO replacement between stat/open, growth after descriptor opening, pathname replacement after opening, same-inode rewrite after acquisition, split UTF-8, late NUL/invalid UTF-8, and original findings/order/redaction. The merge suite adds descendant-held blob-capture output and retains malformed framing, hidden staged secrets, all conflict stages, permitted missing conflict worktrees, unsafe symlinks/directories, exact byte limits, old-Git compatibility, long/delimited paths, directory descendants, and both 250-file merge scenarios. Acquisition errors require `incomplete`; credential controls require `findings` in block/warn.

No performance benchmark ran in this task. Passing the maintained 250-file cases establishes functional compatibility within the scanner/watchdog checks, not a measured latency/RSS improvement. The coordinator owns serialized V1 resource and matched-throughput evidence. Native Windows, live installation, and authenticated provider delivery were not run here.

## Exact T4 interface and remaining work

Candidates deliberately remain `(source: str, path: str)` tuples in existing sorted `(path, source)` order. Pinned OIDs and checked sizes are private metadata in `SnapshotSource.objects`; there is no all-blob content dictionary.

```python
budget = ScanBudget(scan_deadline)
with snapshot_source(root, candidates, budget) as snapshots:
    for candidate in candidates:
        with snapshots.acquire(candidate) as snapshot:
            # None only for permitted missing unresolved-worktree content.
            if snapshot is not None:
                snapshot.candidate       # (source, path)
                snapshot.byte_count      # actual bytes / checked blob size
                snapshot.classification  # "text" or "binary"
                snapshot.chunks()        # rewindable, at most 65536 bytes
```

`ScanBudget.remaining()`, `used_bytes`, `reserve_index(candidate, size)` and `charge(size, operation="candidate_read")` own aggregate charging. All selected index sizes are already reserved when `snapshot_source` opens. Do not charge snapshot replay or increment the budget again in the matcher. A snapshot and its chunk iterators must be consumed within its `acquire` context; do not interleave replay iterators against their shared protected handle.

For diff streaming, use `with capture_git(args, cwd=root, deadline=scan_deadline) as capture:` and consume `capture.chunks()` or bounded `capture.records(separator, maximum=...)`. Only existing explicitly allowed empty nonzero HEAD/ref calls can lend `None`. `run_git` remains the compatibility wrapper for small control calls and the old diff matcher.

T4 removes the one-snapshot `b"".join(snapshot.chunks())` bridge and full line/match arrays; implements exact streaming full/diff match semantics; removes the index/worktree `MAX_FILE_BYTES` checks; uses `remaining` as the worktree ceiling; and makes first growth overflow uniformly `total_bytes_limit/candidate_read`. Preserve the raw-blob fallback, already-reserved index bytes, classification-before-findings, range ownership, source order, deadlines and cleanup. Enumeration/acquisition/later Git diffs remain non-atomic. Cooperative filesystem clock checks cannot bound a blocking disk operation; Windows/non-dir-fd ancestor races remain the existing platform limitation.
