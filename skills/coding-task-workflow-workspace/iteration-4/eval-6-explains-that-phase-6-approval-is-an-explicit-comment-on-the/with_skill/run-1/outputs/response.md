# Phase 6–8 Artifact Recording in GitHub-Native Flow

Now that `05-plan.md`, `06-task-graph.yaml`, and `07-implementation-log.md` are gone, the `coding-task-workflow` skill records these artifacts and milestones directly in GitHub:

---

## Phase 6 Approval (Gate D)

**Where it lives**: The plan issue body and an explicit approval comment.

1. **Plan Issue**: Create a GitHub child issue labelled `agent:phase` and `phase:plan`. The issue body contains the full implementation plan (goal, non-goals, approach, rationale, alternatives, file-by-file map, verification steps) using the plan template.

2. **Approval Recording**: Present a concise summary to the human and ask for explicit approval. Record the approval as **an explicit comment on the plan issue** with a `## Machine Data` section containing:
   ```yaml
   kind: approval
   phase: plan
   status: approved
   approved_by: human
   approved_at: <ISO8601>
   ```

3. **Closing the Issue**: Close the plan issue immediately after the approval comment is posted. If the human requests changes, edit the plan issue body and repeat the approval step.

**Result**: A closed plan issue with durable approval comment. This is what Gate D checks for.

---

## Phase 7 Task Graph (Gate E)

**Where it lives**: The task-graph issue body (YAML) and implementation task issues (one per vertical slice).

1. **Task Graph Storage**: Create a GitHub child issue labelled `agent:phase` and `phase:task-graph`. Put the entire task graph in a **fenced YAML block in the issue body** (not a separate artifact file). The YAML follows the task-graph template and includes:
   - `id`, `name`, `depends_on`, `parallelizable`, `files` for each slice
   - Each slice starts with `stage: red`
   - No circular dependencies

2. **Implementation Task Issues**: For each vertical slice in the task graph, create one GitHub child issue under the task-graph issue. Label each with `agent:task`, `phase:implement`, plus `parallel` or `sequential`. Initialize each with `stage: red` in the machine data.

3. **Closing the Task-Graph Issue**: Once the YAML and all implementation task issues are created, close the task-graph issue.

4. **Hard Stop**: After Gate E is satisfied (task-graph issue closed, at least one task at `stage: red`, all tasks have explicit dependency lists), **stop the session and hand off a resume command**: `coding-task-workflow RESUME=<slug>`. Do not proceed to Phase 8 in the same session.

**Result**: A closed task-graph issue with YAML in its body, plus open implementation task issues under it. This is the durable record for Phase 8 to resume from.

---

## Phase 8 Implementation Log (After Resume)

**Where it lives**: Comments on the individual implementation task issues.

1. **Resume Rebuild**: In Phase 8, use `RESUME=<slug>` to reconstruct state from the GitHub issue tree. Load the task-graph issue and all implementation task issues. Do not rely on local `07-implementation-log.md`.

2. **RED / GREEN / REFACTOR Progress**: For each task issue:
   - **RED**: Write a failing test. Record the result as a comment on the task issue while the issue stays at `stage: red`.
   - **GREEN**: Update the task issue to `stage: green`, write the minimal code, run the test, and record as a comment.
   - **REFACTOR**: Update the task issue to `stage: refactor`, clean up, rerun tests, and record as a comment.

3. **Comment Format**: Each progress comment includes a `## Machine Data` section with:
   ```yaml
   kind: implementation-log
   task_id: <id>
   stage: red | green | refactor
   status: complete | blocked
   updated_at: <ISO8601>
   ```

4. **Task Issue Closure**: Close each task issue when its slice is complete. The task issue comments replace the old `07-implementation-log.md` file.

**Result**: Updated task issues with progress recorded as comments, and closed task issues when slices complete. The GitHub task issues are the durable implementation record.

---

## Summary

| Artifact | Old Location | New Location | Gate Check |
| --- | --- | --- | --- |
| **Phase 6 Plan** | `05-plan.md` | Plan issue body + approval comment | Gate D: plan issue closed + approval comment exists |
| **Phase 7 Task Graph** | `06-task-graph.yaml` | Task-graph issue body (YAML) | Gate E: task-graph issue closed + tasks at `stage: red` |
| **Phase 8 Progress** | `07-implementation-log.md` | Comments on task issues | Task issues updated in place; closed when done |

All artifacts now live in GitHub, making work resumable and auditable across sessions and agents without requiring local per-work-item directories.
