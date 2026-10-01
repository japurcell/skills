# Practical upgrade lessons

These are **observed historical source/execution findings**, not reruns or universal defaults. Original commit/digests/classifications/scope remain in the [ledger](provenance/source-map.json); reported stage results are in the [case study](case-studies/workplan-reports.md). Future execution requires actual target evidence, refreshed authorities and approved scope.

## Independent toolchain surfaces

WPR-PLAN-004: SDK 9 existed, but only runtime 9.0.9 was installed, below the 9.0.20 gate. Both Microsoft.NETCore.App and Microsoft.AspNetCore.App needed independent checks. Official archive SHA-512 and safe-path checks plus versioned extraction avoided replacing the SDK host. Node 24.15.0, npm 12.0.2, Docker 29.7.2 and bounded disposable database readiness were separate prerequisites. This is not installation authorization or a reusable version default.

## SDK pins do not control all builds

WPR-PLAN-008: Docker selected SDK/runtime through Alpine tags without copying root global.json. New central props had to be copied before restore. latestMinor can select later feature bands; record selected version. SDK, TFM, package graph, local tools, images, OS and external workers are independent surfaces.

## Dependency removal and transitive assumptions

WPR-PLAN-005: eight floats removed via exact direct central pins, transitives still unlocked. Removing unused Oracle EF exposed Models CS0234 because scheduler EF types arrived accidentally via that provider. Explicit EF SQL reference restored intended dependency. CA2263 repaired with equivalent generic filter-registration overload. "Unused provider" does not mean no transitive compilation effect.

## Compilation is not host startup

WPR-PLAN-019: Swashbuckle 7.2 compiled on .NET 10, but SwaggerGenerator.GetSwagger failed host startup with TypeLoadException. The conditional upgrade to 10.2.3 repaired loading; later actual JSON/UI/loader HTTP checks passed. Upstream recommended 9.0.6 as an intermediate step; actual stage 9 retained 7.2. Preserve recommended versus executed history.

## Frontend staging before publish

WPR-PLAN-009: direct dotnet publish did not build Angular. A fresh checkout lacked dist/browser; build:docker-local staged it. Release output had matching runtimeconfig, web.config, assembly and index, plus 47 JavaScript assets. build.sh deleted dist; buildP/T/D referenced missing build_version.sh. Missing modules prompted lockfile npm ci, not an arbitrary upgrade. The existing 361-byte SCSS warning was retained; no Angular source changed. Check actual mixed-stack staging and artifact contents.

## Smoke the real published asset path

WPR-PLAN-010: Local always fetched Angular dev server, even empty UiDevServerUrl. Bundled image checked in Development; Local login separately used isolated host/fake UI. A convenient environment can exercise the wrong assets and give misleading publish evidence.

## Startup options and Swagger loader checks

WPR-PLAN-013: Development session startup failed without valid OIDC ClientId/ClientSecret options even without contacting identity provider. Synthetic disposable options resolved it. Swagger's relative ./v1/swagger.json was configured in index.js, not inline index.html. Check JSON, shell and loader independently; no real auth values retained.

## Provider backed migrations and fresh scope persistence

WPR-PLAN-011/WPR-RUN-003: EnsureCreatedAsync could create SQLite tables without migration history if startup preceded migrations. Context/pending-model checks and SQL review preceded fresh disposable updates. SQLite normal script and SQL Server idempotent script are not interchangeable. SQL history/job survived new connection; OpenIddict app/scope/authorization/expired token survived new DI scope. Static model inspection is not migration/persistence execution. Failed-migration rollback was not established just because successful migrations passed.

## SQLite offset instants and redemption

WPR-PLAN-023: stage 10 gates used fresh stores under UTC and America/New_York. Positive/negative-offset TEXT creation/expiry/redemption preserved three independently specified UTC instants and redeemed status through a fresh OpenIddict scope. Provider SQL and cross-connection scheduler persistence passed. Original production data remained unknown. Verify actual stored values, instants and status, not just timezone settings or model shape.

## Synthetic auth configuration and PKCE contracts

WPR-RUN-004, **observed runner assertions**, with executed results separately in WPR-PLAN-012/023: discovery 200, invalid-client 401 with invalid_client, authorization 302 with persisted code, S256 PKCE redemption 200 with Bearer/access/identity token presence, and actual namespaced code type, redeemed status and non-null timestamp. No values are printed here. The historical runner read a source seed credential: an unsafe, nonportable assumption, not a generic test pattern. Future tests supply isolated synthetic options and clients through an approved seam, never extract or copy source credentials or contact real providers by default.

## Bounded owned resource lifecycle

WPR-PLAN-015/WPR-RUN-002: unique network, container, database and file names, loopback dynamic ports, finite request/readiness limits and a 30-second stop. Historical SQL readiness allowed 60 two-second attempts, AuthServer 30 checks and the app 40 two-second attempts; these are evidence, not universal budgets. An early background dotnet run subshell leaked children; exec dotnet and an exact PID trap restored ownership. Clean up only exact owned resources, never broadly delete processes, containers, volumes or shared stores.

## Real image contract checklist

WPR-RUN-005, **observed script assertions**, not execution here: Development anonymous session JSON and app-root shell/script return 200; intentionally unavailable Oracle returns 503 without details. Other checks cover Swagger paths/title/UI/index.js endpoint, Hangfire Job/heartbeat, exact runtime families, full ICU, invariant=false, tzdata, zone file, non-UTC offset and graceful stop. Synthetic auth options avoid a live provider. Controlled hosts separately prove healthy Oracle 200 and API/browser behavior. An unavailable 503 never means healthy or deployment-ready.

## ICU is not timezone data

WPR-PLAN-014: full ICU was initially present, but the zone file was missing; a non-UTC TZ returned +0000. Adding tzdata and rebuilding the actual Alpine image restored the non-UTC offset while retaining invariant=false. Verify culture libraries and timezone files separately, including app behavior.

## Generated code coverage denominators

WPR-COV-002: OpenAPI 10.0.12 added Microsoft.AspNetCore.OpenApi.SourceGenerators.dll, absent from 9.0.20 assets. Services, Models and workPlanReports each acquired 377 unvisited OpenApiXmlCommentSupport.generated.cs points, totaling 1,131 of the 1,166-point increase. Compiler/PDB identities may exist without generated files on disk. Inspect actual package assets and normalized XML source identity before attributing the reduced percentage to untested application code.

## Coverage normalization is not policy

WPR-COV-004: subtracting 1,131 generated points arithmetically gives 3,075/5,441 = 56.51%, versus 57.08%. This is not an executed exclusion run or approved coverage change. The original unadjusted metric remains authoritative unless owners approve policy. Do not introduce blanket generated-code exclusions.

## Coverage collection variability

WPR-COV-005: the initial rollback report had 1,838/5,406 points, with four assemblies showing zero despite passing tests. The identical command without a rebuild yielded 3,086/5,406. Visits varied; the denominator did not. The cause is unestablished; do not attribute missed visits to source changes or claim an instrumentation diagnosis.

## Coverage comparison method

WPR-COV-006: isolate rollback and current source, collect sequential restore/build/full-test OpenCover reports, and inspect Summary visitedSequencePoints/numSequencePoints/sequenceCoverage. Join per-module SequencePoint fileid to Files uid/fullPath; vc>0 means visited. Normalize the checkout prefix through server and inspect project.assets library files for the generator DLL. Both historical builds had 383 warnings and 0 errors; suites had 286 and 293 passes respectively, plus 1 ignore each. Historical archive commands are evidence, not shipped extraction or runner automation.

## Historical runner is not portable automation

WPR-RUN-001: verify-stage9.sh defaults to net9, accepts net10 and exits 2 for an invalid stage; despite its name it covers both stages. It assumes specific project, context, binary, image, route, client and table names, plus Python pymssql. **No executable copy is shipped**. The [playbook](playbook.md#sanitized-evidence-and-explicit-failures) preserves private logs, explicit failures and sanitized evidence without credential-bearing snippets or hardcoded operational values. Future automation must be newly designed and approved for the actual target, not copied from this record.
