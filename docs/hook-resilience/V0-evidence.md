# V0 release verification preparation

Prepared on 2026-10-14 from candidate `0892b501f9eba16d0dc5b209d50c262ae1b314c8` in the private `codex/hook-resilience-v0` worktree. This is verification preparation, not V1 release acceptance. No release timing comparison, aggregate product test run, installation, provider dispatch, or native Windows check was performed here. The coordinator owns active-plan updates and the final coordinated KB pass.

## Delivered procedure

`scripts/verify-hook-release.py` imports the maintained high-rate runner's `guard_cases`, `invoke`, `verify_outcome`, `summary`, and fixture setup, and the resource runner's `fixtures`, `payload`, `fingerprints`, and `checked_run`. It does not copy the policy or fixture corpus. Small maintained-runner extensions expose the existing disposable invocation environment and an optional working directory for the separate RSS launch. Resource failures retain bounded collector stderr, including unavailable native collectors.

The timing mode compares two alternating warm pairs, baseline then candidate followed by candidate then baseline. Each case/condition/pair records a first process, three discarded warmups, and 25 measured subprocess samples. Warm provider copies permit normal bytecode reuse. Each of 25 cold launches per case/condition has its own provider source copy and log home, alternates condition order by sample, excludes source bytecode, disables bytecode writes, and checks zero provider bytecode before and after the invocation. OS and standard-library caches remain uncleared.

The adapter retains raw warm/cold samples, first outputs, native permission decisions, input hashes, hook/helper and harness fingerprints, environment, median/p95/MAD, both pair summaries, and pair-specific deltas. Each warm pair independently applies +2 ms median/+5 ms p95; cold applies +5/+10. A failed pair cannot disappear into an average. Separate two-call clean-case batches report concurrency with successful logging, outside the latency gates. The resources mode uses the maintained finite fixtures, a 500 ms maximum over first/measured calls, and a separate native macOS `/usr/bin/time -l` launch reporting RSS in bytes. It preserves the same interpreter, provider inputs, fixture working directory, and disposable logging environment for elapsed and RSS launches.

Setup, provider copying, outcome decoding/validation, and completed-log verification occur outside the high-rate runner's elapsed interval. Temporary homes remain alive through that verification and are cleaned by the enclosing temporary-directory context even on failure. Every valid inspection or denial requires exactly one completed guard record per launch. The exact legacy `*.guard.failure` malformed-JSON fixture may have no log because it exits before audit initialization; its actual record count and attribution status are retained, and candidate attribution added by T6 remains acceptable. This exception cannot relax logging for valid inputs. `OBSERVABILITY_TESTING=1`, disposable HOME/XDG/log redirects, and reset audit-shadow overrides prevent live-home log writes.

The baseline root must match the actual Git runtime fingerprints at `bc52d7d69aaa046ea97e323879402241a01fead7`; a misleading directory name cannot establish identity. Before/after source and harness checks reject changes during measurement. Existing output paths are refused so failed evidence cannot be overwritten. `--case` accepts exact names for isolated repeats and marks a filtered run ineligible as standalone full-release evidence. `--mechanics-only` uses two samples with no warmups, explicitly marks its report ineligible, and tests collection without claiming performance acceptance.

## Explicit baseline expectation map

The maintained high-rate runner's historical `--expected-behavior baseline` predates `bc52d7d6` and must not be used for this comparison. V0 requests candidate corpus expectations on both conditions, with one explicit baseline override: `*.guard.search.full-provider-envelope` expects deny on `bc52d7d6` and allow on the candidate. Both `danger.full-envelope` and `danger.full-envelope-unknown` expect deny on both conditions. The baseline lacks `_native_shell_shape`, so the full search fixture's 130 literal separators still reach strict segment inspection. Existing repaired native-body and nested execution cases already match candidate expectations at this baseline.

Source comparison and one-shot generated public entrypoint probes confirmed this map, independently of measured outcomes. All **156 timing corpus cases per condition** and all **108 resource fixture cases per condition** passed their predeclared decisions and valid-call completed-log requirements. These probes used a disposable `git archive` baseline and disposable repositories/homes, and discarded elapsed values. They do not establish latency or RSS acceptance. Baseline archive hashes also matched `baseline_fingerprints()`.

## Registry and bounded verification evidence

The explicit `scripts/test-all.py` registry now includes input bounds, diagnostics, diagnostic recovery, stream component, public streaming, T6's `test-security-reporting.py`, and the new adapter suite. Capture suites remain invoked through the provider Bash scanner suites and are not duplicated. T6's source file is intentionally absent from the V0 starting revision and must arrive through serial integration before the actual aggregate run. Registry mechanics use inert substituted suites and therefore can verify this pending registration without running the product suites.

Observed red/green evidence:

- Registry completeness first failed naming all six missing accepted suites, then passed after registration.
- The adapter list/mapping test first failed because its CLI did not exist, then passed with the explicit revision map.
- The exact invalid-case test first exposed an uncaught `ValueError` traceback; the CLI now exits 2 with ordinary argparse diagnostics.
- The warm-cache assertion first failed because no bytecode evidence existed; it passes after normal warm bytecode reuse and explicit warm/cold accounting.
- Resource mechanics first failed in the sandbox. A direct native collector smoke retained `time: sysctl kern.clockrate: Operation not permitted` and exit 1. The same bounded inert-hook resource test passed through approved native execution outside that sandbox; this is collector mechanics, not product resource acceptance.
- Initial in-tree `py_compile` failed when the sandbox refused a generated bytecode write. Repeating with `PYTHONPYCACHEPREFIX=/private/tmp/hook-release-v0-pycache` succeeded without changing source.

Final focused commands and observed results:

```text
rtk proxy python3 scripts/test_test_all.py
  14 tests passed
rtk proxy python3 scripts/test-benchmark-high-rate-hooks.py
  2 tests passed (inert temporary entrypoints)
rtk proxy python3 scripts/test-verify-hook-release.py
  8 tests passed through approved native execution
rtk proxy python3 scripts/verify-hook-release.py --help
  exit 0
rtk proxy python3 scripts/test-all.py --list
  exit 0; accepted suites and adapter listed once
rtk git diff --check
  exit 0
```

Adapter checks cover the revision map, matched pair/cold evidence, normal warm versus zero cold bytecode, completed logging, missing logging rejection, separate RSS launches, an isolated pair violation, exact filters, preservation of original output, wrong native decisions with retained failed samples, wrong baseline identity, and source mutation. RTK 0.51.0 is available; `rtk gain` could not initialize its tracking database in this sandbox. Commands retained RTK prefixes.

## V1 execution commands

After final review and repairs, stop all implementation, tests, generation, and other benchmarks. From the final candidate repository root, confirm the checkout is clean and retain its commit ID. Execute the following serially. The resource command needs approved native macOS collector access if the sandbox denies `sysctl kern.clockrate`. Do not treat an unavailable collector as a passed resource gate.

```bash
rtk git status --short
rtk git rev-parse HEAD
rtk proxy python3 scripts/verify-hook-release.py --help
release_baseline_dir=$(rtk proxy mktemp -d /private/tmp/hook-release-baseline.XXXXXX)
release_evidence_dir=$(rtk proxy mktemp -d /private/tmp/hook-release-evidence.XXXXXX)
rtk git archive bc52d7d69aaa046ea97e323879402241a01fead7 | rtk proxy tar -x -C "$release_baseline_dir"
rtk proxy python3 scripts/verify-hook-release.py --baseline-root "$release_baseline_dir" --candidate-root "$PWD" --mode timing --output "$release_evidence_dir/timing.json"
rtk proxy python3 scripts/verify-hook-release.py --baseline-root "$release_baseline_dir" --candidate-root "$PWD" --mode resources --output "$release_evidence_dir/resources.json"
```

Retain both JSON files, including any failures, with V1 evidence. The adapter's before/after hashes establish the measured runtime source, while the retained Git ID establishes candidate provenance. A benchmark exit zero alone is not provider delivery or installed-copy proof. Complete the plan's freshness, full/targeted product suites, isolated installer, and external-platform evidence separately before serial timing. Do not measure release performance while those checks run.

An isolated violation requires one exact targeted repeat with a **new** output path; list several exact `--case` flags only if several isolated cases require that repeat. For example:

```bash
rtk proxy python3 scripts/verify-hook-release.py --baseline-root "$release_baseline_dir" --candidate-root "$PWD" --mode timing --case codex.guard.clean --output "$release_evidence_dir/timing-repeat-codex-clean.json"
```

Substitute the actual failing case, retaining the same frozen source, interpreter, provider input, and logging conditions. Preserve the original violation and document an attributable environmental explanation. An unexplained or repeated violation fails acceptance; a later passing repeat cannot silently erase it. Resource repeats use `--mode resources` and the exact `*.resources.*` name. Preserve evidence before removing only the owned baseline extraction with `rtk proxy rm -rf -- "$release_baseline_dir"`; keep the evidence directory until its contents are retained by V1.
