---
title: Accessibility, Input, and Localization
priority: HIGH
tags: accessibility, keyboard, screen-reader, automation, localization, high-contrast, input
---

## Use For

Keyboard accessibility, screen reader support, automation semantics, input parity, high contrast, text scaling, and localization-ready UI.

## Prefer

- Accessible names, labels, and help text.
- Keyboard reachability for the main workflow.
- Visible focus and logical tab order.
- High-contrast-safe visuals.
- Localizable strings and layouts that tolerate text growth.
- Standard controls with built-in accessibility behavior.

## Avoid

- Icon-only buttons without accessible names.
- Focus traps or hidden tab stops.
- Hard-coded UI strings.
- Color-only state communication.
- Custom controls without accessibility semantics.

## Review

- Can a keyboard-only user complete the task?
- Does a screen reader have enough information?
- Does high contrast remain legible?
- Are text growth and RTL considered where relevant?
