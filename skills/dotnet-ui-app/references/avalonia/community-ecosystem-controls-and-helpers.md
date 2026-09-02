---
title: Avalonia Community Ecosystem Controls and Helpers
priority: MEDIUM
tags: avalonia, community, controls, packages, ecosystem
sources:
  - https://github.com/AvaloniaUI/Avalonia
  - https://docs.avaloniaui.net/
---

## Use For

Deciding whether to add Avalonia community packages, third-party controls, helpers, MVVM libraries, or navigation frameworks.

## Prefer

- Built-in Avalonia controls first.
- Small targeted dependencies for real gaps.
- Packages compatible with the selected Avalonia version.
- Packages that support all target platforms.
- Documenting why the dependency was added.

## Avoid

- Adding a package before checking built-in controls.
- Pulling in a full suite for one minor visual element.
- Adding navigation/dialog/MVVM frameworks before needed.
- Relying on unmaintained packages for core workflows.

## Evaluate

- Does Avalonia already provide this?
- Compatible with selected Avalonia version?
- Supports every target OS?
- Actively maintained?
- Startup size or publish impact?
- License acceptable?
- Can it be replaced later?

## Good Candidate Areas

- Specialized data grids/tree grids.
- Docking layouts.
- Charts.
- Advanced text editing.
- Complex theming.
- Dialog/navigation helpers for larger apps.

## Review

- Dependency narrowly scoped?
- Built-in alternative considered?
- Matches app design language?
- Works on all targets?
- Maintenance and license risk acceptable?
