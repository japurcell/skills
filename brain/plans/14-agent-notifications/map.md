# Agent notifications

## Destination

Produce an agreed product spec, researched technical choices, and user-reviewed prototypes for a fast, visually pleasing desktop notification app on Windows, Linux, and macOS. Production implementation follows this effort.

## Notes

- Origin: todo 14. Destination and initial preferences confirmed on 2026-10-21.
- Use wayfinder, grilling, research, and prototype skills as applicable. User explicitly waived missing domain-modeling skill.
- Hooks invoke a shared CLI for success, failure, input, approval, cancellation, and unexpected stalls. The app does not monitor agents or detect stalls.
- Target Codex desktop and CLI, Copilot CLI and VS Code, and Gemini CLI, subject to supported integration mechanisms.
- Deliver visual/audio alerts only on the agent's computer, identifying agent and repository.
- All alert types stay in a popup stack until explicitly dismissed, including successes. No automatic dismissal. Snooze moves an alert to the back without hiding it or starting a timer, allowing cycling.
- Dismiss deletes an alert; Dismiss all deletes the current stack. Both offer brief Undo. Pending alerts remain saved indefinitely until dismissed. No dismissed-alert retention or separate history window.
- Prototype Undo is 10 seconds, in memory only, for the most recent dismissal action. Another dismissal replaces it; reload ends it. Exact duration is a prototype default.
- Accepted sound policy: once per new alert; no automatic replay, including Snooze/cycling/reopen/dismissal; explicit Replay sound action. Bursts use one gentle chime, choosing failure sound if any failure is present.
- Accepted quiet-hours policy: optional and initially off, local-time schedule, audio silenced while visual stacking continues, no catch-up sounds. Offer mute for 30 minutes, 1 hour, and until tomorrow; manual sound previews remain available.
- User accepted alerts while the agent window is focused, quiet hours, mute controls, and independent visual/audio settings.
- Sounds are customizable by type, including distinct success/failure sounds. All sounds must be gentle and pleasant, never abrupt or loud.
- Prior PowerShell popups, notify-send, and VS Code terminal settings failed user expectations: sound did not work, appearance did not attract attention, and none satisfied all platforms. Root causes are unverified.
- User selected hybrid startup: first CLI invocation starts one resident app; later invocations reuse it; login startup is optional. Explicit Quit preserves the stack and queues new alerts until manual reopening, when the stack returns.
- Keep all planning documents under `brain/plans/14-agent-notifications/`, per user direction. Disposable prototype code stays outside the vault.
- User accepted the deletion/Undo browser revision and authorized native desktop experiments. Linux targets are Ubuntu desktop and WSL2; user has no admin access. Keep dependencies user-local and stop on unavailable system prerequisites.
- Research and disposable prototypes are authorized. No installations, real hook changes, or production implementation.
- Coordinator owns map/handoff. Research workers own their tickets/findings. Research can close in parallel; otherwise resolve at most one ticket per session.

## Decisions so far

- [Startup and platform delivery](tickets/startup-and-platform-delivery.md): sourced comparison complete; user selected lazy single-resident startup with optional login startup for prototyping.
- [Integration event coverage](tickets/integration-event-coverage.md): command hooks cover differing subsets; generic turn end cannot prove success, and no provider offers a stall event.
- [Hybrid startup prototype](tickets/hybrid-startup-prototype.md): user accepted the browser flow for persistent stacked alerts, Snooze cycling, individual/bulk dismissal, and Quit queuing; native feasibility remains unproven.
- [Native toolkit feasibility](tickets/native-toolkit-feasibility.md): use Qt/PySide 6.12 for this bounded native-window/audio experiment; this is not production framework approval.

## Not yet specified

<!-- FOG START -->
- Visual identity and detailed interaction beyond the accepted pending-alert stack and deletion/Undo flow.
- Sound selection, previews, customization, and accessibility experience.
- Production architecture after native Windows/Ubuntu/WSL2 proof; macOS window/audio were user-confirmed, but compositor, accessibility, and cross-platform behavior remain open.
- Packaging, updates, and integration installation after architecture is understood.
<!-- FOG END -->

## Out of scope

- Production implementation during this map.
- Remote delivery, agent monitoring, and app-generated stall detection in version one.
- Claude integration in version one.
