# WS2 workspace consumer proof

Date: 2026-10-15
Branch: `codex/workspace-consumers-m8`
Base: `b98f8214`

WS2 updates maintained skill authoring guidance, grader usage, create-skill layout grading, its evaluation expectation, and README examples. It adds one public grader test suite and registers it. No workspace payload, canonical `.agents` guidance, plan, discovery record, or historical evidence was edited.

## Public grader red and green

The added suite invokes `skills/default/create-skill/evals/grade_benchmark.py` with disposable iteration directories and checks the grader-written `grading.json`, without calling its private helper.

Before the layout fix, the public suite ran 4 tests and failed all 4: the category placeholder, concrete default-category path, and full repo-local sibling were rejected, while the old root-level `skills/<skill>-workspace/iteration-N/` path was accepted.

After the first fix, the new owner-relative case for `../<name>-workspace/iteration-N/` from a repo-local skill directory failed through the same public CLI. The grader was extended to recognize that sibling form.

Final command: `rtk proxy python3 skills/default/create-skill/evals/test_grade_benchmark.py`
Result: 5 tests passed. Accepted examples are `skills/<category>/<skill>-workspace/iteration-N/`, `skills/default/task-wave-workspace/iteration-3/`, `.agents/skills/<name>-workspace/iteration-N/`, and `../<name>-workspace/iteration-N/` from the owner directory. The obsolete root-level form is rejected.

## Public grader usage

A temporary runner invoked each grader with no arguments and checked its usage path and exit code.

Command: `rtk proxy python3 /private/tmp/verify_ws2_usage.py`
Result: `8 public grader usage examples passed` for commit, create-skill, explore, handoff, improve-skill, official-sources, prd-ralph-loop, and spec-to-tasks. The spec-to-tasks example uses the future canonical `skills/default/spec-to-tasks-workspace/` path.

## Validation

- `rtk proxy python3 scripts/test_test_all.py`: 14 tests passed, including exact registry/list coverage for the new suite.
- `rtk proxy python3 -m py_compile` on the eight affected grader scripts and the new test module: passed.
- `rtk proxy env PYTHONPATH=scripts/vendor python3 skills/default/skill-creator/scripts/quick_validate.py skills/default/create-skill`: `Skill is valid!`
- `rtk proxy python3 -c "import json; json.load(open('skills/default/create-skill/evals/evals.json'))"`: passed.
- `rtk git diff --check`: passed.

At `b98f8214`, `scripts/test_test_all.py` expected `143` in `--help`; the public help text contains `143 SIGTERM` as an exit code and does not display a suite count. The test now asserts the exact `143 SIGTERM` text. The separate `--list` test verifies the registered suite set and count.

Real-home installers, live model evaluations, and human-only orchestration were not run. Composed move, cleanup, and installer verification remains WS3.
