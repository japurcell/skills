# Persistent alert stack prototype

- Current contract and latest evidence: [deletion and Undo](phase-3-deletion-and-undo.md).
- All types persist in a pending-alert stack until dismissed. Snooze moves the front alert to the back without hiding it or starting a timer.
- Individual dismissal deletes one alert; Dismiss all deletes the current stack. Both offer brief Undo. No dismissed-alert retention or separate history window.
- Quit preserves the stack and queues later arrivals until manual reopening. Pending alerts survive restart.
- User accepted the stack interaction, then explicitly replaced retained history with deletion and Undo.
- [Historical browser verification before deletion semantics](phase-2-alert-stack-before-deletion.md) retains earlier test counts and screenshots. Its retained-history behavior is superseded.
- Browser behavior does not prove native process, audio, window placement, concurrency, accessibility, or cross-platform parity.
