# .NET 10 research index

**Researched**, snapshot **2026-09-23**. Adapted from original `dotnet-10-official-guidance/README.md`, WPR-N10-INDEX-001/002. Original baseline was net8, SDK 8.0.204/latestMinor, latest language/analyzers, nullable/implicit usings and transitive audit, not already net9.

## Baseline category loading and refresh

Confirm the intermediate stage or assess all 8-to-9 changes too. SDK, target, framework/EF packages, local tools, images, external workers and hosting are independent. The catalog is a work in progress; refresh before execution.

All 15 categories: [ASP.NET](aspnet-core.md), [containers](containers.md), [core](core-libraries.md), [crypto](cryptography.md), [EF](entity-framework-core.md), [extensions](extensions.md), [globalization](globalization.md), [install tool](install-tool.md), [interop](interop.md), [networking](networking.md), [reflection](reflection.md), [SDK](sdk-msbuild.md), [serialization](serialization.md), [WinForms](windows-forms.md), [WPF](wpf.md).

## Migration actions and unverified gates

Proposed checks: provider/version/floats, KnownIPNetworks, cookie/OIDC/Swagger, explicit configuration nulls, MailAddress, full solution/analyzers/audit, reviewed provider SQL before schema changes, actual Alpine/native/culture/shutdown. Third-party majors are not Microsoft runtime numbers. No UseOracle made removal a decision; retained Oracle EF 10 would require driver 23.26.301+. OpenIddict EF/Quartz groups need separate constraints.

These proposals are not accepted latest-package mandates or observed passes. See [matrix](../dependency-compatibility/compatibility-matrix.md), [case](../../../case-studies/workplan-reports.md), [route](../index.md) and [refresh rules](../../../official-sources.md). Original "not applicable" judgments must be reassessed.

Authorities: [.NET upgrade](https://learn.microsoft.com/en-us/dotnet/core/install/upgrade), [9-to-10 ASP.NET](https://learn.microsoft.com/en-us/aspnet/core/migration/90-to-100?view=aspnetcore-10.0&tabs=visual-studio-code), [10 catalog](https://learn.microsoft.com/en-us/dotnet/core/compatibility/10).
