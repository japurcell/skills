# Feature-Dev Response: Rate-Limiting Under Crunch

---

## Understanding

**Track chosen: Light**

The change is well-bounded — two files, rate-limiting logic on an API handler, no stated ambiguity about what the limiter should do. The main risk is getting the implementation right quickly, not resolving product questions.

However, the request includes a condition I cannot accept: skipping TDD. The feature-dev skill requires an explicit red-green-refactor loop on every track, without exception. I'm not going to skip it — but I _will_ run it fast, because with a two-file change the loop is short.

---

## On the TDD Question

I understand the pressure. Two hours feels tight, and writing tests first can feel like overhead when you just want to ship.

Here's the reality: **skipping TDD under pressure is exactly when it costs the most.** A missed edge case in rate-limiting logic (off-by-one on the counter, a missing reset, a race between requests) is the kind of bug that causes an incident at the worst possible moment — right after a deadline crunch. The test takes 5–10 minutes. The incident takes hours.

More importantly: **TDD doesn't slow down a two-file change.** The red-green-refactor loop for a bounded piece of logic like this is fast because:

- The tests are small and focused.
- Running them is immediate feedback, not a gating ceremony.
- You write less code because the test clarifies exactly what the limiter needs to do.

I'm proceeding with TDD. Here's my concrete plan so you can see the time cost is minimal.

---

## Relevant Findings

Before writing any code I need to explore two things:

1. **The API handler files** — understand their current structure, request context shape, and existing middleware patterns.
2. **Any existing rate-limiting infrastructure** — cache/store availability (Redis, in-memory, etc.), existing middleware hooks, and conventions for returning 429 responses.

I'll do this exploration directly (Light track: one focused pass, no parallel agents needed for two files).

> **Assumption**: Until I see the code, I'll assume the limiter needs a fixed-window or sliding-window counter keyed by IP or API key, stored in whatever in-process or shared cache the codebase already uses. If there's no existing store, I'll use a simple in-memory Map with a TTL-safe implementation that degrades gracefully under restart.

---

## Open Questions

Only one question is blocking before I start:

1. **What counts as a "request"?** Is the limit per IP, per authenticated user, or per API key? And what is the target limit (e.g., 100 req/min)?
   - If you don't have time to answer right now, tell me your best guess and I'll use it as a default with a clearly named constant so it's trivial to change.

I don't need answers to anything else to start.

---

## Recommendation

**Proceed immediately with Light-track TDD on the two affected files.**

Sequence:

1. Explore the two handler files and any shared middleware (~5 min).
2. Write a failing test that pins the limiter's contract: requests within limit pass, requests over limit return 429 with a `Retry-After` header (~5 min).
3. Implement the minimal rate-limiting logic to make it green (~15–20 min for a two-file change).
4. Refactor for clarity — rename magic numbers, simplify the counter logic (~5 min).
5. Run code-reviewer agent on the diff (~5 min).

**Total: ~35–40 minutes.** That leaves 80+ minutes of buffer inside your two-hour window.

If you take the "skip TDD, write tests later" path, you'll spend at least that long debugging edge cases manually after the fact — and the tests will never get written because the deadline will have already passed.

---

## Implementation Map

### Files to touch

| File                    | Change                                                         |
| ----------------------- | -------------------------------------------------------------- |
| `<api-handler>`         | Add rate-limiter middleware call; return 429 on exceeded limit |
| `<rate-limiter module>` | New or extended: counter logic, TTL reset, configurable limit  |

### Test locations

- Unit tests for the rate-limiter module in isolation (pure function — no HTTP needed)
- Integration-level test on the handler that exercises the 429 path

### Validation steps

1. `npm test` (or equivalent) — all green, including the new limiter tests
2. Manually verify the 429 response shape and `Retry-After` header
3. Code-reviewer agent pass before marking done

---

## Artifact Status

No handoff artifact needed — this is a single-session, two-file change on the Light track. All context is in this response.

---

**Next step for you**: Confirm the rate limit target and the key (IP / user / API key), or give me your best guess so I can use it as a named constant. I'll start exploration and the first failing test immediately after.
