# .NET 9 research index

**Researched**, date unspecified. Original net8/SDK 8.0.204 source assessment, not runtime proof or the final tree. All applicability below is WorkPlanReports-specific. Source: immutable `research/dotnet-9-official-guidance/index.md`; WPR-N9-INDEX-001/002.

## Catalog coverage

88 formal entries: ASP.NET 6; containers 2/deployment 2; core 20; crypto 4; EF 12 general/10 Cosmos; interop/JIT 3; networking 6; SDK 10; serialization 3; WinForms 9/WPF 1. Linked C# 13 article separately reviewed because `LangVersion=latest`.

[ASP.NET](aspnetcore.md), [containers/deployment](containers-deployment.md), [core/globalization](core-libraries.md), [crypto](cryptography.md), [EF](ef-core.md), [interop/JIT](interop-jit.md), [networking](networking.md), [SDK](sdk-msbuild.md), [serialization](serialization.md), [WinForms/WPF](windows-forms-wpf.md), [C# 13](csharp-13.md).

## Action summary and evidence limits

Align actual SDK/targets/framework/Extensions/EF/providers/tools/images, VS/MSBuild 17.12+ for net9. Check both Development hosts for DI validation, models/snapshots/transactions and private Design tooling, ingress/OIDC, custom static assets and workbooks, runtime environment precedence/ICU, C# 13 and transitive OOB/HTTP telemetry.

These were proposed checks, not results. Research recommended trusted proxies and Oracle EF alignment; [accepted decisions](../../../case-studies/workplan-reports.md) differed. `MapStaticAssets` was optional, not mechanical replacement. Build, startup, persistence, published assets and external telemetry have distinct evidence. [Route](../index.md) and [authorities](../../../official-sources.md).

Authorities: [.NET upgrade](https://learn.microsoft.com/en-us/dotnet/core/install/upgrade), [8-to-9 ASP.NET](https://learn.microsoft.com/en-us/aspnet/core/migration/80-to-90?view=aspnetcore-10.0&tabs=visual-studio-code), [9 catalog](https://learn.microsoft.com/en-us/dotnet/core/compatibility/9.0).
