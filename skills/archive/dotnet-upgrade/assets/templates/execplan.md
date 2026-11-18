# Upgrade <target> from <starting version> to <destination version>

This plan is a living document. Maintain `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` at each stopping point. Record this plan's target-relative path and approved revision here. Use the target's existing format/location when present; otherwise write authorized documents under `docs/dotnet-upgrade/<route>/`, initially `net8-to-net10`.

## Standalone plan authoring contract


Replace every placeholder before presenting this plan for execution approval. Embed required target facts, commands, decisions and recovery instructions so a reader can resume from this plan and the target repository without companion skills or the original application's checkout. Supporting target-local evidence may be linked, but essential instructions cannot be outsourced to inaccessible documents. Define unfamiliar technical terms when introducing them.

Record the requested phase, source revision, evidence date, plan status (`Draft`, `Awaiting approval`, or `Approved`) and authorized document-write boundary. A route is the starting/destination version pair. A checkpoint is a recorded verified intermediate state, not necessarily a production deployment. An offline draft retains dated research and unknowns; execution requires refreshed necessary evidence. Unsupported routes remain discovery/research until their specific guidance has been researched and reviewed.

## Purpose / Big Picture


Describe the user-visible reason for this upgrade and the observable behavior that must remain unchanged. State how the owner will recognize success, and what is expressly excluded. Do not imply that documentation coverage or compilation proves runtime or deployment behavior.

## Progress


- [ ] [milestone-1] Inventory actual usage, establish baseline evidence and identify owners.
- [ ] [milestone-2] Refresh necessary evidence, resolve compatibility/staging decisions and obtain concrete-plan approval.
- [ ] [milestone-3] Execute only the approved migration stages and verify their behavior.
- [ ] [milestone-4] Report local and deployment readiness separately and capture target-local candidate lessons.

Add actual start/completion timestamps when work occurs. Split partially completed items to expose remaining work. Synchronize each milestone's status and acceptance with this list; do not check off unresolved or deferred gates.

## Surprises & Discoveries


For each discovery, record the observed behavior, command/log, exact revision and environment, effect on the plan, and whether renewed approval is required. Say `None recorded` until evidence exists. Historical evidence from another project is not a new target observation.

## Decision Log


Record each decision with its rationale, evidence/classification, date and owner. Include dependency strategy, all crossed-version assessments, direct-versus-staged rationale, deployment boundaries and risk acceptance. Do not import historical versions, staging choices or security exceptions as defaults.

## Outcomes & Retrospective


At each major milestone or stopping point, state what was achieved, what remains blocked/deferred, and which evidence supports the claim. Separate actual local results from external deployment decisions. Keep candidate lessons local until authoritative-source changes are explicitly approved.

## Context and Orientation


Embed target repository identity and full source revision, existing changes to preserve, project/solution/tool paths and dependencies, actual targets, SDK-selection settings and selected SDK, package/tool constraints, host entry points, providers, frontend/publish/image flow and owners. Describe each behavior contract and its test location. CI means continuous integration; identify its actual configuration and owner, or record its absence. Describe the target's relevant engineering rules and artifact locations.

## Plan of Work


### Milestone 1: Establish actual usage and baseline

Status: open
Acceptance: not met

Name the files and surfaces to inspect, permitted commands/resources and owner boundaries. Embed the actual baseline commands, working directories, environment and observed results. Acceptance requires accounted-for projects/tools, nonempty test discovery where applicable, behavior baselines and explicit failures/unknowns. Read-only requests produce advice only; commands not run are recorded as such.

### Milestone 2: Research, decide and approve

Status: open
Acceptance: not met

List necessary official migration/breaking-change/support sources and package authorities with relevant versions and retrieval dates. Assess every crossed version and actual target usage. State proposed dependency strategy, exact edit scope, stage sequence, verification gates, rollback, permitted resources and external owner limits. Acceptance requires reviewed route guidance, refreshed necessary evidence, resolved execution-critical decisions and explicit owner approval of this concrete plan.

Approval record: <approving owner, date, plan revision, source baseline, allowed paths/resources, strategy/stages/checks/recovery/owner boundaries, or Not approved>. Invocation and the initial upgrade request are not this approval. Material changes to scope, dependency strategy, stages, risks or ownership require updated evidence, a revised plan and renewed approval before related migration edits.

### Milestone 3: Migrate and verify approved stages

Status: open
Acceptance: not met

Create a separate explicit stage paragraph for each chosen checkpoint, naming exact files/edits, selected versions, target commands, observable behavior checks, failure handling and recovery point. Preserve business behavior and data/public contracts. Acceptance requires each planned local gate to be observed at its recorded revision. Never suppress errors, weaken tests or infer success from a fallback. If strategy or scope changes materially, pause at the approval boundary.

### Milestone 4: Report readiness and candidate lessons

Status: open
Acceptance: not met

Name final-revision rechecks, external owner checklists and target-local candidate lesson path. Report which earlier checks were not repeated after later changes. Acceptance requires honest local/deployment status and explicit unresolved gates; a deferred deployment gate is not passed. This milestone may complete local reporting while deployment remains unverified, but must say so. No shared skill source or installed copy changes are authorized by lesson capture.

## Concrete Steps


For every step, write the exact working directory, real target command, non-sensitive environment/configuration, prerequisites, timeout/readiness limit, expected exit/result and log destination. Obtain commands from target scripts, CI and test conventions; resolve placeholders before approval. Cover separately built tools and frontend steps instead of inventing universal build/test commands. Describe what the user sees, not just which file changes.

Embed bounded startup and smoke procedures, provider-specific disposable resource setup, migration ordering, fresh-scope persistence checks, frontend publish/assets checks, image/runtime/culture/timezone checks and graceful shutdown where applicable. Name owned processes/resources and cleanup commands explicitly. A fresh scope uses a new service/database context so a cached object is not mistaken for persisted state.

## Validation and Acceptance


Give exact target commands and measurable expected outputs for applicable build, nonempty tests, warnings, coverage method, startup, docs/API, authentication, jobs, provider migrations/persistence, UTC/non-UTC behavior, published frontend and images. Explain each not-applicable decision from actual usage. A model snapshot is not an executed migration, and provider-specific scripts are not interchangeable.

Compare each result with baseline evidence and preserve revision boundaries. Investigate changed failures, skips, warnings and coverage rather than hiding them. Record selected SDK/runtime/package versions, not only requested minimums. Name deployment checks, approval dependencies and owners separately; local smoke cannot prove externally hosted behavior.

## Idempotence and Recovery


State which steps safely repeat and how partial execution is detected. Record clean checkpoints, scoped source/image recovery, disposable-resource cleanup and how unrelated changes are preserved. Shared state requires owner-approved backups and a verified recovery procedure before mutation. Do not assume a database downgrade is safe or use destructive repository resets. If recovery fails, stop and report the failure and responsible owner.

## Artifacts and Notes


Embed concise baseline/stage transcripts or target-local log references with dates, revisions, result counts, warning/coverage context and evidence limits. Exclude secrets and sensitive operational values. Explain redactions without exposing their removed values. Label proposed commands, researched claims and actual observations distinctly.

## Interfaces and Dependencies


List public API/data/authorization/output invariants, package/tool/runtime/provider dependencies and external services. Specify permitted disposable substitutions and what they cannot prove. Record deployment/configuration ownership and unresolved compatibility constraints. This plan must remain usable without other skills, original checkout paths, installed-copy edits or automatic code-modernization.
