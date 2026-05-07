**Next:** do **not** update tracking yet. Per `/home/adam/dev/personal/skills/skills/build/SKILL.md`, the manager should choose the narrowest reasonable subagent/model and dispatch the **code-simplifier**. If the simplifier returns `DONE`, dispatch the **code-reviewer**. Only after the **code-reviewer** returns `DONE` should the manager update the plan/todo tracking.

**Context for the next subagent (code-simplifier):**
1. The four files the implementer touched.
2. The implementer’s verification context.
3. All current uncommitted files from `git status --porcelain`, **excluding** deleted files and `.gitignore` files.

Keep that handoff lean: pass only already-known task/plan/rules context, not extra repo discovery or a pre-solved design.
