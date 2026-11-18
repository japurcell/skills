# Minimize Reader Load

Can a reader trace where a value comes from and what can change it? Remove forwarding-only wrappers, narrow the scope of mutable state, and derive values instead of synchronizing copies. Make each decision at its owner and pass the result along.

Sources: [upstream principle-minimize-reader-load](https://github.com/cursor/plugins/blob/35a90942a7f02e1ebbc2443643179815f2147954/pstack/skills/principle-minimize-reader-load/SKILL.md), [upstream principle-laziness-protocol](https://github.com/cursor/plugins/blob/35a90942a7f02e1ebbc2443643179815f2147954/pstack/skills/principle-laziness-protocol/SKILL.md)
