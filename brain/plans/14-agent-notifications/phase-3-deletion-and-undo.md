# Alert deletion and Undo

- Current user contract: Dismiss deletes an alert. Dismiss all deletes the current stack. Both offer brief Undo. No dismissed-alert retention or separate history window.
- Pending alerts remain saved until explicitly dismissed, including across Quit and restart. Snooze moves the current alert to the back without deletion or a timer.
- [Prototype](../../../../../../visualizations/2026/10/22/01a16214-d358-76a3-b29a-244a36c7786e/hybrid-startup-prototype.html)
- [Deletion and Undo preview](../../../../../../visualizations/2026/10/22/01a16214-d358-76a3-b29a-244a36c7786e/deletion-undo-preview.png)
- Prototype defaults: 10-second Undo, most recent dismissal only, in-memory recovery buffer. Another dismissal replaces Undo; reload closes it. These details make “brief” concrete and remain adjustable.
- Dismissed records leave persistent browser storage immediately. The temporary Undo buffer is excluded from saved state and discarded after expiry.
- Undo restores the removed alerts in their previous order ahead of later arrivals, without losing new alerts. It restores queued state if the app is quit.
- Loading older demo data purges previously dismissed records and obsolete review flags. There is no history migration into another retained archive.
- Store only agent, repository, timestamps, alert type, and short summary for pending alerts. Avoid raw prompts and tool output. No read/review state or dismissed-alert archive is required.

## Accepted sound and quiet-hours decisions

- Sound plays once per new alert; no automatic replay for unresolved alerts, Snooze, cycling, dismissal, or reopening. Provide explicit Replay sound.
- Coalesce a burst into one gentle chime, using the failure sound if a failure is present. Distinct success/failure choices remain customizable.
- Quiet hours: optional, initially off, local-time schedule; silence audio while visual alerts continue stacking; no catch-up sounds.
- Mute choices: 30 minutes, 1 hour, until tomorrow. Manual sound previews remain available.
- All sounds must remain gentle and pleasant. These sound/quiet controls are accepted requirements, not implemented or verified native behavior in this lifecycle prototype.

## Verification and limits

- Browser checks: bulk deletion reduced four alerts to zero; Undo restored all four with a later arrival retained as a fifth alert.
- Individual deletion reduced five alerts to four; Undo restored the deleted front alert in its previous position.
- Undo expired and disappeared after its window; reload showed zero pending alerts after bulk deletion. Reload immediately after deletion also showed zero alerts and no Undo.
- Two consecutive individual dismissals: Undo restored only the latest alert; the first stayed deleted. Undo after Quit restored four queued alerts without restarting the app; Open app displayed them.
- Screenshot reviewed: stack and Undo remain, with no separate history section. No browser console warnings/errors observed. JavaScript syntax, plan links, and diff whitespace checks passed.
- Browser model only. Native sound, OS windows/startup, concurrency, narrow viewports, and screen readers remain untested. No regression tests are added for removing the history feature.
- Reflection: current user preferences and task-specific findings are captured in this plan; no separate durable brain note is needed.
