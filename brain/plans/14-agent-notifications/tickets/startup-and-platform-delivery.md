# Startup and platform delivery

**Type:** research
**Status:** closed
**Blocked By:** none
**Research Dir:** ../research/startup-and-platform-delivery

## Question

Which startup model supports reliable, fast visual/audio alerts and durable history across Windows, Linux, and macOS?

Compare resident tray/menu bar with optional login startup, starting on every CLI invocation, and one resident instance started on first invocation. Cover cold start, idle resources, concurrency, panels/history, recovery, login sessions, audio, focus restrictions, accessibility, Linux desktop/Wayland variation, and explicit quit. Separate sourced facts from design inferences. Do not diagnose past failures without evidence. Provide primary-source citations, a concise pros/cons table, recommendation, limitations, and prototype checks. Framework selection remains later.

---

## Resolution

Current scope correction: the original question used retained history. User subsequently replaced that with durable pending alerts and deletion plus brief Undo; no separate history window. See [current contract](../phase-3-deletion-and-undo.md). The startup feasibility findings still apply to the pending store.
Recommend prototyping a lazy single resident process, with optional login autostart to remove first-event cold start. It best supports persistent custom panels, serialized concurrent hook events, and durable history while avoiding an always-running process for users who opt out. Keep event history durable outside the UI process and define explicit Quit behavior. The user selected this hybrid for prototyping on 2026-10-21. Native behavior remains unproven.

Windows and macOS provide native topmost/floating window mechanisms, but neither permits reliably taking foreground focus from the user's current work. Standard Wayland toplevels do not provide arbitrary pinned placement; `wlr-layer-shell` can provide it on supporting compositors, so Linux panel parity requires a standard-notification or normal-window fallback. Audio playback is technically feasible on all three systems, with differing device and notification controls. Tray and menu-bar icons must remain optional access paths.

See [startup and platform delivery findings](../research/startup-and-platform-delivery/findings.md) for the comparison, sourced platform facts, design inferences, limitations, and prototype checks.
