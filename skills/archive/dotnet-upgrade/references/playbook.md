# Portable .NET upgrade procedure

This is guidance, not authorization or executable automation. Begin with the phase explicitly requested: discovery, research, planning, approved execution, or verification. Routine C# work is not an upgrade request. Required guidance is bundled here; companion skills are optional.

Read the target repository's rules and manifests first. A target framework moniker (TFM), such as `net10.0`, selects compile/runtime APIs. An SDK builds projects; installed runtime families run them. Neither a package major nor an editor-private runtime proves application support.

## Discovery and baseline

Inventory every project, inherited/overridden target, solution, SDK selection policy, language/analyzer settings, direct/transitive packages, local tools, frontend staging, publishing, images, operating systems, database providers, CI workers, hosting and owners. Inspect debugger paths, hooks and version-specific documentation too. Record commands, directories and observed SDK selection, not just nominal minimums.

Establish real restore/build/test/audit and coverage baselines before migration edits. Include hosts omitted from test references. Record discovery, failures, existing ignores, warnings by ID/location/count, and visited/total coverage points. A failing baseline is a starting state, not a green gate. Reproduce relevant failures through the user-facing boundary and repair without weakening assertions.

## Research to approved strategy

WPR-MAP-001, **project-decision**: WorkPlanReports' research/inventory preceded package, source-edit, owner and gate decisions, then authorship. Wayfinding did not execute. Its .NET 9 checkpoint was undeployed; live integration, production rollout, Fargate deployment and Lambda adaptation were excluded.

Load the matching [route](routes/net8-to-net10/index.md), relevant categories and [necessary official evidence](official-sources.md). Assess every crossed major, including .NET 9 on a direct 8-to-10 move. Choose staging for target risks; a local checkpoint need not be a production release. Other routes remain discovery/research until their specific guidance is researched and reviewed.

Separate packaged assets, dependency bounds, computed compatibility, vendor statements, proposed latest versions and actual runtime observations. Determine provider/API usage before changes. The [historical matrix](routes/net8-to-net10/dependency-compatibility/compatibility-matrix.md) is not the [accepted strategy](case-studies/workplan-reports.md#accepted-package-policy). Direct pins do not lock transitives. Never copy the trust-all proxy exception.

Offline drafts state historical dates, missing evidence and unverified assumptions. No fresh required evidence means draft only. Before migration edits, obtain approval of concrete scope, dependency strategy, staging, measurable checks, rollback and owner boundaries. Invocation or an initial upgrade request alone is not approval. Material scope/strategy changes require renewed approval.

## Standalone plan authoring contract

WPR-TKT-AUTHOR-001, **project-decision**: authorship depended on resolved strategy, edits, owners and gates, embedding context, exact commands/results, recovery, living sections, milestone acceptance and rationale. Source inspection corrected image smoke from Local to Development. No migration occurred during authorship.

A target plan defines purpose, progress, discoveries, decisions, outcomes, context, dependencies, concrete milestones with status/acceptance, exact commands/directories, measurable results, verification, recovery and approval. Define unfamiliar terms. Respect target plan format/location; absent one, use `docs/dotnet-upgrade/<route>/`. Make it resumable without the original checkout or companions. Advice alone does not authorize writing project reports/plans.

## Measurable stage gates

WPR-PLAN-028 and WPR-TKT-GATE-001/002, **project-decision requirements**, not command-presence proof: WorkPlanReports required the whole solution including AuthServer, both EF tools, nonzero discovery/coverage, both disposable providers, startup/auth/health/Swagger/email/Excel/jobs, publish and actual image HTTP/runtime/culture/shutdown, plus warning/audit/transitive review. Missing runtime, Docker or provider blocked the required gate. No new relevant skip or suppressed error made it green.

Translate surfaces to actual target usage, not copied names. Specify pass/fail/blocked/deferred/not-run separately. Record revision/date/environment, selected SDK/runtime/tools/packages, commands/exit codes, tests, warnings, coverage numerator/denominator, reviewed SQL, fresh-scope persistence, publish contents, image identity, longevity, HTTP/body/redirect expectations and cleanup. Compilation does not prove startup, auth, assets, migrations, timezone behavior or deployment.

Historical selection was SDK 9.0.305 then 10.0.401 with `latestMinor`; runtime 9.0.20 was initially missing despite SDK 9. Both tools/providers needed alignment. Later 10.0.302 minimum does not relabel 10.0.401 execution. Tests ran sequentially, including coverage.

## Sanitized evidence and explicit failures

WPR-RUN-006, **observed script structure**, not execution here: historical EF/Auth logs were private, failures nonzero and cleanup removed private files. Filters did not prove arbitrary logs fully sanitized. Review shareable status/timing/contracts; never retain connection strings, credentials, codes, tokens or personal data.

Surface failures using target-standard diagnostics. No swallowed faults, success-shaped fallbacks, disabled audits, weakened tests or transport-success substitutes for exact HTTP status. Preserve unadjusted coverage unless an owner approves changed policy.

## Recovery and schema boundaries

WPR-PLAN-029 and WPR-TKT-GATE-002/003, **project-decision**: repair/rerun before advancing; keep reviewed source/manifest/image fallback and sanitized evidence. Revert through reviewed changes without destructive reset or loss of unrelated work.

Snapshot inspection is not executed migration. Review provider-specific SQL before application to explicitly disposable stores. SQLite lacks a general idempotent script equivalent to SQL Server. Migrate before startup when initialization would create untracked schema. Real schema changes require review, backups and deployment approval, never automatic downgrade. A source checkpoint is not a database backup.

Retry with new empty owned stores. Use unique names, loopback dynamic ports, finite readiness/request limits, exact PID/container/file ownership, failure cleanup and bounded graceful stop. Never delete shared volumes or stop processes by name.

## Local versus deployment readiness

WPR-TKT-GATE-003 and WPR-TKT-EXT-003, **project-decision**: named CI/CD, Windows Admin and AWS checklists were mandatory plan content but non-blocking local handoffs, not verified deployment. Delivery/results remained deferred.

Name owners and independently record delivery references, acknowledgements and actual results. CI owners verify worker SDK/runtime/feeds, full tests/coverage/scanners, frontend/artifact paths. Hosting owners verify OS/runtime/Hosting Bundle/ANCM, entry points/app pools, deployment/rollback. Container owners verify architecture/platform/registry/resources, network/secrets, databases/identity/SMTP, job/Data Protection persistence, health/globalization/shutdown.

A Lambda handler/API Gateway article does not prove a long-lived ASP.NET/Hangfire app runs unchanged on Lambda. Decomposition/adapters and live deployment require separate architecture/approval. Deferral never turns a required local gate green.

## Candidate lessons

Keep new observations with revision, reproduction, classification, scope and unresolved alternatives in the target. Approval is required before promotion into authoritative skill source. Never silently mutate installed copies or personal skills. See [lessons](lessons.md), [case evidence](case-studies/workplan-reports.md) and [ledger](provenance/source-map.json).
