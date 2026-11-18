# Fix Root Causes

**Principle:** When debugging, never paper over symptoms. Trace every problem to its root cause and fix it there.

## Why

Symptom fixes accumulate: each workaround makes the system harder to reason about, and the real bug remains. Root-cause fixes are slower upfront but reduce total debugging time across the project's lifetime.

## Pattern

- **Reproduce first.** If you can't reproduce it, you can't verify your fix.
- **Ask "why" until you hit bedrock.** The test fails → the mock is wrong → the interface changed → the type doesn't match the runtime shape. Fix the type, not the mock.
- First ask whether the triggering state is legitimate. Handle legitimate states where the system failed. If the state should never exist, trace what produced it instead of adding a guard, retry, swallowed error, clamp, or discarded state.
- When several fixes fail the same check, name their shared assumption. Use the pattern of failures to predict what a competing explanation would produce, then test that prediction before trying another fix.
- **Check for the pattern, not just the instance.** If one file has a bug, grep for the same pattern. Fix all instances, or make it structurally impossible.
- **When stuck, instrument - don't guess.** Add logging, read the actual error.
- If finding the deciding fact took a deep investigation, propose a cheap always-on signal that would expose it earlier next time.

## Restart Bugs: Suspect State Before Code

Code doesn't change between runs. State does. When "fails after restart," suspect stale persistent state first - config files, caches, lock files, serialized state. If clearing a state file restores behavior, prioritize state validation as the fix.

## Own Every File You Touch

Never label an issue "pre-existing" to justify skipping it. If you touch a file, you own its quality. Fix lint errors, style violations, and bugs in the file regardless of who introduced them. The distinction between "my changes" and "existing code" doesn't exist - all codebase issues are shared ownership.

## Relationship to Other Principles

[principles/prove-it-works](prove-it-works.md) says to check real state, not proxies. This extends that to debugging: check the real cause, not the proxied symptom.

[principles/encode-lessons-in-structure](encode-lessons-in-structure.md) provides the encoding mechanism once a root cause is understood - make it structurally impossible to recur.

See also [principles/prove-it-works](prove-it-works.md), [principles/encode-lessons-in-structure](encode-lessons-in-structure.md)

[Upstream principle-fix-root-causes](https://github.com/cursor/plugins/blob/35a90942a7f02e1ebbc2443643179815f2147954/pstack/skills/principle-fix-root-causes/SKILL.md)

[upstream principle-attack-the-premise](https://github.com/cursor/plugins/blob/35a90942a7f02e1ebbc2443643179815f2147954/pstack/skills/principle-attack-the-premise/SKILL.md)
