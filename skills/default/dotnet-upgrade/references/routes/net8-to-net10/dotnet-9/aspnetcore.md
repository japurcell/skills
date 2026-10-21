# ASP.NET Core 9

**Researched**, date unspecified; WPR-N9-ASP-001 through 007. Original two web hosts plus tests, Angular frontend and shared net8 target. All negative assessments describe that source only. [Index](index.md); [migration guide](https://learn.microsoft.com/en-us/aspnet/core/migration/80-to-90?view=aspnetcore-10.0&tabs=visual-studio-code).

## Migration guide actions

Update SDK pin, shared TFM and applicable ASP.NET/EF/Extensions packages across every consuming project including tests. Root `latestMinor` does not select a new major. `MapStaticAssets` is optional optimization for build-known assets, not a mechanical replacement for the custom `PhysicalFileProvider` at `wwwroot/dist/browser`. Preserve default documents, SPA paths, caching and actual publish discovery; other locations still need `UseStaticFiles`. Blazor authentication-state serialization/StreamRendering instructions did not apply to Angular.

Sources: [upgrade guide](https://learn.microsoft.com/en-us/dotnet/core/install/upgrade), [static-asset optimization](https://learn.microsoft.com/en-us/aspnet/core/release-notes/aspnetcore-9.0?view=aspnetcore-9.0#static-asset-delivery-optimization), [static files](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/static-files?view=aspnetcore-9.0).

## Forwarded header trust

**Applies.** Unknown proxies' forwarded headers are ignored, including servicing releases 8.0.17/9.0.6, not just a major upgrade. Scheme/host/TLS/OIDC redirects may change. Original source enabled For/Host/Proto while clearing KnownNetworks/KnownProxies, allowing arbitrary proxies and spoofing. Research recommended actual trusted ingress ranges and real ingress/spoof tests. The later owner retained risk, not a portable recommendation. No production topology was tested.

Source: [unknown proxies](https://learn.microsoft.com/en-us/aspnet/core/breaking-changes/8/forwarded-headers-unknown-proxies?view=aspnetcore-9.0).

## Development DI validation

**Possibly applies.** HostBuilder defaults ValidateOnBuild/ValidateScopes in Development unless options explicitly configured. Main host explicitly validated build; AuthServer used defaults. Start both Development hosts and fix invalid/captive dependencies, never suppress validation to pass.

Source: [HostBuilder validation](https://learn.microsoft.com/en-us/aspnet/core/breaking-changes/9/hostbuilder-validation?view=aspnetcore-9.0).

## Data protection key resolution

**Originally not applicable.** `DefaultKeyResolution.ShouldGenerateNewKey` changes meaning for direct/custom resolver consumers. Framework cookies alone do not establish affected API use; no IDefaultKeyResolver/direct call found.

Source: [key resolution](https://learn.microsoft.com/en-us/aspnet/core/breaking-changes/9/key-resolution?view=aspnetcore-9.0).

## Development certificate export

**Originally not applicable.** `dotnet dev-certs` export no longer creates a missing target folder. No export automation found; OpenIddict development signing/encryption helpers are different APIs. Create the directory if the actual target exports.

Source: [certificate export](https://learn.microsoft.com/en-us/aspnet/core/breaking-changes/9/certificate-export?view=aspnetcore-9.0).

## Blazor legacy runtime globals

**Originally not applicable.** `window.MONO`, `window.BINDING`, `window.Module` no longer exported globally for Blazor WASM. Angular/server source had no such client APIs; reassess other WASM targets.

Source: [legacy APIs](https://learn.microsoft.com/en-us/aspnet/core/breaking-changes/9/legacy-apis?view=aspnetcore-9.0).

## Middleware constructor selection

**Originally not applicable.** Multiple satisfiable constructors can fail under a provider without IServiceProviderIsService. Standard DI and single-constructor custom middleware did not match. Reassess alternate containers and constructor shapes.

Source: [middleware constructors](https://learn.microsoft.com/en-us/aspnet/core/breaking-changes/9/middleware-constructors?view=aspnetcore-9.0). Complete [six-entry index](https://learn.microsoft.com/en-us/aspnet/core/breaking-changes/9/overview?view=aspnetcore-9.0). Listed verification is not observed execution; see [case evidence](../../../case-studies/workplan-reports.md).
