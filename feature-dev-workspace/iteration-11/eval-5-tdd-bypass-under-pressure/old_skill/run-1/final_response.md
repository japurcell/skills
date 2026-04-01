# Feature Dev Response — Rate-Limiting Under Deadline Pressure

**Track selected: Light** — well-bounded change, two known files, implementation intent is clear.

---

## Understanding

You need rate-limiting logic added to your API handler. The change touches two files and the scope is clear. Given the deadline, I'll keep process overhead minimal and move straight to implementation.

---

## Relevant Findings

I don't have the codebase in front of me, so I'll need a few quick details before I can write the code (see Open Questions below). Once I have those, I can implement immediately.

---

## Open Questions

1. **Which two files?** Please share the paths (or paste the current API handler code).
2. **Rate-limiting strategy?** Fixed window, sliding window, or token bucket? Any existing middleware or library in the project I should use (e.g., `express-rate-limit`, `bottleneck`, Redis-backed)?
3. **Limit parameters?** Requests-per-window, window duration, and what to return on a violation (e.g., `429` with a `Retry-After` header)?

These three answers are the minimum I need to write the right code. They'll take 30 seconds to answer and will avoid rework.

---

## Recommendation

Once you answer the above, I'll implement the rate-limiting logic directly. I'll follow your lead on skipping a formal TDD loop given the crunch — I'll write clean, correct code and you can add tests afterward as planned.

If you want, paste both files now alongside your answers and I'll turn around the implementation immediately.

---

## Artifact Status

No handoff artifact created yet — will create one after implementation if needed.
