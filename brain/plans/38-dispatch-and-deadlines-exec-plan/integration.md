# I1. Integrate and review the selected revision

I1 owner: integration coordinator; requires S1, E1, W1, P1 and N1 or applicable passing baselines. Run scheduler and router suites, controlled grader, skill-source validation and diff check, then independent standards/specification review. Select only passing wording. Retain separate baseline, shorter challenger, selected word counts and live evidence. Archive todo 38 only when every accepted case has evidence. If externally blocked, integrate independently verified work and preserve the open item, sources, failed attempts and exact remaining action.

## Review correction R4

The standards reviewer found that the aggregate runner omits all four new maintained orchestration suites. Register them and the exercised scheduler suite in `scripts/test-all.py`. Extend the runner's independent completeness check, reproduce the omission with the public listing, verify the new suite entries and run the affected tests. Keep native provider trials opt-in. The pre-existing scheduler suite also belongs in aggregate verification. The specification review found no substantive discrepancy. Recheck the corrected integration revision before archive.

### R4 evidence

The original public `python3 scripts/test-all.py --list` omitted the four offline orchestration suites and `test_scheduler.py`; the independent completeness test failed with exactly these five paths missing. Registered all five suites and extended completeness discovery to `scripts/tests/orchestration`. The runner completeness suite (14 tests), scheduler CLI suite (17 tests), and orchestration suites `test_controlled.py` (9), `test_heartbeat_probe.py` (3), `test_native_gate.py` (22), and `test_w1.py` (10) pass. Provider trials remain opt-in.
