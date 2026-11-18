# Separate Before Serializing Shared State

When concurrent actors may write the same file, branch, key, or object, first ask whether they need shared state at all. Prefer independent outputs that are merged where they are read. Separate fields inside one shared mutable file still contend on that file.

If one shared write target is a genuine invariant, serialize access structurally with a single writer, lock, sequential phases, or compare-and-swap. Instructions alone do not coordinate concurrent writes.

Source: [upstream principle-separate-before-serializing-shared-state](https://github.com/cursor/plugins/blob/35a90942a7f02e1ebbc2443643179815f2147954/pstack/skills/principle-separate-before-serializing-shared-state/SKILL.md)
