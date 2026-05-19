---
name: tdd
description: Test-driven development (TDD) with an explicit red-green-refactor loop. Use this skill whenever the user asks to implement, create, change, fix, or refactor application or library code, even if they never mention tests or TDD. This includes adding features, fixing bugs, writing or updating functions, handlers, components, controllers, modules, API endpoints, scripts, validation, error handling, or CLI commands. The default workflow for any source-code change should be to write a failing test first, make the smallest code change that passes, then refactor safely. Do not use for documentation or explanations only, code review, config or dependency setup, git operations, Docker/infra work, or standalone database queries.
---

# Test-Driven Development

## Philosophy

**Core principle**: Tests should verify behavior through public interfaces, not implementation details. The code can change entirely; tests shouldn't.

**Good tests** are integration-style: they exercise real code paths through public APIs. They describe _what_ the system does, not _how_ it does it. A good test reads like a specification — "user can checkout with valid cart" tells you exactly what capability exists. These tests survive refactors because they don't care about internal structure.

**Bad tests** are coupled to implementation: they mock internal collaborators, test private methods, or verify outcomes through side-channels (like querying a database directly instead of going through the interface). The warning sign is a test that breaks when you refactor but behavior hasn't changed.

See [tests.md](tests.md) for concrete examples, and [mocking.md](mocking.md) for when (and when not) to mock.

The point of TDD is not "have tests." The point is to use a tight feedback loop to discover the interface, prove behavior, and keep the code honest while it changes.

## The One Rule That Derails TDD: Horizontal Slices

Don't write all tests first and then all implementation. That's "horizontal slicing" — it treats RED as "write every test" and GREEN as "write all the code."

This approach produces weak tests because you're writing them against _imagined_ behavior, before you've touched the implementation. You end up testing the _shape_ of things (data structures, function signatures) rather than behaviors that matter. Tests become either over-constrained (they break on internal rename) or under-constrained (they pass even when behavior is broken).

**The right approach is vertical slices**: one test, one implementation, repeat. Each test is written after you've lived through the previous cycle, so you know exactly what behavior is worth testing next.

```
WRONG (horizontal):
  RED:   test1, test2, test3, test4, test5
  GREEN: impl1, impl2, impl3, impl4, impl5

RIGHT (vertical):
  RED→GREEN→REFACTOR: test1→impl1
  RED→GREEN→REFACTOR: test2→impl2
  ...
```

Tiny design note: it is fine to sketch the next 2-3 behaviors in one sentence so the user sees the direction. It is not fine to write all the tests or all the implementation up front.

## Workflow

### 1. Orient (lightweight for simple tasks)

Before writing code, get oriented — but keep this proportional to the task's complexity. For a simple utility function, a sentence or two is enough. For a new module or non-trivial feature, it's worth a paragraph:

- What's the public interface? (What do callers pass in, what do they get back?)
- Which behaviors matter most? (Prioritize; you can't test everything)
- Is there existing test infrastructure? If not, set it up first (see below)

Useful question: _"What should the caller be able to do after this is built?"_

For deeper design questions, see [deep-modules.md](deep-modules.md) and [interface-design.md](interface-design.md).

When the user is fixing a bug, orient around the regression:

- What exact behavior is broken right now?
- What input reproduces it most directly?
- What public-facing assertion would fail before the fix and pass after it?

For bug fixes, start with the narrowest regression test that proves the bug exists. Do not fix the code first and backfill the test later.

#### If there's no test infrastructure yet

Detect the language/framework and set up the minimal test runner before writing any tests. For example:

- **Python**: `pytest` (install with `pip install pytest`, run with `pytest`)
- **JavaScript/TypeScript**: Jest (`npm install --save-dev jest`) or Vitest
- **Go**: built-in (`go test ./...`)
- **Rust**: built-in (`cargo test`)
- **Ruby**: RSpec or minitest

Don't over-engineer the setup. A single test file and a way to run it is enough to start.

### 2. Tracer Bullet (first test)

Write one test that proves the path works end-to-end. It should be the simplest behavior that's actually useful — not a trivial happy path, not a complex edge case. Make it fail first, then make it pass.

The first test should create traction:

- For a new feature, pick the smallest user-visible success case.
- For a bug fix, reproduce the exact bug with the smallest concrete input.
- For an existing codebase, prefer running the narrowest relevant test target instead of the whole suite if the suite is large.

**Show the cycle explicitly in conversation:**

```
# Step 1: Write the test
def test_password_must_be_at_least_8_chars():
    assert not is_valid_password("short")

# Step 2: Run it — it will fail (no implementation yet)
# FAIL: NameError: name 'is_valid_password' is not defined

# Step 3: Write just enough code to pass
def is_valid_password(password):
    return len(password) >= 8

# Step 4: Run it — it passes
# PASSED ✓
```

This explicit walkthrough of the red-green cycle is part of the value. Don't skip to "here's the final code" — show the rhythm.

If tools are available, actually run the relevant test command and use the real failure/output. If tools are not available, state clearly what should fail, why it fails, and what command you would run.

### 3. Incremental Loop

For each remaining behavior: write the test, verify it fails for the right reason, write minimal code, verify it passes.

Key discipline: only enough code to pass the current test. Don't write code for tests you haven't written yet.

That includes "helpful" branches for cases you have not tested yet. If the current test only proves one happy path, do not also add invalid-input handling, extra supported values, or protective edge-case logic just because you expect to need it later.

```
RED:   Write next test → run → should see a clean failure
GREEN: Write minimal code → run → should see it pass
REFACTOR: Clean up if needed → run → still passes
```

When talking through each cycle with the user, it helps to narrate the reason for the failure ("fails because X hasn't been implemented") and what minimal code will fix it.

Be strict about what counts as a good RED step:

- The test must fail for the intended reason, not because of a typo, import error, or broken setup.
- The next test should introduce a behavior that is not already green. If a proposed test already passes, treat it as optional verification and pick a different behavior for the next TDD slice.
- If unrelated existing failures block progress, isolate the relevant test target and say so.
- If the first failure shows the interface is awkward, adjust the design and rewrite the test around the better public interface.

Be equally strict about GREEN: the implementation should satisfy the current behavior and nothing materially beyond it. Untested branches are usually speculation in disguise.

Worked sequencing example (feature work):

```python
# Start with SAVE10 only
def test_save10_applies_10_percent_discount(): ...

# GREEN code after this test should support only SAVE10.
# Do NOT add invalid-code handling yet.
def apply_discount_code(code):
  if code == "SAVE10":
    return 10
  raise NotImplementedError

# Next RED introduces invalid-code behavior
def test_invalid_discount_code_is_rejected(): ...

# Only now add invalid-code handling.
```

If you notice a later test is already green because its behavior was implemented earlier, call that out as a sequencing mistake and reset to the last true RED point.

### 4. Refactor

After the tests pass, look for cleanup opportunities. See [refactoring.md](refactoring.md) for a full list, but the big ones are:

- Extract duplication
- Deepen modules (push complexity behind simpler interfaces)
- Apply SOLID principles where they arise naturally

Run the tests after each refactor step. Never refactor while RED — get to green first.

Refactor in small moves. If you feel tempted to do a large rewrite, stop and add another test first.

## Default Conversation Shape

Use a compact structure that makes the loop obvious:

1. Briefly orient on the interface and the next behavior to implement.
2. Show the next failing test.
3. Show or describe the failure.
4. Add the smallest code change that makes that test pass.
5. Re-run the relevant test.
6. Decide whether to refactor now or move to the next behavior.

For multi-cycle tasks, repeat this per behavior instead of dumping the final solution all at once.

Good phrases:

- "Let's start with the smallest behavior that matters."
- "This test should fail because the feature doesn't exist yet."
- "Now we add only enough code to make that test pass."
- "Before adding the next case, let's make sure the current slice is green."

Avoid narrating a big upfront implementation plan that skips the live loop.

## Test Naming

Test names are specifications. A good name tells you what behavior the test verifies, what inputs matter, and what the expected outcome is:

```python
# Good — reads like a requirement
def test_rejects_password_under_8_chars(): ...
def test_accepts_password_with_uppercase_lowercase_and_digit(): ...
def test_checkout_fails_when_cart_is_empty(): ...

# Bad — describes implementation, not behavior
def test_validate(): ...
def test_password_validator_returns_false(): ...
def test_case_1(): ...
```

Prefer names that describe business behavior or user-visible rules. Avoid names that leak method names, helpers, or private fields unless those are themselves the public API.

## Guardrails

Do not do these things when following TDD:

- Don't write all tests first.
- Don't write implementation for tests that do not exist yet.
- Don't test private methods or internal collections when a public interface can express the same behavior.
- Don't mock code you own just to make a test easier.
- Don't leave RED ambiguous; confirm why the test is failing.
- Don't treat a bug fix as complete without a regression test.
- Don't add untested branches or error handling "while you're here."

If the code is hard to test through the public interface, treat that as design feedback. Improve the interface or introduce a seam at a true system boundary rather than reaching deeper into internals.

When you add a "next useful test," make sure it is actually the next missing behavior. Do not present a test as part of the active red-green loop if the current implementation already satisfies it; in that case either run it as confirmation after the current slice is green or choose a test that still forces a minimal code change.

## How Many Tests?

You can't test everything, and you shouldn't try. Focus on:

- **Critical paths**: the behaviors that absolutely must work
- **Complex logic**: things with conditionals, edge cases, known-tricky spots
- **Bug regressions**: every fixed bug should get a test that would have caught it

Skip testing:

- Framework behavior (trust the framework)
- Trivial getters/setters with no logic
- Behavior already covered by a test at a higher level

When in doubt, ask the user: "This adds 3 more tests covering edge cases. Do you want to include them or are you satisfied with coverage of the main paths?"

For a bug fix, the default minimum is:

- one regression test that reproduces the reported bug
- the smallest fix that makes it pass
- one nearby case only if it meaningfully protects against an obvious follow-on failure

Bias toward stopping after the reported bug is green. Add adjacent coverage only when the prompt, existing behavior, or the format/spec strongly implies that the neighboring case is part of the same requirement.

## Quick Checklist Per Cycle

```
[ ] Test name describes behavior, not implementation
[ ] Test uses public interface only
[ ] Test fails for the intended reason
[ ] Test would survive internal refactor
[ ] Code is minimal for this test
[ ] No speculative features added
[ ] Relevant tests re-run after refactor
```
