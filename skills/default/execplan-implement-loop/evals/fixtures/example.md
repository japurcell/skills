# Example plan

## Purpose / Big Picture
Create output.txt containing exactly the UTF-8 text `complete`.

## Progress
<!-- execplan-loop:generated progress:start -->
- [ ] [M1] T1: Work
- [ ] [M1] T2: Work
- [ ] [M1] T3: Work
<!-- execplan-loop:generated progress:end -->

```execplan-loop-v1
{
  "schema_version": 1,
  "plan_id": "example",
  "tasks": [
    {
      "id": "T1",
      "milestone_id": "M1",
      "kind": "implementation",
      "depends_on": [],
      "verification": [
        {
          "id": "check",
          "argv": [
            "python3",
            "-c",
            "from pathlib import Path\ntry:\n    value = Path(\"output.txt\").read_text(encoding=\"utf-8\")\nexcept OSError:\n    raise SystemExit(2)\nraise SystemExit(0 if value == \"complete\" else 1)"
          ],
          "cwd": ".",
          "timeout_seconds": 5,
          "expected_exit_code": 0,
          "failure_policy": {
            "1": "repair",
            "2": "blocked"
          }
        }
      ],
      "writable_paths": [
        "output.txt"
      ],
      "state": "open",
      "evidence": []
    },
    {
      "id": "T2",
      "milestone_id": "M1",
      "kind": "verification",
      "depends_on": [
        "T1"
      ],
      "verification": [
        {
          "id": "check",
          "argv": [
            "python3",
            "-c",
            "from pathlib import Path\ntry:\n    value = Path(\"output.txt\").read_text(encoding=\"utf-8\")\nexcept OSError:\n    raise SystemExit(2)\nraise SystemExit(0 if value == \"complete\" else 1)"
          ],
          "cwd": ".",
          "timeout_seconds": 5,
          "expected_exit_code": 0,
          "failure_policy": {
            "1": "repair",
            "2": "blocked"
          }
        }
      ],
      "writable_paths": [
        "output.txt"
      ],
      "state": "open",
      "evidence": []
    },
    {
      "id": "T3",
      "milestone_id": "M1",
      "kind": "verification",
      "depends_on": [
        "T2"
      ],
      "verification": [
        {
          "id": "check",
          "argv": [
            "python3",
            "-c",
            "from pathlib import Path\ntry:\n    value = Path(\"output.txt\").read_text(encoding=\"utf-8\")\nexcept OSError:\n    raise SystemExit(2)\nraise SystemExit(0 if value == \"complete\" else 1)"
          ],
          "cwd": ".",
          "timeout_seconds": 5,
          "expected_exit_code": 0,
          "failure_policy": {
            "1": "repair",
            "2": "blocked"
          }
        }
      ],
      "writable_paths": [
        "output.txt"
      ],
      "state": "open",
      "evidence": []
    }
  ],
  "milestones": [
    {
      "id": "M1",
      "verification_task_id": "T2",
      "state": "open",
      "evidence": []
    }
  ],
  "final_task_id": "T3"
}
```

## Surprises & Discoveries
<!-- execplan-loop:generated discoveries:start -->
None.
<!-- execplan-loop:generated discoveries:end -->

## Decision Log
<!-- execplan-loop:generated decisions:start -->
None.
<!-- execplan-loop:generated decisions:end -->

## Outcomes & Retrospective
<!-- execplan-loop:generated outcomes:start -->
Pending.
<!-- execplan-loop:generated outcomes:end -->

### Milestone M1: Deliver output
<!-- execplan-loop:generated milestone-M1:start -->
Status: open
Acceptance: not met
<!-- execplan-loop:generated milestone-M1:end -->

#### Task T1: Work
Create or verify output.txt containing exactly the UTF-8 text `complete`. Stop after the declared content check passes. Read/permission failures block; an incorrect value permits a scoped repair.

#### Task T2: Work
Create or verify output.txt containing exactly the UTF-8 text `complete`. Stop after the declared content check passes. Read/permission failures block; an incorrect value permits a scoped repair.

#### Task T3: Work
Create or verify output.txt containing exactly the UTF-8 text `complete`. Stop after the declared content check passes. Read/permission failures block; an incorrect value permits a scoped repair.
