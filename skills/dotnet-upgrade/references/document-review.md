# .NET Upgrade Bundle Document Review

**Reviewer:** Copilot CLI, fresh Milestone 4 review
**Date:** 2026-10-01
**Destination base:** `fcd0614394cb94a3df7ce4f04e8db4cc6ddcc365`
**Immutable application input:** WorkPlanReports commit `25f3f822d56a6468bc50e52ac16d6331df6604c4`
**Scope:** Integrated document acceptance for `skills/dotnet-upgrade/` and scoped canonical knowledge-base reconciliation. The parent-owned application ExecPlan was read as planning input and was not edited.

## Method and ledger coverage

This was a document-only review. The source artifact inventory came from the immutable application Git tree, not its current worktree. The tree listed 45 files under `docs/dotnet-10-upgrade/`; those paths match the 45 tracked entries in `references/provenance/source-map.json`. Recomputed SHA-256 digests from the immutable Git objects matched all 45 manifest values. The separate prompt capture is the 46th artifact, has no Git revision, and its selected text is 929 bytes with the recorded SHA-256 digest.

The manifest contains 184 unique finding IDs: 46 `observed`, 113 `researched`, 20 `project-decision`, and 5 `unverified`. Each finding was reviewed from its source summary and recorded classification, applicability, verification scope, destination and anchor against the corresponding bundled section. All 184 destination files and anchors resolve. Source meaning and evidence limits remain tied to the historical source revision; an observed result in that project is not a result for a future target.

The review followed the entry point through the general playbook, .NET 8-to-10 route index, .NET 9 and .NET 10 category indexes, all 30 route/dependency research documents, and the historical evidence destinations. It also checked the other internal navigation in all 44 bundled Markdown files. The non-mutating link/anchor audit found 147 internal Markdown links and no unresolved files, fragments, finding anchors or links outside the bundle.

## Semantic and workflow findings

The bundle retains the distinction between .NET 9 checkpoint evidence, .NET 10 checkpoint evidence and later hardening. It does not combine checks from different revisions into an all-green result: the SDK 10.0.302 minimum remains distinct from the 10.0.401 selected by earlier gates, and provider, migration, authorization, publish and image checks not repeated after hardening remain earlier evidence. Package research remains distinct from the accepted narrower package strategy, and conflicting historical EF tool-version narration is preserved rather than silently normalized.

The .NET 8 lifecycle premise in the captured prompt is corrected separately without changing its 929-byte source digest. The prompt's historical support dates are marked for refresh. Original `not applicable` assessments remain scoped to WorkPlanReports, and the route asks future targets to reassess actual source, dependencies, images and external configuration. Negative source searches are not presented as proof about dependency internals or deployments.

The trust-all forwarded-header configuration is explicitly recorded as an accepted WorkPlanReports spoofing risk, never as a portable secure default. Startup, provider persistence, executed migrations, image/globalization/timezone behavior and coverage are distinct evidence. Jenkins, IIS, Fargate, Lambda and live external services remain unverified where their owners deferred work.

All six entries in `evals/evals.json` were reviewed as paper authoring scenarios only. They state the intended boundaries: no migration edits without approval and fresh necessary evidence; unsupported routes remain research; absent companion skills or the original checkout do not break bundled guidance; deployment deferral is not verification; candidate lessons do not silently mutate shared guidance; and routine C# work does not automatically start the upgrade workflow. No model, eval runner or benchmark was invoked, so these are not runtime results.

The `dotnet-upgrade` entry retains `disable-model-invocation: true`. Its `agents/openai.yaml` sidecar exactly matches the `guidance-review` sidecar, `policy.allow_implicit_invocation: false`; the comparable frontmatter field is also present in `guidance-review`. This is a metadata comparison only. The Codex sidecar behavior is documented by its cited source; equivalent recognition and enforcement in Copilot CLI and Gemini CLI remain unverified. The workflow does not automatically invoke `code-modernization`.

Offline work is limited to dated drafts and unknowns; refreshed necessary evidence and approval of the concrete plan precede migration edits. Material scope or strategy changes require renewed approval. Local and deployment readiness remain separate, and owner deferrals do not turn gates green.

## Corrections and reconciliation

The Milestone 2 text at the end of `references/case-studies/workplan-reports.md` described integrated Milestone 4 acceptance as still pending. It now identifies that passage as the historical Milestone 2 extraction record and links this completed integrated review. The top-level `coverage_statement` in `references/provenance/source-map.json` now points to this review; its Milestone 2 `deferred` field is explicitly framed as a historical checkpoint rather than current status.

No source finding was dropped, broadened beyond its recorded applicability, or reclassified. The stale milestone-status wording was the only substantive defect found; the historical source findings and their evidence limits remain unchanged.

The destination knowledge base now links this record from the scoped `skills` instructions, top-level file map entry for `skills/dotnet-upgrade/`, and skills testing guidance. Existing guidance about the retained validator incompatibility and unverified client controls was reconciled, not duplicated or weakened.

## Non-mutating checks and results

From the destination repository root:

    rtk proxy python3 -m json.tool skills/dotnet-upgrade/references/provenance/source-map.json > /dev/null
    rtk proxy python3 -m json.tool skills/dotnet-upgrade/evals/evals.json > /dev/null
    rtk git diff --check
    rtk proxy ./scripts/lint-okf.py

The JSON parses, scoped whitespace checks are clean, and the existing canonical OKF linter passes. A non-retained inline Python audit used immutable `git show` objects to verify the 45 source digests, prompt digest, finding count, destination anchors and relative Markdown links; it reported zero mismatches. The tracked source inventory command was:

    rtk proxy git -C /home/adam/dev/fs/workplan-reports.worktrees/copilot-dotnet10-upgrade-playbook ls-tree -r --name-only 25f3f822d56a6468bc50e52ac16d6331df6604c4 -- docs/dotnet-10-upgrade/

It returned 45 paths. These checks verify document/data structure and navigation, not migration behavior.

## Unresolved limits

No `.NET` command, application migration, trial project, package/archive operation, installation, live model, benchmark, database, image, external service or client invocation was run. No cross-project migration was attempted. `quick_validate.py` was not run or changed; the requested frontmatter property remains an intentional known incompatibility, not a passing validator result. This review does not refresh upstream vendor evidence or certify client enforcement. Copilot/Gemini versions and their treatment of the metadata remain unverified; external deployment owners' gates remain unverified as documented in the case study.

The bundle is accepted for documented coverage and workflow consistency only. That acceptance is not evidence that a different project will migrate successfully or that all three clients enforce explicit-only invocation.
