# .NET 9 containers and deployment

**Researched**, date unspecified; WPR-N9-CONT-001 through 004. Two container/two deployment entries, historical Alpine source. [Index](index.md).

## Runtime setting precedence

**Possibly applies.** Environment variables override corresponding runtimeconfig/project runtime settings in .NET 9. Original Alpine set invariant=false and installed ICU without a conflicting project property. Inspect emitted runtimeconfig and all injected settings together and verify actual culture behavior. Deployment values were unknown.

Source: [environment precedence](https://learn.microsoft.com/en-us/dotnet/core/compatibility/deployment/9.0/envvar-precedence).

## Zlib image removal

**Originally not applicable.** Images no longer install system zlib; runtime statically links zlib-ng. Managed workbook/compression APIs alone do not require the OS shared library. No direct/native zlib dependency found. Install only for a verified native/transitive requirement, then test.

Source: [no zlib](https://learn.microsoft.com/en-us/dotnet/core/compatibility/containers/9.0/no-zlib).

## Monitor image tags

**Originally not applicable.** Monitor tags simplify to version-only. Source had Node/SDK/ASP.NET/SQL images, not dotnet/monitor. Reassess deployed monitoring sidecars too.

Source: [Monitor images](https://learn.microsoft.com/en-us/dotnet/core/compatibility/containers/9.0/monitor-images).

## MonoVM and image verification

**Originally not applicable.** Desktop Windows/macOS/Linux MonoVM runtime packs deprecated. Ordinary ASP.NET Alpine publish had no undocumented Mono switch/pack or AOT configuration.

Source: [MonoVM packages](https://learn.microsoft.com/en-us/dotnet/core/compatibility/deployment/9.0/monovm-packages).

For applicable targets, build/publish/run the actual image, inspect environment/runtimeconfig and exercise auth/report/database/Excel/culture contracts. These are proposed checks, not source research results. [Image lessons](../../../lessons.md) distinguish ICU from timezone files and SDK pins from Docker image selection.
