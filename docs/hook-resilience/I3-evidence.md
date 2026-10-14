# I3: composed recovery and reporting proof

Verified on integrated `8572142515dddfe412824799737f65b379e3fd31` on 2026-10-14.
The coordinator ran public generated-entrypoint suites serially on base:

- `rtk proxy python3 scripts/test-hook-diagnostic-recovery.py -v`: 10 passed in
  8.870 seconds, including overflow, missing helpers, broken audit/Git, hostile
  metadata, independent Guardian inspection, deny-only recovery and real repair/retry.
- `rtk proxy python3 scripts/test-security-reporting.py -v`: 9 passed in
  26.306 seconds, covering findings retained through audit failure/contention and
  later unsafe candidates, encoded ceilings, safe labels, strict fallback and
  early failure attribution.
- `rtk proxy python3 scripts/test-hook-diagnostics.py -v`: 8 passed in
  1.853 seconds, including bounded inventory, asset/registration observations,
  immutable settings, missing/corrupt helpers and compiled build identity.
- `rtk proxy bash scripts/test-install.sh`: exit zero. Disposable installation
  checks compare installed diagnostic bytes to source for all three providers,
  run their isolated doctor commands, preserve settings and exercise existing-home
  ownership/idempotence behavior. This is not authenticated host delivery.
- `rtk proxy python3 scripts/generate-hooks.py --check`: all 38 outputs current.

After the functional suites finished, the coordinator reran the retained
`I2-resource-runner.py` against the final reporting source with no concurrent
tests, generation or benchmarks. The approved native macOS collector wrote
`I3-resources.json`: all 24 case/provider rows passed, zero failures, unchanged
source fingerprints, three elapsed samples and separate RSS per case/provider.
Maximum sequential time was 2,199.192375 ms; peak RSS ranged 33,144,832 to
34,947,072 bytes. The separate concurrent pairs logged two clean results per
provider and ranged 649.501959 to 712.626792 ms. The same finite-case and
small-sample limits as I2 apply; these observations establish neither universal
termination nor statistical tail bounds nor an improvement over baseline.

T6's frozen public streaming13, provider scanner/capture/Guardian suites and
generator26 evidence applies unchanged after its conflict-free rebase. I3's
results establish the composed recovery/reporting outcome. Final independent
review, full release validation and Guardian timing acceptance remain unfinished.
No live home, provider authentication or native Windows execution was used.
