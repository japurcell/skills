**Next:** re-dispatch the **implementer** to fix the two correctness findings in the already touched files. The manager should **not** fix them directly. After the implementer returns `DONE`, send the updated result back through **code-simplifier**, then **code-reviewer** again.

**Tracking:** do **not** mark the task done yet. Under the build workflow, tracking can be updated only after the **final** code-reviewer pass returns `DONE`; that is when the manager updates the plan/todo tracker, records the verification actually performed, and marks the task complete.
