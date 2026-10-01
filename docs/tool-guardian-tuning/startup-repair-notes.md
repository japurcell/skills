# Shared helper startup repair

The retained full guardian process measurements failed the no-regression gate.
This follow-up moves the common helper's `subprocess` import into `run_command`,
the only function in that helper that launches a process. Guardian uses the
common input/output helpers but does not call `run_command`. Static type checking
still sees `subprocess` through a normal `TYPE_CHECKING` import; postponed return
annotations retain the same spelling. No loader, proxy, dependency, or policy
change was introduced.

All four provider-local common outputs were regenerated from
`hooks/families/common.py`. The function still uses `subprocess.run` with the same
argument list, cwd, environment, check, capture, text, timeout, and `shell=False`
values. String and bytes command arguments still raise `TypeError`. Windows
executable lookup remains delegated to the standard library. JSON input readers,
open-stdin completion, UTF-8 output, audit capture, and provider adapters were not
edited. The generator test requires exactly the three import placement changes
and preserves the historical byte fingerprints for everything else, including
the readers. Audit fingerprints remain unchanged.

## Retained failure and illustrative diagnosis

The existing whole-entrypoint reports used 25 samples, 3 warmups, and concurrency
4. The two baselines' clean warm medians were 30.097/26.887 ms for Copilot,
28.634/27.724 ms for Gemini, and 25.955/25.715 ms for Codex. Failed shell candidate
2 measured 32.382, 32.732, and 29.908 ms respectively. Candidate 1 also failed the
gate. These failures remain retained, rather than being replaced by the import
diagnosis.

One fresh `python3 -X importtime` invocation of each clean public guardian
entrypoint attributed 2.428, 2.506, and 2.433 ms cumulatively to `subprocess`
before the repair. After the repair that module was absent from all three import
profiles. `helpers.common` cumulative attribution changed from
4.386/5.220/4.441 ms to 0.990/1.801/1.155 ms. Every invocation returned allow with
exit 0. Profiles used Python 3.14.6, disposable log homes, block mode, no inherited
skip/allowlist values, and disabled bytecode writes. They did not clear OS caches.
The first diagnostic script attempt used the corpus decision decoder incorrectly
and was corrected before retaining the before/after profiles.

These single, instrumented import profiles are illustrative and do not establish
a whole-process latency improvement or acceptance. No retained benchmark was run
during M4 correctness probes. Independent alternating baseline/candidate timing
after integration remains required, including startup, former writer denials,
resource limits, repeated-token growth, and provider-specific gates. Keep or revert
this optional optimization according to that evidence.

The sanitized [diagnostic evidence](evidence/startup-repair-diagnostic.json)
records retained report hashes, full clean statistics, before/after module
profiles, and repair source/output hashes. It contains no payloads, environment
values, raw audit output, or home paths.

## Validation

Before the import change, two new public `run_command` behavior tests passed
against all four original helpers. After regeneration they remained green. They
launch harmless Python processes and check literal shell metacharacters and
Unicode arguments, cwd/environment propagation, `CompletedProcess` results,
stdout/stderr capture, byte output, nonzero results and checked exceptions,
timeouts, unavailable executables, and rejection of strings/bytes command inputs.
They use the already registered `scripts/test_helpers.py` suite.

- `python3 scripts/test_helpers.py`: 16 tests passed.
- `python3 scripts/test-generate-hooks.py`: 25 tests passed. Its initial three
  expected historical-import fingerprint failures were resolved by explicitly
  accounting for only the intended import placement changes.
- `python3 scripts/generate-hooks.py --check`: all 26 generated files current.
- Copilot and Gemini OKF lint suites passed, exercising real helper subprocess
  callers and their failure/timeout handling.
- Copilot, Gemini, and Codex startup suites passed, including existing open-stdin
  and encoding cases.
- Copilot and Gemini observability suites passed, including audit capture cases.
- `python3 scripts/test-tool-guard-false-positives.py`: 144 public candidate
  decisions passed across three providers.

Startup suites emitted sandbox readonly observability database diagnostics while
returning success; no failures were suppressed. Existing helper import tests
also emit Python 3.14 package/spec deprecation warnings. No real install, user
settings change, push, or global guard change was performed. Native Windows
execution and final full-process performance acceptance are outstanding. Root
owns the final session documentation pass and M4 owns integrated resource and
paired latency acceptance.
