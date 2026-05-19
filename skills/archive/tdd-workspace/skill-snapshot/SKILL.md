---
name: tdd
description: Test-driven development (TDD) with red-green-refactor loop. Use this skill whenever the user wants to write code test-first, mentions "TDD", "red-green-refactor", "write tests first", "write a failing test", or asks you to "use TDD" on any feature or bug fix. Also use it when someone says "let's build this with tests", "help me write unit/integration tests as I build", or "I want to test-drive this implementation". Use it for bug fixes where the user wants to start with a failing test. Use it even if they don't say "TDD" explicitly but it's clear they want a test-first workflow.
---

# Test-Driven Development

## Philosophy

**Core principle**: Tests should verify behavior through public interfaces, not implementation details. The code can change entirely; tests shouldn't.

**Good tests** are integration-style: they exercise real code paths through public APIs. They describe _what_ the system does, not _how_ it does it. A good test reads like a specification — "user can checkout with valid cart" tells you exactly what capability exists. These tests survive refactors because they don't care about internal structure.

**Bad tests** are coupled to implementation: they mock internal collaborators, test private methods, or verify outcomes through side-channels (like querying a database directly instead of going through the interface). The warning sign is a test that breaks when you refactor but behavior hasn't changed.

See [tests.md](tests.md) for concrete examples, and [mocking.md](mocking.md) for when (and when not) to mock.

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

## Workflow

### 1. Orient (lightweight for simple tasks)

Before writing code, get oriented — but keep this proportional to the task's complexity. For a simple utility function, a sentence or two is enough. For a new module or non-trivial feature, it's worth a paragraph:

- What's the public interface? (What do callers pass in, what do they get back?)
- Which behaviors matter most? (Prioritize; you can't test everything)
- Is there existing test infrastructure? If not, set it up first (see below)

Useful question: _"What should the caller be able to do after this is built?"_

For deeper design questions, see [deep-modules.md](deep-modules.md) and [interface-design.md](interface-design.md).

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

### 3. Incremental Loop

For each remaining behavior: write the test, verify it fails for the right reason, write minimal code, verify it passes.

Key discipline: only enough code to pass the current test. Don't write code for tests you haven't written yet.

```
RED:   Write next test → run → should see a clean failure
GREEN: Write minimal code → run → should see it pass
REFACTOR: Clean up if needed → run → still passes
```

When talking through each cycle with the user, it helps to narrate the reason for the failure ("fails because X hasn't been implemented") and what minimal code will fix it.

### 4. Refactor

After the tests pass, look for cleanup opportunities. See [refactoring.md](refactoring.md) for a full list, but the big ones are:

- Extract duplication
- Deepen modules (push complexity behind simpler interfaces)
- Apply SOLID principles where they arise naturally

Run the tests after each refactor step. Never refactor while RED — get to green first.

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

## Quick Checklist Per Cycle

```
[ ] Test name describes behavior, not implementation
[ ] Test uses public interface only
[ ] Test would survive internal refactor
[ ] Code is minimal for this test
[ ] No speculative features added
```
