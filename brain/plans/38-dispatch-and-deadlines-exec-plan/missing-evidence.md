# E2. Reject absent observations in the controlled grader

The controlled-eval implementer owns `scripts/tests/orchestration/grade_controlled.py` and its tests. Base the change on E1 at `b1a63dd2`. From that test directory import the existing public grader functions. Three direct reproductions returned the success value `[]` for missing proof.

- `grade_turn({"before": {}, "after": {}})` had no assignment ID, phase, deadline, observed time or recorded action list.
- `grade_transfer(None, False, True)` permitted transfer with unknown worker state.
- With two otherwise valid six-field reports, `grade_continuity(first, second, {}, {}, {})` treated absent worker IDs, setup fact, handoff revision and evidence as matching expected values.

Add the three negative cases before editing the grader. Reject missing observations before comparing values or defaulting counts, with enough detail to identify the missing proof. Retain explicit zero counts, empty action lists during a verified quiet interval, legitimate deadline actions and safe transfer when both statuses are known. Re-run the public scheduler and controlled suites. Stop after a verified change and update this file with the test count and revision.
