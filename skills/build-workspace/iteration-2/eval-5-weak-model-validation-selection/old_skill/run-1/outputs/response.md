The manager should **not** hand off only “run relevant validation.” Under this build workflow, the handoff should stay lean but must include the pieces that prevent drift:

- **Task text**
- **Acceptance criteria**
- **Known constraints**
- **Relevant commands**
- **Explicit file hints already known from the task**

For this task, that means the manager should hand the implementer something like: update `scripts/addy-install.sh` and `skills/build/evals/grade_benchmark.py`; satisfy the task’s acceptance criteria; **use narrow, file-relevant validation**; remember repo constraints already known here such as **scripts are run with `python3`**, there is **no single repo-wide default test/build command**, and **do not substitute generic frontend commands**.

The implementer should then choose verification from the **touched files and their local patterns**, not from generic repo habits. Concretely: start by reading the minimum relevant context around those two files, then run the **smallest existing checks that actually exercise shell-script and Python eval behavior**. Only run a broader suite/build if the code they inspect shows that such a command is actually the relevant existing validation path. If they cannot find a real file-local validation command, they should say that plainly rather than inventing `npm test`, `npm run build`, or other generic frontend commands.
