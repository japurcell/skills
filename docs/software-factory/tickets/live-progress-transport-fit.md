# Live progress transport fit

**Type:** research
**Status:** closed
**Blocked By:** agent-execution-profiles.md
**Research Dir:** docs/software-factory/research/live-progress-transport-fit

## Question

Which browser transport best fits a local factory dashboard receiving committed event/output updates, with occasional human-control requests sent separately?

Compare Server-Sent Events/EventSource, fetch streaming, and WebSocket against current primary sources. Verify reconnect/cursor semantics, what replay and deduplication the application must own, relevant buffering/backpressure limitations, and browser connection constraints for multiple sessions/tabs. Distinguish normative protocol behavior from browser-specific limits. Do not claim any option guarantees persistence, exactly-once effects, one-second latency, or tested native OS packaging.

The factory has a per-repository SQLite executor, foreground workflow runners, human-triggered Continue, saved-before-display history, and an acceptance target of 95% of small received updates displayed within one second under documented local load. No permanent workflow service is selected. Limit the study to the browser transport seam; do not reopen engine, installation, UI layout, or authorization decisions.

Write concise findings with direct primary-source citations to the assigned directory. Append a resolution here that summarizes the findings and links the report, then close this research ticket. The parent design ticket owns the human's eventual transport choice.

---

## Resolution

Claimed by subagent-a7p3nq and closed on 2026-10-13 after primary-source review. The [findings](../research/live-progress-transport-fit/findings.md) recommend SSE/EventSource for one committed server-to-browser feed per dashboard, with human commands sent separately using Fetch. The human subsequently adopted SSE with separate HTTP controls in [Session events and live progress](session-events-and-live-progress.md#confirmed-answers-round-three); this research ticket owns the supporting facts, not that decision. The report covers EventSource reconnect cursors versus application-owned durable replay and deduplication, Fetch and WebSocket tradeoffs, buffering/backpressure, and browser connection constraints. The one-second display target requires measurement with the chosen browser and local serving path; no browser, latency, native packaging, or end-to-end test was performed.
