# coding-task-workflow Artifact Lifecycle and Task Graph Storage Evaluation

## Summary: Clean GitHub Issue Tree

The skill specifies precise closure points for artifacts to keep the GitHub issue tree clean and organized:

| Artifact | Phase | Closes When | Status at end | Purpose |
|----------|-------|------------|--------------|---------|
| **files.csv** | 3 | Immediately after file ledger complete | **CLOSED** | File discovery complete; no further updates |
| **sources.md** | 4 | Immediately after source ledger complete | **CLOSED** | Research sources documented; no further updates |
| **open-questions** | 3–5 | At end of Phase 5 (clarification) | **CLOSED** | All questions resolved or finalized |
| **Phase 7 Task Graph YAML** | 7 | Phase-owned in issue body | In `phase:task-graph` issue | Not a separate artifact subissue |

---

## 1. files.csv Artifact — Closes in Phase 3

**From workflow.md, Phase 3 — Codebase Exploration, Step 7:**

> Close the `files.csv` artifact subissue as soon as the file ledger is complete.

### Details

**Storage**: Artifact subissue under `phase:exploration` issue

**Content**: Fenced `csv` block with file discovery results
```csv
file_path,reason,agent_found_by,pattern,notes
src/client/http.py,HTTP client implementation,Agent A,existing-feature,Entry point for retry logic
tests/client/test_http.py,Client unit tests,Agent A,test-infrastructure,Must add retry tests here
src/config/retry.yaml,Retry configuration,Agent B,config-file,May need to extend for backoff
```

**Closure timing**: **Phase 3, Step 7 — immediately after the file ledger is finalized**

**Why close it**:
- The file list is deterministic and complete
- No further exploration agents will add files
- Other phases (4, 5, 6, 8) use this as a reference; it doesn't change
- Closing signals: "File discovery is DONE; these are the files in scope"

**Gate A requirement**:
From workflow.md line 122:
> Gate A: the exploration phase issue is closed, the `files.csv` artifact issue is **closed**, and the `open-questions` artifact issue exists before Phase 4 begins.

**At end of Phase 3**: ✓ `files.csv` is **CLOSED**

---

## 2. sources.md Artifact — Closes in Phase 4

**From workflow.md, Phase 4 — Online Research, Step 6:**

> Close the `sources.md` artifact subissue as soon as the source ledger is complete.

### Details

**Storage**: Artifact subissue under `phase:research` issue

**Content**: Markdown table with research sources
```markdown
| URL | Date Checked | Finding | Confidence | Applicability | Decision |
|-----|--------------|---------|------------|---------------|----------|
| https://backoff-algorithms.org/exponential | 2026-04-27 | RFC 9110 recommends exponential backoff for 429/503 | High | Direct | Implement per RFC |
| https://python-retry-libs.dev | 2026-04-27 | tenacity library provides jitter; verify compatibility | Medium | Review | Consider for Phase 9 |
```

**Closure timing**: **Phase 4, Step 6 — immediately after the source ledger is finalized**

**Why close it**:
- The research ledger is complete and immutable
- Future phases reference this for decisions but won't modify it
- Closing signals: "Research is DONE; these are the sources checked"

**Gate B requirement**:
From workflow.md line 148:
> Gate B: the research phase issue is closed, the `sources.md` artifact issue is **closed**, and the `open-questions` artifact issue has no question left at `status: open` before Phase 5 begins.

**At end of Phase 4**: ✓ `sources.md` is **CLOSED**

---

## 3. open-questions Artifact — Closes in Phase 5

**From workflow.md, Phase 5 — Clarification, Step 8:**

> Close the `open-questions` artifact issue once every entry is either resolved or explicitly finalized as `needs-human`; do not leave it open after clarification completes.

### Lifecycle

**Created**: Phase 3, Step 8 (as artifact subissue under exploration)

**Remains OPEN through Phases 3, 4, 5**:
- Phase 3: Questions created; status = `open`
- Phase 4: Research agent updates questions; marks resolved or escalates to `needs-human`
- Phase 5: Human clarification addresses remaining questions; marks resolved or finalizes as `needs-human`

**Updated**: Phase 4 and Phase 5

**From workflow.md, Phase 4, Step 7:**
> Update the `open-questions` artifact issue: mark each question `resolved` or `needs-human`, and include the answer or escalation note.

**From workflow.md, Phase 5, Step 7:**
> Update the `open-questions` issue to reflect the final status for each question.

### Content Format

Example of final state:

```yaml
## Machine Data
work_id: 2026-04-27-add-rate-limit-logs
kind: artifact
artifact_name: open-questions
status: closed
phase: clarification
```

| id | question | status | resolved_by | answer |
|----|----------|--------|-------------|--------|
| q1 | What backoff algorithm should we use? | resolved | Phase 4 research | RFC 9110 recommends exponential backoff with jitter |
| q2 | How do we integrate with existing metrics? | resolved | Phase 5 clarification | Use the existing MetricsCollector class |
| q3 | Should we support custom retry strategies? | needs-human | Design decision | Out of scope for MVP; can add later |

### Closure Timing

**Phase 5, Step 8 — immediately after clarification completes**

**Condition for closure**:
- Every entry has `status: resolved` OR `status: needs-human`
- No entry left with `status: open` or `status: unanswered`

**From workflow.md line 175:**
> Gate C: the clarification issue is closed, the `open-questions` artifact issue is **closed**, and no entry contains both `blocking: true` and `status: unanswered` before Phase 6 begins.

**Why close it**:
- All questions have been resolved or explicitly deferred
- Future phases make decisions based on these answers
- Closing signals: "Questions are RESOLVED; no more clarification needed"

**At end of Phase 5**: ✓ `open-questions` is **CLOSED**

---

## 4. Phase 7 Task Graph YAML — Lives in Issue Body, NOT a Separate Artifact

**From artifact-schema.md, Phase Issue Requirements:**

> The Phase 7 task graph is phase-owned: keep the fenced `yaml` block in the `phase:task-graph` issue body rather than creating a separate `task-graph.yaml` artifact subissue.

### Storage Location

**Parent**: `phase:task-graph` child issue (not an artifact subissue)

**Format**: Fenced YAML block in the issue **body** (not a separate artifact subissue)

**Why not a separate artifact subissue**:
- The task graph is THE primary deliverable of Phase 7
- It's not a supplementary reference like files.csv or sources.md
- It needs to be edited and updated as task issues are created
- Keeping it in the issue body makes it immediately visible and version-controlled via GitHub issue history

### Content

**From workflow.md, Phase 7, Step 4:**
> Put the task graph in a fenced `yaml` block using [templates/task-graph.yaml](templates/task-graph.yaml) as the content shape.

**Example task graph in issue body**:

```yaml
work_id: 2026-04-27-add-rate-limit-logs
phase: task-graph
tasks:
  - id: "task-001"
    name: "Write test for single retry"
    depends_on: []
    parallelizable: false
    files:
      - src/client/http.py
      - tests/client/test_http.py
    stage: red

  - id: "task-002"
    name: "Implement retry logic"
    depends_on:
      - task-001
    parallelizable: false
    files:
      - src/client/http.py
    stage: red

  - id: "task-003"
    name: "Add exponential backoff with jitter"
    depends_on:
      - task-002
    parallelizable: true
    files:
      - src/client/http.py
    stage: red

  - id: "task-004"
    name: "Test backoff configuration"
    depends_on:
      - task-003
    parallelizable: false
    files:
      - tests/client/test_http.py
    stage: red
```

### Task Issues Created Separately

**From workflow.md, Phase 7, Step 5:**
> Create one GitHub child issue per vertical slice and attach it under the Phase 7 task-graph issue. Label each `agent:task`, `phase:implement`, plus `parallel` or `sequential` as appropriate.

**Relationship**:
```
phase:task-graph issue
├── YAML in issue body ← task definitions
├── Task issue: task-001 [agent:task, phase:implement, sequential]
├── Task issue: task-002 [agent:task, phase:implement, sequential]
├── Task issue: task-003 [agent:task, phase:implement, parallel]
└── Task issue: task-004 [agent:task, phase:implement, sequential]
```

**Task issue machine data**:
```yaml
work_id: 2026-04-27-add-rate-limit-logs
kind: task
task_id: task-001
phase: implement
stage: red
parallelizable: false
depends_on: []
```

### Closure

**From workflow.md, Phase 7, Step 6:**
> Close the task-graph issue once the YAML and implementation task issues are complete.

**When**: Phase 7, after YAML is authored and all task issues are created

**Status**: **CLOSED** (but task issues remain OPEN for Phase 8 implementation)

**Gate E requirement** (workflow.md line 222):
> the task-graph issue is closed, at least one implementation task issue has `stage: red`, and every task issue records an explicit dependency list before Phase 8 begins.

---

## Clean GitHub Issue Tree Summary

### At End of Phase 3
- ✓ `phase:exploration` issue: **CLOSED**
- ✓ `files.csv` artifact: **CLOSED** (phase 3 output)
- ✓ `open-questions` artifact: **OPEN** (continues through Phase 5)

### At End of Phase 4
- ✓ `phase:research` issue: **CLOSED**
- ✓ `sources.md` artifact: **CLOSED** (phase 4 output)
- ✓ `open-questions` artifact: **OPEN** (updated with research answers; continues to Phase 5)

### At End of Phase 5
- ✓ `phase:clarification` issue: **CLOSED**
- ✓ `open-questions` artifact: **CLOSED** (all questions resolved/finalized)

### At End of Phase 7
- ✓ `phase:task-graph` issue: **CLOSED**
- ✓ Task graph YAML: In `phase:task-graph` issue body (not a separate artifact)
- ✓ Task issues: **OPEN** (waiting for Phase 8 implementation)

---

## Why This Design?

1. **Immutable references**: Once files.csv and sources.md close, later phases know these are fixed and won't change
2. **Progressive resolution**: open-questions stays open across multiple phases, being updated as answers accumulate
3. **Single source of truth for task graph**: YAML in the phase issue body means there's one authoritative version, with GitHub history tracking changes
4. **Clean closure signals**: Closed issues clearly indicate "this work is DONE"; open issues indicate "work in progress"
5. **Resume-friendly**: A fresh session can see at a glance which artifacts are complete and which remain

---

## Specification References

| What | Where |
|------|-------|
| files.csv closure | `workflow.md:116` (Phase 3 Step 7) |
| sources.md closure | `workflow.md:141` (Phase 4 Step 6) |
| open-questions lifecycle | `workflow.md:117–118, 142–143, 169` (Phases 3, 4, 5) |
| Task graph YAML location | `artifact-schema.md` (Phase Issue Requirements section) |
| Task graph YAML authoring | `workflow.md:215` (Phase 7 Step 4) |
| Gate A (files.csv closed) | `workflow.md:122` |
| Gate B (sources.md closed) | `workflow.md:148` |
| Gate C (open-questions closed) | `workflow.md:175` |
| Gate E (task-graph closed) | `workflow.md:222` |
| README artifact table | `README.md:150–170` |
