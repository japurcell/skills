Short answer: push back and re-dispatch the implementer with a lean handoff.

Response (manager -> implementer):

"NEEDS_CONTEXT is not valid for routine repo exploration. Per the build workflow, do your own repo discovery and first‑pass design. Re-dispatching you with this lean handoff:

- Task: [paste task text from plan]
- Success criteria: [explicit acceptance tests], e.g. run the narrowest validation for this stack (e.g. pytest / npm test / ./run.sh) and show green output.
- Constraints & validation commands: [list known constraints], run: git status --porcelain, <validation commands>.
- File hints: only already-known files: [list if any]

Deliverables on DONE:
1) files touched list, 2) git status output, 3) verification logs, 4) brief design notes, 5) any true missing requirements (if so, list them precisely). Do not ask the manager to pre-read or hand over a solution."
