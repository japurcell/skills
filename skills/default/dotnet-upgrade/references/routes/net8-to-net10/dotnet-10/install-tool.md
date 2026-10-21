# .NET Install Tool

**Researched**, **2026-09-23**; WPR-N10-INSTALL-001. One entry for tool version 3.0.0, not SDK 10 runtime equivalence. [Index](index.md).

## Extension private runtime acquisition

**Possibly applies.** dotnet.acquire reuses matching VS Code extension-private runtime and checks latest after configured delay, default five minutes. C# Dev Kit recommendation is relevant to editor behavior, not project SDK/global.json. forceUpdate:true is extension-caller troubleshooting only, not substitute for SDK availability or authority to install.

Source: [acquisition](https://learn.microsoft.com/en-us/dotnet/core/compatibility/install-tool/3.0.0/vscode-dotnet-acquire-no-latest). No editor-private runtime exercised here.
