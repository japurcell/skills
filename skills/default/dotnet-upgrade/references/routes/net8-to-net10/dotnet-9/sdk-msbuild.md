# .NET 9 SDK and MSBuild

**Researched**, date unspecified; WPR-N9-SDK-001 through 003. All ten entries; applicability is historical source only. [Index](index.md).

## SDK requirements and terminal logger

**Applies:** an SDK 8 pin cannot automatically select SDK 9. Update actual toolchains, targets and images; VS/MSBuild 17.12+ is required for net9. **Possibly applies:** Terminal Logger defaults on capable interactive terminals. The README watch workflow differed from scripted/redirected minimal output. Verify actual output consumers, not assumed parser compatibility.

Sources: [version requirements](https://learn.microsoft.com/en-us/dotnet/core/compatibility/sdk/9.0/version-requirements), [Terminal Logger](https://learn.microsoft.com/en-us/dotnet/core/compatibility/sdk/9.0/terminal-logger).

## Solution watch workload and productcommits

Original not-applicable cases: sln add rejects invalid names (no such automation); watch Hot Reload incompatible for net5 or earlier (net8/9 no workaround); workload machine-readable output changes (no workloads/parser); installer version removed from productcommits (no reader).

Sources: [sln add](https://learn.microsoft.com/en-us/dotnet/core/compatibility/sdk/9.0/dotnet-sln), [watch](https://learn.microsoft.com/en-us/dotnet/core/compatibility/sdk/9.0/dotnet-watch), [workloads](https://learn.microsoft.com/en-us/dotnet/core/compatibility/sdk/9.0/dotnet-workload-output), [productcommits](https://learn.microsoft.com/en-us/dotnet/core/compatibility/sdk/9.0/productcommits-versions).

## Custom cultures RIDs and legacy target warnings

Custom-culture resource handling is disabled by default at SDK 9.0.300/MSBuild 17.14 despite the article being under version 10. No resx/EnableCustomCulture was found; SQL embedded resources are not cultures. Other original absent cases: default .NET Framework RID, netstandard1.x warning and net7 warning, since all projects targeted net8/9.

Sources: [custom cultures](https://learn.microsoft.com/en-us/dotnet/core/compatibility/sdk/10.0/msbuild-custom-culture), [Framework RID](https://learn.microsoft.com/en-us/dotnet/core/compatibility/sdk/9.0/default-rid), [Standard warning](https://learn.microsoft.com/en-us/dotnet/core/compatibility/sdk/9.0/netstandard-warning), [net7 warning](https://learn.microsoft.com/en-us/dotnet/core/compatibility/sdk/9.0/net70-warning).

Verify actual SDK selection, solution build/test, interactive watch, normal publish/image and supported VS/MSBuild. No speculative workload/legacy/custom-culture opt-in follows from this research.
