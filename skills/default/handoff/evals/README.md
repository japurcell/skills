# Handoff evaluation maintenance

Load when changing this workflow or its grader. Keep this bundle independently usable with its own fixtures, assertions, grader and tests.

Run from the repository root after grader changes:

    rtk proxy python3 -m unittest discover -s skills/default/handoff/evals -p test_grade_benchmark.py

The five deterministic cases cover creation, feature updates, invalid-path fallback, stale-history resume and pending owner rollout. Use canonical iteration directories with one eval metadata file beside configuration runs. Exit 0 means grading files were written even when assertions fail; inspect `expectations` and `summary.failed`. Invalid invocation and input errors exit nonzero.

Review [guidance-scenarios.json](guidance-scenarios.json) separately for read-only review, a supplied path among several feature folders, and history updates retaining lessons and existing archive content. These cases use `files/guidance-edges-fixture/` and are outside the public grader's five cases. Compare fixture bytes before and after each run. Review exact commands, observed errors, lesson placement, owner limits and reporting semantics beyond selected assertions. Coverage findings remain separate from sampled agent-performance claims.

Keep positive wording and line-range cases alongside stale actions, missing archive evidence, history-only recovery, unauthorized contributor actions and contradictory proof claims. Wording checks are scenario heuristics, not general natural-language verification.
