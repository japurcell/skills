# Live Gemini qualification plan

## Purpose / Big Picture
Create a Python greeting module and tests in this disposable repository. Set `PYTHONDONTWRITEBYTECODE=1` for development commands so no bytecode files enter the task delta.

## Progress
<!-- execplan-loop:generated progress:start -->
- [ ] [M1] T1: Work
- [ ] [M1] T2: Work
- [ ] [M1] T3: Work
<!-- execplan-loop:generated progress:end -->

```execplan-loop-v1
{
  "schema_version": 1,
  "plan_id": "live-qualification",
  "tasks": [
    {
      "id": "T1",
      "milestone_id": "M1",
      "kind": "implementation",
      "depends_on": [],
      "verification": [
        {
          "id": "greeting-tests",
          "argv": [
            "python3",
            "-c",
            "import sys\nsys.dont_write_bytecode = True\nfrom pathlib import Path\nif not all(Path(p).is_file() for p in (\"greeting.py\", \"test_greeting.py\")):\n    raise SystemExit(1)\nimport unittest\ntry:\n    from greeting import greet\n    assert greet(\"Ada\") == \"Hello, Ada!\"\n    assert greet(\"\") == \"Hello, !\"\n    suite = unittest.defaultTestLoader.loadTestsFromName(\"test_greeting\")\n    assert suite.countTestCases() >= 2\nexcept (ImportError, AssertionError, SyntaxError):\n    raise SystemExit(1)\nresult = unittest.TextTestRunner(verbosity=2).run(suite)\nraise SystemExit(0 if result.wasSuccessful() else 1)"
          ],
          "cwd": ".",
          "timeout_seconds": 30,
          "expected_exit_code": 0,
          "failure_policy": {
            "1": "repair"
          }
        }
      ],
      "writable_paths": [
        "greeting.py",
        "test_greeting.py"
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
          "id": "greeting-tests",
          "argv": [
            "python3",
            "-c",
            "import sys\nsys.dont_write_bytecode = True\nfrom pathlib import Path\nif not all(Path(p).is_file() for p in (\"greeting.py\", \"test_greeting.py\")):\n    raise SystemExit(1)\nimport unittest\ntry:\n    from greeting import greet\n    assert greet(\"Ada\") == \"Hello, Ada!\"\n    assert greet(\"\") == \"Hello, !\"\n    suite = unittest.defaultTestLoader.loadTestsFromName(\"test_greeting\")\n    assert suite.countTestCases() >= 2\nexcept (ImportError, AssertionError, SyntaxError):\n    raise SystemExit(1)\nresult = unittest.TextTestRunner(verbosity=2).run(suite)\nraise SystemExit(0 if result.wasSuccessful() else 1)"
          ],
          "cwd": ".",
          "timeout_seconds": 30,
          "expected_exit_code": 0,
          "failure_policy": {
            "1": "repair"
          }
        }
      ],
      "writable_paths": [
        "greeting.py",
        "test_greeting.py"
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
          "id": "greeting-tests",
          "argv": [
            "python3",
            "-c",
            "import sys\nsys.dont_write_bytecode = True\nfrom pathlib import Path\nif not all(Path(p).is_file() for p in (\"greeting.py\", \"test_greeting.py\")):\n    raise SystemExit(1)\nimport unittest\ntry:\n    from greeting import greet\n    assert greet(\"Ada\") == \"Hello, Ada!\"\n    assert greet(\"\") == \"Hello, !\"\n    suite = unittest.defaultTestLoader.loadTestsFromName(\"test_greeting\")\n    assert suite.countTestCases() >= 2\nexcept (ImportError, AssertionError, SyntaxError):\n    raise SystemExit(1)\nresult = unittest.TextTestRunner(verbosity=2).run(suite)\nraise SystemExit(0 if result.wasSuccessful() else 1)"
          ],
          "cwd": ".",
          "timeout_seconds": 30,
          "expected_exit_code": 0,
          "failure_policy": {
            "1": "repair"
          }
        }
      ],
      "writable_paths": [
        "greeting.py",
        "test_greeting.py"
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

### Milestone M1: Deliver tested greeting
<!-- execplan-loop:generated milestone-M1:start -->
Status: open
Acceptance: not met
<!-- execplan-loop:generated milestone-M1:end -->

#### Task T1: Work
Activate `tdd` before source edits. First write at least two unittest cases in test_greeting.py covering greet("Ada") == "Hello, Ada!" and greet("") == "Hello, !". Run them and observe failure before adding greeting.py with greet(name). Then implement the smallest correct function and rerun tests. Set PYTHONDONTWRITEBYTECODE=1 for development commands. Change only greeting.py and test_greeting.py. Do not edit this plan, stage files, or commit. Stop after the declared check passes and propose the required structured result and commit message.

#### Task T2: Work
Run the declared greeting acceptance check. Repair only greeting.py and test_greeting.py if a check identifies a defect. Activate `tdd` for source changes. Stop after acceptance passes.

#### Task T3: Work
Run final greeting acceptance. Repair only greeting.py and test_greeting.py if needed, using `tdd` for source changes. Stop after acceptance passes.
