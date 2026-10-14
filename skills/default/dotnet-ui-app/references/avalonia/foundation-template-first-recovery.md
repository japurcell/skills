---
title: Avalonia Template-First Recovery
priority: CRITICAL
tags: avalonia, recovery, xaml, axaml, startup, resources, templates
sources:
  - https://docs.avaloniaui.net/docs/get-started/
  - https://docs.avaloniaui.net/docs/get-started/create-your-first-project
---

## Use For

Opaque Avalonia XAML, resource, startup, binding, or launch failures best isolated against a fresh official template.

## Prefer

- Scaffold a temporary comparison app from the same template.
- Keep startup close to the template until build and launch succeed.
- Reintroduce resources, styles, services, and navigation incrementally.
- Check debug output for binding/resource errors.

## Avoid

- Copying WinUI or WPF startup files into Avalonia.
- Replacing the project file before understanding the failure.
- Flattening all styles into window-local markup as a permanent fix.
- Assuming all WPF/WinUI XAML constructs work unchanged.

## Recovery Loop

1. Identify template family: simple app, MVVM app, cross-platform app.
2. Scaffold comparison: `dotnet new avalonia.mvvm -o RecoveryReference`
3. Diff `.csproj`, `Program.cs`, `App.axaml`, `MainWindow.axaml`, `Views/`, `ViewModels/`, `Styles/`, assets, and resource includes.
4. Revert suspicious startup/resource changes toward the template.
5. Run `dotnet build` and `dotnet run`.
6. Reapply custom changes in small slices.

## Checks

- `x:Class` matches code-behind.
- Namespaces match.
- `App.axaml` includes intended theme.
- Resource paths are valid.
- Assets are included.
- Compiled binding data types are correct.
- Platform services are not invoked too early.

## Exit Criteria

- App rooted in official template.
- Build succeeds.
- App launches.
- Expected UI appears.
