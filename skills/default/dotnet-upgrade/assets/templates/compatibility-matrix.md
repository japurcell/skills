# Compatibility decisions: <target> / <route>

Use only for authorized target document writes. Record author, date, full target revision, starting/destination versions, assessed intermediate versions, plan location, and evidence mode (`Current research` or `Draft - offline`). This is a decision record, not a latest-package shopping list.

## Target usage and version constraints

| ID/component | Actual project/API/feature usage | Current resolved version and evidence | Stage/destination constraint | Primary authority URL and relevant version | Research/retrieval date | Proposed action and rationale | Unresolved decision and owner |
| --- | --- | --- | --- | --- | --- | --- | --- |
| <stable ID/package/framework/tool/image> | <inspected path and behavior> | <direct/transitive, observed or unknown> | <compatible range/required change/unknown> | <official guide/package metadata/release notes> | <date; historical versus refreshed> | <retain/change/remove and reason> | <decision required before execution> |

Inspect framework, runtime, SDK/MSBuild, libraries, language, providers, tools, identity/jobs, frontend publishing and host/platform surfaces. Assess all crossed versions. Record why a category is not applicable using this target's code, not a historical project's conclusion. Do not remove a dependency until accidental or transitive usage has been inspected.

## Evidence and inference

For each decision, state classification: `researched` means supported by a cited authority; `observed` means a specified command/check actually ran in a recorded environment; `project-decision` means an owner chose a strategy or accepted risk; `unverified` means the claim or gate lacks necessary proof. Multiple classifications may need separate rows or notes.

Package metadata, supported framework declarations and release notes establish different facts; none alone proves host startup or runtime behavior. Record official compatibility evidence separately from target inference and local verification. Keep latest-version research separate from the accepted strategy, and identify target-dependent constraints at each stage rather than assuming one package major works everywhere.

## Freshness, staging and approval

Record current support-policy evidence, breaking-change catalogs, migration guides and package authorities with full URLs and retrieval dates. Identify which evidence is necessary for each proposed migration change, what refresh remains, and its owner. Offline drafts preserve dated historical evidence and unknowns; they cannot authorize execution.

State the direct-versus-staged rationale, including the value of any intermediate local checkpoint and whether an intermediate deployment is actually required. List approved strategy, approving owner/date and concrete plan revision, or write `Not approved`. A material dependency, stage, risk or scope change requires revised evidence and renewed approval before related migration edits. Link exact verification and recovery gates in the target plan; unresolved execution-critical decisions remain blocking.
