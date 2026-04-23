# Issue hierarchy

Use sub-issue structure to keep order and dependency visibility.

## Structure

1. Parent issue (`agent_parent_issue.yml`)
2. Phase sub-issues (`agent_phase_issue.yml`) for phases 00-10
3. Task sub-issues (`agent_task_issue.yml`) for DAG tasks in phase 06+

## Labels (recommended)

- `agent:parent`, `agent:phase`, `agent:task`
- `phase:00` ... `phase:10`
- `parallel`, `sequential`, `blocked`, `needs-human`

## Machine metadata block

Include this fenced YAML in each issue body:

```yaml
work_id: <work-id>
kind: parent|phase|task
phase: "00-10"
parallelizable: true|false
depends_on_issue_numbers: []
artifact_paths: []
status: open|blocked|done
```
