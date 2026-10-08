# Original request provenance

## Captured original request

WPR-PROMPT-001, **project-decision**. Selected `.agents/scratchpad/prompts.md` section, embedded capture dated **2026-09-30**, not in the immutable application Git tree. Revision override is null. Digest covers only the selected text below with LF endings and one final newline, not wrapper/correction. Unrelated scratchpad content is omitted.

## .NET 10 Upgrade

/wayfinder We need to upgrade to .NET 10 because .NET 8 is out of LTS. We need to ensure we are aware of all breaking changes and official guidance for the
upgrade.
[Upgrade to a new .NET version](https://learn.microsoft.com/en-us/dotnet/core/install/upgrade)

1. Upgrade to .NET 9
   - [Upgrade .NET 8 to .NET 9](https://learn.microsoft.com/en-us/aspnet/core/migration/80-to-90?view=aspnetcore-10.0&tabs=visual-studio-code)
   - [Breaking changes in .NET 9](https://learn.microsoft.com/en-us/dotnet/core/compatibility/9.0)
2. Upgrade to .NET 10
   - [Migrate from ASP.NET Core 9 to 10](https://learn.microsoft.com/en-us/aspnet/core/migration/90-to-100?view=aspnetcore-10.0&tabs=visual-studio-code)
   - [Breaking changes in .NET 10](https://learn.microsoft.com/en-us/dotnet/core/compatibility/10)

Make sure that you thoroughly research these references so that we don't miss any important upgrade guidance.

## Support lifecycle correction

WPR-PROMPT-002, **researched**. ".NET 8 is out of LTS" was incorrect at capture time. Maintenance remains support. Microsoft's [policy](https://dotnet.microsoft.com/en-us/platform/support/policy/dotnet-core), retrieved by the extraction plan **2026-09-30**, recorded .NET 8/9 support through **2026-11-10**, .NET 10 through **2028-11-14**. Not independently refreshed here; recheck before future use.

This annotation does not alter the original selected text/digest. See [source map](source-map.json), [authorities](../official-sources.md) and [route](../routes/net8-to-net10/index.md).
