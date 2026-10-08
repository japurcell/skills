# Dated authorities and refresh rules

This bundle preserves original research summaries, not vendor documentation wholesale. The [ledger](provenance/source-map.json) retains original paths, SHA-256 digests, stable findings, classification and scope at application commit `25f3f822d56a6468bc50e52ac16d6331df6604c4`. Original paths are provenance, not runtime dependencies.

.NET 10 categories/dependencies: **2026-09-23**. .NET 9 files do not specify research dates. Application execution: September 24; hardening: September 28, 2026. Prompt capture/lifecycle retrieval recorded by the extraction plan: September 30. Bundle document reconciliation: October 1. No upstream URLs refreshed or application behavior rerun here.

## Primary starting points

| Authority | Historical use and boundary |
| --- | --- |
| [.NET upgrade guide](https://learn.microsoft.com/en-us/dotnet/core/install/upgrade) | SDK, TFM, build, CI and hosting, not merely retargeting. |
| [ASP.NET Core 8 to 9](https://learn.microsoft.com/en-us/aspnet/core/migration/80-to-90?view=aspnetcore-10.0&tabs=visual-studio-code) | First crossed major and optional static assets. |
| [.NET 9 catalog](https://learn.microsoft.com/en-us/dotnet/core/compatibility/9.0) | 88 historical entries plus linked compiler changes, [by category](routes/net8-to-net10/dotnet-9/index.md). |
| [ASP.NET Core 9 to 10](https://learn.microsoft.com/en-us/aspnet/core/migration/90-to-100?view=aspnetcore-10.0&tabs=visual-studio-code) | Does not imply source already was net9. |
| [.NET 10 catalog](https://learn.microsoft.com/en-us/dotnet/core/compatibility/10) | Work in progress, [by category](routes/net8-to-net10/dotnet-10/index.md), refresh before execution. |
| [Support policy](https://dotnet.microsoft.com/en-us/platform/support/policy/dotnet-core) | September 30 retrieval: .NET 8/9 end November 10, 2026; .NET 10 November 14, 2028. Maintenance is support. |
| [Release/support overview](https://learn.microsoft.com/en-us/dotnet/core/releases-and-support) | Article date recorded as 2026-05-15, not research date. |
| [EF 9 changes](https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-9.0/breaking-changes), [EF 10 changes](https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-10.0/breaking-changes) | Provider/tool/transaction/timestamp review distinct from ASP.NET guidance. |
| [EF providers](https://learn.microsoft.com/en-us/ef/core/providers/), [EF CLI](https://learn.microsoft.com/en-us/ef/core/cli/dotnet), [migration management](https://learn.microsoft.com/en-us/ef/core/managing-schemas/migrations/managing), [application](https://learn.microsoft.com/en-us/ef/core/managing-schemas/migrations/applying) | Major alignment, project/startup/context selection, drift and schema review. |
| [EF 10 release notes](https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-10.0/whatsnew) | Recorded article date 2025-10-02; SDK/runtime 10 required. |
| [Windows support](https://learn.microsoft.com/en-us/dotnet/core/install/windows), [IIS](https://learn.microsoft.com/en-us/aspnet/core/host-and-deploy/iis/?view=aspnetcore-10.0), [Hosting Bundle](https://learn.microsoft.com/en-us/aspnet/core/host-and-deploy/iis/hosting-bundle?view=aspnetcore-10.0) | Supported platform is not actual inspected hosting. |
| [Container images](https://learn.microsoft.com/en-us/dotnet/core/docker/container-images) | Explicit OS/native libraries/architecture need target checks. |

Detailed category URLs are preserved beside assessments. Package authorities, dates and bounds remain in [artifact evidence](routes/net8-to-net10/dependency-compatibility/official-package-evidence.md) and the [matrix](routes/net8-to-net10/dependency-compatibility/compatibility-matrix.md).

The original .NET 10 category selectors are also preserved: [extensions](https://learn.microsoft.com/en-us/dotnet/core/compatibility/10#extensions), [globalization](https://learn.microsoft.com/en-us/dotnet/core/compatibility/10#globalization), [install tool](https://learn.microsoft.com/en-us/dotnet/core/compatibility/10#install-tool), [interop](https://learn.microsoft.com/en-us/dotnet/core/compatibility/10#interop), [networking](https://learn.microsoft.com/en-us/dotnet/core/compatibility/10#networking), [reflection](https://learn.microsoft.com/en-us/dotnet/core/compatibility/10#reflection), [serialization](https://learn.microsoft.com/en-us/dotnet/core/compatibility/10#serialization), [Windows Forms](https://learn.microsoft.com/en-us/dotnet/core/compatibility/10#windows-forms), [WPF](https://learn.microsoft.com/en-us/dotnet/core/compatibility/10#windows-presentation-foundation-wpf) and [SDK/MSBuild](https://learn.microsoft.com/en-us/dotnet/core/compatibility/10#sdk-and-msbuild). These historical selectors are not evidence of fresh retrieval.

## Refresh before execution

Detect actual starting/destination versions and feature bands. Refresh both migration guides, all crossed catalogs/relevant entries, lifecycle, provider/tooling compatibility, target-specific NuGet groups, package security/support, image tags/OS and hosting requirements. Distinguish retrieval, article publication, release-note, package publish and execution dates.

Resolve official GitHub paths/releases rather than guessing. Registration metadata proves publication/constraints; publisher `.nupkg` assets/nuspec groups prove actual TFM evidence. Computed compatibility and selectable portable/older assets do not certify vendor runtime support. Test/analyzer/tool versions are not app runtime numbers.

Inaccessible necessary evidence is **UNVERIFIED**, with effect on execution stated. Offline drafts cannot authorize migration before necessary refresh and concrete plan approval. Preserve corrections as dated history. The [prompt correction](provenance/original-prompt.md#support-lifecycle-correction) is separate from its exact text.

## Evidence vocabulary

**Observed** means source inspection or reported execution in the stated revision/environment, not rerun here. **Researched** means documentary/package evidence, not runtime proof. **Project-decision** means WorkPlanReports owner policy/scope/risk, not portable default. **Unverified** means conditional, unknown, proposed or deferred checks lacking observed results. The ledger labels each finding; category assessments are researched unless linked to observed case evidence.
