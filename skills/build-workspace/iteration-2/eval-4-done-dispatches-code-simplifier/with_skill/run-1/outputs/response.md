**Next:** dispatch the **code-simplifier** subagent. The manager should **not update tracking yet**; per the build skill, tracking waits until the **final subagent** returns **`DONE`**.

The next subagent’s context should be:
1. The **four files the implementer touched** — those are the simplifier’s review scope.
2. The task’s **accepted behavior/scope** so it preserves the implementer’s result.
3. The relevant **validation context** so it can re-run the matching checks, not generic ones.

In short: **implementer `DONE` → code-simplifier over touched files → only after simplifier `DONE`, update tracking.**
