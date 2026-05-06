**Manager handoff:** keep it lean but explicit. Under the build workflow, the manager should pass:

- **Task text + success criteria**
- **Known constraints**
- **Known validation commands**
- **Only already-known file hints**

For this slice, that means the handoff should name `scripts/addy-install.sh` and `skills/build/evals/grade_benchmark.py`, and spell out that validation must be chosen for a **shell script + Python grader** slice, not a frontend slice. A good handoff is essentially: “Modify these two files, satisfy these acceptance criteria, and use shell/Python-appropriate validation commands.”

**Implementer verification:** the implementer should **infer the slice’s surface and stack first**, then choose the **narrowest matching checks**. From the prompt: treat “run relevant validation” as a **selection task**, not a cue to run generic repo defaults. So here the implementer should pick targeted validation for Bash/Python behavior around those two files—e.g. script-specific execution/syntax checks and the grader’s direct Python verification path—rather than falling back to generic frontend commands like `npm test`, `npm run build`, or other broad UI checks unless the touched code actually routes through them.
