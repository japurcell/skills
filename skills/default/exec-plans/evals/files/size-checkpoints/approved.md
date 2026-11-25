# Publish atlas labels

## Purpose / Big Picture

The release editor gives each map a stable label from the approved catalog. Governing principle: prove each label from its catalog row. The request covers the label file and its validation only.

## Progress

- [x] (2026-11-20) [milestone-1] D1: approve the catalog.
- [ ] [milestone-2] T001: verify the first label and record the result.

## Surprises & Discoveries

Catalog names preserve accented characters.

## Decision Log

### Catalog encoding

D1 was approved by reviewer Jo after comparing the UTF-8 and ASCII catalogs. Use UTF-8 to preserve the label `café-001`. The review receipt is `ATLAS-7104`.

## Outcomes & Retrospective

The approved catalog can be used. Label verification remains open.

## Plan of Work

### Milestone 1: Approve the catalog

Status: done
Acceptance: met

Jo verified the first catalog row and issued receipt ATLAS-7104.

### Milestone 2: Verify the labels

Status: open
Acceptance: not met

#### T001: Verify the first label

Mara owns this assignment and can start now. Prerequisite: [D1](#catalog-encoding). From the project root run `head -n 1 labels.txt`. Compare the first row to the approved UTF-8 value `café-001`; record the observed result and stop. The coordinator owns milestone acceptance.

## Concrete Steps

Mara's next authorized action is [T001](#t001-verify-the-first-label). Only the release editor signs off the finished labels.

## Validation and Acceptance

Each task checks its assigned catalog row. Release acceptance needs every row checked with its expected UTF-8 value.

## Idempotence and Recovery

Read-only checks can be repeated. On a mismatch, record the row, stop and return it to the release editor.

## Historical Records

The retired catalog export on 2026-11-18 produced checksum receipt `HIST-194C`. The field observations below remain relevant for audit.
