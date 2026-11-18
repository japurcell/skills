# .NET 10 SDK and MSBuild

**Researched**, **2026-09-23**; WPR-N10-SDK-001 through 006. All 27 entries. Historical source applicability, not current graph or external configuration proof. [Index](index.md).

## CLI and watch output streams

watch internal logs move stderr; documented developer command affected, no local parser. Other non-command CLI output moves stderr, verification scripts already redirected/did not parse stdout. Verify real IDE/terminal/external consumers before redirection.

Sources: [watch](https://learn.microsoft.com/en-us/dotnet/core/compatibility/sdk/10.0/dotnet-watch-stderr), [CLI output](https://learn.microsoft.com/en-us/dotnet/core/compatibility/sdk/10.0/dotnet-cli-stderr-output).

## Pruning and package consumers

**Possibly applies.** Framework-provided direct references can produce NU1510 and PrivateAssets=all/IncludeAssets=none, changing generated dependencies. Inspect actual net10/framework graph before removal/suppression. If packed, compare nuspec and consumer restore/build; no source pack workflow.

Sources: [NU1510](https://learn.microsoft.com/en-us/dotnet/core/compatibility/sdk/10.0/nu1510-pruned-references), [private references](https://learn.microsoft.com/en-us/dotnet/core/compatibility/sdk/10.0/prune-packagereference-privateassets).

## Interactivity tools feeds and retries

**Possibly applies.** User-driven commands default to interactive=true; CI/redirected commands are noninteractive. Local tool install creates a manifest if missing; update existing project-scoped manifests, not an unqualified root install. HTTP auditSources fail with NU1302 at SDK 10.0.400+. NUGET_ENABLE_ENHANCED_HTTP_RETRY=false no longer disables exponential retry. Actual global, private and CI NuGet configuration and injected variables were unknown; require HTTPS and explicit unattended behavior.

Sources: [interactivity](https://learn.microsoft.com/en-us/dotnet/core/compatibility/sdk/10.0/dotnet-cli-interactive), [manifest](https://learn.microsoft.com/en-us/dotnet/core/compatibility/sdk/10.0/dotnet-tool-install-local-manifest), [audit HTTP](https://learn.microsoft.com/en-us/dotnet/core/compatibility/sdk/10.0/nuget-audit-source-http-disallowed), [retry](https://learn.microsoft.com/en-us/dotnet/core/compatibility/sdk/10.0/nuget-enhanced-http-retry-removed).

## Tools workloads evaluation native coverage and dnx

Original not-applicable cases:

- RID-specific tool pack, no PackAsTool. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/sdk/10.0/dotnet-tool-pack-publish).
- Workload sets default, no workloads. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/sdk/10.0/default-workload-config).
- TFM DefineConstants unavailable during MSBuild evaluation, no consuming conditions. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/sdk/10.0/defineconstants-not-available-at-evaluation).
- Dynamic native coverage default false, Coverlet MSBuild not native Code Coverage collector. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/sdk/10.0/code-coverage-dynamic-native-instrumentation).
- dnx scripts bypass global.json at SDK 10.0.302+/.NET 11 Preview 6; no dnx was found. Normal dotnet is unaffected. A catalog article labeled 11 is not blanket SDK 10 behavior. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/sdk/11/dnx-scripts-bypass-global-json).
- dnx.ps1 removed, no Windows script usage. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/sdk/10.0/dnx-ps1-removed).
- Double quotes in `#:` file directives disallowed, no file-based apps. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/sdk/10.0/file-level-directive-double-quotes).

## Solution package inventory audit and signing

- new sln defaults slnx; existing sln, request sln explicitly if recreating. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/sdk/10.0/dotnet-new-sln-slnx-default).
- package list restores; no original workflow, use no-restore for intended offline inventory. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/sdk/10.0/dotnet-package-list-restore).
- Restore audits transitives by default; original explicit NuGetAuditMode=all already did so, continue review. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/sdk/10.0/nugetaudit-transitive-packages).
- project.json restore unsupported; no file. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/sdk/10.0/dotnet-restore-project-json-unsupported).
- nuget sign SHA1 fingerprints error; no signing. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/sdk/10.0/dotnet-nuget-sign-sha1-deprecated).
- MSBUILDCUSTOMBUILDEVENTWARNING escape hatch removed; no custom event/variable. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/sdk/10.0/custom-build-event-warning).

## Resources dependency assets and package metadata

- Custom-culture resources opt-in; no resx/culture/EnableCustomCulture, SQL resources distinct. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/sdk/10.0/msbuild-custom-culture).
- Packages without runtime assets omitted deps.json; no DependencyContext/deps consumer. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/sdk/10.0/deps-json-trimmed-packages).
- Versionless PackageReference NU1015; initial all versions including floats, no CPM then. Later accepted central management is not a versionless defect. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/sdk/10.0/nu1015-packagereference-version).
- HTTP list/search warnings become errors; no commands/HTTP source configured locally. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/sdk/10.0/http-warnings-to-errors).
- NuGet IDs validated in URLs; normal static package IDs. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/sdk/10.0/nuget-packageid-validation).
- ToolCommandName not set for non-tool projects; no PackAsTool, local tools are consumers. [Source](https://learn.microsoft.com/en-us/dotnet/core/compatibility/sdk/10.0/toolcommandname-not-set).

Required target checks: actual SDK selection at root/subdirectories and in images, restore/build/test/analyzers/audit/pruning, watch, and publish/runtime assets. The original SDK 8/latestMinor cannot select SDK 10. Tool updates operate in each existing manifest. No blanket diagnostic suppression or package removal.
