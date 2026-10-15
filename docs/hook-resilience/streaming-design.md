# Streaming scanner and nonexecuting recovery design

D1 retained design, 2026-10-14, base `3976fcccd1cc0dfe92a7aab5bc2ff410717e8eff`. This resolves T3/T4/T5 interfaces in [the implementation ExecPlan](implementation-ExecPlan.md). D1 changes only this evidence document; the coordinator owns active plan updates and the final knowledge-maintenance pass.

## Decisions and source contract

T3 supplies verified, rewindable snapshots while retaining the 1 MiB policy. T4 supplies bounded matching and removes that ceiling, using the remaining 8 MiB aggregate allowance instead. Keep 256 snapshots, 8 MiB logical candidate content, 8 MiB per Git capture, eight seconds of scanner work, 100 retained findings and 1,000 processed unsuppressed findings. Replay/framing do not charge logical bytes twice. No cache, cross-provider import, atomic repository snapshot claim, or always-running service is introduced.

T5 recognizes an exact reserved tool request and **always denies its execution**, returning hook-owned diagnostics in the denial reason before candidate/Git/audit work. No executable receives an exemption. A fixed installed human-terminal CLI supplies out-of-band recovery when hook bootstrap/input fails; that CLI gets no agent execution exemption.

`hooks/families/scan_secrets.py` owns acquisition, classification, diff/matching and scanner logging. `hooks/families/common.py` owns JSON transport. `hooks/families/tool_guard.py` owns independent operation validation/Guardian. `hooks/families/allowlist.py` supplies exact suppression with an 8,192-character normalized input ceiling. All edits remain canonical and provider files generated. [The investigation](investigation.md) retains the original reproductions.

Compatibility requirements from current source:

- Each line runs patterns in this order: classic GitHub, fine-grained GitHub, AWS, Stripe, Slack. `finditer` is leftmost and nonoverlapping separately per pattern. Classic matches consume exactly 40 characters; AWS exactly 20. Fine-grained GitHub/Stripe/Slack have greedy unbounded suffixes. Failed minimum-length candidates may contain later valid starts.
- Any NUL anywhere selects binary. Otherwise strict UTF-8 selects text; invalid UTF-8 selects text only for current `TEXT_EXTENSIONS`. Full text uses replacement decoding. Binary projects each byte to ASCII, keeping HT/LF/CR/printable ASCII and replacing other bytes with spaces. A binary tracked candidate gets full projection even in diff scope, including bytes after NUL.
- Text gets full scanning in staged scope, unborn repositories, untracked snapshots, and unresolved stages/worktree. Ordinary tracked text in diff scope gets added Git lines, after charging the acquired full snapshot. Credential paths produce a separate first finding on line 1; `.env` alone remains informational.
- Full-content `str.splitlines()` recognizes LF, CR, CRLF, VT, FF, U+001C/U+001D/U+001E, U+0085, U+2028/U+2029. Empty input has no lines; terminal separator adds no synthetic empty line; consecutive separators retain empty lines. Diff first uses `bytes.splitlines()`, which recognizes only CR/LF/CRLF, then `os.fsdecode`. Do not apply a Unicode splitter to decoded diff content.
- Enumeration, acquisition and later Git diffs are not atomic. An opened descriptor prevents path replacement from selecting another file, but does not freeze concurrent same-inode writes. A spool freezes only the bytes observed during one acquisition.

## T3: acquisition interfaces and ownership

Keep internal types in the rendered scanner, rather than creating a runtime package:

These are behavioral contracts, not mandatory class proliferation. An implementer may combine/simplify private types while preserving range ownership, replay, charging and failure boundaries.

```python
@dataclass(frozen=True)
class Candidate:
    source: str
    path: str
    oid: bytes | None = None       # pinned for EVERY index snapshot
    size: int | None = None        # verified blob metadata

@dataclass
class ScanBudget:
    deadline: float
    used_bytes: int = 0            # never released on snapshot close
    def reserve_index(self, candidate: Candidate, size: int) -> None: ...
    def charge_worktree(self, byte_count: int) -> None: ...
    def remaining(self) -> int: ...

class VerifiedCapture:
    size: int
    def chunks(self, offset: int = 0, length: int | None = None,
               chunk_bytes: int = 65536) -> Iterator[bytes]: ...

@contextmanager
def capture_git(args: list[str], *, cwd: Path, deadline: float,
                input_bytes: bytes | None = None,
                allow_nonzero: bool = False) -> Iterator[VerifiedCapture | None]: ...

class Snapshot:
    candidate: Candidate
    byte_count: int
    classification: str           # "text" or "binary"
    def chunks(self, chunk_bytes: int = 65536) -> Iterator[bytes]: ...

@contextmanager
def snapshot_source(root: Path, candidates: list[Candidate],
                    budget: ScanBudget) -> Iterator[SnapshotSource]: ...

class SnapshotSource:
    @contextmanager
    def acquire(self, candidate: Candidate) -> Iterator[Snapshot | None]: ...
```

`SnapshotSource` owns at most one current index capture plus one active worktree spool. The `acquire` context lends a protected range and closes/discards individual snapshot state at exit. Index capture survives only until its last range is consumed, then closes before the next batch. `Snapshot` cannot outlive that context. Each `chunks()` call replays the same protected range from offset zero, yields at most 64 KiB, checks deadlines and exact EOF/range, and never reopens a worktree pathname. Only permitted missing unresolved-worktree content yields `None`.

`reserve_index` keeps a private candidate ledger to prevent double charging. Reserve every index size once before content requests; identical OIDs in different sources still charge separate snapshots. Worktree acquisition charges actual bytes once. Closing/replaying does not release/recharge the aggregate allowance. Existing `ScanFailure` causes remain the error vocabulary.

### Verified captures

Extract existing `run_git` process/capture logic, preserving owner-only regular `TemporaryFile`, bounded input, discarded stderr, prompt/askpass disabling, five-second Git deadline limited by the shared deadline, and POSIX/Windows completion/descendant checks. Yield `VerifiedCapture` only after accepted parent exit, descendant validation, final size/type/mode verification and bounded final output. Never inspect partial stdout as content or report clean from it. Retain independent unborn-HEAD/missing-ref checks and exact allowed empty nonzero cases.

On every exception, stop the process tree through `_stop_git_process` before closing capture; preserve Windows rescans and cleanup deadline. No stdout pipes, fixed polling sleeps, full `capture.read(size)` or blob slices. Small control calls may keep `run_git` as a wrapper, but blob/diff callers must consume captures incrementally after T4.

Parse NUL/newline metadata incrementally. Retain at most 256 candidate records, at most existing capture bytes overall, and bounded header state. Decimal metadata fields are at most 20 digits. Paths have a bounded record buffer under the existing capture ceiling; no `split(b"\0")` on full capture.

### Pin index objects, including singleton

Remove the singleton `:path` size/read shortcut. Resolve all selected stage-zero/conflict-stage paths using current literal `ls-files --stage -z` batches and 8,192-byte argv estimate. Preserve exact path/stage/duplicate checks, selected directory-descendant behavior, NUL termination and 40/64-digit object IDs. Store metadata only. `cat-file --batch-check` receives OIDs only; require exact IDs, `blob`, nonnegative size, record count/termination, and reserve logical index bytes before requesting bodies.

Fetch grouped bodies with verified `cat-file --batch` where complete framing plus bodies fit 8 MiB. Validate every expected header/body/separator/terminal offset before exposing any view. A view is `(protected capture, offset, length)`, not copied bytes. An individual blob too large to fit with framing uses `cat-file blob OID`; its raw capture must exactly equal checked size. This permits one valid 8 MiB blob without increasing the capture cap. Empty blobs retain valid empty views. Never use filters/textconv/path operands to fetch bodies.

Batch index candidates in existing candidate order, allowing intervening worktree candidates while the current capture remains alive. Only one index batch capture lives at a time; its last index view closes it. The shared ledger bounds combined retained candidate disk bytes to 8 MiB plus framing/control captures, even when a worktree spool coexists. Do not convert 250 index objects into 250 Git subprocesses or reorder findings for throughput. Measure the maintained 250-file case before accepting a batching change.

### Worktree spool and classification

Reuse descriptor-relative directory traversal, no-follow and regular/reparse checks. Add nonblocking open where supported so a path swapped to FIFO cannot hang between `lstat` and open; immediately `fstat` the opened descriptor before reading. Keep parent descriptors through acquisition. Preserve Windows/non-dir-fd checks and explicitly retain their ancestor-race limitation rather than claiming descriptor-level protection there.

Read once into a new owner-only regular `TemporaryFile`, in 64 KiB chunks. Precheck observed size against remaining allowance. Read at most remaining allowance plus one byte, rejecting the first extra byte as `total_bytes_limit/candidate_read`; this catches growth. Decreases/concurrent same-inode writes are the observed snapshot, not an atomic read. Close all descriptors/spools on every exit; permitted missing conflict worktree charges zero.

During acquisition, track NUL and strict incremental UTF-8 validity across the entire snapshot, including decoder EOF flush. After invalid UTF-8, retain the invalid flag without decoded content. Final classification uses NUL first, then UTF-8/extension rules. Index views run the same classification pass. Late markers are resolved before any token finding is emitted. Replay uses the same protected spool/range.

T3's effective snapshot ceiling remains `min(MAX_FILE_BYTES, remaining)`, retaining legacy `file_bytes_limit`. A temporary bridge may materialize ONE at-most-1-MiB snapshot for the unchanged matcher, but never all index blobs. T4 removes this bridge and only the 1 MiB ceiling after semantic proof.

Filesystem deadlines are cooperative. Blocking disk I/O can outlast a clock check. Keep the eight-second work budget but do not claim a strict process kill guarantee. If watchdog evidence exposes provider-timeout overruns, reopen a supervisor decision rather than treating checks as proof.

### T3 public tests and stop

Extend `scripts/test-scan-secrets-capture.py` and `scripts/test-scan-secrets-merge.py` through public generated entrypoints: malformed/partial captures, descendant-held outputs, exact framed boundaries, unsafe FIFO/symlink/reparse/directory reads, growth/replacement, singleton pinned ID under index edits, hidden staged content, every unresolved stage and missing permitted conflict worktree. Genuine credentials require findings; acquisition errors require incomplete, not merely any denial. Test block/warn where applicable.

Run both suites, all three scanner Bash suites and generation freshness. Stop after protected acquisition plus unchanged-detection compatibility under the old file limit. Matching, large-file policy, recovery and reporting remain separate tasks.

## T4: matching, ordering and diff replay

### Stream events

```python
# LineEvent: start(one-based line), data(bounded text fragment), end.
def full_line_events(snapshot: Snapshot, *, deadline: float) -> Iterator[LineEvent]: ...
def diff_added_line_events(root: Path, candidate: Candidate, *,
                           root_has_head: bool, deadline: float) -> Iterator[LineEvent]: ...
def scan_line_events(candidate: Candidate, events: Iterable[LineEvent],
                     allowlist: list[dict[str, str]], report: ScanReport,
                     budget: ScanBudget) -> None: ...
```

Full text replay uses incremental UTF-8 replacement decoding. Binary replay projects bytes in bounded chunks. The full-content splitter implements exactly the separator set above with one pending-CR flag and no complete-line buffer. Finish a pending line at EOF, without a synthetic empty final line. Text fragments stay bounded by one decoded 64 KiB chunk.

Diff uses a separately verified capture. Parse byte CR/LF/CRLF boundaries before filesystem decoding with `surrogateescape`; ASCII token semantics remain unchanged. Keep a short discriminator prefix, then stream added-line remainder as data. Discard nonsemantic filename/header content incrementally. Hunk headers use bounded decimal state, not a whole-line buffer; overlong/malformed numeric fields remain incomplete. Preserve current first `diff --git ` and final-LF checks, hunk recognition and counters: `+` emits/increments; `-` and backslash do not; context increments; unexpected content in a hunk is incomplete. Unicode separators inside decoded diff data do not start additional numbered lines.

Keep current diff arguments: zero context, no external diff/textconv/color, explicit output indicators and literal path operands. Classification uses the acquired full snapshot, although Git's later diff can observe newer state. Do not reopen the worktree or claim atomicity.

### Match machines

Use one explicit state machine per current pattern and a bounded tentative buffer. Fixed patterns retain at most their 40/20-character width, emit at the exact end and restart after the consumed span. Unbounded patterns recognize their literal prefix then explicit ASCII suffix class. Hold at most `prefix length + minimum suffix - 1` characters while proving minimum length. On failure, resume one character after the tentative start and replay that bounded buffer, preserving later starts which `finditer` would try. Once minimum length is reached, ignore same-pattern starts until delimiter, line end or EOF; finalize the complete greedy match. Search cursors are independent per pattern. A fixed overlap is not the implementation for greedy tails.

For a valid unbounded span retain character count, first/last four for current redaction, and complete value only while exact suppression remains possible. The suppression key is `path:line:pattern:full_match` with unchanged ASCII-space normalization/forbidden-separator checks and `allowlist_contains`. Because matches have no trailing spaces, available retention is `8192 - len(prefix.lstrip(" "))`; forbidden controls/escape separators in the prefix make suppression impossible. After the available length is exceeded, discard full value permanently and retain only count/redaction state until finalization. Never suppress by prefix, hash, redacted or truncated value. Keep no unbounded match strings or lines.

Concurrent pattern machines discover matches in another order than today's nested loop. For each current line, accumulate per-pattern summaries: first at most 100 unsuppressed redacted matches, and unsuppressed count saturated at 1,000. Apply exact suppression at match finalization. At line end, flush summaries in `PATTERNS` order, retain only to the global 100 limit and add processed counts only to the global 1,000 limit, stopping there. Do not update global processed count in discovery order. Credential-path findings consume the same global limits first. Counters/slots are bounded regardless of line length or suppressed-match count. This preserves reports when an early AWS match precedes a later GitHub match in text.

Future pattern additions must extend the explicit machine and parity fixtures. No unsupported regex silently falls back to chunk overlap.

Implement transitions with bulk bounded-chunk operations, not five Python per-character loops over 8 MiB. Use compiled prefix searches and suffix-class runs inside each bounded fragment, with the small tentative carry at boundaries. Use C-level separator searches and a byte translation table for binary projection. Empty/no-prefix fragments should advance line/state counts without per-pattern work on every character. Resource proof may require refinement, but cannot weaken regex or line semantics.

### Public T4 cases and stop

Add/register `scripts/test-scan-secrets-streaming.py`. Use all three generated entrypoints, real temporary Git repositories/homes/logs, `OBSERVABILITY_TESTING=1`, no inherited skip/allowlist overrides except suppression cases. Assert native decisions plus audit pattern/line/redacted ordering and no raw fake-token leakage. Proposed public test names and independent literal expectations:

- `test_single_2030848_byte_safe_candidate_allows`: reported one-file fixture allows; committed same-size text plus a 13-byte benign edit also allows in diff scope.
- `test_first_aggregate_overflow_denies`: exactly 8,388,608 logical bytes allows, next byte is `total_bytes_limit`; include a single exact-cap index blob proving framing is free. Snapshot 257 remains incomplete.
- `test_every_token_position_at_chunk_boundary`: split each prefix/minimum/fixed width at every position across 65,536-byte acquisition boundaries; delimiters/EOF/multiple matches preserve literal expected results.
- `test_greedy_suffix_does_not_allow_allowlisted_prefix`: complete short token is suppressed; same prefix plus long suffix is one unsuppressed match, including tails over 8,192 characters; first/last-four redaction stays exact.
- `test_nonoverlap_and_failed_prefix_restart`: repeated fixed matches in a suffix run preserve nonoverlap; later starts inside insufficient tentative candidates are found; different patterns overlap independently.
- `test_full_line_separator_matrix_and_utf8_boundaries`: exact line numbers for all text separators, split CRLF/codepoints, empty input, final separator, invalid replacement in text extensions. Unicode separators in added-diff data stay on one Git line.
- `test_late_binary_marker_replays_same_snapshot`: final NUL/invalid UTF-8 changes route; tokens after NUL and unchanged tracked tokens in projection are found; replacement/removal during replay cannot select new bytes.
- `test_line_pattern_order_and_caps`: earlier AWS/later GitHub reports GitHub first; 101/1,001 mixed unsuppressed tokens preserve retain/count/stop behavior; suppressed matches do not count.
- `test_full_diff_staged_unborn_and_merge_parity`: hidden staged/conflict secrets remain findings; unchanged tracked text secrets remain ignored in diff scope; untracked/unresolved worktree remain full-content.

Run new streaming tests, all three scanner Bash suites, capture, merge and banners. I2 owns full-process RSS/elapsed proof for a single 8 MiB line, newline-dense text, late-binary 8 MiB and 256 snapshots. D1 claims no resource improvement. Stop after semantic parity and remaining-aggregate policy adoption; reporting, diagnostics and installation stay T5/T6.

## T5: diagnostics without requested execution

### Exact reserved request and response

Reserve literal ASCII command `hooks-diagnostics-v1`, without whitespace, operands, wrappers, aliases, quoting, substitutions, punctuation or path. Recognize only after bounded JSON transport and exact supported event/tool/argument validation:

- Codex `PreToolUse`, tool `exec_command` or the explicitly supported fully qualified alias: `{"cmd":"hooks-diagnostics-v1","login":false}`.
- Copilot native `preToolUse`, tool `bash`: `{"command":"hooks-diagnostics-v1"}`. Do not guess PascalCase/Edit compatibility profiles.
- Gemini `BeforeTool`, tool `run_shell_command`: `{"command":"hooks-diagnostics-v1"}`.

Permit only T2-validated inert output/yield metadata. Reject custom shell, workdir/directory, environment, permission/escalation and unknown fields for this route. Outer session/timestamp/cwd use exact provider bounds and are never executable configuration. Inventory the hook process cwd; if envelope cwd disagrees, set `repository_location=unverified` and do not open the supplied arbitrary path. Unknown profiles use ordinary fail-closed handling. Compare marker before Unicode/whitespace normalization.

Return native **deny in block AND warn modes**, exit zero, with reason prefix `scan-secrets diagnostics (request not executed):`. Fields are `action=diagnostics`, `security_outcome=not_scanned`, `enforcement=deny`, and `audit_outcome=not_attempted` unless a bounded optional write succeeded. Never report clean/allowed/successful execution. The marker does not need to be installed or resolve on PATH. The user/model reads the report from the rejected tool call. Ordinary requests still require complete scanning and successful audit under existing policy.

Guardian independently validates/inspects the entire request under T2. No skip, input-budget bypass or marker allowlist is introduced. If Guardian itself fails, a real provider may surface its denial and hide scanner diagnostics; the human fallback remains necessary. Source subprocesses cannot prove authenticated host denial display.

### Execution identity and bootstrap

Authority stays in the already-loaded scanner, not the requested executable. Fake marker executables, mutable script substitution, shell startup/configuration, interpreter flags, environment assignments and appended commands cannot acquire trust: exact marker never executes, modified requests get ordinary handling. Prechecking a mutable script hash is a check/use race and is not execution identity. No arbitrary shell/read-only command is exempt, including Git status.

Move minimal route parsing, native response emission and collection before imports of `helpers.audit`/optional policy helpers and before candidate/Git/audit initialization. Keep canonical collector in `hooks/families/diagnostics.py`, embedded into generated scanner bootstrap and a standalone generated CLI, so recovery does not require another helper import. The bootstrap must not import repository Python modules. Common transport/interpreter failure can still prevent in-hook recovery. Ordinary requests import required helpers and fail closed.

Installed registration must launch the installer-selected absolute trusted Python executable with `-I -S -B` and absolute hook path, rather than rely on a repository cwd, PATH-resolved Python, site startup or an env shebang. Apply this to the recovery-bearing scanner and Guardian registrations in both installers, retaining owned-registration merge rules and unowned handlers. Bootstrap imports only stdlib before routing; ordinary provider-local helper imports are added explicitly afterward. Source subprocess tests already use isolated flags, so prove the actual installed command separately. Same-user ability to replace the trusted interpreter/installed hook remains outside tamper-resistance claims.

Embed a build digest over canonical family/provider/profile inputs and policy limits, excluding its own digest field. Report loaded embedded build separately from bounded no-follow on-disk installed asset hashes. On-disk hashes diagnose installation drift, not the already-loaded bytes or tamper resistance against the installing user. Missing/corrupt helpers produce degraded health but do not prevent bootstrap diagnostics.

### Strict metadata mode and bounds

Use **no Git subprocess and no candidate body reads**. This eliminates fsmonitor, external diff/textconv, pager, askpass, submodule and PATH/config execution from this collector. Do not reuse ordinary `run_git`. A conservative worktree metadata inventory finds large artifacts but cannot prove pending/ignored/tracked state or hidden index stages.

Walk process cwd through no-follow descriptor-relative directory access where supported; skip `.git`, symlinks/reparse points and unsafe directories. Use enumeration/stat only for candidate files. Unsupported platforms report limited access rather than fabricated race guarantees. Emit `kind=worktree_metadata`, enumeration IDs `candidate-0001` etc., regular sizes/unsafe type flags and `pending_status=unknown`. Counts are inventory counts, not complete pending snapshots. `.git/index` may be stat-measured but not parsed/opened, and objects are not opened. Index snapshot counts/sizes remain unknown; direct the human to index inspection if worktree sizes do not explain failure. Linked `.git` files produce `repository_layout=linked_or_unknown` rather than a claimed resolved repository.

Bounds: 1,024 directory visits, 4,096 entries, 256 retained file records, depth 32, 160 encoded bytes per sanitized label, one second collection work inside overall eight seconds, 16 KiB complete serialized response. Installed checks: at most 64 owned assets, 1 MiB total hash input and 256 KiB per settings file. Exceeding bounds reports fixed incomplete/omitted counts, never successful health. The 256 metadata retention limit is separate from scanner snapshots.

Prioritize largest regular files in the retained 256-record inventory using a bounded min-heap during enumeration; do not stop after the first 256 files. Reserve a small portion of slots for unsafe-type entries, and report both observed/omitted counts. Candidate IDs identify records within that report, not persistent repository identity. If enumeration/time limits stop collection, report `inventory_complete=false`; top-size ranking then applies only to the observed entries. Bound final serialization by dropping lowest-priority detail while preserving largest sizes, unsafe counts and incompleteness.

Scan bounded labels for token-shaped prefixes and URL/auth/password-like forms before clipping; replace uncertain labels wholesale with `[REDACTED]`. Escape/omit controls and invalid Unicode. IDs/sizes survive label omission. Never return raw paths, exceptions, commands, payloads, environment values or contents. No-follow bounded settings reads occur only at known installed config locations from fixed installation metadata. Report known provider/event and owned/unowned/duplicate counts, not registration command strings. Do not execute/delete registrations; reject includes/custom paths. Unknown/duplicate/malformed/missing registrations yield uncertain/failed health.

Keep bootstrap/files/registrations/repository/audit/security health separate. A diagnostic response does not prove scanner health or content inspection. Audit is unknown/not-attempted unless an optional bounded probe establishes a result without blocking recovery. Source and installed origins are distinct, and source subprocesses never claim installed execution.

### Human CLI and trust limit

Install standalone stdlib-only `hooks-diagnostics.py` beside each provider scanner. Parser accepts exactly no operands (metadata in current directory), `--doctor` (installed assets/registrations only), or `--help`; all other arguments exit 2 with fixed usage. No command/path/shell/environment/config operands or subprocesses. Installer supplies fixed installation metadata.

Document human invocation using a chosen trusted absolute Python executable, `-I -S -B` and absolute installed CLI path from an ordinary terminal. No `python -m`, `env`, or agent exemption. Isolated Python excludes repository module paths, PYTHONPATH and site startup. Ordinary hooked agent invocation may still be denied. The human owns terminal/interpreter/installation trust; fingerprints and owner-only checks diagnose drift but cannot resist an attacker who can replace the installing user's executable/files. Corrupt CLI requires reinstall from trusted source. The CLI's fixed data behavior grants no reusable execution permission. Missing scanner/audit helpers do not prevent CLI reports; unavailable metadata yields bounded incomplete.

### T5 public tests and stop

Add/register `scripts/test-hook-diagnostics.py` using generated scanner/Guardian entrypoints and disposable installed homes:

- `test_marker_denies_without_execution`: fake basename executable writes sentinel; each native envelope returns denial/report/not-scanned and never writes sentinel.
- `test_candidate_audit_git_failure_preserves_report`: 8 MiB-plus-one, unreadable/unsafe candidate, unwritable audit and missing Git deny ordinary calls; exact request returns bounded metadata without clean claim.
- `test_repository_config_and_imports_never_execute`: fake Git/PATH/shell-startup/Python import/config handlers produce no sentinels; candidate contents/tokens after NUL never enter metadata output.
- `test_spoofed_extended_request_is_ordinary`: paths, Python/env wrappers, arguments, whitespace, semicolon/substitution, Unicode lookalikes, unknown profile/tool, execution context/permission fields do not take recovery route. Dangerous appended operations remain Guardian denials.
- `test_missing_corrupt_helpers_degrade_bootstrap`: optional audit/policy removal permits scanner bootstrap report, ordinary scanner/Guardian fails closed; broken common/bootstrap requires human CLI and is not counted as successful in-hook recovery.
- `test_metadata_doctor_bounds_redaction`: hostile names, 4,097 entries, giant/malformed settings, missing assets, duplicate/unowned handlers produce bounded incomplete/uncertain without config mutation.
- `test_cli_fixed_parser_isolated_imports`: exact modes only; rejected arbitrary operands; repository json/sitecustomize/PYTHONPATH ignored under isolated launch; corrupt scanner helpers/inaccessible repo yield bounded report.
- `test_repair_retry_requires_real_scan`: ordinary failure, diagnostic denial, fixture/human repair, then genuine clean allow; fake secret yields findings denial. Diagnostic health never substitutes for enforcement.

Run diagnostics, Guardian native/shell/limits/banners, generated freshness and disposable installer/config-merge checks. Stop after public workflow and isolated installation proof. Native Windows/authenticated provider dispatch are distinct acceptance, especially combined hook denial display. T6 owns general report/audit truncation.

### Optional coordinator task split

T5a can run alongside T3: own `hooks/families/diagnostics.py`, standalone generated CLI targets/build metadata, manifest/installer registration and asset delivery, isolated CLI/install tests, and usage evidence. Prerequisites are D1 and current installer contracts. Do not edit scanner/Guardian canonical source or route requests in T5a. Stop when the fixed data-only CLI and isolated installed launch/doctor evidence pass; do not claim in-hook recovery.

T5b follows integrated T1/T2/T4 and T5a: own scanner bootstrap embedding, exact reserved profile recognition/native denial, dependency-order changes, and full provider recovery workflow tests. Guardian policy stays independent. Regenerate shared outputs serially at integration. T5b acceptance requires ordinary fail-closed versus diagnostics denial, no marker execution and no false clean/health claim. The coordinator records this split in the task graph if used; this document does not silently change task ownership.

## Observed D1 evidence

No runtime implementation or resource improvement is claimed. Canonical scanner/common/Guardian/allowlist, capture/merge/banner tests, hook security/testing rules and retained provider references were inspected at the stated base.

Direct Python probes confirmed the text/byte splitlines separator difference and empty/final-boundary behavior. These existing public tests passed across all three providers (four tests, 7.421 seconds):

```text
rtk proxy python3 scripts/test-scan-secrets-merge.py \
  MergeScannerTests.test_batch_binary_and_empty_blobs_keep_content_boundaries \
  MergeScannerTests.test_batch_keeps_staged_secret_when_worktree_matches_head \
  MergeScannerTests.test_batch_diff_ignores_unchanged_secrets \
  MergeScannerTests.test_secret_in_theirs_is_detected_after_worktree_replacement -v
```

A disposable real-Git/generated-entrypoint probe using the same suite fixture created one benign 2,030,848-byte untracked `large.txt`. Copilot/Gemini/Codex each returned `file_bytes_limit` and audit `status=incomplete`. This is T4's retained red behavior, not a claimed successful result.

D1 stops here. Dependent tasks obtain their own public red/green/resource/installed evidence. Changes to these interfaces or the deny-only diagnostics boundary require reconciliation of this evidence and the active plan before implementation proceeds.
