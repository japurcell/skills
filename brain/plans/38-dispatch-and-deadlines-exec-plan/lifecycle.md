# Milestone 2. Verify lifecycle, continuity and reporting

Status: in progress
Acceptance: not met

[S1](scheduler.md) owns helper timing and migration. [E1](controlled.md) exercises the helper and host-owned observations, including quiet waiting, one extension, shutdown of worker and writer, same-worker context, a replacement handoff and two six-field reports. [R1](runtime.md) owns the guidance for both callers. Use the public CLI and controlled grader together. Native host acceptance is recorded in [milestone 4](native-and-close.md).

## Progress

- [x] [milestone-2] af044126 made ordinary registrations deadline-only while retaining explicit intervals and version 2 state semantics.
- [x] [milestone-2] b1a63dd2 added six controlled tests and negative cases for lookup-only wakes, wrong assignment, early transfer and missing handoff and report evidence.
- [x] [milestone-2] At 5f2892ab the integrated caller hashes matched the tested files. The combined checkout passed all 17 scheduler tests, 6 controlled tests, 26 router tests and skill-source validation.
- [ ] [milestone-2] [E2](missing-evidence.md) closes three reproduced false positives for completely missing timer, worker and handoff observations.
