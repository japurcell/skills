---
name: dotnet-upgrade
description: "Use only when the user explicitly invokes dotnet-upgrade to research, plan, execute, or verify a .NET version upgrade."
disable-model-invocation: true
---

# .NET Upgrade

Guide an explicitly requested version upgrade while preserving business behavior. A route is the starting and destination version pair. The first documented route is .NET 8-to-10; documentation is not proof of successful execution in another project.

## Select the scope and load only what is needed

Identify the requested phase: discovery, research, planning, approved execution, or verification. Read the target's agent instructions and engineering rules before acting. A read-only advice request authorizes a response, not file creation. Invocation or an initial upgrade request alone does not approve migration.

Read [the general playbook](references/playbook.md) for the selected phase. For .NET 8-to-10, read [the route index](references/routes/net8-to-net10/index.md), then only categories relevant to actual target usage. Assess both .NET 9 and 10 changes even when choosing a direct upgrade. For other routes, stay in discovery/research until route-specific guidance has been researched and reviewed; do not substitute this route.

Load [official sources](references/official-sources.md) when researching or refreshing evidence, [practical lessons](references/lessons.md) when selecting checks or investigating failures, and [the case study](references/case-studies/workplan-reports.md) only for historical context. Original paths are provenance, not required checkouts. Reassess historical not-applicable conclusions, package choices and accepted risks for this target.

Use compatible `dotnet` and `official-sources` skills when available. Their absence does not block this bundled procedure or its templates. Do not automatically invoke `code-modernization`. Client discovery and invocation caveats belong in [client usage](references/client-usage.md); load it only for client or optional installation questions. No root README or `evals/` file is required at runtime.

## Follow the requested phase

1. **Discover and baseline.** Inspect actual projects, targets, SDK selection/build settings, packages and transitive dependencies, tools, host entry points, databases, frontend publishing, images and external owners. Use the [inventory template](assets/templates/inventory.md) only when target document writes are authorized. Derive baseline commands from the target's scripts, CI and test conventions; record revision, environment, selected versions and actual results. Do not guess a generic test command or mutate shared resources.
2. **Research and decide.** Refresh necessary primary sources for the target versions, support policy, crossed-version breaking changes, migration guides and package constraints. Record exact URLs, retrieval dates, relevant version and target usage in the [compatibility matrix](assets/templates/compatibility-matrix.md). Keep authoritative evidence separate from inference and observed results. Choose stages deliberately; an intermediate local checkpoint need not be a production deployment. Offline work may produce marked drafts with dated sources and unknowns, not execution authority.
3. **Plan and obtain approval.** Respect the target's existing plan format/location; otherwise use `docs/dotnet-upgrade/<route>/`, initially `net8-to-net10`. The [standalone plan template](assets/templates/execplan.md) includes concrete scope, dependency strategy, stages, commands, checks, rollback and owner boundaries. Before migration edits, require approval of that concrete plan and refreshed necessary evidence. If either is missing, report the missing gate and stop at permitted advice/research/planning. Material scope, dependency strategy, staging, risk or owner changes require revised evidence and renewed approval.
4. **Execute within the approved boundary.** Follow real target commands and engineering rules in staged, reviewable changes. Preserve observable business behavior, public contracts and data semantics. Test affected behavior using existing tools; compilation alone does not prove startup, authentication, provider persistence, executed database migration, timezone behavior, published assets or deployment. Use isolated disposable resources, bounded readiness and owned-process cleanup. Never suppress errors, weaken failing tests, infer success from fallbacks, or copy accepted security exceptions without target-owner decisions.
5. **Verify and report.** Use [stage evidence](assets/templates/stage-evidence.md) to record each revision's selected SDK/packages, dated commands/environment, actual results, failures and deferred owners. Keep earlier evidence tied to its revision; repeat affected checks after later changes. Report local readiness and deployment readiness separately. Deferral never turns a gate green. Recovery follows the approved plan, not an assumed safe database downgrade.
6. **Capture lessons without shared mutation.** Use [candidate lessons](assets/templates/candidate-lessons.md) in the target project. Record applicability, evidence limits and proposed source destination. Obtain explicit approval before updating authoritative skill source; never silently modify installed copies or the personal skills repository.

## Report the next gate honestly

State the requested phase, route, evidence freshness, concrete-plan approval status, observed results, unresolved gates and owners. Label offline drafts and unverified claims. Historical versions and security decisions are not defaults. Local completion is not deployment completion, document review is not runtime testing, and invocation metadata is not universal client enforcement.
