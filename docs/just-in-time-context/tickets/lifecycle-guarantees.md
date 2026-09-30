# Lifecycle Guarantees

**Type:** grilling
**Status:** open
**Blocked By:** provider-lifecycle-capabilities.md, success-criteria.md
**Research Dir:** not applicable

## Question

What guarantees must retrieval, learning, and maintenance provide across Codex, Copilot, and Gemini given each provider's actual lifecycle capabilities?

Define task, turn, session, and work-session boundaries; required automatic triggers; completion signals; and any provider-specific fallback. Decide what "does not rely on agents remembering" means in observable behavior. Determine whether a hook invokes work, injects guidance, or enforces a pending-work contract, and which supported surfaces the first version guarantees. Skill subcommands remain a proposed interface.

Apply [Context Retrieval Contract](context-retrieval-contract.md) to startup, scope expansion, compaction, resume, and child execution. Choose automatic events and enforcement that establish delivery before dependent work rather than assuming native discovery or inheritance. The semantic retrieval requirements are settled; provider mechanisms and guarantees remain this ticket's decisions.

---

<!-- Resolution will be appended here. -->
