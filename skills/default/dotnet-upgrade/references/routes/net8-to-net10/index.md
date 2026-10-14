# .NET 8 to .NET 10 route

Documented route: .NET 8 through .NET 9 and .NET 10 changes, not certification that every surface or another project has been exercised. Start at the [playbook](../../playbook.md) and [authorities](../../official-sources.md), then actual target categories. The original checkout is unnecessary.

## Catalog coverage and conditional loading

WPR-MAP-002, **researched**: 88 .NET 9 entries plus linked C# 13 review, and all 15 .NET 10 categories. Retain categories even when original source marked them not applicable. Reassess actual code, graphs, publish settings and hosts. Negative direct-source searches do not certify dependency internals or deployment configuration.

| Load when | Bundled references |
| --- | --- |
| Catalog coverage | [9 index](dotnet-9/index.md), [10 index](dotnet-10/index.md) |
| Web/auth/proxy/Swagger/assets/startup | [9 ASP.NET](dotnet-9/aspnetcore.md), [10 ASP.NET](dotnet-10/aspnet-core.md) |
| Containers/publish/OS/culture/shutdown | [9 deployment](dotnet-9/containers-deployment.md), [10 containers](dotnet-10/containers.md), [10 globalization](dotnet-10/globalization.md) |
| Core/compiler/LINQ/streams | [9 core](dotnet-9/core-libraries.md), [C# 13](dotnet-9/csharp-13.md), [10 core](dotnet-10/core-libraries.md) |
| EF/models/migrations/timestamps | [9 EF](dotnet-9/ef-core.md), [10 EF](dotnet-10/entity-framework-core.md) |
| Crypto/native/reflection | [9 crypto](dotnet-9/cryptography.md), [10 crypto](dotnet-10/cryptography.md), [9 interop/JIT](dotnet-9/interop-jit.md), [10 interop](dotnet-10/interop.md), [reflection](dotnet-10/reflection.md) |
| HTTP/telemetry/email | [9 networking](dotnet-9/networking.md), [10 networking](dotnet-10/networking.md) |
| SDK/MSBuild/NuGet/tools/editor | [9 SDK](dotnet-9/sdk-msbuild.md), [10 SDK](dotnet-10/sdk-msbuild.md), [install tool](dotnet-10/install-tool.md) |
| Configuration/DI/logging/services | [extensions](dotnet-10/extensions.md) |
| Serialization | [9](dotnet-9/serialization.md), [10](dotnet-10/serialization.md) |
| Desktop | [9 WinForms/WPF](dotnet-9/windows-forms-wpf.md), [10 WinForms](dotnet-10/windows-forms.md), [10 WPF](dotnet-10/wpf.md) |
| Dependency constraints | [matrix](dependency-compatibility/compatibility-matrix.md), [artifact evidence](dependency-compatibility/official-package-evidence.md) |
| Historical implementation | [lessons](../../lessons.md), [case study](../../case-studies/workplan-reports.md), [ledger](../../provenance/source-map.json) |

## Net9 action summary

WPR-TKT-N9-001, **researched**, date unspecified: align SDK/TFM/framework/Extensions/EF/providers/tools/images, VS/MSBuild 17.12+, C# 13/analyzers. Risks: ingress trust/OIDC, pending models/transactions/Design tooling, environment precedence/ICU, Excel and custom assets. Research proposed narrow proxy trust and Oracle EF alignment; owners later retained trust-all risk and removed unused Oracle EF. Research is not approval.

## Net9 research gates

WPR-TKT-N9-002, **unverified requests**: full suite, both Development hosts/DI, contexts/scripts/disposable migrations, actual container/auth/report/database/assets/YARP, workbooks, transitive OOB packages, C# collection/interface analyzers and external `server.port`/EventSource consumers. Listing does not prove all surfaces later exercised. Ingress/telemetry remained unverified.

## Net10 action summary

WPR-TKT-N10-001, **researched**, September 23, 2026: baseline net8, not net9. Assess both crossed versions, align SDK/targets/framework/EF/tools/images, rename KnownIPNetworks, resolve floats/providers and preserve Swagger absent a separate design. EF 10 runtime, SQLite offsets, async LINQ, MailAddress, cookie scheme/API and Alpine/OpenSSL/ICU are risks.

## Net10 research refresh and gates

WPR-TKT-N10-002, **unverified requests**: tests/analyzers/audit/NU1510, persistence/authorization/timezones, SQL review, API/browser/Swagger/email, image startup/health/culture/stop. External NuGet and ICU/OpenSSL overrides unknown. Refresh the evolving catalog and required authorities before execution.

## Documented and unverified surfaces

Historical local evidence covers ASP.NET/Angular, SQLite/OpenIddict, SQL Server/Hangfire, email parsing without live SMTP, workbook output and Alpine publish/image/globalization/shutdown at specific stages. Desktop, Cosmos, native loaders, trimming/AOT, browser .NET and telemetry remain documentary research. Jenkins/IIS/Fargate, real Oracle/identity/SMTP were unproved. Final hardening reran solution/coverage, not all earlier provider/image gates.

.NET 10/dependency research **2026-09-23**; .NET 9 date unspecified; lifecycle retrieval **2026-09-30**. Rechoose versions/staging with approval for future projects. Unsupported routes remain discovery/research until specifically reviewed.
