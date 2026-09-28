# High-Rate Hook Performance Review

**Type:** grilling
**Status:** closed
**Blocked By:** provider-lifecycle-facts.md, repository-state-retirement.md, markdown-health-retirement.md, repository-okf-hook.md
**Research Dir:** none

## Question

Which retained hook registrations can run once per tool call or more often in each provider, including events beyond pre- and post-tool use? Decide the review's measurement method, representative workloads, baseline and comparison evidence, acceptable latency and noise, review findings format, and when a finding requires an implementation fix. Account for process startup, synchronous work, timeouts, and any notification overhead without inventing a performance target before measuring.

---

## Resolution

The user confirmed this performance-review design on 2026-09-28:

- After the RTK, Markdown Health, repository-state, and OKF changes, enumerate every **retained registration** that can run once per tool call or more often. Include security checks, automatic RTK forwarders, observability and no-op paths, and Gemini model-stream events such as `AfterModel`. Record provider, configuration scope, event, matcher, handler, and expected call rate. Do not assume pre- and post-tool hooks are the only high-rate events.
- Run the registered hook entrypoint scripts **directly on macOS** with representative provider JSON and environment. Live Copilot, Gemini, or Codex CLI runs are **not required for this performance audit**. Other tickets' functional CLI and Windows acceptance checks remain separate.
- Exercise clean/no-op, security finding or warning, handler failure, repeated calls, large input, and contention or concurrency paths where applicable. Measure full subprocess wall time from launch through exit, including startup, input/output, synchronous work, and message construction. Isolate handler time where practical. Run repeated cold and warm samples and report median, p95, and run-to-run variation. A minimal process control estimates startup cost; compare against the current handler version for retained paths where possible. There is no provider-level elapsed-time or disposable no-hook CLI baseline requirement.
- Do not invent a numeric latency budget before measuring. Use baseline and variation data to set a defensible budget, identify reproducible excess cost, and assess headroom against each configured timeout. Review code for avoidable process launches, redundant parsing or scans, synchronous disk and log writes, lock contention, unbounded work, and notification construction in high-rate paths.
- Report each registration's call rate, workload, wall-time distribution, startup/handler attribution when available, timeout risk, cause, proposed change, and matching before/after evidence. Clearly mark costs that cannot be isolated. Require an implementation fix for redundant high-rate work, blocking or unbounded I/O, timeout hazards, and reproducible user-visible latency beyond measured noise. Keep security decisions and failure behavior intact. Document smaller measured trade-offs without forcing a speculative optimization.

This is a planning decision. No benchmark or hook implementation was run while closing this ticket. The read-only inventory found retained per-tool security, RTK forwarding, and telemetry paths; Gemini `AfterModel` telemetry can run per response chunk. The implementation review must verify the final registration inventory after retirements, not reuse the old configuration list as if it were final.
