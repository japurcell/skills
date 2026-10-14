# T4b: streaming integration and aggregate capacity

Implemented 2026-10-14 from `b4dc7038` on private branch
`codex/hook-resilience-t4b`, in the managed worktree
`/Users/adam/.codex/worktrees/hook-stream-integration/skills`. The coordinator owns
the active ExecPlan, test registry, integration, and final coordinated knowledge
maintenance. The base branch and live installations were not mutated.

## Delivered behavior

The scanner renderer embeds `scanner_stream.SOURCE` directly into each generated
provider scanner. Protected snapshot replay feeds bounded full-content events;
Git diffs feed byte-first added-line events directly from `VerifiedCapture`.
No runtime cross-provider import, full-snapshot bridge, full-line list, or legacy
whole-line matcher remains. Pattern definitions now live in the stream component;
generator probes exercise its configured matchers and event/capture interfaces.

Classification still covers the complete acquired snapshot before matching.
Late NUL or invalid UTF-8 in binary-classified files forces ASCII projection of
the same protected snapshot, including unchanged tracked tokens. Text replacement
decoding and full `str.splitlines()` numbering remain distinct from byte-first
Git diff lines with filesystem decoding. Lazy `StreamDiffError` is mapped to
`git_output_invalid/git_diff` around consumption; the current capture is drained
and validated after the processed-finding cap.

One `StreamReport` spans sorted candidates, with credential-path findings first,
100 retained findings and 1,000 processed unsuppressed findings. Exact normalized
allowlisting, complete greedy suffixes, fixed nonoverlap, restart behavior,
redaction, and line/pattern ordering remain intact.

The retired 1 MiB per-snapshot constant/checks are removed. Reads use the remaining
8,388,608-byte aggregate allowance, while preserving 256 snapshots, eight seconds
of work and the separate 8 MiB Git-capture ceiling. Index bytes are reserved once;
framing and replay are free. Exact-cap singleton index content uses the existing
raw-OID fallback. Worktree growth stops at the first extra byte, and overflow
measurements add only the newly read chunk to already charged bytes. Existing
rejection fixtures now exceed the aggregate boundary and retain their unsafe
read, denial/warning, logging and diagnostic assertions.

Integration exposed the component's per-line allocation cost. A bounded prefix
search now creates pattern machines only when a possible token prefix appears;
ten carried characters preserve prefixes split across fragments. Prefix-free
short lines do not allocate five matcher states. The canonical module has mode
100644 and no executable shebang.

Ordinary scans inherit a start timestamp established before recovery bootstrap
reads stdin. Input time and subsequent Git/scan work therefore share the same
nonextendable eight-second budget. Imports still do not read stdin. Recovery's
deny-only protocol is unchanged. Generated diagnostic identities and policy
metadata were refreshed; removed `MAX_FILE_BYTES` reports `not_defined`.

## Public red and retained failed observations

The first public test created one exact 2,030,848-byte safe file, then committed
it and appended a 13-byte benign edit. All three providers rejected both states
with `file_bytes_limit/candidate_read`, measured 2,030,848/2,030,861 and limit
1,048,576 (`Ran 1 test in 0.897s`, six failures). The same generated-entrypoint
test passed after integration (`Ran 1 test in 7.086s`).

A second public fixture used 2,030,848 bytes of short nonempty `x` lines. Before
the lazy allocation repair, all three providers returned
`scan_timeout/candidate_scan` at the unchanged eight-second limit
(`Ran 1 test in 24.212s`, three failures). After repair, that fixture and the
reported safe-text/tiny-edit test passed together in 3.406 seconds. These are
functional observations, not isolated performance measurements.

The first lazy-prefix implementation omitted the fine-grained GitHub prefix.
Independent component tests immediately retained 80 parity failures and one
missing-finding error. Adding the complete prefix and its bounded carry restored
all 12 component tests; the final public and additional oracle runs passed.

The delayed-input fixture initially exceeded the existing 0.5-second input idle
window and correctly returned `input_invalid/input`. A valid drip fixture then
kept total input below two seconds while delaying the first four Git calls by
1.9 seconds each. It reproduced a clean response despite exceeding the intended
combined work allowance (`Ran 1 test in 18.911s`, one failure). Sharing the start
timestamp restored `scan_timeout` for all three providers. The final fixture
explicitly fixes block/diff mode and drips every 0.2 seconds for wider idle-window
headroom.

An initial 11-test public matrix retained one fixture `KeyError`: the assertion
used `omitted_findings` instead of the actual `omittedFindings` audit field.
Canonical audit keys were restored; all finding/count assertions now pass.
No failing assertion or security case was removed or weakened.

## Observed verification

Checks ran serially against frozen runtime source with disposable repositories,
homes and logs, `OBSERVABILITY_TESTING=1`, and no inherited skip/allowlist override
except explicit suppression cases.

- `rtk proxy python3 scripts/test-scan-secrets-stream-component.py`: 12 tests
  passed, 0.136 seconds, including bounded allocation and independent regex,
  separator, byte-diff, greedy and cap oracles.
- `rtk proxy python3 scripts/test-scan-secrets-streaming.py -v`: 13 tests passed,
  41.387 seconds. Covers the reported size, tiny tracked edit, exact aggregate
  worktree/index cap and first overflow, every supported token split at capture
  boundaries and EOF, greedy exact suppression, UTF-8/CRLF/Unicode separators,
  late binary markers, line/pattern/candidate/path ordering, report caps, hidden
  staged content, byte-first diff Unicode, malformed tail after the cap, long
  single lines, empty newline-dense text, and short nonempty dense text.
  After explicitly fixing the delayed-input fixture's mode/scope and widening
  idle-window headroom, its targeted all-provider rerun passed in 24.228 seconds.
- A disposable parity probe using the independent component suite oracles and
  seed 20261014 passed 10,000 additional randomly chunked full-text/binary cases
  and 5,000 byte-first diff cases. It included partial prefixes, invalid UTF-8,
  all supported fake token forms and Unicode separators.
- `rtk proxy python3 -W error scripts/test-hook-diagnostics.py`: 8 tests passed,
  1.854 seconds.
- `rtk proxy python3 -W error scripts/test-hook-diagnostic-recovery.py -v`:
  10 tests passed, 10.206 seconds, including import-safe bootstrap and real retry.
- `rtk proxy python3 scripts/test-security-banners.py`: 14 tests passed,
  7.294 seconds.
- `rtk proxy python3 scripts/test-generate-hooks.py`: 26 tests passed,
  17.588 seconds, with the checkout frozen during snapshot assertions.
- All three provider Bash scanner suites passed, including their respective
  capture, race, malformed input, logging and no-HEAD checks. Codex returned exit
  zero directly; Copilot and Gemini were additionally chained with `&&` to obtain
  unambiguous exit-status evidence after an initial newline-separated batch
  exposed only the final shell status. No behavioral failure prompted that repeat.
- `rtk proxy python3 scripts/test-scan-secrets-merge.py -v`: all 33 tests passed,
  211.568 seconds. Includes long paths under the existing deadline, 250-file
  clean/final-secret merges, near-exact-cap conflict content, malformed framing,
  pinned singleton OIDs, hidden stages, unsafe worktrees and older-Git handling.
- `rtk proxy python3 scripts/generate-hooks.py --check`: 38 files current.
  `rtk git diff --check` passes.

## Limits and ownership

No full-process RSS or isolated latency benchmark ran. Functional capacity and
deadline tests do not establish that every arbitrary 8 MiB input finishes within
eight seconds. I2/V1 own resource and integration acceptance. No live home,
authenticated provider dispatch, native Windows execution, push or installation
was used. Existing non-atomic repository and platform/filesystem limitations
remain. Guardian/common/recovery protocol, manifest, registry, active plan and KB
were not changed. V1 owns registration of the new public suite. The coordinator
owns the single final knowledge-maintenance pass; no durable skill improvement
was identified.
