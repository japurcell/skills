# Simplify Agent Documentation Load Paths

This ExecPlan is a living document. Keep `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` current. Maintain it according to `.agents/skills/exec-plans/SKILL.md`; no repository-level `PLANS.md` exists.

## Purpose / Big Picture

After this work, agents can start from `AGENTS.md` and `.agents/memory/INDEX.md`, load only guidance relevant to their task, and avoid repeated, stale, or contradictory rules. A human can verify the result by reading the shorter routing path, running canonical OKF lint, checking every local Markdown link, and confirming the diff preserves unique durable guidance.

## Progress

- [x] (2026-09-16) [milestone-1] Inventoried maintained agent instructions, memory, and root `AGENTS.md`; excluded generated benchmark outputs, archives, and evaluation fixtures from edit scope.
- [x] (2026-09-16) [milestone-1] Audited maintained files for load-path cost, duplication, stale history, contradictions, and broken routing.
- [x] (2026-09-16) [milestone-2] Split hook auto-ingest and observability guidance by trigger, removed cross-language duplication, and preserved protected `AGENTS.md` sections and unique guidance.
- [x] (2026-09-16) [milestone-3] Ran `update-agent-docs` and `okf-authoring`; validated links, index coverage, canonical lint, whitespace, preserved guidance, and final line counts.

## Surprises & Discoveries

- Observation: Repository search finds many `AGENTS.md` files under generated benchmark outputs, archives, and evaluation fixtures.
  Evidence: The maintained architecture explicitly excludes `skills/*-workspace/**/outputs/`, `skills/archive/`, and `skills/**/evals/files/**/AGENTS.md` from normal edits.
- Observation: Hook guidance dominates maintained agent-doc size.
  Evidence: `.agents/memory/known-issues/hooks.md` has 188 lines, `.agents/instructions/hooks.md` has 124, `.agents/memory/adrs/hooks.md` has 116, and `.agents/memory/testing/hooks.md` has 68.
- Observation: PowerShell instruction and testing documents copied shared shell rules word-for-word.
  Evidence: Exact-line comparison found five duplicated CLI/stream/dependency rules and five duplicated shared-test routing rules.
- Observation: Hook guidance mixed three distinct triggers in every load path.
  Evidence: General provider work loaded detailed source auto-ingest, SQLite trace-store, transcript-finalization, log-rotation, and maintenance guidance even when those subsystems were unrelated.
- Observation: ADR-002's NDJSON wording appeared current beside ADR-008's SQLite source-of-truth decision.
  Evidence: Both entries lacked an explicit supersession marker; ADR-002 now states that ADR-008 supersedes it in part while NDJSON remains fallback audit output.

## Decision Log

- Decision: Audit only root `AGENTS.md` plus maintained Markdown under `.agents/instructions/` and `.agents/memory/`; treat source summaries as manifest-owned records and inspect their routing rather than rewriting their generated bodies without a source change.
  Rationale: Repository boundaries classify benchmark outputs, archives, and evaluation `AGENTS.md` files as fixtures or generated artifacts, while source summaries have a separate ingestion lifecycle.
  Date/Author: 2026-09-16 / Codex
- Decision: Prefer focused in-place edits over a large hierarchy rewrite.
  Rationale: Existing index already routes by area; cleanup should remove real cost and contradictions without creating longer pointer chains.
  Date/Author: 2026-09-16 / Codex
- Decision: Split hook instructions, known issues, and testing into general, auto-ingest, and observability routes while retaining `hooks.md` as the default entry point.
  Rationale: Each subsystem has a distinct loading trigger, and the root orientation contract still needs one obvious general hook path.
  Date/Author: 2026-09-16 / Codex
- Decision: Keep source-summary bodies and the append-only ingestion log unchanged.
  Rationale: Their content is manifest or history owned; the audit found no routing defect that justified rewriting generated summaries or past log entries.
  Date/Author: 2026-09-16 / Codex

## Outcomes & Retrospective

General hook work now loads 187 lines instead of 380, a 193-line (50.8%) reduction. Auto-ingest work loads 255 lines, 125 fewer (32.9%); observability work loads 280 lines, 100 fewer (26.3%). Overall maintained guidance fell from 1,419 to 1,387 lines despite six new focused documents.

Auto-ingest and observability rules, known issues, and tests moved from broad hook documents into trigger-specific files. Shared CLI, stream, executable, dependency, terminal, and test-routing rules now live only in shell guidance instead of repeating in PowerShell guidance. No unique durable rule was dropped. Root `AGENTS.md`, source-summary bodies, and append-only `LOG.md` stayed unchanged.

Canonical lint exits cleanly in human and JSON modes; JSON reports `{"schema_version":1,"diagnostics":[]}`. All 39 maintained Markdown files have resolving local links, and every maintained memory document is indexed. `git diff --check` is silent. Final review found no unresolved conflicts, broken references, or unrelated edits.

## Context and Orientation

`AGENTS.md` is the stable repository entry point. It requires agents to read `.agents/memory/INDEX.md`, which routes work to area-specific instruction, testing, known-issue, and decision documents. `.agents/instructions/` stores required actions; `.agents/memory/` stores durable facts and gotchas. Canonical Markdown in both directories follows the repository OKF representation profile and must pass `./scripts/lint-okf.py`.

The edit scope excludes generated benchmark output, archived skills, evaluation fixtures, immutable `.agents/sources/`, and normal skill implementation files. Protected sections in root `AGENTS.md` must remain intact unless explicitly requested, so this cleanup may shorten only unprotected content there.

## Plan of Work

### Milestone 1: Map and audit maintained guidance
Status: done
Acceptance: met

Read every maintained instruction and memory routing document, classify duplicate content as move or drop, verify narrow-source authority for conflicts, and check local links plus index coverage. Acceptance requires a concrete, bounded edit list with no unresolved authority question.

### Milestone 2: Simplify routing and canonical ownership
Status: done
Acceptance: met

Use `apply_patch` for the smallest coherent edits. Keep default-loaded documents short, replace repeated details with direct pointers, remove stale task history, and split a document only when distinct triggers justify a new file. Update indexes and frontmatter when paths or purposes change. Acceptance requires preserved unique guidance and no broader default-load scope.

### Milestone 3: Synchronize and validate
Status: done
Acceptance: met

Run the mandatory `update-agent-docs` pass, then `okf-authoring` with its shared profile. Run full canonical lint, validate changed and indexed local links, inspect the scoped diff, and compare line counts. Acceptance requires clean lint, no broken references, no unrelated changes, and a synchronized plan.

## Concrete Steps

Run from `/Users/adam/dev/skills`:

    rtk proxy rg --hidden --files .agents/instructions .agents/memory -g '*.md'
    rtk proxy ./scripts/lint-okf.py --format json
    rtk git diff --check

Use targeted searches for repeated rules and path references. Do not edit source-summary bodies unless the audit finds a manifest-backed source-ingestion defect.

## Validation and Acceptance

Canonical human lint must exit `0` silently. JSON lint must print `{"schema_version":1,"diagnostics":[]}`. Every relative Markdown link in maintained agent docs must resolve, index entries must cover every maintained memory document, and `git diff --check` must be silent. Final review must show each removed rule was duplicate, stale, or moved to one canonical destination.

## Idempotence and Recovery

The audit and validation commands are read-only and safe to repeat. Apply small file-scoped patches. If an edit loses unique guidance, restore only that hunk with `apply_patch`; do not use destructive Git commands.

## Artifacts and Notes

Baseline maintained line count is 1,419 lines across root `AGENTS.md` and maintained instruction and memory Markdown matched by the initial inventory. This includes source summaries and the source-ingestion log, whose bodies are not normal cleanup targets.

## Interfaces and Dependencies

Do not add dependencies. Preserve root protected sections, OKF frontmatter types, stable paths, source-summary provenance, and the `AGENTS.md` to `.agents/memory/INDEX.md` loading contract.

Revision note (2026-09-16): Initial plan created after inventory established a multi-file, multi-layer cleanup scope.

Revision note (2026-09-16): Audit and restructuring completed. Hook guidance now routes by subsystem, shared shell/PowerShell duplication is removed, and stale migration and ADR labels are corrected; validation remains open.

Revision note (2026-09-16): Validation completed. Recorded line-count reductions, clean OKF and link checks, preserved-guidance review, and final milestone acceptance.
