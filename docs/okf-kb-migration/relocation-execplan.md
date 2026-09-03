# Relocate the OKF migration documents into version control

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept current as the relocation proceeds. This document follows the repository's `exec-plans` skill.

## Purpose / Big Picture

The OKF knowledge-base migration research, Wayfinder map, tickets, and handoff currently live under `.agents/scratchpad/`, which Git ignores. After this change, every document for the effort will live under `docs/okf-kb-migration/`, internal links and resume instructions will point to the new locations, and `git status --short` will show the files as version-controllable additions. No migration design decision or ticket status will change.

## Progress

- [x] (2026-09-03 03:14Z) [milestone-1] Inventory the OKF effort documents, current references, target documentation conventions, and clean worktree state.
- [x] (2026-09-03 03:15Z) [milestone-1] Move the map, tickets, handoff, and research documents into `docs/okf-kb-migration/` without changing their substantive content.
- [x] (2026-09-03 03:15Z) [milestone-2] Repair relative links, repository-relative paths, and resume instructions for the new tree.
- [x] (2026-09-03 03:17Z) [milestone-3] Validate file counts, ticket blockers, Markdown links, whitespace, Git visibility, and the absence of old effort files in `.agents/scratchpad/`.
- [x] (2026-09-03 03:17Z) [milestone-3] Run the mandatory `update-agent-docs` pass and synchronize this ExecPlan before exit.

## Surprises & Discoveries

- Observation: All current OKF effort documents are ignored scratchpad artifacts, so the worktree is clean even though the effort contains a map, twelve tickets, a handoff, and two research documents.
  Evidence: `git status --short --branch` returned only `## main...origin/main`; a filesystem-derived count found sixteen existing Markdown files.
- Observation: Manual aggregation of files across three scratchpad locations is error-prone.
  Evidence: The first draft said fifteen existing documents; `rg --files` plus `wc -l` proved sixteen. All acceptance counts below now use that measured value.
- Observation: The handoff skill normally restricts handoffs to `.agents/scratchpad/`, but the user explicitly requested that every effort document move into `docs/` for version control.
  Evidence: The user request is the authority for this scoped relocation; future generic handoff creation remains governed by the skill's default path rule.

## Decision Log

- Decision: Consolidate the effort under `docs/okf-kb-migration/`, with `map.md`, `handoff.md`, and `tickets/` at the root and research documents under `research/`.
  Rationale: One self-contained subtree keeps Wayfinder navigation simple and makes the entire effort visible to Git without mixing it into general `docs/research/` notes.
  Date/Author: 2026-09-03 / Codex
- Decision: Preserve the existing filenames and ticket graph; change only paths and links required by relocation.
  Rationale: Stable ticket filenames preserve every `Blocked By` edge and avoid unnecessary semantic churn.
  Date/Author: 2026-09-03 / Codex
- Decision: Move this ExecPlan into the final documentation subtree as `docs/okf-kb-migration/relocation-execplan.md` during milestone 1.
  Rationale: Leaving the relocation plan in ignored scratchpad storage would contradict the user's request that all documents for the effort be version controlled.
  Date/Author: 2026-09-03 / Codex

## Outcomes & Retrospective

The complete OKF migration effort now lives under `docs/okf-kb-migration/` as seventeen Markdown files: the sixteen original research, handoff, map, and ticket documents plus this ExecPlan. Git reports the destination subtree as untracked and therefore version-controllable, while the three old effort locations and the temporary ExecPlan path are absent. All four local Markdown links resolve, every `Blocked By` filename names an existing ticket, and ticket state remains eleven open, one closed, and two unblocked frontier tickets. Whitespace and `git diff --check` validation pass. No application build or product tests were run because no runtime source or behavior changed.

The main lesson was to derive inventory totals from the filesystem instead of manually aggregating counts across directories. The initially misstated total was corrected before relocation and the measured count was used for final acceptance.

## Context and Orientation

Before relocation, the Wayfinder planning tree was `.agents/scratchpad/okf-kb-migration/`, supporting research and the resume handoff were in `.agents/scratchpad/okf-kb-migration-research/`, and the local-system exploration was `.agents/scratchpad/explore-okf-kb-migration.md`. The active tree is now `docs/okf-kb-migration/`: `map.md`, `handoff.md`, `relocation-execplan.md`, `tickets/*.md`, and `research/{okf-primary-sources.md,explore-okf-kb-migration.md}`.

The ticket dependency graph uses filenames, not paths, in each `Blocked By` field, so moving the whole `tickets/` directory preserves graph edges. Links from `map.md` and paths recorded in `handoff.md` must be updated. Scratchpad files are ignored by Git; the destination is not.

## Plan of Work

### Milestone 1: Relocate the complete effort tree

Status: done
Acceptance: met

Create `docs/okf-kb-migration/research/`, move the Wayfinder map and entire ticket directory into `docs/okf-kb-migration/`, move the existing handoff to that root, move both research documents into `research/`, and move this ExecPlan into the destination root. Remove only source directories proven empty after the moves. The destination must contain seventeen Markdown files: the original sixteen effort documents plus this ExecPlan.

### Milestone 2: Repair navigation and resume paths

Status: done
Acceptance: met

Update `docs/okf-kb-migration/map.md` so its research and handoff links resolve inside the consolidated tree. Update `docs/okf-kb-migration/handoff.md` so the active map, ticket, and research paths are repository-relative destination paths and its exact next step invokes Wayfinder with `docs/okf-kb-migration/map.md`. Preserve all ticket statuses and `Blocked By` values.

### Milestone 3: Prove version-controlled integrity

Status: done
Acceptance: met

Verify the final inventory and source absence, resolve every Markdown link in the effort tree, validate that every blocker names an existing ticket, confirm the status counts remain eleven open and one closed with two frontier tickets, scan for old scratchpad paths and trailing whitespace, run `git diff --check`, and confirm `git status --short` exposes the destination files. Run `update-agent-docs`; update `.agents/memory/FILE_MAP.md` and related index material only if the new durable docs area is not already represented accurately.

## Concrete Steps

From `/Users/adam/dev/skills`, create the target research directory, move each explicitly inventoried source, and remove only empty source directories. Then patch links in the moved map and handoff. Validate with `rg --files docs/okf-kb-migration`, targeted `rg` scans, existence checks for blockers and Markdown link targets, `git diff --check`, and `git status --short --branch`.

Expected final inventory summary:

    markdown_files=17
    open_tickets=11
    closed_tickets=1
    frontier_tickets=2
    old_effort_files=0

## Validation and Acceptance

Acceptance requires all seventeen Markdown documents beneath `docs/okf-kb-migration/`, no OKF effort documents at the three old scratchpad locations, no unresolved internal links, no missing blocker files, no changed ticket status or dependency edge, no trailing whitespace, and Git reporting the new documentation subtree as untracked or added. There is no application build or product test because this operation changes documentation paths only.

## Idempotence and Recovery

The move commands use explicit source and destination paths and should run once. Before each move, confirm the source exists and destination does not. If interrupted, inventory both trees and continue only with missing destinations; never overwrite an existing destination. Empty source directories may be removed with `rmdir`, which fails safely if unexpected files remain. Since the starting artifacts are ignored and the destination becomes visible to Git, recovery before commit is to move the exact destination files back to their recorded source paths.

## Artifacts and Notes

The active planning artifact after relocation is `docs/okf-kb-migration/map.md`. The resume state is `docs/okf-kb-migration/handoff.md`. Primary-source research is `docs/okf-kb-migration/research/okf-primary-sources.md`, and current-system exploration is `docs/okf-kb-migration/research/explore-okf-kb-migration.md`.

## Interfaces and Dependencies

No public API, runtime dependency, hook contract, or ticket dependency is changed. The only interface change is the documentation path: future Wayfinder sessions must use `docs/okf-kb-migration/map.md`, and the handoff must point there explicitly.

Revision note (2026-09-03 03:15Z): Marked relocation and path-repair milestones complete after moving all inventoried documents and updating the active map and handoff references. Validation and documentation synchronization remain open.

Revision note (2026-09-03 03:17Z): Closed the validation milestone after measured inventory, link, blocker, status, whitespace, Git visibility, and old-path checks passed; recorded the completed documentation synchronization and final outcome.
