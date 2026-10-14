# T10: Preserve hardening while removing measured overhead

T10 implements the accepted D2 design on private branch `codex/hook-resilience-t10`. Production source and focused tests are frozen at `864bbda0cc59cc7ae44ee814d343765525562700`, based on `ef7a31e4`. Focused checks, all 28 affected suites and all 18 representative timing comparisons passed. Both independent review axes accepted this source without new required findings. Release acceptance remains V1's responsibility.

## Reproduced regression before implementation

With the coordinator's exclusive quiet window, the maintained verifier compared the unchanged repair checkout against exact baseline `bc52d7d69aaa046ea97e323879402241a01fead7`, extracted at `/private/tmp/hook-resilience-v1-phase2/baseline`. Python was `/Users/adam/.pyenv/versions/3.14.6/bin/python3`, Python 3.14.6, on native macOS 26.7.1 arm64.

The exact six cases were `copilot.guard.clean`, `copilot.guard.writer.chars-8787-segments-183`, `gemini.guard.write.utf8-growth`, `codex.guard.write.examples.md`, `codex.guard.write.examples.test.py`, and `codex.guard.search.literal`. The command was:

    rtk proxy python3 scripts/verify-hook-release.py --baseline-root /private/tmp/hook-resilience-v1-phase2/baseline --candidate-root /Users/adam/.codex/worktrees/hook-performance-repair/skills --case copilot.guard.clean --case copilot.guard.writer.chars-8787-segments-183 --case gemini.guard.write.utf8-growth --case codex.guard.write.examples.md --case codex.guard.write.examples.test.py --case codex.guard.search.literal --output /private/tmp/hook-resilience-t10-before.json

It exited 1 with three failed comparisons among 18. Raw samples, first launches, native outputs, completed audit logging, bytecode checks, fingerprints and pair variation are retained in that JSON. `errors` is empty, `sources_unchanged` and `baseline_archive_verified` are true. All six cold comparisons passed. These failures remain retained regardless of later outcomes:

| Case and phase | Median delta | p95 delta | Result |
| --- | ---: | ---: | --- |
| Copilot clean, warm pair 1 | +2.552 ms | +2.666 ms | Failed +2 ms median allowance |
| Copilot writer, warm pair 2 | +2.845 ms | +3.355 ms | Failed +2 ms median allowance |
| Gemini UTF-8 write, warm pair 2 | +2.934 ms | +4.848 ms | Failed +2 ms median allowance |

The procedure uses two alternating warm pairs, 25 measured samples and three warmups, and 25 independent cold copies/homes per case and condition. It checks decisions and completed logs outside measured elapsed time. Warm allowances remain +2/+5 ms median/p95, cold +5/+10 ms. OS and standard-library caches stay uncleared. The original V1 89/468 failed observations and D2 evidence remain operative; this repeat does not replace them.

## Implementation and preserved boundaries

`hooks/families/common.py` now attempts an immediate POSIX nonblocking read and restores the original descriptor flag in `finally`. EAGAIN uses the existing bounded readiness helper, whose POSIX `select` import is deferred. Windows retains `PeekNamedPipe` authority. Timeout `None` and EOF `b""` remain distinct. Acquisition and drain use the adapter, and drain checks the total deadline before another read.

The collector uses the fixed byte regex to visit structural markers only. Marker positions distinguish an adjacent escaped marker from an escape already consumed by ordinary bytes. Only a terminal backslash carries between chunks. The object root, mismatched closers, depth policy, whitespace before/after the object and UTF-8 decoding remain checked; `json.loads` remains the full syntax validator. Input caps remain 2 MiB raw bytes, depth 64, chunks of 65,536 bytes, idle 0.5 seconds and total two seconds. Scanner work retains its shared eight-second budget.

`hooks/families/reporting.py` normalizes and bounds the label before the ASCII-only lowercase substring prefilter. Every conservative D2 trigger is present and matched anywhere in the label. Every potential trigger and all non-ASCII normalized labels use the original unchanged regex; the safe branch returns `report_text(text)`. AST/source comparisons confirm unchanged `report_text`, `report_json_bytes`, credential regex, Guardian canonical policy and scanner canonical source. Generated build identities change with their trusted canonical inputs. No known-tool exemption, profile change, report-cap relaxation, attribution change or audit-failure exception was added.

## Red and green proof

The approved descriptor-adapter seam supplements public generated JSON entrypoints. Before implementation, `rtk proxy python3 scripts/test-hook-input-bounds.py StdinChunkTests` failed four tests with 12 subtest errors because `_read_stdin_chunk` did not exist. After adding the helper, all four passed. The later `test_expired_trailing_drain_never_attempts_another_read` failed once because my initial drain called the adapter before checking the deadline. Moving the deadline check before the read made it pass in the final transport suite.

Final focused runs:

| Command after `rtk proxy` | Result |
| --- | --- |
| `python3 scripts/test-hook-input-bounds.py` | 17 passed, 49.964 s |
| `python3 scripts/test-security-reporting.py` | 14 passed, 70.855 s |
| `python3 scripts/test-generate-hooks.py` | 26 passed alone, 18.241 s |
| `python3 scripts/generate-hooks.py --write`, then `--check` | Canonical outputs current, 38 targets |
| `git diff --check` | Passed |

The independent transport oracle parses 196 literal/generated inputs with standard-library JSON and an explicit decoded-container depth policy at chunk widths 1, 2, 3, 7, 64 and 65,536: 1,176 outcomes. It does not reproduce the new lexer. Public retained-pipe cases cover escape parity, structural-looking string data, long ordinary spans, split UTF-8 and an executable control after the string. Existing public tests retain first-byte/incomplete/total deadlines, raw/depth limits, trailing data, bounded drain and open-stdin completion. Descriptor controls cover immediate data, EOF, timeout, EAGAIN readiness and read/readiness exceptions, including both original POSIX flag states for data, timeout and errors. A simulated Windows adapter control proves readiness is consulted without the POSIX flag API; it is not native Windows execution evidence.

Reporting cases cover all 22 conservative trigger substrings in mixed-case embedded labels, nonmatching trigger words, dotless/dotted Unicode ignore-case behavior, NFKC forms, tokens crossing display clipping positions, block/warn/clean outcomes, completed log writes, byte ceilings and audit failure. Scanner `sessionId` is the public seam for every report-label family. Existing Guardian embedded identifier controls remain intact.

Two test-authoring corrections are retained explicitly. The initial new label cases assumed every Guardian tool label used `report_label`; nonidentifier/Unicode labels use Guardian's pre-existing separate sanitizer, producing 138 expectation failures. The tests were moved to scanner `sessionId`, the owning public seam, and passed before the prefilter edit. A subsequently added native-decision adapter omitted Gemini's literal `decision: deny`, producing 22 assertion failures even though logs correctly recorded denial; that test adapter now recognizes the native value. Production sanitizer behavior was preserved. No old test was removed or weakened.

The first generator run reported three intentionally changed common-body snapshot digests and five sandbox `PermissionError` failures while attempting its temporary in-checkout fixture mutations. The three reviewed common-body digests were updated for the canonical changes. An authorized isolated run passed 26 tests. After the deadline-order repair changed common again, the final snapshots and isolated 26-test run above were repeated. No source mutation or other test ran during that final generator run.

## Affected consumers and timing

All 28 additional affected suites passed sequentially, totaling 443.377 seconds. Per-suite commands, elapsed time and exit status are retained at `/private/tmp/hook-resilience-t10-tests/results.json`; full output is retained beside it and in the compact archive below. The driver sets only a disposable generic `OBSERVABILITY_LOG_PATH` fallback, preserving fixture/provider-specific overrides. It does not install live hooks.

The additional commands, each run under `rtk proxy`, are `python3 scripts/test-security-banners.py`, `python3 scripts/test-tool-guard-native-data.py`, `python3 scripts/test-tool-guard-shell-data.py`, `python3 scripts/test-tool-guard-limits.py`, `python3 scripts/test-tool-guard-false-positives.py`, the three provider Tool Guardian Bash suites, `python3 -W error scripts/test_helpers.py`, `python3 scripts/test-hook-diagnostics.py`, `python3 scripts/test-hook-diagnostic-recovery.py`, `python3 scripts/test-scan-secrets-stream-component.py`, `python3 scripts/test-scan-secrets-streaming.py`, all three ordinary scanner/capture Bash suites, both observability Bash suites, all three startup Bash suites, all three provider OKF Bash suites, both auto-ingest Bash suites and both RTK forwarding Bash suites. `checks.py` and `tests/results.json` in the archive give every exact command. The final `python3 scripts/generate-hooks.py --check` passed with 38 current targets, and runtime source still matched the frozen commit after all suites.

The unchanged expensive merge-acquisition suite is not being repeated solely for this parser change. T10 leaves canonical index/merge/Git acquisition source untouched. Public transport, ordinary scanner/capture, streaming, recovery and diagnostic coverage exercise the changed input/report boundaries. Existing merge evidence remains separate and reusable for unchanged acquisition; a fresh full merge run is not claimed here.

After the coordinator confirmed all semantic checks and independent review probes had stopped, the same maintained exact six-case command ran once with output `/private/tmp/hook-resilience-t10-after.json` against the real generated repair. It exited 0: all 18 comparisons passed, `errors` is empty, `sources_unchanged`, `baseline_archive_verified` and `gates_met` are true. All warm, cold and separate concurrency logging checks report `completed`; all 300 cold launches began with zero provider bytecode. The following numbers are candidate-minus-baseline median/p95 deltas in milliseconds:

| Exact case | Warm pair 1 | Warm pair 2 | Cold |
| --- | ---: | ---: | ---: |
| `copilot.guard.clean` | +1.079/+2.767 | +1.088/+1.391 | +1.357/+1.694 |
| `copilot.guard.writer.chars-8787-segments-183` | +0.690/+0.626 | +0.552/+0.223 | +1.296/+0.932 |
| `gemini.guard.write.utf8-growth` | +0.544/+0.872 | +0.821/+0.901 | +1.056/-0.418 |
| `codex.guard.write.examples.md` | +0.729/-0.354 | +0.733/+0.653 | +0.856/+4.265 |
| `codex.guard.write.examples.test.py` | +0.736/+0.640 | +0.813/+1.550 | +1.490/+3.129 |
| `codex.guard.search.literal` | +0.822/+1.009 | +0.702/+0.228 | +1.322/+0.681 |

`release_acceptance_eligible` is false because exact case filters were used. These results do not supersede the original V1 failures. No full 156-case timing or 108-case resource run occurs in T10. Native Windows, authenticated provider dispatch, installed delivery, full performance acceptance and the coordinator's final knowledge-maintenance pass remain outside this evidence.

## Retained artifacts

[Compact T10 evidence archive](T10-evidence.tar.gz): 37 members, 53,304 bytes, SHA-256 `29295dd723de8dae6352214e1feb7b4c2f9c05593d1adea0a5bf171a095b25ea`. `SHA256.json` hashes every other member and was verified after archive creation. It retains exact before/after timing JSON including failed observations and raw samples, all 28 additional suite logs and results, final reporting/generator logs, static invariants, the sequential test driver and explicit provenance. Terminal-only descriptor/deadline red controls and final transport results are summarized as such in `README.json`; no reconstructed full transcript is presented as raw output. Working files remain under `/private/tmp/hook-resilience-t10-*` until integration/release verification finishes.
