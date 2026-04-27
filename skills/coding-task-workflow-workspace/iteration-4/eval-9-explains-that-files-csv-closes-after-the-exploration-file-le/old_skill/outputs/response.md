# GitHub Issue Tree Closure Points and Phase 7 Task Graph Location

## When Issues Should Close in the coding-task-workflow

The GitHub issue tree is structured hierarchically with parent issues, phase issues, and artifact subissues. Here is when each key artifact closes to keep the issue tree clean:

### `files.csv` — Closes After Exploration Exploration Phase
- **When**: "Close the `files.csv` artifact subissue as soon as the file ledger is complete." (Phase 3, Step 7)
- **Closure point**: At the end of Phase 3 (Codebase Exploration), immediately after the file list is finalized
- **Reason**: This artifact is a supporting ledger that documents which files are relevant to the work item. Once the exploration summary is written, the file listing is complete and ready for downstream phases to reference
- **Location in hierarchy**: `files.csv` is a nested artifact subissue under the `phase:exploration` child issue

### `sources.md` — Closes After Research
- **When**: "Close the `sources.md` artifact subissue as soon as the source ledger is complete." (Phase 4, Step 6)
- **Closure point**: At the end of Phase 4 (Online Research), immediately after the source ledger is finalized
- **Reason**: This artifact documents all URLs and sources that were checked during research. Once all research is complete and recorded, the ledger is stable
- **Location in hierarchy**: `sources.md` is a nested artifact subissue under the `phase:research` child issue

### `open-questions` — Closes at the End of Clarification
- **When**: "Close the `open-questions` artifact issue once every entry is either resolved or explicitly finalized as `needs-human`; do not leave it open after clarification completes." (Phase 5, Step 8)
- **Closure point**: At the end of Phase 5 (Clarification), after all questions have been either resolved with answers or explicitly marked as `needs-human` (assumptions that cannot be resolved further)
- **Reason**: This artifact is durable across Phases 3, 4, and 5 because questions may be resolved during exploration, refined during research, and answered during clarification. Once Phase 5 closes, every question must have a final status
- **Lifecycle**: Opens in Phase 3 → Updated in Phase 4 → Updated and closed in Phase 5
- **Location in hierarchy**: `open-questions` is a nested artifact subissue under the `phase:exploration` child issue (but remains open across multiple phases)

### Summary of the Issue Lifecycle for These Artifacts

| Artifact | Opens | Closes | Durable Across Phases |
|----------|-------|--------|----------------------|
| `files.csv` | Phase 3 | End of Phase 3 | No — closes immediately |
| `sources.md` | Phase 4 | End of Phase 4 | No — closes immediately |
| `open-questions` | Phase 3 | End of Phase 5 | Yes — spans Phases 3, 4, 5 |

---

## Where the Phase 7 Task Graph YAML Lives

The Phase 7 task graph YAML is **stored directly in the body of the `phase:task-graph` GitHub issue**, not in a separate file or artifact subissue.

### Location Details

- **GitHub issue**: Created as a child issue of the parent work-item issue
- **Label**: `agent:phase` and `phase:task-graph`
- **Format**: YAML in a fenced code block within the issue body
- **Template**: Uses [`templates/task-graph.yaml`](references/templates/task-graph.yaml) as the content shape

### Phase 7 Specification

From the workflow specification (Phase 7 — TDD Task Graph):

**Step 4**: "Create a GitHub child issue labelled `agent:phase` and `phase:task-graph`. Put the task graph in a fenced `yaml` block using [templates/task-graph.yaml](templates/task-graph.yaml) as the content shape."

**Step 5**: "Create one GitHub child issue per vertical slice and attach it under the Phase 7 task-graph issue. Label each `agent:task`, `phase:implement`, plus `parallel` or `sequential` as appropriate. Initialize each task issue with `stage: red`; RED, GREEN, and REFACTOR progress stays on that same issue as comments rather than separate issues."

**Step 6**: "Close the task-graph issue once the YAML and implementation task issues are complete."

### Task Graph Hierarchy

The Phase 7 issue tree looks like:
```
Parent issue: #N  [agent:parent]  Feature / bug / spec
  └── Task-graph issue:     [agent:phase, phase:task-graph]
      ├── Task issue:       [agent:task, phase:implement]  Task: <slice 1>
      ├── Task issue:       [agent:task, phase:implement]  Task: <slice 2>
      └── Task issue:       [agent:task, phase:implement]  Task: <slice 3>
```

### Why Not Separate Files

The task graph lives in GitHub (not as a separate file) because:
1. **Durable cross-session record**: The workflow is GitHub-native for Phases 1–11. Agents resume work by reading GitHub issues, not local files
2. **Single source of truth**: The GitHub issue is the authoritative task graph; there is no parallel `task-graph.yaml` file
3. **Sub-issue linking**: Implementation task issues are GitHub sub-issues of the task-graph issue, creating a direct linkage within GitHub's native issue hierarchy

---

## Summary

To keep the GitHub issue tree clean in coding-task-workflow:
- **`files.csv`**: Close at the end of Phase 3 (Exploration) — immediately when the file ledger is complete
- **`sources.md`**: Close at the end of Phase 4 (Research) — immediately when the source ledger is complete  
- **`open-questions`**: Close at the end of Phase 5 (Clarification) — after all questions are resolved or finalized as assumptions

The **Phase 7 task graph YAML** lives in the body of the GitHub `phase:task-graph` issue (a labeled child issue under the parent work-item issue), not as a separate file. Implementation task issues are sub-issues of the task-graph issue, preserving the hierarchy within GitHub.
