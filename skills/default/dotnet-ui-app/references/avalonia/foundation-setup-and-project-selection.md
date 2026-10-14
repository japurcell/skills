---
title: Avalonia Setup and Project Selection
priority: CRITICAL
tags: avalonia, setup, templates, dotnet, cross-platform, mvvm
sources:
  - https://docs.avaloniaui.net/docs/get-started/
  - https://docs.avaloniaui.net/docs/get-started/install-avalonia
  - https://docs.avaloniaui.net/docs/get-started/create-your-first-project
  - https://docs.avaloniaui.net/docs/fundamentals/the-mvvm-pattern
---

## Use For

Starting from scratch with Avalonia, choosing a template, preparing a machine, or deciding whether Avalonia is the right framework.

## Prefer

- Avalonia for cross-platform desktop support across Windows, macOS, and Linux.
- Official Avalonia templates.
- CLI-first creation and verification unless IDE guidance is requested.
- Current supported .NET SDK.
- `avalonia.mvvm` for apps with meaningful state, commands, services, or navigation.
- `avalonia.app` for simple prototypes.

## Avoid

- Treating Avalonia as WinUI with different namespaces.
- Copying WinUI controls, resources, or Windows App SDK APIs.
- Assuming Windows-only APIs are acceptable in shared code.
- Adding third-party controls before checking built-in Avalonia controls.

## Baseline Checks

- `dotnet --info`
- `dotnet new list avalonia`

If templates are missing and setup is approved:

- `dotnet new install Avalonia.Templates`
- `dotnet new list avalonia`

Common scaffold:

- `dotnet new avalonia.mvvm -o MyApp`
- `cd MyApp`
- `dotnet build`
- `dotnet run`

Use `dotnet new avalonia.mvvm --help` or `dotnet new avalonia.app --help` before adding template options.

## Cross-Platform Questions

- Which OSes must be supported?
- Desktop only, or browser/mobile/embedded too?
- Need tray icons, file associations, notifications, or custom window chrome?
- Need MSI/MSIX, DMG, PKG, AppImage, DEB, RPM, Snap, or Flatpak?
- Are native dependencies available on every target OS?

## Review

- Is Avalonia right for the targets?
- Are .NET SDK and templates verified?
- Was the app scaffolded from an official template?
- Does it build and launch?
