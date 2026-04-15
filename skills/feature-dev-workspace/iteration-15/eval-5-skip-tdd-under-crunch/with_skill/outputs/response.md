# Feature Dev Response: Rate-Limiting Under Deadline Pressure

## Understanding

**Track chosen: Light** — well-bounded change, two files, clear intent. This is the right track for moving fast without manufacturing process overhead.

I hear the deadline. Two hours is workable for a two-file rate-limiting change, and I want to keep this moving. But I can't skip the TDD loop — not because of bureaucracy, but because the skill mandates it for every track, and for rate-limiting logic specifically, it's the right call for you right now.

Here's the honest case for TDD under a deadline:

- Rate-limiting bugs (wrong window size, counter not resetting, off-by-one on the limit threshold) are exactly the class of bug that bites silently in production and is hard to diagnose after the fact.
- Writing the test first forces you to specify "what does correct behavior look like" before you write code — which is the same thinking you'd do anyway. Making it explicit takes minutes, not hours.
- For two files, a focused red-green-refactor loop adds roughly 15–20 minutes. It does not add an hour.
- "I'll write tests later" under crunch almost never happens, and untested rate-limiting logic is a liability that outlasts the deadline.

**What I will not do**: skip the TDD red-green-refactor loop. This is non-negotiable per the workflow regardless of track or urgency.

**What I will do**: run the Light track at full speed. No staged approval gates, no extra design phases, no waiting for confirmation on minor decisions. We move directly from focused exploration → TDD implementation → quick review.

---

## Relevant Findings

I don't yet have access to your codebase. Before I can implement, I need a brief look at:

- The API handler file(s) that will be modified
- Any existing middleware, decorator, or request-lifecycle patterns already in place
- Whether there's an existing cache/store (Redis, in-memory, etc.) the rate limiter should use, or whether that needs to be introduced

This exploration will take a few minutes, not a phase unto itself.

---

## Open Questions

Only two questions materially affect the implementation:

1. **Where is the rate-limiting state stored?** If you already have Redis or a shared cache, I'll use it. If not, I'll use an in-memory store with the understanding that it won't work across multiple processes — flag this explicitly in the code.

2. **What are the rate-limit parameters?** (e.g., 100 requests per minute per IP, 1000 per hour per API key). If you don't have a firm number yet, I'll use a configurable constant with a sensible default and we can tune it later.

If you tell me "whatever you think is best," I'll state my assumptions and move forward immediately.

---

## Recommendation

Proceed on the **Light track with TDD**:

1. **Explore** (5 min): Read the two target files and any existing middleware patterns.
2. **Write failing tests** (10 min): Specify the rate-limiting contract — requests within limit succeed, requests over limit return 429 with `Retry-After`, edge cases for window reset.
3. **Implement** (20–30 min): Write the minimal rate-limiting logic that makes the tests pass.
4. **Refactor** (5 min): Clean up the implementation; confirm tests still pass.
5. **Quick review** (5 min): Check for obvious correctness and convention issues.

Total: ~45–55 minutes, well within your two-hour window.

---

## Implementation Map

Once I see your files, the implementation will touch:

| File | Change |
|------|--------|
| `<api-handler file>` | Add rate-limit check at the top of the handler (or via middleware hook) |
| `<rate-limiter/middleware file>` | New rate-limiting logic: sliding window or fixed window, configurable limit + window, 429 response with `Retry-After` header |

**Validation steps** (in order):
1. Red: failing tests that assert on-limit and over-limit behavior
2. Green: implementation passes all tests
3. Refactor: simplify, remove duplication, verify tests still pass
4. Run full test suite to confirm no regressions

---

## Next Step

Share the two files (or point me to the repo path), confirm or correct the rate-limit parameters, and I'll start immediately. The TDD loop is the fastest path to a change you can actually ship with confidence before the deadline.
