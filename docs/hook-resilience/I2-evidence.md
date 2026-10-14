# I2: integrated scanner capacity and resources

Verified on 2026-10-14 against integrated `e0e8418ec02b600f90ecd977a6478e4ebdd716eb`.
T4b rebased without conflicts; comparison with its pre-rebase tip changed only
coordinator plan/audit documents. Its frozen scanner, capture, merge33, banners,
recovery and generator evidence therefore covers the integrated runtime tree.

Coordinator reran `rtk proxy python3 scripts/test-scan-secrets-streaming.py -v`
on base: all 13 tests passed in 42.680 seconds. Generated freshness passed all
38 targets. Full task-suite commands and results remain in `T4b-evidence.md`.

The retained `I2-resource-runner.py` invokes the real generated hooks through
the maintained merge fixture. Reproduce from repository root with:

    rtk proxy python3 docs/hook-resilience/I2-resource-runner.py "$PWD" /tmp/I2-resources.json

The run used an approved native macOS collector for `/usr/bin/time -l`, disposable
repositories/homes/logs, disabled bytecode, and no concurrent tests or generation.
`I2-resources.json` retains platform/interpreter details, exact source fingerprints,
three complete-subprocess samples per case/provider, separate peak RSS, and a
separate two-call concurrency observation. Fixture setup and post-call native
decision/audit verification are outside timing. Source fingerprints stayed equal.

All 24 case/provider rows passed with zero failures. Cases cover 8 MiB long lines,
empty and nonempty dense lines, binary input, a complete greedy fake token,
256 snapshots totaling 8 MiB, the reported 2,030,848-byte dense file, and a tiny
tracked edit to a file of that size. Maximum observed sequential time was
2,293.104459 ms; separate peak RSS ranged 32,784,384 to 34,357,248 bytes. Greedy
token cases produced actual findings; safe cases produced clean native responses.
Each provider's concurrent pair produced two clean log records; durations ranged
655.268916 to 726.141541 ms.

This meets I2's finite-case integration acceptance under the unchanged eight-second
work budget. Three samples do not establish statistical tail guarantees, universal
input bounds, or a memory improvement over baseline. One concurrency batch does
not establish contention p95. This is source behavior, not live installed delivery
or native Windows proof. T6 and final release checks remain pending.
