# Persistent alert stack prototype

- Historical evidence only: this snapshot predates deletion and Undo. Its history-retention descriptions are superseded by [the current contract](phase-3-deletion-and-undo.md), not active requirements.
- Status: user accepted the revised browser interaction with “This looks good.” Native feasibility remains open.
- User direction: keep every popup, including success, until dismissed. Snooze keeps an alert in the stack but moves it to the back, allowing cycling. No timed hiding or automatic dismissal.
- User also confirmed: explicit Quit preserves the stack and queues new alerts until manual reopening.
- [Interactive prototype](../../../../../../visualizations/2026/10/22/01a16214-d358-76a3-b29a-244a36c7786e/hybrid-startup-prototype.html)
- [Stack preview](../../../../../../visualizations/2026/10/22/01a16214-d358-76a3-b29a-244a36c7786e/alert-stack-preview.png)
- Prototype remains a browser simulation; native startup, audio, and desktop placement are untested. Run instructions remain in [startup prototype](phase-1-startup-prototype.md).

## Current behavior

- One front card with Snooze and Dismiss; two peeking cards indicate the next alerts. Count includes the entire pending stack.
- Snooze rotates the front alert to the back without changing history order or marking it reviewed.
- Dismiss removes only that alert from the stack and retains its history entry.
- Dismiss all clears every pending alert in the current stack together, preserving history and review state. The control is disabled when the app is closed or the stack is empty.
- New arrivals join the back, keeping the current card in place. This is a prototype default for review, not a separately accepted ordering policy.
- Quit hides but preserves the whole stack. New events queue without restarting the app; Open app restores every pending alert in order.
- Crash recovery and simulated login also preserve pending alerts. Demo reload preserves stack order and explicit-Quit pause state.
- Existing demo records from the expiry trial are restored to the stack unless explicitly dismissed. No saved alerts are deleted during migration.
- History shows each pending alert's position and keeps dismissed alerts. Mark all reviewed does not clear the stack.

## Verification

- Four-event burst: four pending alerts and four history entries, with success at the front.
- Four Snooze clicks cycled through success, approval, failure, unknown outcome, and back to success. All four records remained; focus followed the Snooze control.
- Quit plus another event: zero instances, five queued alerts. Reload preserved all five and explicit-Quit state. Open restored the stack.
- Dismiss success: four pending alerts and five history entries. Mark all reviewed left all four pending alerts in place.
- Revised guided walkthrough completed. No browser console warnings/errors were observed. Inline JavaScript passed `node --check`; plan links resolved and `git diff --check` passed.
- Bulk dismissal check: added four pending alerts to ten existing dismissed history records. Dismiss all cleared all four, leaving all fourteen history entries unreviewed. Empty-stack control disabled; keyboard focus moved to Open app.
- Reload retained the cleared state. A new event then created a new stack and could be dismissed independently. No browser console warnings/errors; JavaScript syntax and diff whitespace checks passed. [Bulk dismissal preview](../../../../../../visualizations/2026/10/22/01a16214-d358-76a3-b29a-244a36c7786e/dismiss-all-preview.png).
- Native processes, sounds, login registration, narrow viewport, and screen readers remain unverified. No automated tests were added to this throwaway prototype.
- Reflection: user preferences and prototype findings are task-specific and captured here; no separate brain topic is needed.
