---
title: Performance, Diagnostics, and Responsiveness
priority: HIGH
tags: performance, responsiveness, ui-thread, diagnostics, virtualization, profiling
---

## Use For

Sluggish behavior, dropped frames, long startup, laggy scrolling, expensive layout, and responsiveness problems.

## Prefer

- Keeping the UI thread free.
- Simpler visual trees.
- Virtualization-friendly item controls.
- Measurement before optimization.
- Separating startup, layout, rendering, I/O, and data processing.

## Avoid

- Expensive I/O or CPU work on the UI thread.
- Deep visual trees without benefit.
- Heavy templates for large collections.
- Guessing without profiling or targeted observation.

## Review

- Heavy work off the UI thread?
- Large collections virtualized?
- Visual tree no more complex than needed?
- Release behavior checked when relevant?
