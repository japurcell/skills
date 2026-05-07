The manager should **reject that `NEEDS_CONTEXT` and re-dispatch**. In this workflow, **ordinary repo exploration is the implementer’s job**, and the manager must **not** pre-read the repo, draft the solution, or hand over likely patches.

A manager response should look like this:

> `NEEDS_CONTEXT` is not valid here. Repo exploration, pattern lookup, and first-pass design are part of the implementer role. I’m not going to read the repo or solve it for you up front.  
>  
> Proceed from this lean handoff:
> - **Task:** [original task text]
> - **Success criteria:** [acceptance criteria]
> - **Constraints:** [known constraints / repo rules]
> - **Validation:** [known validation commands]
> - **File hints:** [only already-known files, if any]  
>  
> Read the relevant files and patterns yourself, choose the narrowest matching validation, and continue. Use `NEEDS_CONTEXT` only if you hit **missing requirements, missing constraints, or conflicting signals** you cannot resolve from the task, plan, and codebase.

If nothing is actually missing, the manager should **re-dispatch immediately**, typically with the **same model**, not escalate.
