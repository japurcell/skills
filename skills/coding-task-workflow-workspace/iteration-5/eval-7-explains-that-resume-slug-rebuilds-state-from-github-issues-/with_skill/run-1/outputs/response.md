# coding-task-workflow RESUME State Reconstruction Evaluation

## Scenario

- **Command**: `coding-task-workflow RESUME=2026-04-27-add-rate-limit-logs`
- **Constraint**: No local artifact directory (fresh agent session with no local files)
- **Question**: Where does resume state come from? How does workflow decide the next phase?

## Skill Specification: RESUME State Reconstruction

**From SKILL.md, Routing precedence, item 2:**

> `RESUME=<slug>`: rebuild state from the GitHub issue hierarchy for that `work_id` and continue from the next incomplete phase.

**From README.md, Example 5:**

> What happens: agent finds the parent issue and descendant phase/task issues by `work_id`, determines the last completed phase from issue closure state plus approval / implementation-log comments, and resumes from the next incomplete phase.

**From artifact-schema.md, Resume Expectations:**

> `RESUME=<slug>` must reconstruct state from GitHub alone:
> 1. Find the parent issue or phase issue chain by `work_id`.
> 2. Read closed phase issues for completed artifacts.
> 3. Read open artifact / task issues for remaining work.
> 4. Read approval and implementation-log comments where relevant.
> Do **not** assume `.coding-workflow/work/<slug>/` exists.

**From workflow.md Phase 8, Step 1:**

> Resolve `RESUME=<slug>` by loading the parent issue and descendant phase/task issues for that `work_id`. Do not rely on local phase files.

## Where Resume State Comes From

### **Source: GitHub Issues (Not Local Files)**

All resume state is reconstructed from GitHub issue hierarchy. There are **no local files**; the agent does not look for or depend on `.coding-workflow/work/2026-04-27-add-rate-limit-logs/`.

### **Data Sources in GitHub**

The workflow reads four types of GitHub data:

#### **1. Parent Issue**

**Finding it**:
- Query GitHub for the `agent:parent` label
- Search for issue title or body containing the `work_id` slug: `2026-04-27-add-rate-limit-logs`
- Or reconstruct from the slug if the repo uses a naming convention

**What it contains** (Machine Data section):
```yaml
work_id: 2026-04-27-add-rate-limit-logs
kind: parent
status: open
```

**Current phase**:
- Issue body has a `## Current Phase` section tracking which phase was last started
- This is the agent's first hint about progress

#### **2. Phase Issues** (linked as sub-issues to parent)

**Reading completion state**:
- Query all child issues of the parent issue using GitHub's sub-issue relationship
- For each phase issue, check the `phase:<name>` label and issue **closed/open state**:
  - **Closed** = phase complete
  - **Open** = phase in progress or incomplete

**Per-phase closed state detection**:

| Phase | Issue Label | Completion Signal |
|-------|------------|------------------|
| Phase 1 (Intake) | `phase:intake` | **CLOSED** = complete |
| Phase 2 (Worktree) | `phase:worktree` | **CLOSED** = complete |
| Phase 3 (Exploration) | `phase:exploration` | **CLOSED** + `files.csv` closed + `open-questions` exists |
| Phase 4 (Research) | `phase:research` | **CLOSED** + `sources.md` closed + `open-questions` resolved |
| Phase 5 (Clarification) | `phase:clarification` | **CLOSED** + `open-questions` closed |
| Phase 6 (Plan) | `phase:plan` | **CLOSED** (approval in body/comments) |
| Phase 7 (TDD Task Graph) | `phase:task-graph` | **CLOSED** + all task issues exist |
| Phase 8 (Implementation) | `phase:implement` (task issues) | All task issues **CLOSED** |
| Phase 9 (Review) | `phase:review` | **CLOSED** + no open High findings |
| Phase 10 (Verification) | `phase:verify` | **CLOSED** (Gate F passed) |
| Phase 11 (PR) | `phase:pr` | **CLOSED** + PR number in body |

#### **3. Artifact Sub-issues**

**Finding them**:
- Under each phase issue, find artifact sub-issues (linked with GitHub's sub-issue relationship)
- Examples: `files.csv`, `open-questions`, `sources.md`, `task-graph`

**State from artifact issues**:
- **Closed** artifact: work is complete (e.g., `files.csv` closed = file list finalized)
- **Open** artifact: work remains (e.g., `open-questions` open = questions still unresolved)

#### **4. Machine Data Section (YAML Block)**

Every issue has a `## Machine Data` section containing:

```yaml
work_id: 2026-04-27-add-rate-limit-logs
kind: phase  # or artifact, task, approval, implementation-log
phase: research  # which phase this belongs to
status: open  # or closed, approved, complete, blocked
depends_on:
  - 3  # Phase 3 exploration must complete first
```

This machine-readable format allows the agent to:
- Verify the `work_id` matches the RESUME slug
- Read phase dependencies
- Detect gate satisfaction

#### **5. Comments (Approval & Implementation Logs)**

**Approval comments**:
- On `phase:plan` issue: comment marking "Gate D: approved"
- Indicates Plan phase is ready to advance to TDD

**Implementation-log comments**:
- On each `phase:implement` task issue: RED / GREEN / REFACTOR comments
- Track progress through TDD slices

---

## How Workflow Decides the Next Phase

### **Algorithm**

**Step 1: Load GitHub issue hierarchy**

```bash
# Find parent issue by work_id
PARENT_ISSUE=$(gh issue list --label agent:parent --search "2026-04-27-add-rate-limit-logs" --json number | jq -r '.[0].number')

# Get all child issues (phase and artifact issues)
CHILD_ISSUES=$(gh issue view $PARENT_ISSUE --json subIssues)
```

**Step 2: Determine last completed phase**

For each phase in order (1→11):
- Check if the phase issue exists and is **CLOSED**
- For critical artifacts, verify they are **CLOSED** (e.g., Phase 3: is `files.csv` closed?)
- If any required gate condition is **not met**, that phase is incomplete

Example check for Phase 3 completion:
```bash
EXPLORATION_CLOSED=$(gh issue view <exploration-issue> --json state | jq -r .state)
FILES_CSV_CLOSED=$(gh issue view <files-csv-issue> --json state | jq -r .state)
OPEN_QUESTIONS_EXISTS=$(gh issue view <open-questions-issue>)

if [ "$EXPLORATION_CLOSED" == "CLOSED" ] && [ "$FILES_CSV_CLOSED" == "CLOSED" ] && [ -n "$OPEN_QUESTIONS_EXISTS" ]; then
  LAST_COMPLETED=3
fi
```

**Step 3: Check gate conditions**

For gates that require specific state:

- **Gate A** (before Phase 4): Phase 3 exploration issue CLOSED + files.csv CLOSED + open-questions EXISTS
- **Gate B** (before Phase 5): Phase 4 research issue CLOSED + sources.md CLOSED + open-questions has no `status: open` entries
- **Gate C** (before Phase 6): Phase 5 clarification issue CLOSED + open-questions CLOSED
- **Gate D** (before Phase 7): Phase 6 plan issue CLOSED with approval comment
- **Gate E** (before Phase 8 HARD STOP): Phase 7 task-graph CLOSED with all task issues created
- **Gate F** (before Phase 11): Phase 10 verification CLOSED with all acceptance `pass`

**Step 4: Determine next phase**

```
next_phase = last_completed_phase + 1

if next_phase > 7 and last_completed_phase == 7:
  # Special case: HARD STOP after Gate E
  # Return: "coding-task-workflow RESUME=2026-04-27-add-rate-limit-logs"
  # Do not proceed to Phase 8 in this session
  
if next_phase is in [1..7]:
  # Resume from the next incomplete phase
  
if next_phase == 8:
  # Start Phase 8 (implementation) in fresh session after resume handoff
```

### **Example: Resuming after Phase 7 (Hard Stop)**

**Incoming command**: `coding-task-workflow RESUME=2026-04-27-add-rate-limit-logs`

**Agent reads**:
1. Parent issue: `work_id: 2026-04-27-add-rate-limit-logs`
2. Finds `phase:task-graph` issue: **CLOSED**
3. Finds all `phase:implement` task issues: **all exist**
4. Reads Machine Data:
   ```yaml
   work_id: 2026-04-27-add-rate-limit-logs
   phase: task-graph
   status: closed
   ```

**Agent detects**: Gate E is passed, last completed phase is 7

**Agent concludes**: Next phase is Phase 8 (Implementation)

**Agent does**: Enters Phase 8 with fresh session, loads task-graph issue and all task issues, begins delegating implementation subagents

### **Example: Resuming after Phase 4 (Interrupted Research)**

**Incoming command**: `coding-task-workflow RESUME=2026-04-27-add-rate-limit-logs`

**Agent reads**:
1. Parent issue: `work_id: 2026-04-27-add-rate-limit-logs`
2. Finds:
   - `phase:exploration`: **CLOSED** ✓
   - `phase:research`: **OPEN** (incomplete)
   - `open-questions` artifact: still has 2 entries with `status: open`

**Agent detects**: Last completed phase is 3, Phase 4 is incomplete

**Agent concludes**: Next phase is Phase 4 (continue Research)

**Agent does**: Reads the open-questions issue, launches research subagents to resolve the remaining 2 questions, updates the open-questions artifact

---

## Resume vs. Fresh Start

| Aspect | RESUME | Fresh Start |
|--------|--------|------------|
| **Invocation** | `RESUME=2026-04-27-add-rate-limit-logs` | `WORK_ITEM=... ISSUE=42` |
| **State source** | GitHub issue hierarchy | GitHub issue or user input |
| **Artifact files** | Not accessed (no local files) | Not used |
| **Starting phase** | Next incomplete phase | Phase 1 (Intake) |
| **Gate check** | Determines next phase from issue closure | Creates new intake artifact |
| **Parent issue** | Found by `work_id` in GitHub | Created or specified as ISSUE |

---

## Critical Rules

**From SKILL.md Non-negotiable rule #4:**

> After Gate E passes, hard-stop the session and hand off `coding-task-workflow RESUME=<slug>`. Do not begin Phase 8 in the same session. Resume from a fresh session; Phase 8 is the next phase after the resume. Do not restart earlier phases unless the GitHub artifact state says they are incomplete.

**Implication for RESUME**: 
- If resuming with `last_completed_phase == 7`, the agent immediately hands off to a fresh session
- If resuming with `last_completed_phase < 7`, continue from `last_completed_phase + 1` in the same session
- Only restart an earlier phase if GitHub issue state indicates it is actually incomplete

---

## Summary

| Question | Answer |
|----------|--------|
| **Where is resume state?** | **GitHub issue hierarchy** (parent issue + all phase/artifact/task sub-issues) |
| **Local files?** | **NONE** — agent does not depend on `.coding-workflow/work/<slug>/` |
| **How to find parent?** | Query `agent:parent` label + search for `work_id` in issue title/body |
| **How to detect phase completion?** | Read phase issue **closed/open state** + verify gate conditions from artifact sub-issue states + read Machine Data YAML + check approval/implementation-log comments |
| **How to decide next phase?** | Find `last_completed_phase` from issue states, then `next_phase = last_completed_phase + 1` |
| **Special case (Phase 8)?** | After Gate E (Phase 7 complete), hard-stop and return resume handoff command; do not proceed in same session |

This design ensures that any agent can pick up a work item from anywhere in the workflow by reading GitHub alone, with no local file dependencies.
