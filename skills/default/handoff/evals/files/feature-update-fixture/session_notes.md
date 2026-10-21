Goal: finish payment retry rollout.

Done:
- landed retry cap in src/payment_retry.py
- confirmed test coverage for the cap logic

Remaining:
- wire retry metrics
- update rollout docs

Next agent focus: retry metrics and docs

Important details:
- code review said `src/payment_retry.py:2` cap looks fine, but rollout cannot close until metrics are wired
- `tests/test_payment_retry.py:5` is the current passing guardrail to rerun after follow-up edits
- benchmark in `reports/benchmark.txt` showed p95 dropped from 480ms to 310ms
- stale next step `inspect legacy YAML toggles` is obsolete
