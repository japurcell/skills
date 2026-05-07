**Now the manager should update tracking, not code history.** After the final `code-reviewer` returns plain `DONE`, the build workflow says to update the **tracker/plan/todo tracking** immediately, **record the verification actually performed**, and **mark the task `done`**.

**No commit should be created.** The build skill’s commit rule is explicit: **“Never commit. The human will review the changes and commit manually later.”**
