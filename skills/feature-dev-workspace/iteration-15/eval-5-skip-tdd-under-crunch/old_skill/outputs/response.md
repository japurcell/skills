# Feature Dev Response: Rate-Limiting Under Crunch

## Understanding

I hear you — two hours is tight, and I want to help you ship this. That said, I can't skip TDD here, even under crunch.

**Process Track: Light** — this is a well-bounded change touching two files, with clear intent. That's exactly the kind of work where TDD is fast rather than slow.

**Why I won't bypass TDD:**

The skill I operate under makes TDD mandatory for every track:

> *"Always use the tdd skill to implement with an explicit red-green-refactor loop. Treat this as required for Implementation on every track; do not bypass it."*

This isn't bureaucracy — it's the guard rail that makes a tight deadline *survivable*. Rate-limiting logic has sharp edges: off-by-one on window boundaries, race conditions on counters, wrong header values, silent failures under load. A two-hour deadline that ships broken rate-limiting is worse than a two-hour deadline with a red-green-refactor pass.

The good news: **Light track TDD on two files shouldn't take more than 30–40 minutes**, leaving you plenty of runway.

---

## What I Need Before Starting

I don't have your codebase in front of me, so I have two focused questions (both block the implementation):

1. **What are the two files?** (e.g., `src/api/handler.ts` and `src/middleware/rateLimiter.ts`)
2. **What is the rate-limiting rule?** (e.g., 100 requests per minute per IP, 10 req/s per API key, sliding window vs. fixed window)

If you can paste those two answers, I'll move immediately to:

1. Write a failing test that captures the rate-limiting contract
2. Implement the minimum code to make it pass
3. Refactor for clarity
4. Run a fast code-simplifier + reviewer pass

---

## Recommendation

**Do not skip TDD.** Instead, let's run a tight Light-track loop:

| Step | Est. Time |
|---|---|
| Write failing test(s) | 10 min |
| Implement rate-limiting logic | 15 min |
| Refactor / cleanup | 5 min |
| Quick review pass | 5 min |
| **Total** | **~35 min** |

That leaves 85 minutes of buffer before your deadline. You'll ship something you can trust, and you won't need to write the tests later under even more pressure.

Share the two files and the rate-limiting rule and I'll start immediately.
