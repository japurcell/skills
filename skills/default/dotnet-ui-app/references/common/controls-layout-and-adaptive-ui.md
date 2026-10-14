---
title: Controls, Layout, and Adaptive UI
priority: HIGH
tags: controls, layout, adaptive-ui, responsive, forms, lists
---

## Use For

Control selection, page composition, responsive layout, scroll ownership, command placement, and adaptive behavior across UI frameworks.

## Prefer

- Built-in framework controls first.
- Native command, menu, toolbar, or shell surfaces before ad hoc command rows.
- Standard controls for forms, lists, grids, dialogs, menus, tabs, navigation, and status.
- Explicit scroll ownership.
- Responsive techniques: reposition, resize, reflow, show/hide.
- A narrow-width plan when the app can be resized.

## Avoid

- Custom controls only to change appearance.
- Hard-coded sizes that only work at one width.
- Dense desktop-only layouts.
- Nested scroll regions without a clear owner.
- Extra borders/cards when spacing, headings, or child surfaces already group content.

## Review

- Simplest built-in control chosen?
- Page usable when narrow?
- Keyboard, mouse, and touch can reach core actions?
- Spacing and hierarchy consistent?
- Scroll ownership clear?
