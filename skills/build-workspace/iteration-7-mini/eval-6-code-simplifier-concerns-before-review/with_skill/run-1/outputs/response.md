Do not proceed to code-reviewer or update tracking. Per the Build workflow, read the simplifier's concerns and treat this as unresolved work: the helper’s widened scope is a correctness/scope concern.

Re-dispatch the implementer (owner of the fix) with:
- the simplifier’s concern text,
- the touched files,
- the current verification context and git status (uncommitted files),
- clear success criteria (either narrow the helper or inline it, and add tests that prove pre-change behavior is preserved; run the specified verification commands).

After the implementer returns DONE and verification passes, route back through the simplifier then code-reviewer.
