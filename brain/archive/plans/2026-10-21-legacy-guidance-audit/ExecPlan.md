# Recover legacy guidance without restoring the legacy KB

## Purpose / Big Picture

Audit each obligation from the legacy knowledge system against the current brain and skills. Restore current guidance that was lost or weakened, preferably in a matching skill. Preserve the deliberate removal of ingestion, OKF metadata, old directory layouts, and semantic maintenance hooks. Do not commit, stage, install globally, or change unrelated runtime behavior.

This plan follows `.agents/skills/exec-plans/SKILL.md`. The repository is `/Users/adam/.codex/worktrees/6578/skills`. The initial worktree is clean at `378f49c40abcadf34e765a8a4d5a6fd580008ba6`.

## Progress

- [x] (2026-10-21) [milestone-1] Capture the last legacy content and relevant root-instruction variants.
- [x] (2026-10-21) [milestone-1] Audit all 83 source entries and map each obligation to current guidance or an explicit retirement reason.
- [x] (2026-10-21) [milestone-2] Restore admitted gaps in matching skills or narrow brain notes.
- [x] (2026-10-21) [milestone-2] Independently verify obligation coverage, original strength, loading routes, and compatibility with brain intent.
- [x] (2026-10-21) [milestone-3] Validate affected documents and skills, reconcile indexes, and confirm no commits or staged files.

## Surprises & Discoveries

The confirmed example in legacy `.agents/instructions/skills.md` lost direct-reference-depth guidance and weakened the mandatory reference-file table-of-contents threshold from over 100 lines to over 300 lines. The migration's file-level disposition did not prove obligation-level preservation. Early auditors also found weaker invocation-control approval wording, compressed validation scenarios, and knowledge-admission guidance that exists but is not loaded by brain/reflect. These findings remain provisional until each atomic ledger is reconciled.

The initial legacy corpus has 83 entries and 7,389 lines: 77 files from the old instruction, memory, source, retired-skill, and idea trees; four ADRs; and two root `AGENTS.md` variants. Identical path inventories exist at the brain-introduction boundary and immediately before deletion. Auditing uses immutable snapshots under `/tmp/legacy-guidance-audit-378f49c4/`.

## Decision Log

- Use the last content before `f49edd58` removed the legacy system, plus root instructions before brain introduction and before deletion. This captures obligations that had already moved before directory removal.
- Distinguish adopted obligations from third-party reference suggestions. Removing raw snapshots does not make every external example a repository requirement. Preserve unique applicable guidance and provenance without importing unrelated examples or stale platform claims.
- Prefer a matching maintained skill for reusable workflow guidance. Keep project-specific operational facts in existing brain notes. Maintain one canonical owner and explicit loading routes.
- Treat removed-feature instructions as superseded only when the current user decisions or implementation establish that retirement. A vague summary, similar heading, or future todo does not preserve an active obligation.
- Keep coordination metadata and raw source snapshots outside maintained source. Persist a concise audit outcome and detailed traceable coverage evidence when complete. Use a dated audit-plan directory rather than inventing a backlog ID for work already requested directly.
- Initial read-only audits are complete. Authoring recorded 352 rows, hooks 314, and knowledge 380. Initial candidate gaps total 282; these are not all admitted changes, because exact existing equivalents, superseded clauses, and cross-area duplicates require reconciliation.
- Restoration ownership: A owns maintained authoring/task skills, writing-for-agents, self-improve, and brain notes for custom agents and skill architecture. B owns hook/provider/security notes and narrowly matched review/performance skill guidance. C owns brain/reflect admission workflows and remaining repository/script/PowerShell/testing notes. The coordinator owns todos, navigation, the audit plan, and final evidence integration.
- Use finalized source IDs after audit completion. Resolve cross-area overlaps by original path and obligation rather than assuming IDs from an unfinished ledger remain stable.
- Keep todo 4 unchanged because its work belongs to another session. Preserve omitted idea context in the audit evidence without assigning that session new work or messaging it. The coordinator will reconcile only todos 2 and 6 with their original investigation scope; do not mark either investigation complete.
- Old Copilot subagent-loader registrations were already absent before migration. Historical commit 711c1797 removed PascalCase registration; do not invent a migration regression or change runtime registrations to satisfy stale prose.

## Outcomes & Retrospective

Completed all guidance-restoration work. The 83-entry, 7,389-line corpus yielded 1,046 initial rows; independent reviewers added two missed legacy clauses and one current-evidence correction, for 1,049 tracked dispositions. All guidance findings were restored, shown equivalent, or explicitly retired with current scope. Original audit classifications remain visible in the ledger.

Restored rules preferentially live in matching skills; project-specific operational guidance remains in focused brain notes. Existing authoring CLI checks passed 111 tests and 15 applicable changed skill definitions passed validation. Markdown navigation, source-only scope, absence of retired roots, empty staging, and concurrent todo-only HEAD advances were checked. No runtime, global installation, sampled model, or live-provider acceptance is claimed. T7 remains completed with its existing Gemini waiver.

Independent review exposed a pre-existing cleanup-policy/implementation conflict and permissive empty-agent-metadata parsing. The first is captured in todo 13; both are explicit evidence limits, not silently retired obligations. Completed audit evidence is archived beside this plan.

## Context and Orientation

Current persistent knowledge lives in `brain/`; maintained reusable workflows live in `skills/default/`, `skills/forest-service/`, and `.agents/skills/`. Legacy `.agents/instructions/`, `.agents/memory/`, and `.agents/sources/` must remain absent. Brain notes use plain Markdown and standard relative links. Indexes contain navigation only. Mechanical brain hooks maintain the root inventory; semantic review remains in explicit skills.

The old migration map is `brain/archive/plans/01-brain-migration/migration-map.md`. It provides intended destinations and retirement decisions, but each claim must be checked against actual current content.

## Plan of Work

### Milestone 1: Establish obligation-level coverage
Status: done
Acceptance: met

Task A audits skill authoring, root/custom-agent guidance, and retired maintenance skills. Task B audits provider hooks, safety, observability, hook tests, provider references, and ADRs. Task C audits remaining repository, scripts, PowerShell, knowledge admission, CLI references, memory, and idea content. Their exact disjoint source assignments are in the scratch inventory. All three have no prerequisites beyond the captured snapshots and current source.

Each reviewer reads every assigned file in full and records atomic obligations with source line ranges, original strength, current destination and evidence, classification, and a recommended disposition. A file-level claim is insufficient. Separate lost, weakened, preserved, deliberately superseded, duplicate, historical, reference-only, and non-guidance content. Flag stale technical claims for bounded current verification rather than blindly restoring them.

Acceptance requires every source entry to have complete read coverage and every extracted obligation to have a concrete disposition. The coordinator reconciles overlapping findings and admits only current gaps.

### Milestone 2: Restore and verify current guidance
Status: done
Acceptance: met

Restoration tasks depend on the completed audits and coordinator admission. Assign exclusive file ownership before edits. Match reusable guidance to an existing skill; route project-specific facts to existing brain notes. Preserve explicit approval boundaries, thresholds, negative cases, and conditions. Update references when a rule moves so the intended task actually loads it.

An independent reviewer compares restored guidance against each legacy obligation and checks that no ingestion, frontmatter, old directory, obsolete provider assumption, or parallel knowledge system was reintroduced. Resolve every rejected or weakened obligation before acceptance.

### Milestone 3: Validate integrated documentation and finish
Status: done
Acceptance: met

Validate modified skills with their existing validators and applicable public grader fixtures. Review positive and negative document scenarios for restored authoring rules and migration boundaries. Do not create a new validation framework or run unrelated native/runtime matrices for prose-only changes. If source or test code becomes necessary, activate TDD and use the already approved public seams or confirm a new seam before writing tests.

Check standard Markdown links, live loading routes, reachable indexes, current source evidence, and whitespace. Reconcile brain navigation with the standalone indexer if hooks are unavailable. At completion, archive this completed plan and its obligation evidence under `brain/archive/plans/`, update navigation, and leave a concise audit note under `brain/audits/`.

## Concrete Steps

Completed: restoration, independent semantic review, evidence archival, index reconciliation, and integrated documentation checks. No implementation action remains in this plan. Runtime follow-up is todo 13, not unfinished migration guidance.

Commands run from the repository root. Use RTK, for example `rtk proxy git show 'f49edd58^:.agents/instructions/skills.md'`, `rtk proxy python3 skills/default/skill-creator/scripts/quick_validate.py <changed-skill>`, and `rtk proxy git diff --check`. Expected outcomes are complete semantic coverage, valid maintained documents, unchanged legacy-root absence, and no staged files or new commits.

## Validation and Acceptance

The audit ledger is the primary semantic proof. Each restored obligation must be present at its original strength and reachable through the relevant skill or brain entrypoint. Superseded obligations require a concrete current decision or implementation reason. Existing eval scores are supporting evidence, not substitutes for semantic review.

The known authoring example must end with the mandatory over-100-line reference TOC rule, one-level reference navigation, direct links from `SKILL.md`, concise context guidance, and effective-skills reference restored in the maintained authoring workflow. No blanket task deferral to a backlog item counts as preservation.

All 83 source entries must be accounted for. Any unverified external claim remains clearly bounded rather than silently becoming current policy. This task must not commit, stage, install globally, restore legacy folders, or change unrelated runtime behavior. Preserve concurrent user/process changes.

## Idempotence and Recovery

Do not reset the shared worktree. Preserve user and worker edits. Compare each change to the captured initial HEAD and restore only owned changes if a restoration is rejected. Repeating the audit must converge on canonical destinations rather than duplicate notes. Raw snapshots remain outside version control and must not be copied into the vault wholesale.

## Interfaces and Dependencies

No new runtime interface or dependency is planned. The maintained brain, reflection, authoring, planning, and provider workflows retain their current roles. The obligation ledger records source identity, line range, obligation, original strength, destination, evidence, classification, restoration, and verification.

## Follow-up review and scope limits

Independent reviewers reread all assigned legacy snapshots and original rows. They found additional false-preserved clauses, missing selectors, and loading gaps; the coordinator restored them and reviewers verified closure. A353 and B-NEW-001 record extraction omissions; C-NEW-001 records a current-evidence correction. Original IDs remain stable.

The stale-session cleanup implementation already contradicted its later explicit policy before migration. The restored note states both the rule and this conflict; todo 13 scopes an isolated runtime repair. The custom-agent converter accepts single-quoted empty metadata despite the authoring requirement; the explicit rule is restored without claiming structural enforcement. Neither behavior was changed by this documentation task.

Todo 4 remains byte-identical because another session owns it. Omitted proposal context is preserved in idea-context.md as research material, not adopted policy. Todos 2 and 6 regain original investigation conditions; no investigation is marked complete. Todos 10 and 11 retain their accepted scope.

Reflection: the durable lesson is obligation-level comparison before pruning, including conditions, negative cases and loading routes. This is encoded in create-skill and the shared admission procedure, so no duplicate principle note or new machinery is needed. No further write follows from sampled validator success alone.

## Artifacts and Notes

- [Obligation ledger](obligations.json): source inventory, immutable hashes and ranges, original strength, final disposition, and independent verification. Historical evidence only; current owners hold instructions.
- [Validation evidence](validation.json): focused validator/test results, link/index/scope checks, and interpretation limits.
- [Retained proposal context](idea-context.md): original research detail without policy adoption or reassignment of todo 4.
- [Concise audit outcome](../../../audits/2026-10-21-legacy-guidance.md).

Final shared-tree observation: HEAD advanced through three concurrent todo-only commits to `a57b4ff5f1d02fd9fc60d979e63beeb0e7f52f7c`. They changed only `brain/todos.md` and `brain/archive/todos.md`. This task issued no staging or commit commands; those changes were preserved. Todo 4, 10, and 11 remain byte-identical to the initial baseline.
