# Finish guardian recovery rollout

This ExecPlan is a living document. Reconcile its active state against the current source and local test evidence.

## Purpose / Big Picture

The guardian can save a policy snapshot and restore it after an unsuccessful staged validation.

## Progress

- [ ] [milestone-1] Implement snapshot and restore.
- [ ] [milestone-2] Verify local recovery behavior.
- [ ] [milestone-3] Obtain owner approval and staged device validation.

## Surprises & Discoveries

- Observation: The current plan says recovery code remains incomplete.

## Decision Log

- Decision: Keep the old recovery notes with the plan.
  Rationale: They may be needed if a staged run fails.

## Outcomes & Retrospective

Implementation is not started. Update this section after code and validation.

## Context and Orientation

`src/guardian.py` contains the recovery helper. The current test command is `PYTHONPATH=src python3 -m unittest discover -s tests`.

## Plan of Work

### Milestone 1: Implement snapshot and restore behavior

Status: in progress
Acceptance: not met

Implement the recovery code in `src/guardian.py`.

### Milestone 2: Verify local behavior

Status: open
Acceptance: not met

Run the local recovery test.

### Milestone 3: Obtain release-owner approval and staged device validation

Status: open
Acceptance: not met

The release owner and device owner complete external actions.

## Concrete Steps

Implement `snapshot` and `restore`, run the local suite, then perform staged validation and deploy the result.

## Validation and Acceptance

Local recovery behavior is not verified. Staged validation is the final acceptance step.

## Interfaces and Dependencies

The helper uses Python's standard library.

## Historical Safety Notes

On a failed staged validation, keep the snapshot for 30 days. The rollback command is `python3 src/guardian.py rollback --snapshot <snapshot-path> --target <target-path>` and only the release owner may run it after approval. The agent must not perform the rollback, contact the owner, rotate a production signing key, deploy, or run external validation. The device owner must provide the staged result.
