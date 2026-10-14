---
title: Avalonia App Structure
priority: HIGH
tags: avalonia, app-structure, axaml, resources, views, viewmodels, mvvm
sources:
  - https://docs.avaloniaui.net/docs/fundamentals/the-mvvm-pattern
  - https://docs.avaloniaui.net/docs/concepts
---

## Use For

Avalonia project layout, views, view models, resources, styles, services, and platform-specific code.

## Prefer

- Clear split between views, view models, models, services, styles, and assets.
- `App.axaml` for app-level theme/resource inclusion.
- `MainWindow.axaml` as desktop shell.
- MVVM for nontrivial state, commands, navigation, and testable logic.
- Small code-behind for view-specific behavior.
- Platform abstractions for OS-specific services.

## Avoid

- One large window containing shell, business logic, and resources.
- Code-behind as the main architecture for complex apps.
- MVVM ceremony in tiny prototypes.
- Assuming WPF/WinUI resource or binding behavior.
- OS-specific APIs in shared view models.

## Typical Shape

- `App.axaml`
- `App.axaml.cs`
- `Program.cs`
- `MainWindow.axaml`
- `MainWindow.axaml.cs`
- `Views/`
- `ViewModels/`
- `Models/`
- `Services/`
- `Styles/`
- `Assets/`
- `Platforms/Windows`, `Platforms/macOS`, `Platforms/Linux` when needed

## Review

- Startup recognizable from template?
- Views and view models separated where useful?
- Resources/styles scoped appropriately?
- Platform-specific services isolated?
- Structure proportionate to app size?
