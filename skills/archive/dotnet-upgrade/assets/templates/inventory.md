# Upgrade inventory: <target> / <route>

Use only after authorization to write target documents. Replace every placeholder with inspected facts or an explicit unknown and owner. This inventory records the current target, not the original case study. A route is the starting and destination version pair. A baseline is the observed state before migration changes.

Record target repository identity, full source revision, clean/dirty status and relevant existing changes, date, requested phase, permitted write paths, plan location, target rules read, and inventory author. For offline discovery, mark this document `Draft - offline` and distinguish historical evidence from current observations.

## Projects, SDK selection and build settings

| Project/solution path | Role and entry point | Actual targets | Proposed targets | Referenced projects | Evidence path |
| --- | --- | --- | --- | --- | --- |
| <path> | <web/identity/worker/tool/test/desktop> | <inspected frameworks> | <proposal, not approved> | <dependencies> | <file and location> |

Record every solution and separately built tool, test discovery configuration, language/nullable/analyzer settings, shared props/targets, central package management, workload requirements, `global.json` minimum and roll-forward policy, available SDKs and the SDK actually selected per working directory. A roll-forward policy permits selection of later SDKs; a minimum is not evidence of the selected SDK. Inspect CI and container build contexts independently.

## Packages, tools and constraints

| Component | Direct or transitive | Current resolved version | Actual target usage | Tool/framework/provider constraints | Evidence and unresolved owner |
| --- | --- | --- | --- | --- | --- |
| <package/tool> | <direct/transitive/local/global> | <observed or unknown> | <project/API/feature> | <cross-stage constraint> | <lock/assets/config/source or unknown> |

A transitive dependency is supplied by another package. Direct pins alone do not lock the entire dependency graph. Include restore sources without secrets, lock/central-management policy, local tool manifests, code generators, ORM tooling and authentication/job integrations. Do not replace all packages with the latest versions by default.

## Databases and state

Record providers, context/project ownership, migrations and snapshot locations, schema history mechanism, initialization order, persistence contracts, timestamp/timezone semantics, authentication state, keys and durable worker state. Distinguish model inspection from a migration actually executed against a named provider. Specify disposable database creation, isolation, cleanup and owners; do not inventory by applying migrations to shared databases. Record backup/restore prerequisites and unknowns without credentials.

## Publishing, images and hosting

Record frontend scripts/tool versions and how assets reach each publish output, runtime/configuration mode, self-contained versus framework-dependent publishing, runtime identifiers, generated files and ignored artifacts. Record each container's SDK/runtime/OS/architecture, build context, copied SDK-selection files, globalization and timezone dependencies, startup/readiness routes, shutdown behavior, and persistent mounts.

Inspect compose, launch profiles, IIS/other server configuration, cloud workers and deployment manifests independently. A launch profile is not a runtime pin, a published DLL does not install its required runtime, and backend publishing does not necessarily build frontend assets. Capture actual facts; historical image tags and environment modes are not defaults.

## Entry points, behavior and external controls

Record host startup, API/health/docs endpoints, proxy/forwarded-header trust, identity/authentication flows, authorization contracts, jobs, frontend routes, reporting or other business outputs, and error behavior affected by crossed versions. Inventory IDE/debug output paths, local hooks, smoke/browser test launchers and documentation version claims. Name each observable invariant and its existing test or missing check.

| Surface | Current command/configuration | Responsible owner | Local evidence available | External gate/unknown |
| --- | --- | --- | --- | --- |
| <CI, server, cloud worker, database, identity, mail, secrets> | <non-sensitive path or exact command> | <name/role> | <observed scope or not run> | <decision/check and owner> |

CI means continuous integration. Find the target's real build/test/publish commands in scripts and CI configuration. If no tracked pipeline exists, say so and name who must supply its configuration. Do not invent owner approval or treat external deferral as verification.

## Baseline commands and observed results

| Working directory | Exact command and relevant environment | Date and revision | Actual selected versions | Result/log location | Warning, failure or gap |
| --- | --- | --- | --- | --- | --- |
| <target-relative directory> | <actual target command; no secrets> | <date/full SHA> | <SDK/runtime/tools/packages> | <exit code, counts, log> | <baseline issue/owner> |

Cover each solution, separately built tool and relevant frontend. Record nonempty test discovery, pass/fail/skip counts, warnings, coverage method and baseline behavior checks. Commands not run remain `Not run`, not assumed passing. Read-only advice or discovery without execution permission records proposed commands and that limitation instead. Link the compatibility matrix and concrete plan when authorized; inventory completion does not approve migration.
