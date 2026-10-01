# WorkPlanReports historical case study

Immutable input: **WorkPlanReports commit `25f3f822d56a6468bc50e52ac16d6331df6604c4`**. Source paths and original digests are in the [46-artifact, 184-finding ledger](../provenance/source-map.json). This is reported historical evidence, not execution during skill extraction. September 23 research, September 24 stages and September 28 hardening are distinct. Earlier planning prose describes its stage, not final status.

## Staging and scope

WPR-PLAN-001, **project-decision**: preserve reports, authorization and scheduled delivery through .NET 8 -> 9 -> 10. .NET 9 was a mergeable, locally verified source/image rollback checkpoint, never a production rollout. Baseline, source gates, full local gates, hardening and external handoffs are separate. Future targets choose their own staging.

## Historical integration status

WPR-HAND-001, **observed source report**: original application milestones 0-4 and 6 integrated on its upgrade branch; rollback `29f8a62` undeployed, .NET 10 local gate `a6666d4`. No shared database/live deployment changed; temporary worktrees removed. Milestone 5 requests prepared but delivery deferred. This is not a new integration or hosted CI result.

## Historical project and build inventory

WPR-INV-001, WPR-TKT-INV-001, **observed source inspection**: sole `server/NEWworkplan.sln` included cognos-terminal, AuthServer, Services, Models, DTO, ScheduleDelivery and WP-ReportsTestProject. All inherited net8.0, LangVersion latest, AnalysisLevel latest-All, nullable/implicit usings and NuGetAudit=true/Mode=all from Directory.Build.props. Initial test references omitted AuthServer, although solution build included it; later tests added it. No original central package file, NuGet.Config, lock file or solution filter.

SDK 8.0.204/latestMinor selected 8.0.420 locally. Additional installed SDKs were local observations, not CI guarantees. README's minimum 8.0.404 conflicted with nominal pin. Historical inventory/map precede implemented changes; do not treat them as final tree.

## Historical AuthServer and tool inventory

WPR-INV-002, **observed**: EF Design/Sqlite/diagnostics 8.*, OpenIddict.AspNetCore/EntityFrameworkCore/Quartz *, Serilog.AspNetCore/Expressions *, Quartz.Extensions.Hosting 3.18.1; no project references. Eight floats made later restores unconstrained. Local dotnet-ef: AuthServer 8.0.18 with rollForward=false, main API 8.0.4. EF 10 research reversed those initial paths; inventory/matrix agree. Preserve the discrepancy, not fabricated runtime resolution.

## Historical main host dependencies

WPR-INV-003, **observed direct references**: Oracle health 9.0.0; Hangfire ASP/Core/SQL 1.8.22; ASP JWT/OIDC/diagnostics/OpenAPI 8.0.23; SqlClient 6.1.3; EF SQL/Tools 8.0.10; IdentityModel Logging/Protocols/OpenIdConnect and JWT 8.15.0; Newtonsoft 13.0.4; Oracle EF 8.23.60; Serilog ASP 9.0.0/Expressions 5.0.0; Async/File sinks 2.1.0/7.0.0; Swashbuckle 7.2.0; YARP 2.3.0. References DTO/ScheduleDelivery/Services; appsettings copied on publish. References are not transitive or runtime support proof.

## Historical library dependencies

WPR-INV-004, **observed**: Services references DTO/Models/ScheduleDelivery, Hangfire family 1.8.22, OpenAPI 8.0.22, EF Tools 8.0.10, Configuration 8.0.0/FileExtensions/Json 8.0.1, SqlClient 6.1.3, IdentityModel/JWT 8.15.0, Newtonsoft 13.0.4, Oracle EF 8.23.60/ODP 23.26.0, Swashbuckle 7.2.0, Serilog ASP 9.0.0.

Models references DTO and Hangfire family 1.8.22, OpenAPI 8.0.22, EF Tools 8.0.10, IdentityModel/JWT 8.15.0, Newtonsoft 13.0.4, Oracle EF 8.23.60. DTO has only IdentityModel/JWT 8.15.0 and Newtonsoft 13.0.4. Removing unused Oracle EF later exposed Models' accidental EF transitive dependency.

## Historical delivery and test dependencies

WPR-INV-005, **observed**: ScheduleDelivery references DTO, Logging.Abstractions/Options 8.0.2, IdentityModel/JWT 8.15.0, Newtonsoft 13.0.4, SpreadCheetah 1.20.0, Sylvan 0.4.25, Serilog core 4.3.0. Tests reference all except original AuthServer: Coverlet 6.0.4, MVC.Testing 8.0.22, ASP.Testing 8.10.0, Test SDK 18.0.1, Moq 4.20.72, NUnit 4.4.0, analyzers 4.11.2, adapter 5.2.0. No discovery/execution inferred from references.

## Publishing images and hosting

WPR-INV-006, **observed source**: Docker Node 24.15.0 Alpine, separate .NET 8 Alpine SDK/runtime, ICU and invariant=false; no root global.json COPY. Compose used root build context, Development, Data Protection mount and SQL Server 2022. build.sh ran frontend/publish but deleted dist. IIS in-process web.config invoked the DLL, did not install runtime/ANCM. Launch profiles set environment, not framework pins.

## Entry points behavior and external controls

WPR-INV-007, **observed source**: VS Code launch hardcoded net8 debug path; tasks and Playwright inherited CLI SDK/shared target. Copilot/Gemini verify/format hooks had no hardcoded major, cache included SDK/global.json/props. No tracked CI/publish profile. Inventory inspected proxy/health/Swagger, async helpers, EF histories, email parsing and docs. Commands had to cover solution and both tools separately, temporary publish/image, never shared migrations.

## Net8 baseline

WPR-PLAN-002, **observed September 24**: SDK 8.0.420 selected; seven-project restore passed, build 379 warnings/0 errors. Full tests 272 pass/2 fixture-route failures/1 existing ignored fixture. Failed full run emitted no whole-suite coverage; three passing Emailer tests yielded 0.71% scoped coverage only. Transitive audit reported zero vulnerabilities, not universal security proof. Baseline was not green.

## Warning baselines

WPR-PLAN-003, **observed**: baseline IDs CA1034, CA1054, CA1062, CA1307, CA1308, CA1309, CA1707, CA1847, CA1859, CA1861, CA2000, CA2227, CA5391, CS0114, CS8601, CS8603, SYSLIB0051. Later clean stages had 383 occurrences, same 17 IDs. Compare locations/counts/IDs. Incremental 21-warning output is not a clean baseline; RID image publishes each had 612 warnings/same 18 IDs, a separate baseline.

## Baseline fixture route repair

WPR-PLAN-016, **observed**: .NET 9 source gate had 279 pass/2 original failures/1 ignore. Test-host reproduction showed bodyless JSON fixture requests fell through to YARP, 404 rather than 401/JSON. `23aaf8a` repaired inferred-body routing, kept assertions and added empty-body contract; subsequent full gate required independent verification.

## Net9 checkpoint evidence

WPR-PLAN-017, **observed**: independent run 169 contracts, 2,739 visits/50.82% scoped line coverage. Fixture repair run 282 pass/54.04% full line coverage was a different revision. Integrated `29f8a62`: SDK 9.0.305, both runtime families/tools 9.0.20, 286 pass/1 existing ignore, 383 warnings/0 errors, 3,086/5,406 points, 57.08% line/49.41% branch, no reported vulnerabilities. Full solution, disposable providers and image gates passed locally, not hosted CI/deployment.

## Resolved transitive package evidence

WPR-PLAN-018, **observed**: EF SQL/SQLite 9.0.20, OpenIddict 7.7.1, Quartz Hosting 3.22.0. Web/Services SqlClient direct 6.1.3, Models transitive 5.1.9 with no reported advisory. Central direct management neither equalized nor froze all transitives.

## Oracle health contract

WPR-PLAN-006, **project-decision with focused tests**: owned async IHealthCheck kept missing DefaultConnection configuration-time ArgumentException, liveness tag, /health Healthy/Degraded 200 and Unhealthy 503, cancellation/disposal. Expected construction/open failures yield generic unhealthy without credentials; programming faults surface. Controlled DbConnection tests prove semantics, not real Oracle readiness.

## Accepted forwarded header risk

WPR-PLAN-007, **project-decision**: owner retained empty KnownNetworks/KnownProxies trust lists, accepting arbitrary forwarded host/proto/for spoofing contrary to official narrow-trust recommendation. .NET 10 only renamed KnownNetworks to KnownIPNetworks. Never call this hardened or assert spoof rejection. Another project needs its own trust decision; this is an unsafe project exception, not portable secure default.

## Accepted package policy

WPR-PLAN-031 and WPR-TKT-PKG-001, **project-decision**: central exact direct versions for all seven projects, preserve package metadata/remove project Version attributes, pin eight floats, no lock file. Inspect transitives at both stages.

ASP authentication/OpenAPI/diagnostics/MVC.Testing, EF SQL/SQLite/Design/Tools and direct Extensions configuration/logging/options: 9.0.20 -> 10.0.12. ASP.Testing: 9.10.0 -> 10.10.0. OpenIddict three packages 7.7.1 both; Quartz Hosting 3.22.0 -> 4.1.1; IdentityModel/JWT four packages 8.23.0 both; SqlClient 6.1.3 -> 6.1.6 minimum, avoiding v7 auth changes; ODP 23.26.301 both. Serilog ASP 9.0.0 -> 10.0.0, Expressions 5.0.0/core 4.3.0 unchanged. Both EF tools 9.0.20 -> 10.0.12.

Independent test tools deliberately adopted at stage 9: Test SDK 18.10.1, NUnit 4.6.1, adapter 6.3.0, analyzers 4.15.0, Coverlet 10.0.1, retained at stage 10. Unused Oracle EF and the unverified health package were removed; the report driver was retained. This is narrower than [latest-version research](../routes/net8-to-net10/dependency-compatibility/compatibility-matrix.md).

## Retained dependencies and conditional upgrades

WPR-PLAN-032 and WPR-TKT-PKG-002, **project-decision**: Hangfire 1.8.22, YARP 2.3.0, Moq 4.20.72, Newtonsoft 13.0.4, SpreadCheetah 1.20.0, Sylvan 0.4.25 and Async/File sinks 2.1.0/7.0.0 were retained absent a constraint, security or behavior need. Swashbuckle 7.2.0 retention was conditional on runtime Swagger gates; the plan named a 9.0.6 -> 10.2.3 migration fallback. Actual stage 9 retained 7.2.0; .NET 10 failed host startup and adopted 10.2.3. Do not claim an executed 9.0.6 stage or silently dropped endpoints.

## Approved stage9 edit surfaces

WPR-TKT-EDIT-001, **project-decision**: root SDK/shared target, central pins/provider-health removal, both EF tools, Docker tags/props-before-restore, debugger/docs. Keep single TFM/language/analyzers/nullable/audit, custom Angular provider/Swagger/YARP/web.config/hooks unless concrete failure. Probe preserves async/cancel/dispose/configuration-time missing string/200/503/no-secret contract. Retained trust-all needed a separate security decision to change.

## Approved stage10 edit surfaces

WPR-TKT-EDIT-002, **project-decision**: update version surfaces/KnownIPNetworks, adopt two BCL ToListAsync calls only if equivalent, remove AuthServer helper only, retain Services helper. Preserve FormatException/SmtpException and API/browser statuses. No speculative migrations/static-asset/OpenAPI rewrite. Both models/tools, SQL/persistence/timestamps, analyzers/NU1510 and ICU/assets determine any additional work.

## Net10 source contracts

WPR-PLAN-020, **observed**: two AuthServer calls adopted BCL after single-enumeration/order checks; only the AuthServer helper was removed. The email consecutive-dot regression test reached SMTP on .NET 9 but threw unwrapped FormatException before SMTP on .NET 10. Existing SmtpException wrapping stayed unchanged.

## Net10 source gate and analyzers

WPR-PLAN-021, **observed September 24**: SDK 10.0.401, both runtime families and tools at 10.0.12, 64 focused contracts plus HTTP 200 from disposable AuthServer discovery. CA1873 logger work was guarded; the CA1849 ZIP async API and two CA1861 arrays were repaired. A temporary scoped Moq CA1873 pragma was later removed in hardening, not retained as final policy. This source gate was not full provider, publish, image or coverage proof.

## Net10 local checkpoint evidence

WPR-PLAN-022, **observed at `a6666d4`**: SDK 10.0.401, runtime/tools/EF 10.0.12, OpenIddict 7.7.1, Quartz 4.1.1 and SqlClient 6.1.6. The full suite had 293 passes and 1 ignore, with 383 warnings and 0 errors, no NU1510 or reported vulnerabilities; configuration JSON had no explicit nulls. Coverage was 3,075/6,572 points, 46.78% line and 30.3% branch. Both rollback and stage 10 RID images had 612 warnings with the same 18 IDs. None proves later repetition of every gate.

## Authorization code and PKCE contracts

WPR-PLAN-012, **observed in stages 9 and 10 against disposable seeded SQLite**: discovery returned 200; the invalid-client token response was 401 with invalid_client, not 400; authorization returned 302 with a persisted code; S256 PKCE redemption returned 200 with access and identity token presence. The corrected stored token type was `urn:openiddict:params:oauth:token-type:authorization_code`, with redeemed status and non-null RedemptionDate. No token or credential values are retained. No live identity provider or refresh-token flow was proved.

## Stage image and host contract evidence

WPR-PLAN-024, **observed earlier gates**: stage 9 image `sha256:f03da54a777fb7eeb0c9de77d7ae1322dbf42707fe621983c57e49e802a76a4d`, stage 10 image `sha256:41b6c51163d6b95dc116ed4f23162d11612a5964204bc455b3830cee5ddad066`. Both served anonymous session JSON, Angular shell/bundled JavaScript and Swagger JSON/UI/loader with HTTP 200; deliberately unavailable synthetic Oracle returned 503 without details. Hangfire tables and heartbeat were present. Both runtime families matched their stage, and ICU, non-UTC timezone and 30-second stop checks passed.

Controlled hosts separately proved Oracle healthy HTTP 200, protected API 401/403 with Location expectations, intended browser redirects, Excel and email contracts. A 503 is not healthy or live Oracle evidence. A local image is not Jenkins, IIS or Fargate readiness proof.

## Post upgrade hardening

WPR-PLAN-025, **observed September 28**: async naming (`cef2b50`), pragma removal (`559751d`), cookie harness deduplication/disposal (`5ccb11a`), fixture parsing encapsulation (`f0c8eff`), health factory failure hygiene (`8fe4d90`), health-only DI seam (`87411a5`), coverage analysis (`6cec9ea`), fixture error tests (`0ac94e0`), null initialization removal (`72a9cb4`). New cookie CA2000 was detected by clean rebuild and structurally repaired, not suppressed.

Fixture contracts distinguish zero-byte bodies from `{}`, malformed JSON returning 400, unsupported Content-Type returning 415 and authentication precedence. Twelve focused health tests, eight registration tests and sixteen final fixture tests were reported for their own tasks, not as substitutes for full-suite evidence.

## Final hardening evidence limits

WPR-PLAN-026 and WPR-HAND-002, **observed final solution evidence**: clean rebuild **383 baseline warnings, 0 errors**; full tests **302 passed, 1 pre-existing ignored fixture**. OpenCover **3,081/6,574 sequence points, 46.86% line, 30.44% branch**.

Earlier provider/migration/authorization-code/publish/image gates were **not all repeated after hardening**. Attribute them to their earlier revisions/stages, never manufacture all-green final deployment or image evidence. Existing BaseServiceTests ignore is baseline, not a new skip. External CI/hosts/services remain unverified.

## SDK minimum versus observed selection

WPR-PLAN-027, **project-decision**: the final nominal SDK 10.0.302/latestMinor was chosen for CI compatibility, but gates selected 10.0.401. Exact 10.0.302 execution was not established. Do not relabel results or equate the minimum with the selected feature band. Docker does not import root global.json.

## Coverage stage comparison

WPR-COV-001, **observed isolated historical runs**: rollback `29f8a62` with SDK 9.0.305 had 3,086/5,406 points (57.08%); the .NET 10 checkpoint with SDK 10.0.401 had 3,075/6,572 (46.78%). The delta was -11 visited points, +1,166 total points and -10.30 percentage points. Passing test counts alone do not explain it. The later final hardening result of 46.86% is a different report.

## Coverage point decomposition

WPR-COV-003, **observed normalized XML comparison**:

| Assembly | .NET 9 points | .NET 10 points | Generated | Other |
| --- | ---: | ---: | ---: | ---: |
| Services | 1199 | 1609 | +377 | +33 |
| AuthServer | 893 | 881 | 0 | -12 |
| ScheduleDelivery | 57 | 60 | 0 | +3 |
| DTO | 970 | 970 | 0 | 0 |
| workPlanReports | 2243 | 2631 | +377 | +11 |
| Models | 44 | 421 | +377 | 0 |
| Total | 5406 | 6572 | +1131 | +35 |

The other +35 points comprise DbFetch +22, HangFireSchedulerService +12, removed AuthServer helper -12, AuthController +6, ApplicationLifetimeService +3, Emailer +3, Services helper -1 and compiled _Host/Error Razor pages +1 each. [Generator attribution, arithmetic and variability](../lessons.md#generated-code-coverage-denominators) are diagnostics, not exclusion policy.

## External CI source inspection

WPR-TKT-EXT-001, **observed definitions, not execution**: external Jenkinsfile shared buildmodular handled backend/coverage/scanners/unified zip/release; Groovy config selected a Windows worker, published main host to dist and tested solution, no SDK pin. No application-repo workflow/Actions/deployment record found. Actual worker SDK/runtime/feeds/jobs/shared-library behavior unknown. Operational coordinates/worker identifiers omitted. Changes require a separate CI/CD-reviewed PR, not speculative local Jenkins files.

## Corrected Windows hosting platform

WPR-TKT-EXT-002, **project-decision/owner correction**: Windows Server 2019 Datacenter with IIS 10, not IIS 7. Public support covers Server 2019 x64, not an inspected installation. web.config invokes the DLL in-process; Hosting Bundle, runtime, ANCM and app pool verification, deployment and rollback remain Windows Admin-owned.

## External readiness and owner deferrals

WPR-PLAN-030, WPR-HAND-003, **unverified**: CI/CD, Windows Admin and AWS requests prepared; delivery/acknowledgement deferred by owner until channels supplied. Jenkins, IIS and Fargate remain unverified until actual owner results. No real Oracle, identity or SMTP success claimed.

Checklists are [bundled in the playbook](../playbook.md#local-versus-deployment-readiness). Future ECS Fargate and Lambda for suitable parts do not mean this long-lived Hangfire/ASP.NET app runs unchanged on Lambda. A [Lambda/API Gateway workflow article](https://aws.amazon.com/blogs/compute/getting-started-with-serverless-for-developers-part-4-local-developer-workflow/) is not execution proof; decomposition/adapter/deployment is separate work.

## Document extraction review

The October 1, 2026 note records Milestone 2 source-extraction acceptance, not the final integrated review. Milestone 4 document acceptance and destination knowledge-base reconciliation are recorded in the [document review](../document-review.md). No .NET commands, historical runner, trial project, model, benchmark, packaging, installer, migration or live deployment was executed. This case study remains historical WorkPlanReports evidence and does not prove another project's migration or live client behavior.
