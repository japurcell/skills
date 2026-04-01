## Response to Crunch-Time TDD Skip Request

I understand the pressure, and I want to help you ship on time. But I can't agree to skip the TDD loop — the feature-dev workflow is explicit on this:

> "Always use the tdd skill to implement with an explicit red-green-refactor loop."

"Always" means it applies on every track, including Light, including under time pressure. It's not a gate you can defer to later in this workflow.

---

### Why "I'll write tests later" doesn't work here

Even in a two-hour window, the TDD loop is the implementation process — the tests are not added after the fact, they drive the code. Writing tests later means you're actually asking to not use TDD at all for this change. That's a different process, not a faster version of this one.

---

### What I can do that actually fits the 2-hour window

**Use the Light track and minimize scope:**

Rate-limiting logic touching two files is a good candidate for the **Light track** — one focused exploration pass, no lengthy architecture design, one recommended implementation path. The TDD loop on a two-file change is not slow; it typically adds 10–20 minutes of discipline in exchange for higher confidence.

**Concrete path:**

1. Quick exploration of the API handler (5 minutes): what does the handler currently do, where would rate-limiting hook in?
2. Write one focused failing test for the rate-limit behavior
3. Implement the smallest code that makes it green
4. Refactor if obviously needed
5. Write the second file's change the same way
6. Launch one independent code-reviewer agent for a fast read

**This fits 2 hours.** What doesn't fit is also doing it correctly _and_ skipping TDD.

---

### If the scope is genuinely too large for TDD in 2 hours

Then the scope should be cut, not the testing. What is the smallest version of rate-limiting logic you could ship now that still provides value? I can help you define that and implement it properly within the time box.
