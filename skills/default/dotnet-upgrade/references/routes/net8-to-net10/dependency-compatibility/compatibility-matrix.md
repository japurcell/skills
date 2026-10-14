# Historical dependency compatibility matrix

## Research scope and interpretation

WPR-DEP-001 through 008 and WPR-TKT-DEP-001, **researched**, **2026-09-23**. Covers all direct package families in seven backend projects and both local EF tools. "Latest" means stable published no later than that snapshot, not today. Packaged lib/TFM assets differ from NuGet computed compatibility and vendor certification. Build/runtime behavior still needs actual verification.

The baseline was net8 with SDK 8.0.204/latestMinor. EF 9 runs on net8/net9 with net8 provider assets; EF 10 requires SDK/runtime 10 and net10 assets, so cannot run at the net9 checkpoint. Historical STS 9 through November 2026 and LTS 10 through November 2028 are corrected to exact dates in [prompt provenance](../../../provenance/original-prompt.md#support-lifecycle-correction), not offered as perpetual advice.

This is **available-version research**, not [accepted policy](../../../case-studies/workplan-reports.md#accepted-package-policy). Assets/bounds and authorities are detailed separately in [official package evidence](official-package-evidence.md). Original package locations are retained in the [case inventory](../../../case-studies/workplan-reports.md#historical-main-host-dependencies). [Route](../index.md).

## Microsoft framework and SqlClient

Authentication.JwtBearer/OpenIdConnect were at 8.0.23; Diagnostics.EntityFrameworkCore at 8.0.23 in the main host and 8.* in AuthServer; OpenApi at 8.0.23 in the main host and 8.0.22 in Services/Models; Mvc.Testing at 8.0.22. Research recommends **9.0.20 then 10.0.12**, with actual net9/net10 assets. Keep servicing and family alignment. OpenAPI 10 can alter the Swagger graph.

EF SqlServer/Tools 8.0.10 and Design/Sqlite 8.* -> **9.0.20 then 10.0.12**. EF 9 assets target net8; EF 10 targets net10. Keep runtime, provider, design and tools major and servicing versions aligned. EF SQL 10 needs SqlClient >=6.1.6.

Extensions Configuration 8.0.0, FileExtensions 8.0.1, Json 8.0.1, Logging.Abstractions 8.0.2 and Options 8.0.2 -> **9.0.20 then 10.0.12**. Named version 9 packages include net9; version 10 packages include net10, most also net8/net9. Actual framework references and pruning determine need, not adding duplicate direct references.

SqlClient 6.1.3 -> research **7.1.0 for both stages**. Official support covers .NET 8+; assets target net8/net9/netstandard2, with no direct net10 asset. Version 7 Entra connection-string authentication modes require a separate extensions package. The net9 group's IdentityModel >=8.16.0 requirement is satisfied by 8.23.0; EF SQL 10's 6.1.6 floor is also satisfied. Accepted strategy used 6.1.3 then 6.1.6 to avoid an unrelated version 7 authentication change.

Authorities: [ASP authentication](https://api.nuget.org/v3/registration5-gz-semver2/microsoft.aspnetcore.authentication.jwtbearer/index.json), [diagnostics](https://api.nuget.org/v3/registration5-gz-semver2/microsoft.aspnetcore.diagnostics.entityframeworkcore/index.json), [OpenApi](https://api.nuget.org/v3/registration5-gz-semver2/microsoft.aspnetcore.openapi/index.json), [EFSQL](https://api.nuget.org/v3/registration5-gz-semver2/microsoft.entityframeworkcore.sqlserver/index.json), [EF9](https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-9.0/whatsnew), [EF10](https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-10.0/whatsnew), [Configuration](https://api.nuget.org/v3/registration5-gz-semver2/microsoft.extensions.configuration/index.json), [Logging](https://api.nuget.org/v3/registration5-gz-semver2/microsoft.extensions.logging.abstractions/index.json), [Options](https://api.nuget.org/v3/registration5-gz-semver2/microsoft.extensions.options/index.json), [SqlClient README](https://github.com/dotnet/SqlClient/blob/d189eeb7cfafcbe6ac2bb0c63eb5cee1cfd71495/README.md), [7.1.0](https://www.nuget.org/packages/Microsoft.Data.SqlClient/7.1.0).

## Oracle provider and driver

Oracle.EntityFrameworkCore 8.23.60 in main/Services/Models -> research **9.23.26301 then 10.23.26301**. The net8 EF 9 artifact requires Relational [9,10); the net10 EF 10 artifact requires Relational [10,11). Both require ODP [23.26.301,24). Never combine the EF 10 provider with EF 9.

ManagedDataAccess.Core 23.26.0 -> **23.26.301 for both stages**; the starting version was below the provider floor. Assets target net8/netstandard2.1, not net9/net10. The provider dependency is evidence, not standalone driver .NET 10 certification or live connectivity. The August release-note date differs from September 8 publication. The owner removed unused Oracle EF after finding no UseOracle, retaining the direct report driver.

Authorities: [EF9](https://www.nuget.org/packages/Oracle.EntityFrameworkCore/9.23.26301), [EF10](https://www.nuget.org/packages/Oracle.EntityFrameworkCore/10.23.26301), [ODP](https://www.nuget.org/packages/Oracle.ManagedDataAccess.Core/23.26.301), [EF documentation](https://docs.oracle.com/en/database/oracle/oracle-database/26/odpnt/ODPEFCore.html), [ODP docs](https://docs.oracle.com/en/database/oracle/oracle-database/26/odpnt/index.html).

## Identity OpenIddict Quartz and floating versions

IdentityModel.Logging/Protocols/Protocols.OpenIdConnect/System.IdentityModel.Tokens.Jwt 8.15.0 -> **8.23.0 for both stages**; all have net9/net10 assets and matching constituent floors. The publish date is unknown; an earlier incorrect date was removed.

OpenIddict.AspNetCore/EntityFrameworkCore/Quartz floats -> **7.7.1 for both stages**, with net9/net10 assets. EF Relational requires >=9.0.19 on net9 and >=10.0.11 on net10. Quartz integration requires [3.20.1,4) on net9 and >=4 on net10. Starting Hosting 3.18.1 was below the net9 floor; research recommends **3.22.0 then 4.1.1**. Hosting 3.22 has net9/net10/Standard2 assets but does not override integration's net10 Quartz 4 requirement; Hosting 4.1.1 is net10-only. Verify AddQuartzHostedService, major APIs and startup.

Eight floats: EF Design/Sqlite/diagnostics 8.*, OpenIddict ASP/EF/Quartz *, and Serilog ASP/Expressions *. They permit restore drift; 8.* retains EF 8. Research's NuGet lock-file recommendation for repeatability differs from accepted central package management without a lock file. Central direct pins do not freeze transitives.

Authorities: [IdentityModel8.23](https://github.com/AzureAD/azure-activedirectory-identitymodel-extensions-for-dotnet/releases/tag/8.23.0), [OpenIddict7.7.1](https://github.com/openiddict/openiddict-core/releases/tag/7.7.1), [Quartz groups](https://api.nuget.org/v3/registration5-gz-semver2/openiddict.quartz/index.json), [Quartz README](https://github.com/quartznet/quartznet/blob/bf953e895f96df172e9c1938d73ea2d3a8497023/README.md), [3.22](https://github.com/quartznet/quartznet/releases/tag/v3.22.0), [4.1.1](https://github.com/quartznet/quartznet/releases/tag/v4.1.1), [floating versions](https://learn.microsoft.com/en-us/nuget/concepts/dependency-resolution#floating-versions).

## Health Hangfire and proxy evidence

AspNetCore.HealthChecks.Oracle 9.0.0 -> research **9.0.0 for both stages**, with net8/netstandard2/2.1 assets. The README covers ASP.NET only through 8; there is no 9/10-specific stable asset or vendor claim. Vendor support for both stages is **UNVERIFIED**; do not invent version 10. Transitive HealthChecks/Abstractions declared 8.0.11, but the actual restore was then uninspected; research's 9.0.20/10.0.12 recommendation is not permission to add direct packages.

Hangfire.AspNetCore/Core/SqlServer 1.8.22 -> research **1.8.25 for both stages**, with portable/older targets and no net9/net10 asset or certification. Stronger runtime support is **UNVERIFIED**; test SQL storage, job enqueue and processing. Accepted strategy retained 1.8.22.

YARP 2.3.0 is retained for both stages; assets target net6/7/8, with official ".NET 8.0 and newer" support. No bump is required purely for the runtime.

Authorities: [health README](https://github.com/Xabaril/AspNetCore.Diagnostics.HealthChecks/blob/3b6abbd374a5d7bc8d209ff48bc38df947266054/README.md), [health project](https://github.com/Xabaril/AspNetCore.Diagnostics.HealthChecks/blob/3b6abbd374a5d7bc8d209ff48bc38df947266054/src/HealthChecks.Oracle/HealthChecks.Oracle.csproj), [health metadata](https://api.nuget.org/v3/registration5-gz-semver2/aspnetcore.healthchecks.oracle/index.json), [Microsoft health](https://api.nuget.org/v3/registration5-gz-semver2/microsoft.extensions.diagnostics.healthchecks/index.json), [Hangfire release](https://github.com/HangfireIO/Hangfire/releases/tag/v1.8.25), [README](https://github.com/HangfireIO/Hangfire/blob/1d4778c23410b365b5f9ce35458202efe0b0f3ea/README.md), [YARP](https://github.com/dotnet/yarp/releases/tag/v2.3.0).

## Logging and Swashbuckle

Serilog.AspNetCore 9.0.0 in main/Services and * in AuthServer -> **9.0.0 then 10.0.0**, matching Hosting/runtime major as upstream recommends. Explicit version 9 ahead of original net8 needed a compatibility decision. Core 4.3.0 -> research **4.4.0 for both stages**, with net9/net10 assets; accepted strategy retained 4.3. Expressions 5.0 and AuthServer * -> **5.0 for both**, with Standard2/net8 assets and the Serilog 4 dependency transition. Async 2.1/File 7 are retained, with portable assets plus Async net8/File net9, and no net10-specific asset. Package majors are independent.

Swashbuckle 7.2 -> research **9.0.6 then 10.2.3**. Version 9 dependencies target net9; the version 10 metapackage has net8/9/10 groups. Version 10 brings OpenAPI.NET 2 major changes; upstream recommends upgrading via 9.0.6. Accepted initial retention was conditional; actual stage 9 kept 7.2 and stage 10 startup failure required 10.2.3, not a fictional 9.0.6 execution. Do not replace Swagger or drop endpoints.

Authorities: [Serilog ASP README](https://github.com/serilog/serilog-aspnetcore/blob/2002d1f7e356bf0e2980dd5a764529d8ee615264/README.md), [ASP10](https://github.com/serilog/serilog-aspnetcore/releases/tag/v10.0.0), [core4.4](https://github.com/serilog/serilog/releases/tag/v4.4.0), [Expressions5](https://github.com/serilog/serilog-expressions/releases/tag/v5.0.0), [Async](https://github.com/serilog/serilog-sinks-async/releases/tag/v2.1.0), [File](https://github.com/serilog/serilog-sinks-file/releases/tag/v7.0.0), [Swashbuckle10](https://github.com/domaindrivendev/Swashbuckle.AspNetCore/releases/tag/v10.0.0), [10.2.3](https://github.com/domaindrivendev/Swashbuckle.AspNetCore/releases/tag/v10.2.3), [migration](https://github.com/domaindrivendev/Swashbuckle.AspNetCore/blob/HEAD/docs/migrating-to-v10.md).

## Spreadsheet and JSON packages

SpreadCheetah 1.20 -> research **1.28 for both stages**, with explicit .NET 6-10/Standard2 support and net8/9/10 assets. Sylvan.Data.Excel 0.4.25 -> **0.5.8**, with net6/net8/Standard2/2.1 assets, not direct net9/net10 assets; a 0.x change requires read/write checks. Accepted older pins were retained absent demonstrated need. Newtonsoft 13.0.4 remains the latest 13.x with Standard2 assets, not a runtime-major-matching version.

Authorities: [SpreadCheetah README](https://github.com/sveinungf/spreadcheetah/blob/1460188a5dd792fa90c906a2fcbacf1eb8de6bec/README.md), [release](https://github.com/sveinungf/spreadcheetah/releases/tag/v1.28.0), [Sylvan](https://www.nuget.org/packages/Sylvan.Data.Excel/0.5.8), [Json.NET](https://www.newtonsoft.com/json), [.NET Standard](https://learn.microsoft.com/en-us/dotnet/standard/net-standard).

## Test packages and local tools

Mvc.Testing 8.0.22 -> **9.0.20/10.0.12**, matching host net9/net10. ASP.Testing 8.10 -> **9.10/10.10**, distinct helpers with net8/net9 then net8/net9/net10 assets. Test SDK 18.0.1 -> **18.10.1 for both stages**, net8 tooling rather than an app library; VSTest's release was September 15. NUnit 4.4 -> **4.6.1**, with net8/net6/Framework assets, not dedicated 9/10 assets. Adapter 5.2 -> **6.3**, with Platform 2.3.3 bridge/MSBuild; discovery needs execution. Analyzers 4.11.2 -> **4.15**, released September 12, using Roslyn rather than a runtime TFM. Moq 4.20.72 is retained with Standard2/2.1/net6/net462 assets. Coverlet 6.0.4 -> **10.0.1**, an MSBuild version, not a runtime number.

EF tools in AuthServer 8.0.18 and API 8.0.4 -> **9.0.20 then 10.0.12**, each local manifest independently aligned with Design/Tools. The original EF 10 category reverses initial paths; inventory/matrix agree, and the discrepancy is preserved. The root SDK 8 pin/latestMinor will not select 9/10. Verify real discovery, execution and coverage sequentially after tool changes, rather than infer them from assets or majors.

Authorities: [integration tests](https://learn.microsoft.com/en-us/aspnet/core/test/integration-tests?view=aspnetcore-10.0), [ASP Testing10.10](https://www.nuget.org/packages/Microsoft.AspNetCore.Testing/10.10.0), [VSTest](https://github.com/microsoft/vstest/releases/tag/v18.10.1), [NUnit](https://github.com/nunit/nunit/releases/tag/v4.6.1), [adapter](https://github.com/nunit/nunit3-vs-adapter/releases/tag/V6.3.0), [analyzers](https://github.com/nunit/nunit.analyzers/releases/tag/4.15.0), [Moq](https://github.com/devlooped/moq/releases/tag/v4.20.72), [Coverlet](https://github.com/coverlet-coverage/coverlet/releases/tag/v10.0.1), [EF CLI](https://learn.microsoft.com/en-us/ef/core/cli/dotnet), [EF9 tool](https://www.nuget.org/packages/dotnet-ef/9.0.20), [EF10 tool](https://www.nuget.org/packages/dotnet-ef/10.0.12).

## Blocking risks and runtime unknowns

WPR-TKT-DEP-002, **unverified** at research: eight floats, old SDK pin, Oracle provider/driver mismatch and target-specific OpenIddict/Quartz bounds. Health-check support, standalone Oracle connectivity, Quartz hosting and actual tests/coverage need stage evidence. The Serilog ASP major ahead of net8 is an explicit choice, not blanket support. Latest research and selected strategy remain separate.
