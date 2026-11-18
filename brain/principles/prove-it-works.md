# Prove It Works

**Principle:** Every task output must be verified by checking the real thing directly - not by inferring from proxies, self-reports, or "it compiles."

## Why

Unverified work has unknown correctness. Indirect verification (file mtimes, output freshness, agent self-reports, cached screenshots) feels cheaper than direct observation, but acting on a wrong inference costs far more than checking the source.

## Pattern

After completing any task, ask: **"How do I prove this actually works?"**

### Check the real thing, not a proxy

- **Check process liveness directly** (PID, process table), not indirectly (tmux pane status, file mtime).
- **Read the actual value**, not a cached or derived representation.
- **When verification fails, suspect the observation method** before suspecting the system.

### Code / Features

1. Build it (necessary but not sufficient)
2. Run it and exercise the actual feature path
3. Check the full chain: does data flow from input to output?
4. For integrations (IPC, sockets), test the full communication path end-to-end

Verify an observable outcome against an independently derived expectation. Check that a realistic defect makes the test fail for the intended reason, that a harmless implementation change leaves it passing, and that any test double accepts, rejects, and returns what the real dependency would for the case under test.

For a claimed no-effect case, pair it with a control case that should cause the effect. Assert the error type callers branch on, not its message.

### Skills / Scripts / Tools

1. Spawn a subagent to actually use the skill end-to-end
2. Run scripts with real inputs and verify output
3. Test error paths: bad input, missing files, timeouts

### General

- Use a [rerunnable check](build-the-lever.md) when practical. Keep the observed output available for review and commit the check when the verification trail needs to remain auditable.

### Delegation: trust artifacts, not self-reports

When verifying delegated work, inspect the actual output artifact (`git diff --stat`, file contents, runtime behavior) - never the delegate's summary of what they claim to have done. Agents report what they intended, not always what happened. Scope violations and silent failures are invisible in self-reports but obvious in artifacts.

## Relationship to Other Principles

[principles/fix-root-causes](fix-root-causes.md) extends this to debugging - check the real cause, not the proxied symptom.

See also [principles/foundational-thinking](foundational-thinking.md)

[Upstream principle-prove-it-works](https://github.com/cursor/plugins/blob/35a90942a7f02e1ebbc2443643179815f2147954/pstack/skills/principle-prove-it-works/SKILL.md)
[Upstream principle-test-behavior-not-implementation](https://github.com/cursor/plugins/blob/35a90942a7f02e1ebbc2443643179815f2147954/pstack/skills/principle-test-behavior-not-implementation/SKILL.md)
