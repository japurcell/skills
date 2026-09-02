---
title: Avalonia Build, Run, and Launch Verification
priority: CRITICAL
tags: avalonia, build, run, launch, verification, dotnet, desktop
sources:
  - https://docs.avaloniaui.net/docs/get-started/
  - https://docs.avaloniaui.net/docs/deployment/
---

## Use For

Building, running, startup debugging, and verifying an Avalonia app actually opened.

## Workflow

1. Identify solution/project, target framework, configuration, runtime identifier if relevant, and target platform.
2. Build after meaningful edits.
3. Run when feasible.
4. Verify objective launch: visible window, expected title/content, responsive app, no immediate crash.
5. Debug ambiguous launch before saying ready.

## Commands

- `dotnet restore`
- `dotnet build`
- `dotnet run --project ./MyApp.csproj`
- `dotnet build ./MyApp.sln`
- `dotnet build -c Release`

## Startup Checks

- `Program.cs`
- `App.axaml`
- `App.axaml.cs`
- `MainWindow.axaml`
- `MainWindow.axaml.cs`
- lifetime configuration
- theme/style includes
- resource dictionaries
- assets
- view locator/data templates
- DI startup code
- platform-specific services

## Common Failures

- Missing templates or restore failure.
- `x:Class` or namespace mismatch.
- Resource URI/path problems.
- Style selector errors.
- Missing theme include.
- Binding errors in debug output.
- Platform-specific API used unguarded.
- Missing native dependency.

## Exit Criteria

- Build succeeds.
- App launches.
- Expected top-level UI appears.
- No unresolved startup exception remains.
