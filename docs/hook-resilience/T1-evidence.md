# T1: bounded shared hook input transport

Completed focused source proof on 2026-10-14 in the isolated managed worktree `/Users/adam/.codex/worktrees/hook-transport-bounds/skills`, private branch `codex/hook-resilience-t1`, from `3976fccc`. No live home installation or push was performed. The coordinator owns integration, the active ExecPlan, the test registry, and final knowledge maintenance.

## Reproduction and repair

Before editing source, public Copilot Guardian with retained stdin and either no bytes or `{"toolName":` stayed alive at the 1.5-second watchdog with no stdout. The first dedicated regression failed in all twelve Copilot/Gemini/Codex Guardian/scanner combinations for empty and incomplete retained input. Existing investigation evidence independently retained the longer 10,507 ms reproduction.

The shared renderer `hooks/families/common.py` now supplies all four provider common helpers with a 0.5-second first-byte/incomplete idle window, a nonextendable two-second input deadline, a 2,097,152-byte raw ceiling, and maximum nesting of 64 containers including the outer object. The byte ceiling reserves six-byte JSON escape expansion for 256 KiB of native input and 512 KiB for envelope/metadata overhead. The tests exercise maximum native inputs with 500 KiB metadata and measured raw envelopes of 2,084,669 bytes for Copilot, 2,084,642 for Codex, and 905,181 for Gemini.

The reader scans each acquired byte once for string escapes and balanced container boundaries, accumulates bounded chunks, and performs one UTF-8 decode and one JSON parse. It no longer repeatedly parses growing prefixes. Complete JSON returns with stdin open. Buffered trailing data receives the same byte/deadline budget and must be JSON whitespace. A producer cannot extend the drain indefinitely. Bytes written after the reader observes an empty readiness snapshot are outside this established completion boundary; this change does not claim to inspect future bytes.

Finite EOF is immediately readable and does not incur the idle delay. Windows still uses `PeekNamedPipe`, avoiding pre-3.12 nonblocking-pipe limitations. Broken-pipe EOF and regular-file stdin are distinguished from readiness failures; failures propagate through the existing native security denial paths. Runtime streams without a usable descriptor fail closed instead of falling back to an unbounded `.read()`.

The two-second budget covers input acquisition and boundary scanning. It is not a universal whole-hook filesystem/process deadline or a measured peak-memory guarantee. Guardian classification and scanner content/candidate policy were not changed.

## Public proof and compatibility

`rtk proxy python3 scripts/test-hook-input-bounds.py` passed all nine tests, containing 111 public Guardian/scanner subprocess exercises across Copilot, Gemini, and Codex, in 32.792 seconds. Assertions cover native denial and scanner `scan incomplete` / `input_invalid/input`, rather than exit status alone:

- Empty/incomplete retained stdin, including a partial UTF-8 sequence.
- A slow trickle every 0.1 seconds that cannot extend the total deadline past the 2.8-second external watchdog.
- Raw overflow, depth 65, malformed syntax, invalid Unicode escape/UTF-8, a second JSON object, and buffered non-whitespace trailing data.
- Complete open stdin, split UTF-8, split exponent notation, and depth 64 compatibility.
- Maximum escaped native data plus metadata headroom.
- Exact 2 MiB and first-byte overflow with all trailing bytes already available through regular-file stdin.
- Concurrent continuous whitespace production cannot prevent completion within the external watchdog.
- Finite incomplete input denies within the 0.45-second watchdog, without the 0.5-second idle tax.

The regular-file transport fixture lives inside the disposable repository's `.git` directory so it cannot become an unrelated scanner candidate. Per-provider audit paths are isolated because Gemini uses a directory where Copilot/Codex use a file.

Additional observed passing checks:

- `rtk proxy python3 scripts/test-tool-guard-native-data.py`: 22 tests, 7.360 seconds on final source.
- `rtk proxy python3 scripts/test-tool-guard-limits.py`: 18 tests, 9.223 seconds on final source.
- `rtk proxy python3 scripts/test_helpers.py`: 16 tests.
- `rtk proxy bash scripts/test-codex-hooks-startup.sh`: passed, including incomplete/open-stdin/fragmented-number checks.
- `rtk proxy bash scripts/test-hooks-okf-lint.sh`: passed GitHub adapter contract.
- `rtk proxy bash scripts/test-hooks-observability.sh`: passed, including the Windows `PeekNamedPipe` simulation.
- `rtk proxy bash scripts/test-gemini-hooks-observability.sh`: passed on serial retry, including `MOCK_FCNTL_OK` and additional observability scenarios.
- `rtk proxy python3 scripts/test-generate-hooks.py`: 26 tests, 12.208 seconds on final source, with checkout edits paused.
- `rtk proxy python3 scripts/generate-hooks.py --check`: all 35 generated targets current.
- `rtk git diff --check`: passed.

The coordinator explicitly authorized updating only the three common-helper hashes in `scripts/test-generate-hooks.py` after intentional runtime changes were verified. Audit snapshots and unrelated generator assertions were preserved. Generated files were refreshed only through `scripts/generate-hooks.py --write`.

## Retained failures and remaining acceptance

The observability suites initially caught a changed shared trailing-input error message. The reader's `ValueError`/`OSError` are now wrapped by `read_json_input()` in the established `Invalid hook input: expected a JSON object` error; transport causes remain chained internally. Both affected suites passed after this repair.

One Gemini observability run later failed while removing its disposable fixture with `Directory not empty`, without a preceding behavioral assertion failure. A serial rerun passed. The original cleanup failure is retained here; it is not native Windows or installed-delivery evidence, and a recurrence should be investigated as fixture cleanup concurrency.

Native Windows execution, authenticated provider dispatch, and deployed installed copies were not exercised. The maintained 500 ms finite-input resource gate and matched warm/cold timing remain pending coordinated V1: the coordinator deferred them because other workers were active, which would invalidate isolated timing. No performance or RSS acceptance claim is made from these functional watchdogs. The new suite still needs coordinator registration in `scripts/test-all.py`; T1 intentionally did not edit that shared registry or the active ExecPlan. Final coordinated K1 knowledge maintenance remains with the coordinator.
