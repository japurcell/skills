---
title: Testing, Debugging, and Review Checklists
priority: HIGH
tags: testing, debugging, review, verification, accessibility, performance
---

## Verification Loop

- Build after each meaningful edit.
- Run after startup, shell, navigation, resource, or packaging changes.
- Verify actual launch, not just process start.
- Debug startup failures before continuing feature work.
- Test the workflow the user will actually use.

## Design Review

- Navigation simple and predictable.
- Layout usable when narrow.
- Light, dark, contrast, hierarchy, and states hold up.
- Commands placed clearly.
- Built-in controls do most of the work.
- Scroll ownership explicit.

## Code Review

- Structure proportionate to app size.
- Resources and styles centralized where appropriate.
- Dependencies justified.
- Platform assumptions explicit.
- Intended build/run workflow works.

## Accessibility Review

- Keyboard-only flow works.
- Focus visible.
- Accessible names present.
- High contrast and text scaling do not break UI.

## Exit Criteria

- Build succeeds.
- App launches and shows expected UI.
- Primary flows are usable, accessible, and responsive.
