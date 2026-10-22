# Bounded capture qualification

Local T4 evidence, 2026-10-21, macOS arm64. This is recorder/store API proof, not integrated milestone or native cross-platform acceptance.

## Runtime and commands

Working directory: `packages/software-factory` in the private `codex/factory-capture` worktree. Every Node command below used `/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/factory-qualified-node-i2fv29e3/node-v24.22.1-darwin-arm64/bin/node` (the qualified v24.22.1 binary), abbreviated `NODE` below. Development bootstrap was explicitly `rtk proxy npm ci --ignore-scripts --offline --cache /tmp/software-factory-npm-cache`: seven packages installed, zero audit findings; npm reported the ambient v24.21.0 engine mismatch, so no check used that ambient Node.

Observed commands:

- `rtk proxy NODE scripts/build.mjs`: exit 0.
- `rtk proxy NODE node_modules/typescript/bin/tsc --noEmit`: exit 0.
- `rtk proxy NODE node_modules/typescript/bin/tsc -p qualification/tsconfig.json`: exit 0.
- `rtk proxy NODE --test test/capture.test.mjs test/store.test.mjs test/fixtures.test.mjs`: final combined run 30/30 passed (15 capture, 11 existing store, four fixture checks), exit 0.
- `rtk proxy NODE --test test/capture.test.mjs`: 15/15 passed, including the final BOM slice, exit 0.

Red-before-green was observed at the public store/recorder seam: missing capture API; missing recorder; original-byte limit after shrinking redaction; partial failure marker; exact append retry; mixed JSON escapes/multiline secret; UTF-8 BOM retention. These failures were repaired without weakening existing tests.

## Public API and ordering

`new InvocationRecorder({store, invocationId, secrets?, requestShutdown, fallback?})` validates literal filter configuration before any persistence. Supply all known and configured secret values; this module does not read ambient credentials. One recorder owns an invocation's capture writers. `await recorder.openCapture({channel, attemptId?})` returns a writer with `id`. Channels are `stdout`, `stderr`, `result`, `request`, `report`, `event`, and `context`.

Await `writer.write(Uint8Array|string)`, or `await writer.consume(asyncIterable)` to propagate pressure to managed readable streams. `consume` finishes a successful source and saves partial state on an ordinary source error. Callers must await writes and avoid pre-buffering their own streams. `finish('complete'|'partial'|'unknown')` drains the UTF-8 decoder/filter, flushes shared pending text, and saves terminal capture state plus observation event. `recorder.barrier()` saves currently emitted text without closing streams; filter lookbehind cannot be released safely until more input or `finish`. Finish relevant streams before saving terminal execution facts, questions, ownership changes, or launch admission that depends on their contents. Terminal execution orchestration remains T6.

`writer.readResult(limit=1048576)` accepts an ended complete capture only, rejects original or filtered output larger than the explicit limit, reads bounded saved pages and returns parsed JSON. The configurable limit can be lowered from the initial 1 MiB ceiling. Parsing errors are generic and never echo input. Workflow envelope validation belongs to subsequent workflow/adapter tasks. Oversize output remains fully saved as filtered raw text, including ordinary reports larger than the parsing cap.

`store.createCapture({invocationId, attemptId?, channel})`, `store.appendCapture({id,chunks:[{sequence,text}],state?})`, and `store.readCapture({id,after?,limit?})` are the persistence boundary. The recorder is the untrusted-text filtering boundary; callers of low-level store append must supply already-filtered supported text. Append requires contiguous unique sequences. Exact already-committed sequences and matching terminal state reconcile without another event; conflicting text/state rejects atomically. Store reads return `open`, `complete`, `partial`, `unknown`, `pruned`, or `missing`, chunks, nextSequence and hasMore. A deliberate pruned marker is supported without an automatic deletion service.

`store.readEvents({after:decimalString,limit?})` returns committed metadata/reference events, decimal cursor strings, nextCursor and an explicit gap flag for an unavailable nonzero cursor. Invalid cursors reject. Callers rebuild saved facts on a gap; no execution is replayed. Both event and capture responses are at most 200 rows and below 1 MiB serialized JSON, without long-lived read transactions.

## Bounds and failure evidence

One shared invocation queue flushes by 256 KiB or begins flushing after 100 ms pending. Small decode steps and bounded lexical windows avoid full lines/JSON accumulation. Encoded chunks are at most 64 KiB; the recorder currently emits smaller chunks. UTF-16 tails, raw/decoded escaped-string windows, byte-width arrays, and a conservative processing allowance contribute to `bufferedBytes`/`peakBufferedBytes`, capped at 4 MiB. At most 32 simultaneously open capture writers bound decoder/filter state; exceeding this explicit resource bound fails closed. The queue is shared across writers, not multiplied by stdout/stderr. Config allows at most 128 literal values, 4096 UTF-8 bytes each, 64 KiB total; no user regular expressions execute.

Coverage includes byte-split Unicode, incomplete UTF-8, retained BOM, overlapping secrets across input/emission boundaries, escaped sensitive JSON key names, nested/primitive sensitive values, arbitrary whitespace, mixed Unicode escapes and ordinary multiline serialization, unchanged spelling of non-secret JSON, 2.2 MB lines, 1.2 MB structured output, original oversize hidden by redaction shrinking, duplicate/conflicting sequences, empty partial/unknown/pruned/missing details, invalid bounds and cursor gaps.

A real competing SQLite connection held `BEGIN IMMEDIATE` for 350 ms while stdout/stderr producers attempted 13 MiB of output. Producers remained backpressured, no append observation event appeared before commit, all text persisted after release, and reported buffers stayed below 4 MiB. Separate invocation recorders concurrently persisted independent text without changing allowance accounting. Existing eleven admission/owner/store tests retain single-debit race coverage.

A disposable child used the OS `RLIMIT_FSIZE` at 512 KiB to make real SQLite WAL writes fail. No storage mock or private store inspection was used. The recorder retained the previously committed prefix, kept committed events readable, rejected subsequent admission, invoked shutdown exactly once and produced one generic fallback. This proves an actual SQLite file-write failure boundary, not physical disk exhaustion or native Windows failure behavior. Upon failure, local admission blocks immediately, shutdown/fallback run before best-effort database work, and partial/shutdown facts are saved when storage permits. If storage refuses even those facts, existing open state and committed chunks remain honest incomplete evidence; no fallback reset, deletion or external launch occurs.

Schema bootstrap is version 2; opening older schema requires explicit future maintenance, with no automatic migration or history replacement. T16 owns forward maintenance and actual pruned-data deletion. Linux/Windows storage and file-limit behavior remain unqualified. No browser, live harness, notification, cleanup service, or release behavior was introduced.

## Source checks and reflection

SQLite result-code documentation confirms contention is storage handling and `BEGIN IMMEDIATE` isolates the writer transaction: [SQLite result codes](https://sqlite.org/rescode.html). Streaming UTF-8, fatal decoding and BOM behavior are verified on the pinned runtime by public recorder tests; the version-specific Node documentation fetch was unavailable, so no newer documentation is claimed as version-specific proof.

Reflection: durable failure-ordering, encoded-secret and Unicode-boundary lessons are enforced by public tests and runtime bounds. No separate brain note was needed; shared plan/brain updates remain coordinator-owned.
