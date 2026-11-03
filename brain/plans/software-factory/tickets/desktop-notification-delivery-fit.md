# Desktop notification delivery fit

**Type:** research
**Status:** closed
**Blocked By:** operating-and-installation-model.md, human-control-and-publication.md
**Research Dir:** ../research/desktop-notification-delivery/

## Question

Which lightweight native desktop-notification mechanisms fit the accepted local foreground TypeScript runner on macOS, Linux, and Windows, without a permanent notifier service? Research primary documentation/source for installation requirements, app identity/permission requirements, bounded one-shot delivery, user-visible attribution, and opening an observation-only localhost detail URL after the sender exits. Distinguish basic alerts from reliable click behavior and proof of display/attention. Compare built-in platform facilities with a small bundled helper where justified; do not select a product mechanism or implement/test notifications. Identify the smallest remaining product tradeoff, preserving accepted best-effort delivery, a five-second default timeout, and dashboard-only opt-in reminders.

Record platform-specific uncertainty and what requires later native validation. No package installs, actual notifications, permission changes, or product code edits are authorized.

---

## Resolution

Claimed by subagent-desktop-notification-delivery and closed on 2026-10-15 after primary-source review. Both listed policy blockers were verified closed before research began. The [findings](../research/desktop-notification-delivery/findings.md) separate one-shot alert submission from display/attention evidence and from click-through after the sender exits. AppleScript has no URL callback; Linux body hyperlinks are optional by notification server; Windows can relaunch a registered AppNotificationManager helper through COM. A uniform post-exit click guarantee would require platform-specific app activation and installation work. The practical boundary is a best-effort alert with conditional click-through and a dashboard/CLI observation-link fallback; the five-second timeout bounds sending, not visible duration. Optional grouped reminders remain dashboard-host-only. No notifications, permissions, packages, native platforms, or product code were tested or changed.
