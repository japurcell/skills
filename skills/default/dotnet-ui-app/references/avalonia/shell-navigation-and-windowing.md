---
title: Avalonia Shell, Navigation, and Windowing
priority: HIGH
tags: avalonia, shell, navigation, windowing, dialogs, multi-window, platform
sources:
  - https://docs.avaloniaui.net/docs/basics/user-interface
  - https://docs.avaloniaui.net/docs/concepts/services/windowing
---

## Use For

Desktop shell composition, navigation, windows, dialogs, custom chrome, tray behavior, and platform-specific window decisions.

## Prefer

- One simple main window first.
- Navigation that matches workflow, not copied WinUI shell controls.
- Separate views/view models for nontrivial navigation.
- Platform-aware window behavior.
- Built-in dialogs/windows before custom overlays.

## Avoid

- Assuming Avalonia has the same shell model as WinUI.
- Building a navigation framework before needed.
- Custom title bars that break platform expectations.
- Multi-window behavior without workflow justification.
- Scattered conditional platform code in views.

## Guidance

- Use a single-window content host for most desktop apps.
- Use side navigation for stable top-level sections.
- Use tabs for peer documents/views.
- Use modal dialogs sparingly.
- Use secondary windows for detached documents, inspectors, previews, or comparisons.
- Test sizing, placement, minimum size, and close behavior on each OS.
- Treat tray icons, notifications, file associations, and global hotkeys as platform-specific.

## Review

- Navigation simple and task-oriented?
- Main window structure clear?
- Dialogs/secondary windows justified?
- Window behavior works on target OSes?
- Platform-specific behavior isolated?
