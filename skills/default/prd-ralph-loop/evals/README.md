# Ralph loop evaluation maintenance

Load when changing orchestration guidance or its grader. Run from the repository root after relevant changes:

    rtk proxy python3 skills/default/prd-ralph-loop/evals/test_grade_benchmark.py

Score simulated outputs against frozen expectations; never read the current skill as the grading oracle. Verify exact completion, blind continuation, retained selected-task identity and prerequisite/commit evidence, blocked stops, forwarded constraints, consistent decision fields, malformed decisions and unavailable metrics. Inspect failed expectations even when the CLI exits 0. Synthetic outputs establish grading behavior, not product execution.
