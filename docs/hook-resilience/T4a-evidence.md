# T4a bounded stream component evidence

Implemented 2026-10-14 on private branch `codex/hook-resilience-t4a`, based on `d2356309`, in `/Users/adam/.codex/worktrees/hook-stream-matcher/skills`. This is the inactive component specified by [the streaming design](streaming-design.md). The coordinator owns the active ExecPlan and final coordinated knowledge-maintenance pass.

## Outcome and scope

`hooks/families/scanner_stream.py` exports self-contained `SOURCE` for embedding into the generated scanner. It imports only Python standard-library modules, requires no runtime package import, and does not acquire snapshots or invoke Git. Existing public scanner behavior and its 1 MiB limit are unchanged until T4b integration. D1's public 2 MiB reproductions remain unresolved by this component alone.

The component preserves full-text `str.splitlines()` separators and UTF-8 replacement decoding, binary byte projection, byte-first CR/LF/CRLF diff splitting and filesystem surrogateescape decoding, fixed-width nonoverlap, greedy complete suffixes, exact normalized allowlisting, first/last-four redaction, and line/pattern report ordering. It retains at most 100 findings and processes at most 1,000 unsuppressed findings across caller-owned reports. Empty full-content lines advance numbering without allocating events or matcher states.

## T4b interface

Embed `scanner_stream.SOURCE` during rendering. The embedded declarations are:

```python
full_line_events(chunks, classification, check_budget=lambda: None)
diff_added_line_events(chunks, check_budget=lambda: None)
StreamReport(findings=None, processed=0)
scan_line_events(path, events, report, is_allowlisted, redact,
                 check_budget=lambda: None)
```

`chunks` is a one-pass iterable of verified `bytes` fragments, each at most 65,536 bytes. Full-content classification must already be resolved across the entire acquired snapshot and is exactly `"text"` or `"binary"`. T3's protected snapshot or verified capture supplies `.chunks()`; the component never reopens a pathname. A `check_budget()` callback takes no arguments and raises the caller's existing deadline failure. It runs during decoding, parsing, event consumption, and match finalization; errors propagate.

Events are `("start", one_based_line)`, `("data", bounded_string)`, and `("end", None)`. No full line is materialized. Empty full-content lines produce no events because they cannot match current patterns. Diff-added empty lines still produce start/end and advance Git numbering. Unicode separators inside added Git data remain within that Git line.

`report.findings` uses existing `(pattern_name, severity, path, line_number, redacted)` tuples. `report.processed` and `report.stopped` are updated in legacy pattern order at line end. Insert a credential-path finding into the same findings/count first, then construct or update the report. Reuse it across candidates. After reaching the finding cap, remaining current events are drained without matching so late malformed diff output and budget failures remain visible. The caller can stop acquiring subsequent candidates when `report.stopped` is true.

Pass `is_allowlisted=lambda key: allowlist_contains("scan_secrets", key, allowlist)` and the existing `redact_match` helper as `redact`. Match values are retained only while their normalized exact key can fit 8,192 characters. Forbidden prefix controls/escaped separators and overlong keys cannot suppress. Redaction receives a bounded synthetic value with the exact first/last four; all supported token lengths exceed eight.

Malformed diff framing, hunk content, missing hunk numbers, or numbers exceeding 20 digits raise `StreamDiffError` (a `ValueError` subclass). Map this to existing `git_output_invalid` / `git_diff`; catch it around event consumption because parsing is lazy. Final LF and initial `diff --git ` checks cover the full consumed capture. Other invalid component inputs raise `ValueError`. No failure is converted to a clean result.

## Bounds and implementation evidence

Separator searches and regex candidate/suffix runs operate in C over bounded fragments. Each fixed machine carries fewer than its 40/20-character width. Each greedy machine carries fewer than its minimum 31/24/15-character width before proof, then keeps count, first/last four, and at most the available exact-allowlist value. It discards that value permanently when suppression becomes impossible. No whole-line array or unbounded token buffer exists. Per-line per-pattern summaries keep at most 100 redactions and a count saturated at 1,000. Once one pattern has 1,000 unsuppressed matches, it stops further matching on that line.

Diff headers retain an 11-byte discriminator and at most 20 decimal digits; other header content is discarded incrementally. Decoder carry is bounded by its codec. Data events are split back to 65,536 characters even when pending invalid UTF-8 bytes expand a decoded fragment. Allowlist prefix keys are allocated only when normalized prefix length leaves room under 8,192 characters; leading ASCII spaces are skipped by a C-level search without copying an unbounded path.

The focused test exercises a generated 4 MiB greedy single line while tracing allocations and asserts peak component allocations below 1 MiB. It also consumes 8 MiB of empty lines and asserts zero emitted events. These are component bounded-state assertions, not whole-process RSS or eight-second scanner acceptance. No concurrent benchmark was run; the coordinator owns isolated I2/V1 resource proof.

## Verification

From the managed worktree root:

- `rtk proxy python3 scripts/test-scan-secrets-stream-component.py`: 12 tests passed. Tests use independent legacy regex/finditer, full `splitlines()`, and byte-diff oracles; exhaustive token/separator/diff split positions; 300 deterministic randomized bounded inputs; invalid UTF-8/EOF; binary projection; fixed nonoverlap and failed-prefix restart; greedy allowlisted-prefix extension beyond 8,192; exact normalization/forbidden prefixes; mixed pattern/cap ordering; credential-path count consumption; surrogateescape; malformed diff tails after the finding cap; deadline propagation and chunk rejection.
- TDD red observations: missing line-event source, missing report/matcher interface, missing diff interface, and late malformed diff tail hidden after the finding cap. The late-tail test failed with `StreamDiffError not raised` before draining was added and passes afterward.
- `rtk proxy python3 scripts/generate-hooks.py --write`: only the three generated diagnostics CLI `DIAG_BUILD` lines changed, because their canonical-source digest includes the new component. No generated scanner source changed.
- `rtk proxy python3 scripts/generate-hooks.py --check`: passed, all 38 generated files current.

The new suite is intentionally not registered in `scripts/test-all.py` in this task, as assigned. T4b/coordinator owns maintained registry integration, public scanner suites, acquisition integration, and larger-file policy adoption. No live installation, authenticated provider run, or native Windows claim is made here.
