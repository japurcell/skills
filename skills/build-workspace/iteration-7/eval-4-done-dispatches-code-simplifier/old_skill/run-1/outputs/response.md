**Next step:** **Do not update tracking yet.** After an implementer returns `DONE`, the manager should dispatch the **code-simplifier** next. If that returns `DONE`, the manager then dispatches the **code-reviewer**. Tracking is updated **only after** that final reviewer step returns plain `DONE`.

**Context for the next subagent:** send a **lean handoff** with:
1. The **four files the implementer touched**
2. The implementer’s **verification context** — exact commands and results
3. The accepted **task scope / behavior to preserve**
4. The current **`git status --porcelain`** set of **all uncommitted files**, **excluding deleted files and `.gitignore` files**

Keep it to already-known context from the task/plan/repo rules; don’t add broad repo exploration or a pre-solved design.
