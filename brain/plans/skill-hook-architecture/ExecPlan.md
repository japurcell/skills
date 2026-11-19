# Implement the reviewed skill and hook architecture

## Purpose / Big Picture

Seven changes give callers one owner for commit syntax, brain indexing, hook input, scheduling, hook launch registrations, installation policy and conversation batches. Each linked milestone includes its reviewed behavior, implementation entry points, compatibility requirements and acceptance checks. Work from the checkout root. Baseline revision is `069b3f22`. Use Python 3.12+, Bash, PowerShell, Git and RTK. Generated hook files are checked in and must remain usable in their deployed location.

## Progress

- [x] (2026-11-19) Seven designs accepted and adversarially reviewed. The final reviewer reported zero remaining in-scope design findings.
- [ ] [milestone-1] [M1. Commit message validation](ExecPlan/1-commit-validation.md)
- [ ] [milestone-2] [M2. Direct brain reindex](ExecPlan/2-direct-reindex.md)
- [ ] [milestone-3] [M3. Complete-event hook input](ExecPlan/3-hook-input.md)
- [ ] [milestone-4] [M4. Scheduler wake and native completion](ExecPlan/4-scheduler-wake.md)
- [ ] [milestone-5] [M5. Project brain launch registrations](ExecPlan/5-project-launchers.md)
- [ ] [milestone-6] [M6. Skill tree copying](ExecPlan/6-skill-copy.md)
- [ ] [milestone-7] [M7. Project conversation batches](ExecPlan/7-conversation-batches.md)

## Plan of Work

Each milestone file is also its independently owned task. M1, M2, M4, M6 and M7 can start at the plan commit. Serialize M2, M3 and M5 integration because they share generated outputs. M7 owns the Ruminate files and its extraction tests. M2 owns the direct indexer and installer. Isolate those tasks in separate worktrees and run their combined bundle tests after integration. The parent owns this entry, the coordinator integrates scoped task commits, and implementers update their own milestone evidence.

## Concrete Steps

Commit this plan and its navigation before the first implementation edit. Start the direct reindex task, then start independent ready tasks as capacity permits. Use the existing test registry in `scripts/test-all.py` and milestone commands. Run generated freshness checks before installer acceptance. Each milestone stops at its stated contract. Run installer verification in disposable homes and keep raw native proof distinct from fixture results.

## Decision Log

The user selected seven of nine architecture candidates. Design review resolved issue-closing intent, stale retained indexes, unchanged-vault permission checks, early native completion, UTF-8 whitespace, mixed JSON ownership, Addy replacement and exact batch sizes. The seven linked decisions incorporate both review passes. Reusable principles governing these choices include Prove It Works, Boundary Discipline, Make Operations Idempotent, Separate Before Serializing Shared State, Subtract Before You Add, Experience First and Sequence Verifiable Units. The full [principles index](../../principles.md) supplies the related design, verification and delegation principles.

Fresh codebase-design reviewer ranked a shared behavior owner with consumer adapters first in all seven cases. Compared with per-consumer copies plus parity and shared runtime installation, grades in that order were M1 A/C/D, M2 A/D/D, M3 A/C/D, M4 A-/B/F, M5 A/C/F, M6 A-/B-/D and M7 A/B/D. The exceptions matter: ExecPlan retains its standalone registry, native filesystem adapters require Windows proof, and Ruminate keeps both instruction copies synchronized. Runtime-only sharing would compromise relocation. Freeze the independent twenty-command fixture before changing launch generation.

## Surprises & Discoveries

- A wrapped Summary passed the real validator and lost benchmark credit. An empty bullet failed validation and received full credit.
- A retained indexer that exited zero without writing let a stale index pass the old six-string check.
- Six accepted conversations and four requested batches produced three manifests under the legacy splitter.

## Validation and Recovery

Run each milestone's focused checks and then `rtk proxy python3 scripts/test-all.py` against the integrated revision. Use the repository's verify-skills journeys for installed files and provider configuration. Native Windows junction and pipe tests require Windows. Prompt delivery requires a real supported agent host. Record unavailable environments and observed limits and keep their acceptance open. Never substitute fixture results for native proof. Tests use disposable repositories or homes. On partial failure retain evidence, fix the owning module, regenerate from canonical sources and repeat the affected checks. Restore only owned changes when retrying.

## Outcomes & Retrospective

Initial checkpoint: design review complete. Implementation, integrated verification and native acceptance remain open. Update this section with dated results at milestone boundaries.
