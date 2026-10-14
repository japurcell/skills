# T5b deny-only recovery evidence

Date: 2026-10-14. Task base: `79913f48`. Private branch:
`codex/hook-resilience-t5b`. This task implements scanner recovery; the coordinator
owns active plan, test registry, final knowledge maintenance, and integration.

## Delivered behavior

The canonical scanner embeds the self-contained diagnostics collector after the
required common transport import and before optional audit imports, policy
definitions, or candidate/Git/audit initialization. Only a running entrypoint
reads stdin during bootstrap; importing a scanner does not consume open stdin.
The normal path shares one lazy payload read, including bounded invalid/internal
input causes and the existing incomplete-scan reporting/logging path.

Recovery accepts the literal ASCII `hooks-diagnostics-v1` only. Codex requires
`PreToolUse`, `exec_command` or `functions.exec_command`, and
`{"cmd":"hooks-diagnostics-v1","login":false}`. Optional output/yield counters
are exact integers in 0 through 2,147,483,647; booleans are rejected. Native
Copilot uses `bash`/`toolArgs.command`, with `preToolUse` or the documented omitted
event name. Gemini requires `BeforeTool`, `run_shell_command`, and
`tool_input.command`. Copilot/Gemini arguments contain only `command`. Outer
native session/cwd/transcript/tool-use/timestamp metadata has fixed type/length
bounds; unknown fields, aliases, event shapes, execution options, and altered
commands take the ordinary scanner path.

The response is always native deny, exit zero, in block and warn modes. Its
reason starts `scan-secrets diagnostics (request not executed):`, followed by
JSON with `action=diagnostics`, `security_outcome=not_scanned`, `enforcement=deny`,
and `audit_outcome=not_attempted`. The standalone collector's existing independent
health fields remain intact. `diagnostics_encode(report, wrap=...)` budgets the
entire serialized native envelope plus newline, including escaped nested JSON
and Copilot's duplicated reason. It removes labels and lower-priority records
with explicit omission counts instead of truncating encoded bytes.

Collector authority is the loaded scanner's own `__file__`. Inventory always
uses process cwd. A different bounded payload cwd produces
`repository_location=unverified`; the supplied path is never resolved, opened,
or inventoried. Recovery runs no Git/subprocesses and reads no candidate bodies.
Missing/corrupt audit or Guardian policy helpers are reported without importing
them. Ordinary scans deny missing/corrupt audit import in both modes. Guardian
policy and suppression rules are unchanged and independently inspect requests.
Missing/broken common transport or interpreter remains a human standalone CLI
boundary. A Guardian failure may prevent a real provider from displaying the
scanner's denial reason.

## Public reproduction and retained failures

The first new public test used a real disposable Git repository, generated
scanner entrypoints, and an 8,388,609-byte candidate. It failed for all three
providers because the exact marker returned ordinary `file_bytes_limit`
incompleteness rather than diagnostic denial. It passed after embedding. The
fixture intentionally exceeds the future aggregate limit; the current 1 MiB
per-file cap and all acquisition/matcher semantics remain unchanged.

Initial scanner Bash runs exposed an unexpected common-reader exception escaping
the early bootstrap (return code 1 in each existing capture suite). The bootstrap
now retains the fixed `internal_error/input` cause and allows ordinary main to
emit/log its existing fail-closed result. No assertion was removed or weakened.

The first generator run retained 26 tests with 5 failures and 11 errors. T3 had
removed `is_text_candidate`/`read_candidate_bytes` and changed enumeration to
verified captures; old mocks therefore read real checkout metadata. T5b also
introduced provider diagnostics outside the old two-adapter parity boundary.
The coordinator authorized bounded generator fixture repairs:

- Classification and regular/escape/oversized/symlink probes now acquire/replay
  `SnapshotSource` snapshots, retaining content, classification, and exception
  assertions.
- Enumeration/file-count fixtures supply complete protected `VerifiedCapture`
  streams, retaining NUL-path, exact candidate, option, and limit assertions.
- Singleton staged-index proof verifies literal path selection, pinned OID-only
  batch-check/body requests, complete framing, and exact `token` content instead
  of asserting retired pathname-based `git show` calls.
- Diagnostic constants and native diagnostic response have explicit provider
  adapter boundaries. The scanner parity test expects exactly four adapters and
  compares every remaining shared section unchanged. Guardian still expects two.

A repair run caught the adapter-count update applied to the Guardian assertion
instead of the scanner assertion (2 failures, 0 errors); those exact scoped
assertions were corrected. Final generator checks pass. Full failure output was
retained during execution in disposable `/private/tmp/t5b-generator.log`; this
document retains the actionable failure categories independently of that log.

## Observed checks

- `rtk proxy python3 -W error scripts/test-hook-diagnostic-recovery.py -v`:
  10 tests passed, 12.766 seconds. Uses disposable copied installations, homes,
  audit/scan logs, real Git repositories, and `OBSERVABILITY_TESTING=1`.
  Cases cover overflow, unsafe candidate, Git/audit/log failures, missing/corrupt
  helpers, exact profiles and malformed/extended requests, Guardian appended
  dangerous operations, metadata bounds, fake marker/Git/startup/import
  sentinels, body/name token redaction, payload-cwd mismatch, complete wrapper
  bounds, import with open stdin, human CLI fallback, and real repair/retry.
- `rtk proxy python3 scripts/test-generate-hooks.py`: 26 tests passed,
  20.507 seconds, with source frozen during its snapshot assertions.
- `rtk proxy python3 scripts/test-hook-input-bounds.py`: 9 tests passed,
  34.006 seconds after import-safe bootstrap repair.
- `rtk proxy bash scripts/test-codex-hooks-secrets-scanner.sh`,
  `rtk proxy bash scripts/test-hooks-secrets-scanner.sh`, and
  `rtk proxy bash scripts/test-gemini-hooks-secrets-scanner.sh`: all passed after
  the unexpected-input repair, including provider capture/no-HEAD cases. A
  standalone Codex capture run also passed. The later import-safe refactoring
  preserves the exercised `__main__` path; final recovery/input/generator checks
  cover that change. No acquisition or matching behavior was changed here.
- `rtk proxy python3 -W error scripts/test-hook-diagnostics.py`: 8 tests passed,
  2.551 seconds after final source changes.
- `rtk proxy python3 scripts/test-security-banners.py`: 14 tests passed,
  8.817 seconds after final source changes. `scripts/generate-hooks.py --check`
  reports all 38 files current. `rtk git diff --check` passes.

## Limits and integration

Fake executable/startup/config/import sentinel tests prove source hook behavior
under trusted absolute Python `-I -S -B`; they do not authenticate host dispatch
or prove provider-visible combined denial display. No live home, real session,
credential, installed provider trust setting, or remote branch was used. Native
Windows, installed registration delivery, release performance, and final report
truncation work remain separate acceptance. No performance improvement is
claimed for this larger self-contained scanner bootstrap.

The standalone diagnostics outputs and embedded scanner metadata include build
digests over canonical hook source. Rebase onto the coordinator's T4a-containing
base requires serial regeneration of all three diagnostics and scanner outputs,
then affected checks. The manifest, Guardian policy, registry, and active plan
were not edited by this task. The coordinated final KB pass belongs to the
coordinator. No additional durable skill change was identified.
