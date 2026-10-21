---
title: Avalonia Controls and Compiled Bindings
priority: HIGH
tags: avalonia, controls, layout, bindings, compiled-bindings, itemscontrol, datagrid
sources:
  - https://docs.avaloniaui.net/docs/basics/user-interface/controls
  - https://docs.avaloniaui.net/docs/data-binding
  - https://docs.avaloniaui.net/docs/data-binding/compiledbindings
---

## Use For

Avalonia controls, layouts, item templates, commands, data binding, and compiled bindings.

## Prefer

- Built-in Avalonia controls before third-party controls.
- Simple panels and layout containers.
- `ItemsControl`, `ListBox`, `TreeView`, `DataGrid`, or other collection controls by interaction need.
- Commands and bindings for stateful interactions.
- Compiled bindings where type information is clear and maintainable.
- Virtualization-friendly controls for large collections.

## Avoid

- Copying WinUI control assumptions directly.
- Custom controls only to change visuals.
- Deep visual trees.
- Nested scroll regions without explicit ownership.
- Dynamic binding patterns where compiled bindings would be clearer.
- Compiled bindings without correct data type declarations.

## Guidance

- Forms: use standard text input, selection, checkbox, radio, date/time, and validation patterns.
- Commands: use buttons, menus, context menus, toolbars, or command-like layouts.
- Collections: use templates and virtualization where appropriate.
- Navigation: compose intentionally; Avalonia does not require WinUI `NavigationView`.

## Review

- Simplest built-in control selected?
- Scroll ownership clear?
- Large collections virtualization-friendly?
- Bindings maintainable and diagnosable?
- Compiled bindings intentional?
