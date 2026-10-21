---
title: Avalonia Styling, Resources, and Theme Variants
priority: HIGH
tags: avalonia, styling, resources, themes, fluenttheme, simpletheme, selectors, light, dark
sources:
  - https://docs.avaloniaui.net/docs/guides/styles-and-resources
  - https://docs.avaloniaui.net/docs/basics/user-interface/styling
  - https://docs.avaloniaui.net/docs/how-to/theme-switching-how-to
---

## Use For

Avalonia styles, selectors, resources, theme variants, FluentTheme/SimpleTheme, and dark/light support.

## Prefer

- Avalonia theme resources and styles over hard-coded colors.
- Light and dark support by default.
- Semantic resource names.
- Shared style files for reusable rules.
- Local styles only when view-specific.
- Framework theme variants where possible.

## Avoid

- Copying WinUI resource keys.
- Hard-coded colors that fail in dark mode.
- Recreating a design system unnecessarily.
- Excessive selector complexity.
- Styling every control from scratch.
- Redundant borders/cards.

## Guidance

- Start with the template-selected Avalonia theme.
- Keep app-level theme configuration in `App.axaml`.
- Define reusable brushes, spacing, and typography centrally.
- Use selectors intentionally and keep them scoped.
- Use classes for reusable variants.
- Use control templates only when normal styles are insufficient.
- Preserve hover, pressed, selected, disabled, and focused states.

## Review

- Light/dark supported?
- Resources semantic?
- Selectors understandable?
- Custom templates justified?
- Interaction states preserved?
