# Add row limiting to the report command

This ExecPlan is a living document. Keep its active instructions sufficient for a novice who has only this plan and the current source tree.

## Purpose / Big Picture

The command will accept a maximum row count while preserving its JSON and default text output.

## Progress

- [ ] [milestone-1] Add JSON output.
- [ ] [milestone-2] Add a row limit.
- [ ] [milestone-3] Document examples.

## Surprises & Discoveries

- Observation: An older run reported two passing CLI tests.
  Evidence: The dated record below includes the passing JSON output and exact command.

## Decision Log

- Decision: The limit should be optional.
  Rationale: Users who omit it must keep the existing output.

## Outcomes & Retrospective

Implementation is not started. Update this section at each verified checkpoint.

## Context and Orientation

`src/report_cli.py` is the command entry point. `tests/test_cli.py` exercises the public command. Run tests from this directory with `python3 -m unittest discover -s tests`.

## Plan of Work

### Milestone 1: Add JSON output

Status: in progress
Acceptance: not met

The CLI currently prints only text. Add a JSON option that returns the same count and total.

### Milestone 2: Add a row limit

Status: open
Acceptance: not met

Add `--limit N`. Omission shows all rows; negative values must be rejected.

### Milestone 3: Document examples

Status: open
Acceptance: not met

Document verified examples in the README.

## Concrete Steps

The JSON option does not exist yet. First add JSON output, then add the row limit. Run `python3 -m unittest discover -s tests` after each milestone. At the end, document the examples in `README.md`.

## Validation and Acceptance

Only the original text command currently works. JSON acceptance is unmet. The row-limit command has not been tested.

## Idempotence and Recovery

Preserve the current text output. If a change fails, restore `src/report_cli.py` and rerun the suite.

## Interfaces and Dependencies

The CLI currently has no third-party dependencies. Add options using Python's standard library.

## Earlier Run History

2026-09-30: `python3 -m unittest discover -s tests` passed two tests. The run printed text by default and `--json` printed `{"count": 3, "total": 31}`. This is retained evidence only; current source and tests decide the next action.

Earlier planning note: JSON support was unstarted and acceptance was unmet. That note describes the earlier checkpoint.
