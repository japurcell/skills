# Stream large reports

## Purpose / Big Picture

Report operators can process input in bounded memory. The release owner accepted the migration.

## Progress

- [x] (2026-10-01) [milestone-1] Verified equivalent output and the memory limit on the release host.

## Surprises & Discoveries

Generating a benchmark fixture inside the measured process inflated peak RSS. For future memory benchmarks, generate the input before starting the measured process so the result measures the program under test.

## Decision Log

The owner accepted the stream engine as the default after report run R-17 produced identical output and stayed below the 64 MiB limit.

## Milestone 1: Validate and adopt the streaming engine

Status: done
Acceptance: met

Run R-17 processed ten million rows on the release host at 42 MiB peak RSS.

## Concrete Steps

The documentation checkpoint is the only open work. Archival belongs to the release owner.

## Outcomes & Retrospective

The migration was accepted on 2026-10-01. Its measurement lesson is currently recorded only in this plan.
