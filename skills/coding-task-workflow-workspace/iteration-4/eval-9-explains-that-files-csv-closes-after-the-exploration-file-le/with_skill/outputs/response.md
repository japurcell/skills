# GitHub Issue Tree Closure and Phase 7 Task Graph Location

## Artifact Closure Timing

### When to close each artifact:

1. **`files.csv`** — Close when **the exploration ledger is complete**
   - Closure event: `files.csv` ledger is complete
   - Action: Close the `files.csv` artifact subissue
   - Reference: Issue Lifecycle table, line 305 in issue-hierarchy.md

2. **`sources.md`** — Close when **the research phase is complete and the sources ledger is finalized**
   - Closure event: `sources.md` ledger is complete
   - Action: Close the `sources.md` artifact subissue
   - Reference: Issue Lifecycle table, line 306 in issue-hierarchy.md

3. **`open-questions`** — Close when **every open question is finalized**
   - Special note: This artifact remains open **across phases 3–5** (Exploration, Research, and Clarification) while questions are still being resolved
   - Closure event: Every open question is finalized
   - Action: Close the `open-questions` artifact issue
   - Reference: Issue Lifecycle table, lines 307–308 in issue-hierarchy.md

## Phase 7 Task Graph Location

**The Phase 7 task graph YAML lives in the `phase:task-graph` issue body.**

- **Location**: The task graph is rendered as a fenced `yaml` code block directly in the task-graph phase issue body
- **Not a separate artifact**: Do not create a separate `task-graph.yaml` artifact subissue
- **Structure**: The task-graph issue is a phase issue (not an artifact subissue) labeled `phase:task-graph`
- **Format**: The YAML task graph is kept in the issue body as fenced code, following the phase issue template

### References:
- issue-hierarchy.md, line 193: "For Phase 7 specifically, keep the task graph YAML in the phase issue body. Do not create a separate `task-graph.yaml` artifact subissue."
- issue-hierarchy.md, line 22: "Task-graph issue: [phase:task-graph] YAML task graph in issue body"
- artifact-schema.md: "The Phase 7 task graph is phase-owned: keep the fenced `yaml` block in the `phase:task-graph` issue body rather than creating a separate `task-graph.yaml` artifact subissue."

## Summary

The GitHub issue tree ends cleanly by:
- Closing `files.csv` after the exploration ledger is complete (Phase 3)
- Closing `sources.md` after the research ledger is finalized (Phase 4)
- Closing `open-questions` after all research questions are resolved (spanning Phases 3–5, closed when finalized in Phase 5)
- The Phase 7 task graph YAML resides directly in the body of the `phase:task-graph` issue, not in a separate artifact subissue
